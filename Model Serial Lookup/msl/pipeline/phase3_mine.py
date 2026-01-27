from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from msl.decoder.io import load_brand_normalize_rules_csv, load_serial_rules_csv
from msl.decoder.normalize import normalize_brand, normalize_serial, normalize_text
from msl.pipeline.common import ensure_dir
from msl.pipeline.phase3_baseline import infer_column_map, _as_int
from msl.pipeline.ruleset_manager import resolve_ruleset_dir


def _utc_run_id(prefix: str) -> str:
    ts = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace(":", "").replace("+00:00", "Z")
    return f"{prefix}-{ts}"


def _stable_split_key(value: str) -> int:
    h = hashlib.sha256(value.encode("utf-8", errors="ignore")).digest()
    return int.from_bytes(h[:4], "big")


def _train_holdout(is_train_key: int, train_pct: int = 80) -> str:
    return "train" if (is_train_key % 100) < train_pct else "holdout"


def _signature_regex(signature: str) -> str:
    # signature like "AANNNA" where A=letter, N=digit
    parts: list[str] = ["^"]
    for ch in signature:
        if ch == "A":
            parts.append(r"[A-Z]")
        elif ch == "N":
            parts.append(r"\d")
        else:
            parts.append(re.escape(ch))
    parts.append("$")
    return "".join(parts)


def _serial_signature(serial: str) -> str:
    s = normalize_serial(serial)
    out = []
    for ch in s:
        if "A" <= ch <= "Z":
            out.append("A")
        elif ch.isdigit():
            out.append("N")
        else:
            out.append("?")
    return "".join(out)


@dataclass(frozen=True)
class YearCandidate:
    brand: str
    signature: str
    length: int
    pos_start: int
    pos_end: int
    transform: dict | None
    support_n: int
    train_accuracy: float
    holdout_accuracy: float
    collisions_other_brands: int


def _best_year_rule_for_group(rows: list[tuple[str, int]]) -> YearCandidate | None:
    """
    rows: list of (serial_normalized, known_year)
    Returns a candidate where a substring maps to year with high accuracy.
    """
    if len(rows) < 50:
        return None
    sig = _serial_signature(rows[0][0])
    length = len(rows[0][0])
    if any(len(s) != length or _serial_signature(s) != sig for s, _y in rows[:200]):
        return None

    # Pre-split train/holdout deterministically.
    train = []
    holdout = []
    for s, y in rows:
        split = _train_holdout(_stable_split_key(s))
        (train if split == "train" else holdout).append((s, y))

    if len(train) < 40 or len(holdout) < 10:
        return None

    def eval_positions(start: int, width: int, base: int | None) -> tuple[float, float] | None:
        end = start + width - 1
        def acc(bucket: list[tuple[str, int]]) -> float:
            ok = 0
            for s, y in bucket:
                sub = s[start - 1 : end]
                if not sub.isdigit():
                    continue
                val = int(sub)
                if base is not None:
                    val = base + val
                if val == y:
                    ok += 1
            return ok / len(bucket)
        return acc(train), acc(holdout)

    # Candidate search (4-digit direct first, then 2-digit base=2000).
    best: tuple[float, float, int, int, dict | None] | None = None

    # 4-digit year in-line.
    for start in range(1, length - 4 + 2):
        train_acc, hold_acc = eval_positions(start, 4, None)
        if train_acc >= 0.90 and hold_acc >= 0.90:
            score = (train_acc + hold_acc) / 2.0
            if best is None or score > (best[0] + best[1]) / 2.0:
                best = (train_acc, hold_acc, start, start + 3, None)

    # 2-digit year code (base 2000) if all years are >= 2000 and <= 2099.
    years = [y for _s, y in rows]
    if years and min(years) >= 2000 and max(years) <= 2099:
        for start in range(1, length - 2 + 2):
            train_acc, hold_acc = eval_positions(start, 2, 2000)
            if train_acc >= 0.90 and hold_acc >= 0.90:
                score = (train_acc + hold_acc) / 2.0
                if best is None or score > (best[0] + best[1]) / 2.0:
                    best = (
                        train_acc,
                        hold_acc,
                        start,
                        start + 1,
                        {"type": "year_add_base", "base": 2000, "min_year": min(years), "max_year": max(years)},
                    )

    if not best:
        return None
    train_acc, hold_acc, ps, pe, transform = best

    return YearCandidate(
        brand="",
        signature=sig,
        length=length,
        pos_start=ps,
        pos_end=pe,
        transform=transform,
        support_n=len(rows),
        train_accuracy=train_acc,
        holdout_accuracy=hold_acc,
        collisions_other_brands=0,
    )


