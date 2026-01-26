import csv
import sys
import re

def normalize_text(value):
    return " ".join(str(value).split()).strip().upper()

def normalize_serial(value):
    return re.sub(r"[\s\-_/]+", "", normalize_text(value))

def signature(serial):
    s = normalize_serial(serial)
    out = []
    for ch in s:
        if "A" <= ch <= "Z":
            out.append("A")
        elif ch.isdigit():
            out.append("N")
        else:
            out.append("?")
    return "".join(out)

def debug_signatures(path):
    print(f"Analyzing signatures in {path}...")
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        trane_sigs = {}
        
        for row in reader:
            make = normalize_text(row.get('Make', ''))
            if 'TRANE' not in make:
                continue
                
            serial = row.get('SerialNumber', '')
            known = row.get('KnownManufactureYear', '')
            
            if not serial or not known:
                continue
                
            sig = signature(serial)
            key = (len(normalize_serial(serial)), sig)
            
            if key not in trane_sigs:
                trane_sigs[key] = 0
            trane_sigs[key] += 1
            
    print("\n--- Trane Signatures ---")
    for (length, sig), count in sorted(trane_sigs.items(), key=lambda x: -x[1]):
        print(f"Len: {length}, Sig: {sig}, Count: {count}")

if __name__ == "__main__":
    debug_signatures(sys.argv[1])
