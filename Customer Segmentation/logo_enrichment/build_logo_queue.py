#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import customer_processing as cp  # noqa: E402


def load_master_logos(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}

    logos: Dict[str, dict] = {}
    with path.open(mode="r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            canonical = (row.get("Master Customer Name Canonical") or "").strip()
            if not canonical or canonical.startswith("#"):
                continue
            logos[canonical] = {
                "Logo Domain": cp.normalize_company_website(row.get("Logo Domain") or ""),
                "Logo Status": (row.get("Logo Status") or "").strip(),
                "Attempt Count": (row.get("Attempt Count") or "").strip(),
                "Last Attempted At": (row.get("Last Attempted At") or "").strip(),
                "Notes": (row.get("Notes") or "").strip(),
                "Updated At": (row.get("Updated At") or "").strip(),
                "Hosted Logo URL": (row.get("Hosted Logo URL") or "").strip(),
            }
    return logos


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a master logo enrichment queue (Logo.dev).")
    parser.add_argument("--limit", type=int, default=500, help="Max rows to output.")
    parser.add_argument(
        "--input",
        type=str,
        default="",
        help="Optional path to MasterCustomerSegmentation.csv (defaults to output/final/MasterCustomerSegmentation.csv).",
    )
    args = parser.parse_args()

    paths = cp.default_paths()
    master_output = Path(args.input).expanduser() if args.input else paths["master_segmentation_output"]
    if not master_output.exists():
        raise SystemExit(f"Missing master output: {master_output}")

    master_logos_path = cp.repo_root() / "data" / "enrichment" / "MasterLogos.csv"
    master_logos = load_master_logos(master_logos_path)

    rows: List[dict] = []
    with master_output.open(mode="r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            canonical = (row.get("Master Customer Name Canonical") or "").strip()
            if not canonical:
                continue

            website = cp.normalize_company_website(row.get("Company Website") or "")
            if not website:
                continue

            existing = master_logos.get(canonical, {})
            rows.append(
                {
                    "Master Customer Name": (row.get("Master Customer Name") or "").strip(),
                    "Master Customer Name Canonical": canonical,
                    "Company Website": website,
                    "Logo Domain (Approved)": (existing.get("Logo Domain") or "").strip(),
                    "Logo Status": (existing.get("Logo Status") or "").strip(),
                    "Attempt Count": (existing.get("Attempt Count") or "").strip(),
                    "Last Attempted At": (existing.get("Last Attempted At") or "").strip(),
                    "Hosted Logo URL": (existing.get("Hosted Logo URL") or "").strip(),
                    "Notes": (existing.get("Notes") or "").strip(),
                }
            )

    def sort_key(r: dict) -> tuple:
        attempt_count = int((r.get("Attempt Count") or "0").strip() or "0")
        has_status = 1 if (r.get("Logo Status") or "").strip() else 0
        has_hosted = 1 if (r.get("Hosted Logo URL") or "").strip() else 0
        # Prioritize un-attempted, unset status, and missing hosted URL.
        return (has_hosted, has_status, attempt_count, r.get("Master Customer Name Canonical") or "")

    rows = sorted(rows, key=sort_key)[: max(0, args.limit)]

    out_dir = paths["work_dir"] / "logos"
    out_path = out_dir / "LogoQueue.csv"
    fieldnames = [
        "Master Customer Name",
        "Master Customer Name Canonical",
        "Company Website",
        "Logo Domain (Approved)",
        "Logo Status",
        "Attempt Count",
        "Last Attempted At",
        "Hosted Logo URL",
        "Notes",
    ]
    cp.write_csv_dicts(out_path, rows, fieldnames)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
