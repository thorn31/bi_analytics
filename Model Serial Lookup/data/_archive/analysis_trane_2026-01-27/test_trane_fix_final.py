"""Test FINAL Trane serial fix - mutually exclusive regexes."""
import re

# FINAL FIX: Mutually exclusive patterns
style1_3digit = r"^(?=.*[A-Z])\d{3}(?!\d)[A-Z0-9]{2,30}$"  # exactly 3 digits
style1_4plus = r"^(?=.*[A-Z])\d{4,}[A-Z0-9]{2,30}$"  # 4 or more digits

# Test cases
test_cases = [
    # Modern 5+ digit serials
    ("22226NUP4F", 2022, "2010+", 5),
    ("214410805D", 2021, "2010+", 9),
    ("23033078JA", 2023, "2010+", 8),
    ("21262W9NCG", 2021, "2010+", 5),
    ("121610184L", 2012, "2010+", 9),

    # Standard 4-digit 2010+ serials
    ("10161KEDAA", 2010, "2010+", 5),
    ("130313596L", 2013, "2010+", 5),

    # 3-digit legacy serials
    ("315S41F", 2003, "2002-2009", 3),
    ("915S41F", 2009, "2002-2009", 3),
]

print("=" * 90)
print(" " * 25 + "FINAL TRANE REGEX FIX TEST")
print("=" * 90)
print()
print("3-digit pattern: " + style1_3digit)
print("4+ digit pattern: " + style1_4plus)
print()

all_pass = True

for serial, expected_year, expected_rule, expected_lead_digits in test_cases:
    # Count actual leading digits
    m = re.match(r'^(\d+)', serial)
    actual_lead_digits = len(m.group(1)) if m else 0

    matches_3 = bool(re.match(style1_3digit, serial))
    matches_4plus = bool(re.match(style1_4plus, serial))

    # Determine which rule matches
    if matches_3 and matches_4plus:
        result = "CONFLICT - both match!"
        decoded_year = None
        passed = False
    elif matches_3:
        result = "2002-2009 (3-digit)"
        decoded_year = 2000 + int(serial[0:1])
        passed = (decoded_year == expected_year) and (expected_rule == "2002-2009")
    elif matches_4plus:
        result = "2010+ (4+ digit)"
        decoded_year = 2000 + int(serial[0:2])
        passed = (decoded_year == expected_year) and (expected_rule == "2010+")
    else:
        result = "NO MATCH"
        decoded_year = None
        passed = False

    symbol = '✓' if passed else '✗'
    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {serial:12}  lead_digits={actual_lead_digits}  expect={expected_year}/{expected_rule}")
    print(f"      Matched: {result}")
    if decoded_year:
        print(f"      Decoded: {decoded_year} {symbol}")
    print()

    if not passed:
        all_pass = False

print("=" * 90)
if all_pass:
    print("SUCCESS! All tests pass with mutually exclusive regex patterns.")
else:
    print("FAILURE! Some tests still failing.")
print("=" * 90)
# NOTE: Archived one-off analysis artifact (moved 2026-01-28).
