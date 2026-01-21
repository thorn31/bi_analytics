#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

import customer_processing as cp


SUFFIX_PRETTY = {
    # Keep this conservative: these are commonly part of the brand display name when "The" is present.
    "COMPANY": "Company",
    "CO": "Co",
    "CO.": "Co",
    "CORP": "Corp",
    "CORP.": "Corp",
    "CORPORATION": "Corporation",
    "INC": "Inc",
    "INC.": "Inc",
}

IGNORE_WORDS = {
    # Avoid government/institution entities where "The" is usually not desired.
    "COUNTY",
    "FISCAL",
    "COURT",
    "CITY",
    "VILLAGE",
    "TOWN",
    "TOWNSHIP",
    "SCHOOL",
    "SCHOOLS",
    "DISTRICT",
    "UNIVERSITY",
    "COLLEGE",
    "BOARD",
    "PUBLIC",
    "MUNICIPAL",
    "STATE",
    "DEPARTMENT",
    "AUTHORITY",
    "CHURCH",
    "POLICE",
    "FIRE",
    "LIBRARY",
    "HOSPITAL",
    "HEALTH",
    "COMMUNITY",
    "FOUNDATION",
    "MINISTRY",
    # Also avoid common multi-tenant/RE noise for display overrides.
    "PROPERTIES",
    "PROPERTY",
    "APARTMENTS",
    "APARTMENT",
    "AT",
    "CROSSING",
}


def _looks_like_gov_or_institution(canonical: str) -> bool:
    toks = set((canonical or "").split())
    return bool(toks & IGNORE_WORDS)


def _extract_suffix_counts(originals_upper: list[str]) -> Counter[str]:
    """
    Count corporate suffix-like tokens in the original names.
    We count presence anywhere in the string (not just trailing), since many
    sources include punctuation like "Company, LLC".
    """
    counts: Counter[str] = Counter()
    for o in originals_upper:
        for raw in SUFFIX_PRETTY.keys():
            token = raw.replace(".", r"\.")
            if re.search(rf"\b{token}\b", o):
                counts[raw] += 1
    return counts


