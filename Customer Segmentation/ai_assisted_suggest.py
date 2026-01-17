from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
import html as html_lib
from dataclasses import dataclass
from pathlib import Path

from customer_processing import default_paths


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str


WIKIDATA_UA = "CustomerSegmentationBot/1.0 (local analysis)"


def _fetch(url: str, *, timeout_seconds: int = 20, user_agent: str = "Mozilla/5.0") -> str:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _strip_html(text: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def duckduckgo_search(query: str, *, max_results: int = 5, timeout_seconds: int = 20) -> list[SearchResult]:
    # Uses the public "lite" HTML endpoint (no API key). Keep calls minimal.
    url = "https://lite.duckduckgo.com/lite/?" + urllib.parse.urlencode({"q": query})
    # Some search providers heavily filter non-browser user agents.
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    results: list[SearchResult] = []

    # Typical pattern:
    # <a rel="nofollow" href="/l/?uddg=<ENCODED_URL>&rut=..." class='result-link'>Title</a>
    # <td class='result-snippet'>Snippet...</td>
    link_re = re.compile(
        r"<a(?=[^>]*\bclass=['\"]result-link['\"])(?=[^>]*\bhref=['\"](?P<href>[^'\"]+)['\"])[^>]*>(?P<title>.*?)</a>",
        flags=re.DOTALL | re.IGNORECASE,
    )
    snippet_re = re.compile(r"<td[^>]*\bclass=['\"]result-snippet['\"][^>]*>(?P<snippet>.*?)</td>", flags=re.DOTALL | re.IGNORECASE)

    for m in link_re.finditer(html):
        raw_href = m.group("href")
        title = _strip_html(m.group("title"))
        tail = html[m.end() : m.end() + 1200]
        snippet_match = snippet_re.search(tail)
        snippet = _strip_html(snippet_match.group("snippet")) if snippet_match else ""

        final_url = raw_href
        normalized_href = html_lib.unescape(raw_href)
        if normalized_href.startswith("//"):
            normalized_href = "https:" + normalized_href
        if "/l/?" in normalized_href and "duckduckgo.com" in normalized_href:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(normalized_href).query)
            if "uddg" in qs and qs["uddg"]:
                final_url = urllib.parse.unquote(qs["uddg"][0])

        results.append(SearchResult(title=title, url=final_url, snippet=snippet))
        if len(results) >= max_results:
            break

    return results


def wikidata_lookup(term: str, *, timeout_seconds: int = 20) -> tuple[str, str, str]:
    # Returns (qid, description, official_website)
    search_url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "wbsearchentities",
            "search": term,
            "language": "en",
            "format": "json",
            "limit": 8,
        }
    )
    search_json = json.loads(_fetch(search_url, timeout_seconds=timeout_seconds, user_agent=WIKIDATA_UA))
    hits = search_json.get("search", [])
    if not hits:
        return "", "", ""

    def score(hit: dict) -> int:
        label = (hit.get("label") or "").lower()
        desc = (hit.get("description") or "").lower()
        t = term.lower()
        points = 0
        if label == t:
            points += 10
        if t in label:
            points += 4
        if any(w in desc for w in ["company", "manufacturer", "retailer", "restaurant", "bank", "hospital", "health", "utility"]):
            points += 6
        if any(w in desc for w in ["family name", "given name", "surname", "disambiguation"]):
            points -= 8
        return points

    hits.sort(key=score, reverse=True)
    qid = hits[0].get("id") or ""
    desc = (hits[0].get("description") or "").strip()
    if not qid:
        return "", "", ""

    get_url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "wbgetentities",
            "ids": qid,
            "format": "json",
            "props": "claims|descriptions|labels",
        }
    )
    entity_json = json.loads(_fetch(get_url, timeout_seconds=timeout_seconds, user_agent=WIKIDATA_UA))
    ent = (entity_json.get("entities") or {}).get(qid) or {}
    claims = ent.get("claims") or {}
    official = ""
    if "P856" in claims and claims["P856"]:
        try:
            official = claims["P856"][0]["mainsnak"]["datavalue"]["value"]
        except Exception:  # noqa: BLE001
            official = ""
    return qid, desc, official


