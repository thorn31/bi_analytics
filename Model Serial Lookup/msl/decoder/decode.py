from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass

from msl.decoder.io import SerialRule
from msl.decoder.normalize import normalize_serial


@dataclass(frozen=True)
class SerialDecodeResult:
    matched_style_name: str | None
    manufacture_year_raw: str | None
    manufacture_year: int | None
    manufacture_month_raw: str | None
    manufacture_month: int | None
    manufacture_week_raw: str | None
    manufacture_week: int | None
    ambiguous_decade: bool
    confidence: str  # High|Medium|Low|None
    evidence: str
    source_url: str
    notes: str


def _utc_year() -> int:
    # Avoid importing datetime at module import time for determinism in tests.
    import datetime as dt

    return dt.datetime.now(dt.UTC).year


def _infer_century_for_two_digit_year(two_digit: int, *, now_year: int) -> int:
    """
    Convert YY -> YYYY using a pivot around the current year.

    Rule:
    - If YY <= (current_YY + 1): interpret as 20YY
    - Else: interpret as 19YY

    This keeps future years from appearing while mapping common HVAC serial YY encodings.
    """
    yy_now = now_year % 100
    return (2000 + two_digit) if two_digit <= (yy_now + 1) else (1900 + two_digit)


def _slice_positions(serial: str, spec: dict) -> str | None:
    if spec.get("requires_chart") is True:
        return None
    if "positions" in spec:
        start = int(spec["positions"]["start"])
        end = int(spec["positions"]["end"])
        if start < 1 or end < start or end > len(serial):
            return None
        return serial[start - 1 : end]
    if "positions_list" in spec:
        positions = [int(p) for p in spec["positions_list"]]
        if any(p < 1 or p > len(serial) for p in positions):
            return None
        return "".join(serial[p - 1] for p in positions)
    if "pattern" in spec:
        pat = spec.get("pattern") or {}
        if not isinstance(pat, dict) or "regex" not in pat:
            return None
        try:
            rx = re.compile(pat["regex"])
        except Exception:
            return None
        m = rx.search(serial)
        if not m:
            return None
        group = pat.get("group")
        if group is None:
            return m.group(0)
        try:
            return m.group(int(group))
        except Exception:
            return None
    if "mapping" in spec:
        # Mapping must be applied by extracting a single character/substring via `positions`.
        return None
    return None


def _as_int(value: str | None) -> int | None:
    if value is None:
        return None
    v = value.strip()
    if not v.isdigit():
        return None
    return int(v)


def _apply_mapping(raw_value: str | None, mapping: dict | None) -> int | None:
    if raw_value is None or mapping is None:
        return None
    key = raw_value.strip()
    if not key:
        return None
    # Try exact match first, then uppercase.
    if key in mapping:
        return _as_int(str(mapping[key]))
    key_u = key.upper()
    if key_u in mapping:
        return _as_int(str(mapping[key_u]))
    return None


def _confidence_rank(value: str) -> int:
    return {"High": 3, "Medium": 2, "Low": 1, "None": 0}.get(value, 0)


def _regex_specificity_score(pattern: str) -> float:
    if not pattern:
        return 0.0
    literal_alnum = sum(1 for ch in pattern if ch.isalnum())
    wildcard = pattern.count(".*") + pattern.count(".+") + pattern.count(".?")
    char_classes = pattern.count("[")
    anchors = pattern.count("^") + pattern.count("$")
    return float(literal_alnum) - 2.0 * float(wildcard) - 0.5 * float(char_classes) + 1.0 * float(anchors)


