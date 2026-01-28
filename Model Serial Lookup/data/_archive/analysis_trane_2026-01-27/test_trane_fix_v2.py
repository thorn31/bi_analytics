"""Test proposed Trane serial fixes - analyze why some aren't matching."""
import re

# Current rules
style1_2002_regex = r"^(?=.*[A-Z])\d{3}[A-Z0-9]{3,30}$"
style1_2010_regex = r"^(?=.*[A-Z])\d{4}[A-Z0-9]{3,30}$"

# Test actual failing serials from the analysis
failing_serials = [
    ("22226NUP4F", 2022),
    ("214410805D", 2021),
    ("23033078JA", 2023),
    ("21262W9NCG", 2021),
    ("22087U9K4F", 2022),
    ("222530D93V", 2022),
    ("22122023PA", 2022),
    ("22112160PA", 2022),
]

print("=" * 80)
print("ANALYZING WHY SERIALS DON'T MATCH Style 1 (2010+)")
print("=" * 80)

for serial, expected_year in failing_serials:
    print(f"\nSerial: {serial} (expected: {expected_year})")
    print(f"  Length: {len(serial)}")

    # Check if it has letters
    has_letter = bool(re.search(r'[A-Z]', serial))
    print(f"  Has letter: {has_letter}")

    # Count leading digits
    leading_digits_match = re.match(r'^(\d+)', serial)
    if leading_digits_match:
        leading_digits = leading_digits_match.group(1)
        print(f"  Leading digits: {leading_digits} (count: {len(leading_digits)})")

    # Check pattern components
    print(f"  Matches 2002-2009 pattern: {bool(re.match(style1_2002_regex, serial))}")
    print(f"  Matches 2010+ pattern: {bool(re.match(style1_2010_regex, serial))}")

    # Break down why it might not match 2010+
    if len(leading_digits) != 4:
        print(f"  → ISSUE: Has {len(leading_digits)} leading digits, not exactly 4")
        print(f"  → Falls back to 2002-2009 which accepts 3+ digits")
        print(f"  → 2002-2009 extracts position 0 only: '{serial[0]}' → 200{serial[0]} = {2000 + int(serial[0])}")

print("\n" + "=" * 80)
print("SOLUTION ANALYSIS")
print("=" * 80)
print()
print("Problem: Style 1 (2010+) regex requires EXACTLY 4 leading digits: \\d{4}")
print("Reality: Modern serials have 5-6 leading digits before letters")
print()
print("Option 1: Change \\d{4} to \\d{4,6} (4 to 6 digits)")
print("  - Would match both 4-digit (like 10161KEDAA) and 5-6 digit serials")
print("  - Year extraction logic remains the same (positions 0-2)")
print()
print("Option 2: Keep \\d{4} but add higher priority rule for \\d{5,}")
print("  - More explicit, documents the format evolution")
print("  - Requires careful priority ordering")
print()
print("RECOMMENDATION: Option 1 - simpler and works")
# NOTE: Archived one-off analysis artifact (moved 2026-01-28).