def suggest_classification_from_text(text: str) -> tuple[str, str, str]:
    t = text.lower()
    rules: list[tuple[str, list[str], str]] = [
        ("Municipal / Local Government", ["fiscal court", "county", "city of", "municipal", "police", "fire department"], "Government entity"),
        ("University / College", ["university", "college", "community college"], "Higher education"),
        ("Public Schools (K–12)", ["school district", "public schools", "board of education"], "K–12 public education"),
        ("Private Schools (K–12)", ["academy", "prep school", "catholic school", "christian school"], "K–12 private education"),
        ("Healthcare / Senior Living", ["hospital", "medical", "clinic", "assisted living", "senior living"], "Healthcare / senior living"),
        ("Utilities", ["water", "sewer", "wastewater", "electric", "utility", "power company"], "Utility services"),
        ("Financial Services", ["bank", "credit union", "mortgage", "lending", "insurance"], "Financial services"),
        ("Construction", ["construction", "contractor", "builders", "roofing", "plumbing"], "Construction/contracting"),
        ("Manufacturing", ["manufacturing", "manufacturer", "factory", "plant", "packaging"], "Manufacturing"),
        ("Commercial Services", ["hvac", "heating", "cooling", "air conditioning", "ventilation", "mechanical contractor"], "HVAC / building systems"),
        ("Commercial Real Estate", ["real estate", "property management", "apartments", "leasing", "commercial property"], "Commercial real estate"),
        # Retail/Hospitality are treated as support categorizations (secondary), not primary Industrial Group.
        ("Commercial Services", ["hotel", "inn", "resort", "motel", "lodge"], "Hospitality"),
        ("Commercial Services", ["restaurant", "grill", "cafe", "coffee"], "Hospitality"),
        ("Commercial Services", ["retail", "grocery", "supermarket", "pharmacy"], "Retail"),
        ("Commercial Services", ["fitness", "gym"], "Fitness"),
        ("Commercial Services", ["staffing", "consulting", "logistics", "engineering services", "facility services"], "Commercial services"),
        ("Non-Profit / Religious", ["church", "diocese", "ministry", "nonprofit", "foundation"], "Non-profit/religious"),
    ]
    for group, keywords, detail in rules:
        if any(k in t for k in keywords):
            support_category = ""
            if detail == "Hospitality":
                support_category = "Hospitality"
            elif detail in {"Retail", "Fitness"}:
                support_category = "Retail"
            return group, detail, support_category
    return "Unknown / Needs Review", "", ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AI-assisted segmentation suggestions for unclassified masters.")
    parser.add_argument("--limit", type=int, default=10, help="Number of masters to include (default: 10)")
    parser.add_argument("--sleep-seconds", type=float, default=1.0, help="Delay between web requests (default: 1.0)")
    args = parser.parse_args()

    paths = default_paths()
    master_seg_path = paths["master_segmentation_output"]
    if not master_seg_path.exists():
        raise SystemExit(f"Missing {master_seg_path}. Run `python3 segment_customers.py` first.")

    master_map_path = paths["dedupe_output"]
    examples_by_canonical: dict[str, list[str]] = {}
    if master_map_path.exists():
        with master_map_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                canonical = (row.get("Master Customer Name Canonical") or "").strip()
                orig = (row.get("Original Name") or "").strip()
                if not canonical or not orig:
                    continue
                examples_by_canonical.setdefault(canonical, [])
                if orig not in examples_by_canonical[canonical] and len(examples_by_canonical[canonical]) < 3:
                    examples_by_canonical[canonical].append(orig)

    with master_seg_path.open("r", encoding="utf-8-sig", newline="") as handle:
        masters = list(csv.DictReader(handle))

    unclassified = [m for m in masters if (m.get("Method") or "").strip() == "Unclassified"]
    # prioritize merges first, then group size, then name
    def key(m: dict) -> tuple[int, int, str]:
        is_merge = 1 if (m.get("IsMerge") or "").strip().upper() == "TRUE" else 0
        size = int(m.get("MergeGroupSize") or "1")
        return (is_merge, size, (m.get("Master Customer Name") or ""))

    unclassified.sort(key=key, reverse=True)
    top = unclassified[: max(0, args.limit)]

    out_path = paths["segmentation_output"].parent / "AI_Assisted_Suggestions.csv"
    rows_out: list[dict] = []

    for idx, m in enumerate(top, start=1):
        name = (m.get("Master Customer Name") or "").strip()
        canonical = (m.get("Master Customer Name Canonical") or "").strip()
        examples = examples_by_canonical.get(canonical, [])
        # Add light context to improve disambiguation (especially for acronyms).
        if len(name) <= 5 or name.isupper():
            query = f"{name} company"
        elif examples:
            query = f"{name} {examples[0]}"
        else:
            query = f"{name} company"

        results: list[SearchResult] = []
        error = ""
        suggested_website = ""
        wikidata_qid = ""
        wikidata_desc = ""

        # Prefer DuckDuckGo when available (richer snippets), but fall back to Wikidata
        # when search is blocked/throttled.
        try:
            results = duckduckgo_search(query, max_results=5)
        except Exception as exc:  # noqa: BLE001
            error = str(exc)

        if not results:
            try:
                wikidata_qid, wikidata_desc, suggested_website = wikidata_lookup(name)
            except Exception as exc:  # noqa: BLE001
                if error:
                    error = f"{error}; {exc}"
                else:
                    error = str(exc)

        combined_text = " ".join(
            [name, wikidata_desc]
            + [r.title + " " + r.snippet for r in results]
        )
        suggested_group, suggested_detail, suggested_support = suggest_classification_from_text(combined_text)
        has_sources = bool(results) or bool(wikidata_qid)
        suggested_method = "AI-Assisted Search" if (has_sources and suggested_group != "Unknown / Needs Review") else "Unclassified"
        suggested_confidence = "Medium" if suggested_method == "AI-Assisted Search" else "Low"

        row: dict[str, str] = {
            "Rank": str(idx),
            "Master Customer Name": name,
            "Master Customer Name Canonical": canonical,
            "IsMerge": (m.get("IsMerge") or "").strip(),
            "MergeGroupSize": (m.get("MergeGroupSize") or "").strip(),
            "Search Query": query,
            "Suggested Industrial Group": suggested_group,
            "Suggested Industry Detail": suggested_detail,
            "Suggested Support Category": suggested_support,
            "Suggested NAICS": "",
            "Suggested Method": suggested_method,
            "Suggested Confidence": suggested_confidence,
            "Suggested Company Website": suggested_website,
            "Example Original Names": " | ".join(examples),
            "Notes": error,
        }

        for i in range(1, 4):
            if i <= len(results):
                row[f"Source {i} Title"] = results[i - 1].title
                row[f"Source {i} URL"] = results[i - 1].url
            else:
                row[f"Source {i} Title"] = ""
                row[f"Source {i} URL"] = ""

        if not row["Source 1 URL"] and wikidata_qid:
            row["Source 1 Title"] = f"Wikidata: {name}"
            row["Source 1 URL"] = f"https://www.wikidata.org/wiki/{wikidata_qid}"
        if not row["Source 2 URL"] and suggested_website:
            row["Source 2 Title"] = "Official website"
            row["Source 2 URL"] = suggested_website

        rows_out.append(row)
        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

    fieldnames = [
        "Rank",
        "Master Customer Name",
        "Master Customer Name Canonical",
        "IsMerge",
        "MergeGroupSize",
        "Search Query",
        "Suggested Industrial Group",
        "Suggested Industry Detail",
        "Suggested Support Category",
        "Suggested NAICS",
        "Suggested Method",
        "Suggested Confidence",
        "Suggested Company Website",
        "Example Original Names",
        "Source 1 Title",
        "Source 1 URL",
        "Source 2 Title",
        "Source 2 URL",
        "Source 3 Title",
        "Source 3 URL",
        "Notes",
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with out_path.open("w", encoding="utf-8", newline="") as handle:
            w = csv.DictWriter(handle, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows_out)
    except PermissionError as exc:
        raise SystemExit(
            f"Permission error writing {out_path}. Close any app using the file (Excel/Power BI), then re-run."
        ) from exc

    print(f"Wrote {len(rows_out)} suggestions to {out_path}")


if __name__ == "__main__":
    main()
