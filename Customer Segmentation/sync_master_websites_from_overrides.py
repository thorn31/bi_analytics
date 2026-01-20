from __future__ import annotations

import argparse
import csv
from pathlib import Path

from customer_processing import default_paths, normalize_company_website


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Populate data/enrichment/MasterWebsites.csv from website values already present in master segmentation overrides."
    )
    parser.add_argument(
        "--overrides-path",
        default="",
        help="Override CSV to read (defaults to the same path segment_customers.py uses).",
    )
    parser.add_argument(
        "--output-path",
        default="",
        help="Master websites CSV to write (defaults to data/enrichment/MasterWebsites.csv).",
    )
    parser.add_argument(
        "--overwrite-existing",
        action="store_true",
        help="Overwrite existing rows in MasterWebsites.csv when a value is present in overrides.",
    )
    args = parser.parse_args()

    paths = default_paths()
    overrides_path = Path(args.overrides_path).resolve() if args.overrides_path else paths["master_segmentation_overrides"]
    out_path = Path(args.output_path).resolve() if args.output_path else paths["master_websites"]

    if not overrides_path.exists():
        raise SystemExit(f"Missing overrides file: {overrides_path}")

    existing: dict[str, str] = {}
    if out_path.exists():
        with out_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                canonical = (row.get("Master Customer Name Canonical") or "").strip()
                website = (row.get("Company Website") or "").strip()
                if not canonical or canonical.startswith("#"):
                    continue
                if website:
                    existing[canonical] = website

    from_overrides: dict[str, str] = {}
    with overrides_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            canonical = (row.get("Master Customer Name Canonical") or "").strip()
            if not canonical or canonical.startswith("#"):
                continue
            website_raw = (row.get("Company Website") or "").strip()
            if not website_raw:
                continue
            domain = normalize_company_website(website_raw)
            if domain:
                from_overrides[canonical] = domain

    updated = 0
    added = 0
    merged = dict(existing)
    for canonical, domain in from_overrides.items():
        if canonical in merged:
            if args.overwrite_existing and merged[canonical] != domain:
                merged[canonical] = domain
                updated += 1
        else:
            merged[canonical] = domain
            added += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=["Master Customer Name Canonical", "Company Website"])
        w.writeheader()
        w.writerow({"Master Customer Name Canonical": "# Example:", "Company Website": ""})
        w.writerow({"Master Customer Name Canonical": "# MORNING POINTE", "Company Website": "morningpointe.com"})
        for canonical in sorted(merged.keys()):
            w.writerow({"Master Customer Name Canonical": canonical, "Company Website": merged[canonical]})

    print(f"Read {len(from_overrides)} website values from {overrides_path}")
    print(f"Wrote {len(merged)} website values to {out_path} (added={added}, updated={updated})")


if __name__ == "__main__":
    main()