def _style_year_bounds(style_name: str | None) -> tuple[int | None, int | None]:
    """
    Attempt to infer intended min/max year constraints from a human style label.
    This is a safety net for styles labeled with an era but missing explicit transform min/max constraints.
    """
    if not style_name:
        return None, None
    s = style_name.upper()

    # Ranges like "2002-2009" or "2002–2009"
    m = re.search(r"(19\\d{2}|20\\d{2})\\s*[-–]\\s*(19\\d{2}|20\\d{2})", s)
    if m:
        a = int(m.group(1))
        b = int(m.group(2))
        return (min(a, b), max(a, b))

    # "2010+" / "2010 +"
    m = re.search(r"(19\\d{2}|20\\d{2})\\s*\\+", s)
    if m:
        return int(m.group(1)), None

    # "prior to 1973" / "before 1973"
    m = re.search(r"(?:PRIOR TO|BEFORE)\\s*(19\\d{2}|20\\d{2})", s)
    if m:
        # Interpret "prior to YYYY" as <= YYYY-1
        return None, int(m.group(1)) - 1

    # "after 2010" / "since 2010"
    m = re.search(r"(?:AFTER|SINCE)\\s*(19\\d{2}|20\\d{2})", s)
    if m:
        return int(m.group(1)), None

    return None, None


