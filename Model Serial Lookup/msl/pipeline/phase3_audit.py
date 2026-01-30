from __future__ import annotations

import csv
import datetime as dt
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from msl.decoder.normalize import normalize_brand, normalize_text
from msl.pipeline.common import ensure_dir
from msl.pipeline.phase3_baseline import infer_column_map
from msl.pipeline.phase3_mine import _as_int


def _find_col(fieldnames: list[str], candidates: list[str]) -> str | None:
    norm = {normalize_text(c): c for c in (fieldnames or [])}
    for cand in candidates:
        key = normalize_text(cand)
        if key in norm:
            return norm[key]
    return None


def _parse_tons(val: str | None, unit: str | None) -> float | None:
    if val is None:
        return None
    t = str(val).strip()
    if not t:
        return None
    try:
        num = float(t)
    except Exception:
        return None
    u = normalize_text(unit or "")
    if u in {"TON", "TONS"}:
        return num
    if u in {"BTUH", "BTU/H", "BTUHR", "BTU/HR"}:
        return num / 12000.0
    if u in {"MBH", "MBTUH"}:
        return (num * 1000.0) / 12000.0
    return None


def _parse_float(val: str | None) -> float | None:
    if val is None:
        return None
    t = str(val).strip()
    if not t:
        return None
    try:
        return float(t)
    except Exception:
        return None


