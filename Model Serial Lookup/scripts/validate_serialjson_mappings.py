#!/usr/bin/env python3
"""
Validate serial.json mappings against v13 ruleset.

Compares character-to-value mappings from serialmappings.json with existing
SerialDecodeRule.csv rules to identify matches, conflicts, and opportunities.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class MappingComparisonStatus:
    """Status constants for mapping comparisons."""
    MATCH = "MATCH"  # All keys match between serial.json and v13
    CONFLICT = "CONFLICT"  # Same key maps to different values
    PARTIAL = "PARTIAL"  # serial.json has additional keys we don't have
    ORPHAN = "ORPHAN"  # Brand/style in serial.json but no v13 rules
    NO_MAPPING = "NO_MAPPING"  # v13 has rule but no mapping to compare


def normalize_brand_name(brand: str) -> str:
    """Normalize brand names for comparison."""
    return brand.upper().strip().replace(" ", "").replace("-", "")


def load_serialmappings(serialmappings_path: Path) -> Dict[str, Any]:
    """Load serialmappings.json file."""
    with open(serialmappings_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_v13_rules(rules_path: Path) -> List[Dict[str, Any]]:
    """Load v13 SerialDecodeRule.csv."""
    rules = []
    with open(rules_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse date_fields JSON
            if row.get('date_fields'):
                try:
                    row['date_fields_parsed'] = json.loads(row['date_fields'])
                except json.JSONDecodeError:
                    row['date_fields_parsed'] = {}
            else:
                row['date_fields_parsed'] = {}
            rules.append(row)
    return rules


def extract_mapping_from_rule(date_field: Dict[str, Any]) -> Dict[str, int]:
    """Extract mapping dictionary from a date field."""
    if not date_field:
        return {}

    mapping = date_field.get('mapping', {})
    if isinstance(mapping, dict):
        # Convert all values to int
        return {k: int(v) for k, v in mapping.items()}
    return {}


def compare_mappings(
    serial_map: Dict[str, int],
    rule_map: Dict[str, int]
) -> Tuple[str, Dict[str, Any]]:
    """
    Compare two mapping dictionaries.

    Returns:
        (status, details) where status is MATCH/CONFLICT/PARTIAL/NO_MAPPING
    """
    if not rule_map:
        return MappingComparisonStatus.NO_MAPPING, {
            'reason': 'v13 rule has no mapping to compare'
        }

    if not serial_map:
        return MappingComparisonStatus.NO_MAPPING, {
            'reason': 'serial.json has no mapping'
        }

    conflicts = []
    serial_only_keys = set()

    # Check each key in serial.json
    for key, serial_value in serial_map.items():
        if key in rule_map:
            rule_value = rule_map[key]
            if serial_value != rule_value:
                conflicts.append({
                    'key': key,
                    'serial_value': serial_value,
                    'rule_value': rule_value
                })
        else:
            serial_only_keys.add(key)

    # Determine status
    if conflicts:
        return MappingComparisonStatus.CONFLICT, {
            'conflicts': conflicts,
            'serial_only_keys': list(serial_only_keys),
            'num_conflicts': len(conflicts),
            'num_serial_only': len(serial_only_keys)
        }
    elif serial_only_keys:
        return MappingComparisonStatus.PARTIAL, {
            'serial_only_keys': list(serial_only_keys),
            'num_serial_only': len(serial_only_keys),
            'matching_keys': len(serial_map) - len(serial_only_keys)
        }
    else:
        return MappingComparisonStatus.MATCH, {
            'matching_keys': len(serial_map)
        }


def run_validation(
    serialmappings_path: Path,
    rules_path: Path,
    output_dir: Path
) -> None:
    """Run the validation and generate reports."""
    print("Loading serialmappings.json...")
    serial_data = load_serialmappings(serialmappings_path)

    print("Loading v13 rules...")
    v13_rules = load_v13_rules(rules_path)

    # Index v13 rules by brand
    rules_by_brand = defaultdict(list)
    for rule in v13_rules:
        brand_norm = normalize_brand_name(rule['brand'])
        rules_by_brand[brand_norm].append(rule)

    print(f"\nFound {len(serial_data)} brands in serial.json")
    print(f"Found {len(rules_by_brand)} brands in v13 rules")

    # Compare mappings
    results = []
    conflicts_detail = {}

    for brand, brand_data in serial_data.items():
        brand_norm = normalize_brand_name(brand)

        # Check if we have rules for this brand
        if brand_norm not in rules_by_brand:
            # ORPHAN - brand in serial.json but no v13 rules
            for style_name, style_data in brand_data.items():
                year_map = style_data.get('year_map', {})
                month_map = style_data.get('month_map', {})

                if year_map:
                    results.append({
                        'brand': brand,
                        'style_name': style_name,
                        'field_type': 'year',
                        'comparison_status': MappingComparisonStatus.ORPHAN,
                        'num_serial_keys': len(year_map),
                        'num_rule_keys': 0,
                        'conflicts_count': 0,
                        'serial_only_count': len(year_map),
                        'notes': 'No v13 rules found for this brand'
                    })

                if month_map:
                    results.append({
                        'brand': brand,
                        'style_name': style_name,
                        'field_type': 'month',
                        'comparison_status': MappingComparisonStatus.ORPHAN,
                        'num_serial_keys': len(month_map),
                        'num_rule_keys': 0,
                        'conflicts_count': 0,
                        'serial_only_count': len(month_map),
                        'notes': 'No v13 rules found for this brand'
                    })
            continue

        # Compare against each style
        for style_name, style_data in brand_data.items():
            year_map = style_data.get('year_map', {})
            month_map = style_data.get('month_map', {})

            # Find matching rules (best effort match by style name or just use all)
            matching_rules = rules_by_brand[brand_norm]

            # Compare year mappings
            if year_map:
                best_match_status = None
                best_match_details = None
                best_match_rule = None

                for rule in matching_rules:
                    date_fields = rule.get('date_fields_parsed', {})
                    year_field = date_fields.get('year', {})
                    rule_year_map = extract_mapping_from_rule(year_field)

                    status, details = compare_mappings(year_map, rule_year_map)

                    # Prefer MATCH, then PARTIAL, then CONFLICT, then NO_MAPPING
                    priority = {
                        MappingComparisonStatus.MATCH: 4,
                        MappingComparisonStatus.PARTIAL: 3,
                        MappingComparisonStatus.CONFLICT: 2,
                        MappingComparisonStatus.NO_MAPPING: 1
                    }

                    if best_match_status is None or priority[status] > priority[best_match_status]:
                        best_match_status = status
                        best_match_details = details
                        best_match_rule = rule

                result = {
                    'brand': brand,
                    'style_name': style_name,
                    'field_type': 'year',
                    'comparison_status': best_match_status,
                    'num_serial_keys': len(year_map),
                    'num_rule_keys': len(extract_mapping_from_rule(
                        best_match_rule.get('date_fields_parsed', {}).get('year', {})
                    )) if best_match_rule else 0,
                    'conflicts_count': best_match_details.get('num_conflicts', 0),
                    'serial_only_count': best_match_details.get('num_serial_only', 0),
                    'notes': best_match_details.get('reason', '')
                }

                if best_match_rule:
                    result['matched_rule_id'] = best_match_rule.get('rule_id', '')
                    result['matched_rule_name'] = best_match_rule.get('style_name', '')

                results.append(result)

                # Store conflict details
                if best_match_status == MappingComparisonStatus.CONFLICT:
                    key = f"{brand}_{style_name}_year"
                    conflicts_detail[key] = {
                        'brand': brand,
                        'style_name': style_name,
                        'field_type': 'year',
                        'conflicts': best_match_details.get('conflicts', []),
                        'serial_only_keys': best_match_details.get('serial_only_keys', [])
                    }

            # Compare month mappings
            if month_map:
                best_match_status = None
                best_match_details = None
                best_match_rule = None

                for rule in matching_rules:
                    date_fields = rule.get('date_fields_parsed', {})
                    month_field = date_fields.get('month', {})
                    rule_month_map = extract_mapping_from_rule(month_field)

                    status, details = compare_mappings(month_map, rule_month_map)

                    priority = {
                        MappingComparisonStatus.MATCH: 4,
                        MappingComparisonStatus.PARTIAL: 3,
                        MappingComparisonStatus.CONFLICT: 2,
                        MappingComparisonStatus.NO_MAPPING: 1
                    }

                    if best_match_status is None or priority[status] > priority[best_match_status]:
                        best_match_status = status
                        best_match_details = details
                        best_match_rule = rule

                result = {
                    'brand': brand,
                    'style_name': style_name,
                    'field_type': 'month',
                    'comparison_status': best_match_status,
                    'num_serial_keys': len(month_map),
                    'num_rule_keys': len(extract_mapping_from_rule(
                        best_match_rule.get('date_fields_parsed', {}).get('month', {})
                    )) if best_match_rule else 0,
                    'conflicts_count': best_match_details.get('num_conflicts', 0),
                    'serial_only_count': best_match_details.get('num_serial_only', 0),
                    'notes': best_match_details.get('reason', '')
                }

                if best_match_rule:
                    result['matched_rule_id'] = best_match_rule.get('rule_id', '')
                    result['matched_rule_name'] = best_match_rule.get('style_name', '')

                results.append(result)

                # Store conflict details
                if best_match_status == MappingComparisonStatus.CONFLICT:
                    key = f"{brand}_{style_name}_month"
                    conflicts_detail[key] = {
                        'brand': brand,
                        'style_name': style_name,
                        'field_type': 'month',
                        'conflicts': best_match_details.get('conflicts', []),
                        'serial_only_keys': best_match_details.get('serial_only_keys', [])
                    }

    # Write results
    output_dir.mkdir(parents=True, exist_ok=True)

    # Summary report
    report_path = output_dir / 'mapping_comparison_report.csv'
    print(f"\nWriting summary report to {report_path}...")
    with open(report_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'brand', 'style_name', 'field_type', 'comparison_status',
            'num_serial_keys', 'num_rule_keys', 'conflicts_count',
            'serial_only_count', 'matched_rule_id', 'matched_rule_name', 'notes'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({k: result.get(k, '') for k in fieldnames})

    # Conflict details
    conflicts_path = output_dir / 'conflict_details.json'
    print(f"Writing conflict details to {conflicts_path}...")
    with open(conflicts_path, 'w', encoding='utf-8') as f:
        json.dump(conflicts_detail, f, indent=2)

    # Print summary statistics
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    status_counts = defaultdict(int)
    for result in results:
        status_counts[result['comparison_status']] += 1

    print(f"\nTotal comparisons: {len(results)}")
    print(f"  {MappingComparisonStatus.MATCH}: {status_counts[MappingComparisonStatus.MATCH]}")
    print(f"  {MappingComparisonStatus.PARTIAL}: {status_counts[MappingComparisonStatus.PARTIAL]}")
    print(f"  {MappingComparisonStatus.CONFLICT}: {status_counts[MappingComparisonStatus.CONFLICT]}")
    print(f"  {MappingComparisonStatus.ORPHAN}: {status_counts[MappingComparisonStatus.ORPHAN]}")
    print(f"  {MappingComparisonStatus.NO_MAPPING}: {status_counts[MappingComparisonStatus.NO_MAPPING]}")

    if conflicts_detail:
        print(f"\n⚠️  Found {len(conflicts_detail)} mappings with conflicts!")
        print("   Review conflict_details.json for details")
    else:
        print("\n✅ No conflicts found!")

    print(f"\nReports written to: {output_dir}")


def main():
    """Main entry point."""
    # Setup paths
    base_dir = Path(__file__).parent.parent
    serialmappings_path = base_dir / 'data' / 'static' / 'hvacdecodertool' / 'serialmappings.json'
    rules_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v13' / 'SerialDecodeRule.csv'
    output_dir = base_dir / 'data' / 'validation' / 'serialjson'

    # Validate paths
    if not serialmappings_path.exists():
        print(f"ERROR: serialmappings.json not found at {serialmappings_path}")
        sys.exit(1)

    if not rules_path.exists():
        print(f"ERROR: SerialDecodeRule.csv not found at {rules_path}")
        sys.exit(1)

    # Run validation
    run_validation(serialmappings_path, rules_path, output_dir)


if __name__ == '__main__':
    main()
