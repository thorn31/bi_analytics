
import csv
import sys
from pathlib import Path

# Data to update
updates = {
    "10% Cabinetry": {"website": "10percentcabinetry.com", "naics": "238350", "detail": "Finish Carpentry Contractors", "status": "Verified"},
    "2NDS IN Building Material": {"website": "southeasternsalvage.com", "naics": "444190", "detail": "Other Building Material Dealers", "status": "Verified", "notes": "DBA Southeastern Salvage"},
    "3001 Highland Partnership": {"website": "psychotherapycincinnati.com", "naics": "531120", "detail": "Lessors of Nonresidential Buildings", "status": "Verified", "notes": "Property owner for Cincinnati Center For Psychotherapy & Psychoanalysis"},
    "3665 Mallory Jv": {"website": "", "naics": "531120", "detail": "Lessors of Nonresidential Buildings", "status": "Deferred", "rationale": "No specific website found. Likely a single-asset property entity."},
    "3D Technical Services": {"website": "3-dtechnicalservices.com", "naics": "541330", "detail": "Engineering Services", "status": "Verified"},
    "4J Redevelopment": {"website": "coreredevelopment.com", "naics": "531110", "detail": "Lessors of Residential Buildings", "status": "Verified", "notes": "Associated with Core Redevelopment"},
    "A Childs Hope Intl": {"website": "achildshopeintl.org", "naics": "624110", "detail": "Child and Youth Services", "status": "Verified"},
    "A T Redevelopment": {"website": "coreredevelopment.com", "naics": "531110", "detail": "Lessors of Residential Buildings", "status": "Verified", "notes": "Associated with Core Redevelopment"},
    "Abc Automotive Systems": {"website": "abctechnologies.com", "naics": "336390", "detail": "Other Motor Vehicle Parts Manufacturing", "status": "Verified"},
    "Abloom Florist": {"website": "abloomflorist.net", "naics": "453110", "detail": "Florists", "status": "Verified"},
    "Absolute Machine Tools": {"website": "absolutemachine.com", "naics": "423830", "detail": "Industrial Machinery and Equipment Merchant Wholesalers", "status": "Verified"},
    "Accella Tire Fill Systems": {"website": "carlisletyrfil.com", "naics": "326299", "detail": "All Other Rubber Product Manufacturing", "status": "Verified", "notes": "Rebranded to Carlisle TyrFil"},
    "Accurate Mechanical Solutions": {"website": "", "naics": "238220", "detail": "Plumbing, Heating, and Air-Conditioning Contractors", "status": "Deferred", "rationale": "No distinct website found. Shared phone with Dr Plumbing Heating And Cooling."},
    "Activate Games": {"website": "playactivate.com", "naics": "713120", "detail": "Amusement Arcades", "status": "Verified"},
    "Advanced Agrilytics": {"website": "advancedagrilytics.com", "naics": "541990", "detail": "All Other Professional, Scientific, and Technical Services", "status": "Verified"},
    "Advanced Lableworx": {"website": "advancedlabelworx.com", "naics": "323111", "detail": "Commercial Printing (except Screen and Books)", "status": "Verified"},
    "Advantage Engineering": {"website": "advantageengineering.com", "naics": "333249", "detail": "Other Industrial Machinery Manufacturing", "status": "Verified"},
    "Aegis Protective Services": {"website": "aegis-ps.com", "naics": "561612", "detail": "Security Guards and Patrol Services", "status": "Verified"},
    "Aerospace Lubricants": {"website": "aerospacelubricants.com", "naics": "324191", "detail": "Petroleum Lubricating Oil and Grease Manufacturing", "status": "Verified"},
    "Afc Urgent Care": {"website": "afcurgentcare.com", "naics": "621493", "detail": "Freestanding Ambulatory Surgical and Emergency Centers", "status": "Verified"}
}

path = Path("Customer Segmentation/output/work/enrichment/MasterEnrichmentQueue.csv")
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
