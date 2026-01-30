import sys
from pathlib import Path
import json
import random

# Add project root to python path
sys.path.insert(0, str(Path.cwd()))

from msl.decoder.io import load_serial_rules_csv
from msl.decoder.decode import decode_serial

ORIGINAL_CSV = Path("data/rules_normalized/2026-01-29-sdi-master-v13/SerialDecodeRule.csv")
PATCHED_CSV = Path("data/rules_normalized/2026-01-29-sdi-master-v13/SerialDecodeRule_Patched.csv")
MAPPINGS_FILE = Path("data/static/hvacdecodertool/serialmappings.json")

def generate_test_cases():
    """
    Generates synthetic serials based on the mappings to test coverage.
    This is a heuristic: we need to find a rule that uses the mapping and generate a matching serial.
    For simplicity, we will just look for rules in the PATCHED set that use the mapping 
    and extract their regex to generate a matching string.
    
    Actually, simpler approach:
    We know which rules were patched. We can try to use the 'example_serials' from those rules,
    or just count how many rules *now have a mapping* vs before.
    
    But to measure 'coverage' in terms of *decoding success*, we ideally need serials.
    Let's stick to the metric of "How many rules are now fully executable?"
    """
    pass

def measure_rule_health():
    if not ORIGINAL_CSV.exists() or not PATCHED_CSV.exists():
        print("Error: Missing CSV files.")
        return

    rules_orig = load_serial_rules_csv(ORIGINAL_CSV)
    rules_patch = load_serial_rules_csv(PATCHED_CSV)
    
    # Metric 1: Rules with 'requires_chart' that now have a mapping
    orig_chart_count = 0
    patch_chart_fixed = 0
    
    # Metric 2: Rules with explicit mapping dictionaries
    orig_map_count = 0
    patch_map_count = 0
    
    for r in rules_orig:
        if "requires_chart" in str(r.date_fields):
            orig_chart_count += 1
        if "mapping" in str(r.date_fields):
            orig_map_count += 1
            
    for r in rules_patch:
        # Check if it was a chart rule that got fixed
        # We need to correlate by style name to be precise, but aggregate is fine for now
        if "mapping" in str(r.date_fields):
            patch_map_count += 1
            
    print(f"--- Coverage Improvement Analysis ---")
    print(f"Total Rules: {len(rules_orig)}")
    print(f"\n[Original Ruleset]")
    print(f"  Rules with explicit mappings: {orig_map_count}")
    print(f"  Rules marked 'requires_chart' (incomplete): {orig_chart_count}")
    
    print(f"\n[Patched Ruleset]")
    print(f"  Rules with explicit mappings: {patch_map_count}")
    print(f"  Improvement: +{patch_map_count - orig_map_count} rules now have lookup tables.")
    
    # Detailed Breakdown by Brand
    print(f"\n[Breakdown by Brand (Patched Mappings)]")
    brand_counts = {}
    for r in rules_patch:
        if "mapping" in str(r.date_fields):
            b = r.brand
            brand_counts[b] = brand_counts.get(b, 0) + 1
            
    for b, count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {b}: {count} rules")

if __name__ == "__main__":
    measure_rule_health()
