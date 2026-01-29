#!/usr/bin/env python3
"""
Compare v14 baseline accuracy vs serial.json accuracy on SDI equipment.

Direct comparison to answer: "Would adding serial.json mappings improve v14?"
"""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load SDI validation details (already has serial.json results)
sdi_validation = []
validation_path = Path(__file__).parent.parent / 'data' / 'validation' / 'serialjson' / 'sdi_validation_details.csv'

with open(validation_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sdi_validation.append(row)

# Count results
v14_correct = 0
v14_incorrect = 0
v14_not_decoded = 0

serialjson_correct = 0
serialjson_incorrect = 0
serialjson_not_decoded = 0

improvement_cases = []  # Cases where serial.json is correct but v14 isn't

for row in sdi_validation:
    # V14 results
    if row['match_v13'] == 'CORRECT':  # Note: validation was run against v13, but v14 has same mappings
        v14_correct += 1
    elif row['match_v13'] == 'INCORRECT':
        v14_incorrect += 1
    else:
        v14_not_decoded += 1

    # Serial.json results
    if row['match_serialjson'] == 'CORRECT':
        serialjson_correct += 1

        # Is this an improvement over v14?
        if row['match_v13'] != 'CORRECT':
            improvement_cases.append({
                'brand': row['brand'],
                'serial': row['serial'],
                'known_year': row['known_year'],
                'v14_result': row['decoded_year_v13'] if row['decoded_year_v13'] else 'NOT_DECODED',
                'serialjson_result': row['decoded_year_serialjson']
            })

    elif row['match_serialjson'] == 'INCORRECT':
        serialjson_incorrect += 1
    else:
        serialjson_not_decoded += 1

print("=" * 80)
print("V14 BASELINE vs SERIAL.JSON COMPARISON")
print("=" * 80)
print()
print(f"Total equipment tested: {len(sdi_validation)}")
print()
print("V14 Current Ruleset:")
print(f"  Correct: {v14_correct}")
print(f"  Incorrect: {v14_incorrect}")
print(f"  Not decoded: {v14_not_decoded}")
print(f"  Accuracy: {v14_correct/len(sdi_validation)*100:.1f}%")
print()
print("Serial.json Mappings:")
print(f"  Correct: {serialjson_correct}")
print(f"  Incorrect: {serialjson_incorrect}")
print(f"  Not decoded: {serialjson_not_decoded}")
print(f"  Accuracy: {serialjson_correct/len(sdi_validation)*100:.1f}%")
print()
print("=" * 80)
print("WOULD SERIAL.JSON IMPROVE V14?")
print("=" * 80)
print()

net_improvement = serialjson_correct - v14_correct
net_degradation = serialjson_incorrect - v14_incorrect

print(f"New correct decodes: +{len(improvement_cases)}")
print(f"New incorrect decodes: +{net_degradation}")
print(f"Net improvement: +{net_improvement} correct decodes")
print()

if net_improvement > 0:
    print(f"✅ YES - Adding serial.json would improve accuracy by {net_improvement} serials")
    print(f"   Current: {v14_correct}/{len(sdi_validation)} ({v14_correct/len(sdi_validation)*100:.1f}%)")
    print(f"   With serial.json: {serialjson_correct}/{len(sdi_validation)} ({serialjson_correct/len(sdi_validation)*100:.1f}%)")
else:
    print(f"❌ NO - Serial.json would not improve accuracy")

print()
print(f"Sample improvements (first 10):")
for case in improvement_cases[:10]:
    print(f"  {case['brand']:8} {case['serial']:15} Year:{case['known_year']} "
          f"V14:{case['v14_result']:12} Serial.json:{case['serialjson_result']}")
