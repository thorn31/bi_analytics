#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.hvacexport_runlib import create_run_dir
from scripts.hvacexport_runlib import utc_compact_ts


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_current_attribute_names() -> set[str]:
    rules_base = REPO_ROOT / "data" / "rules_normalized"
    cur = (rules_base / "CURRENT.txt").read_text(encoding="utf-8").strip()
    ruleset_dir = rules_base / cur
    p = ruleset_dir / "AttributeDecodeRule.csv"
    if not p.exists():
        return set()
    names: set[str] = set()
    with p.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            n = (row.get("attribute_name") or "").strip()
            if n:
                names.add(n)
    return names


def _load_def_map(path: Path) -> dict[str, str]:
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


@dataclass(frozen=True)
class CatalogKey:
    brand: str
    category: str
    d: str
    d_norm: str
    is_compressed: str


def build_attribute_catalog(*, snapshot_dir: Path, def_map_csv: Path) -> dict[str, Any]:
    segments_csv = snapshot_dir / "segments.csv"
    options_csv = snapshot_dir / "options.csv"
    records_csv = snapshot_dir / "records.csv"

    if not (segments_csv.exists() and options_csv.exists() and records_csv.exists()):
        raise SystemExit(f"Snapshot is missing required files: {snapshot_dir}")

    def_map = _load_def_map(def_map_csv)
    current_attr_names = _load_current_attribute_names()

    seg_rows = _read_csv(segments_csv)
    opt_rows = _read_csv(options_csv)

    # Index options by SegmentId for lightweight aggregation
    opts_by_segment: dict[str, list[str]] = {}
    for row in opt_rows:
        sid = (row.get("SegmentId") or "").strip()
        t = (row.get("OPText") or "").strip()
        if not sid:
            continue
        opts_by_segment.setdefault(sid, []).append(t)

    # Aggregate by (brand, category, DEF)
    buckets: dict[CatalogKey, dict[str, Any]] = {}
    sl_values: dict[CatalogKey, Counter[str]] = {}
    option_values: dict[CatalogKey, Counter[str]] = {}
    pos_coverage: dict[CatalogKey, Counter[str]] = {}

    for row in seg_rows:
        record_id = (row.get("RecordId") or "").strip()
        segment_id = (row.get("SegmentId") or "").strip()
        d = (row.get("DEF") or "").strip()
        d_norm = (row.get("DEFNormalized") or "").strip() or def_map.get(d, "")
        is_comp = (row.get("IsCompressedType") or "").strip() or "false"
        # Pull brand/category from RecordId by joining via records.csv? segments.csv doesn't include it.
        # Our snapshot segments.csv doesn't carry brand/category, so use RecordId -> records.csv lookup.
        # Build this mapping once.
        # NOTE: records.csv is small (1394 rows).
        # We'll lazy-load below.
        if not record_id or not segment_id or not d:
            continue
        buckets.setdefault(
            CatalogKey("", "", d, d_norm, is_comp),
            {},
        )

    rec_rows = _read_csv(records_csv)
    record_meta: dict[str, tuple[str, str]] = {}
    for rr in rec_rows:
        rid = (rr.get("RecordId") or "").strip()
        if not rid:
            continue
        brand = (rr.get("BrandNormalized") or "").strip()
        cat = (rr.get("Category") or "").strip()
        record_meta[rid] = (brand, cat)

    # Now do actual aggregation with brand/category resolved.
    for row in seg_rows:
        record_id = (row.get("RecordId") or "").strip()
        segment_id = (row.get("SegmentId") or "").strip()
        d = (row.get("DEF") or "").strip()
        if not record_id or not segment_id or not d:
            continue
        brand, cat = record_meta.get(record_id, ("", ""))
        d_norm = (row.get("DEFNormalized") or "").strip() or def_map.get(d, "")
        is_comp = (row.get("IsCompressedType") or "").strip() or "false"
        k = CatalogKey(brand, cat, d, d_norm, is_comp)

        b = buckets.get(k)
        if b is None:
            b = {"segments_n": 0, "options_n": 0}
            buckets[k] = b
        b["segments_n"] += 1

        sl = (row.get("SL") or "").strip()
        if sl:
            sl_values.setdefault(k, Counter())[sl] += 1

        start_pos = (row.get("StartPos") or "").strip()
        end_pos = (row.get("EndPos") or "").strip()
        pos_coverage.setdefault(k, Counter())["with_pos" if (start_pos and end_pos) else "no_pos"] += 1

        for op in opts_by_segment.get(segment_id, []):
            if op:
                option_values.setdefault(k, Counter())[op] += 1
                b["options_n"] += 1

    # Build outputs
    out_rows: list[dict[str, str]] = []
    conflicts: list[dict[str, str]] = []

    for k, agg in sorted(
        buckets.items(),
        key=lambda kv: (-int(kv[1].get("segments_n", 0)), kv[0].brand, kv[0].category, kv[0].d),
    ):
        slc = sl_values.get(k, Counter())
        opc = option_values.get(k, Counter())
        pc = pos_coverage.get(k, Counter())
        seg_n = int(agg.get("segments_n", 0))
        opt_n = int(agg.get("options_n", 0))
        with_pos = int(pc.get("with_pos", 0))
        pos_pct = (with_pos / seg_n * 100.0) if seg_n else 0.0

        examples = [s for s, _n in opc.most_common(12)]
        examples_json = json.dumps(examples, ensure_ascii=False)
        top_sls = [s for s, _n in slc.most_common(8)]
        sl_json = json.dumps(top_sls, ensure_ascii=False)

        out_rows.append(
            {
                "BrandNormalized": k.brand,
                "Category": k.category,
                "DEF": k.d,
                "DEFNormalized": k.d_norm,
                "IsCompressedType": k.is_compressed,
                "SegmentsN": str(seg_n),
                "OptionsN": str(opt_n),
                "UniqueOptionsN": str(len(opc)),
                "ExampleOptionsJson": examples_json,
                "ExampleSLJson": sl_json,
                "PositionCoveragePct": f"{pos_pct:.1f}",
                "AlreadyCanonicalAttribute": "true" if (k.d_norm and k.d_norm in current_attr_names) else "false",
            }
        )

        if k.d_norm and k.d_norm in current_attr_names:
            conflicts.append(
                {
                    "BrandNormalized": k.brand,
                    "Category": k.category,
                    "DEF": k.d,
                    "DEFNormalized": k.d_norm,
                    "note": "DEFNormalized collides with an existing AttributeDecodeRule.attribute_name (may be intended; review).",
                }
            )

    return {"rows": out_rows, "conflicts": conflicts, "counts": {"groups_n": len(out_rows)}}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hvacexport_attribute_catalog", description="Build an auditable catalog of hvacexport DEF fields")
    ap.add_argument("--snapshot-id", required=True, help="Snapshot folder name under data/external_sources/hvacexport/")
    ap.add_argument(
        "--hvacexport-root",
        default=str(REPO_ROOT / "data" / "external_sources" / "hvacexport"),
        help="Root folder containing hvacexport snapshots",
    )
    ap.add_argument(
        "--def-map-csv",
        default=str(REPO_ROOT / "data" / "static" / "hvacexport_def_map.csv"),
        help="Optional DEF -> canonical attribute map CSV",
    )
    ap.add_argument("--run-id", default="", help="Run folder name under derived/runs/ (default: autogenerated)")
    args = ap.parse_args(argv)

    snap_dir = Path(args.hvacexport_root) / str(args.snapshot_id)
    run_id = (args.run_id or "").strip() or f"catalog__{utc_compact_ts()}"
    out_dir = create_run_dir(snap_dir, run_id=run_id)

    result = build_attribute_catalog(snapshot_dir=snap_dir, def_map_csv=Path(args.def_map_csv))

    catalog_csv = out_dir / "attribute_catalog.csv"
    fields = [
        "BrandNormalized",
        "Category",
        "DEF",
        "DEFNormalized",
        "IsCompressedType",
        "SegmentsN",
        "OptionsN",
        "UniqueOptionsN",
        "ExampleOptionsJson",
        "ExampleSLJson",
        "PositionCoveragePct",
        "AlreadyCanonicalAttribute",
    ]
    with catalog_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in result["rows"]:
            w.writerow({k: row.get(k, "") for k in fields})

    conflicts_csv = out_dir / "attribute_catalog_conflicts.csv"
    with conflicts_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["BrandNormalized", "Category", "DEF", "DEFNormalized", "note"])
        w.writeheader()
        for row in result["conflicts"]:
            w.writerow(row)

    (out_dir / "attribute_catalog_summary.json").write_text(
        json.dumps({"counts": result["counts"], "conflicts_n": len(result["conflicts"])}, indent=2) + "\n",
        encoding="utf-8",
    )

    (snap_dir / "derived" / "LATEST_CATALOG.txt").write_text(str(catalog_csv.relative_to(snap_dir)), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
