#!/usr/bin/env python3
"""
Validate serial.json mappings against SDI ground truth data.

Tests serial.json character mappings against equipment with known manufacture years
by using existing v13 rules to extract character positions.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
import sys
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


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


def load_sdi_equipment(sdi_path: Path) -> List[Dict[str, Any]]:
    """Load SDI equipment data."""
    equipment = []
    # Try different encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(sdi_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    equipment.append(row)
            break
        except UnicodeDecodeError:
            if encoding == 'cp1252':  # Last encoding to try
                raise
            continue
    return equipment


def extract_character_from_serial(
    serial: str,
    positions: Dict[str, int]
) -> Optional[str]:
    """Extract character(s) from serial number using position spec."""
    if not positions or not serial:
        return None

    start = positions.get('start')
    end = positions.get('end')

    if start is None or end is None:
        return None

    try:
        # Convert to 0-based indexing
        start_idx = start - 1
        end_idx = end  # end is inclusive in our spec, slicing is exclusive

        if start_idx < 0 or end_idx > len(serial):
            return None

        extracted = serial[start_idx:end_idx]
        return extracted if extracted else None
    except (ValueError, IndexError):
        return None


def apply_mapping(
    character: str,
    mapping: Dict[str, int]
) -> Optional[int]:
    """Apply character-to-value mapping."""
    if not character or not mapping:
        return None

    return mapping.get(character)


def get_known_year_from_sdi(equipment: Dict[str, Any]) -> Optional[int]:
    """Extract known manufacture year from SDI equipment record."""
    # Try multiple columns that might contain year
    year_columns = [
        'KnownManufactureYear',
        'ManufactureYear',
        'manufacture_year',
        'Year',
        'year',
        'MfgYear',
        'mfg_year'
    ]

    for col in year_columns:
        if col in equipment and equipment[col]:
            try:
                year = int(equipment[col])
                if 1950 <= year <= 2030:  # Sanity check
                    return year
            except (ValueError, TypeError):
                continue

    return None


def find_matching_rule(
    brand: str,
    serial: str,
    rules: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Find a v13 rule that matches the brand and serial."""
    brand_norm = normalize_brand_name(brand)

    for rule in rules:
        rule_brand_norm = normalize_brand_name(rule['brand'])
        if rule_brand_norm != brand_norm:
            continue

        # Check if serial matches the regex
        serial_regex = rule.get('serial_regex', '')
        if serial_regex and serial_regex != 'UNKNOWN':
            try:
                if re.match(serial_regex, serial):
                    return rule
            except re.error:
                continue

    # If no regex match, return first rule for brand with year positions
    for rule in rules:
        rule_brand_norm = normalize_brand_name(rule['brand'])
        if rule_brand_norm != brand_norm:
            continue

        date_fields = rule.get('date_fields_parsed', {})
        year_field = date_fields.get('year', {})
        if year_field.get('positions'):
            return rule

    return None


