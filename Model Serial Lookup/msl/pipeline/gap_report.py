from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from msl.decoder.io import load_attribute_rules_csv, load_brand_normalize_rules_csv, load_serial_rules_csv, sort_rules_by_priority
from msl.decoder.normalize import normalize_brand
from msl.decoder.validate import validate_attribute_rules, validate_serial_rules
from msl.pipeline.ruleset_manager import resolve_ruleset_dir


def _load_csv(path: Path) -> list[dict]:
    # Be permissive: SDI exports may contain non-UTF8 bytes (e.g., latin-1). We prefer producing
    # a usable gap report over hard-failing on decode errors.
    with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))


def cmd_gap_report(args) -> int:
    ruleset_dir = resolve_ruleset_dir(getattr(args, "ruleset_dir", None) or None)
    if not ruleset_dir:
        raise SystemExit("--ruleset-dir is required and must exist, or CURRENT.txt must point to a valid ruleset")
    serial_csv = Path(args.serial_rules_csv) if args.serial_rules_csv else (ruleset_dir / "SerialDecodeRule.csv")
    attr_csv = Path(args.attribute_rules_csv) if args.attribute_rules_csv else (ruleset_dir / "AttributeDecodeRule.csv")

    brand_alias_map: dict[str, str] = {}
    brand_rules_csv = ruleset_dir / "BrandNormalizeRule.csv"
    if brand_rules_csv.exists():
        brand_alias_map = load_brand_normalize_rules_csv(brand_rules_csv)

    assets = _load_csv(Path(args.input))

    serial_rules = load_serial_rules_csv(serial_csv)
    serial_rules = sort_rules_by_priority(serial_rules)  # Sort by priority
    serial_accepted, serial_issues = validate_serial_rules(serial_rules)

    attr_accepted = []
    if attr_csv.exists():
        attr_rules = load_attribute_rules_csv(attr_csv)
        attr_accepted, _attr_issues = validate_attribute_rules(attr_rules)

    # Pre-index rules per brand for fast checks.
    by_brand_serial = defaultdict(list)
    for r in serial_accepted:
        by_brand_serial[r.brand].append(r)
    by_brand_attr = defaultdict(list)
    for r in attr_accepted:
        by_brand_attr[r.brand].append(r)

    # Gap reasons:
    # - missing_brand_rules: no rules for brand at all
    # - no_serial_decode_rules: only guidance rules exist
    # - serial_chart_required_only: decode rules exist but only chart-required fields (not deterministically usable)
    # - no_attribute_rules: no attribute rules for brand
    # - attribute_guidance_only: only guidance attribute rules exist
    # - other: fallback

    rows_out: list[dict] = []
    counters = Counter()
    by_make = defaultdict(Counter)

    for a in assets:
        make_raw = a.get("Make") or a.get("manufacturerId") or a.get("Manufacturer") or ""
        brand = normalize_brand(make_raw, brand_alias_map)
        serial = (a.get("SerialNumber") or a.get("serialNumber") or a.get("Serial") or "").strip()
        model = (a.get("ModelNumber") or a.get("modelNumber") or a.get("Model") or "").strip()

        s_rules = by_brand_serial.get(brand, [])
        a_rules = by_brand_attr.get(brand, [])

        has_any_serial = bool(s_rules)
        has_serial_decode = any(r.rule_type == "decode" and r.serial_regex for r in s_rules)
        has_serial_guidance = any(r.rule_type == "guidance" for r in s_rules)

        # If the brand has decode rules, see if they include any usable year extraction (positions/pattern/mapping).
        usable_year_rule = False
        for r in s_rules:
            if r.rule_type != "decode":
                continue
            year_spec = (r.date_fields or {}).get("year") or {}
            if isinstance(year_spec, dict) and year_spec.get("requires_chart") is True:
                continue
            if any(k in year_spec for k in ["positions", "positions_list", "pattern"]) or year_spec.get("mapping"):
                usable_year_rule = True
                break

        has_any_attr = bool(a_rules)
        has_attr_decode = any(r.rule_type == "decode" for r in a_rules)
        has_attr_guidance = any(r.rule_type == "guidance" for r in a_rules)

        reason = "other"
        if not has_any_serial and not has_any_attr:
            reason = "missing_brand_rules"
        elif not has_serial_decode and has_serial_guidance:
            reason = "no_serial_decode_rules"
        elif has_serial_decode and not usable_year_rule:
            reason = "serial_chart_required_only"
        elif not has_any_attr:
            reason = "no_attribute_rules"
        elif not has_attr_decode and has_attr_guidance:
            reason = "attribute_guidance_only"

        counters[reason] += 1
        by_make[brand][reason] += 1

        rows_out.append(
            {
                "AssetID": a.get("AssetID") or a.get("equipmentId") or "",
                "MakeRaw": make_raw,
                "DetectedBrand": brand,
                "SerialNumber": serial,
                "ModelNumber": model,
                "Reason": reason,
                "HasSerialRules": "true" if has_any_serial else "false",
                "HasSerialDecodeRules": "true" if has_serial_decode else "false",
                "HasAttributeRules": "true" if has_any_attr else "false",
                "HasAttributeDecodeRules": "true" if has_attr_decode else "false",
            }
        )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "AssetID",
                "MakeRaw",
                "DetectedBrand",
                "SerialNumber",
                "ModelNumber",
                "Reason",
                "HasSerialRules",
                "HasSerialDecodeRules",
                "HasAttributeRules",
                "HasAttributeDecodeRules",
            ],
        )
        w.writeheader()
        w.writerows(rows_out)

    summary_path = out_path.with_suffix(".summary.json")
    summary_path.write_text(
        json.dumps(
            {
                "ruleset_dir": str(ruleset_dir),
                "totals_by_reason": dict(counters),
                "by_brand": {b: dict(c) for b, c in sorted(by_make.items())},
                "serial_rule_issues": [i.__dict__ for i in serial_issues],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(str(out_path))
    print(str(summary_path))
    return 0
