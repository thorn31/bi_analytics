
import csv
import sys
from pathlib import Path

# Data to update
updates = {
    "Affordable Dentures": {"website": "affordabledentures.com", "naics": "621210", "detail": "Offices of Dentists", "status": "Verified"},
    "Affordable Service Solutions": {"website": "affordableservicesolutions.com", "naics": "238220", "detail": "Plumbing, Heating, and Air-Conditioning Contractors", "status": "Verified"},
    "Ag Stones": {"website": "agstones.com", "naics": "423320", "detail": "Brick, Stone, and Related Construction Material Merchant Wholesalers", "status": "Verified"},
    "Agellan Commercial Reit": {"website": "agellan.com", "naics": "531120", "detail": "Lessors of Nonresidential Buildings", "status": "Verified"},
    "Ahc Clarksville": {"website": "ahcseniorcare.com", "naics": "623110", "detail": "Nursing Care Facilities (Skilled Nursing Facilities)", "status": "Verified"},
    "Aicholtz": {"website": "", "naics": "531120", "detail": "Lessors of Nonresidential Buildings", "status": "Deferred", "rationale": "No specific website. Permitting records suggest a property holding entity."},
    "Air Gas": {"website": "airgas.com", "naics": "325120", "detail": "Industrial Gas Manufacturing", "status": "Verified"},
    "Aisin Automotive": {"website": "aisinauto.com", "naics": "336310", "detail": "Motor Vehicle Gasoline Engine and Engine Parts Manufacturing", "status": "Verified"},
    "Aisin World of America": {"website": "aisinworld.com", "naics": "423120", "detail": "Motor Vehicle Supplies and New Parts Merchant Wholesalers", "status": "Verified"},
    "All Eleven": {"website": "", "naics": "531120", "detail": "Lessors of Nonresidential Buildings", "status": "Deferred", "rationale": "Real estate development entity without a public-facing website."},
    "All Occasions Equip Rentals": {"website": "aorents.com", "naics": "532289", "detail": "All Other Consumer Goods Rental", "status": "Verified", "notes": "DBA All Occasions Event Rental"},
    "All Pro Commercial Services": {"website": "allproifm.com", "naics": "561720", "detail": "Janitorial Services", "status": "Verified"},
    "All Pro Parking": {"website": "allproparking.com", "naics": "812930", "detail": "Parking Lots and Garages", "status": "Verified"},
    "Alliance Technical Group": {"website": "alliancetechnicalgroup.com", "naics": "541330", "detail": "Engineering Services", "status": "Verified"},
    "Allison Abrasives": {"website": "allisonabrasives.com", "naics": "327910", "detail": "Abrasive Product Manufacturing", "status": "Verified"},
    "Alparc I Parkway Operating": {"website": "", "naics": "531110", "detail": "Lessors of Residential Buildings", "status": "Deferred", "rationale": "Likely a property-specific operating entity for an apartment complex."},
    "Alparc II Creek Run Operating": {"website": "", "naics": "531110", "detail": "Lessors of Residential Buildings", "status": "Deferred", "rationale": "Likely a property-specific operating entity for an apartment complex."},
    "Alparc II Dearborn Park Operating": {"website": "", "naics": "531110", "detail": "Lessors of Residential Buildings", "status": "Deferred", "rationale": "Likely a property-specific operating entity for an apartment complex."},
    "Alparc II Lakeview Operating": {"website": "", "naics": "531110", "detail": "Lessors of Residential Buildings", "status": "Deferred", "rationale": "Likely a property-specific operating entity for an apartment complex."},
    "Alparc II Tuller Ridge Operating": {"website": "", "naics": "531110", "detail": "Lessors of Residential Buildings", "status": "Deferred", "rationale": "Likely a property-specific operating entity for an apartment complex."}
}

path = Path("output/work/enrichment/MasterEnrichmentQueue.csv")
temp_path = path.with_suffix(".tmp.csv")

with path.open("r", encoding="utf-8-sig", newline="") as infile, \
     temp_path.open("w", encoding="utf-8-sig", newline="") as outfile:
    
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    
    for row in reader:
        name = row["Master Customer Name"]
        if name in updates:
            up = updates[name]
            if up["status"] == "Verified":
                row["Company Website (Approved)"] = up["website"]
                row["NAICS (Approved)"] = up["naics"]
                row["Industry Detail (Approved)"] = up["detail"]
                row["Enrichment Status"] = "Verified"
                row["Enrichment Source"] = "Analyst"
            else:
                row["Enrichment Status"] = "Deferred"
                row["Enrichment Rationale"] = up.get("rationale", "")
            
            if "notes" in up:
                row["Notes"] = up["notes"]
                
        writer.writerow(row)

temp_path.replace(path)
print("Updated queue successfully.")
