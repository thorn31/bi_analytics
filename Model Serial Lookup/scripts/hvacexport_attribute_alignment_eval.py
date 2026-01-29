#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.hvacexport_runlib import create_run_dir
from scripts.hvacexport_runlib import utc_compact_ts


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))


def _jsonl_read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def normalize_refrigerant_value(s: str) -> str:
    t = (s or "").strip().upper()
    if not t or t in {"OTHER", "NA", "N/A"}:
        return ""
    # Accept forms: R-22, R22, R-410A, R410A, R-454B, etc.
    m = re.search(r"\bR[- ]?([0-9]{2,4})([A-Z]?)\b", t)
    if not m:
        return ""
    num = m.group(1)
    suf = m.group(2) or ""
    return f"R-{num}{suf}"


def normalize_voltage_value(s: str) -> str:
    """
    Produce canonical: volts[/volts]-phase-60 (Hz assumed 60 for SDI strings).
    Accepts:
      - hvacexport style: 208/230-3-60, 480-3-60
      - SDI style: 208V/230V - Three Phase, 480V - Three Phase, 120 V - Single Phase
    """
    t = (s or "").strip()
    if not t:
        return ""

    up = t.upper().replace(" ", "")
    # hvacexport already normalized: 208/230-3-60
    if re.fullmatch(r"\d{2,4}(/\d{2,4})?-\d-\d{2}", up):
        return up

    # SDI styles
    # Example: 208V/230V-THREEPHASE
    m = re.match(r"^(\d{2,4})V(/(\d{2,4})V)?-(SINGLE|THREE)PHASE$", up.replace("--", "-").replace("—", "-"))
    if m:
        v1 = m.group(1)
        v2 = m.group(3)
        phase = "1" if m.group(4) == "SINGLE" else "3"
        volts = f"{v1}/{v2}" if v2 else v1
        return f"{volts}-{phase}-60"

    # Another SDI possibility: 120V-SINGLEPHASE (no dash)
    m = re.match(r"^(\d{2,4})V(/(\d{2,4})V)?(SINGLE|THREE)PHASE$", up)
    if m:
        v1 = m.group(1)
        v2 = m.group(3)
        phase = "1" if m.group(4) == "SINGLE" else "3"
        volts = f"{v1}/{v2}" if v2 else v1
        return f"{volts}-{phase}-60"

    # 277V- SINGLE PHASE etc with spaces/hyphens in odd places.
    m = re.search(r"(\d{2,4})V(?:/(\d{2,4})V)?", up)
    if m:
        v1 = m.group(1)
        v2 = m.group(2)
        phase = ""
        if "SINGLEPHASE" in up:
            phase = "1"
        elif "THREEPHASE" in up:
            phase = "3"
        if phase:
            volts = f"{v1}/{v2}" if v2 else v1
            return f"{volts}-{phase}-60"

    return ""


@dataclass(frozen=True)
class CandidateRule:
    brand: str
    attribute_name: str
    model_regex: str
    equipment_types: list[str]
    start: int
    end: int
    data_type: str
    mapping: dict[str, Any]
    source_url: str
    def_raw: str


