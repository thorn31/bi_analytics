#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _json_read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl_write(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for obj in items:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))


def _parse_hp_value(s: str) -> float | None:
    t = _normalize_text(s).upper()
    if not t:
        return None
    # Examples in extracted text:
    # - "1/2"
    # - "3/4"
    # - "7 1/2"
    m = re.fullmatch(r"(\d+)\s+(\d+)/(\d+)", t)
    if m:
        whole = float(m.group(1))
        num = float(m.group(2))
        den = float(m.group(3))
        if den == 0:
            return None
        return whole + (num / den)
    m = re.fullmatch(r"(\d+)/(\d+)", t)
    if m:
        num = float(m.group(1))
        den = float(m.group(2))
        if den == 0:
            return None
        return num / den
    m = re.fullmatch(r"\d+(?:\.\d+)?", t)
    if m:
        return float(t)
    return None


def _extract_york_ahu_fan_option_hp_map(text: str) -> tuple[dict[str, float], str]:
    """
    Parse the "Fan Options" portion of the York AHU nomenclature extract.

    Expected line shape (from pypdf-extracted text):
      "... A NONE. A 0"
      "... B DWDI ... B 1/2"
      "... J ... J 7 1/2"
    """
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    hp_by_code: dict[str, float] = {}
    evidence_lines: list[str] = []

    for ln in lines:
        # Capture: "<code> ... <code> <hp>"
        # Use the final "<code> <hp>" pair to avoid earlier code-like tokens.
        m = re.search(r"\b([A-Z])\s+(\d+(?:\s+\d+/\d+)?|\d+/\d+)\s*$", ln)
        if not m:
            continue
        code = m.group(1).upper()
        hp_raw = m.group(2)
        hp = _parse_hp_value(hp_raw)
        if hp is None:
            continue
        # Keep the first seen mapping per code (stable, deterministic).
        if code not in hp_by_code:
            hp_by_code[code] = hp
            evidence_lines.append(ln)

    # If "A 0" didn't parse (it sometimes appears as "A 0" or "A 0K" in messy extracts),
    # enforce A=0 when explicitly present.
    if "A" not in hp_by_code:
        if re.search(r"\bA\b.*\bA\s+0\b", text):
            hp_by_code["A"] = 0.0
            evidence_lines.insert(0, "A ... A 0")

    # Keep evidence compact.
    evidence = "\n".join(evidence_lines[:25])
    return hp_by_code, evidence


def _pick_examples_from_sdi(
    *,
    sdi_rows: list[dict[str, str]],
    model_regex: re.Pattern,
    code_extractor: re.Pattern,
    valid_codes: set[str],
    max_examples: int = 5,
) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for row in sdi_rows:
        make = (row.get("Make") or "").upper()
        et = (row.get("EquipmentType") or "").strip()
        model = (row.get("ModelNumber") or "").strip().upper()
        if not model or model in seen:
            continue
        if "YORK" not in make and "JOHNSON" not in make and "JCI" not in make:
            continue
        if et.strip().upper() not in {"AIR HANDLING UNIT", "AIR HANDLER", "AIR HANDLING"} and "AIR" not in et.upper():
            continue
        if not model_regex.search(model):
            continue
        m = code_extractor.search(model)
        if not m:
            continue
        code = (m.group(1) or "").upper()
        if code not in valid_codes:
            continue
        seen.add(model)
        out.append(model)
        if len(out) >= max_examples:
            break
    return out


