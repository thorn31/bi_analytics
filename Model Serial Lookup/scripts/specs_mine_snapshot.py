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


def _read_manifest(snapshot_dir: Path) -> dict[str, Any]:
    p = snapshot_dir / "manifest.json"
    if not p.exists():
        raise SystemExit(f"Missing manifest: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))


def _jsonl_write(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for obj in items:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _parse_hp_value(s: str) -> float | None:
    t = _normalize_text(s).upper()
    if not t:
        return None
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


def _pick_examples(
    *,
    sdi_rows: list[dict[str, str]],
    make_contains: list[str],
    equipment_type: str,
    model_predicate,
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
        if not any(tok in make for tok in make_contains):
            continue
        if et.strip() != equipment_type:
            continue
        if not model_predicate(model):
            continue
        seen.add(model)
        out.append(model)
        if len(out) >= max_examples:
            break
    return out


def _mine_york_xt_ahu(text: str, *, snapshot_id: str, retrieved_on: str, sdi_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """
    YORK/JCI XT-series Air Handler nomenclature.

    Primary signal in the PDF text snapshot:
    - a Fan Options table where option letters map to motor HP
    - model string structure: XTI-###X###-<4 letters><3 digits><suffix>
    """
    if "XT" not in text.upper():
        return []
    if "NOMENCL" not in text.upper():
        return []
    if "FAN" not in text.upper() or "MOTOR" not in text.upper():
        return []

    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    hp_by_code: dict[str, float] = {}
    evidence_lines: list[str] = []
    for ln in lines:
        m = re.search(r"\b([A-Z])\s+(\d+(?:\s+\d+/\d+)?|\d+/\d+)\s*$", ln)
        if not m:
            continue
        code = m.group(1).upper()
        hp_raw = m.group(2)
        hp = _parse_hp_value(hp_raw)
        if hp is None:
            continue
        if code not in hp_by_code:
            hp_by_code[code] = hp
            evidence_lines.append(ln)

    if len(hp_by_code) < 5:
        return []

    mapping_str = {k: (str(int(v)) if float(v).is_integer() else str(v)) for k, v in sorted(hp_by_code.items())}
    evidence_excerpt = "\n".join(evidence_lines[:25])[:900]
    source_url = f"spec_sheet_pdf:{snapshot_id}"

    equipment_types = ["Air Handling Unit"]
    brand = "YORK/JCI"

    base_model_regex = r"^XT[IO0]-\d{3}X\d{2,3}-[A-Z]{4}\d{3}[A-Z]$"
    env_pat = r"^XT([IO0])-\d{3}X\d{2,3}-[A-Z]{4}\d{3}[A-Z]$"
    height_pat = r"^XT[IO0]-([0-9]{3})X\d{2,3}-[A-Z]{4}\d{3}[A-Z]$"
    width_pat = r"^XT[IO0]-[0-9]{3}X([0-9]{2,3})-[A-Z]{4}\d{3}[A-Z]$"
    voltage_code_pat = r"^XT[IO0]-\d{3}X\d{2,3}-[A-Z]{4}(\d{3})[A-Z]$"
    supply_code_pat = r"^XT[IO0]-\d{3}X\d{2,3}-[A-Z]{2}([A-Z])[A-Z]\d{3}[A-Z]$"
    return_code_pat = r"^XT[IO0]-\d{3}X\d{2,3}-[A-Z]{3}([A-Z])\d{3}[A-Z]$"

    examples = _pick_examples(
        sdi_rows=sdi_rows,
        make_contains=["YORK", "JOHNSON", "JCI"],
        equipment_type="Air Handling Unit",
        model_predicate=lambda m: bool(re.search(base_model_regex, m)),
        max_examples=5,
    )

    out: list[dict[str, Any]] = []
    out.append(
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
            "examples": examples,
            "limitations": "Derived from York AHU nomenclature: XTI=Indoor, XTO=Outdoor (0 treated as O). Spec-backed; not directly validated against SDI truth columns.",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )
    out.append(
        {
            "rule_type": "decode",
            "brand": brand,
            "attribute_name": "NominalHeightIn",
            "model_regex": r"^XT",
            "equipment_types": equipment_types,
            "units": "in",
            "value_extraction": {"data_type": "Number", "pattern": {"regex": height_pat, "group": 1}},
            "examples": examples,
            "limitations": "Derived from York AHU nomenclature: nominal height is the 3-digit number after 'XT?-'. Spec-backed; not directly validated against SDI truth columns.",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )
    out.append(
        {
            "rule_type": "decode",
            "brand": brand,
            "attribute_name": "NominalWidthIn",
            "model_regex": r"^XT",
            "equipment_types": equipment_types,
            "units": "in",
            "value_extraction": {"data_type": "Number", "pattern": {"regex": width_pat, "group": 1}},
            "examples": examples,
            "limitations": "Derived from York AHU nomenclature: nominal width is the number after 'X' in '###X###'. Spec-backed; not directly validated against SDI truth columns.",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )
    out.append(
        {
            "rule_type": "decode",
            "brand": brand,
            "attribute_name": "PrimaryVoltageCode",
            "model_regex": r"^XT",
            "equipment_types": equipment_types,
            "units": "",
            "value_extraction": {"data_type": "Number", "pattern": {"regex": voltage_code_pat, "group": 1}},
            "examples": examples,
            "limitations": "Derived from York AHU nomenclature: 3-digit primary voltage code suffix. This rule extracts the code only; a separate mapping to VoltageVoltPhaseHz is required.",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )
    out.append(
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
            "examples": examples,
            "limitations": "Derived from York AHU model nomenclature (Fan Options). SDI-auditable via Fan (HP) column (treated as supply fan HP).",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )
    out.append(
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
            "examples": examples,
            "limitations": "Derived from York AHU model nomenclature (Fan Options). Spec-backed; not directly validated against SDI truth columns (SDI has no return-fan HP column).",
            "evidence_excerpt": evidence_excerpt,
            "source_url": source_url,
            "retrieved_on": retrieved_on,
        }
    )
    return out


def _mine_york_sunline_2000(text: str, *, snapshot_id: str, retrieved_on: str, sdi_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """
    YORK Sunline 2000 single package heat pumps (B1CH180/240).

    The extracted text contains an explicit PRODUCT NOMENCLATURE section including:
    - voltage code mapping (25/46/58)
    - nominal heating capacity (180/240) mapped to tons
    """
    up = text.upper()
    if "SUNLINE" not in up and "B1CH" not in up:
        return []
    if "PRODUCT NOMENCLA" not in up or "VOLT" not in up or "CODE" not in up:
        return []

    # Parse voltage code table like:
    # 25 = 208/230-3-60
    # 46 = 460-3-60
    # 58 = 575-3-60
    volt_map: dict[str, str] = {}
    for m in re.finditer(r"\b(\d{2})\s*=\s*([0-9/]+)\s*-\s*([13])\s*-\s*(\d{2})\b", up):
        code = m.group(1)
        volts = m.group(2)
        phase = m.group(3)
        hz = m.group(4)
        volt_map[code] = f"{volts}-{phase}-{hz}"

    # Parse capacity mapping like:
    # 180 = 15 Tons
    cap_map: dict[str, str] = {}
    for m in re.finditer(r"\b(\d{3})\s*=\s*(\d+(?:\.\d+)?)\s*TONS?\b", up):
        cap_map[m.group(1)] = m.group(2)

    if not volt_map and not cap_map:
        return []

    evidence_lines: list[str] = []
    for ln in text.splitlines():
        if re.search(r"\bVOLT\s*AGE\s*CODE\b", ln, flags=re.IGNORECASE) or re.search(r"\b=\s*208/230\b", ln):
            evidence_lines.append(ln.strip())
        if re.search(r"\bNOMINAL\s+HEA", ln, flags=re.IGNORECASE) or re.search(r"\b=\s*\d+\s*TON", ln, flags=re.IGNORECASE):
            evidence_lines.append(ln.strip())
    evidence_excerpt = "\n".join([x for x in evidence_lines if x][:25])[:900]
    source_url = f"spec_sheet_pdf:{snapshot_id}"

    brand = "YORK/JCI"
    equipment_types = ["Packaged Unit"]

    examples = _pick_examples(
        sdi_rows=sdi_rows,
        make_contains=["YORK", "JOHNSON", "JCI"],
        equipment_type="Packaged Unit",
        model_predicate=lambda m: m.startswith("B1CH"),
        max_examples=5,
    )

    out: list[dict[str, Any]] = []

    if cap_map:
        out.append(
            {
                "rule_type": "decode",
                "brand": brand,
                "attribute_name": "NominalCapacityTons",
                "model_regex": r"^B1CH",
                "equipment_types": equipment_types,
                "units": "Tons",
                "value_extraction": {
                    "data_type": "Number",
                    "pattern": {"regex": r"^B1CH(\d{3})", "group": 1},
                    "mapping": cap_map,
                },
                "examples": examples,
                "limitations": "Derived from YORK Sunline 2000 PRODUCT NOMENCLATURE section (B1CH### -> tons). SDI-auditable via KnownCapacityTons (preferred) or Cooling Capacity when available.",
                "evidence_excerpt": evidence_excerpt,
                "source_url": source_url,
                "retrieved_on": retrieved_on,
            }
        )

    if volt_map:
        out.append(
            {
                "rule_type": "decode",
                "brand": brand,
                "attribute_name": "VoltageVoltPhaseHz",
                "model_regex": r"^B1CH",
                "equipment_types": equipment_types,
                "units": "Volt-Phase-Hz",
                "value_extraction": {
                    "data_type": "Text",
                    "pattern": {"regex": r"^B1CH\d{3}[A-Z]\d{3}(\d{2})", "group": 1},
                    "mapping": volt_map,
                },
                "examples": examples,
                "limitations": "Derived from YORK Sunline 2000 PRODUCT NOMENCLATURE voltage code table. Note: SDI often records supply voltage as 480V while nomenclature uses 460V nameplate; treat as near-equivalent during review.",
                "evidence_excerpt": evidence_excerpt,
                "source_url": source_url,
                "retrieved_on": retrieved_on,
            }
        )

    return out


def _mine_carrier_38arz_ard(text: str, *, snapshot_id: str, retrieved_on: str, sdi_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """
    Carrier 38ARZ/ARD (commercial air-cooled split condenser) nomenclature.

    This PDF appears to be 50Hz-focused and includes:
    - Nominal capacity code -> tons mapping (e.g., 007 -> 5.0)
    - Voltage code mapping for code '9' -> 400-3-50

    Safety: scope rules to voltage-code 9 only so we don't misapply 50Hz mappings to 60Hz units.
    """
    up = text.upper()
    if "MODEL NUMBER NOMENCLATURE" not in up:
        return []
    if "38ARZ/ARD" not in up and "38AR" not in up:
        return []
    if "NOMINAL CAPACITY" not in up and "NOMINAL" not in up:
        return []

    # Normalize common extraction artifacts:
    # - "7 .0" -> "7.0"
    # - "VOLTAGE008" -> "VOLTAGE 008"
    # - "50 012" sometimes appears as "50012" in the extract
    norm = up.replace("–", "-").replace("—", "-")
    norm = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", norm)
    norm = re.sub(r"VOLTAGE(0\d{2})", r"VOLTAGE \1", norm)
    norm = re.sub(r"50(0\d{2})", r"50 \1", norm)

    # Capacity mapping: lines like "007  - 5.0"
    cap_map: dict[str, str] = {}
    for m in re.finditer(r"\b(0\d{2}|1\d{2}|2\d{2})\s*-\s*([0-9]+(?:\.[0-9]+)?)\b", norm):
        code = m.group(1)
        tons = m.group(2)
        # Only keep plausible 3-digit codes (007..028 shown in the extract).
        if len(code) == 3 and code.isdigit():
            cap_map[code] = tons

    # Voltage mapping for the 50Hz doc: "9 – 400–3–50"
    volt_map: dict[str, str] = {}
    m = re.search(r"\b9\s*-\s*400\s*-\s*3\s*-\s*50(?:\b|(?=0\d{2}))", norm)
    if m:
        volt_map["9"] = "400-3-50"

    if not cap_map and not volt_map:
        return []

    evidence_lines: list[str] = []
    for ln in text.splitlines():
        if re.search(r"MODEL\s+NUMBER\s+NOMENCLATURE", ln, flags=re.IGNORECASE):
            evidence_lines.append(ln.strip())
        if re.search(r"NOMINAL\s+CAPACITY", ln, flags=re.IGNORECASE):
            evidence_lines.append(ln.strip())
        if re.search(r"\b007\b|\b008\b|\b012\b|\b014\b|\b016\b|\b024\b|\b028\b", ln):
            if "-" in ln or "TON" in ln.upper():
                evidence_lines.append(ln.strip())
        if re.search(r"\b9\b", ln) and re.search(r"400", ln):
            evidence_lines.append(ln.strip())
    evidence_excerpt = "\n".join([x for x in evidence_lines if x][:25])[:900]

    source_url = f"spec_sheet_pdf:{snapshot_id}"
    brand = "CARRIER/ICP"
    equipment_types = ["Cooling Condensing Unit"]

    examples = _pick_examples(
        sdi_rows=sdi_rows,
        make_contains=["CARRIER"],
        equipment_type="Cooling Condensing Unit",
        model_predicate=lambda m: m.startswith("38AR"),
        max_examples=5,
    )

    # Observed SDI format (60Hz) looks like: 38ARZ008---501 (capacity ###, fin type --- , then V/D/P digits).
    # For 50Hz mapping, constrain voltage digit to 9: 38AR?###---9??[suffix]
    cap_pat = r"^38AR[ZD](\d{3})---9\d{2}[A-Z]?-*$"
    volt_pat = r"^38AR[ZD]\d{3}---([0-9])\d{2}[A-Z]?-*$"

    out: list[dict[str, Any]] = []

    if cap_map:
        out.append(
            {
                "rule_type": "decode",
                "brand": brand,
                "attribute_name": "NominalCapacityTons",
                "model_regex": r"^38AR",
                "equipment_types": equipment_types,
                "units": "Tons",
                "value_extraction": {
                    "data_type": "Number",
                    "pattern": {"regex": cap_pat, "group": 1},
                    "mapping": cap_map,
                },
                "examples": examples,
                "limitations": "Derived from Carrier 38ARZ/ARD model nomenclature (50Hz document). This rule is intentionally constrained to voltage-code=9 models to avoid misapplying 50Hz capacity mapping to 60Hz units.",
                "evidence_excerpt": evidence_excerpt,
                "source_url": source_url,
                "retrieved_on": retrieved_on,
            }
        )

    # 60Hz SDI variants: user-provided guidance to treat the SDI voltage code used in local exports
    # as 480-3-60 for this family. This is intentionally separated from the 50Hz "code 9" mapping above
    # and scoped to codes 5/6 seen in SDI examples (e.g., ...---501, ...---601).
    volt_map_60hz_forced = {"5": "480-3-60", "6": "480-3-60"}

    if volt_map or volt_map_60hz_forced:
        out.append(
            {
                "rule_type": "decode",
                "brand": brand,
                "attribute_name": "VoltageVoltPhaseHz",
                "model_regex": r"^38AR",
                "equipment_types": equipment_types,
                "units": "Volt-Phase-Hz",
                "value_extraction": {
                    "data_type": "Text",
                    "pattern": {"regex": r"^38AR[ZD]\d{3}---([0-9])\d{2}[A-Z]?-*$", "group": 1},
                    "mapping": {**volt_map, **volt_map_60hz_forced},
                },
                "examples": examples,
                "limitations": "Derived from Carrier 38ARZ/ARD model nomenclature (50Hz) plus user guidance for local SDI exports. Code 9 maps to 400-3-50 (50Hz); codes 5/6 are force-mapped to 480-3-60 for SDI alignment until a 60Hz nomenclature table is available.",
                "evidence_excerpt": evidence_excerpt,
                "source_url": source_url,
                "retrieved_on": retrieved_on,
            }
        )

    return out


def cmd_specs_mine_snapshot(args: argparse.Namespace) -> int:
    snapshot_id = (args.snapshot_id or "").strip()
    if not snapshot_id:
        raise SystemExit("--snapshot-id is required")

    snapshot_dir = Path(args.snapshot_dir) if args.snapshot_dir else (REPO_ROOT / "data" / "external_sources" / "specs_snapshots" / snapshot_id)
    manifest = _read_manifest(snapshot_dir)
    extracted = manifest.get("extracted") or []
    if not isinstance(extracted, list) or not extracted:
        raise SystemExit(f"No extracted files listed in manifest: {snapshot_dir / 'manifest.json'}")

    sdi_rows: list[dict[str, str]] = []
    if args.sdi_csv:
        sdi_path = Path(args.sdi_csv)
        if sdi_path.exists():
            sdi_rows = _read_csv_rows(sdi_path)

    retrieved_on = args.retrieved_on or dt.date.today().isoformat()

    candidates: list[dict[str, Any]] = []
    mined_by_source: dict[str, int] = {}
    for item in extracted:
        out_txt = Path(str(item.get("output_txt") or ""))
        if not out_txt.exists():
            continue
        text = out_txt.read_text(encoding="utf-8", errors="replace")
        before = len(candidates)
        candidates.extend(_mine_york_xt_ahu(text, snapshot_id=snapshot_id, retrieved_on=retrieved_on, sdi_rows=sdi_rows))
        candidates.extend(_mine_york_sunline_2000(text, snapshot_id=snapshot_id, retrieved_on=retrieved_on, sdi_rows=sdi_rows))
        candidates.extend(_mine_carrier_38arz_ard(text, snapshot_id=snapshot_id, retrieved_on=retrieved_on, sdi_rows=sdi_rows))
        mined_by_source[str(out_txt.name)] = len(candidates) - before

    # De-dup exact candidates (stable).
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for c in candidates:
        key = json.dumps(
            {
                "brand": c.get("brand", ""),
                "attribute_name": c.get("attribute_name", ""),
                "model_regex": c.get("model_regex", ""),
                "equipment_types": c.get("equipment_types", []),
                "value_extraction": c.get("value_extraction", {}),
                "source_url": c.get("source_url", ""),
            },
            sort_keys=True,
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)

    out_dir = Path(args.out_candidates_dir) if args.out_candidates_dir else (REPO_ROOT / "data" / "rules_discovered" / "spec_sheets" / snapshot_id / "candidates")
    out_path = out_dir / "AttributeDecodeRule.candidates.jsonl"
    _jsonl_write(out_path, unique)

    meta = {
        "snapshot_id": snapshot_id,
        "snapshot_dir": str(snapshot_dir),
        "retrieved_on": retrieved_on,
        "candidates_n": len(unique),
        "mined_by_source": mined_by_source,
        "out_candidates_dir": str(out_dir),
    }
    (out_dir / "specs_mine_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(str(out_dir))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Mine deterministic AttributeDecodeRule candidates from spec sheet text snapshots.")
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
    return cmd_specs_mine_snapshot(args)


if __name__ == "__main__":
    raise SystemExit(main())
