from __future__ import annotations

import csv
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

from msl.pipeline.common import ensure_dir, resolve_run_date, write_csv
from msl.pipeline.ruleset_manager import cleanup_old_rulesets, update_current_pointer


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _load_manual_serial_overrides(base_dir: Path) -> list[dict]:
    """
    Optional manual override file:
      data/manual_overrides/serial_overrides.jsonl
    """
    path = base_dir / "serial_overrides.jsonl"
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    return rows


def _load_manual_attribute_overrides(base_dir: Path) -> list[dict]:
    """
    Optional manual/derived override file:
      data/manual_overrides/attribute_overrides.jsonl
    """
    path = base_dir / "attribute_overrides.jsonl"
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    return rows


def _apply_serial_overrides(serial_rules: list[dict], overrides: list[dict]) -> list[dict]:
    if not overrides:
        return serial_rules
    index: dict[tuple[str, str], list[dict]] = {}
    for o in overrides:
        brand = (o.get("brand") or "").strip()
        style = (o.get("style_name") or "").strip()
        if not brand or not style:
            continue
        index.setdefault((brand, style), []).append(o)

    updated: list[dict] = []
    for r in serial_rules:
        brand = (r.get("brand") or "").strip()
        style = (r.get("style_name") or "").strip()
        key = (brand, style)
        os_ = index.get(key, [])
        if not os_:
            updated.append(r)
            continue

        date_fields = r.get("date_fields") or {}
        if not isinstance(date_fields, dict):
            date_fields = {}

        changed = False
        for o in os_:
            field = (o.get("field") or "").strip().lower()
            if field not in {"year", "month", "week", "day"}:
                continue
            spec = date_fields.get(field) or {}
            if not isinstance(spec, dict):
                spec = {}
            # Allow overriding a requires_chart field with an actual mapping.
            if "mapping" in o and isinstance(o.get("mapping"), dict):
                spec["mapping"] = o["mapping"]
                if spec.get("requires_chart") is True:
                    spec.pop("requires_chart", None)
                    spec.pop("snippet", None)
                changed = True
            if "positions" in o and isinstance(o.get("positions"), dict):
                spec["positions"] = o["positions"]
                changed = True
            if "pattern" in o and isinstance(o.get("pattern"), dict):
                spec["pattern"] = o["pattern"]
                changed = True
            if "transform" in o and isinstance(o.get("transform"), dict):
                spec["transform"] = o["transform"]
                changed = True
            date_fields[field] = spec

        if changed:
            r2 = dict(r)
            r2["date_fields"] = date_fields
            updated.append(r2)
        else:
            updated.append(r)
    return updated


def _prune_serial_guidance_artifacts(serial_rules: list[dict]) -> list[dict]:
    """
    Remove low-signal guidance rows that are artifacts of Phase 1 extraction (style list items),
    while keeping meaningful guidance when it's the only representation of a style.

    Policy:
    - Only prunes `rule_type=guidance` + `guidance_action=no_data`
    - Only prunes when there exists at least one decode rule for the same (brand, style_number)
    - Targets truncated `style_name` like `Style 5: 5` or `Style 3:`
    """

    def extract_style_number(style_name: str) -> str | None:
        m = re.match(r"^\s*Style\s*(\d+)\s*:", (style_name or "").strip(), flags=re.IGNORECASE)
        return m.group(1) if m else None

    def is_truncated_style_name(style_name: str) -> bool:
        s = (style_name or "").strip()
        if not s:
            return True
        if re.match(r"^\s*Style\s*\d+\s*:\s*$", s, flags=re.IGNORECASE):
            return True
        m = re.match(r"^\s*Style\s*\d+\s*:\s*(.+?)\s*$", s, flags=re.IGNORECASE)
        if not m:
            return False
        tail = m.group(1).strip()
        if " " in tail or "-" in tail or "/" in tail:
            return False
        return len(tail) <= 3

    decode_style_numbers: set[tuple[str, str]] = set()
    for r in serial_rules:
        if (r.get("rule_type") or "decode") != "decode":
            continue
        brand = (r.get("brand") or "").strip()
        sn = extract_style_number(r.get("style_name") or "")
        if brand and sn:
            decode_style_numbers.add((brand, sn))

    out: list[dict] = []
    for r in serial_rules:
        if (r.get("rule_type") or "decode") != "guidance":
            out.append(r)
            continue
        if (r.get("guidance_action") or "").strip() != "no_data":
            out.append(r)
            continue
        brand = (r.get("brand") or "").strip()
        sn = extract_style_number(r.get("style_name") or "")
        if brand and sn and (brand, sn) in decode_style_numbers and is_truncated_style_name(r.get("style_name") or ""):
            continue
        out.append(r)
    return out