def cmd_phase3_audit(args) -> int:
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    candidates_dir = Path(args.candidates_dir)
    if not candidates_dir.exists():
        raise SystemExit(f"Missing candidates dir: {candidates_dir}")

    run_id = args.run_id or (candidates_dir.parent.name if candidates_dir.name == "candidates" else candidates_dir.name)
    out_dir = ensure_dir(Path(args.out_dir) / run_id)

    attr_cands_path = candidates_dir / "AttributeDecodeRule.candidates.jsonl"
    serial_cands_path = candidates_dir / "SerialDecodeRule.candidates.jsonl"

    attr_cands: list[dict] = []
    if attr_cands_path.exists():
        for line in attr_cands_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                attr_cands.append(json.loads(line))

    serial_cands: list[dict] = []
    if serial_cands_path.exists():
        for line in serial_cands_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                serial_cands.append(json.loads(line))

    with input_path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        fns = reader.fieldnames or []
        cmap = infer_column_map(fns)
        col_model = _find_col(fns, ["ModelNumber", "Model #", "Model", "modelNumber"])
        col_equipment = _find_col(fns, ["EquipmentType", "Equipment", "Type", "equipmentType", "description"])
        col_known_tons = _find_col(fns, ["KnownCapacityTons", "Known Capacity Tons", "CapacityTons", "Known Tons"])
        col_cap_val = _find_col(fns, ["Cooling Capacity \n(Input)", "Cooling Capacity (Input)", "Cooling Capacity", "CoolingCapacity"])
        col_cap_unit = _find_col(fns, ["Cooling Capacity \n(Unit)", "Cooling Capacity (Unit)", "Cooling Capacity Unit", "CoolingCapacityUnit"])
        col_fan_hp = _find_col(fns, ["Fan \n(HP)", "Fan (HP)", "FanHP"])
        col_fan_cfm = _find_col(fns, ["Fan Flow\n(CFM)", "Fan Flow (CFM)", "FanFlow(CFM)", "Fan Flow"])
        col_pump_hp = _find_col(fns, ["Pump \n(HP)", "Pump (HP)", "PumpHP"])
        col_pump_gpm = _find_col(fns, ["Pump Flow\n(GPM)", "Pump Flow (GPM)", "PumpFlow(GPM)", "Pump Flow"])
        col_amp = _find_col(fns, ["Amp", "Amps"])
        col_dhw_gal = _find_col(fns, ["DHW Storage Capacity\n(Gallons)", "DHW Storage Capacity (Gallons)", "DHW Storage Capacity"])

        # Cache a compact representation for collision testing.
        rows: list[dict] = list(reader)

    tol = float(args.capacity_tolerance_tons)

    holdout_rows: list[dict] = []
    fp_rows: list[dict] = []
    holdout_rows_by_type: list[dict] = []
    fp_rows_by_type: list[dict] = []

    def _cand_equipment_types_list(cand: dict) -> list[str]:
        ets = cand.get("equipment_types")
        if ets is None:
            ets = []
        if not isinstance(ets, list):
            ets = []
        legacy = normalize_text(cand.get("equipment_type") or "")
        if legacy:
            ets = list(ets) + [legacy]
        out = [normalize_text(str(x)) for x in ets if str(x).strip()]
        # De-dup, stable.
        seen: set[str] = set()
        final: list[str] = []
        for t in out:
            if t and t not in seen:
                seen.add(t)
                final.append(t)
        return final

    # Attribute candidate audit
    for cand in attr_cands:
        brand = normalize_brand(cand.get("brand"))
        cand_types = _cand_equipment_types_list(cand)
        equipment_type = cand_types[0] if cand_types else ""
        attribute_name = (cand.get("attribute_name") or "").strip()
        model_regex = (cand.get("model_regex") or "").strip()
        ve = cand.get("value_extraction") or {}
        pat = (ve.get("pattern") or {}).get("regex")
        group = int((ve.get("pattern") or {}).get("group") or 1)
        mapping = ve.get("mapping") if isinstance(ve.get("mapping"), dict) else None
        transform = ve.get("transform") if isinstance(ve.get("transform"), dict) else None
        if not pat:
            continue
        try:
            rx = re.compile(pat)
        except Exception:
            continue
        mrx = None
        if model_regex:
            try:
                mrx = re.compile(model_regex)
            except Exception:
                mrx = None

        # Determine truth source per attribute (audit only what we can validate).
        def truth_for_row(row: dict) -> float | None:
            if attribute_name == "NominalCapacityTons":
                # Prefer SDI's explicit KnownCapacityTons when present, otherwise fall back to parsing
                # Cooling Capacity (Input/Unit) into tons.
                if col_known_tons:
                    v = _parse_float(row.get(col_known_tons))
                    if v is not None:
                        return v
                if not col_cap_val or not col_cap_unit:
                    return None
                return _parse_tons(row.get(col_cap_val), row.get(col_cap_unit))
            # SDI truth has a single Fan (HP) column.
            # We can validate generic FanHP and SupplyFanHP against it, but ReturnFanHP is not
            # directly auditable against SDI (it would require a separate return-fan column).
            if attribute_name in {"FanHP", "SupplyFanHP"}:
                return _parse_float(row.get(col_fan_hp)) if col_fan_hp else None
            if attribute_name == "FanFlowCFM":
                return _parse_float(row.get(col_fan_cfm)) if col_fan_cfm else None
            if attribute_name == "PumpHP":
                return _parse_float(row.get(col_pump_hp)) if col_pump_hp else None
            if attribute_name == "PumpFlowGPM":
                return _parse_float(row.get(col_pump_gpm)) if col_pump_gpm else None
            if attribute_name == "Amps":
                return _parse_float(row.get(col_amp)) if col_amp else None
            if attribute_name == "DHWStorageGallons":
                return _parse_float(row.get(col_dhw_gal)) if col_dhw_gal else None
            return None

        tol_map = {
            "NominalCapacityTons": float(args.capacity_tolerance_tons),
            "FanHP": 0.5,
            "SupplyFanHP": 0.5,
            "PumpHP": 0.5,
            "FanFlowCFM": 50.0,
            "PumpFlowGPM": 5.0,
            "Amps": 5.0,
            "DHWStorageGallons": 5.0,
        }
        tol = float(tol_map.get(attribute_name, float(args.capacity_tolerance_tons)))

        def eval_candidate_for_type(et_filter: str | None) -> tuple[int, int, int, int]:
            n = 0
            n_truth = 0
            n_match = 0
            n_correct = 0
            for row in rows:
                make_raw = (row.get(cmap.make) or "").strip() if cmap.make else ""
                b = normalize_brand(make_raw)
                if b != brand:
                    continue
                if et_filter and col_equipment:
                    et = normalize_text((row.get(col_equipment) or "").strip())
                    if et != et_filter:
                        continue
                n += 1
                if not col_model:
                    continue
                model = (row.get(col_model) or "").strip()
                truth = truth_for_row(row)
                if truth is None:
                    continue
                n_truth += 1
                model_norm = normalize_text(model)
                if mrx is not None and not mrx.search(model_norm):
                    continue
                m = rx.search(model_norm)
                if not m:
                    continue
                try:
                    code = m.group(group)
                except Exception:
                    continue
                n_match += 1
                pred = None
                if mapping is not None and code in mapping:
                    try:
                        pred = float(mapping[code])
                    except Exception:
                        pred = None
                elif transform is not None and transform.get("expression") == "tons = code / 12":
                    if code.isdigit():
                        pred = float(int(code)) / 12.0
                else:
                    if code.isdigit():
                        pred = float(int(code))
                if pred is None:
                    continue
                if abs(pred - float(truth)) <= tol:
                    n_correct += 1
            return n, n_truth, n_match, n_correct

        # Keep legacy holdout rows behavior (optional single equipment_type filter).
        n, n_truth, n_match, n_correct = eval_candidate_for_type(equipment_type if equipment_type else None)
        acc = (n_correct / n_match) if n_match else 0.0
        cov = (n_match / n_truth) if n_truth else 0.0
        holdout_rows.append(
            {
                "candidate_type": "AttributeDecodeRule",
                "brand": brand,
                "equipment_type": equipment_type,
                "support_rows": n,
                "truth_rows": n_truth,
                "matched_rows": n_match,
                "correct_rows": n_correct,
                "accuracy_on_matches": f"{acc:.4f}",
                "coverage_on_truth": f"{cov:.4f}",
                "pattern_regex": pat,
                "notes": cand.get("limitations", ""),
            }
        )

        # By-type output: for typed candidates, emit one row per type; for untyped, emit one ALL row.
        type_list = cand_types if cand_types else ["ALL"]
        for et in type_list:
            et_filter = None if et == "ALL" else et
            n, n_truth, n_match, n_correct = eval_candidate_for_type(et_filter)
            acc = (n_correct / n_match) if n_match else 0.0
            cov = (n_match / n_truth) if n_truth else 0.0
            holdout_rows_by_type.append(
                {
                    "candidate_type": "AttributeDecodeRule",
                    "brand": brand,
                    "equipment_type": et,
                    "support_rows": n,
                    "truth_rows": n_truth,
                    "matched_rows": n_match,
                    "correct_rows": n_correct,
                    "accuracy_on_matches": f"{acc:.4f}",
                    "coverage_on_truth": f"{cov:.4f}",
                    "pattern_regex": pat,
                    "notes": cand.get("limitations", ""),
                }
            )

        # False-positive audit: how often does this pattern match other brands' models?
        def fp_for_type(et_filter: str | None) -> tuple[int, int]:
            other_match = 0
            other_total = 0
            for row in rows:
                make_raw = (row.get(cmap.make) or "").strip() if cmap.make else ""
                b = normalize_brand(make_raw)
                if b == brand:
                    continue
                if et_filter and col_equipment:
                    et = normalize_text((row.get(col_equipment) or "").strip())
                    if et != et_filter:
                        continue
                other_total += 1
                if not col_model:
                    continue
                model = (row.get(col_model) or "").strip()
                model_norm = normalize_text(model)
                if mrx is not None and not mrx.search(model_norm):
                    continue
                if rx.search(model_norm):
                    other_match += 1
            return other_total, other_match

        other_total, other_match = fp_for_type(equipment_type if equipment_type else None)
        fp_rows.append(
            {
                "candidate_type": "AttributeDecodeRule",
                "brand": brand,
                "equipment_type": equipment_type,
                "pattern_regex": pat,
                "other_brand_rows": other_total,
                "other_brand_matches": other_match,
                "other_brand_match_rate": f"{(other_match / other_total):.4f}" if other_total else "",
            }
        )
        type_list = cand_types if cand_types else ["ALL"]
        for et in type_list:
            et_filter = None if et == "ALL" else et
            other_total, other_match = fp_for_type(et_filter)
            fp_rows_by_type.append(
                {
                    "candidate_type": "AttributeDecodeRule",
                    "brand": brand,
                    "equipment_type": et,
                    "pattern_regex": pat,
                    "other_brand_rows": other_total,
                    "other_brand_matches": other_match,
                    "other_brand_match_rate": f"{(other_match / other_total):.4f}" if other_total else "",
                }
            )

    # Serial candidate audit (year only)
    for cand in serial_cands:
        brand = normalize_brand(cand.get("brand"))
        pat = cand.get("serial_regex") or ""
        df = cand.get("date_fields") or {}
        year_spec = (df.get("year") or {}).get("positions") or {}
        ys = int(year_spec.get("start") or 0)
        ye = int(year_spec.get("end") or 0)
        transform = (df.get("year") or {}).get("transform") if isinstance((df.get("year") or {}).get("transform"), dict) else None
        if not pat or ys < 1 or ye < ys:
            continue
        try:
            rx = re.compile(pat)
        except Exception:
            continue

        n = 0
        n_truth = 0
        n_match = 0
        n_correct = 0
        for row in rows:
            make_raw = (row.get(cmap.make) or "").strip() if cmap.make else ""
            b = normalize_brand(make_raw)
            if b != brand:
                continue
            n += 1
            if not cmap.serial or not cmap.known_year:
                continue
            serial = (row.get(cmap.serial) or "").strip()
            ky = _as_int((row.get(cmap.known_year) or "").strip())
            if not serial or ky is None:
                continue
            n_truth += 1
            s = re.sub(r"[\s\-_\/]+", "", serial.upper())
            if not rx.search(s):
                continue
            n_match += 1
            if ye > len(s):
                continue
            raw = s[ys - 1 : ye]
            if not raw.isdigit():
                continue
            val = int(raw)
            if transform and transform.get("type") == "year_add_base":
                val = int(transform.get("base", 0)) + val
            if val == ky:
                n_correct += 1
        acc = (n_correct / n_match) if n_match else 0.0
        cov = (n_match / n_truth) if n_truth else 0.0
        holdout_rows.append(
            {
                "candidate_type": "SerialDecodeRule",
                "brand": brand,
                "equipment_type": "",
                "support_rows": n,
                "truth_rows": n_truth,
                "matched_rows": n_match,
                "correct_rows": n_correct,
                "accuracy_on_matches": f"{acc:.4f}",
                "coverage_on_truth": f"{cov:.4f}",
                "pattern_regex": pat,
                "notes": cand.get("style_name", ""),
            }
        )
        # By-type output: serial candidates are brand-scoped; emit a single ALL row (type scoping is optional).
        holdout_rows_by_type.append(
            {
                "candidate_type": "SerialDecodeRule",
                "brand": brand,
                "equipment_type": "ALL",
                "support_rows": n,
                "truth_rows": n_truth,
                "matched_rows": n_match,
                "correct_rows": n_correct,
                "accuracy_on_matches": f"{acc:.4f}",
                "coverage_on_truth": f"{cov:.4f}",
                "pattern_regex": pat,
                "notes": cand.get("style_name", ""),
            }
        )

    holdout_path = out_dir / "holdout_validation_results.csv"
    with holdout_path.open("w", newline="", encoding="utf-8") as f_out:
        w = csv.DictWriter(
            f_out,
            fieldnames=[
                "candidate_type",
                "brand",
                "equipment_type",
                "support_rows",
                "truth_rows",
                "matched_rows",
                "correct_rows",
                "accuracy_on_matches",
                "coverage_on_truth",
                "pattern_regex",
                "notes",
            ],
        )
        w.writeheader()
        for r in holdout_rows:
            w.writerow(r)

    holdout_by_type_path = out_dir / "holdout_validation_results_by_type.csv"
    with holdout_by_type_path.open("w", newline="", encoding="utf-8") as f_out:
        w = csv.DictWriter(
            f_out,
            fieldnames=[
                "candidate_type",
                "brand",
                "equipment_type",
                "support_rows",
                "truth_rows",
                "matched_rows",
                "correct_rows",
                "accuracy_on_matches",
                "coverage_on_truth",
                "pattern_regex",
                "notes",
            ],
        )
        w.writeheader()
        for r in holdout_rows_by_type:
            w.writerow(r)

    fp_path = out_dir / "false_positive_audit.csv"
    with fp_path.open("w", newline="", encoding="utf-8") as f_out:
        w = csv.DictWriter(
            f_out,
            fieldnames=[
                "candidate_type",
                "brand",
                "equipment_type",
                "pattern_regex",
                "other_brand_rows",
                "other_brand_matches",
                "other_brand_match_rate",
            ],
        )
        w.writeheader()
        for r in fp_rows:
            w.writerow(r)

    fp_by_type_path = out_dir / "false_positive_audit_by_type.csv"
    with fp_by_type_path.open("w", newline="", encoding="utf-8") as f_out:
        w = csv.DictWriter(
            f_out,
            fieldnames=[
                "candidate_type",
                "brand",
                "equipment_type",
                "pattern_regex",
                "other_brand_rows",
                "other_brand_matches",
                "other_brand_match_rate",
            ],
        )
        w.writeheader()
        for r in fp_rows_by_type:
            w.writerow(r)

    print(str(out_dir))
    return 0