def validate_against_sdi(
    serialmappings_path: Path,
    rules_path: Path,
    sdi_path: Path,
    output_dir: Path
) -> None:
    """Run validation against SDI ground truth."""
    print("Loading serialmappings.json...")
    serial_data = load_serialmappings(serialmappings_path)

    print("Loading v13 rules...")
    v13_rules = load_v13_rules(rules_path)

    print("Loading SDI equipment data...")
    sdi_equipment = load_sdi_equipment(sdi_path)

    print(f"\nLoaded {len(sdi_equipment)} equipment records")

    # Index serial.json by normalized brand
    serial_by_brand = {}
    for brand, brand_data in serial_data.items():
        brand_norm = normalize_brand_name(brand)
        serial_by_brand[brand_norm] = brand_data

    # Process each equipment record
    results_by_brand = defaultdict(lambda: {
        'total_tested': 0,
        'correct': 0,
        'incorrect': 0,
        'no_mapping': 0,
        'no_rule': 0,
        'correct_samples': [],
        'incorrect_samples': []
    })

    detail_results = []

    for equipment in sdi_equipment:
        brand = equipment.get('Make', equipment.get('Brand', equipment.get('brand', '')))
        serial = equipment.get('SerialNumber', equipment.get('Serial', equipment.get('serial', '')))
        known_year = get_known_year_from_sdi(equipment)

        if not brand or not serial or known_year is None:
            continue

        brand_norm = normalize_brand_name(brand)

        # Check if brand is in serial.json
        if brand_norm not in serial_by_brand:
            continue

        # Find matching v13 rule to get positions
        rule = find_matching_rule(brand, serial, v13_rules)
        if not rule:
            results_by_brand[brand_norm]['no_rule'] += 1
            continue

        # Get year positions from rule
        date_fields = rule.get('date_fields_parsed', {})
        year_field = date_fields.get('year', {})
        positions = year_field.get('positions')

        if not positions:
            results_by_brand[brand_norm]['no_rule'] += 1
            continue

        # Extract year character from serial
        year_char = extract_character_from_serial(serial, positions)
        if not year_char:
            continue

        # Get serial.json mapping for this brand
        brand_styles = serial_by_brand[brand_norm]

        # Try to find the right style (use default if available, otherwise first with year_map)
        year_map = None
        for style_name, style_data in brand_styles.items():
            if 'year_map' in style_data:
                year_map = style_data['year_map']
                if style_name == 'default':
                    break  # Prefer default

        if not year_map:
            results_by_brand[brand_norm]['no_mapping'] += 1
            continue

        # Apply mapping
        decoded_year = apply_mapping(year_char, year_map)

        # Also decode using v13 rule for comparison
        v13_year_map = year_field.get('mapping', {})
        v13_decoded_year = apply_mapping(year_char, v13_year_map) if v13_year_map else None

        # Check if serial.json decoding is correct
        results_by_brand[brand_norm]['total_tested'] += 1

        detail = {
            'brand': brand,
            'serial': serial,
            'known_year': known_year,
            'year_char_extracted': year_char,
            'decoded_year_serialjson': decoded_year if decoded_year else '',
            'decoded_year_v13': v13_decoded_year if v13_decoded_year else '',
            'match_serialjson': 'N/A',
            'match_v13': 'N/A',
            'rule_id': rule.get('rule_id', ''),
            'rule_name': rule.get('style_name', '')
        }

        if decoded_year is not None:
            is_correct = (decoded_year == known_year)
            detail['match_serialjson'] = 'CORRECT' if is_correct else 'INCORRECT'

            if is_correct:
                results_by_brand[brand_norm]['correct'] += 1
                if len(results_by_brand[brand_norm]['correct_samples']) < 3:
                    results_by_brand[brand_norm]['correct_samples'].append(serial)
            else:
                results_by_brand[brand_norm]['incorrect'] += 1
                if len(results_by_brand[brand_norm]['incorrect_samples']) < 3:
                    results_by_brand[brand_norm]['incorrect_samples'].append(
                        f"{serial} (expected {known_year}, got {decoded_year})"
                    )
        else:
            results_by_brand[brand_norm]['no_mapping'] += 1

        if v13_decoded_year is not None:
            is_correct = (v13_decoded_year == known_year)
            detail['match_v13'] = 'CORRECT' if is_correct else 'INCORRECT'

        detail_results.append(detail)

    # Write reports
    output_dir.mkdir(parents=True, exist_ok=True)

    # Summary report
    summary_path = output_dir / 'sdi_validation_report.csv'
    print(f"\nWriting summary report to {summary_path}...")
    with open(summary_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'brand', 'total_tested', 'correct', 'incorrect', 'no_mapping',
            'no_rule', 'accuracy_pct', 'sample_correct_serials', 'sample_incorrect_serials'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for brand_norm, stats in sorted(results_by_brand.items()):
            total = stats['total_tested']
            correct = stats['correct']
            accuracy = (correct / total * 100) if total > 0 else 0

            writer.writerow({
                'brand': brand_norm,
                'total_tested': total,
                'correct': correct,
                'incorrect': stats['incorrect'],
                'no_mapping': stats['no_mapping'],
                'no_rule': stats['no_rule'],
                'accuracy_pct': f"{accuracy:.1f}%",
                'sample_correct_serials': ', '.join(stats['correct_samples']),
                'sample_incorrect_serials': '; '.join(stats['incorrect_samples'])
            })

    # Detail report
    detail_path = output_dir / 'sdi_validation_details.csv'
    print(f"Writing detail report to {detail_path}...")
    with open(detail_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'brand', 'serial', 'known_year', 'year_char_extracted',
            'decoded_year_serialjson', 'decoded_year_v13',
            'match_serialjson', 'match_v13', 'rule_id', 'rule_name'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detail_results)

    # Print summary statistics
    print("\n" + "=" * 80)
    print("SDI VALIDATION SUMMARY")
    print("=" * 80)

    total_tested = sum(stats['total_tested'] for stats in results_by_brand.values())
    total_correct = sum(stats['correct'] for stats in results_by_brand.values())
    overall_accuracy = (total_correct / total_tested * 100) if total_tested > 0 else 0

    print(f"\nOverall:")
    print(f"  Total tested: {total_tested}")
    print(f"  Correct: {total_correct}")
    print(f"  Overall accuracy: {overall_accuracy:.1f}%")

    print(f"\nBy brand:")
    for brand_norm, stats in sorted(results_by_brand.items()):
        total = stats['total_tested']
        if total > 0:
            correct = stats['correct']
            accuracy = (correct / total * 100)
            print(f"  {brand_norm}: {correct}/{total} ({accuracy:.1f}%)")

    print(f"\nReports written to: {output_dir}")


def main():
    """Main entry point."""
    # Setup paths
    base_dir = Path(__file__).parent.parent
    serialmappings_path = base_dir / 'data' / 'static' / 'hvacdecodertool' / 'serialmappings.json'
    rules_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v13' / 'SerialDecodeRule.csv'
    sdi_path = base_dir / 'data' / 'equipment_exports' / '2026-01-25' / 'sdi_equipment_normalized.csv'
    output_dir = base_dir / 'data' / 'validation' / 'serialjson'

    # Validate paths
    if not serialmappings_path.exists():
        print(f"ERROR: serialmappings.json not found at {serialmappings_path}")
        sys.exit(1)

    if not rules_path.exists():
        print(f"ERROR: SerialDecodeRule.csv not found at {rules_path}")
        sys.exit(1)

    if not sdi_path.exists():
        print(f"ERROR: SDI equipment file not found at {sdi_path}")
        sys.exit(1)

    # Run validation
    validate_against_sdi(serialmappings_path, rules_path, sdi_path, output_dir)


if __name__ == '__main__':
    main()
