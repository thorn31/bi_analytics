from __future__ import annotations

import csv
import json
import os
from pathlib import Path

from msl.decoder.attributes import decode_attributes
from msl.decoder.decode import decode_serial
from msl.decoder.io import load_attribute_rules_csv, load_brand_normalize_rules_csv, load_serial_rules_csv
from msl.decoder.normalize import normalize_brand
from msl.decoder.validate import validate_attribute_rules, validate_serial_rules


def cmd_decode(args) -> int:
    serial_rules_csv = args.serial_rules_csv
    if args.ruleset_dir:
        serial_rules_csv = str(Path(args.ruleset_dir) / "SerialDecodeRule.csv")

    attribute_rules_csv = ""
    if args.ruleset_dir:
        attribute_rules_csv = str(Path(args.ruleset_dir) / "AttributeDecodeRule.csv")
    if getattr(args, "attribute_rules_csv", ""):
        attribute_rules_csv = args.attribute_rules_csv

    brand_alias_map: dict[str, str] = {}
    if args.ruleset_dir:
        brand_rules_csv = Path(args.ruleset_dir) / "BrandNormalizeRule.csv"
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

    in_path = Path(args.input)
    with (
        in_path.open("r", newline="", encoding="utf-8") as f_in,
        out_path.open("w", newline="", encoding="utf-8") as f_out,
        (attr_out_path.open("w", newline="", encoding="utf-8") if attr_out_path else open(os.devnull, "w")) as f_attr,
    ):
        reader = csv.DictReader(f_in)
        fieldnames = [
            "AssetID",
            "DetectedBrand",
            "MatchedSerialStyle",
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
            "AttributesJSON",
            "DecodeStatus",
            "DecodeNotes",
        ]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        attr_fieldnames = [
            "AssetID",
            "DetectedBrand",
            "ModelNumber",
            "AttributeName",
            "Value",
            "Units",
            "Confidence",
            "Evidence",
            "SourceURL",
        ]
        attr_writer = None
        if attr_out_path:
            attr_writer = csv.DictWriter(f_attr, fieldnames=attr_fieldnames)
            attr_writer.writeheader()

        for row in reader:
            asset_id = row.get("AssetID") or row.get("asset_id") or ""
            brand = normalize_brand(row.get("Make") or row.get("Brand") or row.get("DetectedBrand"), brand_alias_map)
            model = row.get("ModelNumber") or row.get("Model") or ""
            res = decode_serial(
                brand,
                row.get("SerialNumber") or row.get("Serial") or "",
                accepted,
                min_plausible_year=(int(args.min_manufacture_year) if getattr(args, "min_manufacture_year", 0) > 0 else None),
            )
            attrs = decode_attributes(brand, model, attr_accepted) if attr_accepted else []

            if attr_writer and attrs:
                for a in attrs:
                    attr_writer.writerow(
                        {
                            "AssetID": asset_id,
                            "DetectedBrand": brand,
                            "ModelNumber": model,
                            "AttributeName": a.attribute_name,
                            "Value": a.value,
                            "Units": a.units,
                            "Confidence": a.confidence,
                            "Evidence": a.evidence,
                            "SourceURL": a.source_url,
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
                    "MatchedSerialStyle": res.matched_style_name or "",
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
                    "AttributesJSON": json.dumps(
                        [
                            {
                                "AttributeName": a.attribute_name,
                                "Value": a.value,
                                "Units": a.units,
                                "Confidence": a.confidence,
                                "Evidence": a.evidence,
                                "SourceURL": a.source_url,
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
