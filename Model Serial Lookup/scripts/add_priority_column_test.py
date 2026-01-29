#!/usr/bin/env python3
"""
TEST MIGRATION: Add priority column to SerialDecodeRule.csv

Creates v16-priority-test to verify priority column doesn't break anything.
"""

import csv
import shutil
from pathlib import Path
from collections import defaultdict
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def add_priority_column(input_dir: Path, output_dir: Path) -> None:
    """Add priority column to SerialDecodeRule.csv."""

    input_csv = input_dir / "SerialDecodeRule.csv"
    output_csv = output_dir / "SerialDecodeRule.csv"

    if not input_csv.exists():
        print(f"ERROR: {input_csv} not found")
        sys.exit(1)

    print("=" * 80)
    print("ADDING PRIORITY COLUMN - TEST MIGRATION")
    print("=" * 80)
    print()
    print(f"Input:  {input_csv}")
    print(f"Output: {output_csv}")
    print()

    # Read all rules
    rules = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        original_fieldnames = reader.fieldnames

        for row in reader:
            rules.append(row)

    print(f"Loaded {len(rules)} rules")
    print(f"Original columns: {len(original_fieldnames)}")

    # Check if priority already exists
    if 'priority' in original_fieldnames:
        print("⚠️  WARNING: priority column already exists!")
        print("   Aborting to avoid overwriting.")
        sys.exit(1)

    # Create new fieldnames with priority after brand
    new_fieldnames = []
    for field in original_fieldnames:
        new_fieldnames.append(field)
        if field == 'brand':
            new_fieldnames.append('priority')

    print(f"New columns: {len(new_fieldnames)}")
    print(f"Added 'priority' after 'brand'")
    print()

    # Track brands and assign priorities
    brand_rule_order = defaultdict(list)
    for i, rule in enumerate(rules):
        brand = rule['brand']
        brand_rule_order[brand].append((i, rule))

    # Assign priorities
    # For McQuay: preserve current ordering with explicit priorities
    # For others: leave blank (will auto-calculate)

    mcquay_priority_counter = 10
    priority_assignments = {}

    print("Assigning priorities:")
    print("-" * 80)

    for brand, brand_rules in sorted(brand_rule_order.items()):
        if brand.upper() == 'MCQUAY':
            print(f"\n{brand} ({len(brand_rules)} rules) - EXPLICIT PRIORITIES:")
            for original_idx, rule in brand_rules:
                # Assign explicit priority to preserve order
                priority_assignments[original_idx] = mcquay_priority_counter
                print(f"  {mcquay_priority_counter:>3}: {rule['style_name'][:60]}")
                mcquay_priority_counter += 10
        else:
            # Leave priority blank for auto-calculation
            for original_idx, rule in brand_rules:
                priority_assignments[original_idx] = ""

    # Add priority to each rule
    for i, rule in enumerate(rules):
        rule['priority'] = priority_assignments.get(i, "")

    # Write output
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rules)

    print()
    print("=" * 80)
    print("MIGRATION COMPLETE")
    print("=" * 80)
    print(f"✓ Added priority column")
    print(f"✓ McQuay rules: {mcquay_priority_counter // 10 - 1} explicit priorities assigned")
    print(f"✓ Other brands: blank (auto-calculate)")
    print(f"✓ Output: {output_csv}")

    # Copy other files
    print()
    print("Copying other rule files...")
    for file in input_dir.glob("*.csv"):
        if file.name != "SerialDecodeRule.csv":
            shutil.copy(file, output_dir / file.name)
            print(f"  ✓ {file.name}")

    print()
    print("=" * 80)
    print("NEXT STEPS - VALIDATION")
    print("=" * 80)
    print()
    print("1. Verify the CSV loads without errors:")
    print("   python3 scripts/test_priority_loading.py")
    print()
    print("2. Compare decode results v14 vs v16-priority-test:")
    print("   python3 scripts/test_priority_decode_comparison.py")
    print()
    print("3. If tests pass, update CURRENT.txt:")
    print("   echo '2026-01-29-sdi-master-v16-priority-test' > data/rules_normalized/CURRENT.txt")


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent.parent

    input_dir = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v14'
    output_dir = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v16-priority-test'

    if not input_dir.exists():
        print(f"ERROR: Input directory not found: {input_dir}")
        sys.exit(1)

    if output_dir.exists():
        print(f"⚠️  WARNING: Output directory already exists: {output_dir}")
        response = input("Delete and recreate? (yes/no): ").strip().lower()
        if response == 'yes':
            shutil.rmtree(output_dir)
            print("  ✓ Deleted existing directory")
        else:
            print("  ✗ Aborting")
            sys.exit(0)

    add_priority_column(input_dir, output_dir)


if __name__ == '__main__':
    main()