def cmd_specs_mine_york_ahu_attributes(args: argparse.Namespace) -> int:
    snapshot_id = (args.snapshot_id or "").strip()
    if not snapshot_id:
        raise SystemExit("--snapshot-id is required")

    snapshot_dir = Path(args.snapshot_dir) if args.snapshot_dir else (REPO_ROOT / "data" / "external_sources" / "specs_snapshots" / snapshot_id)
    manifest_path = snapshot_dir / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing snapshot manifest: {manifest_path}")

    manifest = _json_read(manifest_path)
    extracted = manifest.get("extracted") or []
    if not isinstance(extracted, list) or not extracted:
        raise SystemExit(f"No extracted files listed in manifest: {manifest_path}")

    # For now, mine from all extracted text files and merge maps (first-win per code).
    merged_hp_by_code: dict[str, float] = {}
    evidence_chunks: list[str] = []
    for e in extracted:
        out_txt = Path(str(e.get("output_txt") or ""))
        if not out_txt.exists():
            continue
        text = out_txt.read_text(encoding="utf-8", errors="replace")
        hp_by_code, ev = _extract_york_ahu_fan_option_hp_map(text)
        for k, v in hp_by_code.items():
            if k not in merged_hp_by_code:
                merged_hp_by_code[k] = v
        if ev:
            evidence_chunks.append(ev)

    if len(merged_hp_by_code) < 3:
        raise SystemExit(
            "Could not parse enough fan option → HP mappings from extracted spec text. "
            "This PDF may be scanned/low-signal; consider OCR or a cleaner source."
        )

    # Format mapping as strings for AttributeDecodeRule Number coercion.
    mapping_str = {k: (str(int(v)) if float(v).is_integer() else str(v)) for k, v in sorted(merged_hp_by_code.items())}

    # Model patterns observed in SDI include:
    # - XTI-063X081-KBLH046A
    # We assume the 4-letter block encodes options; based on SDI correlation (e.g., KBLH -> L == 15HP).
    base_model_regex = r"^XT[IO0]-\d{3}X\d{2,3}-[A-Z]{4}\d{3}[A-Z]$"
    supply_code_pat = r"^XT[IO0]-\d{3}X\d{2,3}-[A-Z]{2}([A-Z])[A-Z]\d{3}[A-Z]$"
    return_code_pat = r"^XT[IO0]-\d{3}X\d{2,3}-[A-Z]{3}([A-Z])\d{3}[A-Z]$"

    # Additional deterministic fields encoded in the XT AHU model string.
    env_pat = r"^XT([IO0])-\d{3}X\d{2,3}-[A-Z]{4}\d{3}[A-Z]$"
    height_pat = r"^XT[IO0]-([0-9]{3})X\d{2,3}-[A-Z]{4}\d{3}[A-Z]$"
    width_pat = r"^XT[IO0]-[0-9]{3}X([0-9]{2,3})-[A-Z]{4}\d{3}[A-Z]$"
    voltage_code_pat = r"^XT[IO0]-\d{3}X\d{2,3}-[A-Z]{4}(\d{3})[A-Z]$"

    # Examples from SDI (best-effort).
    sdi_rows: list[dict[str, str]] = []
    if args.sdi_csv:
        sdi_path = Path(args.sdi_csv)
        if sdi_path.exists():
            sdi_rows = _read_csv_rows(sdi_path)

    examples_supply: list[str] = []
    examples_return: list[str] = []
    if sdi_rows:
        mrx = re.compile(base_model_regex)
        examples_supply = _pick_examples_from_sdi(
            sdi_rows=sdi_rows,
            model_regex=mrx,
            code_extractor=re.compile(supply_code_pat),
            valid_codes=set(mapping_str.keys()),
        )
        examples_return = _pick_examples_from_sdi(
            sdi_rows=sdi_rows,
            model_regex=mrx,
            code_extractor=re.compile(return_code_pat),
            valid_codes=set(mapping_str.keys()),
        )

    retrieved_on = args.retrieved_on or dt.date.today().isoformat()
    source_url = f"spec_sheet_pdf:{snapshot_id}"
    evidence_excerpt = "\n\n".join(evidence_chunks[:2])[:900]

    equipment_types = ["Air Handling Unit"]
    brand = "YORK/JCI"

    candidates: list[dict[str, Any]] = []

    # UnitEnvironment (Indoor/Outdoor) is strongly encoded by the third character: XTI vs XTO.
    candidates.append(
        {
            "rule_type": "decode",
            "brand": brand,
            "attribute_name": "UnitEnvironment",
            "model_regex": r"^XT",
            "equipment_types": equipment_types,
            "units": "",
            "value_extraction": {
                "data_type": "Text",
                "pattern": {"regex": env_pat, "group": 1},
                "mapping": {"I": "Indoor", "O": "Outdoor", "0": "Outdoor"},
            },
            "examples": examples_supply,
            "limitations": "Derived from York AHU nomenclature: XTI=Indoor, XTO=Outdoor (0 treated as O). Spec-backed; not directly validated against SDI truth columns.",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )

    # Nominal dimensions (height/width) are explicit numeric segments in the model number.
    candidates.append(
        {
            "rule_type": "decode",
            "brand": brand,
            "attribute_name": "NominalHeightIn",
            "model_regex": r"^XT",
            "equipment_types": equipment_types,
            "units": "in",
            "value_extraction": {"data_type": "Number", "pattern": {"regex": height_pat, "group": 1}},
            "examples": examples_supply,
            "limitations": "Derived from York AHU nomenclature: nominal height is the 3-digit number after 'XT?-'. Spec-backed; not directly validated against SDI truth columns.",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )
    candidates.append(
        {
            "rule_type": "decode",
            "brand": brand,
            "attribute_name": "NominalWidthIn",
            "model_regex": r"^XT",
            "equipment_types": equipment_types,
            "units": "in",
            "value_extraction": {"data_type": "Number", "pattern": {"regex": width_pat, "group": 1}},
            "examples": examples_supply,
            "limitations": "Derived from York AHU nomenclature: nominal width is the number after 'X' in '###X###'. Spec-backed; not directly validated against SDI truth columns.",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )

    # Primary voltage code (3 digits) is captured as a raw code for later mapping.
    candidates.append(
        {
            "rule_type": "decode",
            "brand": brand,
            "attribute_name": "PrimaryVoltageCode",
            "model_regex": r"^XT",
            "equipment_types": equipment_types,
            "units": "",
            "value_extraction": {"data_type": "Number", "pattern": {"regex": voltage_code_pat, "group": 1}},
            "examples": examples_supply,
            "limitations": "Derived from York AHU nomenclature: 3-digit primary voltage code suffix. This rule extracts the code only; a separate mapping to VoltageVoltPhaseHz is required.",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )

    candidates.append(
        {
            "rule_type": "decode",
            "brand": brand,
            "attribute_name": "SupplyFanHP",
            "model_regex": r"^XT",
            "equipment_types": equipment_types,
            "units": "HP",
            "value_extraction": {
                "data_type": "Number",
                "pattern": {"regex": supply_code_pat, "group": 1},
                "mapping": mapping_str,
            },
            "examples": examples_supply,
            "limitations": "Derived from York AHU model nomenclature (Fan Options). Applies only to XT* AHU models that include the 4-letter options block + 3-digit voltage code suffix.",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )
    candidates.append(
        {
            "rule_type": "decode",
            "brand": brand,
            "attribute_name": "ReturnFanHP",
            "model_regex": r"^XT",
            "equipment_types": equipment_types,
            "units": "HP",
            "value_extraction": {
                "data_type": "Number",
                "pattern": {"regex": return_code_pat, "group": 1},
                "mapping": mapping_str,
            },
            "examples": examples_return,
            "limitations": "Derived from York AHU model nomenclature (Fan Options). Return fan option position is inferred from the 4-letter options block; validate against additional labeled data before broad promotion.",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )

    out_dir = Path(args.out_candidates_dir) if args.out_candidates_dir else (REPO_ROOT / "data" / "rules_discovered" / "spec_sheets" / snapshot_id / "candidates")
    out_path = out_dir / "AttributeDecodeRule.candidates.jsonl"
    _jsonl_write(out_path, candidates)

    print(str(out_dir))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Mine York XT-series AHU fan HP attributes from spec sheet text snapshots.")
    p.add_argument("--snapshot-id", required=True, help="Snapshot id under data/external_sources/specs_snapshots/")
    p.add_argument("--snapshot-dir", default="", help="Optional explicit snapshot dir (overrides --snapshot-id lookup)")
    p.add_argument(
        "--sdi-csv",
        default=str(REPO_ROOT / "data" / "equipment_exports" / "2026-01-25" / "sdi_equipment_normalized.csv"),
        help="Optional SDI CSV for collecting example model numbers",
    )
    p.add_argument("--out-candidates-dir", default="", help="Output dir that will contain AttributeDecodeRule.candidates.jsonl")
    p.add_argument("--retrieved-on", default="", help="YYYY-MM-DD (default: today)")
    args = p.parse_args(argv)
    return cmd_specs_mine_york_ahu_attributes(args)


if __name__ == "__main__":
    raise SystemExit(main())
