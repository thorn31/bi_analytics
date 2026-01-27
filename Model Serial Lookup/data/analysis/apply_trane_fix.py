"""Apply Trane serial fix by replacing broken rules in SerialDecodeRule.csv."""
import csv
import json
from pathlib import Path

# Read the current ruleset
ruleset_path = Path("data/rules_normalized/2026-01-27-trane-fix-clean/SerialDecodeRule.csv")

with ruleset_path.open('r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

print(f"Loaded {len(rows)} rules from {ruleset_path}")

# Find and replace the broken Trane rules
fixed_count = 0
for i, row in enumerate(rows):
    if row['brand'] == 'TRANE':
        if row['style_name'] == 'Style 1 (2002-2009)':
            print(f"\nLine {i+2}: Fixing 'Style 1 (2002-2009)'")
            print(f"  Old regex: {row['serial_regex']}")

            # Change to 3-digit only pattern
            row['serial_regex'] = r'^(?=.*[A-Z])\d{3}(?!\d)[A-Z0-9]{2,30}$'
            row['style_name'] = 'Style 1 (2002-2009) 3-digit'
            row['example_serials'] = '["315S41F", "915S41F"]'

            # Update notes
            date_fields = json.loads(row['date_fields'])
            row['date_fields'] = json.dumps({
                "year": {
                    "positions": {"start": 1, "end": 1},
                    "transform": {
                        "type": "year_add_base",
                        "base": 2000,
                        "min_year": 2002,
                        "max_year": 2009
                    }
                },
                "week": {"positions": {"start": 2, "end": 3}}
            })

            decade_ambiguity = json.loads(row['decade_ambiguity'])
            decade_ambiguity['notes'] = "Year code is single digit. Matches ONLY serials with exactly 3 leading digits (3 digits NOT followed by another digit)."
            row['decade_ambiguity'] = json.dumps(decade_ambiguity)

            row['evidence_excerpt'] = "From 2002 to 2009: Year of manufacture determined by 1st position (digit). Week by 2nd & 3rd positions. This pattern has exactly 3 leading digits before letters/mixed characters. The negative lookahead (?!\\d) ensures we don't match modern 4+ digit formats."
            row['retrieved_on'] = "2026-01-27"

            print(f"  New regex: {row['serial_regex']}")
            fixed_count += 1

        elif row['style_name'] == 'Style 1 (2010+)':
            print(f"\nLine {i+2}: Fixing 'Style 1 (2010+)'")
            print(f"  Old regex: {row['serial_regex']}")

            # Change to 4+ digit pattern
            row['serial_regex'] = r'^(?=.*[A-Z])\d{4,}[A-Z0-9]{2,30}$'
            row['example_serials'] = '["10161KEDAA", "130313596L", "22226NUP4F", "214410805D", "23033078JA", "121610184L"]'

            # Update date fields to ensure min_year constraint
            row['date_fields'] = json.dumps({
                "year": {
                    "positions": {"start": 1, "end": 2},
                    "transform": {
                        "type": "year_add_base",
                        "base": 2000,
                        "min_year": 2010
                    }
                },
                "week": {"positions": {"start": 3, "end": 4}}
            })

            decade_ambiguity = json.loads(row['decade_ambiguity'])
            decade_ambiguity['notes'] = "Year code is 2 digits. Matches serials with 4 OR MORE leading digits. Min year constraint ensures only 2010+ years are accepted."
            row['decade_ambiguity'] = json.dumps(decade_ambiguity)

            row['evidence_excerpt'] = "Starting in 2010: Year determined by 1st & 2nd positions. Week by 3rd & 4th positions. Modern Trane (2010+) uses 4-9 digit prefixes. Examples: 4-digit '1016', 5-digit '22226', 9-digit '121610184'. The min_year=2010 constraint rejects any decoded year < 2010."
            row['retrieved_on'] = "2026-01-27"

            print(f"  New regex: {row['serial_regex']}")
            fixed_count += 1

print(f"\nFixed {fixed_count} Trane rules")

# Write back to file
backup_path = ruleset_path.with_suffix('.csv.backup')
ruleset_path.rename(backup_path)
print(f"Backed up original to: {backup_path}")

with ruleset_path.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote updated rules to: {ruleset_path}")
print("\nDone!")
