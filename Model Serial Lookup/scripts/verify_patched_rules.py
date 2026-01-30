import sys
from pathlib import Path

# Add project root to python path
sys.path.insert(0, str(Path.cwd()))

from msl.decoder.io import load_serial_rules_csv
from msl.decoder.decode import decode_serial

# Paths
PATCHED_CSV = Path("data/rules_normalized/2026-01-29-sdi-master-v13/SerialDecodeRule_Patched.csv")

def verify():
    if not PATCHED_CSV.exists():
        print(f"Error: {PATCHED_CSV} not found.")
        return

    print("Loading rules...")
    rules = load_serial_rules_csv(PATCHED_CSV)
    print(f"Loaded {len(rules)} rules.")

    test_cases = [
        {
            "brand": "BARD",
            "serial": "28193MT",
            "expected_year": 1978,
            "expected_month": 10,
            "style": "Style 3"
        },
        {
            "brand": "DAIKIN",
            "serial": "5PB1234503",
            "expected_year": 1984,
            "expected_month": None, # Mapping missing in source JSON
            "style": "Style 6"
        }
    ]

    for case in test_cases:
        print(f"\nTesting {case['brand']} - {case['serial']} ({case['style']})...")
        result = decode_serial(case["brand"], case["serial"], rules)
        
        print(f"  Decoded Year: {result.manufacture_year} (Expected: {case['expected_year']})")
        print(f"  Decoded Month: {result.manufacture_month} (Expected: {case['expected_month']})")
        print(f"  Matched Style: {result.matched_style_name}")
        
        # Validation
        year_match = result.manufacture_year == case["expected_year"]
        month_match = result.manufacture_month == case["expected_month"]
        
        if year_match and month_match:
            print("  Result: PASS")
        else:
            print("  Result: FAIL")

if __name__ == "__main__":
    verify()
