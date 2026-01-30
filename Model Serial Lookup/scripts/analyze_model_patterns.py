
import pandas as pd
import re
import argparse
import sys

def generate_pattern(model_number):
    if not isinstance(model_number, str):
        return "UNKNOWN"
    
    # Normalize
    model = model_number.strip().upper()
    
    # 1. Replace sequences of digits with \d+
    # This helps identify fixed letter prefixes/suffixes vs variable numbers
    pattern = re.sub(r'\d+', r'\\d+', model)
    
    return pattern

def analyze_patterns(file_path, min_count=100):
    try:
        # Load data - try standard CSV first, then other encodings if needed
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading CSV: {e}", file=sys.stderr)
            return

        # Normalize column names
        df.columns = [c.strip() for c in df.columns]
        
        # Check for required columns. Adjust names based on typical SDI format.
        # usually 'Manufacturer', 'EquipmentType', 'ModelNumber' (or 'Model')
        
        manufacturer_col = next((c for c in df.columns if 'Manufacturer' in c), None)
        equipment_col = next((c for c in df.columns if 'Equipment' in c and 'Type' in c), None) # e.g. EquipmentType or Equipment Type
        if not equipment_col:
             equipment_col = next((c for c in df.columns if 'Equipment' in c), None)

        model_col = next((c for c in df.columns if 'Model' in c and 'Number' in c), None)
        if not model_col:
            model_col = next((c for c in df.columns if 'Model' in c), None)

        if not (manufacturer_col and equipment_col and model_col):
            print(f"Could not find required columns. Found: {df.columns}", file=sys.stderr)
            return

        print(f"Analyzing {len(df)} records...")
        print(f"Columns: Mfg='{manufacturer_col}', Type='{equipment_col}', Model='{model_col}'")

        # Filter out empty models
        df = df.dropna(subset=[model_col])
        df = df[df[model_col].str.strip() != '']

        # Generate patterns
        df['pattern'] = df[model_col].apply(generate_pattern)

        # Group by Manufacturer, EquipmentType, Pattern
        # We want to find the "heavy targets" - high volume patterns.
        
        # First, count totals by Mfg + Type to identify heavy categories
        cat_counts = df.groupby([manufacturer_col, equipment_col]).size().reset_index(name='CategoryTotal')
        
        # Filter categories that are too small to matter
        significant_cats = cat_counts[cat_counts['CategoryTotal'] > min_count]
        
        # Merge back to get only significant data
        merged = pd.merge(df, significant_cats, on=[manufacturer_col, equipment_col])
        
        # Count patterns within these categories
        pattern_counts = merged.groupby([manufacturer_col, equipment_col, 'pattern']).size().reset_index(name='Count')
        
        # Calculate percentage
        pattern_counts = pd.merge(pattern_counts, cat_counts, on=[manufacturer_col, equipment_col])
        pattern_counts['Percentage'] = (pattern_counts['Count'] / pattern_counts['CategoryTotal']) * 100
        
        # Sort: Most frequent patterns first
        pattern_counts = pattern_counts.sort_values(by=['Count'], ascending=False)

        # Display top patterns
        print("\n=== TOP MODEL NUMBER PATTERNS (Potential High-Value Targets) ===")
        print(f"Showing patterns with >{min_count} occurrences\n")

        # We can group by Mfg/Type for display
        grouped_display = pattern_counts.groupby([manufacturer_col, equipment_col])
        
        # Sort groups by total size (finding the biggest "fish" first)
        sorted_groups = sorted(grouped_display, key=lambda x: x[1]['Count'].sum(), reverse=True)

        for (mfg, eq_type), group in sorted_groups:
            total_assets = group['CategoryTotal'].iloc[0]
            if total_assets < min_count: continue

            print(f"--- {mfg} | {eq_type} (Total Assets: {total_assets}) ---")
            
            # Show top 5 patterns for this group
            top_patterns = group.head(5)
            for _, row in top_patterns.iterrows():
                # Don't show if it's a tiny outlier within a large group
                if row['Count'] < 10: continue 
                
                print(f"   {row['Count']:<6} ({row['Percentage']:5.1f}%)  {row['pattern']}")
            print("")

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='Path to SDI CSV file')
    parser.add_argument('--min-count', type=int, default=100, help='Minimum number of assets to report a pattern')
    args = parser.parse_args()
    
    analyze_patterns(args.input_file, min_count=args.min_count)
