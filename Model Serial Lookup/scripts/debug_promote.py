from pathlib import Path
import csv
import sys
from msl.decoder.normalize import normalize_text

def debug_promotion(base_dir, cand_path):
    base_ruleset = Path(base_dir)
    serial_path = base_ruleset / "SerialDecodeRule.csv"
    
    with serial_path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    
    base_brands = {normalize_text(r.get("brand")) for r in rows}
    print(f"Base brands count: {len(base_brands)}")
    print(f"Is LOCHINVAR in base? {'LOCHINVAR' in base_brands}")
    
    cand_path = Path(cand_path)
    if not cand_path.exists():
        print(f"Candidate file not found: {cand_path}")
        return

    with cand_path.open("r", encoding="utf-8") as f:
        cands = list(csv.DictReader(f))
        
    for c in cands:
        raw = c.get("raw_make")
        if raw == "LOCHENVAR":
            print(f"\nChecking candidate: {c}")
            canonical = normalize_text(c.get("canonical_brand") or c.get("suggested_brand"))
            print(f"Canonical normalized: '{canonical}'")
            
            if canonical not in base_brands:
                print("FAIL: canonical not in base_brands")
            else:
                print("PASS: canonical in base_brands")
                
            sim = float(c.get("similarity"))
            if sim < 0.8:
                print(f"FAIL: similarity {sim} < 0.8")
            else:
                print(f"PASS: similarity {sim} >= 0.8")

if __name__ == "__main__":
    debug_promotion(sys.argv[1], sys.argv[2])
