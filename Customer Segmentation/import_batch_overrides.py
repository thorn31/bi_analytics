from __future__ import annotations

import argparse
import csv
import difflib
import re
from pathlib import Path
from datetime import datetime

from customer_processing import default_paths, get_master_name, load_master_merge_overrides, resolve_master_merge_target


LOCKED_GROUPS = {
    "Manufacturing",
    "Commercial Real Estate",
    "Construction",
    "Energy Services",
    "Utilities",
    "Financial Services",
    "Healthcare / Senior Living",
    "University / College",
    "Public Schools (K–12)",
    "Private Schools (K–12)",
    "Municipal / Local Government",
    "Commercial Services",
    "Non-Profit / Religious",
    "Individual / Misc",
    "Unknown / Needs Review",
}

STOP_TOKENS = {
    "ALL",
    "LOCATIONS",
    "LOCATION",
    "SITES",
    "SITE",
    "INCL",
    "INCLUDING",
    "BILLING",
    "USA",
    "ONE",
    "TWO",
    "THREE",
}

def _safe_open_for_write(path: Path):
    try:
        return path.open("w", encoding="utf-8", newline="")
    except PermissionError:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback = path.with_name(f"{path.stem}_{ts}{path.suffix}")
        print(f"Warning: could not overwrite {path} (file may be open/locked). Writing to {fallback} instead.")
        return fallback.open("w", encoding="utf-8", newline="")


def normalize_industrial_group(value: str) -> tuple[str, str]:
    v = (value or "").strip()
    if not v:
        return "", ""
    if v in LOCKED_GROUPS:
        return v, ""

    lower = v.lower()
    if "construction" in lower:
        support = "Mechanical Contractor" if "mechanical" in lower else ""
        return "Construction", support
    if "telecom" in lower:
        return "Commercial Services", "Telecommunications"
    if "retail" in lower or "hospitality" in lower:
        support = "Hospitality" if "hospitality" in lower else "Retail"
        return "Commercial Services", support
    if "healthcare" in lower:
        return "Healthcare / Senior Living", ""
    if "commercial services" in lower:
        return "Commercial Services", ""
    return "Unknown / Needs Review", ""


def normalize_status(value: str) -> str:
    v = (value or "").strip()
    if not v:
        return ""
    lower = v.lower()
    if lower in {"final", "approved", "done"}:
        return "Final"
    if lower in {"draft", "wip"}:
        return "Draft"
    if lower in {"queued", "queue", "research", "needs research", "needs review"}:
        return "Queued"
    return v

def _load_master_canonicals() -> tuple[set[str], dict[str, list[str]]]:
    """
    Returns (canonicals, prefix_index) where prefix_index maps a short prefix to
    a list of canonicals for cheap candidate narrowing.
    """
    paths = default_paths()
    master_map_path = paths["dedupe_output"]
    canonicals: set[str] = set()
    prefix_index: dict[str, list[str]] = {}

    if not master_map_path.exists():
        return canonicals, prefix_index

    with master_map_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            c = (row.get("Master Customer Name Canonical") or "").strip()
            if not c:
                continue
            canonicals.add(c)
            key = re.sub(r"[^A-Z0-9]", "", c)[:4]
            prefix_index.setdefault(key, []).append(c)

    return canonicals, prefix_index


