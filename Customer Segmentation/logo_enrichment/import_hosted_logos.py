#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import customer_processing as cp  # noqa: E402


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_master_canonicals(master_output_path: Path) -> dict[str, str]:
    """
    Loads Master Customer Name Canonical -> display master name.
    Expected columns: Master Customer Name Canonical, Master Customer Name.
    """
    if not master_output_path.exists():
        return {}
    out: dict[str, str] = {}
    with master_output_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            canonical = (row.get("Master Customer Name Canonical") or "").strip()
            display = (row.get("Master Customer Name") or "").strip()
            if canonical:
                out[canonical] = display
    return out


def _load_customer_key_to_canonical(dedupe_map_path: Path) -> dict[str, str]:
    """
    Loads Customer Key -> Master Customer Name Canonical.
    Expected columns (as produced by dedupe): Customer Key, Master Customer Name Canonical.
    """
    if not dedupe_map_path.exists():
        return {}
    out: dict[str, str] = {}
    with dedupe_map_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row.get("Customer Key") or "").strip()
            canonical = (row.get("Master Customer Name Canonical") or "").strip()
            if key and canonical:
                out[key] = canonical
    return out


def _safe_logo_basename(canonical: str) -> str:
    """
    Generates a stable, filesystem-safe basename for hosted logos.
    """
    v = (canonical or "").strip().upper()
    if not v:
        return ""
    v = v.replace(" ", "_")
    v = re.sub(r"[^A-Z0-9_%.-]+", "_", v)
    v = re.sub(r"_+", "_", v).strip("._")
    return v[:120]


def _join_url(base_url: str, blob_name: str) -> str:
    b = (base_url or "").strip().rstrip("/")
    n = (blob_name or "").lstrip("/")
    if not b or not n:
        return ""
    return f"{b}/{n}"


def _basename_from_url(url: str) -> str:
    v = (url or "").strip()
    if not v:
        return ""
    # Lightweight parse: last path segment.
    v = v.split("?", 1)[0].split("#", 1)[0]
    return v.rstrip("/").rsplit("/", 1)[-1].strip()


_US_STATE_ABBREVS = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
}


def _match_tokens(value: str) -> list[str]:
    """
    Tokenization used only for fuzzy matching.
    """
    return [t for t in _normalize_for_match(value).split(" ") if t]


def _normalize_for_match(value: str) -> str:
    """
    Match-normalization: canonicalize, then remove state abbreviations that commonly
    appear in external customer lists (e.g., "Adair County, KY").
    """
    v = cp.get_master_name(value)
    tokens = [t for t in v.split(" ") if t and t.upper() not in _US_STATE_ABBREVS]
    return " ".join(tokens).strip()


def _match_score(a: str, b: str) -> float:
    """
    Composite similarity score in [0, 1].
    """
    a_norm = _normalize_for_match(a)
    b_norm = _normalize_for_match(b)
    if not a_norm or not b_norm:
        return 0.0
    if a_norm == b_norm:
        return 1.0

    ratio = SequenceMatcher(None, a_norm, b_norm).ratio()
    a_tokens = set(_match_tokens(a_norm))
    b_tokens = set(_match_tokens(b_norm))
    if not a_tokens or not b_tokens:
        tok = 0.0
    else:
        tok = len(a_tokens & b_tokens) / len(a_tokens | b_tokens)

    subset_bonus = 0.0
    if min(len(a_tokens), len(b_tokens)) >= 2 and (a_tokens.issubset(b_tokens) or b_tokens.issubset(a_tokens)):
        subset_bonus = 0.18

    substring_bonus = 0.08 if (a_norm in b_norm or b_norm in a_norm) else 0.0
    return max(0.0, min(1.0, (0.65 * ratio) + (0.35 * tok) + substring_bonus + subset_bonus))


