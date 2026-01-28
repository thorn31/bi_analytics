import sys
from pathlib import Path
# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from msl.decoder.decode import decode_serial
from msl.decoder.io import load_serial_rules_csv
from msl.decoder.validate import validate_serial_rules

def debug_trane_single(ruleset_path, serial):
    print(f"Loading rules from {ruleset_path}...")
    rules_path = Path(ruleset_path) / "SerialDecodeRule.csv"
    raw_rules = load_serial_rules_csv(rules_path)
    accepted, issues = validate_serial_rules(raw_rules)
    
    print(f"Loaded {len(accepted)} rules. Filtered to TRANE:")
    trane_rules = [r for r in accepted if r.brand == "TRANE"]
    for r in trane_rules:
        print(f" - {r.style_name}: Regex='{r.serial_regex}'")

    print(f"\nDecoding Serial: {serial} (Brand: TRANE)")
    res = decode_serial("TRANE", serial, accepted)
    
    print(f"\nResult:")
    print(f"  Confidence: {res.confidence}")
    print(f"  Year: {res.manufacture_year}")
    print(f"  Style: {res.matched_style_name}")
    print(f"  Notes: {res.notes}")

if __name__ == "__main__":
    debug_trane_single(sys.argv[1], sys.argv[2])
# NOTE: Archived one-off investigation script (moved 2026-01-28).
