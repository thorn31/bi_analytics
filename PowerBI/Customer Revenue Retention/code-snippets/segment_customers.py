import csv
import re
import os
import difflib

# Set paths relative to script
INPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "CustomerLastBillingDate.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "CustomerSegmentation.csv")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "CustomerDeduplicationLog.csv")

def get_segment(name):
    name_lower = name.lower()

    # Define helper indicators
    rel_pat = r'\b(church|temple|mosque|synagogue|ministry|baptist|catholic|methodist|lutheran|presbyterian|episcopal|god|saint|st\.|bible|christian|bishop|our lady|notre dame|sacred heart|holy|jesuit|bethlehem|trinity|immaculate|zion|covenant|grace|faith|christ|nazarene|apostolic|assembly of god|archdiocese)\b'
    is_religious_word = re.search(rel_pat, name_lower)
    
    sch_pat = r'\b(school|academy|prep|institute|university|college|seminary|education|learning|primary|elementary|middle school|high school|k-12|collegiate)\b'
    is_school_word = re.search(sch_pat, name_lower)
    
    # 1. Private Schools
    if re.search(r'\b(academy|prep|university|college|seminary|collegiate)\b', name_lower):
        return "Private Schools"
    if is_school_word and is_religious_word:
        return "Private Schools"

    # 2. Public Schools
    if re.search(r'\b(isd|sch dist|public school|elementary|high school|middle school|school district|schools|city school|county school)\b', name_lower):
        return "Public Schools"

    # 3. Religious
    if is_religious_word:
        return "Religious"
        
    # 4. Medical
    if re.search(r'\b(hospital|clinic|health|medical|physician|doctor|dr\.|dental|dentist|surgery|veterinary|vet|healthcare|urgent care|care|dentures?|pharmacy|rehab|recovery|senior living|nursing|rehabilitation|amerimed|pathology|lab|laboratory)\b', name_lower):
        return "Medical"

    # 5. Hospitality
    if re.search(r'\b(hotel|inn|suites|resort|motel|lodge|aloft|marriott|hilton|holiday inn|staybridge|hampton|courtyard|residence inn|fairfield)\b', name_lower):
        return "Hospitality"

    # 6. Municipal
    if re.search(r'\b(city|county|dept|department|state of|fiscal court|jail|police|fire|library|municipal|govt|authority|township)\b', name_lower):
        return "Municipal"

    # 7. Data Center
    if re.search(r'\b(data center|compute|hosting|server|cloud|colocation)\b', name_lower):
        return "Data Center"

    # 8. Industrial
    if re.search(r'\b(mfg|manufacturing|industrial|plant|factory|works|production|packaging|steel|chemical|distributing|logistics|warehouse|engineering|tools|systems|construction|contractor|builders|auto|automotive|parts|metal|plastic|energy|machining|tool|trucking|cargo|freight|transport|shipping|supply chain|distribution)\b', name_lower):
        return "Industrial"

    # 9. Office
    if re.search(r'\b(inc|llc|corp|co|company|group|associates|partners|bank|financial|insurance|realty|properties|law|firm|holding|services|management|solutions|partnership|llp)\b', name_lower):
        return "Office"
    
    # 10. Real Estate Management
    if re.search(r'\b(cbre|jll|colliers|cushman|wakefield|nai|avison young|foundry commercial|equity|prologis|duke realty)\b', name_lower):
        return "Office"

    return "Other"

