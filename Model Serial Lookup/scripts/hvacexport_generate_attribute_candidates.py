#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.hvacexport_runlib import create_run_dir
from scripts.hvacexport_runlib import utc_compact_ts


TARGET_ATTRS = {
    "VoltageVoltPhaseHz",
    "Refrigerant",
    "NominalCapacityTons",
    # Staged capacity-related raw codes (not yet aligned to SDI truth fields)
    "HVACExport_CoolingCode",
    "HVACExport_CoolingMinCode",
    "HVACExport_CoolingMaxCode",
    "HVACExport_CoolingHundredsCode",
    "HVACExport_CoolingTonCode",
    "HVACExport_CFMTonsCode",
    "HVACExport_TonsCFMCode",
    "HVACExport_LowTonsCFMCode",
    "HVACExport_HighTonsCFMCode",
    "HVACExport_KWCoolingTonsCode",
}


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _jsonl_write(path: Path, objs: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(o, ensure_ascii=False) for o in objs]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _load_def_map(def_map_csv: Path) -> dict[str, str]:
    if not def_map_csv.exists():
        return {}
    out: dict[str, str] = {}
    with def_map_csv.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            d = (row.get("def_raw") or "").strip()
            a = (row.get("attribute_name") or "").strip()
            if d and a:
                out[d] = a
    return out


def _load_abbrev_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for it in (obj.get("abbreviationType") or []):
        if isinstance(it, dict):
            k = (it.get("key") or "").strip()
            v = (it.get("value") or "").strip()
            if k and v:
                out[k] = v
    return out


def _load_compressed_tables(path: Path) -> dict[str, dict[str, str]]:
    """
    Return mapping: table_name -> key -> value.
    """
    if not path.exists():
        return {}
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, str]] = {}
    for k, v in obj.items():
        if k in {"metaData", "compressType"}:
            continue
        if isinstance(v, list) and v and isinstance(v[0], dict):
            m: dict[str, str] = {}
            for it in v:
                kk = (it.get("key") or "").strip()
                vv = (it.get("value") or "").strip()
                if kk:
                    m[kk] = vv
            out[k] = m
    return out


