import sys
from pathlib import Path

# Add project root to python path
sys.path.insert(0, str(Path.cwd()))

from msl.decoder.io import load_serial_rules_csv
from msl.decoder.decode import decode_serial

# Paths
ORIGINAL_CSV = Path("data/rules_normalized/2026-01-29-sdi-master-v13/SerialDecodeRule.csv")
PATCHED_CSV = Path("data/rules_normalized/2026-01-29-sdi-master-v13/SerialDecodeRule_Patched.csv")

def compare():
    print("--- Comparison Test: Daikin Style 6 (5PB1234503) ---")
    brand = "DAIKIN"
    serial = "5PB1234503"
    
    # Test Original
    rules_orig = load_serial_rules_csv(ORIGINAL_CSV)
    res_orig = decode_serial(brand, serial, rules_orig, min_plausible_year=1960) # Lowered for test
    
    print(f"\n[Original Ruleset]")
    print(f"  Matched Style: {res_orig.matched_style_name}")
    print(f"  Decoded Year:  {res_orig.manufacture_year}")
    print(f"  Decoded Month: {res_orig.manufacture_month}")

    # Test Patched
    rules_patch = load_serial_rules_csv(PATCHED_CSV)
    res_patch = decode_serial(brand, serial, rules_patch, min_plausible_year=1960)
    
    print(f"\n[Patched Ruleset]")
    print(f"  Matched Style: {res_patch.matched_style_name}")
    print(f"  Decoded Year:  {res_patch.manufacture_year}")
    print(f"  Decoded Month: {res_patch.manufacture_month}")

if __name__ == "__main__":
    compare()
