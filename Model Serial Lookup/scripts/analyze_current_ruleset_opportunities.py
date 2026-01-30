#!/usr/bin/env python3
"""
Analyze current ruleset to identify improvement opportunities.

Identifies:
1. Rules with duplicate/overlapping regex patterns (potential ordering issues)
2. Rules with positions but no mappings (opportunity to add mappings)
3. Decade ambiguity issues that could be improved
4. Brands with low rule coverage vs SDI equipment count
"""

import sys
import re
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from msl.decoder.io import load_serial_rules_csv
from msl.decoder.normalize import normalize_brand


def load_sdi_equipment(sdi_path: Path):
    """Load SDI equipment data."""
    import csv
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


def analyze_ruleset():
    """Analyze current ruleset for improvement opportunities."""

    base_dir = Path(__file__).parent.parent

    # Load current ruleset
    current_txt = base_dir / 'data' / 'rules_normalized' / 'CURRENT.txt'
    current_name = current_txt.read_text().strip()
    current_path = base_dir / 'data' / 'rules_normalized' / current_name / 'SerialDecodeRule.csv'

    print("=" * 80)
    print(f"RULESET ANALYSIS: {current_name}")
    print("=" * 80)
    print()

    print(f"Loading rules from: {current_name}")
    rules = load_serial_rules_csv(current_path)
    print(f"  Loaded {len(rules)} rules")
    print()

    # Filter to decode rules only
    decode_rules = [r for r in rules if r.rule_type == 'decode']
    print(f"  {len(decode_rules)} decode rules (excluding guidance)")
    print()

    # Load SDI equipment
    sdi_path = base_dir / 'data' / 'equipment_exports' / '2026-01-25' / 'sdi_equipment_normalized.csv'
    print(f"Loading SDI equipment data...")
    sdi_equipment = load_sdi_equipment(sdi_path)
    print(f"  Loaded {len(sdi_equipment)} equipment records")
    print()

    # Count equipment by brand
    brand_equipment_count = defaultdict(int)
    for eq in sdi_equipment:
        brand = eq.get('Make', eq.get('Brand', ''))
        if brand:
            brand_norm = normalize_brand(brand)
            brand_equipment_count[brand_norm] += 1

    # Organize rules by brand
    rules_by_brand = defaultdict(list)
    for rule in decode_rules:
        brand_norm = normalize_brand(rule.brand)
        rules_by_brand[brand_norm].append(rule)

    # === OPPORTUNITY 1: Rules with positions but no mappings ===
    print("=" * 80)
    print("OPPORTUNITY 1: Add Mappings to Existing Rules")
    print("=" * 80)
    print()

    no_mapping_rules = []
    for rule in decode_rules:
        date_fields = rule.date_fields or {}
        year_field = date_fields.get('year', {})

        # Has positions but no mapping
        if year_field.get('positions') and not year_field.get('mapping'):
            brand_norm = normalize_brand(rule.brand)
            no_mapping_rules.append({
                'brand': rule.brand,
                'brand_norm': brand_norm,
                'style_name': rule.style_name,
                'has_regex': bool(rule.serial_regex),
                'sdi_count': brand_equipment_count.get(brand_norm, 0),
                'priority': rule.priority
            })

    no_mapping_rules.sort(key=lambda x: x['sdi_count'], reverse=True)

    print(f"Found {len(no_mapping_rules)} rules with positions but NO year mapping")
    print()
    print(f"{'Brand':<20} {'SDI Count':>12} {'Priority':>10} {'Style Name':<50}")
    print("-" * 100)

    for item in no_mapping_rules[:30]:
        priority_str = str(item['priority']) if item['priority'] is not None else 'AUTO'
        print(f"{item['brand']:<20} {item['sdi_count']:>12} {priority_str:>10} {item['style_name'][:50]}")

    print()

    # === OPPORTUNITY 2: Decade ambiguity ===
    print("=" * 80)
    print("OPPORTUNITY 2: Resolve Decade Ambiguity")
    print("=" * 80)
    print()

    ambiguous_rules = []
    for rule in decode_rules:
        decade_amb = rule.decade_ambiguity or {}
        if decade_amb.get('is_ambiguous'):
            brand_norm = normalize_brand(rule.brand)
            date_fields = rule.date_fields or {}
            year_field = date_fields.get('year', {})
            has_mapping = bool(year_field.get('mapping'))

            ambiguous_rules.append({
                'brand': rule.brand,
                'brand_norm': brand_norm,
                'style_name': rule.style_name,
                'has_mapping': has_mapping,
                'notes': decade_amb.get('notes', ''),
                'sdi_count': brand_equipment_count.get(brand_norm, 0),
            })

    ambiguous_rules.sort(key=lambda x: (x['has_mapping'], x['sdi_count']), reverse=True)

    print(f"Found {len(ambiguous_rules)} rules with decade ambiguity")
    print()
    print(f"{'Brand':<20} {'SDI Count':>12} {'Has Map':>10} {'Notes':<50}")
    print("-" * 100)

    for item in ambiguous_rules[:30]:
        has_map = 'YES' if item['has_mapping'] else 'NO'
        print(f"{item['brand']:<20} {item['sdi_count']:>12} {has_map:>10} {item['notes'][:50]}")

    print()

    # === OPPORTUNITY 3: Potential regex overlaps ===
    print("=" * 80)
    print("OPPORTUNITY 3: Check for Rule Ordering Issues (Regex Overlaps)")
    print("=" * 80)
    print()

    overlap_issues = []

    for brand_norm, brand_rules in rules_by_brand.items():
        if len(brand_rules) < 2:
            continue

        # Check each pair of rules for potential overlaps
        for i, rule1 in enumerate(brand_rules):
            for j, rule2 in enumerate(brand_rules[i+1:], start=i+1):
                if not rule1.serial_regex or not rule2.serial_regex:
                    continue

                # Simple overlap check: if one regex is a subset of another
                # (This is a heuristic - real overlap detection would need test cases)
                regex1_len = len(rule1.serial_regex)
                regex2_len = len(rule2.serial_regex)

                # Check if one has mapping and one doesn't
                df1 = rule1.date_fields or {}
                df2 = rule2.date_fields or {}
                has_map1 = bool(df1.get('year', {}).get('mapping'))
                has_map2 = bool(df2.get('year', {}).get('mapping'))

                # Flag if one has mapping but appears later in order
                if has_map2 and not has_map1:
                    overlap_issues.append({
                        'brand': rule1.brand,
                        'rule1_style': rule1.style_name,
                        'rule1_has_map': has_map1,
                        'rule1_priority': rule1.priority,
                        'rule2_style': rule2.style_name,
                        'rule2_has_map': has_map2,
                        'rule2_priority': rule2.priority,
                        'sdi_count': brand_equipment_count.get(brand_norm, 0)
                    })

    overlap_issues.sort(key=lambda x: x['sdi_count'], reverse=True)

    if overlap_issues:
        print(f"Found {len(overlap_issues)} potential ordering issues where rules WITH mappings come after rules WITHOUT")
        print()
        print(f"{'Brand':<20} {'SDI':>8} {'Rule 1 (no map)':<40} {'Rule 2 (has map)':<40}")
        print("-" * 120)

        for item in overlap_issues[:20]:
            print(f"{item['brand']:<20} {item['sdi_count']:>8} {item['rule1_style'][:40]:<40} {item['rule2_style'][:40]:<40}")
    else:
        print("✅ No obvious ordering issues detected (all brands have rules properly ordered)")

    print()

    # === OPPORTUNITY 4: Brands with high SDI count but few rules ===
    print("=" * 80)
    print("OPPORTUNITY 4: Brands Needing More Rules")
    print("=" * 80)
    print()

    brand_coverage = []
    for brand_norm, count in brand_equipment_count.items():
        rule_count = len(rules_by_brand.get(brand_norm, []))
        rules_with_mapping = sum(1 for r in rules_by_brand.get(brand_norm, [])
                                 if (r.date_fields or {}).get('year', {}).get('mapping'))

        if count > 10:  # Only brands with significant SDI presence
            brand_coverage.append({
                'brand': brand_norm,
                'sdi_count': count,
                'rule_count': rule_count,
                'rules_with_mapping': rules_with_mapping,
                'coverage_score': count / max(rule_count, 1)  # Higher = needs more rules
            })

    brand_coverage.sort(key=lambda x: x['coverage_score'], reverse=True)

    print(f"Top brands by SDI count with low rule coverage:")
    print()
    print(f"{'Brand':<20} {'SDI Count':>12} {'Rules':>8} {'w/ Map':>8} {'Coverage Score':>15}")
    print("-" * 80)

    for item in brand_coverage[:30]:
        print(f"{item['brand']:<20} {item['sdi_count']:>12} {item['rule_count']:>8} "
              f"{item['rules_with_mapping']:>8} {item['coverage_score']:>15.1f}")

    print()

    # === SUMMARY ===
    print("=" * 80)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    print()

    print(f"1. 📊 Add Mappings: {len(no_mapping_rules)} rules have positions but no mappings")
    print(f"   → Focus on high-SDI brands like: {', '.join([r['brand'] for r in no_mapping_rules[:5]])}")
    print()

    print(f"2. 📅 Resolve Decade Ambiguity: {len([r for r in ambiguous_rules if r['has_mapping']])} rules with mappings still ambiguous")
    print(f"   → Could improve accuracy by adding decade resolution logic")
    print()

    if overlap_issues:
        print(f"3. 🔧 Fix Ordering: {len(overlap_issues)} potential ordering issues detected")
        print(f"   → Review priority settings for affected brands")
    else:
        print(f"3. ✅ Ordering: Priority system appears to be working correctly")
    print()

    print(f"4. 🎯 Expand Coverage: {len([b for b in brand_coverage if b['rule_count'] < 3])} brands with <3 rules but significant SDI presence")
    print(f"   → Research opportunities for: {', '.join([b['brand'] for b in brand_coverage[:5]])}")
    print()

    print("=" * 80)
    print("Next Actions:")
    print("=" * 80)
    print()
    print("1. Run validation against SDI to see which brands have low accuracy")
    print("2. Add mappings from serial.json to high-priority rules")
    print("3. Research decade resolution strategies for ambiguous rules")
    print("4. Expand rules for high-SDI brands with low coverage")


if __name__ == '__main__':
    analyze_ruleset()
