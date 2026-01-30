from __future__ import annotations

import csv
import datetime as dt
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from msl.decoder.attributes import decode_attributes_with_audit
from msl.decoder.decode import decode_serial
from msl.decoder.io import load_attribute_rules_csv, load_brand_normalize_rules_csv, load_serial_rules_csv, sort_rules_by_priority
from msl.decoder.equipment_type import canonicalize_equipment_type, load_equipment_type_vocab
from msl.decoder.normalize import normalize_brand, normalize_model, normalize_serial, normalize_text
from msl.decoder.validate import validate_attribute_rules, validate_serial_rules
from msl.pipeline.common import ensure_dir
from msl.pipeline.ruleset_manager import resolve_ruleset_dir


def _utc_run_id(prefix: str) -> str:
    ts = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace(":", "").replace("+00:00", "Z")
    return f"{prefix}-{ts}"


def _find_column(fieldnames: list[str], candidates: list[str]) -> str | None:
    if not fieldnames:
        return None
    norm = {normalize_text(c): c for c in fieldnames}
    for cand in candidates:
        key = normalize_text(cand)
        if key in norm:
            return norm[key]
    return None


@dataclass(frozen=True)
class ColumnMap:
    asset_id: str | None
    make: str | None
    model: str | None
    serial: str | None
    equipment_type: str | None
    known_year: str | None


def infer_column_map(fieldnames: list[str]) -> ColumnMap:
    return ColumnMap(
        asset_id=_find_column(fieldnames, ["AssetID", "Unit ID", "EquipmentId", "equipmentId", "ID", "Tag"]),
        make=_find_column(fieldnames, ["Make", "Manufacturer", "Brand", "manufacturerId"]),
        model=_find_column(fieldnames, ["ModelNumber", "Model #", "Model", "modelNumber"]),
        serial=_find_column(fieldnames, ["SerialNumber", "Serial #", "Serial", "serialNumber"]),
        equipment_type=_find_column(fieldnames, ["EquipmentType", "Equipment", "Type", "equipmentType", "description"]),
        known_year=_find_column(fieldnames, ["KnownManufactureYear", "Manuf. Year", "Manuf.\nYear", "InstallYear"]),
    )


def _as_int(value: str | None) -> int | None:
    if value is None:
        return None
    t = str(value).strip()
    if not t or not t.isdigit():
        return None
    try:
        return int(t)
    except Exception:
        return None