def get_master_name(name):
    name = name.upper()
    name = name.replace('&', ' AND ')
    name = name.replace('+', ' AND ')
    if name.startswith('THE '):
        name = name[4:]
    suffix_pat = r'\b(LLC|INC|CO|CORP|L\.L\.C\.|INC\.|COMPANY|LIMITED|LTD|INCORPORATED|CORPORATION)\b'
    name = re.sub(suffix_pat, '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def clean_co_name(name):
    match = re.search(r'\s+(C/O|CO)\s+', name, re.IGNORECASE)
    if match:
        return name[:match.start()].strip()
    return name

def clean_chain_name(name):
    name_upper = name.upper()
    chains = {
        'ORANGETHEORY': 'ORANGETHEORY FITNESS',
        'ORANGE THEORY': 'ORANGETHEORY FITNESS',
        'FLAGSHIP': 'FLAGSHIP HEALTHCARE PROPERTIES',
        'PERFECTION SERVICE': 'PERFECTION SERVICES',
        'PROVIDENCE COMMERCIAL': 'PROVIDENCE COMMERCIAL REAL ESTATE',
        'WALMART': 'WALMART',
        'CINTAS': 'CINTAS',
        'STARBUCKS': 'STARBUCKS',
        'AMAZON': 'AMAZON',
        'CVS': 'CVS',
        'WALGREENS': 'WALGREENS',
        'DOLLAR GENERAL': 'DOLLAR GENERAL',
        'TARGET': 'TARGET',
        'KROGER': 'KROGER',
        'LOWES': 'LOWES',
        'HOME DEPOT': 'HOME DEPOT',
        'MCDONALDS': 'MCDONALDS',
        'BURGER KING': 'BURGER KING',
        'WENDYS': 'WENDYS',
        'TACO BELL': 'TACO BELL',
        'SUBWAY': 'SUBWAY',
        'DOMINOS': 'DOMINOS',
        'PIZZA HUT': 'PIZZA HUT',
        'CHICK-FIL-A': 'CHICK-FIL-A',
        'CHIPOTLE': 'CHIPOTLE',
        'PANERA': 'PANERA BREAD',
        'FEDEX': 'FEDEX',
        'UPS': 'UPS',
        'USPS': 'US POSTAL SERVICE',
        'FIFTH THIRD': 'FIFTH THIRD BANK',
        'PNC': 'PNC BANK',
        'CHASE': 'CHASE BANK',
        'HUNTINGTON': 'HUNTINGTON BANK',
        'WELLTOWER': 'WELLTOWER',
        'CUSHMAN': 'CUSHMAN AND WAKEFIELD',
        'CBRE': 'CBRE',
        'COLLIERS': 'COLLIERS',
        'JLL': 'JLL'
    }
    for key, master in chains.items():
        if name_upper.startswith(key):
            return master
    return name

def dedup_names(processed_rows):
    def get_comparison_key(name):
        noise_words = r'\b(INC|LLC|COMPANY|CORP|LTD|LIMITED|INCORPORATED|THE)\b'
        core_name = re.sub(noise_words, '', name).strip()
        return core_name

    unique_names = list(set(row['Master Customer Name'] for row in processed_rows if row['Master Customer Name']))
    unique_names.sort(key=len)
    
    canonical_map = {}
    assigned_names = set()

    for name in unique_names:
        if name in assigned_names:
            continue
        canonical_map[name] = name
        assigned_names.add(name)
        
        name_key = get_comparison_key(name)
        
        for candidate in unique_names:
            if candidate in assigned_names:
                continue
            candidate_key = get_comparison_key(candidate)
            
            if name_key == candidate_key:
                canonical_map[candidate] = name
                assigned_names.add(candidate)
                continue
            
            similarity = difflib.SequenceMatcher(None, name_key, candidate_key).ratio()
            if similarity > 0.95: 
                canonical_map[candidate] = name
                assigned_names.add(candidate)

    for row in processed_rows:
        original_master = row['Master Customer Name']
        if original_master in canonical_map:
            row['Master Customer Name'] = canonical_map[original_master]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file not found at {INPUT_FILE}")
        return

    processed_rows = []
    with open(INPUT_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            original_name = row['Customer Name']
            primary_name = clean_co_name(original_name)
            master_name = get_master_name(primary_name)
            master_name = clean_chain_name(master_name)
            
            # Initial segment based on master
            segment = get_segment(master_name)

            processed_rows.append({
                'Customer Key': row['Customer Key'],
                'Original Name': original_name,
                'Master Customer Name': master_name,
                'Segment': segment,
                'Source': row['Source']
            })

    # Deduplicate
    dedup_names(processed_rows)
    
    # FINAL Segmentation and Log generation
    log_rows = []
    processed_rows.sort(key=lambda x: x['Master Customer Name'])
    
    for row in processed_rows:
        # Re-run segment on final master
        row['Segment'] = get_segment(row['Master Customer Name'])
        
        orig = row['Original Name']
        final = row['Master Customer Name']
        
        # Track evolution
        s1_co = clean_co_name(orig)
        s2_clean = get_master_name(s1_co)
        s3_chain = clean_chain_name(s2_clean)
        
        change_type = []
        if s1_co.upper() != orig.upper().strip() and ("C/O" in orig.upper() or "CO " in orig.upper()):
            change_type.append("C/O Strip")
        if s3_chain != s2_clean:
            change_type.append("Chain Rule")
        if final != s3_chain:
            change_type.append("Fuzzy Merge")
            
        if change_type:
            log_rows.append({
                'Master Customer Name': final,
                'Original Name': orig,
                'Initial Clean Name': s3_chain,
                'Type': ", ".join(change_type)
            })

    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Customer Key', 'Original Name', 'Master Customer Name', 'Segment', 'Source'])
        writer.writeheader()
        writer.writerows(processed_rows)

    with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Master Customer Name', 'Original Name', 'Initial Clean Name', 'Type'])
        writer.writeheader()
        writer.writerows(log_rows)

    print(f"Processed {len(processed_rows)} rows.")
    print(f"Saved main output to {OUTPUT_FILE}")
    print(f"Saved deduplication log to {LOG_FILE}")

if __name__ == "__main__":
    main()