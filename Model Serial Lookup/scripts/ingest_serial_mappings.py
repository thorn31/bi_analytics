import json
import re
from pathlib import Path

# Paths
INPUT_FILE = Path("data/static/hvacdecodertool/serial.json")
OUTPUT_FILE = Path("data/static/hvacdecodertool/serialmappings")

def normalize_month(value):
    """Converts month names to integers."""
    v = value.lower().strip()
    months = {
        "january": 1, "jan": 1,
        "february": 2, "feb": 2,
        "march": 3, "mar": 3,
        "april": 4, "apr": 4,
        "may": 5,
        "june": 6, "jun": 6,
        "july": 7, "jul": 7,
        "august": 8, "aug": 8,
        "september": 9, "sep": 9, "sept": 9,
        "october": 10, "oct": 10,
        "november": 11, "nov": 11,
        "december": 12, "dec": 12
    }
    return months.get(v, value) # Return original if not found (e.g. for factories)

def parse_brand_key(key):
    """
    Parses keys like 'Daikin Year Style6' or 'Bard Month'.
    Returns (brand, category, style_suffix).
    """
    # Common categories we care about
    categories = ["Month", "Year", "Factory", "Type"]
    
    # Sort categories by length desc to handle "Year Code" vs "Year"
    categories = sorted(categories, key=len, reverse=True)
    
    parts = key.split()
    
    brand_parts = []
    category = None
    style = None
    
    for i, part in enumerate(parts):
        if part in categories:
            brand_parts = parts[:i]
            category = part
            style_parts = parts[i+1:]
            if style_parts:
                style = " ".join(style_parts)
            break
            
    if not category:
        # Fallback for keys that don't match exactly
        if "Year" in parts:
            idx = parts.index("Year")
            brand_parts = parts[:idx]
            category = "Year"
            style = " ".join(parts[idx+1:])
        else:
            return key, "unknown", None

    brand = " ".join(brand_parts)
    return brand, category, style

def ingest():
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    normalized_data = {}

    for key, items in data.items():
        if key in ["metaData", "Brands"]:
            continue

        brand, category, style = parse_brand_key(key)
        
        # Normalize Brand Name (simple casing)
        brand = brand.strip()
        
        if brand not in normalized_data:
            normalized_data[brand] = {}
            
        # Structure: Brand -> Style (or 'default') -> MapType (year_map, month_map)
        style_key = style if style else "default"
        if style_key not in normalized_data[brand]:
            normalized_data[brand][style_key] = {}
            
        map_key = f"{category.lower()}_map"
        
        # Build the map
        mapping = {}
        for item in items:
            k = item["key"]
            v = item["value"]
            
            if category == "Month":
                v = normalize_month(v)
            elif category == "Year" or category == "Year Code":
                try:
                    # Some entries might be ranges or descriptions, but most are years
                    if isinstance(v, str) and v.isdigit():
                        v = int(v)
                except:
                    pass
            
            mapping[k] = v
            
        normalized_data[brand][style_key][map_key] = mapping

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(normalized_data, f, indent=2, sort_keys=True)
    
    print(f"Successfully processed {len(normalized_data)} brands.")
    print(f"Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    ingest()
