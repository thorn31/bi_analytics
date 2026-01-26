from __future__ import annotations

import re


_MULTISPACE_RE = re.compile(r"\s+")
_SEP_RE = re.compile(r"[\s\-_\/]+")


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return _MULTISPACE_RE.sub(" ", value.strip()).upper()


def normalize_serial(value: str | None) -> str:
    t = normalize_text(value)
    # Phase 2 default: remove common separators
    return _SEP_RE.sub("", t)


def normalize_model(value: str | None) -> str:
    # Placeholder for Phase 2: keep separators for now
    return normalize_text(value)


def normalize_brand(value: str | None, alias_map: dict[str, str] | None = None) -> str:
    """
    Normalize a user-supplied manufacturer/make into a canonical brand key.

    `alias_map` is an optional mapping of already-normalized raw make strings to a
    canonical brand key (also normalized). This allows Phase 3 to promote a
    ruleset-local BrandNormalizeRule.csv without hardcoding new aliases.
    """
    t = normalize_text(value)
    if not t:
        return "UNKNOWN"
    if alias_map:
        mapped = alias_map.get(t)
        if mapped:
            t = normalize_text(mapped)
    # Minimal mapping layer (can expand later)
    replacements = {
        "GE": "GENERAL ELECTRIC",
        "GENERAL ELECTRIC": "GENERAL ELECTRIC",
        "JOHNSON CONTROLS": "YORK/JCI",
        "YORK": "YORK/JCI",
        "COLEMAN": "YORK/JCI",
        "LUXAIRE": "YORK/JCI",
        "TRANE": "TRANE",
        "AMERICAN STANDARD": "AMERICAN STANDARD",
        "LENNOX": "LENNOX",
        "CARRIER": "CARRIER/ICP",
        "BRYANT": "CARRIER/ICP",
        "ICP": "CARRIER/ICP",
        "TEMPSTAR": "CARRIER/ICP",
        "HEIL": "CARRIER/ICP",
        "COMFORTMAKER": "CARRIER/ICP",
        "RHEEM": "RHEEM/RUUD",
        "RUUD": "RHEEM/RUUD",
        "GOODMAN": "GOODMAN/AMANA/DAIKIN",
        "AMANA": "GOODMAN/AMANA/DAIKIN",
        "DAIKIN": "GOODMAN/AMANA/DAIKIN",
        "TELEDYNE": "TELEDYNE LAARS",
        "TELEDYNE LAARS": "TELEDYNE LAARS",
        "LAARS": "LAARS",
        "CLIMATE MASTER": "CLIMATE MASTER",
        "AAON": "AAON",
        "MITSUBISHI": "MITSUBISHI",
        "LG": "LG",
    }
    return replacements.get(t, t)
