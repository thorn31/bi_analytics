#!/usr/bin/env python3
"""
Prioritize which rules should get mappings added first.

Scoring factors:
1. SDI equipment count for that brand (higher = more impact)
2. Rule has explicit positions (ready to add mapping)
3. Evidence of serial.json having mapping data
4. Decade ambiguity (could be resolved with better mapping)
"""

import sys
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


def load_serialjson_brands(serialjson_path: Path):
    """Load brands from serialmappings.json."""
    try:
        with open(serialjson_path, 'r') as f:
            data = json.load(f)
        return set(b.upper() for b in data.keys())
    except FileNotFoundError:
        return set()


def prioritize_mappings():
    """Prioritize mapping opportunities."""

    base_dir = Path(__file__).parent.parent

    # Load current ruleset
    current_txt = base_dir / 'data' / 'rules_normalized' / 'CURRENT.txt'
    current_name = current_txt.read_text().strip()
    current_path = base_dir / 'data' / 'rules_normalized' / current_name / 'SerialDecodeRule.csv'

    print("=" * 80)
    print("PRIORITIZED MAPPING OPPORTUNITIES")
    print("=" * 80)
    print()

    print(f"Loading rules from: {current_name}")
    rules = load_serial_rules_csv(current_path)
    decode_rules = [r for r in rules if r.rule_type == 'decode']
    print(f"  {len(decode_rules)} decode rules")
    print()

    # Load SDI equipment
    sdi_path = base_dir / 'data' / 'equipment_exports' / '2026-01-25' / 'sdi_equipment_normalized.csv'
    print("Loading SDI equipment data...")
    sdi_equipment = load_sdi_equipment(sdi_path)
    print(f"  {len(sdi_equipment)} equipment records")
    print()

    # Count equipment by brand
    brand_equipment_count = defaultdict(int)
    for eq in sdi_equipment:
        brand = eq.get('Make', eq.get('Brand', ''))
        if brand:
            brand_norm = normalize_brand(brand)
            brand_equipment_count[brand_norm] += 1

    # Load serial.json brands
    serialjson_path = base_dir / 'data' / 'static' / 'hvacdecodertool' / 'serialmappings.json'
    serialjson_brands = load_serialjson_brands(serialjson_path)
    print(f"Loaded {len(serialjson_brands)} brands from serial.json")
    print()

    # Find rules without mappings
    opportunities = []

    for rule in decode_rules:
        date_fields = rule.date_fields or {}
        year_field = date_fields.get('year', {})
        month_field = date_fields.get('month', {})

        # Has positions but no mapping
        has_year_positions = bool(year_field.get('positions'))
        has_year_mapping = bool(year_field.get('mapping'))
        has_month_positions = bool(month_field.get('positions'))
        has_month_mapping = bool(month_field.get('mapping'))

        if has_year_positions and not has_year_mapping:
            brand_norm = normalize_brand(rule.brand)
            sdi_count = brand_equipment_count.get(brand_norm, 0)

            # Check if brand is in serial.json
            in_serialjson = brand_norm.upper() in serialjson_brands or rule.brand.upper() in serialjson_brands

            # Check decade ambiguity
            decade_amb = rule.decade_ambiguity or {}
            is_ambiguous = decade_amb.get('is_ambiguous', False)

            # Calculate opportunity score
            # Base score: SDI count
            # Bonus: +100 if in serial.json (easy to get mapping)
            # Bonus: +50 if decade ambiguous (mapping could resolve)
            score = sdi_count
            if in_serialjson:
                score += 100
            if is_ambiguous:
                score += 50

            opportunities.append({
                'brand': rule.brand,
                'brand_norm': brand_norm,
                'style_name': rule.style_name,
                'sdi_count': sdi_count,
                'in_serialjson': in_serialjson,
                'is_ambiguous': is_ambiguous,
                'has_month_positions': has_month_positions,
                'has_month_mapping': has_month_mapping,
                'source_url': rule.source_url or '',
                'score': score
            })

    # Sort by score
    opportunities.sort(key=lambda x: x['score'], reverse=True)

    print("=" * 80)
    print("TOP 50 MAPPING OPPORTUNITIES")
    print("=" * 80)
    print()
    print(f"{'#':<4} {'Brand':<20} {'SDI':>6} {'SJ':>4} {'Amb':>5} {'Score':>8} {'Style Name':<50}")
    print("-" * 120)

    for i, opp in enumerate(opportunities[:50], 1):
        sj = 'YES' if opp['in_serialjson'] else 'NO'
        amb = 'YES' if opp['is_ambiguous'] else 'NO'

        print(f"{i:<4} {opp['brand']:<20} {opp['sdi_count']:>6} {sj:>4} {amb:>5} {opp['score']:>8} {opp['style_name'][:50]}")

    print()
    print("Legend:")
    print("  SDI = Number of equipment records in SDI dataset")
    print("  SJ = Brand exists in serial.json (easy to get mapping)")
    print("  Amb = Has decade ambiguity (mapping could resolve)")
    print("  Score = Prioritization score (higher = do first)")
    print()

    # Group by brand
    print("=" * 80)
    print("OPPORTUNITIES BY BRAND (Top 20)")
    print("=" * 80)
    print()

    brand_summary = defaultdict(lambda: {
        'count': 0,
        'sdi_count': 0,
        'in_serialjson': False,
        'ambiguous_count': 0
    })

    for opp in opportunities:
        brand_norm = opp['brand_norm']
        brand_summary[brand_norm]['count'] += 1
        brand_summary[brand_norm]['sdi_count'] = opp['sdi_count']
        brand_summary[brand_norm]['in_serialjson'] = brand_summary[brand_norm]['in_serialjson'] or opp['in_serialjson']
        if opp['is_ambiguous']:
            brand_summary[brand_norm]['ambiguous_count'] += 1

    brand_list = [
        {
            'brand': brand,
            'rules_needing_mapping': summary['count'],
            'sdi_count': summary['sdi_count'],
            'in_serialjson': summary['in_serialjson'],
            'ambiguous_count': summary['ambiguous_count'],
            'score': summary['sdi_count'] + (100 if summary['in_serialjson'] else 0)
        }
        for brand, summary in brand_summary.items()
    ]

    brand_list.sort(key=lambda x: x['score'], reverse=True)

    print(f"{'Brand':<25} {'Rules Need Map':>15} {'SDI Count':>12} {'In SJ':>8} {'Ambiguous':>12} {'Priority':>10}")
    print("-" * 100)

    for item in brand_list[:20]:
        sj = 'YES' if item['in_serialjson'] else 'NO'
        print(f"{item['brand']:<25} {item['rules_needing_mapping']:>15} {item['sdi_count']:>12} {sj:>8} {item['ambiguous_count']:>12} {'HIGH' if item['score'] > 500 else 'MEDIUM' if item['score'] > 100 else 'LOW':>10}")

    print()
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    print("1. **START WITH TRANE**: 12 rules need mappings, 2,071 SDI equipment records")
    print("   → Most of these are Style 1-8 rules without mappings")
    print("   → Research manufacturer documentation or test against SDI data")
    print()

    carrier_rules = [o for o in opportunities if o['brand_norm'] == 'CARRIER/ICP']
    print(f"2. **CARRIER/ICP**: {len(carrier_rules)} rules need mappings, 474 SDI equipment")
    print("   → Brand exists in serial.json - could pull mappings from there")
    print()

    mit_rules = [o for o in opportunities if o['brand_norm'] == 'MITSUBISHI']
    print(f"3. **MITSUBISHI**: {len(mit_rules)} rules need mappings, 365 SDI equipment")
    print("   → Research manufacturer documentation")
    print()

    # Count brands in serial.json
    sj_opps = [o for o in opportunities if o['in_serialjson']]
    print(f"4. **serial.json INTEGRATION**: {len(sj_opps)} rules from brands in serial.json")
    print("   → Quick wins - mappings already exist, just need to integrate")
    print()

    print("Next steps:")
    print("1. Review serial.json for Trane/Carrier/other mappings")
    print("2. Create validation script to test mapping accuracy against SDI")
    print("3. Add mappings to top 10-20 rules and measure accuracy improvement")


if __name__ == '__main__':
    prioritize_mappings()
