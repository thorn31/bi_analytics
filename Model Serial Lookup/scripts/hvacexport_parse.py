#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


_KNOWN_RECORD_TAGS = {"Brand", "Category", "SegCount", "length", "Decodes"}
_KNOWN_SEGMENT_TAGS = {"SL", "DEF", "OP"}


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(microsecond=0)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_xml_header_comments(path: Path, *, max_lines: int = 250) -> dict[str, str]:
    """
    Best-effort parse of top-of-file XML comments. This is metadata only; parsing does not depend on it.
    """
    try:
        head = "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[:max_lines])
    except Exception:
        return {"last_update": "", "version": ""}

    last_update = ""
    version = ""

    m = re.search(r"Last Update\s+([^\n<]+)", head, flags=re.IGNORECASE)
    if m:
        last_update = m.group(1).strip()
    m = re.search(r"Version\s+([0-9.]+)", head, flags=re.IGNORECASE)
    if m:
        version = m.group(1).strip()

    return {"last_update": last_update, "version": version}


def _safe_text(el: ET.Element | None) -> str:
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def _extra_fields_json(el: ET.Element, known_tags: set[str]) -> str:
    """
    Capture all unrecognized direct children of `el` into a JSON string.

    Policy: keep content deterministic and small. If an unknown child has nested structure,
    store its XML serialization rather than attempting to interpret it.
    """
    extras: dict[str, Any] = {}
    for child in list(el):
        if child.tag in known_tags:
            continue
        if len(list(child)) > 0:
            # Nested: serialize.
            extras[child.tag] = {"xml": ET.tostring(child, encoding="unicode")}
        else:
            value: dict[str, Any] = {"text": (child.text or "").strip()}
            if child.attrib:
                value["attrib"] = dict(child.attrib)
            extras[child.tag] = value
    return json.dumps(extras, ensure_ascii=False, sort_keys=True)