def _suggest_display(
    canonical: str,
    *,
    evidence_originals: list[str],
    the_ratio_threshold: float,
    suffix_ratio_threshold: float,
) -> tuple[str, dict]:
    """
    Suggest a display name based on patterns in Original Name within the canonical group.
    """
    originals_clean = [(o or "").strip() for o in evidence_originals if (o or "").strip()]
    originals_upper = [o.upper().strip() for o in originals_clean]

    base = cp.to_display_name(canonical)
    total = len(originals_upper)

    the_count = sum(1 for o in originals_upper if o.startswith("THE "))
    the_ratio = (the_count / total) if total else 0.0

    # Only use the subset with explicit "The ..." as evidence for suffix.
    suffix_counts = _extract_suffix_counts([o for o in originals_upper if o.startswith("THE ")])
    top_suffix, top_suffix_count = ("", 0)
    if suffix_counts:
        top_suffix, top_suffix_count = suffix_counts.most_common(1)[0]
    suffix_share = (top_suffix_count / the_count) if the_count else 0.0
    suffix_pretty = SUFFIX_PRETTY.get(top_suffix, "")

    # Add "The" when it's materially present in the group, OR when we have at least one
    # explicit "The <brand> <suffix>" evidence row (even if the group contains other variants).
    has_the_with_suffix = bool(suffix_counts) and the_count > 0
    prefix = "The " if (the_ratio >= the_ratio_threshold or has_the_with_suffix) else ""

    # Only add a suffix if that suffix is materially present among the "The ..." evidence rows.
    suffix = ""
    if suffix_pretty and suffix_share >= suffix_ratio_threshold:
        # Avoid doubling suffixes (e.g., "Bristol Group Group").
        if not base.upper().endswith(suffix_pretty.upper()):
            suffix = " " + suffix_pretty

    suggested = f"{prefix}{base}{suffix}".strip()

    meta = {
        "Evidence Rows": str(total),
        "THE Count": str(the_count),
        "THE Ratio": f"{the_ratio:.3f}",
        "Top Suffix": top_suffix,
        "Top Suffix Share": f"{suffix_share:.3f}",
    }
    return suggested, meta


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Suggest master display-name overrides based on Original Name patterns within each canonical group."
    )
    parser.add_argument(
        "--dedupe-map",
        default="",
        help="Path to output/dedupe/CustomerMasterMap.csv (defaults to repo default path).",
    )
    parser.add_argument(
        "--out",
        default="output/work/MasterDisplayNameCandidateOverrides.csv",
        help="Output CSV path (default: output/work/MasterDisplayNameCandidateOverrides.csv).",
    )
    parser.add_argument("--limit", type=int, default=25, help="Max suggestions to output (default: 25).")
    parser.add_argument(
        "--min-the-ratio",
        type=float,
        default=0.35,
        help="Minimum share of originals starting with 'The' to suggest prefix (default: 0.35).",
    )
    parser.add_argument(
        "--min-suffix-ratio",
        type=float,
        default=0.35,
        help="Minimum share of originals containing a suffix token to suggest adding it (default: 0.35).",
    )
    parser.add_argument(
        "--min-evidence-rows",
        type=int,
        default=1,
        help="Minimum number of originals that canonicalize to the master before suggesting an override (default: 1).",
    )
    args = parser.parse_args()

    paths = cp.default_paths()
    dedupe_map_path = Path(args.dedupe_map).expanduser().resolve() if args.dedupe_map else paths["dedupe_output"]
    if not dedupe_map_path.exists():
        raise SystemExit(f"Missing dedupe map: {dedupe_map_path} (run dedupe_customers.py)")

    by_canonical: dict[str, list[str]] = defaultdict(list)
    total_by_canonical: Counter[str] = Counter()

    with dedupe_map_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            canonical = (row.get("Master Customer Name Canonical") or "").strip()
            original = (row.get("Original Name") or "").strip()
            if not canonical or not original:
                continue
            total_by_canonical[canonical] += 1
            # Use left-side canonicalization as evidence, to avoid C/O noise driving branding.
            left, _ = cp.split_co_name(original)
            if cp.get_master_name(left) == canonical:
                by_canonical[canonical].append(original)

    suggestions: list[dict[str, str]] = []
    for canonical, originals in by_canonical.items():
        if _looks_like_gov_or_institution(canonical):
            continue
        if len(originals) < args.min_evidence_rows:
            continue

        base = cp.to_display_name(canonical)
        suggested, meta = _suggest_display(
            canonical,
            evidence_originals=originals,
            the_ratio_threshold=args.min_the_ratio,
            suffix_ratio_threshold=args.min_suffix_ratio,
        )

        # Only include when we'd actually change the display value.
        if not suggested or suggested == base:
            continue

        # Evidence: top few most common originals (within evidence set).
        top_originals = Counter([o.strip() for o in originals if o.strip()]).most_common(3)
        examples = " | ".join([name for name, _ in top_originals])

        # Rank: prioritize by how many rows are affected + strength of signal.
        try:
            the_ratio = float(meta["THE Ratio"])
        except Exception:
            the_ratio = 0.0
        try:
            suffix_share = float(meta["Top Suffix Share"])
        except Exception:
            suffix_share = 0.0
        impact = total_by_canonical.get(canonical, 0)
        score = (impact * 1.0) + (impact * 2.0 * the_ratio) + (impact * 0.25 * suffix_share)

        suggestions.append(
            {
                "Score": f"{score:.2f}",
                "Master Customer Name Canonical": canonical,
                "Base Display (current)": base,
                "Suggested Master Customer Name": suggested,
                "Total Rows": str(impact),
                "Evidence Rows": meta["Evidence Rows"],
                "Examples (top 3)": examples,
                **{k: v for k, v in meta.items() if k != "Evidence Rows"},
            }
        )

    suggestions.sort(key=lambda r: (-float(r["Score"]), -int(r["Total Rows"]), r["Master Customer Name Canonical"]))
    top = suggestions[: max(0, args.limit)]

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "Score",
        "Master Customer Name Canonical",
        "Base Display (current)",
        "Suggested Master Customer Name",
        "Total Rows",
        "Evidence Rows",
        "THE Count",
        "THE Ratio",
        "Top Suffix",
        "Top Suffix Share",
        "Examples (top 3)",
    ]
    cp.write_csv_dicts(out_path, top, fieldnames=fieldnames)
    print(f"Wrote {len(top)} suggestions to {out_path}")


if __name__ == "__main__":
    main()