def _expand_customer_names(raw: str) -> list[str]:
    """
    Batch files often include combined names like:
      - 'A / B / C'
      - 'X (Y)' where Y is an alias
      - 'X DBA Y'
    Expand into candidate names to match masters.
    """
    raw = (raw or "").strip()
    if not raw:
        return []

    # Normalize common suffix notes.
    raw = re.sub(r"\s*\(all locations\)\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*\(sites\)\s*", "", raw, flags=re.IGNORECASE)
    raw = raw.replace(" incl. ", " ")
    raw = raw.replace(" (incl. ", " (")

    parts = [p.strip() for p in re.split(r"\s+/\s+", raw) if p.strip()]
    # Some batch entries use "/" to separate a base name from a location/unit token,
    # e.g. "US FOOD SERVICE / KNOXVILLE" or "BUILDING ONE / TWO". When the right-hand
    # side is a short, single-token suffix, treat it as part of the same customer.
    merged_parts: list[str] = []
    for p in parts:
        is_short_suffix = (
            bool(merged_parts)
            and len(p.split()) == 1
            and 3 <= len(p) <= 20
            and p.isalpha()
            and p.upper() == p
            and p.upper() not in STOP_TOKENS
        )
        if is_short_suffix:
            merged_parts[-1] = f"{merged_parts[-1]} {p}"
        else:
            merged_parts.append(p)
    expanded: list[str] = []
    for part in merged_parts:
        # If it contains DBA, capture both sides (prefer right, but keep left too).
        if re.search(r"\bDBA\b", part, flags=re.IGNORECASE):
            left, right = re.split(r"\bDBA\b", part, maxsplit=1, flags=re.IGNORECASE)
            left = left.strip(" -–—")
            right = right.strip(" -–—")
            if left:
                expanded.append(left)
            if right:
                expanded.append(right)
            continue

        # If it contains parenthetical alias, include both base and alias.
        m = re.search(r"^(.*?)\((.*?)\)\s*$", part)
        if m:
            base = m.group(1).strip()
            alias = m.group(2).strip()
            if base:
                expanded.append(base)
            # Only treat as alias if it looks like a name, not a note.
            is_note = bool(re.search(r"\b(verify|unclear|billing|include|incl|all locations|sites?)\b", alias, flags=re.IGNORECASE))
            # Parenthetical location lists like "(CENTERVILLE/CINCINNATI)" are notes, not aliases.
            if "/" in alias or "," in alias:
                is_note = True
            if alias and not is_note:
                expanded.append(alias)
            continue

        expanded.append(part)

    # De-dupe preserving order.
    seen = set()
    out: list[str] = []
    for x in expanded:
        # Drop obviously non-name tokens created by splitting artifacts.
        if not x or len(x) < 3:
            continue
        upper = x.upper().strip()
        if upper in {"BILLING", "LOCATION", "LOCATIONS"}:
            continue
        if upper in STOP_TOKENS:
            continue
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def _resolve_to_master_canonical(
    candidate_canonical: str,
    *,
    canonicals: set[str],
    prefix_index: dict[str, list[str]],
) -> str:
    def normalize_percent(value: str) -> str:
        # Canonical masters tend to look like "10% CABINETRY" (no space before %, single space after).
        value = re.sub(r"\s*%\s*", "% ", value)
        value = re.sub(r"\s+", " ", value).strip()
        return value

    if not candidate_canonical:
        return ""
    if candidate_canonical in canonicals:
        return candidate_canonical

    # Try simple percent spacing variants.
    variants = {
        normalize_percent(candidate_canonical),
        candidate_canonical.replace(" % ", "% "),
        candidate_canonical.replace("% ", "% ").replace(" %", "%"),
    }
    for v in variants:
        if v in canonicals:
            return v

    key = re.sub(r"[^A-Z0-9]", "", candidate_canonical)[:4]
    candidates = prefix_index.get(key, [])
    if not candidates:
        candidates = list(canonicals)

    # Exact match under a punctuation/spacing-insensitive normalization.
    normalized_candidate = re.sub(r"[^A-Z0-9]", "", candidate_canonical)
    for m in candidates:
        if re.sub(r"[^A-Z0-9]", "", m) == normalized_candidate:
            return m

    # If the candidate is a shortened prefix of a longer master canonical, and the
    # match is unique, treat it as the intended canonical (e.g., missing a location suffix).
    prefix_matches = [m for m in candidates if re.sub(r"[^A-Z0-9]", "", m).startswith(normalized_candidate)]
    if len(prefix_matches) == 1:
        return prefix_matches[0]

    match = difflib.get_close_matches(candidate_canonical, candidates, n=1, cutoff=0.92)
    return match[0] if match else ""

def _tokenize(value: str) -> list[str]:
    tokens = [t for t in re.split(r"[^A-Z0-9]+", value.upper()) if t]
    tokens = [t for t in tokens if t not in STOP_TOKENS and t not in {"DBA", "AND", "THE"}]
    return tokens


def _masters_matching_tokens(tokens: list[str], master_canonicals: list[str]) -> list[str]:
    if len(tokens) < 2:
        # Single-token matching is only used as a fallback in the batch import cleanup.
        # It can be ambiguous, so keep it conservative.
        if len(tokens) == 1 and len(tokens[0]) >= 4 and tokens[0] not in STOP_TOKENS:
            token = tokens[0]
            matches: list[str] = []
            for m in master_canonicals:
                m_tokens = set(_tokenize(m))
                if token in m_tokens:
                    matches.append(m)
            return matches
        return []
    matches: list[str] = []
    for m in master_canonicals:
        m_tokens = set(_tokenize(m))
        if all(t in m_tokens for t in tokens):
            matches.append(m)
    return matches


def _merge_rows(base: dict, incoming: dict) -> dict:
    merged = dict(base)
    for k, v in incoming.items():
        if k not in merged or not (merged.get(k) or "").strip():
            merged[k] = v
    return merged


