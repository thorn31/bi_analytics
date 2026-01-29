from __future__ import annotations

import csv
import json
import os
from pathlib import Path

from msl.decoder.attributes import decode_attributes_with_audit
from msl.decoder.decode import decode_serial
from msl.decoder.io import load_attribute_rules_csv, load_brand_normalize_rules_csv, load_serial_rules_csv
from msl.decoder.equipment_type import canonicalize_equipment_type, load_equipment_type_vocab
from msl.decoder.normalize import normalize_brand
from msl.decoder.validate import validate_attribute_rules, validate_serial_rules
from msl.pipeline.ruleset_manager import resolve_ruleset_dir


def cmd_decode(args) -> int:
    # Resolve ruleset_dir: explicit arg > CURRENT.txt > None
    ruleset_dir = resolve_ruleset_dir(getattr(args, "ruleset_dir", "") or None)

    serial_rules_csv = args.serial_rules_csv
    if ruleset_dir:
        serial_rules_csv = str(ruleset_dir / "SerialDecodeRule.csv")

    attribute_rules_csv = ""
    if ruleset_dir:
        attribute_rules_csv = str(ruleset_dir / "AttributeDecodeRule.csv")
    if getattr(args, "attribute_rules_csv", ""):
        attribute_rules_csv = args.attribute_rules_csv

    brand_alias_map: dict[str, str] = {}
    if ruleset_dir:
        brand_rules_csv = ruleset_dir / "BrandNormalizeRule.csv"
        if brand_rules_csv.exists():
            brand_alias_map = load_brand_normalize_rules_csv(brand_rules_csv)

    rules = load_serial_rules_csv(serial_rules_csv)
    accepted, issues = validate_serial_rules(rules)

    attr_rules = []
    attr_accepted = []
    attr_issues = []
    if attribute_rules_csv and Path(attribute_rules_csv).exists():
        attr_rules = load_attribute_rules_csv(attribute_rules_csv)
        attr_accepted, attr_issues = validate_attribute_rules(attr_rules)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    attr_out_path: Path | None = None
    if getattr(args, "attributes_output", ""):
        attr_out_path = Path(args.attributes_output)
        attr_out_path.parent.mkdir(parents=True, exist_ok=True)

    conflict_out_path: Path | None = None
    if attr_out_path:
        conflict_out_path = attr_out_path.parent / "attribute_conflicts_long.csv"

    in_path = Path(args.input)
    vocab = load_equipment_type_vocab("data/static/equipment_types.csv")
    with (
        in_path.open("r", newline="", encoding="utf-8") as f_in,
        out_path.open("w", newline="", encoding="utf-8") as f_out,
        (attr_out_path.open("w", newline="", encoding="utf-8") if attr_out_path else open(os.devnull, "w")) as f_attr,
        (conflict_out_path.open("w", newline="", encoding="utf-8") if conflict_out_path else open(os.devnull, "w")) as f_conf,
    ):
        reader = csv.DictReader(f_in)
        fieldnames = [
            "AssetID",
            "DetectedBrand",
            "EquipmentTypeRaw",
            "EquipmentType",
            "MatchedSerialStyle",
            "MatchedSerialRuleEquipmentTypes",
            "ManufactureYearRaw",
            "ManufactureYear",
            "ManufactureMonthRaw",
            "ManufactureMonth",
            "ManufactureWeekRaw",
            "ManufactureWeek",
            "ManufactureDateAmbiguousDecade",
            "ManufactureDateConfidence",
            "ManufactureDateEvidence",
            "ManufactureDateSourceURL",
            "AttributesCount",
            "AttributeConflictCount",
            "TypedRuleAppliedWithoutTypeContext",
            "AttributesJSON",
            "DecodeStatus",
            "DecodeNotes",
        ]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        attr_fieldnames = [
            "AssetID",
            "DetectedBrand",
            "EquipmentType",
            "ModelNumber",
            "AttributeName",
            "Value",
            "Units",
            "Confidence",
            "Evidence",
            "SourceURL",
            "RuleEquipmentTypes",
            "TypedRuleAppliedWithoutTypeContext",
        ]
        attr_writer = None
        if attr_out_path:
            attr_writer = csv.DictWriter(f_attr, fieldnames=attr_fieldnames)
            attr_writer.writeheader()

        conflict_fieldnames = [
            "AssetID",
            "DetectedBrand",
            "EquipmentType",
            "ModelNumber",
            "AttributeName",
            "CandidateValue",
            "CandidateValueRaw",
            "CandidateConfidence",
            "CandidateScore",
            "CandidateRank",
            "IsSelected",
            "SourceURL",
            "RuleEquipmentTypes",
            "TypedRuleAppliedWithoutTypeContext",
        ]
        conflict_writer = None
        if conflict_out_path:
            conflict_writer = csv.DictWriter(f_conf, fieldnames=conflict_fieldnames)
            conflict_writer.writeheader()

        for row in reader:
            asset_id = row.get("AssetID") or row.get("asset_id") or ""
            brand = normalize_brand(row.get("Make") or row.get("Brand") or row.get("DetectedBrand"), brand_alias_map)
            model = row.get("ModelNumber") or row.get("Model") or ""
            equipment_type_raw = row.get("Equipment") or row.get("EquipmentType") or row.get("Type") or ""
            _et_raw_norm, equipment_type = canonicalize_equipment_type(equipment_type_raw, vocab)
            res = decode_serial(
                brand,
                row.get("SerialNumber") or row.get("Serial") or "",
                accepted,
                equipment_type=equipment_type or None,
                min_plausible_year=(int(args.min_manufacture_year) if getattr(args, "min_manufacture_year", 0) > 0 else None),
            )
            attrs, candidates, conflicts_n = decode_attributes_with_audit(brand, model, attr_accepted, equipment_type=equipment_type or None) if attr_accepted else ([], [], 0)

            typed_wo_context = bool(res.typed_rule_applied_without_type_context) or any(
                a.typed_rule_applied_without_type_context for a in attrs
            )

            selected_by_attr: dict[str, str] = {a.attribute_name: str(a.value) for a in attrs}
            if conflict_writer and conflicts_n > 0:
                by_attr_vals: dict[str, set[str]] = {}
                for c in candidates:
                    by_attr_vals.setdefault(c.attribute_name, set()).add(str(c.value))
                for c in sorted(candidates, key=lambda x: (-float(x.score), x.attribute_name, str(x.value))):
                    vals = by_attr_vals.get(c.attribute_name) or set()
                    if len(vals) < 2:
                        continue
                    is_selected = selected_by_attr.get(c.attribute_name) == str(c.value)
                    conflict_writer.writerow(
                        {
                            "AssetID": asset_id,
                            "DetectedBrand": brand,
                            "EquipmentType": equipment_type,
                            "ModelNumber": model,
                            "AttributeName": c.attribute_name,
                            "CandidateValue": c.value,
                            "CandidateValueRaw": c.value_raw,
                            "CandidateConfidence": c.confidence,
                            "CandidateScore": f"{float(c.score):.3f}",
                            "CandidateRank": "",
                            "IsSelected": "true" if is_selected else "false",
                            "SourceURL": c.source_url,
                            "RuleEquipmentTypes": json.dumps(c.rule_equipment_types, ensure_ascii=False),
                            "TypedRuleAppliedWithoutTypeContext": "true" if c.typed_rule_applied_without_type_context else "false",
                        }
                    )

            if attr_writer and attrs:
                for a in attrs:
                    attr_writer.writerow(
                        {
                            "AssetID": asset_id,
                            "DetectedBrand": brand,
                            "EquipmentType": equipment_type,
                            "ModelNumber": model,
                            "AttributeName": a.attribute_name,
                            "Value": a.value,
                            "Units": a.units,
                            "Confidence": a.confidence,
                            "Evidence": a.evidence,
                            "SourceURL": a.source_url,
                            "RuleEquipmentTypes": json.dumps(a.rule_equipment_types, ensure_ascii=False),
                            "TypedRuleAppliedWithoutTypeContext": "true" if a.typed_rule_applied_without_type_context else "false",
                        }
                    )

            decoded_any = (res.confidence != "None") or bool(attrs)
            decode_status = "NotDecoded"
            if decoded_any:
                decode_status = "Decoded" if (res.confidence != "None" and attrs) else "Partial"

            writer.writerow(
                {
                    "AssetID": asset_id,
                    "DetectedBrand": brand,
                    "EquipmentTypeRaw": equipment_type_raw,
                    "EquipmentType": equipment_type,
                    "MatchedSerialStyle": res.matched_style_name or "",
                    "MatchedSerialRuleEquipmentTypes": json.dumps(res.rule_equipment_types, ensure_ascii=False),
                    "ManufactureYearRaw": res.manufacture_year_raw or "",
                    "ManufactureYear": res.manufacture_year or "",
                    "ManufactureMonthRaw": res.manufacture_month_raw or "",
                    "ManufactureMonth": res.manufacture_month or "",
                    "ManufactureWeekRaw": res.manufacture_week_raw or "",
                    "ManufactureWeek": res.manufacture_week or "",
                    "ManufactureDateAmbiguousDecade": "true" if res.ambiguous_decade else "false",
                    "ManufactureDateConfidence": res.confidence,
                    "ManufactureDateEvidence": res.evidence,
                    "ManufactureDateSourceURL": res.source_url,
                    "AttributesCount": str(len(attrs)),
                    "AttributeConflictCount": str(int(conflicts_n)),
                    "TypedRuleAppliedWithoutTypeContext": "true" if typed_wo_context else "false",
                    "AttributesJSON": json.dumps(
                        [
                            {
                                "AttributeName": a.attribute_name,
                                "Value": a.value,
                                "Units": a.units,
                                "Confidence": a.confidence,
                                "Evidence": a.evidence,
                                "SourceURL": a.source_url,
                                "RuleEquipmentTypes": a.rule_equipment_types,
                                "TypedRuleAppliedWithoutTypeContext": a.typed_rule_applied_without_type_context,
                            }
                            for a in attrs
                        ],
                        ensure_ascii=False,
                    ),
                    "DecodeStatus": decode_status,
                    "DecodeNotes": res.notes,
                }
            )

    if issues and args.write_rejected:
        rej_path = Path(args.write_rejected)
        rej_path.parent.mkdir(parents=True, exist_ok=True)
        rej_path.write_text(
            "\n".join([json.dumps({"brand": i.brand, "style_name": i.style_name, "issue": i.issue}) for i in issues]) + "\n",
            encoding="utf-8",
        )

    if attr_issues and args.write_rejected:
        rej_path = Path(args.write_rejected)
        rej_path.parent.mkdir(parents=True, exist_ok=True)
        with rej_path.open("a", encoding="utf-8") as f:
            for i in attr_issues:
                f.write(json.dumps({"brand": i.brand, "style_name": i.style_name, "issue": i.issue}) + "\n")

    print(str(out_path))
    return 0
