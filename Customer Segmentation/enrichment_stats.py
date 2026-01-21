from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def _norm(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


def main() -> None:
    path = Path("output/final/MasterCustomerSegmentation.csv")
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")

    groups: dict[str, dict[str, int]] = defaultdict(lambda: {"Total": 0, "Verified": 0, "Deferred": 0, "Pending": 0})

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            industrial_group = _norm(row.get("Industrial Group")) or "(blank)"
            status = _norm(row.get("Enrichment Status")) or "Pending"

            groups[industrial_group]["Total"] += 1
            if status == "Verified":
                groups[industrial_group]["Verified"] += 1
            elif status == "Deferred":
                groups[industrial_group]["Deferred"] += 1
            else:
                groups[industrial_group]["Pending"] += 1

    records = []
    for group, counts in groups.items():
        total = counts["Total"]
        verified = counts["Verified"]
        deferred = counts["Deferred"]
        pending = counts["Pending"]
        unenriched = deferred + pending
        pct_enriched = round((verified / total * 100.0), 1) if total else 0.0
        records.append(
            {
                "Industrial Group": group,
                "Total": total,
                "Verified": verified,
                "Deferred": deferred,
                "Pending": pending,
                "Unenriched": unenriched,
                "% Enriched": pct_enriched,
            }
        )

    records.sort(key=lambda r: (r["Unenriched"], r["Total"]), reverse=True)

    print(f"{'Industrial Group':<40} | {'Total':<6} | {'Verif.':<6} | {'Defer':<6} | {'Pending':<7} | {'% Done':<6}")
    print("-" * 90)
    for r in records:
        name = str(r["Industrial Group"])[:39]
        print(f"{name:<40} | {r['Total']:<6} | {r['Verified']:<6} | {r['Deferred']:<6} | {r['Pending']:<7} | {r['% Enriched']}%")

    total_records = sum(r["Total"] for r in records)
    total_verified = sum(r["Verified"] for r in records)
    total_deferred = sum(r["Deferred"] for r in records)

    print(f"\nTotal Records: {total_records}")
    print(f"Total Verified: {total_verified} ({(total_verified / total_records * 100.0) if total_records else 0.0:.1f}%)")
    print(f"Total Deferred: {total_deferred} ({(total_deferred / total_records * 100.0) if total_records else 0.0:.1f}%)")


if __name__ == "__main__":
    main()
