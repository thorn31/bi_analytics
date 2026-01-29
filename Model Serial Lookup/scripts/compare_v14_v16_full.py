#!/usr/bin/env python3
"""
Compare v14 vs v16-priority-test on ALL brands.

Shows total impact of priority system across entire SDI dataset.
"""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from msl.decoder.io import load_serial_rules_csv, sort_rules_by_priority
from msl.decoder.normalize import normalize_brand


def load_sdi_equipment(sdi_path: Path):
    """Load SDI equipment data."""
    equipment = []
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(sdi_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    equipment.append(row)
            break
        except UnicodeDecodeError:
            if encoding == 'cp1252':
                raise
            continue
    return equipment


def find_matching_rule(serial: str, brand: str, rules):
    """Find first matching rule."""
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


def decode_year_with_rule(serial: str, rule):
    """Decode year using rule."""
    if not rule:
        return None, "NO_RULE"

    date_fields = rule.date_fields or {}
    year_field = date_fields.get('year', {})
    positions = year_field.get('positions', {})
    mapping = year_field.get('mapping', {})

    if not positions:
        return None, "NO_POSITIONS"

    if not mapping:
        return None, "NO_MAPPING"

    start = positions.get('start')
    end = positions.get('end')

    if start is None or end is None:
        return None, "BAD_POSITIONS"

    try:
        year_char = serial[start-1:end]
        year = mapping.get(year_char)
        if year:
            return int(year), "SUCCESS"
        else:
            return None, "CHAR_NOT_IN_MAP"
    except (IndexError, ValueError, TypeError):
        return None, "EXTRACT_ERROR"


def get_known_year(equipment):
    """Get known year from equipment record."""
    for col in ['KnownManufactureYear', 'ManufactureYear']:
        if col in equipment and equipment[col]:
            try:
                year = int(equipment[col])
                if 1950 <= year <= 2030:
                    return year
            except (ValueError, TypeError):
                continue
    return None


def compare_versions():
    """Compare v14 vs v16 across all brands."""

    base_dir = Path(__file__).parent.parent

    print("=" * 80)
    print("V14 vs V16-PRIORITY-TEST FULL COMPARISON")
    print("=" * 80)
    print()

    # Load rulesets
    v14_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v14' / 'SerialDecodeRule.csv'
    v16_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v16-priority-test' / 'SerialDecodeRule.csv'

    print("Loading rulesets...")
    v14_rules = load_serial_rules_csv(v14_path)
    print(f"  v14: {len(v14_rules)} rules (unsorted)")

    v16_rules = load_serial_rules_csv(v16_path)
    v16_rules = sort_rules_by_priority(v16_rules)
    print(f"  v16: {len(v16_rules)} rules (sorted by priority)")
    print()

    # Load SDI equipment
    sdi_path = base_dir / 'data' / 'equipment_exports' / '2026-01-25' / 'sdi_equipment_normalized.csv'
    print(f"Loading SDI equipment: {sdi_path.name}")
    sdi_equipment = load_sdi_equipment(sdi_path)
    print(f"  Loaded {len(sdi_equipment)} equipment records")
    print()

    # Process each record
    print("Testing decode on all equipment...")
    print()

    v14_stats = defaultdict(lambda: {'total': 0, 'matched': 0, 'decoded': 0, 'correct': 0, 'incorrect': 0})
    v16_stats = defaultdict(lambda: {'total': 0, 'matched': 0, 'decoded': 0, 'correct': 0, 'incorrect': 0})

    v14_overall = {'total': 0, 'matched': 0, 'decoded': 0, 'correct': 0, 'incorrect': 0}
    v16_overall = {'total': 0, 'matched': 0, 'decoded': 0, 'correct': 0, 'incorrect': 0}

    for equipment in sdi_equipment:
        brand = equipment.get('Make', equipment.get('Brand', ''))
        serial = equipment.get('SerialNumber', equipment.get('Serial', ''))
        known_year = get_known_year(equipment)

        if not brand or not serial or not known_year:
            continue

        brand_norm = normalize_brand(brand)

        # Test v14
        v14_rule = find_matching_rule(serial, brand, v14_rules)
        v14_year, v14_status = decode_year_with_rule(serial, v14_rule)

        v14_stats[brand_norm]['total'] += 1
        v14_overall['total'] += 1

        if v14_rule:
            v14_stats[brand_norm]['matched'] += 1
            v14_overall['matched'] += 1

        if v14_year:
            v14_stats[brand_norm]['decoded'] += 1
            v14_overall['decoded'] += 1

            if v14_year == known_year:
                v14_stats[brand_norm]['correct'] += 1
                v14_overall['correct'] += 1
            else:
                v14_stats[brand_norm]['incorrect'] += 1
                v14_overall['incorrect'] += 1

        # Test v16
        v16_rule = find_matching_rule(serial, brand, v16_rules)
        v16_year, v16_status = decode_year_with_rule(serial, v16_rule)

        v16_stats[brand_norm]['total'] += 1
        v16_overall['total'] += 1

        if v16_rule:
            v16_stats[brand_norm]['matched'] += 1
            v16_overall['matched'] += 1

        if v16_year:
            v16_stats[brand_norm]['decoded'] += 1
            v16_overall['decoded'] += 1

            if v16_year == known_year:
                v16_stats[brand_norm]['correct'] += 1
                v16_overall['correct'] += 1
            else:
                v16_stats[brand_norm]['incorrect'] += 1
                v16_overall['incorrect'] += 1

    # Print results
    print("=" * 80)
    print("OVERALL RESULTS")
    print("=" * 80)
    print()

    print(f"{'Metric':<30} {'v14':>12} {'v16':>12} {'Change':>12}")
    print("-" * 80)
    print(f"{'Total equipment tested':<30} {v14_overall['total']:>12} {v16_overall['total']:>12} {v16_overall['total']-v14_overall['total']:>12}")
    print(f"{'Matched a rule':<30} {v14_overall['matched']:>12} {v16_overall['matched']:>12} {v16_overall['matched']-v14_overall['matched']:>12}")
    print(f"{'Decoded year':<30} {v14_overall['decoded']:>12} {v16_overall['decoded']:>12} {v16_overall['decoded']-v14_overall['decoded']:>12}")
    print(f"{'Correct year':<30} {v14_overall['correct']:>12} {v16_overall['correct']:>12} {v16_overall['correct']-v14_overall['correct']:>12}")
    print(f"{'Incorrect year':<30} {v14_overall['incorrect']:>12} {v16_overall['incorrect']:>12} {v16_overall['incorrect']-v14_overall['incorrect']:>12}")
    print()

    v14_acc = (v14_overall['correct'] / v14_overall['total'] * 100) if v14_overall['total'] > 0 else 0
    v16_acc = (v16_overall['correct'] / v16_overall['total'] * 100) if v16_overall['total'] > 0 else 0

    print(f"{'Accuracy (correct/total)':<30} {v14_acc:>11.1f}% {v16_acc:>11.1f}% {v16_acc-v14_acc:>11.1f}%")
    print()

    # By brand
    print("=" * 80)
    print("RESULTS BY BRAND (Top 20 with changes)")
    print("=" * 80)
    print()

    brand_improvements = []
    for brand in set(list(v14_stats.keys()) + list(v16_stats.keys())):
        v14 = v14_stats[brand]
        v16 = v16_stats[brand]

        improvement = v16['correct'] - v14['correct']
        degradation = v16['incorrect'] - v14['incorrect']

        if improvement != 0 or degradation != 0:
            brand_improvements.append({
                'brand': brand,
                'v14_correct': v14['correct'],
                'v16_correct': v16['correct'],
                'improvement': improvement,
                'v14_total': v14['total'],
                'v16_total': v16['total'],
                'v14_decoded': v14['decoded'],
                'v16_decoded': v16['decoded']
            })

    brand_improvements.sort(key=lambda x: x['improvement'], reverse=True)

    print(f"{'Brand':<15} {'v14 Correct':>12} {'v16 Correct':>12} {'Change':>12} {'v14 Decoded':>12} {'v16 Decoded':>12}")
    print("-" * 95)

    for item in brand_improvements[:20]:
        print(f"{item['brand']:<15} {item['v14_correct']:>12} {item['v16_correct']:>12} "
              f"{'+' if item['improvement'] >= 0 else ''}{item['improvement']:>11} "
              f"{item['v14_decoded']:>12} {item['v16_decoded']:>12}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    improvement = v16_overall['correct'] - v14_overall['correct']

    if improvement > 0:
        print(f"✅ SUCCESS! Priority system improved decoding by {improvement} correct years")
        print(f"   v14: {v14_overall['correct']:,}/{v14_overall['total']:,} ({v14_acc:.1f}%)")
        print(f"   v16: {v16_overall['correct']:,}/{v16_overall['total']:,} ({v16_acc:.1f}%)")
    elif improvement < 0:
        print(f"⚠️  REGRESSION! Priority system decreased accuracy by {abs(improvement)} correct years")
    else:
        print(f"➖ NO CHANGE - Priority system had no impact on overall accuracy")

    print()
    print(f"Brands with improvements: {len([x for x in brand_improvements if x['improvement'] > 0])}")
    print(f"Brands with degradations: {len([x for x in brand_improvements if x['improvement'] < 0])}")


if __name__ == '__main__':
    compare_versions()
