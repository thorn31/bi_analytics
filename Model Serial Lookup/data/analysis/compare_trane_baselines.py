"""Compare Trane accuracy before and after fix."""
import csv
from pathlib import Path
from collections import defaultdict, Counter

def load_baseline(path):
    """Load baseline CSV and return list of dicts."""
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def analyze_trane(data, label):
    """Analyze Trane decoding accuracy."""
    # Filter for Trane only
    trane = [r for r in data if r.get('DetectedBrand') == 'TRANE']

    # Filter for comparable records (have both known and decoded years)
    comparable = []
    for r in trane:
        known = r.get('KnownManufactureYear', '').strip()
        decoded = r.get('ManufactureYear', '').strip()
        if known and decoded:
            try:
                known_int = int(float(known))
                decoded_int = int(float(decoded))
                r['_known_int'] = known_int
                r['_decoded_int'] = decoded_int
                r['_correct'] = (known_int == decoded_int)
                comparable.append(r)
            except ValueError:
                pass

    total_correct = sum(1 for r in comparable if r['_correct'])
    total_wrong = len(comparable) - total_correct

    print(f"\n{'='*80}")
    print(f"{label}")
    print(f"{'='*80}")
    print(f"Total Trane records: {len(trane)}")
    print(f"Comparable records (known & decoded): {len(comparable)}")
    print(f"Correct: {total_correct}")
    print(f"Wrong: {total_wrong}")
    print(f"Accuracy: {total_correct/len(comparable)*100:.1f}%")

    # By matched style
    print(f"\nAccuracy by Matched Style:")
    by_style = defaultdict(lambda: {'correct': 0, 'total': 0})
    for r in comparable:
        style = r.get('MatchedSerialStyle', '').strip()
        if style:
            by_style[style]['total'] += 1
            if r['_correct']:
                by_style[style]['correct'] += 1

    for style in sorted(by_style.keys(), key=lambda x: by_style[x]['total'], reverse=True):
        stats = by_style[style]
        acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {style}: {stats['correct']}/{stats['total']} ({acc:.1f}%)")

    # By serial length
    print(f"\nAccuracy by Serial Length:")
    by_length = defaultdict(lambda: {'correct': 0, 'total': 0})
    for r in comparable:
        serial = r.get('SerialNumber', '').strip()
        if serial:
            length = len(serial)
            by_length[length]['total'] += 1
            if r['_correct']:
                by_length[length]['correct'] += 1

    for length in sorted(by_length.keys()):
        stats = by_length[length]
        acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  Length {length}: {stats['correct']}/{stats['total']} ({acc:.1f}%)")

    # 10-digit analysis
    ten_digit = [r for r in comparable if len(r.get('SerialNumber', '').strip()) == 10]
    ten_digit_correct = sum(1 for r in ten_digit if r['_correct'])
    if ten_digit:
        print(f"\n10-Digit Serials:")
        print(f"  Total: {len(ten_digit)}")
        print(f"  Correct: {ten_digit_correct}")
        print(f"  Wrong: {len(ten_digit) - ten_digit_correct}")
        print(f"  Accuracy: {ten_digit_correct/len(ten_digit)*100:.1f}%")

        # Sample wrong ones
        wrong_10 = [r for r in ten_digit if not r['_correct']]
        if wrong_10:
            print(f"\n  Sample wrong predictions (first 10):")
            for r in wrong_10[:10]:
                serial = r.get('SerialNumber', '').strip()
                style = r.get('MatchedSerialStyle', '').strip()
                print(f"    {serial}: Known {r['_known_int']}, Decoded {r['_decoded_int']} ({style})")

    return {
        'total': len(comparable),
        'correct': total_correct,
        'wrong': total_wrong,
        'accuracy': total_correct/len(comparable) if comparable else 0,
        'by_style': dict(by_style),
        'ten_digit_accuracy': ten_digit_correct/len(ten_digit) if ten_digit else 0,
        'ten_digit_total': len(ten_digit),
        'ten_digit_correct': ten_digit_correct
    }

# Load both baselines
print("\nLoading baseline data...")
old_path = Path("data/reports/phase3-baseline-2026-01-26T055846+0000/baseline_decoder_output.csv")
new_path = Path("data/reports/trane-fix-validation/baseline_decoder_output.csv")

old_data = load_baseline(old_path)
new_data = load_baseline(new_path)

print(f"Loaded {len(old_data)} records from old baseline")
print(f"Loaded {len(new_data)} records from new baseline")

# Analyze both
old_stats = analyze_trane(old_data, "BEFORE FIX (2026-01-26 baseline)")
new_stats = analyze_trane(new_data, "AFTER FIX (2026-01-27 trane-fix-validation)")

# Summary comparison
print(f"\n{'='*80}")
print("IMPROVEMENT SUMMARY")
print(f"{'='*80}")
print(f"Overall accuracy: {old_stats['accuracy']*100:.1f}% → {new_stats['accuracy']*100:.1f}% (Δ {(new_stats['accuracy']-old_stats['accuracy'])*100:+.1f}%)")
print(f"10-digit accuracy: {old_stats['ten_digit_accuracy']*100:.1f}% → {new_stats['ten_digit_accuracy']*100:.1f}% (Δ {(new_stats['ten_digit_accuracy']-old_stats['ten_digit_accuracy'])*100:+.1f}%)")
print(f"Correct predictions: {old_stats['correct']} → {new_stats['correct']} (Δ {new_stats['correct']-old_stats['correct']:+d})")
print(f"Wrong predictions: {old_stats['wrong']} → {new_stats['wrong']} (Δ {new_stats['wrong']-old_stats['wrong']:+d})")

# Determine success
if new_stats['accuracy'] > old_stats['accuracy']:
    print(f"\n✓ SUCCESS! Accuracy improved by {(new_stats['accuracy']-old_stats['accuracy'])*100:.1f} percentage points")
else:
    print(f"\n✗ WARNING: Accuracy did not improve")

print()
