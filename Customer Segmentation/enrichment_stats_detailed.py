from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def _norm(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


def _has_value(value: str | None) -> bool:
    return bool(_norm(value))


def main() -> None:
    path = Path("output/final/MasterCustomerSegmentation.csv")
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")

    groups: dict[str, dict[str, int]] = defaultdict(
        lambda: {"Total": 0, "Has_NAICS": 0, "Has_Website": 0, "Verified": 0}
    )

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            industrial_group = _norm(row.get("Industrial Group")) or "(blank)"
            status = _norm(row.get("Enrichment Status")) or "Pending"

            groups[industrial_group]["Total"] += 1
            if _has_value(row.get("NAICS")):
                groups[industrial_group]["Has_NAICS"] += 1
            if _has_value(row.get("Company Website")):
                groups[industrial_group]["Has_Website"] += 1
            if status == "Verified":
                groups[industrial_group]["Verified"] += 1

    records = []
    for group, counts in groups.items():
        total = counts["Total"]
        has_naics = counts["Has_NAICS"]
        has_web = counts["Has_Website"]
        pct_naics = round((has_naics / total * 100.0), 1) if total else 0.0
        pct_web = round((has_web / total * 100.0), 1) if total else 0.0
        records.append(
            {
                "Industrial Group": group,
                "Total": total,
                "Has_NAICS": has_naics,
                "Has_Website": has_web,
                "% NAICS": pct_naics,
                "% Web": pct_web,
                "Verified": counts["Verified"],
            }
        )

    records.sort(key=lambda r: r["Total"], reverse=True)

    print(f"{'Industrial Group':<40} | {'Total':<6} | {'Has NAICS':<10} | {'Has Web':<10} | {'% NAICS':<8} | {'% Web':<6}")
    print("-" * 95)
    for r in records:
        name = str(r["Industrial Group"])[:39]
        print(f"{name:<40} | {r['Total']:<6} | {r['Has_NAICS']:<10} | {r['Has_Website']:<10} | {r['% NAICS']}%   | {r['% Web']}%")

    total_records = sum(r["Total"] for r in records)
    total_naics = sum(r["Has_NAICS"] for r in records)
    total_web = sum(r["Has_Website"] for r in records)

    print(f"\nTotal Records: {total_records}")
    print(f"Records with NAICS: {total_naics} ({(total_naics / total_records * 100.0) if total_records else 0.0:.1f}%)")
    print(f"Records with Website: {total_web} ({(total_web / total_records * 100.0) if total_records else 0.0:.1f}%)")


if __name__ == "__main__":
    main()
