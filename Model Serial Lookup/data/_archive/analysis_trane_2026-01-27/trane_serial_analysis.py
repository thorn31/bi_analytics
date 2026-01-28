"""Analyze Trane serial patterns to understand decoding failures."""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
import re
from pathlib import Path

def load_baseline_data(path: Path) -> list[dict]:
    """Load the baseline decoder output."""
    with path.open('r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def analyze_trane_patterns():
    """Analyze Trane serial patterns by equipment type and year."""
    path = Path("data/reports/phase3-baseline-2026-01-26T055846+0000/baseline_decoder_output.csv")
    rows = load_baseline_data(path)

    # Filter for Trane only
    trane = [r for r in rows if r.get('DetectedBrand') == 'TRANE']

    print(f"Total Trane records: {len(trane)}")
    known_year_count = sum(1 for r in trane if r.get('KnownManufactureYear', '').strip())
    decoded_year_count = sum(1 for r in trane if r.get('ManufactureYear', '').strip())
    print(f"Records with known year: {known_year_count}")
    print(f"Records with decoded year: {decoded_year_count}")

    # Analyze by serial length
    serial_lengths = Counter()
    for r in trane:
        serial = r.get('SerialNumber', '').strip()
        if serial:
            serial_lengths[len(serial)] += 1

    print("\n=== Serial Length Distribution ===")
    for length in sorted(serial_lengths.keys()):
        print(f"{length}: {serial_lengths[length]}")

    # Analyze by equipment type
    equipment_types = Counter(r.get('EquipmentType', '').strip() for r in trane)
    print("\n=== Equipment Type Distribution ===")
    for eq_type, count in equipment_types.most_common():
        if eq_type:
            print(f"{eq_type}: {count}")

    # Focus on records with both known and decoded years
    comparable = []
    for r in trane:
        known = r.get('KnownManufactureYear', '').strip()
        decoded = r.get('ManufactureYear', '').strip()
        if known and decoded:
            try:
                # Handle floats like "2015.0"
                known_int = int(float(known))
                decoded_int = int(float(decoded))
                r['_known_int'] = known_int
                r['_decoded_int'] = decoded_int
                r['_correct'] = (known_int == decoded_int)
                comparable.append(r)
            except ValueError:
                pass

    total_correct = sum(1 for r in comparable if r['_correct'])
    total_comparable = len(comparable)
    accuracy_pct = (total_correct / total_comparable * 100) if total_comparable > 0 else 0

    print(f"\n=== Overall Accuracy ===")
    print(f"Comparable records: {total_comparable}")
    print(f"Correct: {total_correct}")
    print(f"Wrong: {total_comparable - total_correct}")
    print(f"Accuracy: {accuracy_pct:.1f}%")

    # Analyze by serial length
    print(f"\n=== Accuracy by Serial Length ===")
    by_length = defaultdict(lambda: {'correct': 0, 'total': 0})
    for r in comparable:
        serial = r.get('SerialNumber', '').strip()
        if serial:
            length = len(serial)
            by_length[length]['total'] += 1
            if r['_correct']:
                by_length[length]['correct'] += 1

    for length in sorted(by_length.keys()):
        stats = by_length[length]
        acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"Length {length}: {stats['correct']}/{stats['total']} ({acc:.1f}%)")

    # Analyze by equipment type
    print(f"\n=== Accuracy by Equipment Type ===")
    by_equip = defaultdict(lambda: {'correct': 0, 'total': 0})
    for r in comparable:
        eq_type = r.get('EquipmentType', '').strip()
        if eq_type:
            by_equip[eq_type]['total'] += 1
            if r['_correct']:
                by_equip[eq_type]['correct'] += 1

    for eq_type in sorted(by_equip.keys(), key=lambda x: by_equip[x]['total'], reverse=True):
        stats = by_equip[eq_type]
        acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{eq_type}: {stats['correct']}/{stats['total']} ({acc:.1f}%)")

    # Analyze by matched style
    print(f"\n=== Accuracy by Matched Style ===")
    by_style = defaultdict(lambda: {'correct': 0, 'total': 0})
    for r in comparable:
        style = r.get('MatchedSerialStyle', '').strip()
        if style:
            by_style[style]['total'] += 1
            if r['_correct']:
                by_style[style]['correct'] += 1

    for style in sorted(by_style.keys(), key=lambda x: by_style[x]['total'], reverse=True):
        stats = by_style[style]
        acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{style}: {stats['correct']}/{stats['total']} ({acc:.1f}%)")

    # Deep dive: 10-digit serials
    print("\n=== 10-Digit Serial Analysis ===")
    ten_digit = [r for r in comparable if len(r.get('SerialNumber', '').strip()) == 10]
    ten_digit_correct = sum(1 for r in ten_digit if r['_correct'])
    print(f"Total 10-digit serials: {len(ten_digit)}")
    print(f"Correct: {ten_digit_correct}")
    print(f"Wrong: {len(ten_digit) - ten_digit_correct}")
    if ten_digit:
        print(f"Accuracy: {ten_digit_correct / len(ten_digit) * 100:.1f}%")

    # Sample wrong predictions
    wrong_10 = [r for r in ten_digit if not r['_correct']]
    print("\n=== Sample Wrong Predictions (10-digit) ===")
    for r in wrong_10[:20]:
        serial = r.get('SerialNumber', '').strip()
        style = r.get('MatchedSerialStyle', '').strip()
        eq_type = r.get('EquipmentType', '').strip()
        print(f"Serial: {serial}")
        print(f"  Known: {r['_known_int']}, Decoded: {r['_decoded_int']}")
        print(f"  Style: {style}")
        print(f"  Equipment: {eq_type}")
        print()

    # Pattern analysis: what prefixes exist?
    print("\n=== 10-Digit Serial Prefix Patterns ===")
    prefix_year_counts = defaultdict(Counter)
    for r in ten_digit:
        serial = r.get('SerialNumber', '').strip()
        if serial:
            prefix2 = serial[:2]
            prefix3 = serial[:3]
            known = r['_known_int']
            prefix_year_counts['2-digit'][prefix2] += 1
            prefix_year_counts['3-digit'][prefix3] += 1

    print("2-digit prefixes (top 20):")
    for prefix, count in prefix_year_counts['2-digit'].most_common(20):
        # Get years for this prefix
        years = [r['_known_int'] for r in ten_digit if r.get('SerialNumber', '').strip()[:2] == prefix]
        year_counts = Counter(years)
        print(f"  {prefix}: {count} total - years: {dict(year_counts.most_common(5))}")

    print("\n3-digit prefixes (top 20):")
    for prefix, count in prefix_year_counts['3-digit'].most_common(20):
        years = [r['_known_int'] for r in ten_digit if r.get('SerialNumber', '').strip()[:3] == prefix]
        year_counts = Counter(years)
        print(f"  {prefix}: {count} total - years: {dict(year_counts.most_common(5))}")

    # Equipment type correlation with errors
    print("\n=== Equipment Type vs Error Patterns ===")
    wrong_all = [r for r in comparable if not r['_correct']]
    print(f"Total wrong predictions: {len(wrong_all)}")

    wrong_by_equip = Counter(r.get('EquipmentType', '').strip() for r in wrong_all)
    print("\nBy Equipment Type:")
    for eq_type, count in wrong_by_equip.most_common():
        if eq_type:
            print(f"  {eq_type}: {count}")

    wrong_by_style = Counter(r.get('MatchedSerialStyle', '').strip() for r in wrong_all)
    print("\nBy Matched Style:")
    for style, count in wrong_by_style.most_common():
        if style:
            print(f"  {style}: {count}")

    # Save detailed report
    report_path = Path("data/analysis/trane_patterns_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open('w') as f:
        f.write("# Trane Serial Pattern Analysis\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Total Trane records: {len(trane)}\n")
        f.write(f"- Records with known year: {known_year_count}\n")
        f.write(f"- Overall accuracy: {total_correct}/{total_comparable} ({accuracy_pct:.1f}%)\n\n")

        f.write("## Key Findings\n\n")
        f.write("### Serial Length Distribution\n\n")
        for length in sorted(serial_lengths.keys()):
            f.write(f"- Length {length}: {serial_lengths[length]}\n")
        f.write("\n")

        f.write("### Accuracy by Serial Length\n\n")
        for length in sorted(by_length.keys()):
            stats = by_length[length]
            acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            f.write(f"- Length {length}: {stats['correct']}/{stats['total']} ({acc:.1f}%)\n")
        f.write("\n")

        f.write("### Accuracy by Equipment Type\n\n")
        for eq_type in sorted(by_equip.keys(), key=lambda x: by_equip[x]['total'], reverse=True):
            stats = by_equip[eq_type]
            acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            f.write(f"- {eq_type}: {stats['correct']}/{stats['total']} ({acc:.1f}%)\n")
        f.write("\n")

        f.write("### Accuracy by Matched Style\n\n")
        for style in sorted(by_style.keys(), key=lambda x: by_style[x]['total'], reverse=True):
            stats = by_style[style]
            acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            f.write(f"- {style}: {stats['correct']}/{stats['total']} ({acc:.1f}%)\n")
        f.write("\n")

        f.write("## 10-Digit Serial Analysis\n\n")
        f.write(f"- Total 10-digit serials: {len(ten_digit)}\n")
        f.write(f"- Correct: {ten_digit_correct}\n")
        f.write(f"- Wrong: {len(ten_digit) - ten_digit_correct}\n")
        if ten_digit:
            f.write(f"- Accuracy: {ten_digit_correct / len(ten_digit) * 100:.1f}%\n\n")

        f.write("### Sample Wrong Predictions\n\n")
        for r in wrong_10[:20]:
            serial = r.get('SerialNumber', '').strip()
            style = r.get('MatchedSerialStyle', '').strip()
            eq_type = r.get('EquipmentType', '').strip()
            f.write(f"- **{serial}**: Known {r['_known_int']}, Decoded {r['_decoded_int']} ")
            f.write(f"(Style: {style}, Equipment: {eq_type})\n")
        f.write("\n")

        f.write("### Prefix Patterns (2-digit)\n\n")
        for prefix, count in prefix_year_counts['2-digit'].most_common(20):
            years = [r['_known_int'] for r in ten_digit if r.get('SerialNumber', '').strip()[:2] == prefix]
            year_counts = Counter(years)
            f.write(f"- **{prefix}**: {count} total - years: {dict(year_counts.most_common(5))}\n")
        f.write("\n")

        f.write("## Error Analysis\n\n")
        f.write(f"Total wrong predictions: {len(wrong_all)}\n\n")
        f.write("### By Equipment Type\n\n")
        for eq_type, count in wrong_by_equip.most_common():
            if eq_type:
                f.write(f"- {eq_type}: {count}\n")
        f.write("\n")
        f.write("### By Matched Style\n\n")
        for style, count in wrong_by_style.most_common():
            if style:
                f.write(f"- {style}: {count}\n")
        f.write("\n")

    print(f"\nReport saved to: {report_path}")
    return comparable

if __name__ == "__main__":
    analyze_trane_patterns()
# NOTE: Archived one-off analysis artifact (moved 2026-01-28).
