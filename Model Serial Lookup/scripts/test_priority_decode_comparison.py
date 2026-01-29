#!/usr/bin/env python3
"""
Compare decode results between v14 and v16-priority-test.

Ensures that adding priority column doesn't change decode behavior.
"""

import sys
import csv
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from msl.decoder.io import load_serial_rules_csv
from msl.decoder.normalize import normalize_brand


def find_matching_rule(serial: str, brand: str, rules):
    """Find first matching rule."""
    import re

    brand_norm = normalize_brand(brand)

    for rule in rules:
        if normalize_brand(rule.brand) != brand_norm:
            continue

        if not rule.serial_regex:
            continue

        try:
            if re.match(rule.serial_regex, serial):
                return rule
        except re.error:
            continue

    return None


def decode_with_rules(serial: str, brand: str, rules):
    """Simple decode using rules."""
    rule = find_matching_rule(serial, brand, rules)

    if not rule:
        return None, "NO_MATCH"

    # Try to decode year
    date_fields = rule.date_fields
    year_field = date_fields.get('year', {})
    positions = year_field.get('positions', {})
    mapping = year_field.get('mapping', {})

    if not positions or not mapping:
        return rule.style_name, "NO_MAPPING"

    start = positions.get('start')
    end = positions.get('end')

    if start is None or end is None:
        return rule.style_name, "NO_POSITIONS"

    try:
        year_char = serial[start-1:end]
        year = mapping.get(year_char)
        if year:
            return rule.style_name, f"YEAR_{year}"
        else:
            return rule.style_name, f"CHAR_{year_char}_NOT_IN_MAP"
    except (IndexError, ValueError):
        return rule.style_name, "EXTRACT_ERROR"


def test_decode_comparison():
    """Compare v14 vs v16 decode results."""

    base_dir = Path(__file__).parent.parent

    print("=" * 80)
    print("TEST: Decode Comparison v14 vs v16-priority-test")
    print("=" * 80)
    print()

    # Load both rulesets
    v14_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v14' / 'SerialDecodeRule.csv'
    v16_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v16-priority-test' / 'SerialDecodeRule.csv'

    print("Loading rulesets...")
    v14_rules = load_serial_rules_csv(v14_path)
    v16_rules = load_serial_rules_csv(v16_path)
    print(f"  v14: {len(v14_rules)} rules")
    print(f"  v16: {len(v16_rules)} rules")
    print()

    # Load test serials from SDI
    sdi_path = base_dir / 'data' / 'equipment_exports' / '2026-01-25' / 'sdi_equipment_normalized.csv'

    print(f"Loading test data: {sdi_path.name}")

    test_serials = []

    # Try different encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(sdi_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    brand = row.get('Make', row.get('Brand', ''))
                    serial = row.get('SerialNumber', row.get('Serial', ''))

                    if brand and serial:
                        test_serials.append((brand, serial))

                    # Limit to first 500 for quick testing
                    if i >= 500:
                        break
            break
        except UnicodeDecodeError:
            if encoding == 'cp1252':
                raise
            continue

    print(f"  Loaded {len(test_serials)} test serials")
    print()

    # Test decoding
    print("Testing decode consistency...")
    print()

    differences = []
    v14_results = defaultdict(int)
    v16_results = defaultdict(int)

    for brand, serial in test_serials:
        v14_rule, v14_result = decode_with_rules(serial, brand, v14_rules)
        v16_rule, v16_result = decode_with_rules(serial, brand, v16_rules)

        v14_results[v14_result] += 1
        v16_results[v16_result] += 1

        if v14_result != v16_result or v14_rule != v16_rule:
            differences.append({
                'brand': brand,
                'serial': serial,
                'v14_rule': v14_rule,
                'v14_result': v14_result,
                'v16_rule': v16_rule,
                'v16_result': v16_result
            })

    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    print(f"Total serials tested: {len(test_serials)}")
    print(f"Differences found: {len(differences)}")
    print()

    if len(differences) == 0:
        print("✓ PERFECT MATCH - All decodes identical")
        print()
        print("Result distribution:")
        for result, count in sorted(v14_results.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {result}: {count}")

    else:
        print("✗ DIFFERENCES DETECTED")
        print()
        print("First 10 differences:")
        for i, diff in enumerate(differences[:10], 1):
            print(f"{i}. {diff['brand']} - {diff['serial']}")
            print(f"   v14: {diff['v14_rule']} → {diff['v14_result']}")
            print(f"   v16: {diff['v16_rule']} → {diff['v16_result']}")
            print()

        print("⚠️  This might be expected if you reordered rules!")
        print("   v16 should have BETTER accuracy due to proper ordering")

    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()

    if len(differences) == 0:
        print("✓ PASSED - No decode changes detected")
        print("  Adding priority column did not break anything")
    else:
        print(f"⚠️  {len(differences)} decode differences found")
        print("  This is EXPECTED if rule ordering changed")
        print("  Review differences above to ensure they're improvements")

    print()
    print("Next steps:")
    print("1. If results look good, update SerialRule class to use priority")
    print("2. Implement priority-based sorting in decoder")
    print("3. Test full decode run on SDI equipment")


if __name__ == '__main__':
    test_decode_comparison()
