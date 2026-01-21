from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def _norm(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory Industry Detail values with Industrial Group context.")
    parser.add_argument(
        "--input",
        default="output/final/MasterCustomerSegmentation.csv",
        help="CSV path to analyze (default: output/final/MasterCustomerSegmentation.csv).",
    )
    parser.add_argument(
        "--out-dir",
        default="output/work/inventory",
        help="Folder to write reports (default: output/work/inventory).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=50,
        help="How many top rows to print per section (default: 50).",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Missing input: {in_path}")

    out_dir = Path(args.out_dir)

    overall = Counter()
    by_group = Counter()
    group_totals = Counter()
    blanks_by_group = Counter()

    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            group = _norm(row.get("Industrial Group")) or "(blank)"
            detail = _norm(row.get("Industry Detail"))

            group_totals[group] += 1
            if not detail:
                blanks_by_group[group] += 1
                detail = "(blank)"

            overall[detail] += 1
            by_group[(group, detail)] += 1

    # Write overall details (flat)
    overall_rows = [
        {"Industry Detail": detail, "Count": count, "Pct of Total": round(count / sum(overall.values()) * 100.0, 2)}
        for detail, count in overall.most_common()
    ]
    overall_path = out_dir / "IndustryDetail_overall.csv"
    _write_csv(overall_path, ["Industry Detail", "Count", "Pct of Total"], overall_rows)

    # Write grouped detail counts
    grouped_rows = []
    for (group, detail), count in by_group.most_common():
        total = group_totals[group]
        grouped_rows.append(
            {
                "Industrial Group": group,
                "Industry Detail": detail,
                "Count": count,
                "Pct of Group": round((count / total * 100.0) if total else 0.0, 2),
            }
        )
    grouped_path = out_dir / "IndustryDetail_byGroup.csv"
    _write_csv(grouped_path, ["Industrial Group", "Industry Detail", "Count", "Pct of Group"], grouped_rows)

    # Write group totals / blanks
    totals_rows = []
    for group, total in group_totals.most_common():
        blanks = blanks_by_group.get(group, 0)
        totals_rows.append(
            {
                "Industrial Group": group,
                "Total": total,
                "Blank Industry Detail": blanks,
                "Pct Blank": round((blanks / total * 100.0) if total else 0.0, 2),
            }
        )
    totals_path = out_dir / "IndustryDetail_groupTotals.csv"
    _write_csv(totals_path, ["Industrial Group", "Total", "Blank Industry Detail", "Pct Blank"], totals_rows)

    # Console summary
    total_records = sum(group_totals.values())
    total_blank = sum(blanks_by_group.values())
    print(f"Input: {in_path}")
    print(f"Total records: {total_records}")
    print(f"Blank Industry Detail: {total_blank} ({(total_blank / total_records * 100.0) if total_records else 0.0:.1f}%)")
    print(f"Wrote: {overall_path}")
    print(f"Wrote: {grouped_path}")
    print(f"Wrote: {totals_path}")

    top = max(1, int(args.top))
    print(f"\nTop {top} Industry Detail values (overall):")
    for detail, count in overall.most_common(top):
        print(f"- {detail} ({count})")

    print(f"\nTop {top} (Industrial Group, Industry Detail) combinations:")
    for (group, detail), count in by_group.most_common(top):
        print(f"- {group} | {detail} ({count})")


if __name__ == "__main__":
    main()

