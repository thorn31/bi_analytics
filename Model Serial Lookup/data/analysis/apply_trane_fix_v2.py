"""Apply Trane serial fix v2 - allow both rules to match, rely on year bounds."""
import csv
import json
from pathlib import Path

# Start fresh from the original ruleset
import shutil
src = Path("data/rules_normalized/2026-01-26-sdi-promoted20-2026-01-26-heuristic36a-mitsu")
dst = Path("data/rules_normalized/2026-01-27-trane-fix-v2")

if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

ruleset_path = dst / "SerialDecodeRule.csv"

with ruleset_path.open('r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

print(f"Loaded {len(rows)} rules from {ruleset_path}")

# Find and fix the Trane rules
fixed_count = 0
for i, row in enumerate(rows):
    if row['brand'] == 'TRANE':
        if row['style_name'] == 'Style 1 (2002-2009)':
            print(f"\nLine {i+2}: Fixing 'Style 1 (2002-2009)'")
            print(f"  Old regex: {row['serial_regex']}")

            # Keep 3+ digits BUT ensure max_year is enforced
            row['serial_regex'] = r'^(?=.*[A-Z])\d{3,}[A-Z0-9]{2,30}$'

            # Ensure max_year=2009 is set
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

            row['evidence_excerpt'] = "From 2002 to 2009: Year determined by 1st position only (single digit). This rule matches 3+ digit prefixes but max_year=2009 constraint rejects any result >= 2010."
            row['retrieved_on'] = "2026-01-27"

            print(f"  New regex: {row['serial_regex']}")
            fixed_count += 1

        elif row['style_name'] == 'Style 1 (2010+)':
            print(f"\nLine {i+2}: Fixing 'Style 1 (2010+)'")
            print(f"  Old regex: {row['serial_regex']}")

            # Change to 4+ digits
            row['serial_regex'] = r'^(?=.*[A-Z])\d{4,}[A-Z0-9]{2,30}$'
            row['example_serials'] = '["10161KEDAA", "130313596L", "22226NUP4F", "214410805D", "23033078JA"]'

            # Ensure min_year=2010 is set
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

            row['evidence_excerpt'] = "Starting in 2010: Year determined by 1st & 2nd positions (two digits). This rule matches 4+ digit prefixes and min_year=2010 constraint rejects any result < 2010."
            row['retrieved_on'] = "2026-01-27"

            print(f"  New regex: {row['serial_regex']}")
            fixed_count += 1

print(f"\nFixed {fixed_count} Trane rules")
print("\nKEY INSIGHT:")
print("Both rules can now match the same serial. The decoder will:")
print("1. Try 2002-2009: extract digit 1 → add 2000 → check 2002-2009 bounds")
print("2. Try 2010+: extract digits 1-2 → add 2000 → check >= 2010")
print("3. Year bounds filtering will reject invalid results")
print("4. Pick best remaining match based on scoring")

# Write back
with ruleset_path.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nWrote updated rules to: {ruleset_path}")
print("Done!")
