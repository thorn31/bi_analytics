import csv
import sys
from pathlib import Path

def normalize_sdi_export(input_path, output_path):
    print(f"Reading {input_path}...")
    
    mapping = {
        "Manufacturer": "Make",
        "Model #": "ModelNumber",
        "Serial #": "SerialNumber",
        "Manuf.\nYear": "KnownManufactureYear",
        "Cooling Capacity \n(Input)": "KnownCapacityTons",
        "Equipment": "EquipmentType"
    }
    
    with open(input_path, 'r', encoding='utf-8-sig', newline='') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames
        
        # Calculate new fieldnames
        new_fieldnames = []
        for f in fieldnames:
            new_fieldnames.append(mapping.get(f, f))
            
        # Ensure required columns are present
        required = ["Make", "ModelNumber", "SerialNumber", "KnownManufactureYear"]
        for r in required:
            if r not in new_fieldnames:
                new_fieldnames.append(r)
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=new_fieldnames)
            writer.writeheader()
            
            for row in reader:
                new_row = {}
                for old_key, val in row.items():
                    new_key = mapping.get(old_key, old_key)
                    new_row[new_key] = val
                writer.writerow(new_row)
                
    print(f"Writing standardized file to {output_path}...")
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python normalize_sdi.py <input_csv> <output_csv>")
        sys.exit(1)
    
    normalize_sdi_export(sys.argv[1], sys.argv[2])