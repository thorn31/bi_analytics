from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from customer_processing import default_paths, get_master_name


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
    out_path = paths["master_segmentation_overrides"]

    # Load existing overrides to avoid duplicates (last write wins for the same canonical)
    existing: dict[str, dict] = {}
    if out_path.exists():
        with out_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                canonical = (row.get("Master Customer Name Canonical") or "").strip()
                if canonical and not canonical.startswith("#"):
                    existing[canonical] = row

    for r in rows:
        customer = (r.get("Customer") or "").strip()
        if not customer:
            continue
        canonical = get_master_name(customer)

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

        existing[canonical] = {
            "Master Customer Name Canonical": canonical,
            "Industrial Group": industrial_group,
            "Industry Detail": (r.get("Industry Detail") or "").strip(),
            "NAICS": naics,
            "Method": (r.get("Method") or "").strip() or "Manual Override",
            "Support Category": support,
            "Company Website": domain,
            "Notes": f"Imported from {md_path.name}",
        }

    # Normalize any pre-existing non-locked groups (from earlier imports).
    for canonical, row in existing.items():
        group, inferred_support = normalize_industrial_group(row.get("Industrial Group", ""))
        if group:
            row["Industrial Group"] = group
        if inferred_support and not row.get("Support Category"):
            row["Support Category"] = inferred_support

    fieldnames = [
        "Master Customer Name Canonical",
        "Industrial Group",
        "Industry Detail",
        "NAICS",
        "Method",
        "Support Category",
        "Company Website",
        "Notes",
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=fieldnames)
        w.writeheader()
        w.writerows([existing[k] for k in sorted(existing.keys())])

    print(f"Wrote {len(existing)} master overrides to {out_path}")


if __name__ == "__main__":
    main()
