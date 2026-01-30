#!/usr/bin/env python3
"""
Generate rule templates from serial.json for brands without v13 rules.

Creates JSONL templates with mappings populated but positions/regex marked for research.
"""

import json
from pathlib import Path
from typing import Dict, Any
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


def load_v13_rules(rules_path: Path) -> Dict[str, bool]:
    """Load v13 rules and return set of brands that have rules."""
    import csv
    brands_with_rules = set()
    with open(rules_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            brand_norm = normalize_brand_name(row['brand'])
            brands_with_rules.add(brand_norm)
    return brands_with_rules


def generate_rule_template(
    brand: str,
    style_name: str,
    style_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a rule template from serial.json style data."""
    template = {
        "rule_type": "decode",
        "brand": brand,
        "style_name": f"NEEDS_RESEARCH: serial.json template - {style_name}",
        "serial_regex": "UNKNOWN - REQUIRES RESEARCH",
        "date_fields": {},
        "example_serials": [],
        "source": "serial.json v3.80 (template)",
        "notes": "TEMPLATE ONLY: Has mappings but needs regex/positions researched. "
                 "DO NOT USE IN PRODUCTION without validation."
    }

    # Add year mapping if present
    if 'year_map' in style_data:
        year_map = style_data['year_map']

        # Determine if there's decade ambiguity
        years = list(year_map.values())
        year_range = max(years) - min(years)
        is_ambiguous = year_range >= 100  # If span > 100 years, likely has ambiguity

        template['date_fields']['year'] = {
            "positions": {
                "start": "UNKNOWN",
                "end": "UNKNOWN",
                "_comment": "REQUIRES RESEARCH: Determine character position(s) in serial number"
            },
            "mapping": year_map
        }

        if is_ambiguous:
            template['decade_ambiguity'] = {
                "is_ambiguous": True,
                "notes": f"Year range {min(years)}-{max(years)} may indicate decade ambiguity. "
                         "Verify if mappings repeat across decades."
            }
        else:
            template['decade_ambiguity'] = {
                "is_ambiguous": False,
                "notes": f"Year range {min(years)}-{max(years)}"
            }

    # Add month mapping if present
    if 'month_map' in style_data:
        template['date_fields']['month'] = {
            "positions": {
                "start": "UNKNOWN",
                "end": "UNKNOWN",
                "_comment": "REQUIRES RESEARCH: Determine character position(s) in serial number"
            },
            "mapping": style_data['month_map']
        }

    # Add factory mapping if present
    if 'factory_map' in style_data:
        template['date_fields']['factory'] = {
            "positions": {
                "start": "UNKNOWN",
                "end": "UNKNOWN",
                "_comment": "REQUIRES RESEARCH: Determine character position(s) in serial number"
            },
            "mapping": style_data['factory_map']
        }

    # Add type mapping if present (York specific)
    if 'type_map' in style_data:
        template['type_field'] = {
            "positions": {
                "start": "UNKNOWN",
                "end": "UNKNOWN",
                "_comment": "REQUIRES RESEARCH: Determine character position(s) in serial number"
            },
            "mapping": style_data['type_map']
        }

    return template


def generate_templates(
    serialmappings_path: Path,
    rules_path: Path,
    output_path: Path
) -> None:
    """Generate rule templates for brands without v13 rules."""
    print("Loading serialmappings.json...")
    serial_data = load_serialmappings(serialmappings_path)

    print("Loading v13 rules...")
    brands_with_rules = load_v13_rules(rules_path)

    templates = []

    print("\nGenerating templates for brands without rules...")

    for brand, brand_data in serial_data.items():
        brand_norm = normalize_brand_name(brand)

        # Only generate templates for brands without v13 rules
        if brand_norm in brands_with_rules:
            print(f"  Skipping {brand} - already has v13 rules")
            continue

        print(f"  Generating template for {brand}...")

        for style_name, style_data in brand_data.items():
            # Skip if no useful data
            if not any(k in style_data for k in ['year_map', 'month_map', 'factory_map', 'type_map']):
                continue

            template = generate_rule_template(brand, style_name, style_data)
            templates.append(template)

    # Write templates to JSONL
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nWriting {len(templates)} templates to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        for template in templates:
            f.write(json.dumps(template, indent=2))
            f.write('\n')

    print("\n" + "=" * 80)
    print("TEMPLATE GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nGenerated {len(templates)} rule templates")

    # Print summary
    brands_generated = set(t['brand'] for t in templates)
    print(f"\nBrands with templates:")
    for brand in sorted(brands_generated):
        brand_templates = [t for t in templates if t['brand'] == brand]
        print(f"  {brand}: {len(brand_templates)} style(s)")

    print(f"\nTemplates written to: {output_path}")
    print("\n⚠️  IMPORTANT: These are templates only!")
    print("   - Requires research to fill in regex patterns and positions")
    print("   - Must validate against actual serial numbers before use")
    print("   - DO NOT use in production without testing")


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent.parent
    serialmappings_path = base_dir / 'data' / 'static' / 'hvacdecodertool' / 'serialmappings.json'
    rules_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v13' / 'SerialDecodeRule.csv'
    output_path = base_dir / 'data' / 'validation' / 'serialjson' / 'rule_templates.jsonl'

    # Validate paths
    if not serialmappings_path.exists():
        print(f"ERROR: serialmappings.json not found at {serialmappings_path}")
        sys.exit(1)

    if not rules_path.exists():
        print(f"ERROR: SerialDecodeRule.csv not found at {rules_path}")
        sys.exit(1)

    # Generate templates
    generate_templates(serialmappings_path, rules_path, output_path)


if __name__ == '__main__':
    main()
