from __future__ import annotations

import argparse
import csv
import re
import time
import urllib.parse

from ai_assisted_suggest import duckduckgo_search
from customer_processing import default_paths


BLOCKED_DOMAINS = {
    "facebook.com",
    "linkedin.com",
    "wikipedia.org",
    "crunchbase.com",
    "bloomberg.com",
    "yelp.com",
    "mapquest.com",
    "yellowpages.com",
    "2findlocal.com",
    "opencorporates.com",
    "dnb.com",
    "indeed.com",
    "glassdoor.com",
    "seniorly.com",
    "familyassets.com",
}


def domain_of(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:  # noqa: BLE001
        return ""
    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def pick_official_site(master_name: str, results: list[dict]) -> str:
    # Heuristic: pick the first non-directory domain that looks like the company site.
    name_tokens = [t for t in re.split(r"\W+", master_name.lower()) if t and len(t) > 2]
    for r in results:
        url = r["url"]
        host = domain_of(url)
        if not host:
            continue
        if any(host.endswith(b) for b in BLOCKED_DOMAINS):
            continue
        title = (r["title"] or "").lower()
        if name_tokens and any(tok in host or tok in title for tok in name_tokens[:2]):
            return url
        # still accept as fallback if it isn't an obvious directory
        return url
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest official websites for master customers missing a website.")
    parser.add_argument("--limit", type=int, default=10, help="Number of masters to include (default: 10)")
    parser.add_argument("--sleep-seconds", type=float, default=1.0, help="Delay between web requests (default: 1.0)")
    args = parser.parse_args()

    paths = default_paths()
    master_path = paths["master_segmentation_output"]
    if not master_path.exists():
        raise SystemExit(f"Missing {master_path}. Run `python3 segment_customers.py` first.")

    with master_path.open("r", encoding="utf-8-sig", newline="") as handle:
        masters = list(csv.DictReader(handle))

    # Only those missing website
    candidates = [m for m in masters if not (m.get("Company Website") or "").strip()]
    # prioritize merges first
    def sort_key(m: dict) -> tuple[int, int, str]:
        is_merge = 1 if (m.get("IsMerge") or "").strip().upper() == "TRUE" else 0
        size = int(m.get("MergeGroupSize") or "1")
        return (is_merge, size, (m.get("Master Customer Name") or ""))

    candidates.sort(key=sort_key, reverse=True)
    top = candidates[: max(0, args.limit)]

    out_path = paths["segmentation_output"].parent / "MasterWebsiteSuggestions.csv"
    rows_out: list[dict] = []

    for idx, m in enumerate(top, start=1):
        name = (m.get("Master Customer Name") or "").strip()
        canonical = (m.get("Master Customer Name Canonical") or "").strip()
        query = f"{name} official website"

        results = duckduckgo_search(query, max_results=5)
        result_dicts = [{"title": r.title, "url": r.url, "snippet": r.snippet} for r in results]

        website = pick_official_site(name, result_dicts)

        row = {
            "Rank": str(idx),
            "Master Customer Name": name,
            "Master Customer Name Canonical": canonical,
            "IsMerge": (m.get("IsMerge") or "").strip(),
            "MergeGroupSize": (m.get("MergeGroupSize") or "").strip(),
            "Search Query": query,
            "Suggested Company Website": website,
            "Source 1 Title": result_dicts[0]["title"] if len(result_dicts) > 0 else "",
            "Source 1 URL": result_dicts[0]["url"] if len(result_dicts) > 0 else "",
            "Source 2 Title": result_dicts[1]["title"] if len(result_dicts) > 1 else "",
            "Source 2 URL": result_dicts[1]["url"] if len(result_dicts) > 1 else "",
            "Source 3 Title": result_dicts[2]["title"] if len(result_dicts) > 2 else "",
            "Source 3 URL": result_dicts[2]["url"] if len(result_dicts) > 2 else "",
        }
        rows_out.append(row)
        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

    fieldnames = list(rows_out[0].keys()) if rows_out else [
        "Rank",
        "Master Customer Name",
        "Master Customer Name Canonical",
        "IsMerge",
        "MergeGroupSize",
        "Search Query",
        "Suggested Company Website",
        "Source 1 Title",
        "Source 1 URL",
        "Source 2 Title",
        "Source 2 URL",
        "Source 3 Title",
        "Source 3 URL",
    ]

    try:
        with out_path.open("w", encoding="utf-8", newline="") as handle:
            w = csv.DictWriter(handle, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows_out)
    except PermissionError as exc:
        raise SystemExit(
            f"Permission error writing {out_path}. Close any app using the file (Excel/Power BI), then re-run."
        ) from exc

    print(f"Wrote {len(rows_out)} website suggestions to {out_path}")


if __name__ == "__main__":
    main()