def cmd_phase3_baseline(args) -> int:
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    ruleset_dir = resolve_ruleset_dir(getattr(args, "ruleset_dir", None))
    if not ruleset_dir or not ruleset_dir.exists():
        raise SystemExit("--ruleset-dir is required and must exist, or CURRENT.txt must point to a valid ruleset")

    serial_rules_csv = ruleset_dir / "SerialDecodeRule.csv"
    attr_rules_csv = ruleset_dir / "AttributeDecodeRule.csv"
    if not serial_rules_csv.exists():
        raise SystemExit(f"Missing SerialDecodeRule.csv in {ruleset_dir}")

    run_id = args.run_id or _utc_run_id("phase3-baseline")
    out_dir = ensure_dir(Path(args.out_dir) / run_id)

    # Load rules once (validated).
    serial_rules = load_serial_rules_csv(serial_rules_csv)
    serial_rules = sort_rules_by_priority(serial_rules)  # Sort by priority
    serial_accepted, _serial_issues = validate_serial_rules(serial_rules)

    attr_accepted = []
    if attr_rules_csv.exists():
        attr_rules = load_attribute_rules_csv(attr_rules_csv)
        attr_accepted, _attr_issues = validate_attribute_rules(attr_rules)

    brand_alias_map: dict[str, str] = {}
    brand_rules_csv = ruleset_dir / "BrandNormalizeRule.csv"
    if brand_rules_csv.exists():
        brand_alias_map = load_brand_normalize_rules_csv(brand_rules_csv)

    equipment_vocab = load_equipment_type_vocab("data/static/equipment_types.csv")

    # Read input + infer mapping.
    with input_path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("Input CSV missing header row")
        cmap = infer_column_map(reader.fieldnames)

        # Persist mapping.
        with (out_dir / "source_column_map.csv").open("w", newline="", encoding="utf-8") as f_map:
            w = csv.DictWriter(f_map, fieldnames=["canonical_field", "source_column"])
            w.writeheader()
            for canonical, src in [
                ("AssetID", cmap.asset_id),
                ("Make", cmap.make),
                ("ModelNumber", cmap.model),
                ("SerialNumber", cmap.serial),
                ("EquipmentType", cmap.equipment_type),
                ("KnownManufactureYear", cmap.known_year),
            ]:
                w.writerow({"canonical_field": canonical, "source_column": src or ""})

        canonical_path = out_dir / "canonical_assets.csv"
        baseline_out_path = out_dir / "baseline_decoder_output.csv"
        attrs_long_path = out_dir / "baseline_attributes_long.csv"

        fieldnames_canonical = [
            "AssetID",
            "MakeRaw",
            "Make",
            "ModelNumberRaw",
            "ModelNumber",
            "SerialNumberRaw",
            "SerialNumber",
            "EquipmentTypeRaw",
            "EquipmentType",
            "KnownManufactureYear",
        ]
        with (
            canonical_path.open("w", newline="", encoding="utf-8") as f_can,
            baseline_out_path.open("w", newline="", encoding="utf-8") as f_out,
            attrs_long_path.open("w", newline="", encoding="utf-8") as f_attr,
        ):
            can_w = csv.DictWriter(f_can, fieldnames=fieldnames_canonical)
            can_w.writeheader()

            out_fields = fieldnames_canonical + [
                "DetectedBrand",
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
            out_w = csv.DictWriter(f_out, fieldnames=out_fields)
            out_w.writeheader()

            attr_fields = [
                "AssetID",
                "Make",
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
            attr_w = csv.DictWriter(f_attr, fieldnames=attr_fields)
            attr_w.writeheader()

            # Profiling accumulators.
            total = 0
            missing = Counter()
            by_brand_total = Counter()
            by_brand_total_with_serial = Counter()  # Records with non-empty SerialNumber
            by_brand_total_with_model = Counter()   # Records with non-empty ModelNumber
            by_brand_year_decoded = Counter()
            by_brand_year_correct = Counter()
            by_brand_year_decoded_and_known = Counter()
            by_brand_has_known_year = Counter()
            by_brand_attr_any = Counter()
            by_brand_attr_tons = Counter()
            by_brand_attr_conflict_rows = Counter()
            by_brand_typed_wo_context_rows = Counter()
            by_brand_missing_type = Counter()

            by_equipment = Counter()

            # By (brand, equipment_type) breakdowns for type-auditable reports.
            by_bt_total = Counter()
            by_bt_total_with_serial = Counter()
            by_bt_total_with_model = Counter()
            by_bt_year_decoded = Counter()
            by_bt_year_correct = Counter()
            by_bt_year_decoded_and_known = Counter()
            by_bt_has_known_year = Counter()
            by_bt_attr_any = Counter()
            by_bt_attr_tons = Counter()
            by_bt_attr_conflict_rows = Counter()
            by_bt_typed_wo_context_rows = Counter()
            by_bt_missing_type = Counter()

            for row in reader:
                make_raw = (row.get(cmap.make) if cmap.make else "") or ""
                model_raw = (row.get(cmap.model) if cmap.model else "") or ""
                serial_raw = (row.get(cmap.serial) if cmap.serial else "") or ""
                
                # Skip records where both model and serial are missing. 
                # These cannot be decoded and shouldn't count against coverage stats.
                if not model_raw.strip() and not serial_raw.strip():
                    continue

                total += 1

                asset_id_raw = (row.get(cmap.asset_id) if cmap.asset_id else "") or ""
                if not asset_id_raw:
                    # Stable fallback key: row number (1-based, excluding header)
                    asset_id_raw = f"ROW-{total}"
                serial_raw = (row.get(cmap.serial) if cmap.serial else "") or ""
                et_raw = (row.get(cmap.equipment_type) if cmap.equipment_type else "") or ""
                known_year_raw = (row.get(cmap.known_year) if cmap.known_year else "") or ""

                make = normalize_brand(make_raw, brand_alias_map)
                model = normalize_model(model_raw)
                serial = normalize_serial(serial_raw)
                _et_raw_norm, equipment_type = canonicalize_equipment_type(et_raw, equipment_vocab)

                known_year = _as_int(known_year_raw)

                if not make_raw:
                    missing["Make"] += 1
                if not model_raw:
                    missing["ModelNumber"] += 1
                if not serial_raw:
                    missing["SerialNumber"] += 1
                if known_year_raw and known_year is None:
                    missing["KnownManufactureYear_non_numeric"] += 1

                by_brand_total[make] += 1
                bt_key = (make, equipment_type or "")
                by_bt_total[bt_key] += 1
                if serial_raw.strip():
                    by_brand_total_with_serial[make] += 1
                    by_bt_total_with_serial[bt_key] += 1
                if model_raw.strip():
                    by_brand_total_with_model[make] += 1
                    by_bt_total_with_model[bt_key] += 1
                if equipment_type:
                    by_equipment[equipment_type] += 1
                else:
                    by_brand_missing_type[make] += 1
                    by_bt_missing_type[bt_key] += 1

                if known_year is not None:
                    by_brand_has_known_year[make] += 1
                    by_bt_has_known_year[bt_key] += 1

                can_row = {
                    "AssetID": asset_id_raw,
                    "MakeRaw": make_raw,
                    "Make": make,
                    "ModelNumberRaw": model_raw,
                    "ModelNumber": model,
                    "SerialNumberRaw": serial_raw,
                    "SerialNumber": serial,
                    "EquipmentTypeRaw": et_raw,
                    "EquipmentType": equipment_type,
                    "KnownManufactureYear": str(known_year) if known_year is not None else "",
                }
                can_w.writerow(can_row)

                # Baseline decode run using current Phase 2 engine components.
                sres = decode_serial(
                    make,
                    serial_raw,
                    serial_accepted,
                    equipment_type=equipment_type or None,
                    min_plausible_year=1980,
                )
                attrs, candidates, conflicts_n = (
                    decode_attributes_with_audit(make, model_raw, attr_accepted, equipment_type=equipment_type or None)
                    if attr_accepted
                    else ([], [], 0)
                )
                typed_wo_context = bool(sres.typed_rule_applied_without_type_context) or any(
                    a.typed_rule_applied_without_type_context for a in attrs
                )
                if conflicts_n > 0:
                    by_brand_attr_conflict_rows[make] += 1
                    by_bt_attr_conflict_rows[bt_key] += 1
                if typed_wo_context:
                    by_brand_typed_wo_context_rows[make] += 1
                    by_bt_typed_wo_context_rows[bt_key] += 1

                for a in attrs:
                    attr_w.writerow(
                        {
                            "AssetID": asset_id_raw,
                            "Make": make,
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

                decoded_any = (sres.confidence != "None") or bool(attrs)
                decode_status = "NotDecoded"
                if decoded_any:
                    decode_status = "Decoded" if (sres.confidence != "None" and attrs) else "Partial"

                if sres.manufacture_year is not None:
                    by_brand_year_decoded[make] += 1
                    by_bt_year_decoded[bt_key] += 1
                    if known_year is not None:
                        by_brand_year_decoded_and_known[make] += 1
                        by_bt_year_decoded_and_known[bt_key] += 1
                        if sres.manufacture_year == known_year:
                            by_brand_year_correct[make] += 1
                            by_bt_year_correct[bt_key] += 1
                if known_year is not None:
                    # Count as "in scope" for accuracy even if decode is missing.
                    pass

                if attrs:
                    by_brand_attr_any[make] += 1
                    by_bt_attr_any[bt_key] += 1
                    if any(a.attribute_name == "NominalCapacityTons" for a in attrs):
                        by_brand_attr_tons[make] += 1
                        by_bt_attr_tons[bt_key] += 1

                out_w.writerow(
                    {
                        **can_row,
                        "DetectedBrand": make,
                        "MatchedSerialStyle": sres.matched_style_name or "",
                        "MatchedSerialRuleEquipmentTypes": json.dumps(sres.rule_equipment_types, ensure_ascii=False),
                        "ManufactureYearRaw": sres.manufacture_year_raw or "",
                        "ManufactureYear": sres.manufacture_year or "",
                        "ManufactureMonthRaw": sres.manufacture_month_raw or "",
                        "ManufactureMonth": sres.manufacture_month or "",
                        "ManufactureWeekRaw": sres.manufacture_week_raw or "",
                        "ManufactureWeek": sres.manufacture_week or "",
                        "ManufactureDateAmbiguousDecade": "true" if sres.ambiguous_decade else "false",
                        "ManufactureDateConfidence": sres.confidence,
                        "ManufactureDateEvidence": sres.evidence,
                        "ManufactureDateSourceURL": sres.source_url,
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
                        "DecodeNotes": sres.notes,
                    }
                )

    # Scorecard by brand
    score_path = out_dir / "baseline_decoder_scorecard.csv"
    with score_path.open("w", newline="", encoding="utf-8") as f_score:
        fields = [
            "Brand",
            "N",
            "N_WithSerial",
            "N_WithModel",
            "YearDecodedN",
            "YearCoveragePct",
            "KnownYearN",
            "YearAccuracyPct",
            "AnyAttributesN",
            "AnyAttributesCoveragePct",
            "NominalCapacityTonsN",
            "NominalCapacityTonsCoveragePct",
            "AttributeConflictRowsN",
            "AttributeConflictRatePct",
            "TypedRuleWithoutTypeContextRowsN",
            "TypedRuleWithoutTypeContextRatePct",
        ]
        w = csv.DictWriter(f_score, fieldnames=fields)
        w.writeheader()
        for brand, n in sorted(by_brand_total.items(), key=lambda kv: (-kv[1], kv[0])):
            n_serial = by_brand_total_with_serial[brand]
            n_model = by_brand_total_with_model[brand]
            yd = by_brand_year_decoded[brand]
            ky = by_brand_has_known_year[brand]
            yc = by_brand_year_correct[brand]
            ydk = by_brand_year_decoded_and_known[brand]
            any_a = by_brand_attr_any[brand]
            tons_a = by_brand_attr_tons[brand]
            conflicts_n = by_brand_attr_conflict_rows[brand]
            typed_wo_ctx_n = by_brand_typed_wo_context_rows[brand]
            w.writerow(
                {
                    "Brand": brand,
                    "N": n,
                    "N_WithSerial": n_serial,
                    "N_WithModel": n_model,
                    "YearDecodedN": yd,
                    "YearCoveragePct": f"{(yd / n_serial * 100.0):.1f}" if n_serial else "",
                    "KnownYearN": ky,
                    "YearAccuracyPct": f"{(yc / ydk * 100.0):.1f}" if ydk else "",
                    "AnyAttributesN": any_a,
                    "AnyAttributesCoveragePct": f"{(any_a / n_model * 100.0):.1f}" if n_model else "",
                    "NominalCapacityTonsN": tons_a,
                    "NominalCapacityTonsCoveragePct": f"{(tons_a / n_model * 100.0):.1f}" if n_model else "",
                    "AttributeConflictRowsN": conflicts_n,
                    "AttributeConflictRatePct": f"{(conflicts_n / n * 100.0):.1f}" if n else "",
                    "TypedRuleWithoutTypeContextRowsN": typed_wo_ctx_n,
                    "TypedRuleWithoutTypeContextRatePct": f"{(typed_wo_ctx_n / n * 100.0):.1f}" if n else "",
                }
            )

    # Scorecard by brand x equipment type (type-auditable).
    score_by_type_path = out_dir / "baseline_decoder_scorecard_by_type.csv"
    with score_by_type_path.open("w", newline="", encoding="utf-8") as f_bt:
        fields = [
            "Brand",
            "EquipmentType",
            "N",
            "N_WithSerial",
            "N_WithModel",
            "KnownYearN",
            "YearDecodedN",
            "MissingYearN",
            "YearDecodedAndKnownN",
            "YearCorrectN",
            "WrongYearN",
            "YearCoveragePct",
            "YearAccuracyOnMatchesPct",
            "AnyAttributesN",
            "MissingAttrN",
            "AnyAttributesCoveragePct",
            "NominalCapacityTonsN",
            "NominalCapacityTonsCoveragePct",
            "AttributeConflictRowsN",
            "AttributeConflictRatePct",
            "TypedRuleWithoutTypeContextRowsN",
            "TypedRuleWithoutTypeContextRatePct",
        ]
        w = csv.DictWriter(f_bt, fieldnames=fields)
        w.writeheader()

        def _pct(num: int, den: int) -> float | None:
            if not den:
                return None
            return (num / den) * 100.0

        bt_rows: list[dict] = []
        for (brand, et), n in by_bt_total.items():
            n_serial = by_bt_total_with_serial[(brand, et)]
            n_model = by_bt_total_with_model[(brand, et)]
            yd = by_bt_year_decoded[(brand, et)]
            ky = by_bt_has_known_year[(brand, et)]
            ydk = by_bt_year_decoded_and_known[(brand, et)]
            yc = by_bt_year_correct[(brand, et)]
            wrong_year_n = max(ydk - yc, 0)
            missing_year_n = max(n_serial - yd, 0)
            any_a = by_bt_attr_any[(brand, et)]
            missing_attr_n = max(n_model - any_a, 0)
            tons_a = by_bt_attr_tons[(brand, et)]
            conflicts_n = by_bt_attr_conflict_rows[(brand, et)]
            typed_wo_ctx_n = by_bt_typed_wo_context_rows[(brand, et)]
            bt_rows.append(
                {
                    "Brand": brand,
                    "EquipmentType": et,
                    "N": n,
                    "N_WithSerial": n_serial,
                    "N_WithModel": n_model,
                    "KnownYearN": ky,
                    "YearDecodedN": yd,
                    "MissingYearN": missing_year_n,
                    "YearDecodedAndKnownN": ydk,
                    "YearCorrectN": yc,
                    "WrongYearN": wrong_year_n,
                    "YearCoveragePct": f"{_pct(yd, n_serial):.1f}" if _pct(yd, n_serial) is not None else "",
                    "YearAccuracyOnMatchesPct": f"{_pct(yc, ydk):.1f}" if _pct(yc, ydk) is not None else "",
                    "AnyAttributesN": any_a,
                    "MissingAttrN": missing_attr_n,
                    "AnyAttributesCoveragePct": f"{_pct(any_a, n_model):.1f}" if _pct(any_a, n_model) is not None else "",
                    "NominalCapacityTonsN": tons_a,
                    "NominalCapacityTonsCoveragePct": f"{_pct(tons_a, n_model):.1f}" if _pct(tons_a, n_model) is not None else "",
                    "AttributeConflictRowsN": conflicts_n,
                    "AttributeConflictRatePct": f"{_pct(conflicts_n, n):.1f}" if _pct(conflicts_n, n) is not None else "",
                    "TypedRuleWithoutTypeContextRowsN": typed_wo_ctx_n,
                    "TypedRuleWithoutTypeContextRatePct": f"{_pct(typed_wo_ctx_n, n):.1f}" if _pct(typed_wo_ctx_n, n) is not None else "",
                }
            )
        bt_rows_sorted = sorted(bt_rows, key=lambda r: (-int(r["N"]), r["Brand"], r["EquipmentType"] or ""))
        for row in bt_rows_sorted:
            w.writerow({k: row.get(k, "") for k in fields})

    # Next targets: make it easy to see what to improve next (highest-impact brands).
    next_targets_csv = out_dir / "next_targets_by_brand.csv"
    next_targets_md = out_dir / "next_targets.md"
    next_targets_json = out_dir / "next_targets.json"

    def _pct(num: int, den: int) -> float | None:
        if not den:
            return None
        return (num / den) * 100.0

    by_brand_rows: list[dict] = []
    for brand, n in by_brand_total.items():
        n_serial = by_brand_total_with_serial[brand]
        n_model = by_brand_total_with_model[brand]
        yd = by_brand_year_decoded[brand]
        ky = by_brand_has_known_year[brand]
        ydk = by_brand_year_decoded_and_known[brand]
        yc = by_brand_year_correct[brand]
        wrong_year_n = max(ydk - yc, 0)
        # Missing year = records with serial that weren't decoded
        missing_year_n = max(n_serial - yd, 0)

        any_a = by_brand_attr_any[brand]
        # Missing attr = records with model that weren't decoded
        missing_attr_n = max(n_model - any_a, 0)
        tons_a = by_brand_attr_tons[brand]

        by_brand_rows.append(
            {
                "Brand": brand,
                "N": n,
                "N_WithSerial": n_serial,
                "N_WithModel": n_model,
                "KnownYearN": ky,
                "YearDecodedN": yd,
                "MissingYearN": missing_year_n,
                "YearDecodedAndKnownN": ydk,
                "YearCorrectN": yc,
                "WrongYearN": wrong_year_n,
                "YearCoveragePct": f"{_pct(yd, n_serial):.1f}" if _pct(yd, n_serial) is not None else "",
                "YearAccuracyOnMatchesPct": f"{_pct(yc, ydk):.1f}" if _pct(yc, ydk) is not None else "",
                "AnyAttributesN": any_a,
                "MissingAttrN": missing_attr_n,
                "AnyAttributesCoveragePct": f"{_pct(any_a, n_model):.1f}" if _pct(any_a, n_model) is not None else "",
                "NominalCapacityTonsN": tons_a,
                "NominalCapacityTonsCoveragePct": f"{_pct(tons_a, n_model):.1f}" if _pct(tons_a, n_model) is not None else "",
            }
        )

    by_brand_rows_sorted = sorted(by_brand_rows, key=lambda r: (-int(r["N"]), r["Brand"]))
    with next_targets_csv.open("w", newline="", encoding="utf-8") as f_nt:
        fields = [
            "Brand",
            "N",
            "N_WithSerial",
            "N_WithModel",
            "KnownYearN",
            "YearDecodedN",
            "MissingYearN",
            "YearDecodedAndKnownN",
            "YearCorrectN",
            "WrongYearN",
            "YearCoveragePct",
            "YearAccuracyOnMatchesPct",
            "AnyAttributesN",
            "MissingAttrN",
            "AnyAttributesCoveragePct",
            "NominalCapacityTonsN",
            "NominalCapacityTonsCoveragePct",
        ]
        w = csv.DictWriter(f_nt, fieldnames=fields)
        w.writeheader()
        for row in by_brand_rows_sorted:
            w.writerow({k: row.get(k, "") for k in fields})

    # Compute top lists (filtering out tiny brands by KnownYearN/N thresholds to reduce noise).
    top_year_gaps = sorted(
        [r for r in by_brand_rows if int(r.get("KnownYearN") or 0) >= 20],
        key=lambda r: (-int(r["MissingYearN"]), -int(r["KnownYearN"]), -int(r["N"]), r["Brand"]),
    )[:15]
    top_wrong_year = sorted(
        [r for r in by_brand_rows if int(r.get("YearDecodedAndKnownN") or 0) >= 20],
        key=lambda r: (-int(r["WrongYearN"]), -int(r["YearDecodedAndKnownN"]), -int(r["N"]), r["Brand"]),
    )[:15]
    top_attr_gaps = sorted(
        [r for r in by_brand_rows if int(r.get("N") or 0) >= 20],
        key=lambda r: (-int(r["MissingAttrN"]), -int(r["N"]), r["Brand"]),
    )[:15]

    lines: list[str] = []
    lines.append(f"# Next Targets — {run_id}\n\n")
    lines.append(f"- Baseline output: `{baseline_out_path}`\n")
    lines.append(f"- Scorecard: `{score_path}`\n")
    lines.append(f"- Full per-brand table: `{next_targets_csv}`\n\n")

    lines.append("## Top Year Coverage Gaps (MissingYearN)\n")
    for r in top_year_gaps:
        lines.append(
            f"- {r['Brand']}: MissingYear={r['MissingYearN']} (Decoded={r['YearDecodedN']}/{r['N_WithSerial']} with serial; Coverage={r['YearCoveragePct']}%)\n"
        )

    lines.append("\n## Top Wrong-Year Volume (WrongYearN)\n")
    for r in top_wrong_year:
        acc = r.get("YearAccuracyOnMatchesPct") or ""
        lines.append(
            f"- {r['Brand']}: WrongYear={r['WrongYearN']} (Decoded&Known={r['YearDecodedAndKnownN']}; Accuracy={acc}%)\n"
        )

    lines.append("\n## Top Attribute Coverage Gaps (MissingAttrN)\n")
    for r in top_attr_gaps:
        lines.append(
            f"- {r['Brand']}: MissingAttr={r['MissingAttrN']} "
            f"(AnyAttr={r['AnyAttributesN']}/{r['N_WithModel']} with model; Coverage={r['AnyAttributesCoveragePct']}%)\n"
        )

    next_targets_md.write_text("".join(lines), encoding="utf-8")
    next_targets_json.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "top_year_gaps": top_year_gaps,
                "top_wrong_year": top_wrong_year,
                "top_attr_gaps": top_attr_gaps,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # Next targets by type (brand x type segments).
    next_targets_by_type_csv = out_dir / "next_targets_by_type.csv"
    next_targets_by_type_md = out_dir / "next_targets_by_type.md"

    # Reuse bt_rows_sorted (already computed above for scorecard_by_type).
    with next_targets_by_type_csv.open("w", newline="", encoding="utf-8") as f_btnt:
        fields = [
            "Brand",
            "EquipmentType",
            "N",
            "N_WithSerial",
            "N_WithModel",
            "KnownYearN",
            "YearDecodedN",
            "MissingYearN",
            "YearDecodedAndKnownN",
            "YearCorrectN",
            "WrongYearN",
            "YearCoveragePct",
            "YearAccuracyOnMatchesPct",
            "AnyAttributesN",
            "MissingAttrN",
            "AnyAttributesCoveragePct",
            "NominalCapacityTonsN",
            "NominalCapacityTonsCoveragePct",
            "AttributeConflictRowsN",
            "TypedRuleWithoutTypeContextRowsN",
        ]
        w = csv.DictWriter(f_btnt, fieldnames=fields)
        w.writeheader()
        for row in bt_rows_sorted:
            w.writerow({k: row.get(k, "") for k in fields})

    # Produce a short markdown focusing on the largest problem segments.
    def _label_et(v: str) -> str:
        return v if v else "(MISSING)"

    top_bt_year_gaps = sorted(
        [r for r in bt_rows_sorted if int(r.get("KnownYearN") or 0) >= 20],
        key=lambda r: (-int(r.get("MissingYearN") or 0), -int(r.get("KnownYearN") or 0), -int(r.get("N") or 0)),
    )[:20]
    top_bt_wrong_year = sorted(
        [r for r in bt_rows_sorted if int(r.get("YearDecodedAndKnownN") or 0) >= 20],
        key=lambda r: (-int(r.get("WrongYearN") or 0), -int(r.get("YearDecodedAndKnownN") or 0), -int(r.get("N") or 0)),
    )[:20]
    top_bt_attr_gaps = sorted(
        [r for r in bt_rows_sorted if int(r.get("N") or 0) >= 20],
        key=lambda r: (-int(r.get("MissingAttrN") or 0), -int(r.get("N") or 0)),
    )[:20]
    top_bt_conflicts = sorted(
        [r for r in bt_rows_sorted if int(r.get("N") or 0) >= 20],
        key=lambda r: (-int(r.get("AttributeConflictRowsN") or 0), -int(r.get("N") or 0)),
    )[:20]

    lines = []
    lines.append(f"# Next Targets by Equipment Type — {run_id}\n\n")
    lines.append(f"- Baseline output: `{baseline_out_path}`\n")
    lines.append(f"- Scorecard (by type): `{score_by_type_path}`\n")
    lines.append(f"- Full brand×type table: `{next_targets_by_type_csv}`\n\n")

    lines.append("## Top Year Coverage Gaps (Brand × Type)\n")
    for r in top_bt_year_gaps:
        lines.append(
            f"- {r['Brand']} / {_label_et(r.get('EquipmentType') or '')}: MissingYear={r['MissingYearN']} "
            f"(Decoded={r['YearDecodedN']}/{r['N_WithSerial']} with serial; Coverage={r['YearCoveragePct']}%)\n"
        )

    lines.append("\n## Top Wrong-Year Volume (Brand × Type)\n")
    for r in top_bt_wrong_year:
        lines.append(
            f"- {r['Brand']} / {_label_et(r.get('EquipmentType') or '')}: WrongYear={r['WrongYearN']} "
            f"(Decoded&Known={r['YearDecodedAndKnownN']}; Accuracy={r['YearAccuracyOnMatchesPct']}%)\n"
        )

    lines.append("\n## Top Attribute Coverage Gaps (Brand × Type)\n")
    for r in top_bt_attr_gaps:
        lines.append(
            f"- {r['Brand']} / {_label_et(r.get('EquipmentType') or '')}: MissingAttr={r['MissingAttrN']} "
            f"(AnyAttr={r['AnyAttributesN']}/{r['N_WithModel']} with model; Coverage={r['AnyAttributesCoveragePct']}%)\n"
        )

    lines.append("\n## Top Attribute Conflicts (Brand × Type)\n")
    for r in top_bt_conflicts:
        lines.append(
            f"- {r['Brand']} / {_label_et(r.get('EquipmentType') or '')}: Conflicts={r['AttributeConflictRowsN']} (N={r['N']})\n"
        )

    next_targets_by_type_md.write_text("".join(lines), encoding="utf-8")

    # Training data profile markdown
    profile_path = out_dir / "training_data_profile.md"
    top_brands = by_brand_total.most_common(25)
    top_types = by_equipment.most_common(25)

    profile_lines = []
    profile_lines.append(f"# Training Data Profile — {run_id}\n")
    profile_lines.append(f"- Source: `{input_path}`\n")
    profile_lines.append(f"- Ruleset: `{ruleset_dir}`\n")
    profile_lines.append(f"- Rows: {total}\n")
    profile_lines.append("\n## Missingness\n")
    if missing:
        for k, v in missing.most_common():
            profile_lines.append(f"- {k}: {v} ({(v/total*100.0):.1f}%)\n")
    else:
        profile_lines.append("- (none)\n")

    profile_lines.append("\n## Top Brands\n")
    for b, n in top_brands:
        profile_lines.append(f"- {b}: {n}\n")

    profile_lines.append("\n## Top Equipment Types\n")
    for t, n in top_types:
        profile_lines.append(f"- {t}: {n}\n")

    profile_path.write_text("".join(profile_lines), encoding="utf-8")

    # Convenience summary JSON
    summary = {
        "run_id": run_id,
        "input_path": str(input_path),
        "ruleset_dir": str(ruleset_dir),
        "rows": total,
        "missing": dict(missing),
        "top_brands": top_brands,
        "top_equipment_types": top_types,
        "outputs": {
            "source_column_map": str(out_dir / "source_column_map.csv"),
            "canonical_assets": str(out_dir / "canonical_assets.csv"),
            "baseline_decoder_output": str(out_dir / "baseline_decoder_output.csv"),
            "baseline_attributes_long": str(out_dir / "baseline_attributes_long.csv"),
            "baseline_scorecard": str(out_dir / "baseline_decoder_scorecard.csv"),
            "baseline_scorecard_by_type": str(out_dir / "baseline_decoder_scorecard_by_type.csv"),
            "next_targets_markdown": str(next_targets_md),
            "next_targets_by_brand_csv": str(next_targets_csv),
            "next_targets_json": str(next_targets_json),
            "next_targets_by_type_markdown": str(out_dir / "next_targets_by_type.md"),
            "next_targets_by_type_csv": str(out_dir / "next_targets_by_type.csv"),
            "training_data_profile": str(out_dir / "training_data_profile.md"),
        },
    }
    (out_dir / "phase3_baseline_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(str(out_dir))
    return 0
