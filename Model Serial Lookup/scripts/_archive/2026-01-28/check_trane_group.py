import csv
import sys
import re

def normalize_serial(val):
    return re.sub(r"[\s\-_/]+", "", str(val).strip().upper())

def check_group(path):
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        
        examples = []
        for row in reader:
            if "MITSUBISHI" in row['Make'].upper():
                sn = normalize_serial(row['SerialNumber'])
                year = row['KnownManufactureYear'].strip()
                if sn and year:
                    examples.append((sn, year))
        
        print(f"Total Mitsubishi examples: {len(examples)}")
        for sn, yr in examples[:30]:
            print(f"SN: {sn} | KnownYear: {yr}")

if __name__ == "__main__":
    check_group(sys.argv[1])
# NOTE: Archived one-off investigation script (moved 2026-01-28).