def _load_typo_pairs(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        return []
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: list[tuple[str, str]] = []
    for it in (obj.get("possibleTypo") or []):
        if isinstance(it, dict):
            k = (it.get("key") or "").strip()
            v = (it.get("value") or "").strip()
            if k and v:
                out.append((k, v))
    return out


_OP_LINE_RE = re.compile(r"^\s*([^\s-]+)\s*-\s*(.+?)\s*$")
_V_CODE_RE = re.compile(r"\b(V\d{1,2})\b", flags=re.IGNORECASE)
_R_CODE_RE = re.compile(r"\b(R\d{1,2})\b", flags=re.IGNORECASE)


def _is_ambiguous_value(s: str) -> bool:
    t = (s or "").strip().lower()
    if not t:
        return True
    if " or " in t:
        return True
    if "revision" in t:
        return True
    return False


def _reduce_with_abbrev(value: str, abbr: dict[str, str]) -> str | None:
    """
    Conservative reduction:
    - If value is exactly an abbreviation key, expand it.
    - If value contains a single V# or R# token and otherwise only digits/separators,
      reduce to that token and expand it.
    - Otherwise, return None.
    """
    v = (value or "").strip()
    if not v or _is_ambiguous_value(v):
        return None

    if v in abbr:
        return abbr[v]

    # Try voltage token extraction.
    m = _V_CODE_RE.search(v)
    if m:
        token = m.group(1).upper()
        # Only accept if string is basically numeric/separators plus the token.
        cleaned = _V_CODE_RE.sub("", v, count=1)
        cleaned = cleaned.strip().replace(" ", "")
        if cleaned and not re.fullmatch(r"[0-9/().+-]*", cleaned):
            return None
        if token in abbr:
            return abbr[token]
        return None

    m = _R_CODE_RE.search(v)
    if m:
        token = m.group(1).upper()
        cleaned = _R_CODE_RE.sub("", v, count=1)
        cleaned = cleaned.strip().replace(" ", "")
        if cleaned and not re.fullmatch(r"[0-9/().+-]*", cleaned):
            return None
        if token in abbr:
            return abbr[token]
        return None

    # If it already looks like a normalized voltage or refrigerant, accept as-is.
    if re.fullmatch(r"\d{2,4}(/\d{2,4})?-\d-\d{2}", v.replace(" ", "")):
        return v.replace(" ", "")
    if re.fullmatch(r"R-?[0-9]{2,4}[A-Z]?", v.upper()):
        up = v.upper().replace("R", "R-", 1) if v.upper().startswith("R") and not v.upper().startswith("R-") else v.upper()
        return up

    return None


def _coerce_number(value: str) -> float | None:
    t = (value or "").strip()
    if not t:
        return None
    # Reject common ambiguity markers for numeric fields.
    if " or " in t.lower():
        return None
    # If this looks like a tonnage string, prefer the numeric immediately tied to "Ton/Tons".
    # This avoids accidentally extracting CFM/BTU values from strings like "800 CFM 2 Ton".
    if re.search(r"\btons?\b", t, flags=re.IGNORECASE):
        # Reject ranges like "1.5 - 2 Tons".
        if re.search(r"\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?\s*tons?\b", t, flags=re.IGNORECASE):
            return None
        ton_nums = re.findall(r"(\d+(?:\.\d+)?)\s*tons?\b", t, flags=re.IGNORECASE)
        if len(ton_nums) != 1:
            return None
        try:
            return float(ton_nums[0])
        except Exception:
            return None
    try:
        return float(t)
    except Exception:
        # Try extracting a single numeric token from strings like "27.5 Tons".
        nums = re.findall(r"\d+(?:\.\d+)?", t)
        if len(nums) != 1:
            return None
        try:
            return float(nums[0])
        except Exception:
            return None


def _coerce_number_from_code(code: str) -> float | None:
    """
    Conservative numeric parsing for direct positional codes (no mapping table).
    """
    t = (code or "").strip()
    if not t:
        return None
    if not re.fullmatch(r"\d+(?:\.\d+)?", t):
        return None
    try:
        return float(t)
    except Exception:
        return None


def _apply_typo_aliases(mapping: dict[str, str], typo_pairs: list[tuple[str, str]]) -> dict[str, str]:
    """
    Conservative: for 1–2 char keys only, apply a single substitution (replace all occurrences)
    and add alias if it doesn't conflict.
    """
    out = dict(mapping)
    for k, v in list(mapping.items()):
        if len(k) > 2:
            continue
        for a, b in typo_pairs:
            if not a or not b:
                continue
            if a not in k:
                continue
            alias = k.replace(a, b)
            if alias == k:
                continue
            if alias not in out:
                out[alias] = v
    return out


def _parse_options_from_snapshot(options_rows: list[dict[str, str]], segment_id: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in options_rows:
        if (row.get("SegmentId") or "").strip() != segment_id:
            continue
        t = (row.get("OPText") or "").strip()
        m = _OP_LINE_RE.match(t)
        if not m:
            continue
        key = m.group(1).strip()
        val = m.group(2).strip()
        if key:
            mapping[key] = val
    return mapping


def _build_length_regex(length_s: str) -> str:
    try:
        length = int(length_s)
    except Exception:
        length = 0
    if length <= 0:
        return ""
    return rf"^[A-Z0-9-]{{{length}}}$"


def _build_prefix_regex(keys: list[str], length_s: str) -> str:
    try:
        length = int(length_s)
    except Exception:
        length = 0
    if length <= 0:
        return ""
    keys = [k for k in keys if k]
    if not keys or len(keys) > 50:
        return ""
    union = "|".join(sorted(re.escape(k) for k in set(keys)))
    # Anchor length check at start so it's not relative to the consumed prefix.
    return rf"^(?=.{{{length}}}$)(?:{union})"


def _build_prefix_minlen_regex(keys: list[str], min_len: int) -> str:
    if min_len <= 0:
        return ""
    keys = [k for k in keys if k]
    if not keys or len(keys) > 50:
        return ""
    union = "|".join(sorted(re.escape(k) for k in set(keys)))
    return rf"^(?=.{{{min_len},}}$)(?:{union})"


@dataclass(frozen=True)
class CandidateKey:
    brand: str
    attribute_name: str
    model_regex: str
    equipment_types_key: str
    start: int
    end: int
    def_raw: str


def generate_candidates(
    *,
    snapshot_dir: Path,
    def_map_csv: Path,
    category_map_csv: Path,
    support_dir: Path,
    include_typo_aliases: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from msl.decoder.normalize import normalize_brand, normalize_model

    records = _read_csv_rows(snapshot_dir / "records.csv")
    segments = _read_csv_rows(snapshot_dir / "segments.csv")
    options = _read_csv_rows(snapshot_dir / "options.csv")

    def_map = _load_def_map(def_map_csv)
    abbr = _load_abbrev_map(support_dir / "abbreviation.json")
    compressed_tables = _load_compressed_tables(support_dir / "compressed.json")
    typo_pairs = _load_typo_pairs(support_dir / "typo.json") if include_typo_aliases else []

    record_meta: dict[str, dict[str, str]] = {}
    for r in records:
        rid = (r.get("RecordId") or "").strip()
        if not rid:
            continue
        record_meta[rid] = r

    # Determine record -> prefix segment keys (segment ordinal 1).
    prefix_keys_by_record: dict[str, list[str]] = {}
    for s in segments:
        if (s.get("SegmentOrdinal") or "").strip() != "1":
            continue
        rid = (s.get("RecordId") or "").strip()
        sid = (s.get("SegmentId") or "").strip()
        if not rid or not sid:
            continue
        # Prefer snapshot options.
        m = _parse_options_from_snapshot(options, sid)
        if not m and s.get("OptionCount") and (s.get("OptionCount") or "").strip() != "0":
            # OptionCount indicates options exist but parse failed; still ignore to stay safe.
            pass
        prefix_keys_by_record[rid] = list(m.keys())

    candidates_by_key: dict[CandidateKey, dict[str, Any]] = {}
    dropped_mapping_keys_n = 0
    merged_mapping_conflicts_n = 0
    built_rules_n = 0

    for s in segments:
        rid = (s.get("RecordId") or "").strip()
        sid = (s.get("SegmentId") or "").strip()
        d = (s.get("DEF") or "").strip()
        if not rid or not sid or not d:
            continue
        # Prefer current def_map over snapshot DEFNormalized so we can iterate mappings without re-parsing snapshots.
        attr = def_map.get(d, "") or (s.get("DEFNormalized") or "").strip()
        if attr not in TARGET_ATTRS:
            continue

        rec = record_meta.get(rid, {})
        brand_raw = (rec.get("BrandRaw") or "").strip()
        brand = normalize_brand(brand_raw)
        category = (rec.get("Category") or "").strip()

        # Equipment type scoping: accepted only.
        equipment_types: list[str] = []
        if (rec.get("CategoryMapStatus") or "").strip().lower() == "accepted":
            try:
                equipment_types = json.loads(rec.get("CategoryEquipmentTypes") or "[]")
                if not isinstance(equipment_types, list):
                    equipment_types = []
                equipment_types = [str(x).strip() for x in equipment_types if str(x).strip()]
            except Exception:
                equipment_types = []

        # Positions
        try:
            start = int((s.get("StartPos") or "").strip())
            end = int((s.get("EndPos") or "").strip())
        except Exception:
            continue
        if start < 1 or end < start:
            continue

        # Map values into the correct data type for the target attribute.
        data_type = "Text"
        units = ""
        if attr == "NominalCapacityTons" or attr.startswith("HVACExport_"):
            data_type = "Number"
            units = "tons" if attr == "NominalCapacityTons" else ""

        # If no mapping table exists and this is a staged numeric code attribute, allow direct extraction
        # (no mapping) as long as the extracted substring is numeric.
        allow_direct_numeric = (data_type == "Number") and attr.startswith("HVACExport_")

        # Mapping source: snapshot options if present, else compressed table by DEF name.
        mapping_raw: dict[str, str] = {}
        if (s.get("OptionCount") or "").strip() not in {"", "0"}:
            mapping_raw = _parse_options_from_snapshot(options, sid)
        if not mapping_raw:
            mapping_raw = dict(compressed_tables.get(d, {}))
        if not mapping_raw and not allow_direct_numeric:
            continue

        mapping_final: dict[str, Any] = {}
        if mapping_raw:
            for k, v in mapping_raw.items():
                kk = str(k).strip()
                vv = str(v).strip()
                if not kk or not vv:
                    continue
                if data_type == "Number":
                    num = _coerce_number(vv)
                    if num is None:
                        dropped_mapping_keys_n += 1
                        continue
                    mapping_final[kk] = num
                else:
                    reduced = _reduce_with_abbrev(vv, abbr)
                    if reduced is None:
                        dropped_mapping_keys_n += 1
                        continue
                    mapping_final[kk] = reduced

        if include_typo_aliases and typo_pairs:
            # Only safe for text mappings.
            if data_type == "Text":
                mapping_final = _apply_typo_aliases(mapping_final, typo_pairs)

        if not mapping_final and not allow_direct_numeric:
            continue

        # Build model_regex: length-based + (optional) prefix gating.
        #
        # For staged direct-numeric code attributes (HVACExport_*), the hvacexport record length is often
        # too strict vs real-world ModelNumber formatting in exports (extra separators, suffixes, etc.).
        # Keep safety by requiring the segment-1 prefix when available and only enforcing a *minimum*
        # length that guarantees positional extraction is possible.
        length_s = (rec.get("Length") or "").strip()
        length_rx = _build_length_regex(length_s)
        prefix_keys = prefix_keys_by_record.get(rid, [])
        prefix_rx = _build_prefix_regex(prefix_keys, length_s)
        if allow_direct_numeric:
            prefix_minlen_rx = _build_prefix_minlen_regex(prefix_keys, end)
            model_regex = prefix_minlen_rx or prefix_rx or length_rx or ""
        else:
            model_regex = prefix_rx or length_rx or ""

        # Construct candidate key and merge.
        equipment_types_key = ",".join(sorted(equipment_types))
        ck = CandidateKey(
            brand=brand,
            attribute_name=attr,
            model_regex=model_regex,
            equipment_types_key=equipment_types_key,
            start=start,
            end=end,
            def_raw=d,
        )

        ve: dict[str, Any] = {"data_type": data_type, "positions": {"start": start, "end": end}}
        if mapping_final:
            ve["mapping"] = mapping_final
        obj = candidates_by_key.get(ck)
        if obj is None:
            obj = {
                "rule_type": "decode",
                "brand": brand,
                "attribute_name": attr,
                "model_regex": model_regex,
                "equipment_types": equipment_types,
                "value_extraction": ve,
                "units": units,
                "examples": [],
                "limitations": (
                    f"Derived from hvacexport snapshot + hvacdecodertool compressed/abbreviation tables. Category={category}. DEF={d}. Ambiguous mappings omitted."
                    if not allow_direct_numeric
                    else f"Direct numeric positional extraction from hvacexport (no mapping table available). Category={category}. DEF={d}. Units/scaling TBD."
                ),
                "evidence_excerpt": f"hvacexport RecordId={rid} DEF={d} pos={start}-{end}",
                "source_url": f"hvacexport:{snapshot_dir.name}",
                "retrieved_on": "",
                "image_urls": [],
            }
            candidates_by_key[ck] = obj
            built_rules_n += 1
        else:
            # Merge mapping: keep only consistent keys (only when mapping exists on both).
            if mapping_final and isinstance(obj.get("value_extraction", {}).get("mapping"), dict):
                existing = obj.get("value_extraction", {}).get("mapping", {})
                if not isinstance(existing, dict):
                    existing = {}
                new_map: dict[str, Any] = dict(existing)
                for mk, mv in mapping_final.items():
                    if mk in new_map and new_map[mk] != mv:
                        merged_mapping_conflicts_n += 1
                        # drop conflicting key
                        new_map.pop(mk, None)
                        continue
                    new_map[mk] = mv
                obj["value_extraction"]["mapping"] = new_map

    out = list(candidates_by_key.values())
    # Stable sort for determinism.
    out.sort(key=lambda o: (o.get("brand", ""), o.get("attribute_name", ""), o.get("model_regex", ""), json.dumps(o.get("equipment_types") or []), o.get("source_url", "")))

    summary = {
        "snapshot_id": snapshot_dir.name,
        "targets": sorted(TARGET_ATTRS),
        "rules_built_n": built_rules_n,
        "rules_out_n": len(out),
        "dropped_mapping_keys_n": dropped_mapping_keys_n,
        "merged_mapping_conflicts_n": merged_mapping_conflicts_n,
    }
    return out, summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hvacexport_generate_attribute_candidates", description="Generate AttributeDecodeRule candidates from hvacexport snapshot")
    ap.add_argument("--snapshot-id", required=True)
    ap.add_argument("--hvacexport-root", default=str(REPO_ROOT / "data" / "external_sources" / "hvacexport"))
    ap.add_argument("--def-map-csv", default=str(REPO_ROOT / "data" / "static" / "hvacexport_def_map.csv"))
    ap.add_argument("--category-map-csv", default=str(REPO_ROOT / "data" / "static" / "hvacexport_category_map.csv"))
    ap.add_argument("--support-dir", default=str(REPO_ROOT / "data" / "static" / "hvacdecodertool"))
    ap.add_argument("--run-id", default="", help="Run folder name under derived/runs/ (default: autogenerated)")
    ap.add_argument("--out-name", default="AttributeDecodeRule.hvacexport.candidates.jsonl", help="Filename within the run folder")
    ap.add_argument("--include-typo-aliases", action="store_true", help="Include conservative typo-derived key aliases (disabled by default)")
    args = ap.parse_args(argv)

    snap_dir = Path(args.hvacexport_root) / str(args.snapshot_id)
    run_id = (args.run_id or "").strip() or f"candidates__{utc_compact_ts()}"
    run_dir = create_run_dir(snap_dir, run_id=run_id)

    objs, summary = generate_candidates(
        snapshot_dir=snap_dir,
        def_map_csv=Path(args.def_map_csv),
        category_map_csv=Path(args.category_map_csv),
        support_dir=Path(args.support_dir),
        include_typo_aliases=bool(args.include_typo_aliases),
    )

    out_path = run_dir / args.out_name
    _jsonl_write(out_path, objs)
    (run_dir / f"{Path(args.out_name).stem}.summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (snap_dir / "derived" / "LATEST_CANDIDATES.txt").write_text(str(out_path.relative_to(snap_dir)), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
