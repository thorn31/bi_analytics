import csv
import sys

def print_headers(path):
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)
        print(f"Headers for {path}:")
        for i, h in enumerate(headers):
            print(f"{i}: {repr(h)}")

if __name__ == "__main__":
    print_headers(sys.argv[1])
# NOTE: Archived one-off investigation script (moved 2026-01-28).
