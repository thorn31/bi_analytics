
import csv
from pathlib import Path

updates = {
    "ALPARC IV CITYGATE OPERATING": {"website": "", "naics": "531120", "detail": "Lessors of Nonresidential Buildings", "status": "Deferred", "rationale": "Property operating entity for Citygate Commerce Center."}, 
    "ALPARC IV CRAMER CREEK OPERATING": {"website": "", "naics": "531120", "detail": "Lessors of Nonresidential Buildings", "status": "Deferred", "rationale": "Property operating entity for Cramer Creek office park."}, 
    "ALPLA": {"website": "alpla.com", "naics": "326199", "detail": "All Other Plastics Product Manufacturing", "status": "Verified", "rationale": "Official corporate website found."}, 
    "ALSTOM": {"website": "alstom.com", "naics": "336510", "detail": "Railroad Rolling Stock Manufacturing", "status": "Verified", "rationale": "Official corporate website found."}, 
    "ALTA REFRIGERATION": {"website": "altarefrigeration.com", "naics": "238220", "detail": "Plumbing, Heating, and Air-Conditioning Contractors", "status": "Verified", "rationale": "Official website found for commercial refrigeration contractor."}, 
    "AMANO CINCINNATI": {"website": "amanocincinnati.com", "naics": "333999", "detail": "All Other Miscellaneous General Purpose Machinery Manufacturing", "status": "Verified", "rationale": "Manufacturer of parking and security systems."}, 
    "AMERICAN SOCIETY FOR CLINICAL PATHOLOGY": {"website": "ascp.org", "naics": "813920", "detail": "Professional Organizations", "status": "Verified", "rationale": "Official professional association website."}, 
    "AMMEGA US DBA MIDWEST INDUSTRIAL RUBBER": {"website": "mir-belting.com", "naics": "326220", "detail": "Rubber and Plastics Hoses and Belting Manufacturing", "status": "Verified", "rationale": "Official website for industrial belting manufacturer."}, 
    "ANKAA GLOBAL LOGISTICS": {"website": "ankaaglobal.com", "naics": "488510", "detail": "Freight Transportation Arrangement", "status": "Verified", "rationale": "Official logistics company website."}, 
    "ANSON LOGISTICS ASSETS": {"website": "", "naics": "488510", "detail": "Freight Transportation Arrangement", "status": "Deferred", "rationale": "No specific website found for this asset-holding entity."}, 
    "ARGOSY CASINO HOTEL": {"website": "hollywoodindiana.com", "naics": "721120", "detail": "Casino Hotels", "status": "Verified", "rationale": "Official website for Hollywood Casino Lawrenceburg (formerly Argosy)."}, 
    "ARK BROOKVALE": {"website": "", "naics": "531120", "detail": "Lessors of Nonresidential Buildings", "status": "Deferred", "rationale": "Likely a property holding entity for specific Charlotte property."}, 
    "ART GEISSLER": {"website": "remax.com", "naics": "531210", "detail": "Offices of Real Estate Agents and Brokers", "status": "Verified", "rationale": "Personal real estate agent page on Re/Max found."}, 
    "ARTS RENTAL": {"website": "artsrental.com", "naics": "532289", "detail": "All Other Consumer Goods Rental", "status": "Verified", "rationale": "Official event and party rental website."}, 
    "ARVATO DIGITAL USA": {"website": "arvato.com", "naics": "541614", "detail": "Process, Physical Distribution, and Logistics Consulting Services", "status": "Verified", "rationale": "Official corporate website for digital solutions/fulfillment."}, 
    "ASPHALT INSTITUTE": {"website": "asphaltinstitute.org", "naics": "813910", "detail": "Business Associations", "status": "Verified", "rationale": "Official trade association website."}, 
    "ATKINS AND PEARCE": {"website": "atkinsandpearce.com", "naics": "313220", "detail": "Narrow Fabric Mills and Schiffli Machine Embroidery", "status": "Verified", "rationale": "Official textile manufacturer website."}, 
    "ATKINS AND STANG": {"website": "", "naics": "238210", "detail": "Electrical Contractors and Other Wiring Installation Contractors", "status": "Deferred", "rationale": "No dedicated website found beyond directory listings."}, 
    "ATRIUM LP": {"website": "", "naics": "531120", "detail": "Lessors of Nonresidential Buildings", "status": "Deferred", "rationale": "Property entity for The Atrium office building in Knoxville."}, 
    "AUDI KNOXVILLE": {"website": "audiknoxville.com", "naics": "441110", "detail": "New Car Dealers", "status": "Verified", "rationale": "Official dealership website."} 
}

path = Path("output/work/enrichment/MasterEnrichmentQueue.csv")
temp_path = path.with_suffix(".tmp.csv")

with path.open("r", encoding="utf-8-sig", newline="") as infile, \
     temp_path.open("w", encoding="utf-8-sig", newline="") as outfile:
    
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    
    for row in reader:
        # Match against Canonical to be safe
        canonical = row["Master Customer Name Canonical"]
        if canonical in updates:
            up = updates[canonical]
            if up["status"] == "Verified":
                row["Company Website (Approved)"] = up["website"]
                row["NAICS (Approved)"] = up["naics"]
                row["Industry Detail (Approved)"] = up["detail"]
                row["Enrichment Status"] = "Verified"
                row["Enrichment Confidence"] = "High"
                row["Enrichment Rationale"] = up["rationale"]
                row["Enrichment Source"] = "Analyst"
            else:
                row["Enrichment Status"] = "Deferred"
                row["Enrichment Rationale"] = up["rationale"]
                
        writer.writerow(row)

temp_path.replace(path)
print("Updated queue successfully for Batch 4.")
