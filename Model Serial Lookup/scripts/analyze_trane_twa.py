
import pandas as pd
import re
import argparse
import sys

def analyze_trane_twa(file_path):
    try:
        df = pd.read_csv(file_path)
        
        # Filter for Trane
        df['Manufacturer_Norm'] = df['Manufacturer'].astype(str).str.upper().str.strip()
        
        target_df = df[
            (df['Manufacturer_Norm'].str.contains('TRANE')) & 
            (df['Model #'].astype(str).str.contains('TWA'))
        ].copy()
        
        print(f"Found {len(target_df)} Trane TWA assets.")
        
        # Regex to extract Pos 7 and 8 (assuming TWA is at start or near start)
        # Handle prefixes like '4TWA...' or just 'TWA...'
        # We want the char 2 positions after the capacity digits
        
        # Pattern: TWA + 3 digits + (.) + (.)
        regex = r"TWA\d{3}(.)(.)"
        
        def extract_codes(model):
            m = re.search(regex, str(model))
            if m:
                return m.group(1), m.group(2)
            return None, None

        target_df[['Pos7', 'Pos8']] = target_df['Model #'].apply(lambda x: pd.Series(extract_codes(x)))
        
        print("\nPosition 8 (Voltage?) Distribution:")
        print(target_df['Pos8'].value_counts())
        
        # Show examples
        print("\nExamples:")
        for p8 in target_df['Pos8'].dropna().unique():
            example = target_df[target_df['Pos8'] == p8].iloc[0]['Model #']
            print(f"Pos8='{p8}': {example}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    args = parser.parse_args()
    
    analyze_trane_twa(args.input_file)
