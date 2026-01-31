# HVAC Export Integration - Quick Start

## Trane Pilot (5-Step Process)

### Step 1: Dry Run Validation
```bash
./scripts/run_hvacexport_integration_workflow.sh --brand TRANE --dry-run
```

**Expected outputs** in `data/validation/hvacexport/`:
- `trane_regex_quality_report.csv`
- `trane_sdi_column_alignment.csv`
- `trane_attribute_conflicts.csv`

### Step 2: Review Quality Report
```bash
# Check how many GOOD rules exist
grep ",GOOD$" data/validation/hvacexport/trane_regex_quality_report.csv | wc -l

# Review samples
head -20 data/validation/hvacexport/trane_regex_quality_details.csv
```

**Quality gate**: Need at least some GOOD rules to proceed.

### Step 3: Check SDI Alignment
```bash
# View attribute mapping strategy
cat data/validation/hvacexport/trane_sdi_column_alignment.csv

# Check for conflicts with building-center.org
cat data/validation/hvacexport/trane_attribute_conflicts.csv
```

**Expected**: Most attributes have action=RENAME or MATCH (can integrate).

### Step 4: Run Full Integration
```bash
./scripts/run_hvacexport_integration_workflow.sh --brand TRANE
```

**Expected outputs**:
- `data/rules_normalized/YYYY-MM-DD-hvacexport-trane/AttributeDecodeRule.csv`
- `data/validation/hvacexport/trane_integration_log.csv`
- `data/validation/hvacexport/trane_decode_accuracy_comparison.csv`

### Step 5: Review Accuracy
```bash
# View accuracy comparison
cat data/validation/hvacexport/trane_decode_accuracy_comparison.csv

# Check mismatches (if any)
cat data/validation/hvacexport/trane_decode_mismatches.csv | head -20
```

**Success criteria**:
- ✅ No regressions (baseline accuracy maintained)
- ✅ Improvements (more attributes decoded)
- ✅ >85% accuracy on new decodes
- ✅ <5% mismatch rate

### Step 6: Activate (if approved)
```bash
# Update CURRENT.txt
echo "$(date +%Y-%m-%d)-hvacexport-trane" > data/rules_normalized/CURRENT.txt

# Commit
git add data/rules_normalized/$(date +%Y-%m-%d)-hvacexport-trane/
git add data/validation/hvacexport/
git commit -m "Integrate HVAC export rules for Trane (pilot)

- Added X supplementary attribute rules
- Validated against SDI truth data
- Decode accuracy: X% (baseline) → Y% (merged)

Validation reports: data/validation/hvacexport/"
```

---

## Troubleshooting

### No GOOD rules
**Problem**: `grep ",GOOD$" trane_regex_quality_report.csv` returns 0

**Solution**: Lower quality threshold
```bash
./scripts/run_hvacexport_integration_workflow.sh --brand TRANE --min-quality WEAK
```

### High mismatch rate
**Problem**: Many entries in `trane_decode_mismatches.csv`

**Solution**: Review mismatch patterns
```bash
# Group by attribute to find systematic issues
cut -d',' -f1 data/validation/hvacexport/trane_decode_mismatches.csv | sort | uniq -c
```

If specific attribute has issues, consider skipping it in alignment.

### Conflicts with building-center.org
**Problem**: Many conflicts in `trane_attribute_conflicts.csv`

**Expected**: This is normal! Merge script automatically skips conflicts (building-center.org takes priority).

**Action**: Review log to see what was skipped
```bash
grep ",SKIPPED," data/validation/hvacexport/trane_integration_log.csv | head -20
```

---

## Next Brands

After Trane pilot succeeds, expand to:

1. **Carrier**
   ```bash
   ./scripts/run_hvacexport_integration_workflow.sh --brand CARRIER
   ```

2. **Lennox**
   ```bash
   ./scripts/run_hvacexport_integration_workflow.sh --brand LENNOX
   ```

3. **York**
   ```bash
   ./scripts/run_hvacexport_integration_workflow.sh --brand YORK
   ```

4. **Goodman**
   ```bash
   ./scripts/run_hvacexport_integration_workflow.sh --brand GOODMAN
   ```

---

## Full Documentation

See `docs/HVACEXPORT_INTEGRATION.md` for complete workflow details.

---

## Spec sheets (3rd attribute source)
If you have vendor spec sheets with model nomenclature tables (often higher-trust than inferred mappings),
see `docs/WORKFLOW.md` (Spec sheet PDF snapshots) and run:
```bash
./scripts/run_specs_snapshot_workflow.sh --snapshot-id <snapshot-id> --tag specs
```
