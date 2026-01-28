# Ruleset Promotion Workflow with Manual Fixes (Archived)

## Overview

When promoting new candidate rules into the ruleset, **manual fixes must be reapplied** to ensure critical corrections persist across updates. This is necessary because the `phase3-promote` command identifies duplicates by exact pattern match, so updated/fixed rules have different keys than their broken originals.

## The Problem

The `phase3-promote` deduplication logic uses:
```python
key = (brand, style_name, serial_regex, source_url)
```

If you manually fix a `serial_regex`, the key changes. Future mining operations might rediscover the original broken pattern from external sources (like Building Center), creating a candidate with the original regex. Since the keys don't match, **both rules would be added to the CSV**, creating conflicts.

## The Solution

A persistent fix script (`scripts/apply_manual_serial_fixes.py`) maintains a registry of known fixes and automatically:
1. Detects rules matching broken patterns
2. Applies the correct fix
3. Removes duplicate rules with same (brand, style_name)

## Standard Workflow

### Step 1: Promote New Candidates

```bash
python3 -m msl phase3-promote \
  --base-ruleset-dir $(cat data/rules_normalized/CURRENT.txt) \
  --candidates-dir data/rules_discovered/YYYY-MM-DD-source/candidates \
  --run-id YYYY-MM-DD-descriptive-name \
  --out-dir data/rules_normalized
```

This creates: `data/rules_normalized/YYYY-MM-DD-descriptive-name/`

### Step 2: Apply Manual Fixes

**CRITICAL: Always run this after promotion!**

```bash
python3 scripts/apply_manual_serial_fixes.py \
  --ruleset-dir data/rules_normalized/YYYY-MM-DD-descriptive-name
```

This will:
- Detect and fix any rules matching known broken patterns
- Remove duplicates (keeping the most recent fix)
- Create a backup: `SerialDecodeRule.csv.before_manual_fixes`

**Preview changes first:**
```bash
python3 scripts/apply_manual_serial_fixes.py \
  --ruleset-dir data/rules_normalized/YYYY-MM-DD-descriptive-name \
  --dry-run
```

### Step 3: Validate

Run baseline to verify the fixes worked:

```bash
python3 -m msl phase3-baseline \
  --input data/equipment_exports/latest/sdi_equipment_YYYY_MM_DD.csv \
  --ruleset-dir data/rules_normalized/YYYY-MM-DD-descriptive-name \
  --run-id YYYY-MM-DD-validation
```

Check Trane accuracy in the output:
```bash
python3 -c "
import csv
with open('data/reports/YYYY-MM-DD-validation/baseline_decoder_output.csv') as f:
    trane = [r for r in csv.DictReader(f) if r.get('DetectedBrand') == 'TRANE']
    comparable = [r for r in trane if r.get('KnownManufactureYear') and r.get('ManufactureYear')]
    correct = sum(1 for r in comparable if r.get('KnownManufactureYear') == r.get('ManufactureYear'))
    print(f'Trane accuracy: {correct}/{len(comparable)} ({correct/len(comparable)*100:.1f}%)')
"
```

Expected: **Trane accuracy ≥ 90%** (should be ~94% with the fix)

### Step 4: Update CURRENT

Once validated:

```bash
echo "data/rules_normalized/YYYY-MM-DD-descriptive-name" > data/rules_normalized/CURRENT.txt
```

## Adding New Manual Fixes

To add a new fix to the registry, edit `scripts/apply_manual_serial_fixes.py` and add an entry to the `MANUAL_FIXES` list:

```python
{
    "name": "Short description of the fix",
    "match": {
        "brand": "BRAND_NAME",
        "style_name": "Style Name",
        "serial_regex_any": [
            r"pattern_to_match_v1",
            r"pattern_to_match_v2",
        ]
    },
    "fix": {
        "serial_regex": r"fixed_pattern",
        "example_serials": ["example1", "example2"],
        "date_fields": { ... },
        "decade_ambiguity": { ... },
        "evidence_excerpt": "explanation",
        "retrieved_on": "YYYY-MM-DD"
    },
    "reason": "Detailed explanation of why this fix is needed",
    "issue_url": "https://github.com/your-org/project/issues/NNN"
}
```

## Current Registered Fixes

### 1. Trane Style 1 (2002-2009) - Length Constraint

**Problem:** Original pattern `^(?=.*[A-Z])\d{3}[A-Z0-9]{3,30}$` matched 10-character modern serials, incorrectly decoding them as 2002 instead of 2022.

**Fix:** Added `(?=.{7,9}$)` lookahead to restrict to 7-9 character serials only.

**Impact:** Improved accuracy from 61.8% to 95.3%

**Reference:** `docs/trane_fix_summary.md`

### 2. Trane Style 1 (2010+) - Length Constraint

**Problem:** Original pattern `^(?=.*[A-Z])\d{4}[A-Z0-9]{3,30}$` required exactly 4 leading digits, missing modern 5-9 digit prefixes.

**Fix:** Changed to `\d{4,}` and added `(?=.{10,}$)` lookahead to restrict to 10+ character serials.

**Impact:** Improved accuracy from 91.2% to 93.2%

**Reference:** `docs/trane_fix_summary.md`

## Troubleshooting

### "No matching rule found" but validation shows low accuracy

The script may not be detecting the broken rule. Check:
1. Is the pattern in `serial_regex_any` correct?
2. Run with `--dry-run` to see what's being checked
3. Manually inspect the CSV for the actual pattern

### Duplicates keep appearing

If duplicates persist after running the script:
1. Check if the `(brand, style_name)` grouping is correct
2. Verify `retrieved_on` dates are being set
3. Manually remove duplicates and add their patterns to the fix registry

### Fix doesn't apply

1. Run with `--dry-run` to see debug output
2. Check that the `match` specification is correct
3. Verify the CSV hasn't been manually edited with different fieldnames

## Best Practices

1. **Always run manual fixes after promotion** - Make it part of your standard workflow
2. **Always validate after fixes** - Run baseline to confirm accuracy didn't regress
3. **Document new fixes** - Add them to this file and the fix registry
4. **Test on old rulesets** - Verify new fixes can be applied to historical versions
5. **Commit backups** - The `.before_manual_fixes` files can help debug issues

## Future Improvements

Potential enhancements to make this more robust:

1. **Add fix script to phase3-promote** - Automatically apply fixes after merging candidates
2. **Add metadata tags** - Mark rules as "manually_fixed" to track provenance
3. **Pattern conflict detection** - Warn if a candidate would create a duplicate style_name
4. **Automated testing** - CI/CD checks that fixes maintain accuracy thresholds
5. **Source blocking** - Ability to mark certain source patterns as "never promote"
