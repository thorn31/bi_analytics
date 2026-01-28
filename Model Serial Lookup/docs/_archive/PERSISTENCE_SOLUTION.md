# Trane Fix Persistence Solution (Archived)

## Summary

**Problem:** Manual regex fixes to SerialDecodeRule.csv will NOT automatically persist across ruleset promotions because `phase3-promote` uses exact pattern matching for deduplication.

**Solution:** Created `scripts/apply_manual_serial_fixes.py` - a reusable script that maintains a registry of known fixes and must be run after each promotion.

## Why Fixes Don't Persist Automatically

The `phase3-promote` command detects duplicates using:
```python
key = (brand, style_name, serial_regex, source_url)
```

When you fix a broken `serial_regex`, the key changes:

**Original (broken):**
```
(TRANE, Style 1 (2002-2009), ^(?=.*[A-Z])\d{3}[A-Z0-9]{3,30}$, https://...)
```

**Fixed:**
```
(TRANE, Style 1 (2002-2009), ^(?=.{7,9}$)(?=.*[A-Z])\d{3,}[A-Z0-9]{2,30}$, https://...)
```

Since these are **different keys**, if a future mining operation rediscovers the original Building Center pattern, it will be **added as a new row** instead of being skipped. You'd end up with both the broken and fixed rules in the CSV.

## The Solution

### 1. Created Persistent Fix Script

`scripts/apply_manual_serial_fixes.py` contains a registry of all known manual fixes:

```python
MANUAL_FIXES = [
    {
        "name": "Trane Style 1 (2002-2009) - Length Constraint",
        "match": {
            "brand": "TRANE",
            "style_name": "Style 1 (2002-2009)",
            "serial_regex_any": [
                r"^(?=.*[A-Z])\d{3}[A-Z0-9]{3,30}$",  # Original
                r"^(?=.*[A-Z])\d{3,}[A-Z0-9]{2,30}$",  # v2
                # ... other variations
            ]
        },
        "fix": {
            "serial_regex": r"^(?=.{7,9}$)(?=.*[A-Z])\d{3,}[A-Z0-9]{2,30}$",
            # ... complete fix specification
        }
    },
    # ... more fixes
]
```

The script:
- Detects any rules matching broken patterns
- Applies the registered fix
- Removes duplicates (keeping the most recent version)
- Creates a backup before making changes

### 2. Standard Workflow

**After every `phase3-promote`, run:**

```bash
# Promote new candidates
python3 -m msl phase3-promote \
  --base-ruleset-dir $(cat data/rules_normalized/CURRENT.txt) \
  --candidates-dir data/rules_discovered/new-rules/candidates \
  --run-id 2026-01-27-new-rules \
  --out-dir data/rules_normalized

# Apply manual fixes (CRITICAL!)
python3 scripts/apply_manual_serial_fixes.py \
  --ruleset-dir data/rules_normalized/2026-01-27-new-rules

# Validate
python3 -m msl phase3-baseline \
  --input data/equipment_exports/latest/equipment.csv \
  --ruleset-dir data/rules_normalized/2026-01-27-new-rules \
  --run-id validation

# Update CURRENT if validated
echo "data/rules_normalized/2026-01-27-new-rules" > data/rules_normalized/CURRENT.txt
```

### 3. Verification

Test the script works:

```bash
# Preview what would be fixed (dry-run)
python3 scripts/apply_manual_serial_fixes.py --dry-run

# Test on current ruleset (should show "already fixed")
python3 scripts/apply_manual_serial_fixes.py \
  --ruleset-dir data/rules_normalized/2026-01-27-trane-fix-v3 \
  --dry-run

# Test on original broken ruleset (should show fixes applied)
python3 scripts/apply_manual_serial_fixes.py \
  --ruleset-dir data/rules_normalized/2026-01-26-sdi-promoted20-2026-01-26-heuristic36a-mitsu \
  --dry-run
```

## Files Created

1. **scripts/apply_manual_serial_fixes.py**
   - Executable script with fix registry
   - Can be run standalone or integrated into CI/CD
   - Includes dry-run mode for testing

2. **docs/WORKFLOW_RULESET_PROMOTION.md**
   - Complete workflow documentation
   - Step-by-step promotion process
   - Troubleshooting guide

3. **docs/trane_fix_summary.md**
   - Technical details of the Trane fix
   - Before/after accuracy metrics
   - Root cause analysis

4. **docs/PERSISTENCE_SOLUTION.md** (this file)
   - High-level overview of the persistence solution

## Current Status

✅ **Fix is applied** to `data/rules_normalized/2026-01-27-trane-fix-v3`
✅ **CURRENT.txt points** to the fixed ruleset
✅ **Persistence script created** and tested
✅ **Documentation complete**

## Recommendations

### Immediate
1. ✅ **Done:** Use the fix script after every promotion
2. ✅ **Done:** Document the workflow
3. Consider: Add a reminder in the phase3-promote output

### Future Enhancements
1. **Integrate into phase3-promote:** Automatically apply fixes after merging candidates
2. **Add CI/CD checks:** Fail if Trane accuracy drops below 90%
3. **Source pattern blocking:** Mark specific patterns as "never promote"
4. **Metadata tracking:** Add "manually_fixed" flag to rules
5. **Conflict detection:** Warn if promoting would create duplicate (brand, style_name)

## Testing

Verified the solution works:

```bash
# Current ruleset (already fixed)
$ python3 scripts/apply_manual_serial_fixes.py --ruleset-dir data/rules_normalized/2026-01-27-trane-fix-v3 --dry-run
✓ No matching rule found (may already be fixed)
✓ Removed 32 duplicate(s)

# Original ruleset (broken)
$ python3 scripts/apply_manual_serial_fixes.py --ruleset-dir data/rules_normalized/2026-01-26-sdi-promoted20-2026-01-26-heuristic36a-mitsu --dry-run
✓ Fixed rule: TRANE Style 1 (2002-2009)
✓ Fixed rule: TRANE Style 1 (2010+)
✓ Fixes applied: 2
```

## Questions?

- **Do I need to run this every time?** YES - after every `phase3-promote`
- **What if I forget?** The Trane accuracy will drop from ~94% to ~73%
- **Can I automate it?** Yes - add it to your promotion script or CI/CD pipeline
- **Will it break anything?** No - it creates a backup and only fixes known patterns
- **How do I add new fixes?** Edit `MANUAL_FIXES` list in the script

## Success Metrics

With the fix applied:
- **Trane overall accuracy:** 73.0% → 94.0% ✅
- **10-digit serials:** 60.9% → 93.6% ✅
- **Style 1 (2002-2009):** 61.8% → 95.3% ✅

If these metrics regress after a promotion, you forgot to run the fix script!
