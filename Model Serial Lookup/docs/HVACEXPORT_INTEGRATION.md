# HVAC Export Integration Guide

## Overview

This guide documents the process for integrating model number decode rules from the HVAC export (decoder.xml) as supplementary attribute rules alongside existing building-center.org rules.

**Integration Philosophy**: HVAC export rules supplement (not replace) building-center.org rules. Building-center.org rules have priority as they're manually researched with evidence.

## Quick Start (Pilot: Trane)

### 1. Run Validation (Dry Run)

```bash
./scripts/run_hvacexport_integration_workflow.sh --brand TRANE --dry-run
```

This validates regex quality and SDI alignment without making changes.

### 2. Review Validation Reports

Check the outputs in `data/validation/hvacexport/`:

- `trane_regex_quality_report.csv` - Filter for `status=GOOD` (90%+ match rate)
- `trane_sdi_column_alignment.csv` - Verify attribute mappings
- `trane_attribute_conflicts.csv` - Review overlaps with building-center.org

**Quality Bar**: Only integrate rules with:
- `status=GOOD` (90%+ match rate if >10 samples)
- Clear SDI column alignment
- No conflicts with building-center.org

### 3. Run Full Integration

```bash
./scripts/run_hvacexport_integration_workflow.sh --brand TRANE
```

This merges supplementary rules and validates against SDI truth data.

### 4. Review Integration Results

Check:
- `trane_integration_log.csv` - What was added/skipped
- `trane_decode_accuracy_comparison.csv` - Before/after accuracy
- `trane_decode_mismatches.csv` - Cases where decoded ≠ truth

**Success Criteria**:
- No regressions (baseline accuracy maintained)
- Measurable improvements (additional attributes decoded)
- >85% accuracy on new decodes
- <5% conflict rate

### 5. Activate Merged Ruleset (if approved)

```bash
# Update CURRENT.txt to point to new ruleset
echo "$(date +%Y-%m-%d)-hvacexport-trane" > data/rules_normalized/CURRENT.txt

# Commit
git add data/rules_normalized/$(date +%Y-%m-%d)-hvacexport-trane/
git add data/validation/hvacexport/
git commit -m "Integrate HVAC export rules for Trane

- Added X supplementary attribute rules
- Validated against SDI truth data
- No regressions on existing rules

Integration log: data/validation/hvacexport/trane_integration_log.csv"
```

---

## Detailed Workflow

### Phase 1: Validation

#### 1.1 Regex Quality Validation

**Goal**: Test whether hvacexport regex patterns actually match real SDI model numbers.

```bash
python scripts/validate_hvacexport_regex_quality.py \
  --candidates-jsonl data/external_sources/hvacexport/.../AttributeDecodeRule.hvacexport.candidates.jsonl \
  --sdi-csv data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv \
  --brand TRANE \
  --min-threshold 90.0 \
  --output-dir data/validation/hvacexport/
```

**Outputs**:
- `trane_regex_quality_report.csv` - Match rates per rule
- `trane_regex_quality_details.csv` - Sample matches/non-matches

**Quality Thresholds**:
- `GOOD`: 90%+ match rate (if >10 samples), 30%+ (if ≤10 samples)
- `WEAK`: 10-30% match rate (needs review)
- `POOR`: <10% match rate (likely broken, skip)

#### 1.2 SDI Column Alignment

**Goal**: Map HVAC export attributes to SDI column names and validate format compatibility.

```bash
python scripts/analyze_hvacexport_sdi_alignment.py \
  --candidates-jsonl data/external_sources/hvacexport/.../AttributeDecodeRule.hvacexport.candidates.jsonl \
  --sdi-csv data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv \
  --current-rules data/rules_normalized/CURRENT/AttributeDecodeRule.csv \
  --brand TRANE \
  --output-dir data/validation/hvacexport/
```

**Outputs**:
- `trane_sdi_column_alignment.csv` - Attribute mapping strategy
- `trane_attribute_conflicts.csv` - Overlaps with building-center.org

**Alignment Actions**:
- `RENAME`: Attribute has SDI mapping (e.g., `HVACExport_CoolingTonCode` → `NominalCapacityTons`)
- `KEEP`: No SDI column (keep as intermediate code like `HVACExport_CoolingCode`)
- `MATCH`: Direct SDI match (e.g., `Refrigerant`)
- `SKIP`: Needs research or format incompatible

### Phase 2: Integration

#### 2.1 Merge Supplementary Rules

