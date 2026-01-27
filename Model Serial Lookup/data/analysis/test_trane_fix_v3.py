"""Test the FIXED Trane serial patterns."""
import re

# ORIGINAL rules
style1_2002_orig = r"^(?=.*[A-Z])\d{3}[A-Z0-9]{3,30}$"
style1_2010_orig = r"^(?=.*[A-Z])\d{4}[A-Z0-9]{3,30}$"

# FIXED rules
style1_2002_fixed = r"^(?=.*[A-Z])\d{3}(?!\d)[A-Z0-9]{3,30}$"  # 3 digits NOT followed by digit
style1_2010_fixed = r"^(?=.*[A-Z])\d{4,}[A-Z0-9]{3,30}$"  # 4 or more digits

# Test cases covering all scenarios
test_cases = [
    # Modern 10-digit serials (should match 2010+ only with fix)
    ("22226NUP4F", 2022, "modern-2022", "2010+"),
    ("214410805D", 2021, "modern-2021", "2010+"),
    ("23033078JA", 2023, "modern-2023", "2010+"),
    ("21262W9NCG", 2021, "modern-2021", "2010+"),

    # Standard 9-10 digit 2010+ serials (should match 2010+)
    ("10161KEDAA", 2010, "standard-2010", "2010+"),
    ("130313596L", 2013, "standard-2013", "2010+"),

    # Legacy 7-8 digit serials (should match 2002-2009 only)
    ("315S41F", 2003, "legacy-2003", "2002-2009"),
    ("9153S41", 2009, "legacy-2009", "2002-2009"),
]

print("=" * 90)
print(" " * 30 + "TRANE REGEX FIX TESTING")
print("=" * 90)
print()

def test_rule_set(rules_2002, rules_2010, label):
    print(f"\n{'=' * 90}")
    print(f"{label}")
    print(f"{'=' * 90}")
    print(f"2002-2009 regex: {rules_2002}")
    print(f"2010+ regex: {rules_2010}")
    print()

    correct_count = 0
    wrong_count = 0

    for serial, expected_year, desc, expected_match in test_cases:
        matches_2002 = bool(re.match(rules_2002, serial))
        matches_2010 = bool(re.match(rules_2010, serial))

        # Simulate decoder priority: 2002-2009 comes first in CSV
        if matches_2002:
            matched_rule = "2002-2009"
            year_code = serial[0:1]  # position 1 only
            decoded_year = 2000 + int(year_code)
        elif matches_2010:
            matched_rule = "2010+"
            year_code = serial[0:2]  # positions 1-2
            decoded_year = 2000 + int(year_code)
        else:
            matched_rule = "NONE"
            decoded_year = None

        correct = (decoded_year == expected_year) and (matched_rule == expected_match)
        symbol = '✓' if correct else '✗'

        if correct:
            correct_count += 1
        else:
            wrong_count += 1

        status = "PASS" if correct else "FAIL"
        print(f"  [{status}] {serial:12} (expected {expected_year}, {expected_match})")
        print(f"        Matches 2002-2009: {matches_2002}, Matches 2010+: {matches_2010}")
        print(f"        → Decoded as {decoded_year} via {matched_rule} {symbol}")

    print()
    print(f"  Results: {correct_count} PASS, {wrong_count} FAIL")
    return correct_count == len(test_cases)

# Test original rules
orig_passed = test_rule_set(style1_2002_orig, style1_2010_orig, "ORIGINAL RULES (BROKEN)")

# Test fixed rules
fixed_passed = test_rule_set(style1_2002_fixed, style1_2010_fixed, "FIXED RULES")

print("\n" + "=" * 90)
print("SUMMARY")
print("=" * 90)
print(f"Original rules: {'✓ PASS' if orig_passed else '✗ FAIL'}")
print(f"Fixed rules: {'✓ PASS' if fixed_passed else '✗ FAIL'}")
print()

if fixed_passed:
    print("SUCCESS! Fixed rules correctly decode all test serials.")
else:
    print("WARNING: Fixed rules still have issues.")
