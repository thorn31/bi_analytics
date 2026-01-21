import csv
from pathlib import Path

# Research findings for Batch 9 (30 customers)
updates = {
    "Old Dominion Freight Line": {
        "website": "https://www.odfl.com",
        "naics": "484122",
        "detail": "General Freight Trucking",
        "status": "Verified",
        "rationale": "Confirmed major freight carrier."
    },
    "Old National Bank": {
        "website": "https://www.oldnational.com",
        "naics": "522110",
        "detail": "Commercial Banking",
        "status": "Verified",
        "rationale": "Confirmed regional bank."
    },
    "Old Town Trolley Tours of Nashville": {
        "website": "https://www.trolleytours.com/nashville",
        "naics": "487110",
        "detail": "Sightseeing Transportation",
        "status": "Verified",
        "rationale": "Confirmed Nashville trolley tour operator."
    },
    "Omni Nashville Hotel": {
        "website": "https://www.omnihotels.com",
        "naics": "721110",
        "detail": "Hotel and Hospitality",
        "status": "Verified",
        "rationale": "Confirmed luxury hotel in Nashville."
    },
    "On The Border": {
        "website": "https://www.ontheborder.com",
        "naics": "722511",
        "detail": "Mexican Restaurant Chain",
        "status": "Verified",
        "rationale": "Confirmed restaurant brand."
    },
    "On The Border Mexican Grill and Cantina": {
        "website": "https://www.ontheborder.com",
        "naics": "722511",
        "detail": "Mexican Restaurant Chain",
        "status": "Verified",
        "rationale": "Confirmed restaurant brand."
    },
    "One Dutch Partners": {
        "status": "Deferred",
        "rationale": "Ambiguous Entity",
        "notes": "No direct website found. Possibly 'One Dutch' or 'One Equity Partners'. Deferred to avoid misattribution."
    },
    "One Holland": {
        "website": "https://oneholland.com",
        "naics": "722511",
        "detail": "Restaurant Franchise Group",
        "status": "Verified",
        "rationale": "Confirmed restaurant management group."
    },
    "One Stop Medical": {
        "status": "Deferred",
        "rationale": "Generic Name",
        "notes": "Multiple clinics with this name exist in TN, GA, WA. No specific location provided to confirm match."
    },
    "One Touch Vending": {
        "website": "https://onetouchdrinks.com",
        "naics": "454210",
        "detail": "Vending Machine Operators",
        "status": "Verified",
        "rationale": "Confirmed One Touch Drinks/Vending."
    },
    "Onesource Water": {
        "status": "Deferred",
        "rationale": "Ambiguous Entity",
        "notes": "Multiple potential matches: '1sourcewater.com' vs 'onesourcewater.net'. Deferred for disambiguation."
    },
    "Onsite Retail Group": {
        "website": "https://onsiteretailgroup.com",
        "naics": "531210",
        "detail": "Commercial Real Estate Brokerage",
        "status": "Verified",
        "rationale": "Confirmed Cincinnati retail real estate firm."
    },
    "Opus Packaging": {
        "website": "https://opuspackaging.com",
        "naics": "322211",
        "detail": "Corrugated Packaging Manufacturing",
        "status": "Verified",
        "rationale": "Confirmed packaging manufacturer."
    },
    "Oral Facial Surgery": {
        "status": "Deferred",
        "rationale": "Generic Name",
        "notes": "Common practice name. 'Southern Oral Facial Surgery' is in Nashville, but cannot confirm without more specific match."
    },
    "Oral Facial Surgery Center": {
        "status": "Deferred",
        "rationale": "Generic Name",
        "notes": "Generic name used by multiple providers."
    },
    "Orangetheory Fitness": {
        "website": "https://www.orangetheory.com",
        "naics": "713940",
        "detail": "Fitness Center Chain",
        "status": "Verified",
        "rationale": "Confirmed major fitness brand."
    },
    "OReilly Auto Parts": {
        "website": "https://www.oreillyauto.com",
        "naics": "441310",
        "detail": "Auto Parts Retail",
        "status": "Verified",
        "rationale": "Confirmed major auto parts retailer."
    },
    "Orr Protection Systems": {
        "website": "https://www.orrprotection.com",
        "naics": "238210",
        "detail": "Fire Protection Systems",
        "status": "Verified",
        "rationale": "Confirmed fire protection specialist."
    },
    "Orthocincy": {
        "website": "https://orthocincy.com",
        "naics": "621111",
        "detail": "Orthopaedic Medical Practice",
        "status": "Verified",
        "rationale": "Confirmed major regional orthopaedic group."
    },
    "Orthopedic Associates of SW Ohio": {
        "website": "https://oadoctors.org",
        "naics": "621111",
        "detail": "Orthopaedic Medical Practice",
        "status": "Verified",
        "rationale": "Confirmed SW Ohio practice."
    },
    "Orthopedic Institute of Dayton": {
        "website": "https://orthodayton.com",
        "naics": "621111",
        "detail": "Orthopaedic Medical Practice",
        "status": "Verified",
        "rationale": "Confirmed Dayton practice."
    },
    "Ossur North America": {
        "website": "https://www.ossur.com",
        "naics": "339113",
        "detail": "Prosthetics and Orthotics Manufacturing",
        "status": "Verified",
        "rationale": "Confirmed North American division of Ossur."
    },
    "Osterwisch Company": {
        "website": "https://www.osterwisch.com",
        "naics": "238210",
        "detail": "Electrical and Mechanical Contractor",
        "status": "Verified",
        "rationale": "Confirmed Cincinnati contractor."
    },
    "Otics": {
        "website": "https://www.oticsusa.com",
        "naics": "336390",
        "detail": "Automotive Parts Manufacturing",
        "status": "Verified",
        "rationale": "Confirmed OTICS USA (Morristown, TN)."
    },
    "Otics USA": {
        "website": "https://www.oticsusa.com",
        "naics": "336390",
        "detail": "Automotive Parts Manufacturing",
        "status": "Verified",
        "rationale": "Confirmed OTICS USA (Morristown, TN)."
    },
    "Outback Steakhouse": {
        "website": "https://www.outback.com",
        "naics": "722511",
        "detail": "Steakhouse Restaurant Chain",
        "status": "Verified",
        "rationale": "Confirmed restaurant brand."
    },
    "Outdoor Ventures": {
        "website": "https://outdoorventures.us",
        "naics": "713990",
        "detail": "Adventure Park Design and Construction",
        "status": "Verified",
        "rationale": "Confirmed Fairfield, OH adventure park builder."
    },
    "Overhead Door Company of Northern KY": {
        "website": "https://www.overheaddooronline.com",
        "naics": "238290",
        "detail": "Garage Door Installation and Service",
        "status": "Verified",
        "rationale": "Confirmed regional Overhead Door franchise."
    },
    "Owens Corning": {
        "website": "https://www.owenscorning.com",
        "naics": "327993",
        "detail": "Insulation and Roofing Manufacturing",
        "status": "Verified",
        "rationale": "Confirmed major building materials manufacturer."
    },
    "Oxford Physical Therapy": {
        "website": "https://www.oxfordpt.com",
        "naics": "621340",
        "detail": "Physical Therapy Clinics",
        "status": "Verified",
        "rationale": "Confirmed Cincinnati physical therapy group."
    }
}

path = Path("output/work/enrichment/MasterEnrichmentQueue.csv")
temp_path = path.with_suffix(".tmp.csv")

if not path.exists():
    print(f"Error: {path} not found.")
    exit(1)

with path.open("r", encoding="utf-8-sig", newline="") as infile, \
     temp_path.open("w", encoding="utf-8-sig", newline="") as outfile:
    
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    
    for row in reader:
        name = row["Master Customer Name"].strip()
        if name in updates:
            up = updates[name]
            if up["status"] == "Verified":
                row["Company Website (Approved)"] = up["website"]
                row["NAICS (Approved)"] = up["naics"]
                row["Industry Detail (Approved)"] = up["detail"]
                row["Enrichment Status"] = "Verified"
                row["Enrichment Source"] = "Analyst"
                row["Enrichment Rationale"] = up["rationale"]
            else:
                row["Enrichment Status"] = "Deferred"
                row["Enrichment Rationale"] = up.get("rationale", "")
            
            if "notes" in up:
                row["Notes"] = up["notes"]
                
        writer.writerow(row)

temp_path.replace(path)
print(f"Updated {len(updates)} records in queue successfully.")