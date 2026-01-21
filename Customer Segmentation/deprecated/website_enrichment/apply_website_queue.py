from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import sys

# Ensure repo-root imports work when executed from this archived folder.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from customer_processing import (  # noqa: E402
    default_paths,
    normalize_company_website,
    write_csv_dicts,
)


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="(ARCHIVED) Apply approved websites from output/website_enrichment/WebsiteEnrichmentQueue.csv into data/enrichment/MasterWebsites.csv."
    )
    parser.add_argument(
        "--queue-path",
        default="output/website_enrichment/WebsiteEnrichmentQueue.csv",
        help="Queue CSV path (default: output/website_enrichment/WebsiteEnrichmentQueue.csv).",
    )
    parser.add_argument(
        "--websites-path",
        default="",
        help="Master websites CSV path (defaults to data/enrichment/MasterWebsites.csv).",
    )
    parser.add_argument(
        "--overwrite-existing",
        action="store_true",
        help="Overwrite existing website values when a queue value is present (default: false).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing files.",
    )
    args = parser.parse_args()

    paths = default_paths()
    websites_path = Path(args.websites_path).resolve() if args.websites_path else paths["master_websites"]
    queue_path = Path(args.queue_path).resolve()

    if not queue_path.exists():
        raise SystemExit(f"Missing queue file: {queue_path}")

    queue_rows = _read_csv(queue_path)
    required_cols = {"Master Customer Name Canonical", "Approved Website (fill in)"}
    if not queue_rows:
        raise SystemExit(f"No rows found in queue: {queue_path}")
    if not required_cols.issubset(set(queue_rows[0].keys())):
        raise SystemExit(f"Queue missing required columns {sorted(required_cols)}: {queue_path}")

    # Load existing websites.
    existing_rows: list[dict] = []
    existing: dict[str, str] = {}
    if websites_path.exists():
        existing_rows = _read_csv(websites_path)
        for row in existing_rows:
            canonical = (row.get("Master Customer Name Canonical") or "").strip()
            if not canonical or canonical.startswith("#"):
                continue
            website = normalize_company_website(row.get("Company Website") or "")
            if website:
                existing[canonical] = website

    adds: list[tuple[str, str]] = []
    updates: list[tuple[str, str, str]] = []
    skips: list[str] = []

    for row in queue_rows:
        canonical = (row.get("Master Customer Name Canonical") or "").strip()
        approved_raw = (row.get("Approved Website (fill in)") or "").strip()
        if not canonical or canonical.startswith("#"):
            continue
        if not approved_raw:
            continue
        domain = normalize_company_website(approved_raw)
        if not domain:
            skips.append(canonical)
            continue
        if canonical in existing:
            if existing[canonical] == domain:
                continue
            if args.overwrite_existing:
                updates.append((canonical, existing[canonical], domain))
                existing[canonical] = domain
        else:
            adds.append((canonical, domain))
            existing[canonical] = domain

    if args.dry_run:
        print(f"Queue: {queue_path}")
        print(f"Websites: {websites_path}")
        print(f"Would add: {len(adds)}")
        print(f"Would update: {len(updates)} (overwrite_existing={args.overwrite_existing})")
        print(f"Skipped (unparseable): {len(skips)}")
        for c, d in adds[:20]:
            print(f"ADD {c} => {d}")
        for c, old, new in updates[:20]:
            print(f"UPDATE {c}: {old} -> {new}")
        raise SystemExit(0)

    # Write updated MasterWebsites.csv (preserve comment/example rows if present).
    rows_out: list[dict[str, str]] = []
    if existing_rows:
        for row in existing_rows:
            canonical = (row.get("Master Customer Name Canonical") or "").strip()
            if canonical.startswith("#"):
                rows_out.append(
                    {
                        "Master Customer Name Canonical": canonical,
                        "Company Website": (row.get("Company Website") or "").strip(),
                    }
                )
    else:
        rows_out.append({"Master Customer Name Canonical": "# Example:", "Company Website": ""})
        rows_out.append({"Master Customer Name Canonical": "# MORNING POINTE", "Company Website": "morningpointe.com"})

    for canonical in sorted(existing.keys()):
        rows_out.append({"Master Customer Name Canonical": canonical, "Company Website": existing[canonical]})

    write_csv_dicts(
        websites_path,
        rows_out,
        fieldnames=["Master Customer Name Canonical", "Company Website"],
    )

    # Write a small apply report to output/work for auditability.
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = (paths.get("work_dir") or (Path("output") / "work")) / f"WebsiteQueueApplyReport_{ts}.csv"
    report_rows: list[dict[str, str]] = []
    for c, d in adds:
        report_rows.append({"Action": "Add", "Master Customer Name Canonical": c, "Old": "", "New": d})
    for c, old, new in updates:
        report_rows.append({"Action": "Update", "Master Customer Name Canonical": c, "Old": old, "New": new})
    for c in skips:
        report_rows.append({"Action": "SkipUnparseable", "Master Customer Name Canonical": c, "Old": "", "New": ""})

    write_csv_dicts(
        report_path,
        report_rows,
        fieldnames=["Action", "Master Customer Name Canonical", "Old", "New"],
    )

    print(f"Applied queue to {websites_path} (added={len(adds)}, updated={len(updates)}, skipped={len(skips)})")
    print(f"Wrote apply report to {report_path}")


if __name__ == "__main__":
    main()

