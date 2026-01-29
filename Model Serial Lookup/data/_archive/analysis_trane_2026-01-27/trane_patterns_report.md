# Trane Serial Pattern Analysis

## Summary

- Total Trane records: 1727
- Records with known year: 1638
- Overall accuracy: 313/429 (73.0%)

## Key Findings

### Serial Length Distribution

- Length 3: 19
- Length 6: 10
- Length 7: 11
- Length 8: 16
- Length 9: 785
- Length 10: 373
- Length 11: 2
- Length 14: 3
- Length 15: 36

### Accuracy by Serial Length

- Length 7: 3/3 (100.0%)
- Length 8: 1/1 (100.0%)
- Length 9: 142/149 (95.3%)
- Length 10: 167/274 (60.9%)
- Length 11: 0/1 (0.0%)
- Length 14: 0/1 (0.0%)

### Accuracy by Equipment Type

- COOLING CONDENSING UNIT: 141/174 (81.0%)
- PACKAGED UNIT: 119/161 (73.9%)
- HEAT PUMP CONDENSING UNIT: 31/41 (75.6%)
- AIR HANDLING UNIT: 16/40 (40.0%)
- FURNACE: 1/5 (20.0%)
- FAN COIL / UNIT VENT: 2/4 (50.0%)
- CHILLER: 2/3 (66.7%)
- WSHP: 1/1 (100.0%)

### Accuracy by Matched Style

- Style 1 (2002-2009): 165/267 (61.8%)
- Style 1 (2010+): 146/160 (91.2%)
- Style 3: A 92 M 07217: 2/2 (100.0%)

## 10-Digit Serial Analysis

- Total 10-digit serials: 274
- Correct: 167
- Wrong: 107
- Accuracy: 60.9%

### Sample Wrong Predictions

- **11251PX52F**: Known 2010, Decoded 2011 (Style: Style 1 (2010+), Equipment: HEAT PUMP CONDENSING UNIT)
- **22226NUP4F**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: HEAT PUMP CONDENSING UNIT)
- **22087U9K4F**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: HEAT PUMP CONDENSING UNIT)
- **22353FHR3V**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: AIR HANDLING UNIT)
- **22354SYH3V**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: AIR HANDLING UNIT)
- **22482KSW3V**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: AIR HANDLING UNIT)
- **222530D93V**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: AIR HANDLING UNIT)
- **22122023PA**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: PACKAGED UNIT)
- **22112160PA**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: PACKAGED UNIT)
- **22112172PA**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: PACKAGED UNIT)
- **22112159PA**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: PACKAGED UNIT)
- **22421814YA**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: COOLING CONDENSING UNIT)
- **22302209YA**: Known 2022, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: COOLING CONDENSING UNIT)
- **214410805D**: Known 2021, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: PACKAGED UNIT)
- **214510430D**: Known 2021, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: PACKAGED UNIT)
- **23033078JA**: Known 2023, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: PACKAGED UNIT)
- **21262W9NCG**: Known 2021, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: AIR HANDLING UNIT)
- **21262W97CG**: Known 2021, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: AIR HANDLING UNIT)
- **21305LRJ5F**: Known 2021, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: COOLING CONDENSING UNIT)
- **21115JDE5F**: Known 2021, Decoded 2002 (Style: Style 1 (2002-2009), Equipment: COOLING CONDENSING UNIT)

### Prefix Patterns (2-digit)

- **12**: 68 total - years: {2012: 68}
- **22**: 48 total - years: {2022: 47, 2002: 1}
- **21**: 24 total - years: {2021: 23, 44470: 1}
- **10**: 20 total - years: {2010: 20}
- **14**: 19 total - years: {2014: 18, 2004: 1}
- **11**: 13 total - years: {2013: 6, 2011: 4, 2010: 3}
- **23**: 11 total - years: {2023: 11}
- **17**: 8 total - years: {2017: 8}
- **13**: 7 total - years: {2013: 7}
- **15**: 7 total - years: {2015: 6, 2014: 1}
- **19**: 5 total - years: {2019: 5}
- **18**: 5 total - years: {2018: 3, 43221: 1, 43405: 1}
- **84**: 5 total - years: {2008: 5}
- **73**: 5 total - years: {2007: 5}
- **24**: 5 total - years: {2024: 4, 2017: 1}
- **16**: 4 total - years: {2016: 4}
- **31**: 3 total - years: {2003: 3}
- **25**: 3 total - years: {2025: 3}
- **93**: 3 total - years: {2009: 3}
- **51**: 3 total - years: {2005: 3}

## Error Analysis

Total wrong predictions: 116

### By Equipment Type

- PACKAGED UNIT: 42
- COOLING CONDENSING UNIT: 33
- AIR HANDLING UNIT: 24
- HEAT PUMP CONDENSING UNIT: 10
- FURNACE: 4
- FAN COIL / UNIT VENT: 2
- CHILLER: 1

### By Matched Style

- Style 1 (2002-2009): 102
- Style 1 (2010+): 14

# Archived (moved 2026-01-28)
