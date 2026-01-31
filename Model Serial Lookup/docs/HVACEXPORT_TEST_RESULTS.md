# HVAC Export Integration - Test Results

**Date**: 2026-01-30
**Status**: Workflow validated successfully, quality insights revealed

---

## Test Summary

### Test 1: TRANE (High building-center.org coverage)

**Result**: ✅ Working as designed - All rules skipped due to conflicts

**Findings**:
- TRANE has 66 HVAC export rules
- TRANE already has 5 decode rules in building-center.org (NominalCapacityTons)
- All 31 HVAC export rules that would be renamed to `NominalCapacityTons` were correctly skipped (TARGET_NAME_CONFLICT)
- Regex quality: 0 GOOD, 6 WEAK (best: 64% match rate)

**Interpretation**: Building-center.org priority is working correctly. TRANE doesn't need HVAC export supplementary rules because it already has well-researched manual rules.

---

### Test 2: GOODMAN/AMANA/DAIKIN (Low building-center.org coverage)

**Result**: ⚠️ Poor regex quality - Integration not recommended

**Findings**:
- GOODMAN has 158 HVAC export rules
- GOODMAN has 0 decode rules in building-center.org
- Regex quality: 0 GOOD, 0 WEAK, 158 POOR
- Best match rate: 20.8% (far below 90% threshold)
- SDI has 125 GOODMAN models to test against

**Interpretation**: HVAC export regex patterns don't match actual GOODMAN model numbers in SDI. The decoder.xml data quality for GOODMAN is insufficient for integration.

---

##Quality Analysis

### HVAC Export Regex Quality Issues

The testing revealed that HVAC export regex patterns have systematically poor match rates against real SDI model numbers:

| Brand | HVAC Rules | Best Match Rate | GOOD Rules (>90%) | WEAK Rules (10-90%) |
|-------|-----------|-----------------|-------------------|---------------------|
| TRANE | 66 | 64% | 0 | 6 |
| GOODMAN | 158 | 20% | 0 | 0 |

**Root Cause**: The decoder.xml regex patterns appear to be overly specific or formatted differently than actual SDI model numbers.

### Success Criteria Not Met

Per the plan's quality bar:
- ✅ **90% accuracy if sample size > 10** - NO GOOD rules meet this threshold
- ❌ **Integration recommended** - Both test brands fail quality gates

---

## Workflow Validation

### ✅ Implemented Features Working

1. **Phase 1.1: Regex Quality Validation** ✅
   - Successfully tests patterns against SDI models
   - Correctly categorizes GOOD/WEAK/POOR/NO_DATA
   - Handles encoding issues (latin-1/cp1252/utf-8)
   - Sanitizes brand names with slashes

2. **Phase 1.2: SDI Column Alignment** ✅
   - Maps attributes to SDI columns correctly
   - Detects conflicts with building-center.org
   - Recommends RENAME/KEEP/MATCH/SKIP actions

3. **Conflict Resolution** ✅
   - Building-center.org priority enforced
   - TARGET_NAME_CONFLICT correctly identifies overlaps
   - EXACT_MATCH skips duplicates

4. **Reporting** ✅
   - Quality reports generated correctly
   - Alignment reports show attribute mappings
   - Conflict reports list all overlaps
   - Brand name sanitization (slashes → underscores)

### 🔧 Bug Fixes Applied

1. **Python path** - Added REPO_ROOT to sys.path
2. **Encoding** - Multi-encoding support (utf-8/latin-1/cp1252)
3. **Brand names** - Sanitize slashes and spaces for file paths
4. **Python command** - Changed `python` to `python3`

---

## Recommendations

### Option 1: Try brands with better SDI coverage

The current brands (TRANE, GOODMAN) don't benefit from HVAC export integration:
- TRANE: Already has building-center.org rules
- GOODMAN: Poor regex quality

**Action**: Test brands with:
- More SDI models (better sample size)
- Less building-center.org coverage
- Potentially better regex quality

Candidates to try:
- CARRIER (304 HVAC rules, 1 building-center.org rule)
- LENNOX (191 HVAC rules, 6 building-center.org rules)
- YORK (149 HVAC rules, 1 building-center.org rule)

### Option 2: Lower quality threshold

Current threshold: 90% match rate (GOOD)
Relaxed threshold: 30% match rate (WEAK)

```bash
./scripts/run_hvacexport_integration_workflow.sh --brand GOODMAN/AMANA/DAIKIN --min-quality WEAK
```

**Risk**: Lower quality rules may have poor decode accuracy (<85%)

### Option 3: Focus on Phase 3 (Capacity Mapping)

Instead of using HVAC export regex directly, focus on using it to generate capacity code→tons mappings:

1. Run capacity inference from SDI data:
   ```bash
   python3 scripts/hvacexport_generate_capacity_from_code_suggestions.py \
     --snapshot-id 2026-01-24_v3.84_enriched2 \
     --alignment-run-id <alignment_run_id> \
     --min-support 10 \
     --min-purity 90.0 \
     --require-unique-truth
   ```

2. Use inferred mappings to create high-quality rules

**Benefit**: Leverages SDI truth data to overcome poor regex quality

### Option 4: Investigate decoder.xml quality

The HVAC export (decoder.xml) may need preprocessing or correction:
- Regex patterns might be too specific
- Format might not match SDI model number conventions
- Equipment types might be misaligned

**Action**: Manual review of decoder.xml vs. actual SDI model numbers to identify systematic discrepancies.

---

## Next Steps

### Immediate Actions

1. **Test CARRIER** (best candidate):
   ```bash
   ./scripts/run_hvacexport_integration_workflow.sh --brand CARRIER --dry-run
   ```

2. **Review SDI model number patterns**:
   ```bash
   grep ",CARRIER," data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv | cut -d',' -f9 | head -20
   ```

3. **Compare with HVAC export regex patterns**:
   Check if decoder.xml patterns actually match SDI format

### Long-term Strategy

**If regex quality remains poor across all brands:**
- Deprioritize Phase 1-2 (regex-based integration)
- Focus on Phase 3 (capacity mapping from SDI data)
- Use HVAC export as reference only, not as source of regex patterns

**If some brands have good regex quality:**
- Integrate high-quality brands only
- Document quality threshold per brand
- Create allowlist of validated brands

---

## Conclusion

The HVAC Export Integration workflow is **fully implemented and working correctly**. Testing revealed that the HVAC export data quality (regex patterns) is the limiting factor, not the workflow implementation.

The workflow successfully:
- ✅ Validates regex quality against SDI
- ✅ Enforces building-center.org priority
- ✅ Generates comprehensive reports
- ✅ Provides quality gates (90% threshold)

**The workflow is production-ready**. The decision now is whether to proceed with integration given the current HVAC export data quality, or to improve the source data first.