def parse_tables(md_text: str) -> list[dict]:
    sections: list[dict] = []
    current: dict | None = None
    for line in md_text.splitlines():
        m = re.match(r"^##\s+(.*)\s*$", line)
        if m:
            current = {"name": m.group(1).strip(), "lines": []}
            sections.append(current)
            continue
        if current is not None:
            current["lines"].append(line)

    def parse_table(lines: list[str]) -> list[dict]:
        out: list[dict] = []
        header: list[str] | None = None
        for i, line in enumerate(lines):
            if line.strip().startswith("|") and "---" in line:
                j = i - 1
                while j >= 0 and not lines[j].strip():
                    j -= 1
                if j >= 0 and lines[j].strip().startswith("|"):
                    header = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                    k = i + 1
                    while k < len(lines):
                        l = lines[k]
                        if not l.strip().startswith("|"):
                            break
                        cols = [c.strip() for c in l.strip().strip("|").split("|")]
                        if len(cols) >= len(header):
                            out.append(dict(zip(header, cols)))
                        k += 1
                break
        return out

    rows: list[dict] = []
    for sec in sections:
        table = parse_table(sec["lines"])
        if not table:
            continue
        for r in table:
            r["_Section"] = sec["name"]
            rows.append(r)
    return rows


def support_category_from_section(section: str) -> str:
    s = section.strip().lower()
    if "retail" in s or "hospitality" in s:
        # support category can be refined by row later; default to Hospitality if mentioned
        if "hospitality" in s:
            return "Hospitality"
        return "Retail"
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a markdown batch file into master segmentation overrides CSV.")
    parser.add_argument("--input-md", default="input/Batch Process 1.md")
    args = parser.parse_args()

    md_path = Path(args.input_md)
    if not md_path.exists():
        raise SystemExit(f"Missing {md_path}")

    md_text = md_path.read_text(encoding="utf-8")
    rows = parse_tables(md_text)
    if not rows:
        raise SystemExit("No tables found to import.")

    paths = default_paths()
    repo_root = paths["manual_overrides"].parent.parent
    out_path = repo_root / "input" / "MasterSegmentationOverrides.csv"
    reconciled_out_path = repo_root / "input" / "MasterSegmentationOverrides_reconciled.csv"

    # Load existing overrides to avoid duplicates (last write wins for the same canonical)
    existing: dict[str, dict] = {}
    if out_path.exists():
        with out_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                canonical = (row.get("Master Customer Name Canonical") or "").strip()
                if canonical and not canonical.startswith("#"):
                    existing[canonical] = row

    master_canonicals, prefix_index = _load_master_canonicals()
    master_merge_overrides = load_master_merge_overrides(paths["master_merge_overrides"])

    for r in rows:
        customer_raw = (r.get("Customer") or "").strip()
        if not customer_raw:
            continue

        customer_names = _expand_customer_names(customer_raw)
        if not customer_names:
            continue

        section = (r.get("_Section") or "").strip()
        industrial_group = section
        # Treat Retail/Hospitality as support category, not primary group.
        support = support_category_from_section(section)
        if support:
            industrial_group = "Commercial Services"

        # Normalize section names into the locked Industrial Group list.
        section_lower = section.lower()
        if "construction" in section_lower:
            industrial_group = "Construction"
            # Preserve some context from the section title as support info.
            if "mechanical" in section_lower:
                support = support or "Mechanical Contractor"
        elif "commercial services" in section_lower or "telecommunications" in section_lower:
            industrial_group = "Commercial Services"
            if "telecommunications" in section_lower:
                support = support or "Telecommunications"
        elif "healthcare" in section_lower:
            industrial_group = "Healthcare / Senior Living"
        elif "non-profit" in section_lower or "religious" in section_lower:
            industrial_group = "Non-Profit / Religious"
        elif "public schools" in section_lower:
            industrial_group = "Public Schools (K–12)"
        elif "private schools" in section_lower:
            industrial_group = "Private Schools (K–12)"
        elif "university" in section_lower or "college" in section_lower:
            industrial_group = "University / College"
        elif "municipal" in section_lower or "local government" in section_lower:
            industrial_group = "Municipal / Local Government"
        elif "manufacturing" in section_lower:
            industrial_group = "Manufacturing"
        elif "commercial real estate" in section_lower:
            industrial_group = "Commercial Real Estate"
        elif "energy services" in section_lower:
            industrial_group = "Energy Services"
        elif "utilities" in section_lower:
            industrial_group = "Utilities"
        elif "financial services" in section_lower:
            industrial_group = "Financial Services"
        elif "individual" in section_lower:
            industrial_group = "Individual / Misc"
        elif "unknown" in section_lower or "needs review" in section_lower:
            industrial_group = "Unknown / Needs Review"

        domain = (r.get("Domain") or "").strip()
        naics = (r.get("NAICS") or "").strip()
        if naics == "—":
            naics = ""
        raw_method = (r.get("Method") or "").strip() or "Manual Override"
        # Optional column support (some batches may include an explicit Status).
        status = normalize_status(r.get("Status") or r.get("Review Status") or "") or "Final"
        method = "AI Analyst Research" if raw_method == "AI-Assisted Search" else raw_method

        for customer in customer_names:
            candidate_canonical = get_master_name(customer)
            if master_merge_overrides:
                candidate_canonical = resolve_master_merge_target(candidate_canonical, master_merge_overrides)
            resolved = _resolve_to_master_canonical(
                candidate_canonical, canonicals=master_canonicals, prefix_index=prefix_index
            )

            notes = f"Imported from {md_path.name}"
            if resolved and resolved != candidate_canonical:
                notes = f"{notes}; resolved '{candidate_canonical}' -> '{resolved}'"
            elif not resolved and master_canonicals:
                # Attempt to expand brand/location style names into multiple masters.
                tokens = _tokenize(candidate_canonical)
                token_matches = _masters_matching_tokens(tokens, list(master_canonicals))
                if 1 <= len(token_matches) <= 25:
                    for mcan in token_matches:
                        expanded_notes = f"{notes}; expanded tokens {tokens} -> '{mcan}'"
                        existing[mcan] = {
                            "Master Customer Name Canonical": mcan,
                            "Industrial Group": industrial_group,
                            "Industry Detail": (r.get("Industry Detail") or "").strip(),
                            "NAICS": naics,
                            "Method": method,
                            "Status": status,
                            "Support Category": support,
                            "Company Website": domain,
                            "Notes": expanded_notes,
                        }
                    continue
                notes = f"{notes}; unresolved master canonical '{candidate_canonical}'"

            canonical = resolved or candidate_canonical
            existing[canonical] = {
                "Master Customer Name Canonical": canonical,
                "Industrial Group": industrial_group,
                "Industry Detail": (r.get("Industry Detail") or "").strip(),
                "NAICS": naics,
                "Method": method,
                "Status": status,
                "Support Category": support,
                "Company Website": domain,
                "Notes": notes,
            }

    # Cleanup: reconcile any non-master override keys that linger from prior imports.
    moved = 0
    expanded = 0
    dropped = 0
    for canonical in list(existing.keys()):
        if canonical in master_canonicals:
            continue
        if canonical.startswith("#"):
            continue
        # Drop pure noise keys.
        if canonical in STOP_TOKENS or canonical in {"BILLING", "LOCATIONS", "LOCATION"}:
            del existing[canonical]
            dropped += 1
            continue

        resolved = _resolve_to_master_canonical(canonical, canonicals=master_canonicals, prefix_index=prefix_index)
        if resolved:
            row = existing.pop(canonical)
            row["Master Customer Name Canonical"] = resolved
            row["Notes"] = (row.get("Notes", "") + f"; auto-reconciled '{canonical}' -> '{resolved}'").strip("; ")
            if resolved in existing:
                existing[resolved] = _merge_rows(existing[resolved], row)
            else:
                existing[resolved] = row
            moved += 1
            continue

        tokens = _tokenize(canonical)
        token_matches = _masters_matching_tokens(tokens, list(master_canonicals))
        if 1 <= len(token_matches) <= 25:
            row = existing.pop(canonical)
            for target in token_matches:
                new_row = dict(row)
                new_row["Master Customer Name Canonical"] = target
                new_row["Notes"] = (new_row.get("Notes", "") + f"; auto-expanded '{canonical}' -> '{target}'").strip("; ")
                if target in existing:
                    existing[target] = _merge_rows(existing[target], new_row)
                else:
                    existing[target] = new_row
            expanded += 1

    # Normalize any pre-existing non-locked groups (from earlier imports).
    for canonical, row in existing.items():
        group, inferred_support = normalize_industrial_group(row.get("Industrial Group", ""))
        if group:
            row["Industrial Group"] = group
        if inferred_support and not row.get("Support Category"):
            row["Support Category"] = inferred_support
        if not (row.get("Status") or "").strip():
            # Default any existing rows to Final (unless explicitly queued elsewhere).
            row["Status"] = "Final"

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

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with _safe_open_for_write(out_path) as handle:
        w = csv.DictWriter(handle, fieldnames=fieldnames)
        w.writeheader()
        w.writerows([existing[k] for k in sorted(existing.keys())])

    print(f"Wrote {len(existing)} master overrides to {out_path}")
    if moved or expanded or dropped:
        print(f"Reconciled {moved} canonicals and expanded {expanded}; dropped {dropped} noise rows.")

    # Also write a reconciled copy used by the segmentation step (preferred when present).
    reconciled_out_path.parent.mkdir(parents=True, exist_ok=True)
    with _safe_open_for_write(reconciled_out_path) as handle:
        w = csv.DictWriter(handle, fieldnames=fieldnames)
        w.writeheader()
        w.writerows([existing[k] for k in sorted(existing.keys())])


if __name__ == "__main__":
    main()
