from __future__ import annotations

import json
import re
from typing import Any


_STYLE_PREFIX_RE = re.compile(r"^\s*Style\s*(\d+)\s*:", re.IGNORECASE)


def _style_number(style_name: str | None) -> str | None:
    if not style_name:
        return None
    m = _STYLE_PREFIX_RE.match(style_name.strip())
    return m.group(1) if m else None


def _loads_json_maybe(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return default
    s = value.strip()
    if not s:
        return default
    try:
        return json.loads(s)
    except Exception:
        return default


def _is_deterministic_year_rule(date_fields: dict[str, Any]) -> bool:
    """
    Conservative check: is there a year spec that is not chart-required and has at least one extraction method?
    """
    if not isinstance(date_fields, dict):
        return False
    year = date_fields.get("year") or {}
    if not isinstance(year, dict):
        return False
    if year.get("requires_chart") is True:
        return False
    return bool(year.get("positions") or year.get("positions_list") or year.get("pattern") or year.get("mapping"))


def prune_superseded_serial_guidance(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove guidance-only serial rows that are superseded by deterministic decode rules for the same brand/style.

    Policy (safe + narrow):
    - Only affects rows where style_name begins with "Style <n>:"
    - Drop guidance rows when a deterministic year decode rule exists for the same (brand, style_number).
    """
    has_decode: set[tuple[str, str]] = set()
    for r in rows:
        if (r.get("rule_type") or "decode") != "decode":
            continue
        brand = (r.get("brand") or "").strip()
        sn = _style_number(r.get("style_name"))
        if not brand or not sn:
            continue
        date_fields = _loads_json_maybe(r.get("date_fields"), {})
        if _is_deterministic_year_rule(date_fields):
            has_decode.add((brand, sn))

    out: list[dict[str, Any]] = []
    for r in rows:
        if (r.get("rule_type") or "decode") != "guidance":
            out.append(r)
            continue
        brand = (r.get("brand") or "").strip()
        sn = _style_number(r.get("style_name"))
        if brand and sn and (brand, sn) in has_decode:
            continue
        out.append(r)
    return out


def prune_superseded_attribute_guidance(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove generic attribute guidance rows that are superseded by deterministic decode rules.

    Policy (safe + narrow):
    - Only removes guidance rows with:
      - guidance_action == "chart_required"
      - empty model_regex (brand-wide guidance)
      - empty value_extraction dict
    - Only when at least one decode rule exists for (brand, attribute_name).
    """
    has_decode: set[tuple[str, str]] = set()
    for r in rows:
        if (r.get("rule_type") or "decode") != "decode":
            continue
        brand = (r.get("brand") or "").strip()
        attr = (r.get("attribute_name") or "").strip()
        if brand and attr:
            has_decode.add((brand, attr))

    out: list[dict[str, Any]] = []
    for r in rows:
        if (r.get("rule_type") or "decode") != "guidance":
            out.append(r)
            continue
        if (r.get("guidance_action") or "").strip() != "chart_required":
            out.append(r)
            continue
        brand = (r.get("brand") or "").strip()
        attr = (r.get("attribute_name") or "").strip()
        if not brand or not attr or (brand, attr) not in has_decode:
            out.append(r)
            continue
        model_regex = (r.get("model_regex") or "").strip()
        ve = _loads_json_maybe(r.get("value_extraction"), {})
        if model_regex:
            out.append(r)
            continue
        if isinstance(ve, dict) and ve:
            out.append(r)
            continue
        out.append(r)  # default keep; guarded below
        # We only drop when it's truly the generic empty guidance row.
        if not model_regex and isinstance(ve, dict) and not ve:
            out.pop()
    return out

