from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

# Ensure repo-root imports work when executed as `python3 website_enrichment/...`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from customer_processing import default_paths, write_csv_dicts


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a ranked queue of masters missing websites for review/enrichment."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Max masters to include (default: 500).",
    )
    parser.add_argument(
        "--include-with-website",
        action="store_true",
        help="Include masters that already have a website (default: false).",
    )
    parser.add_argument(
        "--output",
        default="output/website_enrichment/WebsiteEnrichmentQueue.csv",
        help="Output CSV path (default: output/website_enrichment/WebsiteEnrichmentQueue.csv).",
    )
    parser.add_argument(
        "--examples-per-master",
        type=int,
        default=3,
        help="Number of example customer names to include per master (default: 3).",
    )
    args = parser.parse_args()

    paths = default_paths()
    master_seg_path = paths["master_segmentation_output"]
    master_map_path = paths["dedupe_output"]

    if not master_seg_path.exists():
        raise SystemExit(f"Missing {master_seg_path}. Run `python3 segment_customers.py` first.")
    if not master_map_path.exists():
        raise SystemExit(f"Missing {master_map_path}. Run `python3 dedupe_customers.py` first.")

    masters = _read_csv(master_seg_path)
    master_rows = _read_csv(master_map_path)

    examples_by_canonical: dict[str, list[str]] = {}
    for r in master_rows:
        canonical = (r.get("Master Customer Name Canonical") or "").strip()
        orig = (r.get("Original Name") or "").strip()
        if not canonical or not orig:
            continue
        examples_by_canonical.setdefault(canonical, [])
        if orig not in examples_by_canonical[canonical] and len(examples_by_canonical[canonical]) < args.examples_per_master:
            examples_by_canonical[canonical].append(orig)

    out_rows: list[dict[str, str]] = []
    for m in masters:
        canonical = (m.get("Master Customer Name Canonical") or "").strip()
        website = (m.get("Company Website") or "").strip()
        if not args.include_with_website and website:
            continue

        examples = examples_by_canonical.get(canonical, [])
        out_rows.append(
            {
                "Master Customer Name": (m.get("Master Customer Name") or "").strip(),
                "Master Customer Name Canonical": canonical,
                "IsMerge": (m.get("IsMerge") or "").strip(),
                "MergeGroupSize": (m.get("MergeGroupSize") or "").strip(),
                "Industrial Group": (m.get("Industrial Group") or "").strip(),
                "Industry Detail": (m.get("Industry Detail") or "").strip(),
                "Method": (m.get("Method") or "").strip(),
                "Status": (m.get("Status") or "").strip(),
                "Company Website": website,
                "Example Customer Names": " | ".join(examples),
                "Approved Website (fill in)": "",
                "Notes (optional)": "",
            }
        )

    def sort_key(r: dict[str, str]) -> tuple[int, int, int, str]:
        # Missing websites first, then masters with merges, then largest merge groups.
        missing = 1 if not (r.get("Company Website") or "").strip() else 0
        is_merge = 1 if (r.get("IsMerge") or "").strip().upper() == "TRUE" else 0
        try:
            size = int((r.get("MergeGroupSize") or "1").strip() or "1")
        except ValueError:
            size = 1
        name = (r.get("Master Customer Name") or "").strip()
        return (-missing, -is_merge, -size, name)

    out_rows.sort(key=sort_key)
    if args.limit >= 0:
        out_rows = out_rows[: args.limit]

    out_path = Path(args.output)
    written = write_csv_dicts(
        out_path,
        out_rows,
        fieldnames=[
            "Master Customer Name",
            "Master Customer Name Canonical",
            "IsMerge",
            "MergeGroupSize",
            "Industrial Group",
            "Industry Detail",
            "Method",
            "Status",
            "Company Website",
            "Example Customer Names",
            "Approved Website (fill in)",
            "Notes (optional)",
        ],
    )
    print(f"Wrote {len(out_rows)} rows to {written}")


if __name__ == "__main__":
    main()