def _candidate_from_obj(obj: dict[str, Any]) -> CandidateRule | None:
    if (obj.get("rule_type") or "").strip() != "decode":
        return None
    attr = (obj.get("attribute_name") or "").strip()
    if attr not in {
        "VoltageVoltPhaseHz",
        "Refrigerant",
        "NominalCapacityTons",
        # staged numeric codes from hvacexport (no SDI truth alignment yet)
        "HVACExport_CoolingCode",
        "HVACExport_CoolingMinCode",
        "HVACExport_CoolingMaxCode",
        "HVACExport_CoolingHundredsCode",
        "HVACExport_CoolingTonCode",
        "HVACExport_CFMTonsCode",
        "HVACExport_TonsCFMCode",
        "HVACExport_LowTonsCFMCode",
        "HVACExport_HighTonsCFMCode",
        "HVACExport_KWCoolingTonsCode",
    }:
        return None
    ve = obj.get("value_extraction") or {}
    if not isinstance(ve, dict):
        return None
    data_type = (ve.get("data_type") or "").strip() or ("Number" if attr.startswith("HVACExport_") else "Text")
    pos = ve.get("positions") or {}
    if not isinstance(pos, dict):
        return None
    try:
        start = int(pos.get("start"))
        end = int(pos.get("end"))
    except Exception:
        return None
    mapping = ve.get("mapping") or {}
    if not isinstance(mapping, dict):
        return None
    # Staged numeric codes may be direct positional extraction with no mapping table.
    if not mapping and not attr.startswith("HVACExport_"):
        return None
    ets = obj.get("equipment_types") or []
    if not isinstance(ets, list):
        ets = []
    ets = [str(x).strip() for x in ets if str(x).strip()]
    return CandidateRule(
        brand=(obj.get("brand") or "").strip(),
        attribute_name=attr,
        model_regex=(obj.get("model_regex") or "").strip(),
        equipment_types=ets,
        start=start,
        end=end,
        data_type=data_type,
        mapping={str(k): v for k, v in mapping.items()},
        source_url=(obj.get("source_url") or "").strip(),
        def_raw=(obj.get("evidence_excerpt") or "").split("DEF=")[-1].split()[0] if "DEF=" in (obj.get("evidence_excerpt") or "") else "",
    )


def _choose_best_rule(rules: list[CandidateRule]) -> CandidateRule:
    # typed over untyped, then longer model_regex.
    rules.sort(key=lambda r: (not bool(r.equipment_types), -len(r.model_regex or ""), r.def_raw, r.start, r.end))
    return rules[0]


def _decode_one_attribute(model: str, rules: list[CandidateRule]) -> tuple[str, CandidateRule | None]:
    for r in rules:
        if r.start < 1 or r.end < r.start or r.end > len(model):
            continue
        code = model[r.start - 1 : r.end]
        if code in r.mapping:
            return str(r.mapping[code]), r
        if code.upper() in r.mapping:
            return str(r.mapping[code.upper()]), r
    return "", None


def _decode_one_number(model: str, rules: list[CandidateRule]) -> tuple[float | None, CandidateRule | None]:
    for r in rules:
        if r.start < 1 or r.end < r.start or r.end > len(model):
            continue
        code = model[r.start - 1 : r.end]
        v = None
        if code in r.mapping:
            v = r.mapping[code]
        elif code.upper() in r.mapping:
            v = r.mapping[code.upper()]
        if v is None:
            continue
        try:
            return float(v), r
        except Exception:
            continue
    return None, None


def _decode_one_numeric_code(model: str, rules: list[CandidateRule]) -> tuple[str, CandidateRule | None]:
    """
    For staged hvacexport metrics where no mapping table is available, extract the raw numeric substring.
    Preserve leading zeros by returning a string.
    """
    for r in rules:
        if r.start < 1 or r.end < r.start or r.end > len(model):
            continue
        code = model[r.start - 1 : r.end]
        if not code or not re.fullmatch(r"\d+", code):
            continue
        return code, r
    return "", None


def _strip_model_for_positions(model: str) -> str:
    """
    SDI ModelNumber often contains separators (spaces, dashes, slashes) that shift positional extraction.
    hvacexport segment positions are typically defined on a compact model string.
    """
    return re.sub(r"[\s\-_/]+", "", (model or "").strip())


def _normalize_model_for_regex(model: str) -> str:
    """
    hvacexport-derived model_regex patterns are built for a restricted alphabet ([A-Z0-9-]).
    SDI ModelNumber fields may include spaces/slashes/etc, so normalize for regex matching.
    """
    return re.sub(r"[^A-Z0-9-]+", "", (model or "").strip().upper())