def _apply_attribute_overrides(attribute_rules: list[dict], overrides: list[dict]) -> list[dict]:
    """
    Current policy: append overrides (after lightweight de-dupe).
    Overrides should be full AttributeDecodeRule-shaped dicts (decode or guidance).
    """
    if not overrides:
        return attribute_rules
    existing: set[tuple] = set()
    for r in attribute_rules:
        existing.add(
            (
                (r.get("rule_type") or "").strip(),
                (r.get("brand") or "").strip(),
                (r.get("attribute_name") or "").strip(),
                (r.get("model_regex") or "").strip(),
                json.dumps(r.get("value_extraction") or {}, sort_keys=True),
                (r.get("source_url") or "").strip(),
            )
        )
    out = list(attribute_rules)
    for o in overrides:
        key = (
            (o.get("rule_type") or "").strip(),
            (o.get("brand") or "").strip(),
            (o.get("attribute_name") or "").strip(),
            (o.get("model_regex") or "").strip(),
            json.dumps(o.get("value_extraction") or {}, sort_keys=True),
            (o.get("source_url") or "").strip(),
        )
        if key in existing:
            continue
        existing.add(key)
        out.append(o)
    return out


def _validate_serial_rule(rule: dict) -> list[str]:
    errors: list[str] = []
    rule_type = rule.get("rule_type") or "decode"
    if rule_type == "guidance":
        for k in ["brand", "style_name", "guidance_action", "guidance_text", "source_url", "retrieved_on"]:
            if not rule.get(k):
                errors.append(f"missing:{k}")
        # date_fields is optional for guidance but should be a dict if present.
        if "date_fields" in rule and rule.get("date_fields") is not None and not isinstance(rule.get("date_fields"), dict):
            errors.append("bad_date_fields")
        return errors

    for k in [
        "brand",
        "style_name",
        "serial_regex",
        "date_fields",
        "example_serials",
        "decade_ambiguity",
        "evidence_excerpt",
        "source_url",
        "retrieved_on",
    ]:
        if k not in rule:
            errors.append(f"missing:{k}")
    try:
        rx = re.compile(rule.get("serial_regex", ""))
    except Exception as e:
        errors.append(f"bad_regex:{e}")
        return errors
    examples = rule.get("example_serials") or []
    if not isinstance(examples, list) or not examples:
        errors.append("no_examples")
        return errors
    for ex in examples[:50]:
        if not isinstance(ex, str) or not rx.search(ex):
            errors.append(f"example_no_match:{ex}")
            break

    # Validate positions/positions_list are within bounds for at least one example.
    example_len = len(examples[0]) if isinstance(examples[0], str) else None
    if example_len:
        for field_name, spec in (rule.get("date_fields") or {}).items():
            if not isinstance(spec, dict):
                continue
            if spec.get("requires_chart") is True:
                continue
            if "positions" in spec:
                pos = spec["positions"]
                if pos["start"] < 1 or pos["end"] > example_len:
                    errors.append(f"out_of_bounds:{field_name}")
            if "positions_list" in spec:
                for p in spec["positions_list"]:
                    if p < 1 or p > example_len:
                        errors.append(f"out_of_bounds:{field_name}")
                        break
            if "pattern" in spec:
                pat = spec.get("pattern") or {}
                if not isinstance(pat, dict) or "regex" not in pat:
                    errors.append(f"bad_pattern:{field_name}")
                    continue
                try:
                    prx = re.compile(pat["regex"])
                except Exception as e:
                    errors.append(f"bad_pattern_regex:{field_name}:{e}")
                    continue
                group = pat.get("group")
                if group is not None and not isinstance(group, int):
                    errors.append(f"bad_pattern_group:{field_name}")
                    continue
                matched = False
                for ex in examples[:50]:
                    m = prx.search(ex)
                    if not m:
                        continue
                    matched = True
                    if group is not None:
                        try:
                            _ = m.group(group)
                        except Exception:
                            errors.append(f"bad_pattern_group:{field_name}")
                    break
                if not matched:
                    errors.append(f"pattern_no_match:{field_name}")
    return errors


def _validate_attribute_rule(rule: dict) -> list[str]:
    errors: list[str] = []
    rule_type = rule.get("rule_type") or "decode"

    for k in ["brand", "attribute_name", "value_extraction", "source_url", "retrieved_on"]:
        if k not in rule:
            errors.append(f"missing:{k}")

    if rule_type == "guidance":
        if not rule.get("guidance_action") or not rule.get("guidance_text"):
            errors.append("guidance_missing_fields")
        return errors

    ve = rule.get("value_extraction") or {}
    if not isinstance(ve, dict) or not ve:
        errors.append("missing_value_extraction")
        return errors

    if "positions" not in ve and "pattern" not in ve:
        errors.append("value_extraction_missing_positions_or_pattern")

    return errors