**Goal**: Add hvacexport rules to AttributeDecodeRule.csv without duplicating building-center.org rules.

```bash
python scripts/merge_hvacexport_supplementary.py \
  --current-rules data/rules_normalized/CURRENT/AttributeDecodeRule.csv \
  --hvacexport-candidates data/external_sources/hvacexport/.../AttributeDecodeRule.hvacexport.candidates.jsonl \
  --sdi-alignment data/validation/hvacexport/trane_sdi_column_alignment.csv \
  --quality-report data/validation/hvacexport/trane_regex_quality_report.csv \
  --min-quality GOOD \
  --brand TRANE \
  --output data/rules_normalized/YYYY-MM-DD-hvacexport-trane/AttributeDecodeRule.csv \
  --log data/validation/hvacexport/trane_integration_log.csv
```

**Logic**:
1. Skip brand+attribute if building-center.org has rule (priority 1)
2. Add high-quality rules with SDI-aligned names (priority 2)
3. Keep low-confidence as `HVACExport_*Code` (priority 3)

**Outputs**:
- `YYYY-MM-DD-hvacexport-trane/AttributeDecodeRule.csv` - Merged ruleset
- `trane_integration_log.csv` - What was added/skipped

#### 2.2 Validate Against SDI

**Goal**: Test merged ruleset accuracy using SDI truth data.

```bash
python scripts/validate_merged_ruleset_attributes.py \
  --sdi-csv data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv \
  --baseline-rules data/rules_normalized/CURRENT/AttributeDecodeRule.csv \
  --merged-rules data/rules_normalized/YYYY-MM-DD-hvacexport-trane/AttributeDecodeRule.csv \
  --brand TRANE \
  --output-dir data/validation/hvacexport/
```

**Validation Mappings**:
- `NominalCapacityTons` → SDI `KnownCapacityTons`
- `Refrigerant` → SDI `Refrigerant`
- `VoltageVoltPhaseHz` → SDI `Voltage (Volt-Phase)`

**Outputs**:
- `trane_decode_accuracy_comparison.csv` - Baseline vs. merged accuracy
- `trane_decode_mismatches.csv` - Decoded ≠ SDI truth (needs investigation)

### Phase 3: Capacity Code Mapping (Optional)

**Goal**: Infer code→tons mappings from SDI data with unit conversion detection.

**Use existing script**:

```bash
python scripts/hvacexport_generate_capacity_from_code_suggestions.py \
  --snapshot-id 2026-01-24_v3.84_enriched2 \
  --alignment-run-id <alignment_run_id> \
  --min-support 10 \
  --min-purity 90.0 \
  --require-unique-truth \
  --brands TRANE
```

**Logic**:
- Test unit conversions (direct tons, MBH÷12, BTUH÷12000)
- Pick conversion with highest correlation to SDI `KnownCapacityTons`
- Require 90% purity + 10 minimum samples

**Outputs**:
- Augmented JSONL with inferred mappings
- Rules renamed: `HVACExport_CoolingTonCode` → `NominalCapacityTons`

**Then re-run Phase 1-2 with augmented candidates.**

---

## Key Quality Thresholds

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| Regex match rate | 90% (if >10 samples) | Filter low-quality patterns |
| Capacity mapping purity | 90% | Ensure code→tons consistency |
| Capacity mapping support | 10 samples | Minimum sample size |
| Decode accuracy | 85%+ | New attributes must be accurate |
| Regression rate | 0% | Existing rules must not break |

---

## File Structure

### Source Files
- `data/static/hvacdecodertool/decoder.xml` - Original HVAC export (1.9MB, 129 brands)
- `data/external_sources/hvacexport/2026-01-24_v3.84_enriched2/` - Processed data
- `data/external_sources/hvacexport/.../runs/candidates__20260129T2245Z_relax_codes/` - Latest candidates (1,683 rules)

### Scripts
- `scripts/validate_hvacexport_regex_quality.py` - Phase 1.1
- `scripts/analyze_hvacexport_sdi_alignment.py` - Phase 1.2
- `scripts/merge_hvacexport_supplementary.py` - Phase 2.1
- `scripts/validate_merged_ruleset_attributes.py` - Phase 2.2
- `scripts/hvacexport_generate_capacity_from_code_suggestions.py` - Phase 3 (existing)
- `scripts/run_hvacexport_integration_workflow.sh` - Full automation

