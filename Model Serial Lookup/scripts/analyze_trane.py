import csv
import sys

def analyze_trane_failures(csv_path):
    print(f"Analyzing {csv_path} for TRANE failures...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        failures = []
        decoded_wrong = []
        not_decoded = []
        
        for row in reader:
            if row.get('DetectedBrand') != 'TRANE':
                continue
                
            serial = row.get('SerialNumber', '').strip()
            if not serial:
                continue
                
            known = row.get('KnownManufactureYear', '').strip()
            decoded = row.get('ManufactureYear', '').strip()
            
            # Normalize known year (handle "2015" vs "15" vs "2015.0")
            if known.endswith('.0'): known = known[:-2]
            
            if not known:
                continue
                
            if not decoded:
                not_decoded.append((serial, known, row.get('ModelNumber', '')))
            elif decoded != known:
                decoded_wrong.append((serial, known, decoded, row.get('ModelNumber', '')))
                
    print(f"\n--- TRANE Summary ---")
    print(f"Total Not Decoded (with known year): {len(not_decoded)}")
    print(f"Total Decoded Wrong: {len(decoded_wrong)}")
    
    print("\n--- Sample: Not Decoded (Top 20) ---")
    print("Serial | Known Year | Model")
    for s, k, m in not_decoded[:20]:
        print(f"{s} | {k} | {m}")
        
    print("\n--- Sample: Decoded Wrong (Top 20) ---")
    print("Serial | Known Year | Decoded Year | Model")
    for s, k, d, m in decoded_wrong[:20]:
        print(f"{s} | {k} | {d} | {m}")

if __name__ == "__main__":
    analyze_trane_failures(sys.argv[1])
