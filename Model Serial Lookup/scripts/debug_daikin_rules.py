import sys
from pathlib import Path
import csv

# Add project root to python path
sys.path.insert(0, str(Path.cwd()))

from msl.decoder.io import load_serial_rules_csv

PATCHED_CSV = Path("data/rules_normalized/2026-01-29-sdi-master-v13/SerialDecodeRule_Patched.csv")

def debug_daikin():
    rules = load_serial_rules_csv(PATCHED_CSV)
    daikin_rules = [r for r in rules if "DAIKIN" in r.brand.upper()]
    
    print(f"Total Daikin Rules: {len(daikin_rules)}")
    for r in daikin_rules[:5]:
        print(f"\nBrand: '{r.brand}'")
        print(f"Style: '{r.style_name}'")
        print(f"Regex: '{r.serial_regex}'")
        print(f"Date Fields: {r.date_fields}")

if __name__ == "__main__":
    debug_daikin()

