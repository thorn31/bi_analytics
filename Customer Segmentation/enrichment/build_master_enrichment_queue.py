from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

# Ensure repo-root imports work when executed as `python3 enrichment/...`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from customer_processing import default_paths, write_csv_dicts  # noqa: E402


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_city_state_by_customer_key(path: Path) -> dict[str, tuple[str, str]]:
    if not path.exists():
        return {}
    out: dict[str, tuple[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row.get("CUSTOMER_KEY") or "").strip()
            if not key:
                continue
            city = (row.get("CITY") or "").strip()
            state = (row.get("STATE") or "").strip()
            out[key] = (city, state)
    return out


def _is_generic_industry_detail(value: str) -> bool:
    v = (value or "").strip().lower()
    if not v:
        return True
    generic = {
        "business services",
        "professional services",
        "commercial services",
        "unknown",
        "unclear",
        "your organization (internal)",
        "property/address entity",
        "holding company",
    }
    if v in generic:
        return True
    # Very short details tend to be unhelpful.
    if len(v) < 6:
        return True
    return False


def _needs_naics_enrichment(value: str) -> bool:
    """
    NAICS targeting rule:
    - blank is not acceptable
    - 2-digit is acceptable
    - 4+ digit is the target (acceptable)
    - anything else (e.g., 3-digit) is flagged for enrichment
    """
    v = (value or "").strip()
    if not v:
        return True
    if v in {"31-33", "44-45", "48-49"}:
        # Treat NAICS sector ranges as "2-digit acceptable" (not flagged).
        return False
    digits = "".join(ch for ch in v if ch.isdigit())
    if len(digits) == 0:
        return True
    if len(digits) == 2:
        return False
    if len(digits) >= 4:
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a ranked master enrichment queue (website/NAICS/industry detail)."
    )
    parser.add_argument("--limit", type=int, default=500, help="Max masters to include (default: 500).")
    parser.add_argument(
        "--output",
        default="output/work/enrichment/MasterEnrichmentQueue.csv",
        help="Output CSV path (default: output/work/enrichment/MasterEnrichmentQueue.csv).",
    )
    parser.add_argument(
        "--examples-per-master",
        type=int,
        default=3,
        help="Number of example customer names/locations to include (default: 3).",
    )
    parser.add_argument(
        "--customer-dim-path",
        default="data/sources/CUSTOMERS.D_DB.csv",
        help="Optional customer dimension extract for City/State context (default: data/sources/CUSTOMERS.D_DB.csv).",
    )
    parser.add_argument(
        "--include-complete",
        action="store_true",
        help="Include masters that already have website+NAICS+industry detail (default: false).",
    )
    parser.add_argument(
        "--include-deferred",
        action="store_true",
        help="Include masters marked Deferred in MasterEnrichment.csv (default: false).",
    )
    args = parser.parse_args()

    paths = default_paths()
    master_seg_path = Path(paths["master_segmentation_output"])
    master_map_path = Path(paths["dedupe_output"])
    if not master_seg_path.exists():
        raise SystemExit(f"Missing {master_seg_path}. Run `python3 segment_customers.py` first.")
    if not master_map_path.exists():
        raise SystemExit(f"Missing {master_map_path}. Run `python3 dedupe_customers.py` first.")

    masters = _read_csv(master_seg_path)
    master_rows = _read_csv(master_map_path)
    city_state_by_key = _load_city_state_by_customer_key(Path(args.customer_dim_path))

    # Existing enrichment metadata (attempt counts, deferred status, etc.)
    enrichment_path = Path(paths.get("master_enrichment") or "data/enrichment/MasterEnrichment.csv")
    enrichment_by_canonical: dict[str, dict] = {}
    if enrichment_path.exists():
        for r in _read_csv(enrichment_path):
            canonical = (r.get("Master Customer Name Canonical") or "").strip()
            if not canonical or canonical.startswith("#"):
                continue
            enrichment_by_canonical[canonical] = r

    examples_by_canonical: dict[str, list[str]] = {}
    example_keys_by_canonical: dict[str, list[str]] = {}
    for r in master_rows:
        canonical = (r.get("Master Customer Name Canonical") or "").strip()
        orig = (r.get("Original Name") or "").strip()
        key = (r.get("Customer Key") or "").strip()
        if not canonical:
            continue
        if orig:
            examples_by_canonical.setdefault(canonical, [])
            if orig not in examples_by_canonical[canonical] and len(examples_by_canonical[canonical]) < args.examples_per_master:
                examples_by_canonical[canonical].append(orig)
        if key:
            example_keys_by_canonical.setdefault(canonical, [])
            if key not in example_keys_by_canonical[canonical] and len(example_keys_by_canonical[canonical]) < args.examples_per_master:
                example_keys_by_canonical[canonical].append(key)

    out_rows: list[dict[str, str]] = []
    for m in masters:
        canonical = (m.get("Master Customer Name Canonical") or "").strip()
        if not canonical:
            continue

        website = (m.get("Company Website") or "").strip()
        naics = (m.get("NAICS") or "").strip()
        detail = (m.get("Industry Detail") or "").strip()

        missing_website = not website
        missing_naics = _needs_naics_enrichment(naics)
        missing_detail = _is_generic_industry_detail(detail)
        if not args.include_complete and not (missing_website or missing_naics or missing_detail):
            continue

        targets: list[str] = []
        if missing_website:
            targets.append("Website")
        if missing_naics:
            targets.append("NAICS")
        if missing_detail:
            targets.append("Industry Detail")

        existing_enrichment = enrichment_by_canonical.get(canonical, {})
        existing_status = (existing_enrichment.get("Enrichment Status") or "").strip()
        if existing_status.lower() == "deferred" and not args.include_deferred:
            continue
        attempt_count_raw = (existing_enrichment.get("Attempt Count") or "").strip()
        last_attempted = (existing_enrichment.get("Last Attempted At") or "").strip()
        attempt_outcome = (existing_enrichment.get("Attempt Outcome") or "").strip()

        examples = examples_by_canonical.get(canonical, [])
        example_keys = example_keys_by_canonical.get(canonical, [])
        locations: list[str] = []
        for k in example_keys:
            city, state = city_state_by_key.get(k, ("", ""))
            if not city and not state:
                continue
            loc = ", ".join([x for x in [city, state] if x])
            if loc and loc not in locations:
                locations.append(loc)

        out_rows.append(
            {
                "Master Customer Name": (m.get("Master Customer Name") or "").strip(),
                "Master Customer Name Canonical": canonical,
                "IsMerge": (m.get("IsMerge") or "").strip(),
                "MergeGroupSize": (m.get("MergeGroupSize") or "").strip(),
                "Industrial Group": (m.get("Industrial Group") or "").strip(),
                "Industry Detail (Current)": detail,
                "NAICS (Current)": naics,
                "Company Website (Current)": website,
                "Method": (m.get("Method") or "").strip(),
                "Status": (m.get("Status") or "").strip(),
                "Confidence (Current)": (m.get("Confidence") or "").strip(),
                "Rationale (Current)": (m.get("Rationale") or "").strip(),
                "Enrichment Targets": " | ".join(targets),
                "Attempt Count": attempt_count_raw,
                "Last Attempted At": last_attempted,
                "Attempt Outcome": attempt_outcome,
                "Example Customer Names": " | ".join(examples),
                "Example Locations": " | ".join(locations),
                "Industry Detail (Approved)": "",
                "NAICS (Approved)": "",
                "Company Website (Approved)": "",
                "Enrichment Status": "Verified",
                "Enrichment Confidence": "",
                "Enrichment Rationale": "",
                "Enrichment Source": "Analyst",
                "Attempt Outcome": "",
                "Notes": "",
            }
        )

    def sort_key(r: dict[str, str]) -> tuple[int, int, int, int, int, str]:
        targets = {t.strip() for t in (r.get("Enrichment Targets") or "").split("|") if t.strip()}
        # Priority order requested:
        # 1) Industry Detail
        # 2) NAICS
        # 3) Website
        missing_detail = 1 if "Industry Detail" in targets else 0
        missing_naics = 1 if "NAICS" in targets else 0
        missing_website = 1 if "Website" in targets else 0

        # Most important: if we've already tried to enrich it, push it to the bottom.
        try:
            attempt_count = int((r.get("Attempt Count") or "0").strip() or "0")
        except ValueError:
            attempt_count = 0
        tried_flag = 1 if attempt_count > 0 else 0

        # Use merge impact only as a tie-breaker (lower priority).
        is_merge = 1 if (r.get("IsMerge") or "").strip().upper() == "TRUE" else 0
        try:
            size = int((r.get("MergeGroupSize") or "1").strip() or "1")
        except ValueError:
            size = 1

        name = (r.get("Master Customer Name") or "").strip()
        return (tried_flag, -missing_detail, -missing_naics, -missing_website, -is_merge, -size, name)

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
            "Industry Detail (Current)",
            "NAICS (Current)",
            "Company Website (Current)",
            "Method",
            "Status",
            "Confidence (Current)",
            "Rationale (Current)",
            "Enrichment Targets",
            "Attempt Count",
            "Last Attempted At",
            "Attempt Outcome",
            "Example Customer Names",
            "Example Locations",
            "Industry Detail (Approved)",
            "NAICS (Approved)",
            "Company Website (Approved)",
            "Enrichment Status",
            "Enrichment Confidence",
            "Enrichment Rationale",
            "Enrichment Source",
            "Attempt Outcome",
            "Notes",
        ],
    )
    print(f"Wrote {len(out_rows)} rows to {written}")


if __name__ == "__main__":
    main()
