import csv
import sys
from collections import defaultdict, Counter
from pathlib import Path

def generate_match_report(input_csv, output_md):
    print(f"Generating match analysis from {input_csv}...")
    
    # Stats containers
    brand_stats = defaultdict(lambda: {
        'total': 0, 'decoded': 0, 'correct': 0, 'wrong': 0, 'missing_input': 0
    })
    rule_performance = defaultdict(lambda: {'matches': 0, 'correct': 0, 'wrong': 0})
    failure_reasons = defaultdict(lambda: Counter())
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            brand = row.get('DetectedBrand', 'UNKNOWN')
            style = row.get('MatchedSerialStyle', '')
            status = row.get('DecodeStatus', '')
            
            # Ground truth vs Decoded
            decoded_year = row.get('ManufactureYear', '').strip()
            # Handle source data "2005.0" vs "2005"
            known_year = (row.get('KnownManufactureYear') or "").split('.')[0].strip() 
            
            # Count totals
            brand_stats[brand]['total'] += 1
            
            # Analyze decoding
            if style:
                brand_stats[brand]['decoded'] += 1
                rule_performance[(brand, style)]['matches'] += 1
                
                if known_year and decoded_year:
                    if known_year == decoded_year:
                        brand_stats[brand]['correct'] += 1
                        rule_performance[(brand, style)]['correct'] += 1
                    else:
                        brand_stats[brand]['wrong'] += 1
                        rule_performance[(brand, style)]['wrong'] += 1
            else:
                # Failure analysis
                sn = row.get('SerialNumber', '').strip()
                if not sn:
                    brand_stats[brand]['missing_input'] += 1
                    failure_reasons[brand]['Missing Serial Number'] += 1
                else:
                    # Heuristic failure buckets
                    if len(sn) < 5:
                        failure_reasons[brand]['Serial Too Short (<5)'] += 1
                    elif sn.isdigit():
                        failure_reasons[brand]['No Numeric Rule Matched'] += 1
                    elif sn.isalpha():
                        failure_reasons[brand]['No Alpha Rule Matched'] += 1
                    else:
                        failure_reasons[brand]['No Alphanumeric Rule Matched'] += 1

    # Generate Markdown
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("# detailed Match Analysis Report\n\n")
        f.write(f"- Source: `{input_csv}`\n\n")
        
        f.write("## 1. Brand Performance Summary\n")
        f.write("| Brand | Total | Decoded | Coverage | Accuracy (on Known) | Top Failure Reason |\n")
        f.write("|---|---|---|---|---|---|\n")
        
        for brand, stats in sorted(brand_stats.items(), key=lambda x: -x[1]['total']):
            if stats['total'] < 5: continue # Skip noise
            
            cov_pct = (stats['decoded'] / stats['total']) * 100
            acc_denom = stats['correct'] + stats['wrong']
            acc_pct = (stats['correct'] / acc_denom * 100) if acc_denom else 0
            
            top_fail = "N/A"
            if failure_reasons[brand]:
                top_fail = failure_reasons[brand].most_common(1)[0][0]
                
            f.write(f"| **{brand}** | {stats['total']} | {stats['decoded']} | {cov_pct:.1f}% | {acc_pct:.1f}% | {top_fail} |\n")
            
        f.write("\n## 2. Rule Effectiveness (Which Rules Work?)\n")
        f.write("Shows which specific styles/rules are actually successfully decoding your assets.\n\n")
        
        # Group by brand
        sorted_rules = sorted(rule_performance.items(), key=lambda x: (x[0][0], -x[1]['matches']))
        
        current_brand = ""
        for (brand, style), stats in sorted_rules:
            if stats['matches'] < 5: continue 
            
            if brand != current_brand:
                f.write(f"\n### {brand}\n")
                f.write("| Rule Name (Style) | Matches | Correct | Wrong | Accuracy |\n")
                f.write("|---|---|---|---|---|\n")
                current_brand = brand
                
            acc_denom = stats['correct'] + stats['wrong']
            acc_pct = (stats['correct'] / acc_denom * 100) if acc_denom else 0
            
            f.write(f"| {style} | {stats['matches']} | {stats['correct']} | {stats['wrong']} | **{acc_pct:.1f}%** |\n")

    print(f"Report written to {output_md}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python report_matches.py <baseline_output.csv> <report.md>")
        sys.exit(1)
    generate_match_report(sys.argv[1], sys.argv[2])
