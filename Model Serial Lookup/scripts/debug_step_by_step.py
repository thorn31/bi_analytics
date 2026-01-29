import sys
from pathlib import Path
import json
import re

# Add project root to python path
sys.path.insert(0, str(Path.cwd()))

from msl.decoder.io import load_serial_rules_csv
from msl.decoder.decode import _slice_positions, _apply_mapping, _as_int

PATCHED_CSV = Path("data/rules_normalized/2026-01-29-sdi-master-v13/SerialDecodeRule_Patched.csv")

def debug_step_by_step():
    rules = load_serial_rules_csv(PATCHED_CSV)
    
    # Find Daikin Style 6
    target = None
    for r in rules:
        if "DAIKIN" in r.brand and "Style 6" in r.style_name:
            target = r
            break
    
    if not target:
        print("Rule not found!")
        return

    print(f"Rule: {target.style_name}")
    print(f"Regex: {target.serial_regex}")
    print(f"Date Fields: {json.dumps(target.date_fields, indent=2)}")

    serial = "5PB1234503"
    print(f"\nTesting Serial: {serial}")
    
    # Regex Match
    match = re.search(target.serial_regex, serial)
    print(f"Regex Match: {bool(match)}")

    # Year Extraction
    year_spec = target.date_fields.get("year", {})
    year_raw = _slice_positions(serial, year_spec)
    print(f"Year Raw: '{year_raw}'")
    
    year = _apply_mapping(year_raw, year_spec.get("mapping"))
    print(f"Year Decoded: {year}")

    # Month Extraction
    month_spec = target.date_fields.get("month", {})
    month_raw = _slice_positions(serial, month_spec)
    print(f"Month Raw: '{month_raw}'")
    
    # Let's check if there's a mapping for month
    month = _apply_mapping(month_raw, month_spec.get("mapping"))
    print(f"Month Decoded: {month}")

if __name__ == "__main__":
    debug_step_by_step()
