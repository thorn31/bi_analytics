#!/usr/bin/env python3
"""
Analyze coverage gaps between serial.json and v13 rules.

Identifies brands in serial.json that we don't have rules for, and prioritizes
them based on SDI equipment counts.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
import sys

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


def analyze_coverage_gaps(
    serialmappings_path: Path,
    rules_path: Path,
    sdi_path: Path,
    output_dir: Path
) -> None:
    """Analyze coverage gaps and generate report."""
    print("Loading serialmappings.json...")
    serial_data = load_serialmappings(serialmappings_path)

    print("Loading v13 rules...")
    v13_rules = load_v13_rules(rules_path)

    print("Loading SDI equipment data...")
    sdi_equipment = load_sdi_equipment(sdi_path)

    # Index rules by brand
    rules_by_brand = defaultdict(list)
    for rule in v13_rules:
        brand_norm = normalize_brand_name(rule['brand'])
        rules_by_brand[brand_norm].append(rule)

    # Count SDI equipment by brand
    sdi_by_brand = defaultdict(int)
    for equipment in sdi_equipment:
        brand = equipment.get('Make', equipment.get('Brand', equipment.get('brand', '')))
        if brand:
            brand_norm = normalize_brand_name(brand)
            sdi_by_brand[brand_norm] += 1

    # Analyze each brand in serial.json
    results = []

    for brand, brand_data in serial_data.items():
        brand_norm = normalize_brand_name(brand)

        # Count style variants in serial.json
        num_styles = len(brand_data)
        has_year_map = any('year_map' in style_data for style_data in brand_data.values())
        has_month_map = any('month_map' in style_data for style_data in brand_data.values())
        has_factory_map = any('factory_map' in style_data for style_data in brand_data.values())

        # Count total mappings
        total_year_keys = sum(
            len(style_data.get('year_map', {}))
            for style_data in brand_data.values()
        )
        total_month_keys = sum(
            len(style_data.get('month_map', {}))
            for style_data in brand_data.values()
        )

        # Check v13 rules
        has_rules = brand_norm in rules_by_brand
        rule_count = len(rules_by_brand.get(brand_norm, []))

        # Check if any v13 rule has year mapping
        has_v13_year_map = False
        has_v13_month_map = False
        if has_rules:
            for rule in rules_by_brand[brand_norm]:
                date_fields = rule.get('date_fields_parsed', {})
                if date_fields.get('year', {}).get('mapping'):
                    has_v13_year_map = True
                if date_fields.get('month', {}).get('mapping'):
                    has_v13_month_map = True

        # Get SDI count
        sdi_count = sdi_by_brand.get(brand_norm, 0)

        # Calculate opportunity score
        # High score = high opportunity
        # +10 points per SDI equipment
        # +5 points if serial.json has year mapping but v13 doesn't
        # +3 points if serial.json has month mapping but v13 doesn't
        # +2 points for each additional style variant
        # -1 point for each existing v13 rule

        opportunity_score = 0
        opportunity_score += sdi_count * 10
        if has_year_map and not has_v13_year_map:
            opportunity_score += 5
        if has_month_map and not has_v13_month_map:
            opportunity_score += 3
        opportunity_score += (num_styles - 1) * 2
        opportunity_score -= rule_count

        # Determine gap type
        if not has_rules:
            gap_type = "NO_RULES"
        elif not has_v13_year_map and has_year_map:
            gap_type = "MISSING_YEAR_MAP"
        elif not has_v13_month_map and has_month_map:
            gap_type = "MISSING_MONTH_MAP"
        else:
            gap_type = "COMPLETE"

        results.append({
            'brand': brand,
            'brand_norm': brand_norm,
            'gap_type': gap_type,
            'has_rules': 'Yes' if has_rules else 'No',
            'rule_count': rule_count,
            'has_v13_year_map': 'Yes' if has_v13_year_map else 'No',
            'has_v13_month_map': 'Yes' if has_v13_month_map else 'No',
            'serial_num_styles': num_styles,
            'serial_year_keys': total_year_keys,
            'serial_month_keys': total_month_keys,
            'has_factory_map': 'Yes' if has_factory_map else 'No',
            'sdi_equipment_count': sdi_count,
            'opportunity_score': opportunity_score
        })

    # Sort by opportunity score descending
    results.sort(key=lambda x: x['opportunity_score'], reverse=True)

    # Write report
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / 'brand_coverage_gaps.csv'

    print(f"\nWriting report to {report_path}...")
    with open(report_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'brand', 'gap_type', 'opportunity_score', 'sdi_equipment_count',
            'has_rules', 'rule_count', 'has_v13_year_map', 'has_v13_month_map',
            'serial_num_styles', 'serial_year_keys', 'serial_month_keys',
            'has_factory_map'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({k: result.get(k, '') for k in fieldnames})

    # Print summary
    print("\n" + "=" * 80)
    print("COVERAGE GAP ANALYSIS")
    print("=" * 80)

    gap_type_counts = defaultdict(int)
    for result in results:
        gap_type_counts[result['gap_type']] += 1

    print(f"\nTotal brands in serial.json: {len(results)}")
    print(f"  NO_RULES: {gap_type_counts['NO_RULES']}")
    print(f"  MISSING_YEAR_MAP: {gap_type_counts['MISSING_YEAR_MAP']}")
    print(f"  MISSING_MONTH_MAP: {gap_type_counts['MISSING_MONTH_MAP']}")
    print(f"  COMPLETE: {gap_type_counts['COMPLETE']}")

    print("\nTop 10 Opportunities:")
    print("-" * 80)
    print(f"{'Brand':<15} {'Gap Type':<20} {'Score':<8} {'SDI Count':<10} {'Rules'}")
    print("-" * 80)
    for result in results[:10]:
        print(f"{result['brand']:<15} {result['gap_type']:<20} "
              f"{result['opportunity_score']:<8} {result['sdi_equipment_count']:<10} "
              f"{result['rule_count']}")

    print(f"\nReport written to: {report_path}")


def main():
    """Main entry point."""
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

    # Run analysis
    analyze_coverage_gaps(serialmappings_path, rules_path, sdi_path, output_dir)


if __name__ == '__main__':
    main()