def cmd_validate(args) -> int:
    staged_dir = Path(args.staged_dir)
    run_date = resolve_run_date(args.run_date, str(staged_dir))

    out_norm_dir = ensure_dir(Path(args.out_normalized_dir) / run_date)
    out_reports_dir = ensure_dir(Path(args.out_reports_dir) / run_date)

    serial_rules = _load_jsonl(staged_dir / "serial_rules.jsonl")
    attribute_rules = _load_jsonl(staged_dir / "attribute_rules.jsonl")
    skips = _load_jsonl(staged_dir / "skips.jsonl")

    # Optional manual overrides (no-op if file absent).
    overrides_dir = Path("data/manual_overrides")
    serial_overrides = _load_manual_serial_overrides(overrides_dir)
    if serial_overrides:
        serial_rules = _apply_serial_overrides(serial_rules, serial_overrides)
    serial_rules = _prune_serial_guidance_artifacts(serial_rules)
    attribute_overrides = _load_manual_attribute_overrides(overrides_dir)
    if attribute_overrides:
        attribute_rules = _apply_attribute_overrides(attribute_rules, attribute_overrides)

    exceptions: list[dict] = []
    valid_serial: list[dict] = []
    for r in serial_rules:
        errs = _validate_serial_rule(r)
        if errs:
            exceptions.append({"type": "SerialDecodeRule", "errors": errs, "rule": r})
        else:
            valid_serial.append(r)

    # Export minimal normalized CSVs (can expand schema later as needed)
    serial_csv = out_norm_dir / "SerialDecodeRule.csv"
    write_csv(
        serial_csv,
        fieldnames=[
            "rule_type",
            "brand",
            "style_name",
            "serial_regex",
            "equipment_types",
            "date_fields",
            "example_serials",
            "decade_ambiguity",
            "guidance_action",
            "guidance_text",
            "evidence_excerpt",
            "source_url",
            "retrieved_on",
            "image_urls",
        ],
        rows=[
            {
                "rule_type": r.get("rule_type", "decode"),
                **{k: r.get(k, "") for k in ["brand", "style_name", "serial_regex", "evidence_excerpt", "source_url", "retrieved_on"]},
                "equipment_types": json.dumps(r.get("equipment_types", []), ensure_ascii=False),
                "date_fields": json.dumps(r.get("date_fields", {}), ensure_ascii=False),
                "example_serials": json.dumps(r.get("example_serials", []), ensure_ascii=False),
                "decade_ambiguity": json.dumps(r.get("decade_ambiguity", {}), ensure_ascii=False),
                "guidance_action": r.get("guidance_action", ""),
                "guidance_text": r.get("guidance_text", ""),
                "image_urls": json.dumps(r.get("image_urls", []), ensure_ascii=False),
            }
            for r in valid_serial
        ],
    )

    attr_csv = out_norm_dir / "AttributeDecodeRule.csv"
    attr_exceptions: list[dict] = []
    valid_attr: list[dict] = []
    for r in attribute_rules:
        errs = _validate_attribute_rule(r)
        if errs:
            attr_exceptions.append({"type": "AttributeDecodeRule", "errors": errs, "rule": r})
        else:
            valid_attr.append(r)

    write_csv(
        attr_csv,
        fieldnames=[
            "rule_type",
            "brand",
            "model_regex",
            "attribute_name",
            "equipment_types",
            "value_extraction",
            "units",
            "examples",
            "limitations",
            "guidance_action",
            "guidance_text",
            "evidence_excerpt",
            "source_url",
            "retrieved_on",
            "image_urls",
        ],
        rows=[
            {
                "rule_type": r.get("rule_type", "decode"),
                "brand": r.get("brand", ""),
                "model_regex": r.get("model_regex", ""),
                "attribute_name": r.get("attribute_name", ""),
                "equipment_types": json.dumps(r.get("equipment_types", []), ensure_ascii=False),
                "value_extraction": json.dumps(r.get("value_extraction", {}), ensure_ascii=False),
                "units": r.get("units", ""),
                "examples": json.dumps(r.get("examples", []), ensure_ascii=False),
                "limitations": r.get("limitations", ""),
                "guidance_action": r.get("guidance_action", ""),
                "guidance_text": r.get("guidance_text", ""),
                "evidence_excerpt": r.get("evidence_excerpt", ""),
                "source_url": r.get("source_url", ""),
                "retrieved_on": r.get("retrieved_on", ""),
                "image_urls": json.dumps(r.get("image_urls", []), ensure_ascii=False),
            }
            for r in valid_attr
        ],
    )

    exc_path = out_reports_dir / "validation_exceptions.jsonl"
    with exc_path.open("w", encoding="utf-8") as f:
        for e in exceptions:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
        for e in attr_exceptions:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    review_path = out_reports_dir / "review_queue.csv"
    write_csv(
        review_path,
        fieldnames=["brand", "source_url", "section_title", "issue_type", "notes", "raw_html_path"],
        rows=[
            {
                "brand": s.get("brand", ""),
                "source_url": s.get("source_url", ""),
                "section_title": s.get("section_title", ""),
                "issue_type": "LLM_SKIP",
                "notes": s.get("reason", ""),
                "raw_html_path": s.get("raw_html_path", ""),
            }
            for s in skips
        ],
    )

    # Update CURRENT.txt pointer to this new ruleset
    update_current_pointer(out_norm_dir)
    print(f"Updated CURRENT.txt -> {out_norm_dir}")

    # Auto-cleanup old rulesets unless --no-cleanup specified
    if not getattr(args, "no_cleanup", False):
        cleanup_old_rulesets()

    print(str(out_norm_dir))
    print(str(out_reports_dir))
    return 0
