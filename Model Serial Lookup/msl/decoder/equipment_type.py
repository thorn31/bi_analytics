from __future__ import annotations

import csv
from pathlib import Path

from msl.decoder.normalize import normalize_text


def load_equipment_type_vocab(path: str | Path) -> dict[str, str]:
    """
    Load canonical equipment type descriptions from `data/static/equipment_types.csv`.

    The file is treated as a vocabulary, not a join table.
    Returns: normalized_description -> canonical_description
    """
    p = Path(path)
    if not p.exists():
        return {}

    out: dict[str, str] = {}
    with p.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        fns = reader.fieldnames or []
        # Expected headers: Asset_MechanicalID, Asset_Description
        desc_col = None
        for cand in ["Asset_Description", "EquipmentType", "Equipment", "Type", "description"]:
            if cand in fns:
                desc_col = cand
                break
        if not desc_col:
            return {}
        for row in reader:
            desc = normalize_text(row.get(desc_col) or "")
            if not desc:
                continue
            out[desc] = row.get(desc_col) or desc
    return out


def canonicalize_equipment_type(raw: str | None, vocab: dict[str, str]) -> tuple[str, str]:
    """
    Canonicalize an equipment type string.

    Policy:
    - Normalize text.
    - If normalized value is in vocab: return the vocab's canonical description.
    - Else: return the normalized value as a "custom/unknown" type.
    """
    raw_norm = normalize_text(raw or "")
    if not raw_norm:
        return "", ""
    return raw_norm, vocab.get(raw_norm, raw_norm)

