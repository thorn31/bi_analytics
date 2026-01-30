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


def _load_capacity_rules(candidates_jsonl: Path) -> list[tuple[CapRule, re.Pattern[str] | None]]:
    from msl.decoder.normalize import normalize_brand

    out: list[tuple[CapRule, re.Pattern[str] | None]] = []
    for obj in _jsonl_read(candidates_jsonl):
        if (obj.get("rule_type") or "").strip() != "decode":
            continue
        if (obj.get("attribute_name") or "").strip() != "NominalCapacityTons":
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
        ets = obj.get("equipment_types") or []
        if not isinstance(ets, list):
            ets = []
        ets = [str(x).strip() for x in ets if str(x).strip()]
        rx_s = (obj.get("model_regex") or "").strip()
        try:
            rx = re.compile(rx_s) if rx_s else None
        except Exception:
            rx = None
        out.append(
            (
                CapRule(
                    brand=normalize_brand(obj.get("brand") or ""),
                    equipment_types=ets,
                    model_regex=rx_s,
                    start=start,
                    end=end,
                    mapping=mapping_f,
                ),
                rx,
            )
        )
    return out


def _choose_best_rule(rules: list[CapRule]) -> CapRule:
    # typed over untyped, then longer regex.
    rules.sort(key=lambda r: (not bool(r.equipment_types), -len(r.model_regex or ""), r.start, r.end))
    return rules[0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="hvacexport_capacity_mapping_eval",
        description="Evaluate NominalCapacityTons mapping candidates on an SDI dataset and produce per-code accuracy stats (holdout-friendly).",
    )
    ap.add_argument("--input-sdi", required=True)
    ap.add_argument("--candidates-jsonl", required=True, help="NominalCapacityTons candidates JSONL (typically capacity_from_codes output)")
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--min-support", type=int, default=5)
    args = ap.parse_args(argv)

    from msl.decoder.normalize import normalize_brand, normalize_model

    rows = _read_csv_rows(Path(args.input_sdi))
    rules = _load_capacity_rules(Path(args.candidates_jsonl))

    # Index by brand for speed
    by_brand: dict[str, list[tuple[CapRule, re.Pattern[str] | None]]] = defaultdict(list)
    for r, rx in rules:
        by_brand[r.brand].append((r, rx))

    # Stats keyed by (brand, equipment_type, model_regex, start, end, code, mapped_tons)
    stats: dict[tuple[str, str, str, int, int, str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for row in rows:
        brand = normalize_brand((row.get("Make") or "").strip())
        equip_type = (row.get("EquipmentType") or "").strip()
        model_raw = normalize_model(row.get("ModelNumber") or "")
        model = _normalize_model_for_regex(model_raw)
        if not model:
            continue
        truth_raw = (row.get("KnownCapacityTons") or "").strip()
        if not truth_raw:
            continue
        try:
            truth = float(truth_raw)
        except Exception:
            continue

        candidates_for_row: list[CapRule] = []
        for r, rx in by_brand.get(brand, []):
            if r.equipment_types and equip_type and equip_type not in r.equipment_types:
                continue
            if rx and not rx.search(model):
                continue
            # ensure positions valid
            if r.end > len(model) or r.start < 1 or r.end < r.start:
                continue
            candidates_for_row.append(r)
        if not candidates_for_row:
            continue

        best = _choose_best_rule(candidates_for_row)
        code = model[best.start - 1 : best.end]
        if code not in best.mapping:
            continue
        mapped = best.mapping[code]
        key = (
            brand,
            equip_type,
            best.model_regex,
            best.start,
            best.end,
            code,
            f"{mapped:.3f}".rstrip("0").rstrip("."),
        )
        stats[key]["SupportN"] += 1
        if abs(mapped - truth) <= 0.25:
            stats[key]["MatchN"] += 1
        else:
            stats[key]["MismatchN"] += 1

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "BrandNormalized",
        "EquipmentType",
        "RuleModelRegex",
        "RuleStartPos",
        "RuleEndPos",
        "Code",
        "MappedTons",
        "SupportN",
        "MatchN",
        "MismatchN",
        "AccuracyPct",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for (b, et, rx, start, end, code, tons), m in sorted(stats.items()):
            support = int(m.get("SupportN", 0))
            if support < int(args.min_support):
                continue
            match = int(m.get("MatchN", 0))
            mismatch = int(m.get("MismatchN", 0))
            acc = (match / support * 100.0) if support else 0.0
            w.writerow(
                {
                    "BrandNormalized": b,
                    "EquipmentType": et,
                    "RuleModelRegex": rx,
                    "RuleStartPos": str(start),
                    "RuleEndPos": str(end),
                    "Code": code,
                    "MappedTons": tons,
                    "SupportN": str(support),
                    "MatchN": str(match),
                    "MismatchN": str(mismatch),
                    "AccuracyPct": f"{acc:.1f}",
                }
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

