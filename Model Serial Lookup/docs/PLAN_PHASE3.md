# PLAN_PHASE3.MD — Rule Discovery from Labeled Asset Reports

## Purpose
Use completed (labeled) asset reports as "ground truth" to:
1) Discover new decoding rules and normalization mappings.
2) Validate them statistically and deterministically against the ground truth.
3) Promote only high-confidence rules into new versioned dictionaries used by the Phase 2 decoder engine.

Phase 3 does NOT implement Excel integration or external web lookups.
Phase 3 outputs updated dictionaries + evidence reports.

Project checklist / TODOs: `docs/TODO.md`

---

## Inputs
### A) Labeled asset reports (CSV/JSONL)
One or more files containing (or mappable to) these minimum fields:
- `AssetID` (or stable row key)
- `Make` (manufacturer / brand)
- `ModelNumber`
- `SerialNumber`
- `EquipmentType` (ground truth categorical)
- `KnownManufactureYear` (or `InstallYear` as proxy)
- `KnownCapacityTons` (or cooling BTUH convertible to tons)

Optional but useful:
- `KnownManufactureMonth` / `KnownManufactureWeek`
- `Refrigerant`
- `Voltage/Phase`
- `MotorHP`
- `Notes/Description`
- `Site/Facility`
- `InstallDate`

### B) Current rule dictionaries (from Phase 1/2)
Located in `data/rules_normalized/<version>/`:
- `SerialDecodeRule.csv`
- `AttributeDecodeRule.csv` (previously referred to as ModelDecodeRule)

---

## Outputs
### A) Candidate rule artifacts (Intermediate)
Stored in `data/rules_discovered/<run_id>/candidates/`:
- `SerialDecodeRule.candidates.jsonl`
- `AttributeDecodeRule.candidates.jsonl`
- `BrandNormalizeRule.candidates.jsonl` (New)
- `EquipmentTypeRule.candidates.jsonl` (New)

### B) Validation reports (Required for promotion)
Stored in `data/reports/<run_id>/`:
- `phase3_rule_discovery_summary.md`
- `candidate_rule_scorecard.csv`
- `holdout_validation_results.csv`
- `false_positive_audit.csv`

### C) Promoted dictionaries (New version folder)
Stored in `data/rules_normalized/<new_version>/`:
- `SerialDecodeRule.csv`
- `AttributeDecodeRule.csv`
- `BrandNormalizeRule.csv` (if applicable)
- `EquipmentTypeRule.csv` (if applicable)

Promotion requires passing explicit gates (below).

---

## Non-Goals / Constraints
- No external browsing/scraping.
- No "guessing" rules from a handful of examples.
- No decade disambiguation heuristics unless explicitly learnable and validated.
- No ML model deployment. Outputs are **explicit rules** (regex + position/mapping) compatible with the Phase 2 engine.
- Do not overwrite existing dictionaries; always create a new version folder in `data/rules_normalized/`.

---

## Definitions
### Ground truth fields
- Manufacture year: `KnownManufactureYear` (preferred) or `InstallYear` (proxy)
- Capacity: `KnownCapacityTons` (preferred) or `KnownCapacityBTUH/12000`
- Equipment type: `EquipmentType` (provided)

### Coverage
Percent of records for which the Phase 2 engine produces a non-null value for a target field.

### Accuracy
Percent of decoded values that match ground truth (within tolerance where applicable).

---

## Step 1 — Standardize and Profile Training Data
### 1.1 Normalize columns
Create a canonical schema mapping for each report:
- Map input columns to standard names (`Make`, `ModelNumber`, `SerialNumber`, etc.).
- Record mapping in `data/reports/<run_id>/source_column_map.csv`.

### 1.2 Normalize values (do not change meaning)
- Normalize `Make` strings (trim, uppercase, collapse whitespace).
- Normalize `ModelNumber` and `SerialNumber` using Phase 2 normalization functions (`msl.decoder.normalize`).
- Standardize `EquipmentType` labels into a controlled vocabulary (map only; no inference).

### 1.3 Data profiling
Compute:
- Counts by brand and equipment type.
- % missing for model/serial/year/capacity/type.
- Distributions for capacity (min/median/max per type).
Output: `data/reports/<run_id>/training_data_profile.md`

---

## Step 2 — Baseline Phase 2 Engine Performance
Run the current Phase 2 decoder engine (`msl decode`) on the labeled dataset and compute:
- Coverage and accuracy by brand for:
  - `ManufactureYear`
  - `CapacityTons` (via `AttributesJSON`)
- Confusion analysis for "NotDecoded" cases:
  - Missing serial/model
  - Unknown brand
  - No rule match

Output: `data/reports/<run_id>/baseline_decoder_scorecard.csv`

This baseline is used to quantify Phase 3 improvement.

---

## Step 3 — Candidate Rule Discovery (Rule Mining)

### 3A) Brand Normalization Mining
Goal: Map messy `Make` strings into stable canonical brands.

Method:
- Cluster `Make` strings by similarity (token-based).
- Propose mappings where:
  - Cluster size >= `MIN_N_BRAND` (default 20).
  - Cluster majority canonical brand share >= 98%.

Output candidates:
- `raw_make`, `canonical_brand`, `support_n`, `purity`, `examples`

