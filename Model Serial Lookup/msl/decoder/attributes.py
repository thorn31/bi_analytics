from __future__ import annotations

import json
import re
from dataclasses import dataclass

from msl.decoder.io import AttributeRule
from msl.decoder.normalize import normalize_model
from msl.decoder.normalize import normalize_text


@dataclass(frozen=True)
class DecodedAttribute:
    attribute_name: str
    value_raw: str
    value: str | float | int
    units: str
    confidence: str  # High|Medium|Low|None
    evidence: str
    source_url: str
    rule_equipment_types: list[str]
    typed_rule_applied_without_type_context: bool


@dataclass(frozen=True)
class AttributeCandidate:
    attribute_name: str
    value_raw: str
    value: str | float | int
    units: str
    confidence: str
    evidence: str
    source_url: str
    rule_equipment_types: list[str]
    typed_rule_applied_without_type_context: bool
    score: float


def _regex_specificity_score(pattern: str) -> float:
    """
    Heuristic: higher score means a regex is more specific (more literal signal, fewer wildcards).
    Safe + deterministic; doesn't attempt full regex parsing.
    """
    if not pattern:
        return 0.0
    # Favor literal alnum characters (they usually represent fixed prefixes/codes).
    literal_alnum = sum(1 for ch in pattern if ch.isalnum())
    # Penalize common "make it match anything" constructs.
    wildcard = pattern.count(".*") + pattern.count(".+") + pattern.count(".?")
    char_classes = pattern.count("[")
    return float(literal_alnum) - 2.0 * float(wildcard) - 0.5 * float(char_classes)


def _extract_from_positions(model: str, positions: dict) -> str | None:
    try:
        start = int(positions["start"])
        end = int(positions["end"])
    except Exception:
        return None
    if start < 1 or end < start or end > len(model):
        return None
    return model[start - 1 : end]


def _extract_from_pattern(model: str, pat: dict) -> str | None:
    if not isinstance(pat, dict) or "regex" not in pat:
        return None
    try:
        rx = re.compile(pat["regex"])
    except Exception:
        return None
    m = rx.search(model)
    if not m:
        return None
    group = pat.get("group")
    if group is None:
        return m.group(0)
    try:
        return m.group(int(group))
    except Exception:
        return None


def _as_number(value: str) -> float | None:
    v = value.strip()
    try:
        return float(v)
    except Exception:
        return None


def _apply_transform(value: str, transform: dict) -> str | float | int:
    if not isinstance(transform, dict) or "expression" not in transform:
        return value
    expr = transform.get("expression")
    # Only support the transforms we emit in Phase 1 today.
    if expr == "tons = code / 12":
        num = _as_number(value)
        if num is None:
            return value
        return num / 12.0
    return value


def _is_manual_source(source_url: str | None) -> bool:
    s = (source_url or "").strip().lower()
    return s in {"manual_additions", "manual_override", "manual"} or s.startswith("manual:")


