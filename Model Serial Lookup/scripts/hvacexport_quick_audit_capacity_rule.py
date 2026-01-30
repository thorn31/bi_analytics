#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


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


def _normalize_model_for_regex(model: str) -> str:
    return re.sub(r"[^A-Z0-9-]+", "", (model or "").strip().upper())


@dataclass(frozen=True)
class CapRule:
    brand: str
    equipment_types: list[str]
    model_regex: str
    start: int
    end: int
    mapping: dict[str, float]
    source_url: str
    evidence: str


def _choose_best_rule(rules: list[CapRule]) -> CapRule:
    rules.sort(key=lambda r: (not bool(r.equipment_types), -len(r.model_regex or ""), r.start, r.end))
    return rules[0]


def _load_rules(candidates_jsonl: Path, *, brand: str, equipment_type: str) -> list[tuple[CapRule, re.Pattern[str] | None]]:
    from msl.decoder.normalize import normalize_brand

    out: list[tuple[CapRule, re.Pattern[str] | None]] = []
    want_brand = normalize_brand(brand)
    for obj in _jsonl_read(candidates_jsonl):
        if (obj.get("rule_type") or "").strip() != "decode":
            continue
        if (obj.get("attribute_name") or "").strip() != "NominalCapacityTons":
            continue
        b = normalize_brand(obj.get("brand") or "")
        if b != want_brand:
            continue
        ets = obj.get("equipment_types") or []
        if not isinstance(ets, list):
            ets = []
        ets = [str(x).strip() for x in ets if str(x).strip()]
        if equipment_type and ets and equipment_type not in ets:
            continue

        ve = obj.get("value_extraction") or {}
        if not isinstance(ve, dict):
            continue
        pos = ve.get("positions") or {}
        if not isinstance(pos, dict):
            continue
        try:
            start = int(pos.get("start"))
            end = int(pos.get("end"))
        except Exception:
            continue
        mapping = ve.get("mapping") or {}
        if not isinstance(mapping, dict) or not mapping:
            continue
        mapping_f: dict[str, float] = {}
        ok = True
        for k, v in mapping.items():
            try:
                mapping_f[str(k)] = float(v)
            except Exception:
                ok = False
                break
        if not ok:
            continue
        rx_s = (obj.get("model_regex") or "").strip()
        try:
            rx = re.compile(rx_s) if rx_s else None
        except Exception:
            rx = None
        out.append(
            (
                CapRule(
                    brand=b,
                    equipment_types=ets,
                    model_regex=rx_s,
                    start=start,
                    end=end,
                    mapping=mapping_f,
                    source_url=(obj.get("source_url") or "").strip(),
                    evidence=(obj.get("evidence_excerpt") or "").strip(),
                ),
                rx,
            )
        )
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hvacexport_quick_audit_capacity_rule", description="Quick audit for a capacity mapping rule set on an SDI CSV.")
    ap.add_argument("--input-sdi", required=True)
    ap.add_argument("--candidates-jsonl", required=True)
    ap.add_argument("--brand", required=True)
    ap.add_argument("--equipment-type", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tolerance-tons", type=float, default=0.25)
    args = ap.parse_args(argv)

    from msl.decoder.normalize import normalize_brand, normalize_model

    rules = _load_rules(Path(args.candidates_jsonl), brand=str(args.brand), equipment_type=str(args.equipment_type))
    if not rules:
        raise SystemExit("No rules found for the requested brand/type in candidates file")

    rows = _read_csv_rows(Path(args.input_sdi))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_rows = out_dir / "audit_rows.csv"
    out_summary = out_dir / "audit_summary.json"

    fields = [
        "Building",
        "Unit ID",
        "Make",
        "EquipmentType",
        "ModelNumber",
        "ModelForRegex",
        "TruthTons",
        "DecodedTons",
        "Code",
        "Result",
        "RuleModelRegex",
        "RuleStartPos",
        "RuleEndPos",
        "RuleSource",
    ]

    matched_n = 0
    match_n = 0
    mismatch_n = 0
    truth_n = 0

    with out_rows.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            if normalize_brand(row.get("Make") or "") != normalize_brand(args.brand):
                continue
            if (row.get("EquipmentType") or "").strip() != str(args.equipment_type):
                continue
            truth_s = (row.get("KnownCapacityTons") or "").strip()
            if not truth_s:
                continue
            truth_n += 1
            try:
                truth = float(truth_s)
            except Exception:
                continue
            model_raw = normalize_model(row.get("ModelNumber") or "")
            model_for_regex = _normalize_model_for_regex(model_raw)

            candidates_for_row: list[CapRule] = []
            for r, rx in rules:
                if rx and not rx.search(model_for_regex):
                    continue
                if r.end > len(model_for_regex) or r.start < 1 or r.end < r.start:
                    continue
                candidates_for_row.append(r)
            if not candidates_for_row:
                continue

            best = _choose_best_rule(candidates_for_row)
            code = model_for_regex[best.start - 1 : best.end]
            if code not in best.mapping:
                continue
            decoded = best.mapping[code]
            matched_n += 1
            ok = abs(decoded - truth) <= float(args.tolerance_tons)
            if ok:
                match_n += 1
            else:
                mismatch_n += 1
            w.writerow(
                {
                    "Building": (row.get("Building") or "").strip(),
                    "Unit ID": (row.get("Unit ID") or "").strip(),
                    "Make": (row.get("Make") or "").strip(),
                    "EquipmentType": (row.get("EquipmentType") or "").strip(),
                    "ModelNumber": (row.get("ModelNumber") or "").strip(),
                    "ModelForRegex": model_for_regex,
                    "TruthTons": truth_s,
                    "DecodedTons": f"{decoded:.3f}".rstrip("0").rstrip("."),
                    "Code": code,
                    "Result": "match" if ok else "mismatch",
                    "RuleModelRegex": best.model_regex,
                    "RuleStartPos": str(best.start),
                    "RuleEndPos": str(best.end),
                    "RuleSource": best.source_url,
                }
            )

    summary = {
        "brand": str(args.brand),
        "equipment_type": str(args.equipment_type),
        "input_rows_n": len(rows),
        "truth_rows_n": truth_n,
        "matched_rows_n": matched_n,
        "match_n": match_n,
        "mismatch_n": mismatch_n,
        "accuracy_on_matches": (match_n / matched_n if matched_n else None),
        "coverage_on_truth": (matched_n / truth_n if truth_n else None),
        "candidates_rules_n": len(rules),
        "tolerance_tons": float(args.tolerance_tons),
        "out_rows": str(out_rows),
    }
    out_summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