### 3B) Serial Decode Rule Mining (Manufacture Year)
Goal: Discover serial patterns where year (and possibly month/week) can be extracted.

Process (per brand):
1) Consider only records with:
   - Non-empty serial.
   - Known manufacture year.
2) Group serials by:
   - Length.
   - Character class signature (e.g., `NNNNNNN`, `ANNNNN`, etc.).
3) For each group:
   - Attempt to identify positions that correlate with year:
     - Test candidate substrings (1–4 chars) across positions.
     - Evaluate whether substring-to-year mapping is consistent.
   - Propose candidate rule ONLY if:
     - `support_n` >= `MIN_N_SERIAL` (default 50).
     - Accuracy >= 98% on training split.
     - Regex specificity is sufficient (low match risk outside brand).

Important:
- Do not assume decade; if a 2-digit year pattern exists, mark as ambiguous unless data proves a single-decade span AND is stable in holdout.

Candidate rule must include:
- `serial_regex`
- `date_fields` (year extraction via positions or mapping)
- `support_n`
- `train_accuracy`
- `notes`

### 3C) Attribute Capacity Rule Mining (Nominal Tons)
Goal: Detect capacity codes embedded in model numbers.

Process (per brand AND equipment type where relevant):
1) Consider only records with:
   - Non-empty model.
   - Known capacity tons.
2) Normalize capacity to a comparable numeric (float tons).
3) Search for common capacity code patterns:
   - 2–3 digit numeric tokens in the model.
   - Standardized tokens like 018/024/030/036/042/048/060 etc.
   - Suffix/prefix segments separated by dashes.
4) Fit candidate rules:
   - Extract token at position or via regex group.
   - Transform token to tons (e.g., token/12k or direct mapping).
5) Promote candidate only if:
   - `support_n` >= `MIN_N_MODEL` (default 50).
   - Tolerance match >= 95% within ±0.5 tons (configurable).
   - Low false-positive risk across other brands.

Candidate rule must include:
- `model_regex` (or null if position-based is safer)
- `attribute_name` (`NominalCapacityTons`)
- `value_extraction` (positions/pattern + transform/mapping)
- `support_n`, `train_accuracy`, `notes`

### 3D) Equipment Type Classification Rules (Optional)
Goal: Produce explicit rules mapping patterns to `EquipmentType` categories.

Process:
- For each brand, extract discriminative tokens from model/description.
- Propose rules like:
  - `if model contains token X and brand Y => type = WSHP`
- Promote only if:
  - `support_n` >= `MIN_N_TYPE` (default 100).
  - Precision >= 98% for the target class (avoid false positives).
- Allow "Unknown" fallback; never force classification.

Output:
- `EquipmentTypeRule.candidates.jsonl`

---

## Step 4 — Validation Gates (Hard Requirements)

### 4.1 Train/holdout split
Per brand, split records deterministically:
- 80% train / 20% holdout
- Stratify by equipment type where possible

### 4.2 Candidate acceptance thresholds (defaults)
- `MIN_N_BRAND` = 20
- `MIN_N_SERIAL` = 50
- `MIN_N_MODEL` = 50
- `MIN_N_TYPE` = 100
- Train accuracy >= 98%
- Holdout accuracy >= 98%
- False positive rate <= 0.5% when evaluated against:
  - Other brands.
  - Other types.
  - Random serial/model strings from the dataset.

### 4.3 False positive audit
For each candidate regex:
- Test against all records NOT in the target brand.
- Report any matches as "collision risk".
Candidates with collisions are rejected unless the collisions can be resolved by adding constraints.

Outputs:
- `data/reports/<run_id>/holdout_validation_results.csv`
- `data/reports/<run_id>/false_positive_audit.csv`

---

## Step 5 — Promotion into Versioned Dictionaries
Only candidates passing all gates are promoted.

### 5.1 Versioning
Create a new folder: `data/rules_normalized/<YYYY-MM-DD>-discovery-v1`

### 5.2 Promotion rules
- Add promoted rules to the relevant dictionary CSVs:
  - Merge with existing rules from `SerialDecodeRule.csv` and `AttributeDecodeRule.csv`.
  - Add new files `BrandNormalizeRule.csv` and `EquipmentTypeRule.csv` if candidates exist.
- Preserve metadata:
  - `source = internal_asset_reports`
  - `support_n`, `train_accuracy`, `holdout_accuracy`
  - `example_serials` / `examples`
  - `created_on`
- Do not delete existing rules; only add or supersede with explicit precedence metadata.

Output:
- `data/rules_normalized/<new_version>/*.csv`

---

## Step 6 — Re-Score the Decoder (Improvement Check)
Run Phase 2 engine again (`msl decode`) using the promoted dictionaries and compute:
- Coverage delta.
- Accuracy delta.
- Breakdown by brand/type.

Output: `data/reports/<run_id>/post_promotion_scorecard.csv`

---

## Deliverables Summary
1) Candidate rules (JSONL) with scorecard.
2) Validation reports (holdout + false positive audits).
3) Promoted dictionaries (new version).
4) Before/after decoder performance summary.

---

## Exit Criteria
Phase 3 is complete when:
- Promoted rules increase manufacture year coverage by >= 10% with no accuracy regression, OR
- Promoted rules significantly improve one high-volume brand where baseline coverage is weak.
- False positives remain below threshold across non-target brands.

End of Phase 3 Plan.