def _best_master_match(
    customer_name: str,
    masters: dict[str, str],
) -> tuple[str, float, str, float]:
    """
    Returns (best_canonical, best_score, second_canonical, second_score).
    """
    best_can = ""
    best_score = -1.0
    second_can = ""
    second_score = -1.0

    for canonical, display in masters.items():
        # Score against both canonical and display name and take max.
        score = max(_match_score(customer_name, canonical), _match_score(customer_name, display))
        if score > best_score:
            second_can, second_score = best_can, best_score
            best_can, best_score = canonical, score
        elif score > second_score:
            second_can, second_score = canonical, score

    return best_can, best_score, second_can, second_score


@dataclass(frozen=True)
class MappedLogo:
    master_canonical: str
    customer_key: str
    customer_name: str
    source_path: Path | None
    source_url: str
    staged_path: Path
    blob_name: str
    hosted_url: str
    match_method: str
    match_score: str
    second_match: str
    second_score: str
    match_margin: str


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Map local logo files to master canonicals, stage renamed files for upload, "
            "and optionally update data/enrichment/MasterLogos.csv with Hosted Logo URL."
        )
    )
    parser.add_argument("--mapping-csv", required=True, help="CSV containing customer->logo mapping.")
    parser.add_argument(
        "--logos-dir",
        default="",
        help="Base directory for logo files referenced by mapping (optional; used to resolve relative paths).",
    )
    parser.add_argument(
        "--base-url",
        default="",
        help="Base hosted URL (e.g. https://<acct>.blob.core.windows.net/<container>). Not required if Hosted Logo URL is provided per row.",
    )
    parser.add_argument(
        "--stage-dir",
        default="output/work/logos/staged",
        help="Where to copy/rename files for upload (default: output/work/logos/staged).",
    )
    parser.add_argument(
        "--plan-csv",
        default="output/work/logos/plans/HostedLogoUploadPlan.csv",
        help="Where to write an upload plan CSV (default: output/work/logos/plans/HostedLogoUploadPlan.csv).",
    )
    parser.add_argument(
        "--master-output",
        default="",
        help="Optional path to output/final/MasterCustomerSegmentation.csv for name matching (defaults to repo default path).",
    )
    parser.add_argument(
        "--dedupe-map",
        default="",
        help="Path to output/dedupe/CustomerMasterMap.csv (defaults to repo default path).",
    )
    parser.add_argument(
        "--master-logos",
        default="data/enrichment/MasterLogos.csv",
        help="Path to MasterLogos.csv (default: data/enrichment/MasterLogos.csv).",
    )
    parser.add_argument(
        "--customer-key-column",
        default="Customer Key",
        help="Column name in mapping CSV for the customer key (default: Customer Key).",
    )
    parser.add_argument(
        "--canonical-column",
        default="Master Customer Name Canonical",
        help="Optional column name in mapping CSV for master canonical (default: Master Customer Name Canonical).",
    )
    parser.add_argument(
        "--logo-path-column",
        default="Logo Path",
        help="Column name in mapping CSV for the logo file path/filename (default: Logo Path).",
    )
    parser.add_argument(
        "--customer-name-column",
        default="Customer_Name",
        help="Column name in mapping CSV for customer name when keys/canonicals are missing (default: Customer_Name).",
    )
    parser.add_argument(
        "--logo-url-column",
        default="Logo_URL",
        help="Column name in mapping CSV for an existing logo URL (default: Logo_URL).",
    )
    parser.add_argument(
        "--hosted-url-column",
        default="Hosted Logo URL",
        help="Optional column name in mapping CSV for the final hosted logo URL (default: Hosted Logo URL).",
    )
    parser.add_argument(
        "--allow-non-base-hosted",
        action="store_true",
        help=(
            "Allow persisting Hosted Logo URL values that do not start with --base-url (default: false). "
            "When false and --base-url is provided, non-matching URLs are treated as source URLs to "
            "download/stage instead of final hosted URLs."
        ),
    )
    parser.add_argument(
        "--min-match-score",
        type=float,
        default=0.85,
        help="Minimum fuzzy match score to auto-map customer name to a master (default: 0.85).",
    )
    parser.add_argument(
        "--min-match-margin",
        type=float,
        default=0.06,
        help="Minimum gap between best and second-best match to auto-map (default: 0.06).",
    )
    parser.add_argument(
        "--overwrite-existing-hosted",
        action="store_true",
        help="Overwrite existing Hosted Logo URL in MasterLogos.csv (default: false).",
    )
    parser.add_argument(
        "--apply-master-logos",
        action="store_true",
        help="Write Hosted Logo URL values into MasterLogos.csv (default: false).",
    )
    parser.add_argument(
        "--require-local-files",
        action="store_true",
        help="Fail rows without a resolvable local file path (default: false; allows URL-only mapping).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print a summary without copying files or writing MasterLogos.csv.",
    )
    args = parser.parse_args()

    paths = cp.default_paths()
    mapping_path = Path(args.mapping_csv).expanduser().resolve()
    if not mapping_path.exists():
        raise SystemExit(f"Missing mapping CSV: {mapping_path}")

    master_output_path = Path(args.master_output).expanduser().resolve() if args.master_output else paths["master_segmentation_output"]
    masters = _load_master_canonicals(master_output_path)
    if not masters:
        raise SystemExit(f"Missing or empty master output for name matching: {master_output_path}")

    dedupe_map_path = Path(args.dedupe_map).expanduser().resolve() if args.dedupe_map else paths["dedupe_output"]
    key_to_canonical = _load_customer_key_to_canonical(dedupe_map_path)

    logos_dir = Path(args.logos_dir).expanduser().resolve() if args.logos_dir else mapping_path.parent
    stage_dir = Path(args.stage_dir).expanduser().resolve()
    plan_path = Path(args.plan_csv).expanduser().resolve()

    rows = _read_csv(mapping_path)
    if not rows:
        raise SystemExit(f"No rows found: {mapping_path}")

    # The mapping file can be path-based, url-based, key-based, or name-based.
    # We'll validate required columns per-row, but ensure at least one of the expected fields exists.
    header = set(rows[0].keys())
    has_any_source = (args.logo_path_column in header) or (args.logo_url_column in header) or (args.hosted_url_column in header)
    has_any_identity = (args.canonical_column in header) or (args.customer_key_column in header) or (args.customer_name_column in header)
    if not has_any_source or not has_any_identity:
        raise SystemExit(
            f"Mapping CSV must include at least one logo source column "
            f"({args.logo_path_column} or {args.logo_url_column} or {args.hosted_url_column}) and at least one identity column "
            f"({args.canonical_column}, {args.customer_key_column}, or {args.customer_name_column}): {mapping_path}"
        )

    if not args.base_url and args.hosted_url_column not in header:
        raise SystemExit(
            f"Provide --base-url or include a '{args.hosted_url_column}' column in the mapping CSV: {mapping_path}"
        )

    mapped: list[MappedLogo] = []
    skipped = 0
    missing_files = 0
    missing_keys = 0
    missing_master = 0
    needs_review = 0

    seen_blob_names: set[str] = set()
    for row in rows:
        raw_path = (row.get(args.logo_path_column) or "").strip() if args.logo_path_column in row else ""
        raw_hosted = (row.get(args.hosted_url_column) or "").strip() if args.hosted_url_column in row else ""
        raw_url = (row.get(args.logo_url_column) or "").strip() if args.logo_url_column in row else ""

        # If --base-url is provided, we treat that as the *only* acceptable final hosted destination
        # (unless --allow-non-base-hosted is set). Any other URL in the "Hosted Logo URL" column
        # is interpreted as a source URL that should be downloaded and then uploaded to --base-url.
        base_url = (args.base_url or "").strip().rstrip("/")
        hosted_is_final = False
        if raw_hosted:
            if not base_url:
                hosted_is_final = True
            elif args.allow_non_base_hosted:
                hosted_is_final = True
            else:
                hosted_is_final = raw_hosted.startswith(base_url + "/") or raw_hosted == base_url

        source_url = raw_url or (raw_hosted if (raw_hosted and not hosted_is_final) else "")

        if not raw_path and not source_url and not raw_hosted:
            skipped += 1
            continue

        source_path: Path | None = None
        if raw_path:
            p = Path(raw_path)
            if not p.is_absolute():
                cwd_candidate = (Path.cwd() / p).resolve()
                p = cwd_candidate if cwd_candidate.exists() else (logos_dir / p).resolve()
            if not p.exists():
                missing_files += 1
                if args.require_local_files:
                    continue
            else:
                source_path = p

        master_canonical = (row.get(args.canonical_column) or "").strip()
        customer_name = (row.get(args.customer_name_column) or "").strip() if args.customer_name_column in row else ""
        if master_canonical:
            master_canonical = cp.get_master_name(master_canonical)
            match_method = "canonical"
            match_score = "1.00"
            second_match = ""
            second_score = ""
            match_margin = ""
        else:
            customer_key = (row.get(args.customer_key_column) or "").strip()
            if customer_key:
                if not key_to_canonical:
                    raise SystemExit(f"Missing or empty dedupe map for customer->master lookup: {dedupe_map_path}")
                master_canonical = key_to_canonical.get(customer_key, "")
                if not master_canonical:
                    missing_master += 1
                    continue
                match_method = "customer_key"
                match_score = "1.00"
                second_match = ""
                second_score = ""
                match_margin = ""
            else:
                if not customer_name:
                    missing_keys += 1
                    continue
                best, best_score, second, second_score = _best_master_match(customer_name, masters)
                margin = 1.0 if not second else (best_score - second_score)
                eps = 1e-9
                if (best_score + eps) < args.min_match_score or (margin + eps) < args.min_match_margin:
                    needs_review += 1
                    # Still produce an output row for manual review, but do not stage/copy.
                    match_method = "fuzzy_needs_review"
                    match_score = f"{best_score:.2f}"
                    second_match = second
                    second_score = "" if not second else f"{second_score:.2f}"
                    match_margin = f"{margin:.2f}"
                    master_canonical = best
                else:
                    match_method = "fuzzy"
                    match_score = f"{best_score:.2f}"
                    second_match = second
                    second_score = "" if not second else f"{second_score:.2f}"
                    match_margin = f"{margin:.2f}"
                    master_canonical = best

        customer_key = (row.get(args.customer_key_column) or "").strip()
        safe_base = _safe_logo_basename(master_canonical)
        if not safe_base:
            skipped += 1
            continue

        ext = ""
        if source_path is not None:
            ext = source_path.suffix.lower()
        if not ext and source_url:
            # Heuristic extension from URL path.
            m = re.search(r"\.(png|jpg|jpeg|webp|gif|svg)\b", source_url.lower())
            ext = f".{m.group(1)}" if m else ""
        ext = ext or ".png"

        # If the row supplies a final hosted URL, preserve its filename in the plan; otherwise
        # standardize filenames to the master canonical name (so downloaded files are renamed).
        blob_name = (_basename_from_url(raw_hosted) if hosted_is_final else "") or f"{safe_base}{ext}"
        if blob_name in seen_blob_names:
            # Deterministic de-dupe to avoid clobbering; prefer the first mapping row.
            skipped += 1
            continue
        seen_blob_names.add(blob_name)

        staged_path = stage_dir / blob_name
        hosted_url = raw_hosted if hosted_is_final else _join_url(args.base_url, blob_name)
        mapped.append(
            MappedLogo(
                master_canonical=master_canonical,
                customer_key=customer_key,
                customer_name=customer_name,
                source_path=source_path,
                source_url=source_url,
                staged_path=staged_path,
                blob_name=blob_name,
                hosted_url=hosted_url,
                match_method=match_method,
                match_score=match_score,
                second_match=second_match,
                second_score=second_score,
                match_margin=match_margin,
            )
        )

    if args.dry_run:
        print(f"Mapping: {mapping_path}")
        print(f"Logos dir: {logos_dir}")
        print(f"Dedupe map: {dedupe_map_path}")
        print(f"Master output: {master_output_path}")
        print(f"Base URL: {args.base_url or '(none)'}")
        would_copy = sum(1 for m in mapped if m.source_path is not None and not m.staged_path.exists())
        print(f"Would write plan rows: {len(mapped)}")
        print(f"Would copy local files: {would_copy} -> {stage_dir}")
        print(f"Skipped: {skipped} (blank/duplicate/invalid)")
        print(f"Missing files: {missing_files}")
        print(f"Missing customer keys: {missing_keys}")
        print(f"Missing master mapping: {missing_master}")
        print(f"Needs review (fuzzy below threshold): {needs_review}")
        for item in mapped[:10]:
            print(f"{item.master_canonical} => {item.blob_name} ({item.match_method}, score={item.match_score})")
        raise SystemExit(0)

    copied = 0
    if any(item.source_path is not None for item in mapped):
        stage_dir.mkdir(parents=True, exist_ok=True)
        for item in mapped:
            if item.staged_path.exists() or item.source_path is None:
                continue
            shutil.copy2(item.source_path, item.staged_path)
            copied += 1

    plan_rows: list[dict[str, str]] = []
    for item in mapped:
        plan_rows.append(
            {
                "Master Customer Name Canonical": item.master_canonical,
                "Customer Key": item.customer_key,
                "Customer Name": item.customer_name,
                "Source Path": "" if item.source_path is None else str(item.source_path),
                "Source URL": (item.source_url or "").strip(),
                "Staged Path": str(item.staged_path),
                "Blob Name": item.blob_name,
                "Hosted Logo URL": item.hosted_url,
                "Match Method": item.match_method,
                "Match Score": item.match_score,
                "Second Match": item.second_match,
                "Second Score": item.second_score,
                "Match Margin": item.match_margin,
            }
        )
    cp.write_csv_dicts(
        plan_path,
        plan_rows,
        fieldnames=[
            "Master Customer Name Canonical",
            "Customer Key",
            "Customer Name",
            "Source Path",
            "Source URL",
            "Staged Path",
            "Blob Name",
            "Hosted Logo URL",
            "Match Method",
            "Match Score",
            "Second Match",
            "Second Score",
            "Match Margin",
        ],
    )
    if copied:
        print(f"Copied {copied} local files to {stage_dir}")
    else:
        print("No local files copied (URL-only mapping or missing Logo Path files).")
    print(f"Wrote upload plan: {plan_path}")

    review_path = plan_path.with_name("HostedLogoMatchReview.csv")
    review_rows: list[dict[str, str]] = []
    for item in mapped:
        if item.match_method not in {"fuzzy", "fuzzy_needs_review"}:
            continue
        review_rows.append(
            {
                "Customer Name": item.customer_name,
                "Suggested Master Canonical": item.master_canonical,
                "Match Score": item.match_score,
                "Second Match": item.second_match,
                "Second Score": item.second_score,
                "Match Margin": item.match_margin,
                "Source URL": (item.source_url or "").strip(),
                "Source Path": "" if item.source_path is None else str(item.source_path),
                "Blob Name": item.blob_name,
                "Hosted Logo URL": item.hosted_url,
                "Outcome": "Needs Review" if item.match_method == "fuzzy_needs_review" else "Auto-Matched",
            }
        )
    if review_rows:
        cp.write_csv_dicts(
            review_path,
            review_rows,
            fieldnames=[
                "Customer Name",
                "Suggested Master Canonical",
                "Match Score",
                "Second Match",
                "Second Score",
                "Match Margin",
                "Source URL",
                "Source Path",
                "Blob Name",
                "Hosted Logo URL",
                "Outcome",
            ],
        )
        print(f"Wrote match review: {review_path}")

    if not args.apply_master_logos:
        return
    if not mapped:
        # Defensive: avoid overwriting MasterLogos.csv with an empty file when the mapping
        # CSV contains no applicable rows (e.g., pipeline ran with --skip-upload and produced
        # an empty persist mapping).
        print("No mapped logo rows to apply; leaving MasterLogos.csv unchanged.")
        return

    master_logos_path = Path(args.master_logos).expanduser().resolve()
    existing_rows: list[dict] = []
    existing: dict[str, dict[str, str]] = {}
    if master_logos_path.exists():
        existing_rows = _read_csv(master_logos_path)
        for r in existing_rows:
            canonical = (r.get("Master Customer Name Canonical") or "").strip()
            if not canonical or canonical.startswith("#"):
                continue
            existing[canonical] = r

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updates = 0
    adds = 0
    for item in mapped:
        # Only apply high-confidence matches. Anything flagged "needs review" still appears
        # in the upload plan for manual correction.
        if item.match_method.startswith("fuzzy_needs_review"):
            continue
        base = dict(existing.get(item.master_canonical, {}))
        if not base:
            base = {
                "Master Customer Name Canonical": item.master_canonical,
                "Logo Domain": "",
                "Logo Status": "",
                "Attempt Count": "0",
                "Last Attempted At": "",
                "Notes": "",
                "Updated At": "",
                "Hosted Logo URL": "",
            }
            adds += 1

        current = (base.get("Hosted Logo URL") or "").strip()
        if current and not args.overwrite_existing_hosted:
            existing[item.master_canonical] = base
            continue
        if current != item.hosted_url:
            base["Hosted Logo URL"] = item.hosted_url
            if not (base.get("Logo Status") or "").strip():
                base["Logo Status"] = "Hosted"
            base["Updated At"] = now
            existing[item.master_canonical] = base
            updates += 1

    # Preserve comment/example rows if present.
    out_rows: list[dict[str, str]] = []
    for r in existing_rows:
        canonical = (r.get("Master Customer Name Canonical") or "").strip()
        if canonical.startswith("#"):
            out_rows.append(
                {
                    "Master Customer Name Canonical": canonical,
                    "Logo Domain": (r.get("Logo Domain") or "").strip(),
                    "Logo Status": (r.get("Logo Status") or "").strip(),
                    "Attempt Count": (r.get("Attempt Count") or "").strip(),
                    "Last Attempted At": (r.get("Last Attempted At") or "").strip(),
                    "Notes": (r.get("Notes") or "").strip(),
                    "Updated At": (r.get("Updated At") or "").strip(),
                    "Hosted Logo URL": (r.get("Hosted Logo URL") or "").strip(),
                }
            )

    for canonical in sorted(existing.keys()):
        r = existing[canonical]
        out_rows.append(
            {
                "Master Customer Name Canonical": canonical,
                "Logo Domain": (r.get("Logo Domain") or "").strip(),
                "Logo Status": (r.get("Logo Status") or "").strip(),
                "Attempt Count": (r.get("Attempt Count") or "").strip(),
                "Last Attempted At": (r.get("Last Attempted At") or "").strip(),
                "Notes": (r.get("Notes") or "").strip(),
                "Updated At": (r.get("Updated At") or "").strip(),
                "Hosted Logo URL": (r.get("Hosted Logo URL") or "").strip(),
            }
        )

    cp.write_csv_dicts(
        master_logos_path,
        out_rows,
        fieldnames=[
            "Master Customer Name Canonical",
            "Logo Domain",
            "Logo Status",
            "Attempt Count",
            "Last Attempted At",
            "Notes",
            "Updated At",
            "Hosted Logo URL",
        ],
    )
    print(f"Updated {master_logos_path} (adds={adds}, updates={updates}, overwrite_existing_hosted={args.overwrite_existing_hosted})")


if __name__ == "__main__":
    main()
