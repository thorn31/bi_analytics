import csv
import sys

def check_trane_matches(path):
    print(f"Checking Trane results in {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        matches = 0
        total_trane = 0
        samples = []
        
        for row in reader:
            if row.get('DetectedBrand') == 'TRANE':
                total_trane += 1
                year = row.get('ManufactureYear', '').strip()
                style = row.get('MatchedSerialStyle', '').strip()
                sn = row.get('SerialNumber', '').strip()
                
                if style:
                    matches += 1
                
                if len(samples) < 20 and not style and sn:
                    samples.append((sn, row.get('KnownManufactureYear', '')))
                    
        print(f"Total Trane Rows: {total_trane}")
        print(f"Total Decoded: {matches}")
        print("\n--- Samples of Non-Decoded Trane ---")
        for sn, known in samples:
            print(f"SN: {sn} | Known: {known}")

if __name__ == "__main__":
    check_trane_matches(sys.argv[1])
# NOTE: Archived one-off investigation script (moved 2026-01-28).
