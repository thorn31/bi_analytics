from __future__ import annotations

import csv
import difflib
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime

from customer_processing import load_master_merge_overrides, resolve_master_merge_target


STOP_TOKENS = {
    "ALL",
    "LOCATIONS",
    "LOCATION",
    "SITES",
    "SITE",
    "INCL",
    "INCLUDING",
    "USA",
}


def load_master_canonicals(path: Path) -> tuple[list[str], set[str], dict[str, list[str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        canonicals = sorted({row["Master Customer Name Canonical"] for row in csv.DictReader(handle) if row.get("Master Customer Name Canonical")})
    canon_set = set(canonicals)
    prefix_index: dict[str, list[str]] = defaultdict(list)
    for c in canonicals:
        key = re.sub(r"[^A-Z0-9]", "", c)[:4]
        prefix_index[key].append(c)
    return canonicals, canon_set, prefix_index


def normalize_tokens(value: str) -> str:
    tokens = [t for t in value.split() if t]
    # Remove stop tokens
    tokens = [t for t in tokens if t not in STOP_TOKENS]
    # Collapse consecutive duplicates
    collapsed: list[str] = []
    for t in tokens:
        if not collapsed or collapsed[-1] != t:
            collapsed.append(t)
    return " ".join(collapsed).strip()


def candidate_variants(canonical: str) -> list[str]:
    variants = []
    c = canonical.strip()
    if not c:
        return variants

    variants.append(c)
    variants.append(c.replace(" % ", "%"))
    variants.append(c.replace("% ", "%").replace(" %", "%"))

    variants.append(normalize_tokens(c))

    # If there's DBA, try left/right sides.
    if " DBA " in c:
        left, right = c.split(" DBA ", 1)
        variants.append(left.strip())
        variants.append(right.strip())
        variants.append(normalize_tokens(right.strip()))

    # If it ends with BILLING, try removing it.
    if c.endswith(" BILLING"):
        variants.append(c[: -len(" BILLING")].strip())
        variants.append(normalize_tokens(c[: -len(" BILLING")].strip()))

    # De-dupe preserving order.
    out: list[str] = []
    seen = set()
    for v in variants:
        v = v.strip()
        if v and v not in seen:
            out.append(v)
            seen.add(v)
    return out


def resolve(canonical: str, *, master_list: list[str], master_set: set[str], prefix_index: dict[str, list[str]]) -> tuple[str, float]:
    for v in candidate_variants(canonical):
        if v in master_set:
            return v, 1.0

    # Try fuzzy on narrowed candidates.
    key = re.sub(r"[^A-Z0-9]", "", canonical)[:4]
    candidates = prefix_index.get(key, master_list)
    best = ""
    best_score = 0.0
    for m in difflib.get_close_matches(canonical, candidates, n=5, cutoff=0.85):
        score = difflib.SequenceMatcher(None, canonical, m).ratio()
        if score > best_score:
            best_score = score
            best = m
    return best, best_score


def merge_rows(base: dict, incoming: dict) -> dict:
    merged = dict(base)
    for k, v in incoming.items():
        if k not in merged or not (merged.get(k) or "").strip():
            merged[k] = v
    return merged


def normalize_override_row(row: dict) -> dict:
    """
    Apply backward-compatible defaults and normalization to override rows.
    """
    out = dict(row)
    method = (out.get("Method") or "").strip()
    status = (out.get("Status") or "").strip()
    if method == "AI-Assisted Search":
        out["Method"] = "AI Analyst Research"
    if not status:
        out["Status"] = "Final"
    return out


def safe_open_for_write(path: Path):
    try:
        return path.open("w", encoding="utf-8", newline="")
    except PermissionError:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback = path.with_name(f"{path.stem}_{ts}{path.suffix}")
        print(f"Warning: could not overwrite {path} (file may be open/locked). Writing to {fallback} instead.")
        return fallback.open("w", encoding="utf-8", newline="")


def main() -> None:
    overrides_path = Path("data/governance/MasterSegmentationOverrides.csv")
    reconciled_path = Path("output/work/MasterSegmentationOverrides_reconciled.csv")
    master_map_path = Path("output/dedupe/CustomerMasterMap.csv")
    report_path = Path("output/work/OverrideCanonicalReconcile.csv")
    mismatch_report_path = Path("output/work/OverrideMismatchReport.csv")
    master_merge_overrides_path = Path("data/governance/MasterMergeOverrides.csv")

    if not overrides_path.exists():
        raise SystemExit(f"Missing {overrides_path}")
    if not master_map_path.exists():
        raise SystemExit(f"Missing {master_map_path}. Run `python3 dedupe_customers.py` first.")

    master_list, master_set, prefix_index = load_master_canonicals(master_map_path)
    master_merge_overrides = load_master_merge_overrides(master_merge_overrides_path)

    with overrides_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    by_canonical: dict[str, dict] = {}
    header = rows[0].keys() if rows else []
    for row in rows:
        canonical = (row.get("Master Customer Name Canonical") or "").strip()
        if not canonical or canonical.startswith("#"):
            continue
        by_canonical[canonical] = normalize_override_row(row)

    actions: list[dict] = []
    moved = 0

    for canonical, row in list(by_canonical.items()):
        # If the canonical is known to be merged into another master, normalize it first.
        if master_merge_overrides:
            merged_target = resolve_master_merge_target(canonical, master_merge_overrides)
            if merged_target and merged_target != canonical:
                existing_target = by_canonical.get(merged_target)
                new_row = dict(row)
                new_row["Master Customer Name Canonical"] = merged_target
                new_row["Notes"] = (new_row.get("Notes", "") + f"; merged '{canonical}' -> '{merged_target}'").strip("; ")

                if existing_target:
                    by_canonical[merged_target] = merge_rows(existing_target, new_row)
                else:
                    by_canonical[merged_target] = new_row
                del by_canonical[canonical]
                moved += 1
                actions.append(
                    {
                        "Action": "MovedByMasterMerge",
                        "From": canonical,
                        "To": merged_target,
                        "Score": "1.000",
                        "Notes": row.get("Notes", ""),
                    }
                )
                continue

        if canonical in master_set:
            continue
        target, score = resolve(canonical, master_list=master_list, master_set=master_set, prefix_index=prefix_index)
        if not target:
            actions.append(
                {
                    "Action": "Unresolved",
                    "From": canonical,
                    "To": "",
                    "Score": "",
                    "Notes": row.get("Notes", ""),
                }
            )
            continue

        # Only auto-move if it is a very strong match.
        if score >= 0.95:
            existing_target = by_canonical.get(target)
            new_row = dict(row)
            new_row["Master Customer Name Canonical"] = target
            new_row["Notes"] = (new_row.get("Notes", "") + f"; reconciled from '{canonical}' (score={score:.3f})").strip("; ")

            if existing_target:
                by_canonical[target] = merge_rows(existing_target, new_row)
            else:
                by_canonical[target] = new_row

            del by_canonical[canonical]
            moved += 1
            actions.append(
                {
                    "Action": "Moved",
                    "From": canonical,
                    "To": target,
                    "Score": f"{score:.3f}",
                    "Notes": row.get("Notes", ""),
                }
            )
        else:
            actions.append(
                {
                    "Action": "Suggest",
                    "From": canonical,
                    "To": target,
                    "Score": f"{score:.3f}",
                    "Notes": row.get("Notes", ""),
                }
            )

    # Write updated overrides (do not overwrite in-place; file may be open/locked)
    fieldnames = [
        "Master Customer Name Canonical",
        "Industrial Group",
        "Industry Detail",
        "NAICS",
        "Method",
        "Status",
        "Support Category",
        "Company Website",
        "Notes",
    ]
    reconciled_path.parent.mkdir(parents=True, exist_ok=True)
    with reconciled_path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=fieldnames)
        w.writeheader()
        for k in sorted(by_canonical.keys()):
            w.writerow({fn: by_canonical[k].get(fn, "") for fn in fieldnames})

    # Write report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=["Action", "From", "To", "Score", "Notes"])
        w.writeheader()
        w.writerows(actions)

    # Write a lightweight mismatch report: canonicals in overrides that don't exist as masters.
    mismatches = [a for a in actions if a.get("Action") in {"Unresolved", "Suggest"}]
    mismatch_report_path.parent.mkdir(parents=True, exist_ok=True)
    with safe_open_for_write(mismatch_report_path) as handle:
        w = csv.DictWriter(handle, fieldnames=["Type", "Master Customer Name Canonical", "Field", "Override", "Output"])
        w.writeheader()
        for m in mismatches:
            w.writerow(
                {
                    "Type": "MissingCanonical",
                    "Master Customer Name Canonical": m.get("From", ""),
                    "Field": "",
                    "Override": "",
                    "Output": "",
                }
            )

    print(f"Reconciled {moved} override canonicals into existing masters.")
    print(f"Wrote reconciled overrides to {reconciled_path}")
    print(f"Wrote report to {report_path}")
    print(f"Wrote mismatch report to {mismatch_report_path}")


if __name__ == "__main__":
    main()
