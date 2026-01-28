import csv
import sys

def analyze_trane_stats(csv_path):
    print(f"Analyzing {csv_path}...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        total = 0
        has_known = 0
        decoded = 0
        
        sample_missing_known = []
        
        for row in reader:
            if row.get('DetectedBrand') != 'TRANE':
                continue
            total += 1
            
            known = row.get('KnownManufactureYear', '').strip()
            dec = row.get('ManufactureYear', '').strip()
            
            if known:
                has_known += 1
            else:
                if len(sample_missing_known) < 5:
                    sample_missing_known.append(row.get('SerialNumber', ''))
            
            if dec:
                decoded += 1
                
    print(f"Total Trane: {total}")
    print(f"With Known Year: {has_known}")
    print(f"Decoded Year: {decoded}")
    print(f"Sample Serial (Missing Known Year): {sample_missing_known}")

if __name__ == "__main__":
    analyze_trane_stats(sys.argv[1])
# NOTE: Archived one-off investigation script (moved 2026-01-28).
