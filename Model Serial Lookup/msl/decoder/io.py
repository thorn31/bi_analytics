from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SerialRule:
    rule_type: str  # decode|guidance
    brand: str
    style_name: str
    serial_regex: str
    equipment_types: list[str]
    date_fields: dict
    example_serials: list[str]
    decade_ambiguity: dict
    guidance_action: str
    guidance_text: str
    evidence_excerpt: str
    source_url: str
    retrieved_on: str
    image_urls: list[str]


@dataclass(frozen=True)
class AttributeRule:
    rule_type: str  # decode|guidance
    brand: str
    model_regex: str
    attribute_name: str
    equipment_types: list[str]
    value_extraction: dict
    units: str
    examples: list[str]
    limitations: str
    guidance_action: str
    guidance_text: str
    evidence_excerpt: str
    source_url: str
    retrieved_on: str
    image_urls: list[str]


def load_serial_rules_csv(path: str | Path) -> list[SerialRule]:
    from msl.decoder.normalize import normalize_brand

    p = Path(path)
    rules: list[SerialRule] = []
    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            brand = normalize_brand(row.get("brand"))
            try:
                equipment_types = json.loads(row.get("equipment_types") or "[]")
                if not isinstance(equipment_types, list):
                    equipment_types = []
                equipment_types = [str(x).strip() for x in equipment_types if str(x).strip()]
            except Exception:
                equipment_types = []
            rules.append(
                SerialRule(
                    rule_type=(row.get("rule_type") or "decode").strip(),
                    brand=brand,
                    style_name=(row.get("style_name") or "").strip(),
                    serial_regex=(row.get("serial_regex") or "").strip(),
                    equipment_types=equipment_types,
                    date_fields=json.loads(row.get("date_fields") or "{}"),
                    example_serials=json.loads(row.get("example_serials") or "[]"),
                    decade_ambiguity=json.loads(row.get("decade_ambiguity") or "{}"),
                    guidance_action=(row.get("guidance_action") or "").strip(),
                    guidance_text=(row.get("guidance_text") or "").strip(),
                    evidence_excerpt=(row.get("evidence_excerpt") or "").strip(),
                    source_url=(row.get("source_url") or "").strip(),
                    retrieved_on=(row.get("retrieved_on") or "").strip(),
                    image_urls=json.loads(row.get("image_urls") or "[]"),
                )
            )
    return rules


def load_attribute_rules_csv(path: str | Path) -> list[AttributeRule]:
    from msl.decoder.normalize import normalize_brand

    p = Path(path)
    rules: list[AttributeRule] = []
    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            brand = normalize_brand(row.get("brand"))
            try:
                equipment_types = json.loads(row.get("equipment_types") or "[]")
                if not isinstance(equipment_types, list):
                    equipment_types = []
                equipment_types = [str(x).strip() for x in equipment_types if str(x).strip()]
            except Exception:
                equipment_types = []
            rules.append(
                AttributeRule(
                    rule_type=(row.get("rule_type") or "decode").strip(),
                    brand=brand,
                    model_regex=(row.get("model_regex") or "").strip(),
                    attribute_name=(row.get("attribute_name") or "").strip(),
                    equipment_types=equipment_types,
                    value_extraction=json.loads(row.get("value_extraction") or "{}"),
                    units=(row.get("units") or "").strip(),
                    examples=json.loads(row.get("examples") or "[]"),
                    limitations=(row.get("limitations") or "").strip(),
                    guidance_action=(row.get("guidance_action") or "").strip(),
                    guidance_text=(row.get("guidance_text") or "").strip(),
                    evidence_excerpt=(row.get("evidence_excerpt") or "").strip(),
                    source_url=(row.get("source_url") or "").strip(),
                    retrieved_on=(row.get("retrieved_on") or "").strip(),
                    image_urls=json.loads(row.get("image_urls") or "[]"),
                )
            )
    return rules


def load_brand_normalize_rules_csv(path: str | Path) -> dict[str, str]:
    """
    Load BrandNormalizeRule.csv into a mapping of normalized raw-make -> canonical brand.

    Expected columns (flexible):
    - raw_make_normalized OR raw_make
    - canonical_brand OR suggested_brand
    """
    from msl.decoder.normalize import normalize_text

    p = Path(path)
    if not p.exists():
        return {}

    out: dict[str, str] = {}
    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw = normalize_text(row.get("raw_make_normalized") or row.get("raw_make"))
            canonical = normalize_text(row.get("canonical_brand") or row.get("suggested_brand"))
            if raw and canonical:
                out[raw] = canonical
    return out
