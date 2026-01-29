#!/usr/bin/env python3
"""
Test suite for serial.json integration and validation.

Tests that serial.json mappings are consistent with v13 rules and work correctly
on real equipment data.
"""

import json
import csv
from pathlib import Path
import sys

try:
    import pytest
except ModuleNotFoundError:  # pragma: no cover
    import unittest

    raise unittest.SkipTest("pytest is not installed; skipping pytest-based integration tests")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def serialmappings():
    """Load serialmappings.json."""
    base_dir = Path(__file__).parent.parent
    path = base_dir / 'data' / 'static' / 'hvacdecodertool' / 'serialmappings.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def v13_rules():
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


def test_serialjson_loads_correctly(serialmappings):
    """Test that serialmappings.json loads without errors."""
    assert serialmappings is not None
    assert isinstance(serialmappings, dict)
    assert len(serialmappings) > 0


def test_serialjson_has_expected_brands(serialmappings):
    """Test that serialmappings.json contains expected brands."""
    expected_brands = ['Trane', 'Daikin', 'York', 'Carrier', 'Lennox', 'Bard']
    for brand in expected_brands:
        assert brand in serialmappings, f"Expected brand {brand} not found"


def test_trane_legacy_mapping_structure(serialmappings):
    """Test that Trane has the expected legacy mapping structure."""
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


def test_trane_legacy_matches_v13(serialmappings, v13_rules):
    """Test that Trane legacy mappings match v13 rules."""
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
    for key, value in trane_year_map.items():
        if key in v13_year_map:
            assert int(v13_year_map[key]) == value, \
                f"Trane year mapping mismatch for key {key}: serial.json={value}, v13={v13_year_map[key]}"


def test_daikin_style6_mapping(serialmappings):
    """Test that Daikin/McQuay Style6 has expected mapping."""
    assert 'Daikin' in serialmappings
    assert 'Style6' in serialmappings['Daikin']

    style6 = serialmappings['Daikin']['Style6']
    assert 'year_map' in style6

    year_map = style6['year_map']
    # Check known mappings
    assert year_map['A'] == 1971
    assert year_map['X'] == 1992
    assert year_map['Y'] == 1993
    assert year_map['Z'] == 1994


def test_no_conflicts_on_existing_rules(serialmappings, v13_rules):
    """Test that there are no mapping conflicts between serial.json and v13."""
    # This tests the key finding from validation: we should have either
    # MATCH or NO_MAPPING, but never CONFLICT

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


def test_trane_sample_serials(serialmappings):
    """Test Trane mappings on known sample serials."""
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


def test_mapping_completeness(serialmappings):
    """Test that mappings are reasonably complete (no huge gaps)."""
    # For letter-based year mappings, we expect mostly contiguous letters
    # (skipping I and O is common)

    for brand, brand_data in serialmappings.items():
        for style_name, style_data in brand_data.items():
            year_map = style_data.get('year_map', {})

            if not year_map:
                continue

            # Check if keys are single letters
            keys = list(year_map.keys())
            if all(len(k) == 1 and k.isalpha() for k in keys):
                # Should have at least 10 letters for a reasonable mapping
                assert len(keys) >= 10, \
                    f"{brand} {style_name} has only {len(keys)} year mappings, seems incomplete"


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


def test_all_mappings_are_integers(serialmappings):
    """Test that all mapping values are integers."""
    for brand, brand_data in serialmappings.items():
        for style_name, style_data in brand_data.items():
            for map_type in ['year_map', 'month_map']:
                if map_type in style_data:
                    mapping = style_data[map_type]
                    for key, value in mapping.items():
                        assert isinstance(value, int), \
                            f"{brand} {style_name} {map_type}[{key}] = {value} is not an integer"


def test_year_mappings_in_reasonable_range(serialmappings):
    """Test that year mappings are in a reasonable range (1950-2030)."""
    for brand, brand_data in serialmappings.items():
        for style_name, style_data in brand_data.items():
            if 'year_map' in style_data:
                year_map = style_data['year_map']
                for key, year in year_map.items():
                    assert 1950 <= year <= 2030, \
                        f"{brand} {style_name} year_map[{key}] = {year} is out of reasonable range"


def test_month_mappings_in_valid_range(serialmappings):
    """Test that month mappings are between 1 and 12."""
    for brand, brand_data in serialmappings.items():
        for style_name, style_data in brand_data.items():
            if 'month_map' in style_data:
                month_map = style_data['month_map']
                for key, month in month_map.items():
                    assert 1 <= month <= 12, \
                        f"{brand} {style_name} month_map[{key}] = {month} is not a valid month"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
