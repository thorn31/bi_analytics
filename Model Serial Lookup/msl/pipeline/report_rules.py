from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from msl.pipeline.ruleset_manager import resolve_ruleset_dir


def _load_csv_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _json_field(value: str) -> object:
    if not value:
        return None
    v = value.strip()
    if not v:
        return None
    if v[0] not in "[{":
        return None
    try:
        return json.loads(v)
    except Exception:
        return None


def _report_serial(rows: list[dict]) -> str:
    total = len(rows)
    by_type = Counter(r.get("rule_type") or "" for r in rows)
    brands_any = {r.get("brand") for r in rows if r.get("brand")}
    brands_decode = {r.get("brand") for r in rows if (r.get("brand") and r.get("rule_type") == "decode")}

    guidance_actions = Counter(
        (r.get("guidance_action") or "") for r in rows if (r.get("rule_type") == "guidance")
    )

    # Brand-level stats
    brand_counts = defaultdict(lambda: Counter())
    for r in rows:
        b = r.get("brand") or ""
        if not b:
            continue
        brand_counts[b][r.get("rule_type") or ""] += 1

    top_guidance = sorted(
        ((b, c.get("guidance", 0), c.get("decode", 0)) for b, c in brand_counts.items()),
        key=lambda x: (-x[1], x[0]),
    )[:15]

    lines: list[str] = []
    lines.append("SerialDecodeRule")
    lines.append(f"- rows: {total}")
    lines.append(f"- rule_type: {dict(by_type)}")
    lines.append(f"- brands: {len(brands_any)} (decode brands: {len(brands_decode)})")
    if guidance_actions:
        lines.append(f"- guidance_action: {dict(guidance_actions.most_common(10))}")
    if top_guidance:
        lines.append("- top brands by guidance rows:")
        for b, g, d in top_guidance:
            lines.append(f"  - {b}: guidance={g}, decode={d}")
    return "\n".join(lines)


def _report_attribute(rows: list[dict]) -> str:
    total = len(rows)
    by_type = Counter(r.get("rule_type") or "" for r in rows)
    brands_any = {r.get("brand") or r.get("oem_family") for r in rows if (r.get("brand") or r.get("oem_family"))}
    brands_decode = {
        r.get("brand") or r.get("oem_family")
        for r in rows
        if ((r.get("brand") or r.get("oem_family")) and r.get("rule_type") == "decode")
    }
    attrs = Counter(r.get("attribute_name") or "" for r in rows)

    lines: list[str] = []
    lines.append("AttributeDecodeRule")
    lines.append(f"- rows: {total}")
    lines.append(f"- rule_type: {dict(by_type)}")
    lines.append(f"- brands: {len(brands_any)} (decode brands: {len(brands_decode)})")
    lines.append(f"- attributes: {dict(attrs.most_common(10))}")
    return "\n".join(lines)


def cmd_report(args) -> int:
    base_dir = Path(args.rules_base_dir)
    ruleset_dir = resolve_ruleset_dir(getattr(args, "ruleset_dir", None) or None, base_dir=base_dir)

    if ruleset_dir is None:
        raise SystemExit(
            f"No ruleset dir found. Pass --ruleset-dir or ensure CURRENT.txt exists in {base_dir}."
        )

    serial_path = Path(args.serial_rules_csv) if args.serial_rules_csv else (ruleset_dir / "SerialDecodeRule.csv")
    attr_path = (
        Path(args.attribute_rules_csv) if args.attribute_rules_csv else (ruleset_dir / "AttributeDecodeRule.csv")
    )

    print(f"Ruleset: {ruleset_dir}")

    if serial_path.exists():
        serial_rows = _load_csv_rows(serial_path)
        print(_report_serial(serial_rows))
    else:
        print("SerialDecodeRule")
        print(f"- missing: {serial_path}")

    if attr_path.exists():
        attr_rows = _load_csv_rows(attr_path)
        print(_report_attribute(attr_rows))
    else:
        print("AttributeDecodeRule")
        print(f"- missing: {attr_path}")

    return 0

