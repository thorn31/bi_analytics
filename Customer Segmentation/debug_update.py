import csv
from pathlib import Path

path = Path("output/work/enrichment/MasterEnrichmentQueue.csv")
temp_path = path.with_suffix(".debug.csv")

with path.open("r", encoding="utf-8-sig", newline="") as infile, \
     temp_path.open("w", encoding="utf-8-sig", newline="") as outfile:
    
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    
    for row in reader:
        if row["Master Customer Name"].strip() == "Nashville Office 1":
            print(f"Found it! Old Website: '{row.get('Company Website (Approved)', 'MISSING')}'")
            row["Company Website (Approved)"] = "https://TEST.com"
            print(f"Set to: '{row['Company Website (Approved)']}'")
        writer.writerow(row)

print("Finished.")
