import csv
import sys

def main():
    limit = 20
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass

    path = "output/final/SegmentationReviewWorklist.csv"
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        candidates = []
        for row in reader:
            # Skip if already marked Final
            if (row.get("Status") or "").strip() == "Final":
                continue
            # Skip if already Queued (unless we want to re-do them, but let's find fresh ones first)
            # if (row.get("Status") or "").strip() == "Queued":
            #    continue
            
            candidates.append(row["Master Customer Name"])
            if len(candidates) >= limit:
                break
    
    print("\n".join(candidates))

if __name__ == "__main__":
    main()

