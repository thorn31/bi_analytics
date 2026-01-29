import json
import csv
import io
from pathlib import Path

# Paths
MAPPINGS_FILE = Path("data/static/hvacdecodertool/serialmappings")
INPUT_CSV = Path("data/rules_normalized/2026-01-29-sdi-master-v13/SerialDecodeRule.csv")
OUTPUT_CSV = Path("data/rules_normalized/2026-01-29-sdi-master-v13/SerialDecodeRule_Patched.csv")

def patch():
    if not MAPPINGS_FILE.exists():
        print(f"Error: {MAPPINGS_FILE} not found.")
        return
    if not INPUT_CSV.exists():
        print(f"Error: {INPUT_CSV} not found.")
        return

    with open(MAPPINGS_FILE, "r", encoding="utf-8") as f:
        mappings = json.load(f)

    # Normalize mapping brands for easier lookup (uppercase)
    normalized_mappings = {k.upper(): v for k, v in mappings.items()}

    updated_rows = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            brand = row["brand"].upper()
            style_name = row["style_name"]
            
            if brand in normalized_mappings:
                brand_map = normalized_mappings[brand]
                
                # Try to find a specific style match
                # Style names in CSV are like "Style 1: ...", "Style 2: ..."
                # Keys in mapping are like "Style1", "Style2", or "default"
                
                target_style = "default"
                import re
                style_match = re.search(r"Style\s*(\d+)", style_name, re.IGNORECASE)
                if style_match:
                    style_num = style_match.group(1)
                    possible_keys = [f"Style{style_num}", f"Style {style_num}", f"Style{style_num}:"]
                    for pk in possible_keys:
                        if pk in brand_map:
                            target_style = pk
                            break
                
                # Special case for Bosch "Code" style
                if brand == "BOSCH" and "year code" in style_name.lower():
                    if "Code" in brand_map:
                        target_style = "Code"

                if target_style in brand_map:
                    style_map = brand_map[target_style]
                    
                    try:
                        date_fields = json.loads(row["date_fields"] or "{}")
                        changed = False
                        
                        if "year_map" in style_map and "year" in date_fields:
                            if "mapping" not in date_fields["year"]:
                                date_fields["year"]["mapping"] = style_map["year_map"]
                                changed = True
                                
                        if "month_map" in style_map and "month" in date_fields:
                            if "mapping" not in date_fields["month"]:
                                date_fields["month"]["mapping"] = style_map["month_map"]
                                changed = True
                                
                        if changed:
                            row["date_fields"] = json.dumps(date_fields)
                            # If it still requires chart elsewhere, keep it as is, 
                            # but usually we are fulfilling the chart requirement here.
                            pass

                    except Exception as e:
                        print(f"Error processing row {brand} {style_name}: {e}")

            updated_rows.append(row)

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"Patched {len(updated_rows)} rules.")
    print(f"Output saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    patch()