def cmd_phase3_mine(args) -> int:
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    ruleset_dir = resolve_ruleset_dir(getattr(args, "ruleset_dir", None) or None)
    if not ruleset_dir or not ruleset_dir.exists():
        raise SystemExit("--ruleset-dir is required and must exist, or CURRENT.txt must point to a valid ruleset")

    run_id = args.run_id or _utc_run_id("phase3-mine")
    out_candidates_dir = ensure_dir(Path(args.out_candidates_dir) / run_id / "candidates")
    out_reports_dir = ensure_dir(Path(args.out_reports_dir) / run_id)

    # Known brands from the existing ruleset (used for brand-normalization candidate suggestions).
    existing_rules = load_serial_rules_csv(ruleset_dir / "SerialDecodeRule.csv")
    known_brands = sorted({r.brand for r in existing_rules if r.brand})

    brand_alias_map: dict[str, str] = {}
    brand_rules_csv = ruleset_dir / "BrandNormalizeRule.csv"
    if brand_rules_csv.exists():
        brand_alias_map = load_brand_normalize_rules_csv(brand_rules_csv)

    with input_path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("Input CSV missing header row")
        cmap = infer_column_map(reader.fieldnames)
        if not cmap.make:
            raise SystemExit("Could not infer Make/Manufacturer column")

        # Brand-normalization candidate suggestions.
        raw_make_counts: Counter[str] = Counter()
        raw_make_examples: dict[str, list[str]] = defaultdict(list)
        for row in reader:
            raw = (row.get(cmap.make) or "").strip()
            if not raw:
                continue
            key = normalize_text(raw)
            raw_make_counts[key] += 1
            if len(raw_make_examples[key]) < 5 and raw not in raw_make_examples[key]:
                raw_make_examples[key].append(raw)

    # Suggest mappings for raw makes that do not already map cleanly to a known brand.
    cand_brand_path = out_candidates_dir / "BrandNormalizeRule.candidates.csv"
    with cand_brand_path.open("w", newline="", encoding="utf-8") as f_out:
        w = csv.DictWriter(
            f_out,
            fieldnames=["raw_make", "support_n", "current_normalize_brand", "suggested_brand", "similarity", "examples"],
        )
        w.writeheader()

        for raw_make, n in raw_make_counts.most_common():
            current = normalize_brand(raw_make)
            # Find closest known brand by SequenceMatcher (stdlib) on compacted text.
            raw_comp = re.sub(r"[^A-Z0-9]", "", raw_make.upper())
            best_brand = ""
            best_score = 0.0
            for b in known_brands:
                b_comp = re.sub(r"[^A-Z0-9]", "", b.upper())
                if raw_comp == b_comp:
                    best_score = 1.0
                    best_brand = b
                    break
                score = SequenceMatcher(a=raw_comp, b=b_comp).ratio()
                if score > best_score:
                    best_score = score
                    best_brand = b
            
            # If we found an exact match (identity), we don't need a normalization rule.
            if best_score == 1.0:
                continue

            if best_score < float(args.min_brand_similarity):
                continue
            w.writerow(
                {
                    "raw_make": raw_make,
                    "support_n": n,
                    "current_normalize_brand": current,
                    "suggested_brand": best_brand,
                    "similarity": f"{best_score:.3f}",
                    "examples": json.dumps(raw_make_examples.get(raw_make, []), ensure_ascii=False),
                }
            )

    # Serial-year candidate mining (limited MVP: year positions only).
    # Re-read CSV (DictReader is one-pass).
    rows_by_brand_group: dict[tuple[str, int, str], list[tuple[str, int]]] = defaultdict(list)
    with input_path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        cmap = infer_column_map(reader.fieldnames or [])
        if not cmap.make or not cmap.serial or not cmap.known_year:
            summary_path = out_reports_dir / "phase3_rule_discovery_summary.md"
            summary_path.write_text(
                "# Phase 3 Rule Discovery Summary\n\n"
                "- Serial-year mining skipped: missing one of required columns (Make/Serial/KnownManufactureYear).\n",
                encoding="utf-8",
            )
            print(str(out_reports_dir.parent))
            return 0

        for row in reader:
            make = normalize_brand((row.get(cmap.make) or "").strip(), brand_alias_map)
            serial_raw = (row.get(cmap.serial) or "").strip()
            known_year = _as_int((row.get(cmap.known_year) or "").strip())
            if not make or make == "UNKNOWN":
                continue
            if not serial_raw or known_year is None:
                continue
            serial = normalize_serial(serial_raw)
            if not serial:
                continue
            sig = _serial_signature(serial)
            key = (make, len(serial), sig)
            rows_by_brand_group[key].append((serial, known_year))

    # Evaluate best candidate per (brand,length,signature) group.
    candidates: list[YearCandidate] = []
    for (brand, length, sig), rows in rows_by_brand_group.items():
        if len(rows) < int(args.min_serial_support):
            continue
        # Stable: sample first 2000 for speed, but keep deterministic order.
        rows2 = sorted(rows, key=lambda x: (x[0], x[1]))[:2000]
        cand = _best_year_rule_for_group(rows2)
        if not cand:
            continue
        # Collision check: how many other-brand serials match this regex?
        rx = re.compile(_signature_regex(sig))
        collisions = 0
        for (b2, l2, sig2), rows_other in rows_by_brand_group.items():
            if b2 == brand:
                continue
            if l2 != length or sig2 != sig:
                continue
            # Any match indicates collision risk for brand-less application; still ok if Phase 2 filters by brand.
            # Count a small sample.
            collisions += min(50, len(rows_other))
        candidates.append(
            YearCandidate(
                brand=brand,
                signature=sig,
                length=length,
                pos_start=cand.pos_start,
                pos_end=cand.pos_end,
                transform=cand.transform,
                support_n=cand.support_n,
                train_accuracy=cand.train_accuracy,
                holdout_accuracy=cand.holdout_accuracy,
                collisions_other_brands=collisions,
            )
        )

    # Write candidates JSONL in SerialDecodeRule-like shape with metrics.
    serial_cand_path = out_candidates_dir / "SerialDecodeRule.candidates.jsonl"
    with serial_cand_path.open("w", encoding="utf-8") as f_out:
        for c in sorted(candidates, key=lambda x: (-x.support_n, -x.holdout_accuracy, x.brand, x.length)):
            date_fields = {"year": {"positions": {"start": c.pos_start, "end": c.pos_end}}}
            if c.transform:
                date_fields["year"]["transform"] = c.transform
            obj = {
                "rule_type": "decode",
                "brand": c.brand,
                "style_name": f"PHASE3 mined year @ {c.pos_start}-{c.pos_end} ({c.signature})",
                "serial_regex": _signature_regex(c.signature),
                "date_fields": date_fields,
                "example_serials": [],
                "decade_ambiguity": {"is_ambiguous": True, "notes": "Mined from asset report; validate before promotion"},
                "evidence_excerpt": f"VERIFIED: Rule matches {c.support_n} assets with {c.holdout_accuracy:.1%} accuracy via holdout validation.",
                "source_url": "internal_asset_reports",
                "retrieved_on": dt.date.today().isoformat(),
                "image_urls": [],
                "support_n": c.support_n,
                "train_accuracy": round(c.train_accuracy, 4),
                "holdout_accuracy": round(c.holdout_accuracy, 4),
                "collisions_other_brands": c.collisions_other_brands,
            }
            f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")

    # Scorecard CSV
    score_path = out_reports_dir / "candidate_rule_scorecard.csv"
    with score_path.open("w", newline="", encoding="utf-8") as f_score:
        w = csv.DictWriter(
            f_score,
            fieldnames=[
                "candidate_type",
                "brand",
                "length",
                "signature",
                "year_pos_start",
                "year_pos_end",
                "support_n",
                "train_accuracy",
                "holdout_accuracy",
                "collisions_other_brands",
            ],
        )
        w.writeheader()
        for c in sorted(candidates, key=lambda x: (-x.support_n, -x.holdout_accuracy, x.brand, x.length)):
            w.writerow(
                {
                    "candidate_type": "SerialDecodeRule.year",
                    "brand": c.brand,
                    "length": c.length,
                    "signature": c.signature,
                    "year_pos_start": c.pos_start,
                    "year_pos_end": c.pos_end,
                    "support_n": c.support_n,
                    "train_accuracy": f"{c.train_accuracy:.4f}",
                    "holdout_accuracy": f"{c.holdout_accuracy:.4f}",
                    "collisions_other_brands": c.collisions_other_brands,
                }
            )

    summary_path = out_reports_dir / "phase3_rule_discovery_summary.md"
    summary_path.write_text(
        "# Phase 3 Rule Discovery Summary\n\n"
        f"- Input: `{input_path}`\n"
        f"- Ruleset: `{ruleset_dir}`\n"
        f"- Run ID: `{run_id}`\n\n"
        "## Outputs\n"
        f"- Brand normalization candidates: `{cand_brand_path}`\n"
        f"- Serial year candidates: `{serial_cand_path}`\n"
        f"- Candidate scorecard: `{score_path}`\n",
        encoding="utf-8",
    )

    # -------------------------
    # Attribute capacity mining
    # -------------------------
    def find_col(name_candidates: list[str]) -> str | None:
        # Use the same normalization strategy as phase3-baseline.
        with input_path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f2:
            r2 = csv.DictReader(f2)
            fns = r2.fieldnames or []
        norm = {normalize_text(c): c for c in fns}
        for cand in name_candidates:
            key = normalize_text(cand)
            if key in norm:
                return norm[key]
        return None

    col_model = find_col(["ModelNumber", "Model #", "Model", "modelNumber"])
    col_equipment = find_col(["EquipmentType", "Equipment", "Type", "equipmentType", "description"])
    col_cap_val = find_col(["Cooling Capacity \n(Input)", "Cooling Capacity (Input)", "Cooling Capacity", "CoolingCapacity"])
    col_cap_unit = find_col(["Cooling Capacity \n(Unit)", "Cooling Capacity (Unit)", "Cooling Capacity Unit", "CoolingCapacityUnit"])

    def parse_tons(val: str | None, unit: str | None) -> float | None:
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
        if not u:
            return None
        if u in {"TON", "TONS"}:
            return num
        if u in {"BTUH", "BTU/H", "BTUHR", "BTU/HR"}:
            return num / 12000.0
        if u in {"MBH", "MBTUH"}:
            return (num * 1000.0) / 12000.0
        return None

    @dataclass(frozen=True)
    class CapacityCandidate:
        brand: str
        equipment_type: str
        model_regex: str
        token_index: int
        token_width: int
        pattern_regex: str
        transform: dict | None
        mapping: dict | None
        support_n: int
        match_n: int
        train_accuracy: float
        holdout_accuracy: float

    def extract_numeric_tokens(model: str) -> list[str]:
        m = normalize_text(model)
        if not m:
            return []
        return re.findall(r"\d+", m)

    def build_kth_token_regex(k: int, width: int) -> str:
        # Capture the k-th numeric token (1-based) if it is exactly `width` digits.
        # Note: tokens are digit runs separated by non-digits.
        return rf"^(?:\D*\d+){{{k-1}}}\D*(\d{{{width}}})(?!\d)"

    def split_rows(rows: list[tuple[str, str, float]]) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
        train = []
        hold = []
        for split_key, model, tons in rows:
            split = _train_holdout(_stable_split_key(split_key))
            (train if split == "train" else hold).append((model, tons))
        return train, hold

    def acc_for_rule(rows: list[tuple[str, float]], rx: re.Pattern, transform: dict | None, mapping: dict | None, tol: float) -> float:
        if not rows:
            return 0.0
        ok = 0
        denom = 0
        for model, tons in rows:
            m = rx.search(model)
            if not m:
                continue
            code = m.group(1)
            pred = None
            if mapping is not None:
                if code in mapping:
                    pred = float(mapping[code])
            elif transform is not None and transform.get("expression") == "tons = code / 12":
                if code.isdigit():
                    pred = float(int(code)) / 12.0
            else:
                # direct numeric
                if code.isdigit():
                    pred = float(int(code))
            if pred is None:
                continue
            denom += 1
            if abs(pred - tons) <= tol:
                ok += 1
        if denom == 0:
            return 0.0
        return ok / denom

    def mine_capacity_candidates(group_rows: list[tuple[str, str, float]], brand: str, equipment_type: str) -> list[CapacityCandidate]:
        # group_rows: (model_normalized_text, tons)
        if len(group_rows) < int(args.min_model_support):
            return []
        train, holdout = split_rows(group_rows)
        if len(train) < int(args.min_model_support) * 0.6 or len(holdout) < 10:
            return []

        tol = float(args.capacity_tolerance_tons)
        best: CapacityCandidate | None = None

        def compute_model_regex_for_matches(models: list[str]) -> str:
            # Build a conservative anchored prefix regex from the compact model prefix distribution.
            # Goal: reduce false positives by restricting to common starting families for this group.
            if not models:
                return ""
            counts: Counter[str] = Counter()
            for m in models:
                compact = re.sub(r"[^A-Z0-9]", "", normalize_text(m))
                if len(compact) < 4:
                    continue
                counts[compact[:4]] += 1
            if not counts:
                return ""
            total = sum(counts.values())
            chosen: list[str] = []
            covered = 0
            for pref, n in counts.most_common(20):
                share = n / total if total else 0.0
                if share < 0.05:
                    continue
                chosen.append(pref)
                covered += n
                if covered / total >= 0.95:
                    break
            if not chosen:
                # Fall back to the most common prefix only if it dominates.
                pref, n = counts.most_common(1)[0]
                if (n / total) >= 0.70:
                    chosen = [pref]
            if not chosen:
                return ""
            # Allow separators between characters (e.g., RN-01 should match RN01).
            def sep_tolerant(prefix: str) -> str:
                parts = []
                for ch in prefix:
                    parts.append(re.escape(ch))
                return r"^" + r"[^A-Z0-9]*".join(parts)

            return r"(?:" + "|".join([sep_tolerant(p) for p in chosen]) + r")"

        # Consider k-th numeric token rules for width 3 (BTU code /12) and width 2 (direct tons).
        for width, transform in [(3, {"expression": "tons = code / 12"}), (2, None)]:
            for k in range(1, 6):
                pat = build_kth_token_regex(k, width)
                try:
                    rx = re.compile(pat)
                except Exception:
                    continue

                # Compute match count.
                match_n = 0
                codes: list[str] = []
                matched_models: list[str] = []
                for _sk, m, _t in group_rows:
                    mm = rx.search(m)
                    if mm:
                        match_n += 1
                        codes.append(mm.group(1))
                        if len(matched_models) < 2000:
                            matched_models.append(m)
                if match_n < int(args.min_model_support):
                    continue
                if match_n / len(group_rows) < float(args.min_model_match_rate):
                    continue

                # Prefer transform-based rule if it fits; else try mapping based on observed codes.
                train_acc = acc_for_rule(train, rx, transform, None, tol)
                hold_acc = acc_for_rule(holdout, rx, transform, None, tol)
                mapping = None

                if not (train_acc >= float(args.min_model_train_accuracy) and hold_acc >= float(args.min_model_holdout_accuracy)):
                    # Build mapping from code -> median tons (rounded to 0.5) and re-evaluate.
                    by_code: dict[str, list[float]] = defaultdict(list)
                    for m, t in train:
                        mm = rx.search(m)
                        if not mm:
                            continue
                        code = mm.group(1)
                        by_code[code].append(float(t))
                    mapping2: dict[str, float] = {}
                    for code, vals in by_code.items():
                        vals2 = sorted(vals)
                        med = vals2[len(vals2) // 2]
                        mapping2[code] = round(med * 2.0) / 2.0
                    if len(mapping2) < 3:
                        continue
                    train_acc = acc_for_rule(train, rx, None, mapping2, tol)
                    hold_acc = acc_for_rule(holdout, rx, None, mapping2, tol)
                    mapping = mapping2

                if train_acc < float(args.min_model_train_accuracy) or hold_acc < float(args.min_model_holdout_accuracy):
                    continue

                cand = CapacityCandidate(
                    brand=brand,
                    equipment_type=equipment_type,
                    model_regex=compute_model_regex_for_matches(matched_models),
                    token_index=k,
                    token_width=width,
                    pattern_regex=pat,
                    transform=(transform if mapping is None else None),
                    mapping=mapping,
                    support_n=len(group_rows),
                    match_n=match_n,
                    train_accuracy=train_acc,
                    holdout_accuracy=hold_acc,
                )

                # Choose highest holdout accuracy, then highest match coverage.
                if best is None:
                    best = cand
                else:
                    if (cand.holdout_accuracy, cand.match_n) > (best.holdout_accuracy, best.match_n):
                        best = cand

        return [best] if best else []

    capacity_groups: dict[tuple[str, str], list[tuple[str, str, float]]] = defaultdict(list)
    if col_model and col_cap_val and col_cap_unit:
        with input_path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f3:
            reader = csv.DictReader(f3)
            row_i = 0
            for row in reader:
                row_i += 1
                brand = normalize_brand((row.get(cmap.make) or "").strip(), brand_alias_map)
                if not brand or brand == "UNKNOWN":
                    continue
                model_raw = (row.get(col_model) or "").strip()
                if not model_raw:
                    continue
                tons = parse_tons(row.get(col_cap_val), row.get(col_cap_unit))
                if tons is None:
                    continue
                et = normalize_text((row.get(col_equipment) or "").strip()) if col_equipment else ""
                # Split-key should not collapse to just model (many rows share the same model).
                serial_hint = (row.get(cmap.serial) or "").strip() if cmap.serial else ""
                asset_hint = (row.get(cmap.asset_id) or "").strip() if cmap.asset_id else ""
                split_key = f"{brand}|{et}|{model_raw}|{serial_hint}|{asset_hint}|{row_i}"
                capacity_groups[(brand, et)].append((split_key, normalize_text(model_raw), float(tons)))

    cap_candidates: list[CapacityCandidate] = []
    for (brand, et), rows in capacity_groups.items():
        cap_candidates.extend(mine_capacity_candidates(rows, brand=brand, equipment_type=et))

    # -----------------------------------------
    # Generic numeric attribute mining (direct)
    # -----------------------------------------
    @dataclass(frozen=True)
    class NumericAttrCandidate:
        brand: str
        equipment_type: str
        attribute_name: str
        units: str
        model_regex: str
        token_index: int
        token_width: int
        pattern_regex: str
        support_n: int
        match_n: int
        train_accuracy: float
        holdout_accuracy: float

    def parse_float(val: str | None) -> float | None:
        if val is None:
            return None
        t = str(val).strip()
        if not t:
            return None
        try:
            return float(t)
        except Exception:
            return None

    def mine_numeric_attr_candidates(
        group_rows: list[tuple[str, str, float]],
        *,
        brand: str,
        equipment_type: str,
        attribute_name: str,
        units: str,
        tolerance: float,
    ) -> list[NumericAttrCandidate]:
        if len(group_rows) < int(args.min_model_support):
            return []
        train, holdout = split_rows(group_rows)
        if len(train) < int(args.min_model_support) * 0.6 or len(holdout) < 10:
            return []

        best: NumericAttrCandidate | None = None

        def compute_model_regex_for_matches(models: list[str]) -> str:
            # Reuse the same approach as capacity mining.
            if not models:
                return ""
            counts: Counter[str] = Counter()
            for m in models:
                compact = re.sub(r"[^A-Z0-9]", "", normalize_text(m))
                if len(compact) < 4:
                    continue
                counts[compact[:4]] += 1
            if not counts:
                return ""
            total = sum(counts.values())
            chosen: list[str] = []
            covered = 0
            for pref, n in counts.most_common(20):
                share = n / total if total else 0.0
                if share < 0.05:
                    continue
                chosen.append(pref)
                covered += n
                if covered / total >= 0.95:
                    break
            if not chosen:
                pref, n = counts.most_common(1)[0]
                if (n / total) >= 0.70:
                    chosen = [pref]
            if not chosen:
                return ""
            def sep_tolerant(prefix: str) -> str:
                parts = []
                for ch in prefix:
                    parts.append(re.escape(ch))
                return r"^" + r"[^A-Z0-9]*".join(parts)
            return r"(?:" + "|".join([sep_tolerant(p) for p in chosen]) + r")"

        def acc(rows: list[tuple[str, float]], rx: re.Pattern) -> tuple[float, int]:
            denom = 0
            ok = 0
            for model, truth in rows:
                m = rx.search(model)
                if not m:
                    continue
                code = m.group(1)
                if not code.isdigit():
                    continue
                pred = float(int(code))
                denom += 1
                if abs(pred - truth) <= tolerance:
                    ok += 1
            return ((ok / denom) if denom else 0.0), denom

        for width in range(1, 6):
            for k in range(1, 6):
                pat = build_kth_token_regex(k, width)
                try:
                    rx = re.compile(pat)
                except Exception:
                    continue
                matched_models: list[str] = []
                match_n = 0
                for _sk, m, _v in group_rows:
                    if rx.search(m):
                        match_n += 1
                        if len(matched_models) < 2000:
                            matched_models.append(m)
                if match_n < int(args.min_model_support):
                    continue
                if match_n / len(group_rows) < float(args.min_model_match_rate):
                    continue
                train_acc, train_match_n = acc(train, rx)
                hold_acc, hold_match_n = acc(holdout, rx)
                if train_match_n < 10 or hold_match_n < 5:
                    continue
                if train_acc < float(args.min_model_train_accuracy) or hold_acc < float(args.min_model_holdout_accuracy):
                    continue
                cand = NumericAttrCandidate(
                    brand=brand,
                    equipment_type=equipment_type,
                    attribute_name=attribute_name,
                    units=units,
                    model_regex=compute_model_regex_for_matches(matched_models),
                    token_index=k,
                    token_width=width,
                    pattern_regex=pat,
                    support_n=len(group_rows),
                    match_n=match_n,
                    train_accuracy=train_acc,
                    holdout_accuracy=hold_acc,
                )
                if best is None or (cand.holdout_accuracy, cand.match_n) > (best.holdout_accuracy, best.match_n):
                    best = cand

        return [best] if best else []

    # Collect numeric truth columns
    col_fan_hp = find_col(["Fan \n(HP)", "Fan (HP)", "FanHP"])
    col_fan_cfm = find_col(["Fan Flow\n(CFM)", "Fan Flow (CFM)", "FanFlow(CFM)", "Fan Flow"])
    col_pump_hp = find_col(["Pump \n(HP)", "Pump (HP)", "PumpHP"])
    col_pump_gpm = find_col(["Pump Flow\n(GPM)", "Pump Flow (GPM)", "PumpFlow(GPM)", "Pump Flow"])
    col_amp = find_col(["Amp", "Amps"])
    col_dhw_gal = find_col(["DHW Storage Capacity\n(Gallons)", "DHW Storage Capacity (Gallons)", "DHW Storage Capacity"])

    numeric_specs = []
    if col_fan_hp:
        numeric_specs.append(("FanHP", col_fan_hp, "HP", 0.5))
    if col_fan_cfm:
        numeric_specs.append(("FanFlowCFM", col_fan_cfm, "CFM", 50.0))
    if col_pump_hp:
        numeric_specs.append(("PumpHP", col_pump_hp, "HP", 0.5))
    if col_pump_gpm:
        numeric_specs.append(("PumpFlowGPM", col_pump_gpm, "GPM", 5.0))
    if col_amp:
        numeric_specs.append(("Amps", col_amp, "A", 5.0))
    if col_dhw_gal:
        numeric_specs.append(("DHWStorageGallons", col_dhw_gal, "Gallons", 5.0))

    numeric_groups: dict[tuple[str, str, str], list[tuple[str, str, float]]] = defaultdict(list)
    if col_model and numeric_specs:
        with input_path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f4:
            reader = csv.DictReader(f4)
            row_i = 0
            for row in reader:
                row_i += 1
                brand = normalize_brand((row.get(cmap.make) or "").strip(), brand_alias_map)
                if not brand or brand == "UNKNOWN":
                    continue
                model_raw = (row.get(col_model) or "").strip()
                if not model_raw:
                    continue
                et = normalize_text((row.get(col_equipment) or "").strip()) if col_equipment else ""
                serial_hint = (row.get(cmap.serial) or "").strip() if cmap.serial else ""
                asset_hint = (row.get(cmap.asset_id) or "").strip() if cmap.asset_id else ""
                for attr_name, col_val, _units, _tol in numeric_specs:
                    v = parse_float(row.get(col_val))
                    if v is None:
                        continue
                    split_key = f"{brand}|{et}|{attr_name}|{model_raw}|{serial_hint}|{asset_hint}|{row_i}"
                    numeric_groups[(brand, et, attr_name)].append((split_key, normalize_text(model_raw), float(v)))

    numeric_candidates: list[NumericAttrCandidate] = []
    for (brand, et, attr_name), rows in numeric_groups.items():
        spec = next((s for s in numeric_specs if s[0] == attr_name), None)
        if not spec:
            continue
        _attr_name, _col_val, units, tol = spec
        numeric_candidates.extend(
            mine_numeric_attr_candidates(
                rows,
                brand=brand,
                equipment_type=et,
                attribute_name=attr_name,
                units=units,
                tolerance=float(tol),
            )
        )

    # Write attribute candidates (capacity + numeric)
    attr_cand_path = out_candidates_dir / "AttributeDecodeRule.candidates.jsonl"
    with attr_cand_path.open("w", encoding="utf-8") as f_out:
        # Capacity first
        for c in sorted(cap_candidates, key=lambda x: (-x.holdout_accuracy, -x.match_n, x.brand, x.equipment_type)):
            ve = {"data_type": "Number", "pattern": {"regex": c.pattern_regex, "group": 1}}
            if c.mapping is not None:
                ve["mapping"] = c.mapping
            if c.transform is not None:
                ve["transform"] = c.transform
            obj = {
                "rule_type": "decode",
                "brand": c.brand,
                "model_regex": c.model_regex,
                "attribute_name": "NominalCapacityTons",
                "value_extraction": ve,
                "units": "Tons",
                "examples": [],
                "limitations": f"Mined from asset report cooling capacity; equipment_type={c.equipment_type!r}; match_n={c.match_n}/{c.support_n}.",
                "evidence_excerpt": f"VERIFIED: Rule matches {c.match_n} assets with {c.holdout_accuracy:.1%} accuracy via holdout validation.",
                "source_url": "internal_asset_reports",
                "retrieved_on": dt.date.today().isoformat(),
                "image_urls": [],
                "support_n": c.support_n,
                "match_n": c.match_n,
                "train_accuracy": round(c.train_accuracy, 4),
                "holdout_accuracy": round(c.holdout_accuracy, 4),
                "equipment_type": c.equipment_type,
            }
            f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")

        # Additional numeric attributes
        for c in sorted(
            numeric_candidates, key=lambda x: (-x.holdout_accuracy, -x.match_n, x.attribute_name, x.brand, x.equipment_type)
        ):
            ve = {"data_type": "Number", "pattern": {"regex": c.pattern_regex, "group": 1}}
            obj = {
                "rule_type": "decode",
                "brand": c.brand,
                "model_regex": c.model_regex,
                "attribute_name": c.attribute_name,
                "value_extraction": ve,
                "units": c.units,
                "examples": [],
                "limitations": f"Mined from asset report {c.attribute_name}; equipment_type={c.equipment_type!r}; match_n={c.match_n}/{c.support_n}.",
                "evidence_excerpt": f"VERIFIED: Rule matches {c.match_n} assets with {c.holdout_accuracy:.1%} accuracy via holdout validation.",
                "source_url": "internal_asset_reports",
                "retrieved_on": dt.date.today().isoformat(),
                "image_urls": [],
                "support_n": c.support_n,
                "match_n": c.match_n,
                "train_accuracy": round(c.train_accuracy, 4),
                "holdout_accuracy": round(c.holdout_accuracy, 4),
                "equipment_type": c.equipment_type,
            }
            f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")

    # Append attribute candidates to scorecard
    with score_path.open("a", newline="", encoding="utf-8") as f_score:
        w = csv.DictWriter(
            f_score,
            fieldnames=[
                "candidate_type",
                "brand",
                "length",
                "signature",
                "year_pos_start",
                "year_pos_end",
                "support_n",
                "train_accuracy",
                "holdout_accuracy",
                "collisions_other_brands",
            ],
        )
        # Only append if we wrote any candidates.
        for c in cap_candidates:
            w.writerow(
                {
                    "candidate_type": f"AttributeDecodeRule.NominalCapacityTons ({c.equipment_type or 'ANY'})",
                    "brand": c.brand,
                    "length": "",
                    "signature": "",
                    "year_pos_start": "",
                    "year_pos_end": "",
                    "support_n": c.support_n,
                    "train_accuracy": f"{c.train_accuracy:.4f}",
                    "holdout_accuracy": f"{c.holdout_accuracy:.4f}",
                    "collisions_other_brands": "",
                }
            )
        for c in numeric_candidates:
            w.writerow(
                {
                    "candidate_type": f"AttributeDecodeRule.{c.attribute_name} ({c.equipment_type or 'ANY'})",
                    "brand": c.brand,
                    "length": "",
                    "signature": "",
                    "year_pos_start": "",
                    "year_pos_end": "",
                    "support_n": c.support_n,
                    "train_accuracy": f"{c.train_accuracy:.4f}",
                    "holdout_accuracy": f"{c.holdout_accuracy:.4f}",
                    "collisions_other_brands": "",
                }
            )

    # Extend summary doc with attribute candidates.
    if cap_candidates or numeric_candidates:
        summary_path.write_text(
            summary_path.read_text(encoding="utf-8")
            + f"- Attribute candidates (capacity): `{attr_cand_path}`\n",
            encoding="utf-8",
        )

    print(str(out_reports_dir.parent))
    return 0
