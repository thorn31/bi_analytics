#!/usr/bin/env python3
"""
Compare v14 vs v15 Trane rule performance on SDI equipment.

Shows the impact of reordering rules.
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_rules(rules_path: Path) -> List[Dict[str, Any]]:
    """Load rules from CSV."""
    rules = []
    with open(rules_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('date_fields'):
                try:
                    row['date_fields_parsed'] = json.loads(row['date_fields'])
                except json.JSONDecodeError:
                    row['date_fields_parsed'] = {}
            rules.append(row)
    return rules


def load_sdi_equipment(sdi_path: Path) -> List[Dict[str, Any]]:
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


def find_matching_rule(serial: str, brand_rules: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Find first matching rule for a serial."""
    for rule in brand_rules:
        regex = rule.get('serial_regex', '')
        if regex:
            try:
                if re.match(regex, serial):
                    return rule
            except re.error:
                continue
    return None


def decode_year(serial: str, rule: Dict[str, Any]) -> Optional[int]:
    """Decode year from serial using rule."""
    date_fields = rule.get('date_fields_parsed', {})
    year_field = date_fields.get('year', {})

    positions = year_field.get('positions', {})
    mapping = year_field.get('mapping', {})

    if not positions or not mapping:
        return None

    start = positions.get('start')
    end = positions.get('end')

    if start is None or end is None:
        return None

    try:
        year_char = serial[start-1:end]
        return int(mapping.get(year_char)) if year_char in mapping else None
    except (IndexError, ValueError):
        return None


def test_ruleset(rules: List[Dict[str, Any]], sdi_equipment: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Test ruleset against SDI equipment."""

    # Filter to Trane rules
    trane_rules = [r for r in rules if r['brand'].upper() == 'TRANE']

    # Test each Trane equipment
    results = {
        'total': 0,
        'matched_rule': 0,
        'decoded': 0,
        'correct': 0,
        'incorrect': 0,
        'by_rule': {}
    }

    for equipment in sdi_equipment:
        brand = equipment.get('Make', equipment.get('Brand', ''))
        if brand.upper() != 'TRANE':
            continue

        serial = equipment.get('SerialNumber', equipment.get('Serial', ''))
        if not serial:
            continue

        # Get known year
        known_year = None
        for col in ['KnownManufactureYear', 'ManufactureYear']:
            if col in equipment and equipment[col]:
                try:
                    known_year = int(equipment[col])
                    if 1950 <= known_year <= 2030:
                        break
                except (ValueError, TypeError):
                    continue

        if not known_year:
            continue

        results['total'] += 1

        # Find matching rule
        rule = find_matching_rule(serial, trane_rules)
        if not rule:
            continue

        results['matched_rule'] += 1
        rule_name = rule['style_name']

        if rule_name not in results['by_rule']:
            results['by_rule'][rule_name] = {
                'matched': 0,
                'decoded': 0,
                'correct': 0,
                'incorrect': 0
            }

        results['by_rule'][rule_name]['matched'] += 1

        # Try to decode
        decoded_year = decode_year(serial, rule)
        if decoded_year:
            results['decoded'] += 1
            results['by_rule'][rule_name]['decoded'] += 1

            if decoded_year == known_year:
                results['correct'] += 1
                results['by_rule'][rule_name]['correct'] += 1
            else:
                results['incorrect'] += 1
                results['by_rule'][rule_name]['incorrect'] += 1

    return results


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent.parent

    v14_rules_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v14' / 'SerialDecodeRule.csv'
    v15_rules_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v15-trane-reordered' / 'SerialDecodeRule.csv'
    sdi_path = base_dir / 'data' / 'equipment_exports' / '2026-01-25' / 'sdi_equipment_normalized.csv'

    print("=" * 80)
    print("V14 vs V15 TRANE RULE COMPARISON")
    print("=" * 80)
    print()

    print("Loading data...")
    v14_rules = load_rules(v14_rules_path)
    v15_rules = load_rules(v15_rules_path)
    sdi_equipment = load_sdi_equipment(sdi_path)

    print(f"  V14 rules: {len([r for r in v14_rules if r['brand'].upper() == 'TRANE'])} Trane rules")
    print(f"  V15 rules: {len([r for r in v15_rules if r['brand'].upper() == 'TRANE'])} Trane rules")
    print(f"  SDI equipment: {len([e for e in sdi_equipment if e.get('Make', '').upper() == 'TRANE'])} Trane units")
    print()

    print("Testing V14...")
    v14_results = test_ruleset(v14_rules, sdi_equipment)

    print("Testing V15...")
    v15_results = test_ruleset(v15_rules, sdi_equipment)

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    print(f"{'Metric':<30} {'V14':>10} {'V15':>10} {'Improvement':>12}")
    print("-" * 80)
    print(f"{'Total Trane equipment':<30} {v14_results['total']:>10} {v15_results['total']:>10} {' ':>12}")
    print(f"{'Matched a rule':<30} {v14_results['matched_rule']:>10} {v15_results['matched_rule']:>10} {'+'+str(v15_results['matched_rule']-v14_results['matched_rule']):>12}")
    print(f"{'Decoded year':<30} {v14_results['decoded']:>10} {v15_results['decoded']:>10} {'+'+str(v15_results['decoded']-v14_results['decoded']):>12}")
    print(f"{'Correct year':<30} {v14_results['correct']:>10} {v15_results['correct']:>10} {'+'+str(v15_results['correct']-v14_results['correct']):>12}")
    print(f"{'Incorrect year':<30} {v14_results['incorrect']:>10} {v15_results['incorrect']:>10} {'+'+str(v15_results['incorrect']-v14_results['incorrect']):>12}")
    print()

    if v14_results['decoded'] > 0:
        v14_accuracy = v14_results['correct'] / v14_results['decoded'] * 100
    else:
        v14_accuracy = 0

    if v15_results['decoded'] > 0:
        v15_accuracy = v15_results['correct'] / v15_results['decoded'] * 100
    else:
        v15_accuracy = 0

    print(f"{'Accuracy':<30} {v14_accuracy:>9.1f}% {v15_accuracy:>9.1f}% {'+'+str(v15_accuracy-v14_accuracy)+'%':>12}")
    print()

    print("=" * 80)
    print("TOP RULES IN V15 (by matches)")
    print("=" * 80)
    print()

    sorted_rules = sorted(v15_results['by_rule'].items(),
                         key=lambda x: x[1]['matched'],
                         reverse=True)

    for rule_name, stats in sorted_rules[:10]:
        if stats['matched'] > 0:
            accuracy = (stats['correct'] / stats['decoded'] * 100) if stats['decoded'] > 0 else 0
            print(f"{rule_name[:50]:<50}")
            print(f"  Matched: {stats['matched']:>4}  Decoded: {stats['decoded']:>4}  "
                  f"Correct: {stats['correct']:>4}  Accuracy: {accuracy:>5.1f}%")

    print()
    print("=" * 80)
    print("IMPACT SUMMARY")
    print("=" * 80)
    print()

    improvement = v15_results['correct'] - v14_results['correct']

    if improvement > 0:
        print(f"✅ SUCCESS! Reordering improved Trane decoding by {improvement} correct serials")
        print(f"   V14: {v14_results['correct']}/{v14_results['total']} ({v14_results['correct']/v14_results['total']*100:.1f}%)")
        print(f"   V15: {v15_results['correct']}/{v15_results['total']} ({v15_results['correct']/v15_results['total']*100:.1f}%)")
    else:
        print(f"⚠️  No improvement detected")


if __name__ == '__main__':
    main()