def run_alignment(
    *,
    snapshot_dir: Path,
    input_sdi: Path,
    candidates_jsonl_paths: list[Path],
    out_prefix: str,
    max_rows: int | None,
    min_brand_support: int,
) -> None:
    from msl.decoder.normalize import normalize_brand, normalize_model

    rows = _read_csv_rows(input_sdi)
    if max_rows is not None:
        rows = rows[: max_rows]

    cand_objs: list[dict[str, Any]] = []
    for p in candidates_jsonl_paths:
        cand_objs.extend(_jsonl_read(p))
    rules: list[CandidateRule] = []
    for obj in cand_objs:
        r = _candidate_from_obj(obj)
        if r:
            rules.append(r)

    # Index rules by brand+attribute, compile regexes.
    by_brand_attr: dict[tuple[str, str], list[tuple[CandidateRule, re.Pattern[str] | None]]] = defaultdict(list)
    for r in rules:
        rx = None
        if r.model_regex:
            try:
                rx = re.compile(r.model_regex)
            except Exception:
                rx = None
        by_brand_attr[(r.brand, r.attribute_name)].append((r, rx))

    run_dir = create_run_dir(snapshot_dir, run_id=out_prefix)
    out_rows_path = run_dir / "alignment_rows.csv"
    out_sum_path = run_dir / "alignment_summary_by_brand_type.csv"
    out_overall_path = run_dir / "alignment_summary_overall.json"
    out_code_suggestions = run_dir / "capacity_code_suggestions.csv"

    # SDI exports sometimes embed newlines in header cells (e.g. "Voltage \r\n(Volt-Phase)").
    # Detect robustly to keep this tool usable across exports and fixtures.
    def _norm_key(k: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", (k or "").lower())

    keys = set()
    if rows:
        keys = set(rows[0].keys())
    voltage_col = ""
    want = _norm_key("Voltage (Volt-Phase)")
    for k in keys:
        nk = _norm_key(k)
        if nk == want:
            voltage_col = k
            break
    if not voltage_col:
        for k in keys:
            nk = _norm_key(k)
            if "voltage" in nk and ("voltphase" in nk or "voltphase" in nk.replace("voltphase", "voltphase")):
                voltage_col = k
                break
    if not voltage_col:
        # Fallback: common variant in some normalized exports.
        for k in keys:
            if "Voltage" in k:
                voltage_col = k
                break
    fields = [
        "Building",
        "Unit ID",
        "EquipmentType",
        "Make",
        "BrandNormalized",
        "ModelNumber",
        "SDI_Refrigerant",
        "SDI_VoltageVoltPhase",
        "SDI_KnownCapacityTons",
        "Decoded_Refrigerant",
        "Decoded_VoltageVoltPhaseHz",
        "Decoded_NominalCapacityTons",
        "Norm_SDI_Refrigerant",
        "Norm_Decoded_Refrigerant",
        "Norm_SDI_Voltage",
        "Norm_Decoded_Voltage",
        "CapacityResult",
        "RefrigerantResult",
        "VoltageResult",
        "RefrigerantRuleEquipmentTypes",
        "RefrigerantRuleModelRegex",
        "RefrigerantRuleStartPos",
        "RefrigerantRuleEndPos",
        "RefrigerantRuleSource",
        "VoltageRuleEquipmentTypes",
        "VoltageRuleModelRegex",
        "VoltageRuleStartPos",
        "VoltageRuleEndPos",
        "VoltageRuleSource",
        "CapacityRuleEquipmentTypes",
        "CapacityRuleModelRegex",
        "CapacityRuleStartPos",
        "CapacityRuleEndPos",
        "CapacityRuleSource",
        "Decoded_HVACExport_CoolingCode",
        "Decoded_HVACExport_CoolingMinCode",
        "Decoded_HVACExport_CoolingMaxCode",
        "Decoded_HVACExport_CoolingHundredsCode",
        "Decoded_HVACExport_CoolingTonCode",
        "Decoded_HVACExport_CFMTonsCode",
        "Decoded_HVACExport_TonsCFMCode",
        "Decoded_HVACExport_LowTonsCFMCode",
        "Decoded_HVACExport_HighTonsCFMCode",
        "Decoded_HVACExport_KWCoolingTonsCode",
    ]

    # Stats by (brand,type)
    stats: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    # For staged code->tons suggestions (derived from labeled SDI truth)
    # Keyed by the specific extraction rule used (regex + positions), so mappings are auditable and can be
    # promoted into deterministic mapping rules later.
    code_truth_counts: dict[tuple[str, str, str, str, int, int, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def _eval_one(attr: str, truth_raw: str, decoded_raw: str) -> tuple[str, str, str]:
        if not truth_raw.strip():
            return "truth_missing", "", ""
        if attr == "Refrigerant":
            tnorm = normalize_refrigerant_value(truth_raw)
            dnorm = normalize_refrigerant_value(decoded_raw)
        else:
            tnorm = normalize_voltage_value(truth_raw)
            dnorm = normalize_voltage_value(decoded_raw)
        if not tnorm:
            return "uncomparable", tnorm, dnorm
        if not decoded_raw:
            return "no_decode", tnorm, dnorm
        if not dnorm:
            return "uncomparable", tnorm, dnorm
        return ("match" if tnorm == dnorm else "mismatch"), tnorm, dnorm

    def _eval_capacity(truth_raw: str, decoded_value: float | None, tol: float = 0.25) -> str:
        t = (truth_raw or "").strip()
        if not t:
            return "truth_missing"
        try:
            truth = float(t)
        except Exception:
            return "uncomparable"
        if decoded_value is None:
            return "no_decode"
        return "match" if abs(decoded_value - truth) <= tol else "mismatch"

    with out_rows_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            make = (row.get("Make") or "").strip()
            brand = normalize_brand(make)
            equip_type = (row.get("EquipmentType") or "").strip()
            model = normalize_model(row.get("ModelNumber") or "")
            model_for_regex = _normalize_model_for_regex(model)
            model_compact = _strip_model_for_positions(model_for_regex)
            building = (row.get("Building") or "").strip()
            unit_id = (row.get("Unit ID") or "").strip()

            sdi_ref = (row.get("Refrigerant") or "").strip()
            sdi_volt = (row.get(voltage_col) or "").strip()
            sdi_cap = (row.get("KnownCapacityTons") or "").strip()

            # Collect matching rules for each attribute.
            decoded_ref = ""
            decoded_volt = ""
            decoded_cap: float | None = None
            decoded_codes: dict[str, str] = {}
            ref_rule: CandidateRule | None = None
            volt_rule: CandidateRule | None = None
            cap_rule: CandidateRule | None = None

            # Refrigerant
            candidates_for_ref: list[CandidateRule] = []
            for r, rx in by_brand_attr.get((brand, "Refrigerant"), []):
                if r.equipment_types and equip_type and equip_type not in r.equipment_types:
                    continue
                if rx and not rx.search(model_for_regex):
                    continue
                candidates_for_ref.append(r)
            if candidates_for_ref:
                ref_rule = _choose_best_rule(candidates_for_ref)
                # decode using only the best rule (avoid confusing side effects)
                decoded_ref, _ = _decode_one_attribute(model_for_regex, [ref_rule])
                if not decoded_ref:
                    decoded_ref, _ = _decode_one_attribute(model_compact, [ref_rule])

            # Voltage
            candidates_for_volt: list[CandidateRule] = []
            for r, rx in by_brand_attr.get((brand, "VoltageVoltPhaseHz"), []):
                if r.equipment_types and equip_type and equip_type not in r.equipment_types:
                    continue
                if rx and not rx.search(model_for_regex):
                    continue
                candidates_for_volt.append(r)
            if candidates_for_volt:
                volt_rule = _choose_best_rule(candidates_for_volt)
                decoded_volt, _ = _decode_one_attribute(model_for_regex, [volt_rule])
                if not decoded_volt:
                    decoded_volt, _ = _decode_one_attribute(model_compact, [volt_rule])

            # Capacity (NominalCapacityTons)
            candidates_for_cap: list[CandidateRule] = []
            for r, rx in by_brand_attr.get((brand, "NominalCapacityTons"), []):
                if r.equipment_types and equip_type and equip_type not in r.equipment_types:
                    continue
                if rx and not rx.search(model_for_regex):
                    continue
                candidates_for_cap.append(r)
            if candidates_for_cap:
                cap_rule = _choose_best_rule(candidates_for_cap)
                decoded_cap, _ = _decode_one_number(model_for_regex, [cap_rule])
                if decoded_cap is None:
                    decoded_cap, _ = _decode_one_number(model_compact, [cap_rule])

            # Staged code metrics (no match/mismatch evaluation yet; emit for audit)
            code_attrs = [
                "HVACExport_CoolingCode",
                "HVACExport_CoolingMinCode",
                "HVACExport_CoolingMaxCode",
                "HVACExport_CoolingHundredsCode",
                "HVACExport_CoolingTonCode",
                "HVACExport_CFMTonsCode",
                "HVACExport_TonsCFMCode",
                "HVACExport_LowTonsCFMCode",
                "HVACExport_HighTonsCFMCode",
                "HVACExport_KWCoolingTonsCode",
            ]
            for attr in code_attrs:
                candidates_for_code: list[CandidateRule] = []
                for r, rx in by_brand_attr.get((brand, attr), []):
                    if r.equipment_types and equip_type and equip_type not in r.equipment_types:
                        continue
                    if rx and not rx.search(model_for_regex):
                        continue
                    candidates_for_code.append(r)
                if not candidates_for_code:
                    continue
                best = _choose_best_rule(candidates_for_code)
                v, _ = _decode_one_numeric_code(model_for_regex, [best])
                if not v:
                    v, _ = _decode_one_numeric_code(model_compact, [best])
                if v:
                    decoded_codes[attr] = v
                    # Build code->tons suggestions from labeled truth (for later mapping work).
                    if sdi_cap.strip():
                        try:
                            truth_tons = float(sdi_cap.strip())
                            truth_key = f"{truth_tons:.3f}".rstrip("0").rstrip(".")
                            code_truth_counts[(brand, equip_type, attr, best.model_regex, best.start, best.end, v)][truth_key] += 1
                        except Exception:
                            pass

            # Evaluate
            ref_res, norm_sdi_ref, norm_dec_ref = _eval_one("Refrigerant", sdi_ref, decoded_ref)
            volt_res, norm_sdi_volt, norm_dec_volt = _eval_one("Voltage", sdi_volt, decoded_volt)
            cap_res = _eval_capacity(sdi_cap, decoded_cap)

            key = (brand, equip_type)
            for attr_name, truth, dec, res in [
                ("Refrigerant", sdi_ref, decoded_ref, ref_res),
                ("Voltage", sdi_volt, decoded_volt, volt_res),
            ]:
                if truth.strip():
                    stats[key][f"{attr_name}_TruthN"] += 1
                    if dec:
                        stats[key][f"{attr_name}_DecodedN"] += 1
                    if res == "match":
                        stats[key][f"{attr_name}_MatchN"] += 1
                    if res == "mismatch":
                        stats[key][f"{attr_name}_MismatchN"] += 1
                    if res == "uncomparable":
                        stats[key][f"{attr_name}_UncomparableN"] += 1

            if sdi_cap.strip():
                stats[key]["Capacity_TruthN"] += 1
                if decoded_cap is not None:
                    stats[key]["Capacity_DecodedN"] += 1
                if cap_res == "match":
                    stats[key]["Capacity_MatchN"] += 1
                if cap_res == "mismatch":
                    stats[key]["Capacity_MismatchN"] += 1
                if cap_res == "uncomparable":
                    stats[key]["Capacity_UncomparableN"] += 1

            w.writerow(
                {
                    "Building": building,
                    "Unit ID": unit_id,
                    "EquipmentType": equip_type,
                    "Make": make,
                    "BrandNormalized": brand,
                    "ModelNumber": model,
                    "SDI_Refrigerant": sdi_ref,
                    "SDI_VoltageVoltPhase": sdi_volt,
                    "SDI_KnownCapacityTons": sdi_cap,
                    "Decoded_Refrigerant": decoded_ref,
                    "Decoded_VoltageVoltPhaseHz": decoded_volt,
                    "Decoded_NominalCapacityTons": (f"{decoded_cap:.3f}".rstrip("0").rstrip(".") if decoded_cap is not None else ""),
                    "Norm_SDI_Refrigerant": norm_sdi_ref,
                    "Norm_Decoded_Refrigerant": norm_dec_ref,
                    "Norm_SDI_Voltage": norm_sdi_volt,
                    "Norm_Decoded_Voltage": norm_dec_volt,
                    "CapacityResult": cap_res,
                    "RefrigerantResult": ref_res,
                    "VoltageResult": volt_res,
                    "RefrigerantRuleEquipmentTypes": json.dumps(ref_rule.equipment_types, ensure_ascii=False) if ref_rule else "",
                    "RefrigerantRuleModelRegex": ref_rule.model_regex if ref_rule else "",
                    "RefrigerantRuleStartPos": str(ref_rule.start) if ref_rule else "",
                    "RefrigerantRuleEndPos": str(ref_rule.end) if ref_rule else "",
                    "RefrigerantRuleSource": ref_rule.source_url if ref_rule else "",
                    "VoltageRuleEquipmentTypes": json.dumps(volt_rule.equipment_types, ensure_ascii=False) if volt_rule else "",
                    "VoltageRuleModelRegex": volt_rule.model_regex if volt_rule else "",
                    "VoltageRuleStartPos": str(volt_rule.start) if volt_rule else "",
                    "VoltageRuleEndPos": str(volt_rule.end) if volt_rule else "",
                    "VoltageRuleSource": volt_rule.source_url if volt_rule else "",
                    "CapacityRuleEquipmentTypes": json.dumps(cap_rule.equipment_types, ensure_ascii=False) if cap_rule else "",
                    "CapacityRuleModelRegex": cap_rule.model_regex if cap_rule else "",
                    "CapacityRuleStartPos": str(cap_rule.start) if cap_rule else "",
                    "CapacityRuleEndPos": str(cap_rule.end) if cap_rule else "",
                    "CapacityRuleSource": cap_rule.source_url if cap_rule else "",
                    "Decoded_HVACExport_CoolingCode": decoded_codes.get("HVACExport_CoolingCode", ""),
                    "Decoded_HVACExport_CoolingMinCode": decoded_codes.get("HVACExport_CoolingMinCode", ""),
                    "Decoded_HVACExport_CoolingMaxCode": decoded_codes.get("HVACExport_CoolingMaxCode", ""),
                    "Decoded_HVACExport_CoolingHundredsCode": decoded_codes.get("HVACExport_CoolingHundredsCode", ""),
                    "Decoded_HVACExport_CoolingTonCode": decoded_codes.get("HVACExport_CoolingTonCode", ""),
                    "Decoded_HVACExport_CFMTonsCode": decoded_codes.get("HVACExport_CFMTonsCode", ""),
                    "Decoded_HVACExport_TonsCFMCode": decoded_codes.get("HVACExport_TonsCFMCode", ""),
                    "Decoded_HVACExport_LowTonsCFMCode": decoded_codes.get("HVACExport_LowTonsCFMCode", ""),
                    "Decoded_HVACExport_HighTonsCFMCode": decoded_codes.get("HVACExport_HighTonsCFMCode", ""),
                    "Decoded_HVACExport_KWCoolingTonsCode": decoded_codes.get("HVACExport_KWCoolingTonsCode", ""),
                }
            )

    # Summary by brand/type
    sum_fields = [
        "BrandNormalized",
        "EquipmentType",
        "Capacity_TruthN",
        "Capacity_DecodedN",
        "Capacity_MatchN",
        "Capacity_MismatchN",
        "Capacity_UncomparableN",
        "Capacity_CoveragePct",
        "Capacity_AccuracyPct",
        "Refrigerant_TruthN",
        "Refrigerant_DecodedN",
        "Refrigerant_MatchN",
        "Refrigerant_MismatchN",
        "Refrigerant_UncomparableN",
        "Refrigerant_CoveragePct",
        "Refrigerant_AccuracyPct",
        "Voltage_TruthN",
        "Voltage_DecodedN",
        "Voltage_MatchN",
        "Voltage_MismatchN",
        "Voltage_UncomparableN",
        "Voltage_CoveragePct",
        "Voltage_AccuracyPct",
    ]

    def pct(a: int, b: int) -> str:
        if b <= 0:
            return ""
        return f"{(a / b * 100.0):.1f}"

    out_sum_rows: list[dict[str, str]] = []
    for (brand, et), m in sorted(stats.items()):
        # filter tiny brands if requested
        if min_brand_support and sum(m.get(k, 0) for k in ["Refrigerant_TruthN", "Voltage_TruthN", "Capacity_TruthN"]) < min_brand_support:
            continue
        ct = int(m.get("Capacity_TruthN", 0))
        cd = int(m.get("Capacity_DecodedN", 0))
        cm = int(m.get("Capacity_MatchN", 0))
        cmm = int(m.get("Capacity_MismatchN", 0))
        cu = int(m.get("Capacity_UncomparableN", 0))
        rt = int(m.get("Refrigerant_TruthN", 0))
        rd = int(m.get("Refrigerant_DecodedN", 0))
        rm = int(m.get("Refrigerant_MatchN", 0))
        rmm = int(m.get("Refrigerant_MismatchN", 0))
        ru = int(m.get("Refrigerant_UncomparableN", 0))

        vt = int(m.get("Voltage_TruthN", 0))
        vd = int(m.get("Voltage_DecodedN", 0))
        vm = int(m.get("Voltage_MatchN", 0))
        vmm = int(m.get("Voltage_MismatchN", 0))
        vu = int(m.get("Voltage_UncomparableN", 0))

        out_sum_rows.append(
            {
                "BrandNormalized": brand,
                "EquipmentType": et,
                "Capacity_TruthN": str(ct),
                "Capacity_DecodedN": str(cd),
                "Capacity_MatchN": str(cm),
                "Capacity_MismatchN": str(cmm),
                "Capacity_UncomparableN": str(cu),
                "Capacity_CoveragePct": pct(cd, ct),
                "Capacity_AccuracyPct": pct(cm, cd),
                "Refrigerant_TruthN": str(rt),
                "Refrigerant_DecodedN": str(rd),
                "Refrigerant_MatchN": str(rm),
                "Refrigerant_MismatchN": str(rmm),
                "Refrigerant_UncomparableN": str(ru),
                "Refrigerant_CoveragePct": pct(rd, rt),
                "Refrigerant_AccuracyPct": pct(rm, rd),
                "Voltage_TruthN": str(vt),
                "Voltage_DecodedN": str(vd),
                "Voltage_MatchN": str(vm),
                "Voltage_MismatchN": str(vmm),
                "Voltage_UncomparableN": str(vu),
                "Voltage_CoveragePct": pct(vd, vt),
                "Voltage_AccuracyPct": pct(vm, vd),
            }
        )

    with out_sum_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sum_fields)
        w.writeheader()
        for r in out_sum_rows:
            w.writerow({k: r.get(k, "") for k in sum_fields})

    overall = {
        "rows_written": len(rows),
        "summary_rows_written": len(out_sum_rows),
        "candidates_rules_n": len(rules),
        "capacity_code_keys_n": len(code_truth_counts),
    }
    out_overall_path.write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")

    # Code->tons suggestions: derived from labeled SDI truth. This does NOT change candidates/rulesets;
    # it is an audit artifact to help decide which code attributes can be safely mapped to tons later.
    with out_code_suggestions.open("w", newline="", encoding="utf-8") as f:
        fields2 = [
            "BrandNormalized",
            "EquipmentType",
            "AttributeName",
            "RuleModelRegex",
            "RuleStartPos",
            "RuleEndPos",
            "Code",
            "SupportN",
            "MostCommonTons",
            "MostCommonTonsN",
            "PurityPct",
            "UniqueTruthTonsN",
            "TruthTonsValuesJson",
        ]
        w2 = csv.DictWriter(f, fieldnames=fields2)
        w2.writeheader()
        for (b, et, attr, model_regex, start, end, code), dist in sorted(code_truth_counts.items()):
            support = sum(dist.values())
            if support <= 0:
                continue
            most_tons, most_n = max(dist.items(), key=lambda kv: kv[1])
            purity = most_n / support * 100.0
            w2.writerow(
                {
                    "BrandNormalized": b,
                    "EquipmentType": et,
                    "AttributeName": attr,
                    "RuleModelRegex": model_regex,
                    "RuleStartPos": str(start),
                    "RuleEndPos": str(end),
                    "Code": code,
                    "SupportN": str(support),
                    "MostCommonTons": most_tons,
                    "MostCommonTonsN": str(most_n),
                    "PurityPct": f"{purity:.1f}",
                    "UniqueTruthTonsN": str(len(dist)),
                    "TruthTonsValuesJson": json.dumps(dist, sort_keys=True),
                }
            )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hvacexport_attribute_alignment_eval", description="Evaluate hvacexport-derived candidates against SDI normalized data")
    ap.add_argument("--snapshot-id", required=True)
    ap.add_argument("--hvacexport-root", default=str(REPO_ROOT / "data" / "external_sources" / "hvacexport"))
    ap.add_argument("--input-sdi", default=str(REPO_ROOT / "data" / "equipment_exports" / "2026-01-25" / "sdi_equipment_normalized.csv"))
    ap.add_argument("--candidates-jsonl", default="", help="Path to candidates JSONL. If omitted, uses derived/LATEST_CANDIDATES.txt")
    ap.add_argument("--run-id", default="", help="Run folder name under derived/runs/ (default: autogenerated)")
    ap.add_argument("--max-rows", type=int, default=0)
    ap.add_argument("--min-brand-support", type=int, default=25)
    args = ap.parse_args(argv)

    snap_dir = Path(args.hvacexport_root) / str(args.snapshot_id)
    candidates_paths: list[Path] = []
    if (args.candidates_jsonl or "").strip():
        candidates_paths = [Path(p.strip()) for p in str(args.candidates_jsonl).split(",") if p.strip()]
    if not candidates_paths:
        latest = snap_dir / "derived" / "LATEST_CANDIDATES.txt"
        if not latest.exists():
            raise SystemExit("Missing --candidates-jsonl and no derived/LATEST_CANDIDATES.txt present. Run candidate generation first.")
        rel = latest.read_text(encoding="utf-8").strip()
        candidates_paths = [Path(rel)]

    resolved: list[Path] = []
    for p in candidates_paths:
        pp = p
        if not pp.is_absolute():
            pp = snap_dir / pp
        resolved.append(pp)

    run_alignment(
        snapshot_dir=snap_dir,
        input_sdi=Path(args.input_sdi),
        candidates_jsonl_paths=resolved,
        out_prefix=((args.run_id or "").strip() or f"alignment__{utc_compact_ts()}"),
        max_rows=(int(args.max_rows) if int(args.max_rows) > 0 else None),
        min_brand_support=int(args.min_brand_support),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
