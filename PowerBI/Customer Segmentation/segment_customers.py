import csv
import re
import os
import difflib

# Set paths relative to script
INPUT_FILE = os.path.join(os.path.dirname(__file__), "input", "CustomerLastBillingDate.csv")
OVERRIDE_FILE = os.path.join(os.path.dirname(__file__), "input", "ManualOverrides.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "output", "CustomerSegmentation.csv")
LOG_FILE = os.path.join(os.path.dirname(__file__), "output", "CustomerDeduplicationLog.csv")

def load_overrides():
    overrides = {}
    if os.path.exists(OVERRIDE_FILE):
        with open(OVERRIDE_FILE, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row['Customer Key'] or row['Customer Key'].startswith('#'):
                    continue
                overrides[row['Customer Key']] = {
                    'master': row['Manual Master Name'].strip(),
                    'segment': row['Manual Segment'].strip()
                }
    return overrides

def get_segment(name):
    name_lower = name.lower()

    # Define helper indicators
    rel_pat = r'\b(church|temple|mosque|synagogue|ministry|baptist|catholic|methodist|lutheran|presbyterian|episcopal|god|saint|st\.|bible|christian|bishop|our lady|notre dame|sacred heart|holy|jesuit|bethlehem|trinity|immaculate|zion|covenant|grace|faith|christ|nazarene|apostolic|assembly of god|archdiocese)\b'
    is_religious_word = re.search(rel_pat, name_lower)
    
    # 1. College/University (New)
    if re.search(r'\b(university|college|higher ed|higher education|polytechnic|institute of technology)\b', name_lower):
        return "College/University"

    # 2. Private Schools
    if re.search(r'\b(academy|prep|collegiate|seminary|k-12|primary|elementary|middle school|high school)\b', name_lower):
        return "Private Schools"
    if "school" in name_lower and is_religious_word:
        return "Private Schools"
    if "school" in name_lower and re.search(r'\b(education|learning|early childhood)\b', name_lower):
        return "Private Schools"

    # 3. Public Schools
    if re.search(r'\b(isd|sch dist|public school|school district|schools|city school|county school)\b', name_lower):
        return "Public Schools"

    # 4. Religious
    if is_religious_word:
        return "Religious"
        
    # 5. Medical
    if re.search(r'\b(hospital|clinic|health|medical|physician|doctor|dr\.|dental|dentist|surgery|veterinary|vet|healthcare|urgent care|care|dentures?|pharmacy|rehab|recovery|senior living|nursing|rehabilitation|amerimed|pathology|lab|laboratory)\b', name_lower):
        return "Medical"

    # 6. Hospitality
    if re.search(r'\b(hotel|inn|suites|resort|motel|lodge|aloft|marriott|hilton|holiday inn|staybridge|hampton|courtyard|residence inn|fairfield)\b', name_lower):
        return "Hospitality"

    # 7. Municipal
    if re.search(r'\b(city of|town of|village of|state of|commonwealth of)\b', name_lower):
        return "Municipal"

    excluded_muni = re.search(r'\b(systems?|protection|security|builders?|bank|finance|food|ymca|kid city|solutions?|service|inc|llc|corp)\b', name_lower)
    
    if not excluded_muni:
        if re.search(r'\b(county|fiscal court|jail|police|fire|library|municipal|govt|authority|township)\b', name_lower):
            return "Municipal"

    # 8. Data Center
    if re.search(r'\b(data center|compute|hosting|server|cloud|colocation)\b', name_lower):
        return "Data Center"

    # 9. Industrial
    if re.search(r'\b(mfg|manufacturing|industrial|plant|factory|works|production|packaging|steel|chemical|distributing|logistics|warehouse|engineering|tools|systems|construction|contractor|builders|auto|automotive|parts|metal|plastic|energy|machining|tool|trucking|cargo|freight|transport|shipping|supply chain|distribution)\b', name_lower):
        return "Industrial"

    # 10. Office (Strict list)
    if re.search(r'\b(bank|financial|insurance|realty|properties|law|firm|holding|associates|partners|consulting|agency|hq|headquarters|investment|real estate|cbre|jll|colliers|cushman|wakefield|nai|avison young|foundry commercial|equity|prologis|duke realty)\b', name_lower):
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

def split_co_name(name):
    match = re.search(r'\s+(C/O|CO)\s+', name, re.IGNORECASE)
    if match:
        return name[:match.start()].strip(), name[match.end():].strip()
    return name, None

def get_chain_master(name):
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
    return None

def dedup_names(processed_rows, overrides):
    def get_comparison_key(name):
        noise_words = r'\b(INC|LLC|COMPANY|CORP|LTD|LIMITED|INCORPORATED|THE)\b'
        core_name = re.sub(noise_words, '', name).strip()
        return core_name

    unique_names = list(set(row['Master Customer Name'] for row in processed_rows))
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
        # Override Lock: Don't change rows that have overrides
        if row['Customer Key'] in overrides:
            continue
            
        original_master = row['Master Customer Name']
        if original_master in canonical_map:
            row['Master Customer Name'] = canonical_map[original_master]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file not found at {INPUT_FILE}")
        return

    overrides = load_overrides()
    print(f"Loaded {len(overrides)} manual overrides.")

    processed_rows = []
    with open(INPUT_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row['Customer Key']
            original_name = row['Customer Name']
            
            if key in overrides:
                master_name = overrides[key]['master']
                segment = overrides[key]['segment']
                if not segment:
                    segment = get_segment(master_name)
            else:
                left_part, right_part = split_co_name(original_name)
                candidate_name = left_part
                clean_candidate = get_master_name(candidate_name)
                
                chain_match_left = get_chain_master(clean_candidate)
                
                master_name = clean_candidate
                # Default segment source is original to catch LLC/Inc
                segment_source = original_name 
                
                if chain_match_left:
                    master_name = chain_match_left
                    segment_source = master_name # Chain match -> use Master for segment
                else:
                    if right_part:
                        clean_right = get_master_name(right_part)
                        chain_match_right = get_chain_master(clean_right)
                        if chain_match_right:
                            master_name = chain_match_right
                            segment_source = master_name # Chain match -> use Master
                        else:
                            master_name = clean_candidate
                    else:
                        master_name = clean_candidate
                
                segment = get_segment(segment_source)

            processed_rows.append({
                'Customer Key': key,
                'Original Name': original_name,
                'Master Customer Name': master_name,
                'Segment': segment,
                'Source': row['Source']
            })

    dedup_names(processed_rows, overrides)
    
    # Generate Log
    log_rows = []
    processed_rows.sort(key=lambda x: x['Master Customer Name'])
    
    for row in processed_rows:
        key = row['Customer Key']
        orig = row['Original Name']
        final = row['Master Customer Name']
        
        if key in overrides:
            log_rows.append({
                'Master Customer Name': final,
                'Original Name': orig,
                'Initial Clean Name': '(Override)',
                'Type': 'Manual Override'
            })
            continue

        s1_co, _ = split_co_name(orig)
        s2_clean = get_master_name(s1_co)
        chain_res = get_chain_master(s2_clean)
        s3_chain = chain_res if chain_res else s2_clean
        
        change_type = []
        if s1_co.upper() != orig.upper().strip() and ("C/O" in orig.upper() or "CO " in orig.upper()):
            _, right_part = split_co_name(orig)
            if right_part:
                clean_right = get_master_name(right_part)
                if get_chain_master(clean_right) == final:
                    change_type.append("C/O Swap (Right Side Chain)")
                else:
                    change_type.append("C/O Strip")
            else:
                change_type.append("C/O Strip")

        if chain_res and chain_res == final and "C/O Swap" not in str(change_type):
             change_type.append("Chain Rule")
             
        if final != s3_chain and not change_type:
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
