#!/usr/bin/env python3
"""
Test suite for serial.json integration and validation (no pytest required).

Tests that serial.json mappings are consistent with v13 rules and work correctly
on real equipment data.
"""

import json
import csv
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_serialmappings():
    """Load serialmappings.json."""
    base_dir = Path(__file__).parent.parent
    path = base_dir / 'data' / 'static' / 'hvacdecodertool' / 'serialmappings.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_v13_rules():
    """Load v13 SerialDecodeRule.csv."""
    base_dir = Path(__file__).parent.parent
    path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v13' / 'SerialDecodeRule.csv'
    rules = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('date_fields'):
                try:
                    row['date_fields_parsed'] = json.loads(row['date_fields'])
                except json.JSONDecodeError:
                    row['date_fields_parsed'] = {}
            rules.append(row)
    return rules


def test_serialjson_loads_correctly():
    """Test that serialmappings.json loads without errors."""
    serialmappings = load_serialmappings()
    assert serialmappings is not None
    assert isinstance(serialmappings, dict)
    assert len(serialmappings) > 0
    print("✓ serial.json loads correctly")


def test_serialjson_has_expected_brands():
    """Test that serialmappings.json contains expected brands."""
    serialmappings = load_serialmappings()
    expected_brands = ['Trane', 'Daikin', 'York', 'Carrier', 'Lennox', 'Bard']
    for brand in expected_brands:
        assert brand in serialmappings, f"Expected brand {brand} not found"
    print("✓ All expected brands present")


def test_trane_legacy_mapping_structure():
    """Test that Trane has the expected legacy mapping structure."""
    serialmappings = load_serialmappings()
    assert 'Trane' in serialmappings
    assert 'default' in serialmappings['Trane']

    trane_default = serialmappings['Trane']['default']
    assert 'year_map' in trane_default
    assert 'month_map' in trane_default

    # Check some known mappings
    year_map = trane_default['year_map']
    assert year_map['W'] == 1983
    assert year_map['X'] == 1984
    assert year_map['Y'] == 1985
    assert year_map['Z'] == 2001
    print("✓ Trane legacy mapping structure correct")


def test_trane_legacy_matches_v13():
    """Test that Trane legacy mappings match v13 rules."""
    serialmappings = load_serialmappings()
    v13_rules = load_v13_rules()

    trane_year_map = serialmappings['Trane']['default']['year_map']

    # Find Trane legacy rule in v13
    trane_legacy_rule = None
    for rule in v13_rules:
        if rule['brand'].upper() == 'TRANE' and 'Legacy' in rule.get('style_name', ''):
            trane_legacy_rule = rule
            break

    assert trane_legacy_rule is not None, "Trane legacy rule not found in v13"

    # Compare mappings
    date_fields = trane_legacy_rule.get('date_fields_parsed', {})
    year_field = date_fields.get('year', {})
    v13_year_map = year_field.get('mapping', {})

    assert v13_year_map, "v13 Trane legacy rule has no year mapping"

    # Check key-by-key match
    matches = 0
    for key, value in trane_year_map.items():
        if key in v13_year_map:
            assert int(v13_year_map[key]) == value, \
                f"Trane year mapping mismatch for key {key}: serial.json={value}, v13={v13_year_map[key]}"
            matches += 1

    print(f"✓ Trane legacy mappings match v13 ({matches} keys matched)")


def test_no_conflicts_on_existing_rules():
    """Test that there are no mapping conflicts between serial.json and v13."""
    serialmappings = load_serialmappings()
    v13_rules = load_v13_rules()

    def normalize_brand(brand):
        return brand.upper().strip().replace(" ", "").replace("-", "")

    # Index v13 rules by brand
    rules_by_brand = {}
    for rule in v13_rules:
        brand_norm = normalize_brand(rule['brand'])
        if brand_norm not in rules_by_brand:
            rules_by_brand[brand_norm] = []
        rules_by_brand[brand_norm].append(rule)

    conflicts = []

    for brand, brand_data in serialmappings.items():
        brand_norm = normalize_brand(brand)

        if brand_norm not in rules_by_brand:
            continue

        for style_name, style_data in brand_data.items():
            year_map = style_data.get('year_map', {})

            if not year_map:
                continue

            # Check against all rules for this brand
            for rule in rules_by_brand[brand_norm]:
                date_fields = rule.get('date_fields_parsed', {})
                year_field = date_fields.get('year', {})
                v13_year_map = year_field.get('mapping', {})

                if not v13_year_map:
                    continue

                # Check for conflicts
                for key, serial_value in year_map.items():
                    if key in v13_year_map:
                        v13_value = int(v13_year_map[key])
                        if serial_value != v13_value:
                            conflicts.append({
                                'brand': brand,
                                'style': style_name,
                                'key': key,
                                'serial_value': serial_value,
                                'v13_value': v13_value,
                                'rule': rule.get('style_name', '')
                            })

    assert len(conflicts) == 0, \
        f"Found {len(conflicts)} mapping conflicts between serial.json and v13: {conflicts}"
    print("✓ No conflicts found between serial.json and v13 rules")