### Validation Outputs
- `data/validation/hvacexport/{brand}_regex_quality_report.csv`
- `data/validation/hvacexport/{brand}_sdi_column_alignment.csv`
- `data/validation/hvacexport/{brand}_integration_log.csv`
- `data/validation/hvacexport/{brand}_decode_accuracy_comparison.csv`
- `data/validation/hvacexport/{brand}_decode_mismatches.csv`

### Tests
- `tests/test_hvacexport_integration.py` - Integration test suite

---

## Troubleshooting

### Issue: Regex doesn't match any SDI models

**Cause**: Pattern too specific or format mismatch.

**Solution**: Review SDI model format, adjust regex or skip brand.

```bash
# Check SDI models for brand
grep "^[^,]*,TRANE," data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv | cut -d',' -f9 | head -20
```

### Issue: Code→tons mapping <90% purity

**Cause**: Unit ambiguity (MBH vs. BTUH) or SDI data quality.

**Solution**: Check unit conversion logic, flag for manual research.

```bash
# Review capacity mapping suggestions
python scripts/hvacexport_capacity_mapping_eval.py \
  --input-sdi data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv \
  --candidates-jsonl <capacity_from_codes_candidates.jsonl> \
  --min-support 10
```

### Issue: Voltage format doesn't match SDI

**Cause**: HVAC export uses numeric (voltage=480, phase=3), SDI uses text ("480V - Three Phase").

**Solution**: Add format conversion:
- Phase code → text: {1: "Single Phase", 3: "Three Phase"}
- Format: `f"{voltage}V - {phase_text}"`
- Handle ranges: `f"{v_min}V/{v_max}V - {phase_text}"`

**Implementation**: Add to `merge_hvacexport_supplementary.py` or skip if can't parse.

### Issue: Conflicts with building-center.org rules

**Cause**: Both sources have rules for same brand+attribute.

**Solution**: Keep building-center.org (priority 1), skip HVAC export.

Review conflicts:
```bash
cat data/validation/hvacexport/trane_attribute_conflicts.csv
```

---

## Expansion Strategy

### Pilot: Trane (Complete First)

1. Run full workflow
2. Validate accuracy >85%
3. Review mismatches
4. Commit if approved

### Phase 2: Major Brands

Expand to high-volume brands:
- Carrier
- Lennox
- York
- Goodman

Use same workflow per brand.

### Phase 3: Remaining Brands

Integrate remaining 120+ brands using automated workflow.

---

## Maintenance

### When decoder.xml Updates

1. Place new decoder.xml in `data/static/hvacdecodertool/`
2. Re-run processing pipeline:
   ```bash
   python scripts/hvacexport_parse.py --input data/static/hvacdecodertool/decoder.xml --output data/external_sources/hvacexport/YYYY-MM-DD_vX.XX
   python scripts/hvacexport_generate_attribute_candidates.py --snapshot-id YYYY-MM-DD_vX.XX_enriched2 --run-id candidates__$(date +%Y%m%dT%H%M%SZ)
   ```
3. Re-run integration workflow for affected brands

### Ongoing Validation

Periodically re-validate against updated SDI data:

```bash
./scripts/run_hvacexport_integration_workflow.sh --brand TRANE --dry-run
```

Check for accuracy regressions or new conflicts.

---

## Success Metrics

### Coverage
- **Before**: 30-40 brands with attribute rules (building-center.org)
- **Target**: 100+ brands with attribute rules (building-center.org + hvacexport)

### Accuracy
- **Baseline**: 95%+ accuracy (building-center.org rules)
- **Target**: 85%+ accuracy (hvacexport supplementary rules)
- **No regressions**: Maintain baseline accuracy

### Gap-Filling
- Populate missing SDI columns (where we can decode but SDI has no data)
- Enable attribute-based search/filtering in customer system

---

## References

### Related Documentation
- [HVAC Export Processing](../data/external_sources/hvacexport/README.md)
- [Attribute Decoder Architecture](../msl/decoder/attributes.py)
- [SDI Equipment Export](../data/equipment_exports/README.md)

### Key Scripts (Existing)
- `scripts/hvacexport_parse.py` - Parse decoder.xml
- `scripts/hvacexport_generate_attribute_candidates.py` - Generate JSONL rules
- `scripts/hvacexport_attribute_catalog.py` - Attribute inventory
- `scripts/hvacexport_generate_capacity_from_code_suggestions.py` - Capacity-specific rules

### Contact
For questions about this integration process, see:
- Plan document: `docs/HVACEXPORT_INTEGRATION_PLAN.md`
- Git history: `git log --grep="hvacexport"`
