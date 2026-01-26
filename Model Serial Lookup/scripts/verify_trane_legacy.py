import csv
import sys

def verify_trane_legacy(path):
    print(f"Verifying Trane Legacy matches in {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        legacy_matches = 0
        correct = 0
        samples = []
        
        for row in reader:
            if row.get('DetectedBrand') != 'TRANE':
                continue
                
            style = row.get('MatchedSerialStyle', '')
            if "Legacy Letter Code" in style:
                legacy_matches += 1
                
                decoded = row.get('ManufactureYear', '').strip()
                known = row.get('KnownManufactureYear', '').strip()
                # Normalize known (remove .0)
                if known.endswith('.0'): known = known[:-2]
                
                if decoded == known:
                    correct += 1
                    if len(samples) < 10:
                        samples.append((row['SerialNumber'], decoded, known, "MATCH"))
                elif known:
                    if len(samples) < 10:
                        samples.append((row['SerialNumber'], decoded, known, "MISMATCH"))

    print(f"Total Legacy Rules Fired: {legacy_matches}")
    print(f"Matches with Known Year: {correct}")
    if legacy_matches > 0:
        print(f"Accuracy for Legacy Rule: {correct / legacy_matches:.1%}")
    
    print("\n--- Verification Samples ---")
    print(f"{ 'Serial':<15} | { 'Decoded':<8} | { 'Known':<8} | Status")
    for s, d, k, status in samples:
        print(f"{s:<15} | {d:<8} | {k:<8} | {status}")

if __name__ == "__main__":
    verify_trane_legacy(sys.argv[1])
