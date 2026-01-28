import csv
import sys

def check_column_counts(path):
    print(f"File: {path}")
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)
        print(f"Headers: {headers}")
        
        trane_total = 0
        trane_with_year = 0
        
        for row in reader:
            if len(row) < 11: continue
            
            make = row[7].upper()
            year = row[10].strip()
            
            if "TRANE" in make:
                trane_total += 1
                if year and year != "":
                    trane_with_year += 1
                    
        print(f"Total Trane: {trane_total}")
        print(f"Trane with KnownYear: {trane_with_year}")

if __name__ == "__main__":
    check_column_counts(sys.argv[1])
# NOTE: Archived one-off investigation script (moved 2026-01-28).