def _load_category_equipment_type_map(path: Path) -> dict[str, list[str]]:
    """
    CSV contract:
      hvacexport_category,equipment_types_json,confidence,status,reason

    equipment_types_json is a JSON list of canonical equipment type strings.
    """
    if not path.exists():
        return {}
    out: dict[str, list[str]] = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            cat = (row.get("hvacexport_category") or "").strip()
            et_json = (row.get("equipment_types_json") or "").strip()
            if not cat:
                continue
            try:
                parsed = json.loads(et_json or "[]")
                if not isinstance(parsed, list):
                    parsed = []
                parsed = [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                parsed = []
            out[cat] = parsed
    return out


def _load_category_map_meta(path: Path) -> dict[str, dict[str, str]]:
    """
    Same CSV as _load_category_equipment_type_map, but returns metadata fields for audit.
    """
    if not path.exists():
        return {}
    out: dict[str, dict[str, str]] = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            cat = (row.get("hvacexport_category") or "").strip()
            if not cat:
                continue
            out[cat] = {
                "confidence": (row.get("confidence") or "").strip(),
                "status": (row.get("status") or "").strip(),
                "reason": (row.get("reason") or "").strip(),
            }
    return out


def _load_def_normalization_map(path: Path) -> dict[str, str]:
    """
    CSV contract:
      def_raw,attribute_name,units,data_type,notes

    We only consume def_raw -> attribute_name for now.
    """
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            d = (row.get("def_raw") or "").strip()
            a = (row.get("attribute_name") or "").strip()
            if d and a:
                out[d] = a
    return out


def _load_abbreviations_json(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: list[dict[str, str]] = []
    for it in (obj.get("abbreviationType") or []):
        if isinstance(it, dict):
            k = (it.get("key") or "").strip()
            v = (it.get("value") or "").strip()
            if k or v:
                out.append({"key": k, "value": v})
    return out


def _load_compressed_types_json(path: Path) -> list[str]:
    if not path.exists():
        return []
    obj = json.loads(path.read_text(encoding="utf-8"))
    vals = obj.get("compressType") or []
    if not isinstance(vals, list):
        return []
    return [str(x).strip() for x in vals if str(x).strip()]


def _load_possible_typos_json(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: list[dict[str, str]] = []
    for it in (obj.get("possibleTypo") or []):
        if isinstance(it, dict):
            k = (it.get("key") or "").strip()
            v = (it.get("value") or "").strip()
            if k or v:
                out.append({"key": k, "value": v})
    return out


@dataclass(frozen=True)
class ParseStats:
    records_n: int
    segments_n: int
    options_n: int
    empty_optext_n: int
    brands: Counter[str]
    categories: Counter[str]
    defs: Counter[str]
    warnings: list[dict[str, Any]]


def parse_hvacexport_to_snapshot(
    *,
    input_path: Path,
    snapshot_id: str,
    out_root: Path,
    overwrite: bool,
    copy_xml: bool,
    support_dir: Path | None,
    category_map_csv: Path | None,
    def_map_csv: Path | None,
) -> Path:
    from msl.decoder.normalize import normalize_brand

    if not input_path.exists():
        raise SystemExit(f"Missing input XML: {input_path}")
    if not snapshot_id.strip():
        raise SystemExit("--snapshot-id is required")

    snapshot_dir = out_root / snapshot_id
    if snapshot_dir.exists():
        if not overwrite:
            raise SystemExit(f"Snapshot folder already exists: {snapshot_dir} (use --overwrite to replace)")
        shutil.rmtree(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    records_csv = snapshot_dir / "records.csv"
    segments_csv = snapshot_dir / "segments.csv"
    options_csv = snapshot_dir / "options.csv"

    category_map = _load_category_equipment_type_map(category_map_csv) if category_map_csv else {}
    category_meta = _load_category_map_meta(category_map_csv) if category_map_csv else {}
    def_map = _load_def_normalization_map(def_map_csv) if def_map_csv else {}

    compressed_types: set[str] = set()
    if support_dir and support_dir.exists():
        try:
            compressed_types = set(_load_compressed_types_json(support_dir / "compressed.json"))
        except Exception:
            compressed_types = set()

    records_fields = [
        "SnapshotId",
        "RecordId",
        "RecordOrdinal",
        "BrandRaw",
        "BrandNormalized",
        "Category",
        "CategoryEquipmentTypes",
        "CategoryMapConfidence",
        "CategoryMapStatus",
        "CategoryMapReason",
        "Length",
        "SegCountDeclared",
        "SegmentCountObserved",
        "OptionCountObserved",
        "ExtraFieldsJson",
    ]
    segments_fields = [
        "SnapshotId",
        "SegmentId",
        "RecordId",
        "SegmentOrdinal",
        "SL",
        "DEF",
        "DEFNormalized",
        "IsCompressedType",
        "StartPos",
        "EndPos",
        "OptionCount",
        "ExtraFieldsJson",
    ]
    options_fields = [
        "SnapshotId",
        "OptionId",
        "SegmentId",
        "RecordId",
        "SegmentOrdinal",
        "OptionOrdinal",
        "OPText",
    ]

    stats = ParseStats(
        records_n=0,
        segments_n=0,
        options_n=0,
        empty_optext_n=0,
        brands=Counter(),
        categories=Counter(),
        defs=Counter(),
        warnings=[],
    )

    with (
        records_csv.open("w", newline="", encoding="utf-8") as f_rec,
        segments_csv.open("w", newline="", encoding="utf-8") as f_seg,
        options_csv.open("w", newline="", encoding="utf-8") as f_opt,
    ):
        rec_w = csv.DictWriter(f_rec, fieldnames=records_fields)
        seg_w = csv.DictWriter(f_seg, fieldnames=segments_fields)
        opt_w = csv.DictWriter(f_opt, fieldnames=options_fields)
        rec_w.writeheader()
        seg_w.writeheader()
        opt_w.writeheader()

        record_ordinal = 0
        # Stream parse to avoid loading the full DOM (hvacexport can be large).
        context = ET.iterparse(str(input_path), events=("start", "end"))
        _evt0, root = next(context)  # prime and get root

        for evt, el in context:
            if evt != "end":
                continue
            if el.tag != "Record":
                continue

            record_ordinal += 1
            record_id = f"r{record_ordinal:05d}"
            brand_raw = _safe_text(el.find("Brand"))
            brand_norm = normalize_brand(brand_raw)
            category = _safe_text(el.find("Category"))
            segcount_declared = _safe_text(el.find("SegCount"))
            length_raw = _safe_text(el.find("length"))
            # Placeholder or mapped equipment types (JSON list).
            mapped_types = category_map.get(category, [])
            meta_fields = category_meta.get(category, {})

            stats.brands[brand_norm or ""] += 1
            stats.categories[category or ""] += 1

            segs = []
            decodes = el.find("Decodes")
            if decodes is not None:
                segs = decodes.findall("segment")

            seg_count_observed = len(segs)
            option_count_observed = 0

            # If the record defines a total length and segment lengths sum to it, compute start/end positions.
            start_end_by_segment: dict[int, tuple[int, int]] = {}
            try:
                total_len = int(length_raw) if length_raw else None
            except Exception:
                total_len = None
            seg_lens: list[int] = []
            if total_len is not None:
                ok = True
                for seg in segs:
                    try:
                        seg_lens.append(int(_safe_text(seg.find("SL"))))
                    except Exception:
                        ok = False
                        break
                if ok and seg_lens and sum(seg_lens) == total_len:
                    pos = 1
                    for idx, slen in enumerate(seg_lens, start=1):
                        start = pos
                        end = pos + slen - 1
                        start_end_by_segment[idx] = (start, end)
                        pos = end + 1
                elif ok and seg_lens and sum(seg_lens) != total_len:
                    stats.warnings.append(
                        {
                            "type": "segment_length_sum_mismatch",
                            "RecordId": record_id,
                            "BrandNormalized": brand_norm,
                            "Category": category,
                            "Length": total_len,
                            "SegmentLengthsSum": sum(seg_lens),
                        }
                    )

            # Segment rows
            for si, seg in enumerate(segs, start=1):
                segment_id = f"{record_id}_s{si:03d}"
                sl = _safe_text(seg.find("SL"))
                d = _safe_text(seg.find("DEF"))
                d_norm = def_map.get(d, "")
                ops = seg.findall("OP")
                option_count_observed += len(ops)
                stats.defs[d or ""] += 1
                se = start_end_by_segment.get(si)

                seg_w.writerow(
                    {
                        "SnapshotId": snapshot_id,
                        "SegmentId": segment_id,
                        "RecordId": record_id,
                        "SegmentOrdinal": str(si),
                        "SL": sl,
                        "DEF": d,
                        "DEFNormalized": d_norm,
                        "IsCompressedType": "true" if (d in compressed_types) else "false",
                        "StartPos": str(se[0]) if se else "",
                        "EndPos": str(se[1]) if se else "",
                        "OptionCount": str(len(ops)),
                        "ExtraFieldsJson": _extra_fields_json(seg, _KNOWN_SEGMENT_TAGS),
                    }
                )

                # Option rows
                for oi, op in enumerate(ops, start=1):
                    op_text = ((op.text or "").strip()) if op is not None else ""
                    if not op_text:
                        stats.empty_optext_n += 1
                    opt_w.writerow(
                        {
                            "SnapshotId": snapshot_id,
                            "OptionId": f"{segment_id}_o{oi:03d}",
                            "SegmentId": segment_id,
                            "RecordId": record_id,
                            "SegmentOrdinal": str(si),
                            "OptionOrdinal": str(oi),
                            "OPText": op_text,
                        }
                    )

            # Record row
            rec_w.writerow(
                {
                    "SnapshotId": snapshot_id,
                    "RecordId": record_id,
                    "RecordOrdinal": str(record_ordinal),
                    "BrandRaw": brand_raw,
                    "BrandNormalized": brand_norm,
                    "Category": category,
                    "CategoryEquipmentTypes": json.dumps(mapped_types, ensure_ascii=False),
                    "CategoryMapConfidence": meta_fields.get("confidence", ""),
                    "CategoryMapStatus": meta_fields.get("status", ""),
                    "CategoryMapReason": meta_fields.get("reason", ""),
                    "Length": length_raw,
                    "SegCountDeclared": segcount_declared,
                    "SegmentCountObserved": str(seg_count_observed),
                    "OptionCountObserved": str(option_count_observed),
                    "ExtraFieldsJson": _extra_fields_json(el, _KNOWN_RECORD_TAGS),
                }
            )

            # Warning: declared vs observed segment count mismatch
            try:
                decl = int(segcount_declared) if segcount_declared else None
            except Exception:
                decl = None
            if decl is not None and decl != seg_count_observed:
                stats.warnings.append(
                    {
                        "type": "segcount_mismatch",
                        "RecordId": record_id,
                        "BrandNormalized": brand_norm,
                        "Category": category,
                        "SegCountDeclared": decl,
                        "SegmentCountObserved": seg_count_observed,
                    }
                )

            # Update totals
            stats = ParseStats(
                records_n=stats.records_n + 1,
                segments_n=stats.segments_n + seg_count_observed,
                options_n=stats.options_n + option_count_observed,
                empty_optext_n=stats.empty_optext_n,
                brands=stats.brands,
                categories=stats.categories,
                defs=stats.defs,
                warnings=stats.warnings,
            )

            # Free memory.
            el.clear()
            root.clear()

    # Snapshot metadata
    meta = {
        "snapshot_id": snapshot_id,
        "source_path": str(input_path),
        "source_basename": input_path.name,
        "source_size_bytes": input_path.stat().st_size,
        "source_sha256": _sha256_file(input_path),
        "xml_header": _read_xml_header_comments(input_path),
        "parsed_at_utc": _utc_now().isoformat().replace("+00:00", "Z"),
        "counts": {
            "records_n": stats.records_n,
            "segments_n": stats.segments_n,
            "options_n": stats.options_n,
            "unique_brands_n": len([b for b in stats.brands.keys() if b]),
            "unique_categories_n": len([c for c in stats.categories.keys() if c]),
            "unique_defs_n": len([d for d in stats.defs.keys() if d]),
            "empty_optext_n": stats.empty_optext_n,
        },
        "warnings": stats.warnings,
    }
    (snapshot_dir / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Optional: copy original XML into the snapshot for later portability.
    if copy_xml:
        shutil.copy2(input_path, snapshot_dir / "hvacexport.xml")

    # If available, snapshot hvacdecodertool support files (abbreviations/compressed/typos) for later joins.
    if support_dir and support_dir.exists():
        try:
            abbrev = _load_abbreviations_json(support_dir / "abbreviation.json")
            with (snapshot_dir / "abbreviations.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["key", "value"])
                w.writeheader()
                for row in abbrev:
                    w.writerow(row)
        except Exception:
            pass
        try:
            comp = _load_compressed_types_json(support_dir / "compressed.json")
            with (snapshot_dir / "compressed_types.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["def_name"])
                w.writeheader()
                for name in comp:
                    w.writerow({"def_name": name})
        except Exception:
            pass
        try:
            typos = _load_possible_typos_json(support_dir / "typo.json")
            with (snapshot_dir / "possible_typos.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["key", "value"])
                w.writeheader()
                for row in typos:
                    w.writerow(row)
        except Exception:
            pass

    # Summary markdown for quick inspection.
    def _top_lines(counter: Counter[str], n: int) -> list[str]:
        out = []
        for k, v in counter.most_common(n):
            label = k if k else "(empty)"
            out.append(f"- {v:>5}  {label}\n")
        return out

    lines = []
    lines.append(f"# HVACExport Snapshot — {snapshot_id}\n\n")
    lines.append(f"- Source: `{input_path}`\n")
    lines.append(f"- Output: `{snapshot_dir}`\n")
    lines.append(f"- Parsed at (UTC): `{meta['parsed_at_utc']}`\n")
    lines.append("\n## Counts\n")
    for k, v in meta["counts"].items():
        lines.append(f"- {k}: {v}\n")
    lines.append("\n## Top Brands (normalized)\n")
    lines.extend(_top_lines(stats.brands, 20))
    lines.append("\n## Top Categories\n")
    lines.extend(_top_lines(stats.categories, 20))
    lines.append("\n## Top DEF Values\n")
    lines.extend(_top_lines(stats.defs, 30))
    lines.append("\n## Warnings\n")
    lines.append(f"- segcount_mismatch_n: {sum(1 for w in stats.warnings if w.get('type')=='segcount_mismatch')}\n")
    lines.append(f"- segment_length_sum_mismatch_n: {sum(1 for w in stats.warnings if w.get('type')=='segment_length_sum_mismatch')}\n")

    (snapshot_dir / "summary.md").write_text("".join(lines), encoding="utf-8")

    return snapshot_dir


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hvacexport_parse", description="Parse HVACExport XML into a versioned snapshot folder")
    p.add_argument("--input", default=str(REPO_ROOT / "data" / "static" / "hvacexport.xml"), help="Path to hvacexport.xml")
    p.add_argument("--snapshot-id", required=True, help="Snapshot folder name (manual), e.g. 2026-01-24_v3.84")
    p.add_argument(
        "--out-root",
        default=str(REPO_ROOT / "data" / "external_sources" / "hvacexport"),
        help="Root output folder",
    )
    p.add_argument("--overwrite", action="store_true", help="Overwrite snapshot folder if it already exists")
    p.add_argument("--copy-xml", action="store_true", help="Copy input XML into the snapshot folder")
    p.add_argument(
        "--support-dir",
        default=str(REPO_ROOT / "data" / "static" / "hvacdecodertool"),
        help="Optional hvacdecodertool folder (abbreviation/compressed/typo) to snapshot alongside outputs",
    )
    p.add_argument(
        "--category-map-csv",
        default=str(REPO_ROOT / "data" / "static" / "hvacexport_category_map.csv"),
        help="Optional mapping CSV from hvacexport Category -> canonical equipment types (JSON list)",
    )
    p.add_argument(
        "--def-map-csv",
        default=str(REPO_ROOT / "data" / "static" / "hvacexport_def_map.csv"),
        help="Optional mapping CSV from DEF -> normalized attribute name (for staging only)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_path = Path(args.input)
    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    parse_hvacexport_to_snapshot(
        input_path=input_path,
        snapshot_id=str(args.snapshot_id),
        out_root=out_root,
        overwrite=bool(args.overwrite),
        copy_xml=bool(args.copy_xml),
        support_dir=Path(args.support_dir) if getattr(args, "support_dir", "") else None,
        category_map_csv=Path(args.category_map_csv) if getattr(args, "category_map_csv", "") else None,
        def_map_csv=Path(args.def_map_csv) if getattr(args, "def_map_csv", "") else None,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