def decode_serial(
    brand: str,
    serial_raw: str | None,
    rules: list[SerialRule],
    *,
    min_plausible_year: int | None = 1980,
) -> SerialDecodeResult:
    serial = normalize_serial(serial_raw)
    if not serial:
        return SerialDecodeResult(None, None, None, None, None, None, None, False, "None", "", "", "empty serial")

    decode_rules = [r for r in rules if r.brand == brand and r.rule_type == "decode"]
    guidance_rules = [r for r in rules if r.brand == brand and r.rule_type == "guidance"]

    best: tuple[tuple, SerialDecodeResult] | None = None

    for idx, r in enumerate(decode_rules):
        try:
            rx = re.compile(r.serial_regex)
        except Exception:
            continue
        if not rx.search(serial):
            continue

        date_fields = r.date_fields or {}
        year_spec = date_fields.get("year", {}) or {}
        month_spec = date_fields.get("month", {}) or {}
        week_spec = date_fields.get("week", {}) or {}

        year_raw = _slice_positions(serial, year_spec)
        month_raw = _slice_positions(serial, month_spec)
        week_raw = _slice_positions(serial, week_spec)

        # Apply per-field transforms when explicitly provided by Phase 1 rules.
        def apply_transform(raw: str | None, spec: dict) -> str | None:
            if raw is None:
                return None
            t = spec.get("transform") or {}
            if not isinstance(t, dict) or "type" not in t:
                return raw
            if t.get("type") == "reverse_string":
                return raw[::-1]
            return raw

        year_raw_t = apply_transform(year_raw, year_spec)
        month_raw_t = apply_transform(month_raw, month_spec)
        week_raw_t = apply_transform(week_raw, week_spec)

        year = _as_int(year_raw_t)
        if year is None:
            year = _apply_mapping(year_raw_t, year_spec.get("mapping"))
        month = _as_int(month_raw_t)
        if month is None:
            month = _apply_mapping(month_raw_t, month_spec.get("mapping"))
        week = _as_int(week_raw_t)
        if week is None:
            week = _apply_mapping(week_raw_t, week_spec.get("mapping"))

        # Year base transforms (e.g., Trane style-specific years) are applied after numeric parse.
        if year is None:
            # Do not accept a match unless we can decode a year.
            continue
        else:
            # If the rule produced a 2-digit year and does not explicitly apply a base, infer the century.
            # Many Building-Center rules encode the year as YY.
            y_transform = (year_spec.get("transform") or {}) if isinstance(year_spec, dict) else {}
            if (
                isinstance(year, int)
                and 0 <= year <= 99
                and isinstance(year_raw_t, str)
                and year_raw_t.isdigit()
                and len(year_raw_t) == 2
                and not (isinstance(y_transform, dict) and y_transform.get("type") == "year_add_base")
            ):
                year = _infer_century_for_two_digit_year(year, now_year=_utc_year())

            t = year_spec.get("transform") or {}
            if isinstance(t, dict) and t.get("type") == "year_add_base":
                try:
                    base = int(t.get("base", 0))
                    year = base + int(year)
                except Exception:
                    pass
            # Respect explicit min/max year constraints if provided.
            if isinstance(t, dict):
                min_year = t.get("min_year")
                max_year = t.get("max_year")
                try:
                    if min_year is not None and year < int(min_year):
                        continue
                    if max_year is not None and year > int(max_year):
                        continue
                except Exception:
                    pass
            # Generic plausibility guard: avoid obviously wrong future years.
            if year > (_utc_year() + 1):
                continue

            # Safety net: honor year bounds inferred from style name text.
            inferred_min, inferred_max = _style_year_bounds(r.style_name)
            if inferred_min is not None and year < inferred_min:
                continue
            if inferred_max is not None and year > inferred_max:
                continue
            # Additional safety: prevent obviously obsolete/false decodes from matching modern equipment.
            # This is conservative: returning NotDecoded is preferable to returning a wrong year.
            if min_plausible_year is not None and year < int(min_plausible_year):
                continue

        ambiguous = bool((r.decade_ambiguity or {}).get("is_ambiguous"))
        # Treat non-4-digit numeric year as ambiguous for Phase 2.
        if year_raw and year_raw.isdigit() and len(year_raw) != 4:
            ambiguous = True
        confidence = "High"
        if ambiguous:
            confidence = "Medium"
        elif month is None and week is None:
            confidence = "Low"

        evidence = r.evidence_excerpt or ""
        res = SerialDecodeResult(
            matched_style_name=r.style_name,
            manufacture_year_raw=year_raw,
            manufacture_year=year,
            manufacture_month_raw=month_raw,
            manufacture_month=month,
            manufacture_week_raw=week_raw,
            manufacture_week=week,
            ambiguous_decade=ambiguous,
            confidence=confidence,
            evidence=evidence,
            source_url=r.source_url,
            notes="",
        )

        score_tuple = (
            _confidence_rank(res.confidence),
            0 if res.ambiguous_decade else 1,
            1 if res.manufacture_month is not None else 0,
            1 if res.manufacture_week is not None else 0,
            _regex_specificity_score(r.serial_regex),
            len(r.serial_regex or ""),
            len(r.style_name or ""),
            -idx,  # Prefer earlier rules when otherwise comparable
        )
        if best is None or score_tuple > best[0]:
            best = (score_tuple, res)

    if best is not None:
        return best[1]

    notes = ""
    if guidance_rules:
        def infer_guidance_match_regex(style_name: str) -> list[re.Pattern]:
            # Very small heuristic: interpret placeholders like "6 ######" into match regexes.
            # Used to avoid showing pattern-specific guidance when the serial clearly doesn't fit.
            if ":" not in style_name:
                return []
            tail = style_name.split(":", 1)[1]
            tail = re.sub(r"\([^)]*\)", " ", tail)
            parts = re.split(r"\s*(?:~or~|-or-|or|\|)\s*", tail, flags=re.IGNORECASE)
            patterns: list[re.Pattern] = []
            for part in parts:
                part = " ".join(part.split())
                if not re.search(r"[#xX]", part):
                    continue
                tokens = re.findall(r"[A-Z0-9]+|[#xX]+", part.upper())
                if not tokens:
                    continue
                regex = "^"
                for tok in tokens:
                    if set(tok) == {"#"}:
                        regex += rf"\\d{{{len(tok)}}}"
                    elif set(tok.lower()) == {"x"}:
                        regex += rf"[A-Z0-9]{{{len(tok)}}}"
                    else:
                        regex += re.escape(tok)
                regex += "$"
                try:
                    patterns.append(re.compile(regex))
                except Exception:
                    continue
            return patterns

        applicable: list[str] = []
        for g in guidance_rules:
            if not g.guidance_text:
                continue
            action = g.guidance_action or ""
            if action == "contact_manufacturer":
                applicable.append(g.guidance_text)
                continue
            if action == "pattern_no_example":
                candidates = infer_guidance_match_regex(g.style_name)
                if candidates and any(rx.search(serial) for rx in candidates):
                    applicable.append(g.guidance_text)
                continue
        notes = " | ".join(applicable[:3])
    return SerialDecodeResult(None, None, None, None, None, None, None, False, "None", "", "", notes)
