#!/usr/bin/env python3
"""
Proof of Concept: Reorder Trane rules to fix blocking issues.

Reorders Trane rules so that:
1. Rules with mappings come before rules without
2. More specific patterns come before broader patterns
3. Manual/researched rules come before generic styles
"""

import csv
import json
import re
from pathlib import Path
from typing import List, Dict, Any
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def calculate_regex_specificity(regex: str) -> int:
    """
    Calculate specificity score for a regex pattern.
    Higher score = more specific.
    """
    if not regex:
        return 0

    score = 0

    # Literal characters are most specific
    score += len(re.findall(r'[A-Z0-9](?![+*?])', regex))

    # Character classes are less specific
    score -= regex.count('[A-Z0-9')
    score -= regex.count('[A-Z]')
    score -= regex.count('\\d')

    # Wildcards/quantifiers reduce specificity
    score -= regex.count('+') * 2
    score -= regex.count('*') * 3
    score -= regex.count('{') * 1

    # Anchors add specificity
    score += regex.count('^')
    score += regex.count('$')

    # Shorter patterns with same elements are more specific
    # Penalize very broad patterns
    if '[A-Z0-9-]' in regex or '[A-Z0-9]' in regex:
        score -= 10

    return score


def has_year_mapping(rule: Dict[str, Any]) -> bool:
    """Check if rule has year mapping."""
    date_fields = rule.get('date_fields_parsed', {})
    year_field = date_fields.get('year', {})
    return bool(year_field.get('mapping', {}))


def is_manual_rule(rule: Dict[str, Any]) -> bool:
    """Check if rule is marked as manual/researched."""
    style_name = rule.get('style_name', '')
    return 'Manual' in style_name or 'manual' in style_name


def reorder_trane_rules(input_path: Path, output_path: Path) -> None:
    """Reorder Trane rules in the CSV file."""

    # Load all rules
    all_rules = []
    trane_rules = []

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            # Parse date_fields
            if row.get('date_fields'):
                try:
                    row['date_fields_parsed'] = json.loads(row['date_fields'])
                except json.JSONDecodeError:
                    row['date_fields_parsed'] = {}
            else:
                row['date_fields_parsed'] = {}

            if row['brand'].upper() == 'TRANE':
                trane_rules.append(row)
            else:
                all_rules.append(row)

    print(f"Found {len(trane_rules)} Trane rules")
    print(f"Found {len(all_rules)} non-Trane rules")
    print()

    # Score each Trane rule
    print("Scoring Trane rules...")
    for rule in trane_rules:
        regex = rule.get('serial_regex', '')

        # Calculate priority score (higher = should come first)
        priority = 0

        # 1. Manual rules get highest priority
        if is_manual_rule(rule):
            priority += 1000

        # 2. Rules with mappings get high priority
        if has_year_mapping(rule):
            priority += 500

        # 3. Add regex specificity
        priority += calculate_regex_specificity(regex)

        rule['_priority'] = priority
        rule['_specificity'] = calculate_regex_specificity(regex)
        rule['_has_mapping'] = has_year_mapping(rule)

        print(f"  {rule['style_name'][:50]:<50} "
              f"Priority:{priority:>4} "
              f"Specificity:{rule['_specificity']:>3} "
              f"Mapping:{'YES' if rule['_has_mapping'] else 'NO'}")

    # Sort by priority (descending)
    trane_rules_sorted = sorted(trane_rules, key=lambda x: x['_priority'], reverse=True)

    print()
    print("=" * 80)
    print("REORDERED TRANE RULES (new order):")
    print("=" * 80)
    for i, rule in enumerate(trane_rules_sorted, 1):
        print(f"{i:>2}. {rule['style_name'][:50]:<50} "
              f"(Priority: {rule['_priority']})")

    # Find where Trane rules start in original file
    first_trane_idx = None
    for i, row in enumerate(all_rules):
        if row['brand'].upper() == 'TRANE':
            first_trane_idx = i
            break

    # If no Trane in non-Trane list, append at end
    if first_trane_idx is None:
        first_trane_idx = len(all_rules)

    # Build output (insert reordered Trane rules at first Trane position)
    output_rules = all_rules[:first_trane_idx] + trane_rules_sorted + all_rules[first_trane_idx:]

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for rule in output_rules:
            # Remove internal fields
            rule.pop('date_fields_parsed', None)
            rule.pop('_priority', None)
            rule.pop('_specificity', None)
            rule.pop('_has_mapping', None)
            writer.writerow(rule)

    print()
    print(f"Reordered ruleset written to: {output_path}")


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent.parent

    # Input: current v14
    input_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v14' / 'SerialDecodeRule.csv'

    # Output: v15 with reordered Trane rules
    output_dir = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v15-trane-reordered'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'SerialDecodeRule.csv'

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    print("=" * 80)
    print("TRANE RULE REORDERING - PROOF OF CONCEPT")
    print("=" * 80)
    print()

    reorder_trane_rules(input_path, output_path)

    # Copy other files from v14 to v15
    print()
    print("Copying other rule files from v14 to v15...")
    import shutil
    v14_dir = input_path.parent
    for file in v14_dir.glob('*.csv'):
        if file.name != 'SerialDecodeRule.csv':
            shutil.copy(file, output_dir / file.name)
            print(f"  Copied {file.name}")

    print()
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Update CURRENT.txt to point to v15:")
    print("   echo '2026-01-29-sdi-master-v15-trane-reordered' > data/rules_normalized/CURRENT.txt")
    print()
    print("2. Run validation against SDI to measure improvement:")
    print("   python3 scripts/validate_serialjson_against_sdi.py")
    print()
    print("3. Compare v14 vs v15 accuracy on Trane serials")


if __name__ == '__main__':
    main()