def _collect_attribute_candidates(
    brand: str,
    model_raw: str | None,
    rules: list[AttributeRule],
    *,
    equipment_type: str | None,
) -> list[AttributeCandidate]:
    model = normalize_model(model_raw)
    if not model:
        return []

    # Only use deterministic decode rules; guidance can be surfaced later if desired.
    brand_rules = [r for r in rules if r.brand == brand and r.rule_type == "decode"]
    preferred_source_hint = {
        "CARRIER/ICP": "carrier-tonnage-decoder",
        "TRANE": "trane-tonnage-decoder",
        "YORK/JCI": "york-tonnage-decoder",
        "RHEEM/RUUD": "rheem-tonnage-decoder",
        "GOODMAN/AMANA/DAIKIN": "goodman-tonnage-decoder",
    }.get(brand, "")
    if preferred_source_hint:
        brand_rules.sort(key=lambda r: (preferred_source_hint not in (r.source_url or "").lower(), r.source_url or ""))
    # Build candidates first, then pick the best per attribute to avoid conflicting values.
    candidates: list[AttributeCandidate] = []
    equipment_type_norm = normalize_text(equipment_type or "") if equipment_type else ""

    for r in brand_rules:
        # Equipment type gating (if provided on the rule).
        typed_rule = bool(r.equipment_types)
        typed_without_context = False
        if typed_rule:
            if equipment_type_norm:
                if normalize_text(equipment_type_norm) not in {normalize_text(t) for t in r.equipment_types}:
                    continue
            else:
                typed_without_context = True

        if r.model_regex:
            try:
                mrx = re.compile(r.model_regex)
            except Exception:
                continue
            if not mrx.search(model):
                continue

        ve = r.value_extraction or {}
        raw: str | None = None
        if "positions" in ve:
            raw = _extract_from_positions(model, ve.get("positions") or {})
        elif "pattern" in ve:
            raw = _extract_from_pattern(model, ve.get("pattern") or {})
        if raw is None:
            continue

        value: str | float | int = raw
        mapping = ve.get("mapping")
        if isinstance(mapping, dict):
            key = raw
            if key in mapping:
                value = mapping[key]
            elif key.upper() in mapping:
                value = mapping[key.upper()]

        transform = ve.get("transform")
        if isinstance(transform, dict):
            value = _apply_transform(str(value), transform)

        data_type = (ve.get("data_type") or "").lower()
        if data_type == "number" and isinstance(value, str):
            num = _as_number(value)
            if num is not None:
                value = num

        confidence = "High"
        # If we only extracted a code (no mapping/transform), treat as Medium unless the rule declares a
        # numeric data_type (in that case the substring itself is the final value).
        if not isinstance(mapping, dict) and not isinstance(transform, dict):
            if (ve.get("data_type") or "").lower() != "number":
                confidence = "Medium"

        # Specificity score (higher is better).
        score = 0.0
        if r.model_regex:
            score += 5.0
            score += _regex_specificity_score(r.model_regex)
        if "positions" in ve:
            score += 3.0
        elif "pattern" in ve:
            score += 2.0
            pat = ve.get("pattern") or {}
            if isinstance(pat, dict) and isinstance(pat.get("regex"), str):
                score += _regex_specificity_score(pat["regex"])
        if isinstance(mapping, dict):
            score += 2.0
        if isinstance(transform, dict):
            score += 1.0

        candidates.append(
            AttributeCandidate(
                attribute_name=r.attribute_name,
                value_raw=raw,
                value=value,
                units=r.units or "",
                confidence=confidence,
                evidence=r.evidence_excerpt or "",
                source_url=r.source_url or "",
                rule_equipment_types=list(r.equipment_types or []),
                typed_rule_applied_without_type_context=typed_without_context,
                score=score,
            )
        )

    def conf_rank(c: str) -> int:
        return {"High": 3, "Medium": 2, "Low": 1, "None": 0}.get(c, 0)

    # Prefer typed rules when equipment_type is known and at least one typed rule matches.
    if equipment_type_norm:
        any_typed = any(bool(c.rule_equipment_types) for c in candidates)
        if any_typed:
            candidates = [c for c in candidates if bool(c.rule_equipment_types)]

    return candidates


def decode_attributes(
    brand: str,
    model_raw: str | None,
    rules: list[AttributeRule],
    *,
    equipment_type: str | None = None,
) -> list[DecodedAttribute]:
    candidates = _collect_attribute_candidates(brand, model_raw, rules, equipment_type=equipment_type)

    def conf_rank(c: str) -> int:
        return {"High": 3, "Medium": 2, "Low": 1, "None": 0}.get(c, 0)

    # Pick the best candidate per attribute name. If two equal-score rules yield the same value,
    # keep one (stable) instance.
    best_by_attr: dict[str, tuple[int, int, float, str, DecodedAttribute]] = {}
    for c in candidates:
        key = c.attribute_name
        cur = best_by_attr.get(key)
        decoded = DecodedAttribute(
            attribute_name=c.attribute_name,
            value_raw=c.value_raw,
            value=c.value,
            units=c.units,
            confidence=c.confidence,
            evidence=c.evidence,
            source_url=c.source_url,
            rule_equipment_types=c.rule_equipment_types,
            typed_rule_applied_without_type_context=c.typed_rule_applied_without_type_context,
        )
        cand_tuple = (
            conf_rank(decoded.confidence),
            1 if _is_manual_source(decoded.source_url) else 0,
            float(c.score),
            str(decoded.value),
            decoded,
        )
        if cur is None or cand_tuple[:4] > cur[:4]:
            best_by_attr[key] = cand_tuple

    # Preserve deterministic ordering: by confidence desc, then score desc, then attribute name.
    picked = sorted(best_by_attr.values(), key=lambda t: (-t[0], -t[1], -t[2], t[4].attribute_name))
    return [t[4] for t in picked]


def decode_attributes_with_audit(
    brand: str,
    model_raw: str | None,
    rules: list[AttributeRule],
    *,
    equipment_type: str | None = None,
) -> tuple[list[DecodedAttribute], list[AttributeCandidate], int]:
    """
    Decode attributes and also return candidate details for auditing.

    Returns: (picked_attributes, candidates, conflicts_n)
    where conflicts_n is the count of attributes where 2+ distinct values were eligible.
    """
    candidates = _collect_attribute_candidates(brand, model_raw, rules, equipment_type=equipment_type)
    picked = decode_attributes(brand, model_raw, rules, equipment_type=equipment_type)

    by_attr_values: dict[str, set[str]] = {}
    for c in candidates:
        by_attr_values.setdefault(c.attribute_name, set()).add(str(c.value))
    conflicts_n = sum(1 for _attr, vals in by_attr_values.items() if len(vals) >= 2)
    return picked, candidates, conflicts_n
