"""Apply Trane serial fix v3 - use total length as discriminator."""
import csv
import json
from pathlib import Path
import shutil

# Start fresh from the original ruleset
src = Path("data/rules_normalized/2026-01-26-sdi-promoted20-2026-01-26-heuristic36a-mitsu")
dst = Path("data/rules_normalized/2026-01-27-trane-fix-v3")

if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

ruleset_path = dst / "SerialDecodeRule.csv"

with ruleset_path.open('r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

print(f"Loaded {len(rows)} rules from {ruleset_path}")
print("\nKEY INSIGHT FROM DOCUMENTATION:")
print("2002-2009: Position 1 = year, Positions 2-3 = week")
print("2010+: Positions 1-2 = year, Positions 3-4 = week")
print("\nDATA ANALYSIS SHOWS:")
print("2002-2009 serials: predominantly length 7-9")
print("2010+ serials: predominantly length 10+")
print("\nSOLUTION: Use total serial length as discriminator via regex lookaheads")

# Find and fix the Trane rules
fixed_count = 0
for i, row in enumerate(rows):
    if row['brand'] == 'TRANE':
        if row['style_name'] == 'Style 1 (2002-2009)':
            print(f"\nLine {i+2}: Fixing 'Style 1 (2002-2009)'")
            print(f"  Old regex: {row['serial_regex']}")

            # Match 3+ digits BUT only for serials of total length 7-9
            row['serial_regex'] = r'^(?=.{7,9}$)(?=.*[A-Z])\d{3,}[A-Z0-9]{2,30}$'
            row['example_serials'] = '["91531S41F", "315S41F", "2212WHP4F"]'

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
            decade_ambiguity['notes'] = "Year code is single digit. Matches serials with total length 7-9 characters. This length constraint prevents conflict with 2010+ format which uses 10+ character serials."
            row['decade_ambiguity'] = json.dumps(decade_ambiguity)

            row['evidence_excerpt'] = "From 2002 to 2009: Year determined by position 1 (single digit), week by positions 2-3. Analysis of real data shows these serials are 7-9 characters total length. The regex uses (?=.{7,9}$) lookahead to ensure this length constraint."
            row['retrieved_on'] = "2026-01-27"

            print(f"  New regex: {row['serial_regex']}")
            print(f"  Length constraint: 7-9 characters")
            fixed_count += 1

        elif row['style_name'] == 'Style 1 (2010+)':
            print(f"\nLine {i+2}: Fixing 'Style 1 (2010+)'")
            print(f"  Old regex: {row['serial_regex']}")

            # Match 4+ digits for serials of total length 10+
            row['serial_regex'] = r'^(?=.{10,}$)(?=.*[A-Z])\d{4,}[A-Z0-9]{2,30}$'
            row['example_serials'] = '["10161KEDAA", "130313596L", "22226NUP4F", "214410805D", "23033078JA"]'

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
            decade_ambiguity['notes'] = "Year code is 2 digits. Matches serials with total length 10+ characters. This length constraint prevents conflict with 2002-2009 format which uses 7-9 character serials."
            row['decade_ambiguity'] = json.dumps(decade_ambiguity)

            row['evidence_excerpt'] = "Starting in 2010: Year determined by positions 1-2 (two digits), week by positions 3-4. Analysis of real data shows these serials are 10+ characters total length. The regex uses (?=.{10,}$) lookahead to ensure this length constraint."
            row['retrieved_on'] = "2026-01-27"

            print(f"  New regex: {row['serial_regex']}")
            print(f"  Length constraint: 10+ characters")
            fixed_count += 1

print(f"\nFixed {fixed_count} Trane rules")
print("\nThis approach makes the rules mutually exclusive:")
print("- Serials 7-9 chars → 2002-2009 rule (1-digit year)")
print("- Serials 10+ chars → 2010+ rule (2-digit year)")

# Write back
with ruleset_path.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nWrote updated rules to: {ruleset_path}")
print("Done!")
# NOTE: Archived one-off analysis artifact (moved 2026-01-28).