def test_trane_sample_serials():
    """Test Trane mappings on known sample serials."""
    serialmappings = load_serialmappings()
    year_map = serialmappings['Trane']['default']['year_map']

    # These are from actual SDI data validated to be correct
    test_cases = [
        ('D', 1989),  # D02221593 -> 1989
        ('P', 1999),  # P311K00FF -> 1999
        ('K', 1995),  # K01289961 -> 1995
        ('W', 1983),  # Legacy mapping
        ('Z', 2001),  # Legacy mapping
    ]

    for char, expected_year in test_cases:
        assert char in year_map, f"Character {char} not in Trane year_map"
        assert year_map[char] == expected_year, \
            f"Trane year_map[{char}] = {year_map[char]}, expected {expected_year}"

    print(f"✓ Trane sample serials decode correctly ({len(test_cases)} tested)")


def test_sdi_validation_results_exist():
    """Test that SDI validation has been run and results exist."""
    base_dir = Path(__file__).parent.parent
    report_path = base_dir / 'data' / 'validation' / 'serialjson' / 'sdi_validation_report.csv'

    assert report_path.exists(), "SDI validation report not found. Run validate_serialjson_against_sdi.py first"

    # Read and check report
    with open(report_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) > 0, "SDI validation report is empty"

    # Check for Trane results
    trane_row = None
    for row in rows:
        if row['brand'].upper() == 'TRANE':
            trane_row = row
            break

    assert trane_row is not None, "Trane not found in SDI validation results"

    # Trane should have reasonable accuracy (at least 30%)
    accuracy_str = trane_row['accuracy_pct'].rstrip('%')
    accuracy = float(accuracy_str)
    assert accuracy >= 30.0, \
        f"Trane accuracy is {accuracy}%, expected at least 30%"

    print(f"✓ SDI validation completed with Trane accuracy: {accuracy}%")


def test_all_mappings_are_integers():
    """Test that all mapping values are integers."""
    serialmappings = load_serialmappings()
    total_checked = 0

    for brand, brand_data in serialmappings.items():
        for style_name, style_data in brand_data.items():
            for map_type in ['year_map', 'month_map']:
                if map_type in style_data:
                    mapping = style_data[map_type]
                    for key, value in mapping.items():
                        assert isinstance(value, int), \
                            f"{brand} {style_name} {map_type}[{key}] = {value} is not an integer"
                        total_checked += 1

    print(f"✓ All mapping values are integers ({total_checked} checked)")


def test_year_mappings_in_reasonable_range():
    """Test that year mappings are in a reasonable range (1950-2030)."""
    serialmappings = load_serialmappings()
    total_checked = 0

    for brand, brand_data in serialmappings.items():
        for style_name, style_data in brand_data.items():
            if 'year_map' in style_data:
                year_map = style_data['year_map']
                for key, year in year_map.items():
                    assert 1950 <= year <= 2030, \
                        f"{brand} {style_name} year_map[{key}] = {year} is out of reasonable range"
                    total_checked += 1

    print(f"✓ All year mappings in reasonable range ({total_checked} checked)")


def test_month_mappings_in_valid_range():
    """Test that month mappings are between 1 and 12."""
    serialmappings = load_serialmappings()
    total_checked = 0

    for brand, brand_data in serialmappings.items():
        for style_name, style_data in brand_data.items():
            if 'month_map' in style_data:
                month_map = style_data['month_map']
                for key, month in month_map.items():
                    assert 1 <= month <= 12, \
                        f"{brand} {style_name} month_map[{key}] = {month} is not a valid month"
                    total_checked += 1

    print(f"✓ All month mappings valid ({total_checked} checked)")


def run_all_tests():
    """Run all tests."""
    tests = [
        test_serialjson_loads_correctly,
        test_serialjson_has_expected_brands,
        test_trane_legacy_mapping_structure,
        test_trane_legacy_matches_v13,
        test_no_conflicts_on_existing_rules,
        test_trane_sample_serials,
        test_sdi_validation_results_exist,
        test_all_mappings_are_integers,
        test_year_mappings_in_reasonable_range,
        test_month_mappings_in_valid_range,
    ]

    print("=" * 80)
    print("Running serial.json Integration Tests")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1

    print()
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
