"""Test proposed Trane serial fixes."""
import re

# Current rules
style1_2002_regex = r"^(?=.*[A-Z])\d{3}[A-Z0-9]{3,30}$"
style1_2010_regex = r"^(?=.*[A-Z])\d{4}[A-Z0-9]{3,30}$"

# Proposed new rule - matches 5+ leading digits followed by letters
style1_modern_regex = r"^(?=.*[A-Z])\d{5,}[A-Z]{2,}[A-Z0-9]*$"

# Test serials from analysis
test_cases = [
    # Modern 10-digit serials (should match new rule)
    ("22226NUP4F", 2022, "10-digit modern 2022"),
    ("214410805D", 2021, "10-digit modern 2021"),
    ("23033078JA", 2023, "10-digit modern 2023"),
    ("21262W9NCG", 2021, "10-digit modern 2021"),
    ("22087U9K4F", 2022, "10-digit modern 2022"),
    ("222530D93V", 2022, "10-digit modern 2022"),

    # Existing 9-digit serials (should still match 2010+ rule)
    ("10161KEDAA", 2010, "9-digit 2010+"),
    ("130313596L", 2013, "9-digit 2010+"),
    ("12345ABCD", 2012, "9-digit 2010+"),

    # Legacy 7-8 digit serials (should match 2002-2009 rule)
    ("9153S41", 2009, "7-digit legacy"),
    ("315S41F", 2003, "7-digit legacy"),
]

print("=" * 80)
print("TRANE SERIAL REGEX TESTING")
print("=" * 80)

for serial, expected_year, desc in test_cases:
    matches_2002 = bool(re.match(style1_2002_regex, serial))
    matches_2010 = bool(re.match(style1_2010_regex, serial))
    matches_modern = bool(re.match(style1_modern_regex, serial))

    print(f"\nSerial: {serial} ({desc}, expected: {expected_year})")
    print(f"  Length: {len(serial)}")
    print(f"  Matches Style 1 (2002-2009): {matches_2002}")
    print(f"  Matches Style 1 (2010+): {matches_2010}")
    print(f"  Matches Style 1 (modern): {matches_modern}")

    # Determine which rule would match first (priority order matters)
    # In the decoder, rules are evaluated in order, so modern should come first
    matched_rule = None
    decoded_year = None

    if matches_modern:
        matched_rule = "Style 1 (modern)"
        # Extract positions 1-2 for year
        year_str = serial[0:2]
        decoded_year = 2000 + int(year_str)
    elif matches_2010:
        matched_rule = "Style 1 (2010+)"
        year_str = serial[0:2]
        decoded_year = 2000 + int(year_str)
    elif matches_2002:
        matched_rule = "Style 1 (2002-2009)"
        # Extract position 1 only for year
        year_str = serial[0:1]
        decoded_year = 2000 + int(year_str)

    if matched_rule:
        correct = decoded_year == expected_year
        symbol = '✓' if correct else '✗'
        print(f"  Would match: {matched_rule}")
        print(f"  Decoded year: {decoded_year} {symbol}")
    else:
        print(f"  Would match: NONE (no match)")

print("\n" + "=" * 80)
print("PRIORITY ORDER RECOMMENDATION:")
print("=" * 80)
print("1. Style 1 (modern) - 5+ digits")
print("2. Style 1 (2010+) - exactly 4 digits")
print("3. Style 1 (2002-2009) - 3+ digits (fallback)")
print()
# NOTE: Archived one-off analysis artifact (moved 2026-01-28).
