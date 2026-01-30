#!/usr/bin/env python3
"""
Check Trane rule priorities to see if priority system is working.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from msl.decoder.io import load_serial_rules_csv, sort_rules_by_priority, calculate_rule_priority
from msl.decoder.normalize import normalize_brand


def check_trane_priorities():
    """Check Trane rule priorities."""

    base_dir = Path(__file__).parent.parent

    # Load current ruleset
    current_txt = base_dir / 'data' / 'rules_normalized' / 'CURRENT.txt'
    current_name = current_txt.read_text().strip()
    current_path = base_dir / 'data' / 'rules_normalized' / current_name / 'SerialDecodeRule.csv'

    print("=" * 80)
    print("TRANE RULE PRIORITY CHECK")
    print("=" * 80)
    print()

    print(f"Loading rules from: {current_name}")
    rules = load_serial_rules_csv(current_path)

    # Get Trane rules
    trane_rules = [r for r in rules if normalize_brand(r.brand) == 'TRANE' and r.rule_type == 'decode']
    print(f"Found {len(trane_rules)} Trane decode rules")
    print()

    # Sort by priority
    sorted_rules = sort_rules_by_priority(trane_rules)

    print("Trane rules in MATCH ORDER (after priority sorting):")
    print()
    print(f"{'Order':<6} {'Priority':<10} {'Has Map':<10} {'Style Name':<60}")
    print("-" * 100)

    for i, rule in enumerate(sorted_rules, 1):
        # Calculate priority
        if rule.priority is not None:
            priority = rule.priority
            priority_str = str(priority)
        else:
            priority = calculate_rule_priority(rule)
            priority_str = f"{priority} (auto)"

        # Check if has mapping
        date_fields = rule.date_fields or {}
        year_field = date_fields.get('year', {})
        has_mapping = bool(year_field.get('mapping'))

        print(f"{i:<6} {priority_str:<10} {'YES' if has_mapping else 'NO':<10} {rule.style_name[:60]}")

    print()
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()

    # Check if Legacy Letter Code is first
    legacy_rule = sorted_rules[0]
    if 'legacy' in legacy_rule.style_name.lower():
        print("✅ GOOD: Legacy Letter Code rule is first (highest priority)")
    else:
        print(f"❌ BAD: First rule is '{legacy_rule.style_name}', not Legacy Letter Code")
        print("   Priority system may not be working correctly!")

    print()

    # Check if rules with mappings come before rules without
    first_no_map_idx = None
    last_map_idx = None

    for i, rule in enumerate(sorted_rules):
        date_fields = rule.date_fields or {}
        year_field = date_fields.get('year', {})
        has_mapping = bool(year_field.get('mapping'))

        if has_mapping:
            last_map_idx = i
        else:
            if first_no_map_idx is None:
                first_no_map_idx = i

    if last_map_idx is not None and first_no_map_idx is not None:
        if first_no_map_idx < last_map_idx:
            print(f"⚠️  WARNING: Rules without mappings start at position {first_no_map_idx + 1}")
            print(f"            but rules WITH mappings exist until position {last_map_idx + 1}")
            print("            This means some rules with mappings are checked AFTER rules without mappings!")
            print()
            print("  This is OK if the rules without mappings are more specific (longer regex).")
            print("  Let's check the regex lengths:")
            print()

            # Show the problematic rules
            for i in range(first_no_map_idx, min(last_map_idx + 1, len(sorted_rules))):
                rule = sorted_rules[i]
                date_fields = rule.date_fields or {}
                year_field = date_fields.get('year', {})
                has_mapping = bool(year_field.get('mapping'))
                regex_len = len(rule.serial_regex or "")

                priority = rule.priority if rule.priority is not None else calculate_rule_priority(rule)

                print(f"  {i+1:3}. Priority {priority:>5} | Regex len {regex_len:>3} | {'MAP' if has_mapping else 'NO '} | {rule.style_name[:50]}")

    print()


if __name__ == '__main__':
    check_trane_priorities()
