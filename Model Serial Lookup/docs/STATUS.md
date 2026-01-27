# STATUS — Model/Serial Lookup (Resume Notes)

## Goal
Build an **offline, versioned rule dictionary** from Building-Center pages to decode equipment information from:
- `Make` (manufacturer)
- `SerialNumber` (manufacture date rules)
- `ModelNumber` (attribute extraction rules; capacity is only one attribute)

Phase 1 = one-time ingestion + normalization into CSV rule dictionaries.  
Phase 2 = deterministic decoder engine consuming those CSVs (Excel/Power Query comes later).
Phase 3 = rule discovery from labeled asset reports (see `docs/PLAN_PHASE3.md`).

Project checklist / TODOs live in `docs/TODO.md` (keep it updated).

---

## Current state (last known good run)
Recommended "current" pointers (as of 2026-01-27):
- **Ruleset (Master):** `data/rules_normalized/2026-01-27-trane-fix-v3/` (see CURRENT.txt)
- **Baseline report:** `data/reports/trane-fix-v3/`
- **Trane accuracy:** 94.0% (up from 73.0%)

Previous pointers (2026-01-26):
- Phase 1 baseline ruleset: `data/rules_normalized/2026-01-26-heuristic36a-ocrserial2-ocrattrs2-prune1`
- Phase 2 recommended ruleset: `data/rules_normalized/2026-01-26-sdi-promoted20-2026-01-26-heuristic36a-mitsu`
- Phase 3 baseline report: `data/reports/2026-01-26-sdi-baseline14-mitsu`

Ruleset (Phase 1 output):
- `data/rules_normalized/2026-01-25-heuristic29a/`
  - `SerialDecodeRule.csv` (includes `image_urls`)
  - `AttributeDecodeRule.csv` (includes `image_urls`)
  - Attribute extraction improvement: emits `ModelNomenclature` guidance rows for tonnage-decoder pages where the actual model nomenclature is only available in images/PDFs.

Ruleset (Phase 1 output + OCR-derived attribute overrides):
- `data/rules_normalized/2026-01-25-heuristic29a-ocrattrs2/`
  - Adds deterministic attribute decode rules mined from OCR text:
    - `VoltageVoltPhaseHz`
    - `NominalCapacityTons` (when the OCR includes explicit example models)
    - limited `Refrigerant` / `CompressorStage` where code binding is unambiguous

Ruleset (Phase 1 output + OCR serial charts + OCR model attributes):
- `data/rules_normalized/2026-01-26-heuristic29a-ocrserial1-ocrattrs2/`
  - OCR-derived `serial_overrides.jsonl` applied during validation reduced `requires_chart=true` date fields from 127 → 110.

Ruleset (Phase 1 output + improved color-span parsing + improved text parsing + OCR serial charts + OCR model attributes):
- `data/rules_normalized/2026-01-26-heuristic35a-ocrserial2-ocrattrs2/`
  - Improves parsing of “colored digit” examples (works even when pages don’t include an explicit Legend line, e.g. Bosch water heater styles).
  - Improves parsing of HTML entities and multi-field single-line instructions (e.g. `&amp;` in “1st & 2nd digits”).
  - OCR-derived serial overrides applied during validation reduced `requires_chart=true` date fields to 107.

Ruleset (Phase 1 output; same features, plus longer evidence excerpts):
- `data/rules_normalized/2026-01-26-heuristic36a-ocrserial2-ocrattrs2-prune1/`
  - `evidence_excerpt` now keeps up to ~600 chars (HTML-unescaped + whitespace-collapsed) so instructions aren’t cut off mid-sentence.

Ruleset (Phase 3 promoted additions; recommended for Phase 2 decoding against real equipment exports):
- `data/rules_normalized/2026-01-26-sdi-promoted20-2026-01-26-heuristic36a-mitsu/`
  - Adds a small set of **internally-mined** decode rules (capacity + 1 serial-year rule) on top of the Phase 1 corpus.
  - Includes the OCR-derived serial/attribute improvements from Phase 1.
  - Includes `BrandNormalizeRule.csv` (if present) for ruleset-local make normalization (used by `msl decode`, `msl gap-report`, and Phase 3 baseline/mine).
  - Includes `data/rules_discovered/manual_additions/SerialDecodeRule.candidates.jsonl` promoted into the ruleset (currently Lochinvar formats found in real assets).
  - Brand normalization additions: `LOCHENVAR` and `LOCHINVAR POWER-FIN` map to `LOCHINVAR`.
  - AAON: adds a deterministic serial date rule for common `YYYYMM...` prefixes (mined from SDI export).
  - Mitsubishi: adds deterministic serial year rules for common `W`/`YW`/`ZW` formats (mined from SDI export).
  - Serial guidance cleanup: prunes "style list" `no_data` artifacts so `SerialDecodeRule.csv` better reflects real decode vs actionable guidance.
  - Restores Phase 3 mined capacity rules for top brands (TRANE, AAON, MITSUBISHI, LENNOX/LENOX) with holdout validation.

Ruleset (Trane serial fix applied; current master):
- `data/rules_normalized/2026-01-27-trane-fix-v3/`
  - **Major Fix:** Trane Style 1 serial patterns now use length-based discrimination to prevent 10-digit modern serials from incorrectly matching legacy 2002-2009 rule
  - Style 1 (2002-2009): Added `(?=.{7,9}$)` length constraint (7-9 characters only)
  - Style 1 (2010+): Added `(?=.{10,}$)` length constraint (10+ characters only)
  - **Impact:** Trane overall accuracy: 73.0% → 94.0% (+21.1 percentage points)
  - 10-digit serial accuracy: 60.9% → 93.6% (+32.7 percentage points)
  - Style 1 (2002-2009) accuracy: 61.8% → 95.3% (+33.5 percentage points)
  - Fixed serials like `22226NUP4F`, `214410805D`, `23033078JA` now decode correctly as 2022, 2021, 2023
  - See `docs/trane_fix_summary.md` for technical details
  - **IMPORTANT:** Manual fixes must be reapplied after every promotion - see `docs/WORKFLOW_RULESET_PROMOTION.md`

Cached source corpus (Phase 1 raw archive):
- `data/raw_html/2026-01-25/` contains 578 fetched pages:
  - HVAC age pages
  - Tonnage decoder pages
  - Water-heater age pages (expanded coverage)

Quick coverage report:
```bash
python3 -m msl report --ruleset-dir $(cat data/rules_normalized/CURRENT.txt)
```

Sample input + output used for checking against your asset list:
- Input: `out/user_assets_sample.csv`
- Serial decode output (Phase 2 serial-only): `out/user_assets_sample_decoded_serial.csv`
- Full decode output (serial + attributes): `out/user_assets_sample_decoded_full_28b_latest.csv`

Phase 3 baseline reports (SDI export):
- Baseline (Phase 1 ruleset): `data/reports/2026-01-25-sdi-baseline2/`
- Baseline (Phase 3 promoted ruleset, current decoder): `data/reports/2026-01-26-sdi-baseline7-promoted12/`
- Baseline (Phase 3 promoted ruleset, current decoder): `data/reports/2026-01-26-sdi-baseline8-promoted14/`
  - Includes `baseline_attributes_long.csv` for Excel-friendly validation.
- Baseline (current): `data/reports/2026-01-26-sdi-baseline14-mitsu/`
  - Includes `baseline_attributes_long.csv` for Excel-friendly validation.
  - Includes `next_targets.md` + `next_targets_by_brand.csv` for “what to fix next” prioritization.

---

## Ruleset Promotion Workflow (Phase 3)

**CRITICAL:** After every `phase3-promote`, manual fixes must be applied to ensure critical patterns persist.

### Standard Promotion Workflow

```bash
# 1. Promote new candidates
python3 -m msl phase3-promote \
  --base-ruleset-dir $(cat data/rules_normalized/CURRENT.txt) \
  --candidates-dir data/rules_discovered/YYYY-MM-DD-source/candidates \
  --run-id YYYY-MM-DD-descriptive-name \
  --out-dir data/rules_normalized

# 2. Apply manual fixes (CRITICAL - don't skip!)
python3 scripts/apply_manual_serial_fixes.py \
  --ruleset-dir data/rules_normalized/YYYY-MM-DD-descriptive-name

# 3. Validate with baseline
python3 -m msl phase3-baseline \
  --input data/equipment_exports/latest/equipment.csv \
  --ruleset-dir data/rules_normalized/YYYY-MM-DD-descriptive-name \
  --run-id YYYY-MM-DD-validation

# 4. Update CURRENT pointer if validated
echo "data/rules_normalized/YYYY-MM-DD-descriptive-name" > data/rules_normalized/CURRENT.txt
```

**Why this is required:** The `phase3-promote` deduplication uses exact pattern matching, so manually fixed regexes have different keys than their broken originals. Future mining could rediscover broken patterns from external sources, creating duplicates. The fix script detects and repairs these automatically.

**See:** `docs/WORKFLOW_RULESET_PROMOTION.md` for complete documentation.

---

## How to run the pipeline (Phase 1)
All commands run from repo root.

1) Discover (TOC → page list)
```bash
python3 -m msl discover \
  --seed-url https://www.building-center.org/hvac-table-of-contents-2/ \
  --seed-url https://www.building-center.org/tonnage-estimate-main/ \
  --seed-url https://www.building-center.org/water-heater-table-of-contents-age-manufacture-date-serial-number/
```

2) Fetch HTML (archive)
```bash
python3 -m msl fetch --page-index data/page_index/YYYY-MM-DD/page_index.csv
```

For iterative runs:
```bash
python3 -m msl fetch --page-index data/page_index/YYYY-MM-DD/page_index.csv --skip-existing
```

3) Extract sections (HVAC-age styles + tonnage/model decoder text)
```bash
python3 -m msl extract --raw-dir data/raw_html/YYYY-MM-DD
```

Note: A corrected extraction run that derives `brand` from URL slugs (prevents cross-brand aliasing) is:
- `data/extracted_sections/2026-01-25-extract2/extracted_sections.jsonl`

Latest extraction run:
- `data/extracted_sections/2026-01-25-extract3/extracted_sections.jsonl`
  - Captures `pdf_urls` + `image_urls` on tonnage decoder pages for later OCR/manual transcription

4) Normalize (heuristic, no API key required)
```bash
python3 -m msl normalize --provider heuristic --extracted-dir data/extracted_sections/YYYY-MM-DD --run-date YYYY-MM-DD-<tag>
```

5) Validate + export CSV rules
```bash
python3 -m msl validate --staged-dir data/rules_staged/YYYY-MM-DD-<tag> --run-date YYYY-MM-DD-<tag>
```

## OCR helpers
### Model nomenclature OCR (Phase 1 attributes)
If a tonnage decoder page only has a model nomenclature diagram (image/PDF), Phase 1 records it as:
- `AttributeDecodeRule.attribute_name = ModelNomenclature` with `rule_type=guidance` and `guidance_action=chart_required`

To OCR those images into text files for later transcription into deterministic attribute rules:
```bash
python3 -m msl ocr-model-nomenclature \
  --ruleset-dir data/rules_normalized/2026-01-25-heuristic29a \
  --images-log data/logs_images/2026-01-25-extract3-img1/fetch_images_log.csv \
  --run-id 2026-01-25-ocr-model1 \
  --output-csv data/manual_overrides/model_nomenclature_ocr_2026-01-25.csv
```

Then mine deterministic AttributeDecodeRule overrides (Voltage + limited others) from the OCR text:
```bash
python3 -m msl mine-ocr-attributes \
  --input-csv data/manual_overrides/model_nomenclature_ocr_2026-01-25.csv \
  --out-overrides data/manual_overrides/attribute_overrides.jsonl
```

Finally, re-run validation to apply the overrides into a new ruleset:
```bash
python3 -m msl validate \
  --staged-dir data/rules_staged/2026-01-25-heuristic29a \
  --run-date 2026-01-25-heuristic29a-ocrattrs2
```

---

## How to run the decoder (Phase 2 serial-only, current)
This currently decodes:
- serial manufacture date (from `SerialDecodeRule.csv`)
- model-derived attributes (from `AttributeDecodeRule.csv`) as `AttributesJSON` (currently limited scope; see gaps below)

Attribute decoding policy (current):
- Uses only `rule_type=decode` attribute rules.
- Deduplicates by `(AttributeName, Units, Value)` per asset (keeps the preferred source URL when multiple equivalent rules exist).

## Gap analysis helper
To see why assets are still `NotDecoded` / `Partial` for a given input CSV:
```bash
python3 -m msl gap-report \
  --ruleset-dir data/rules_normalized/2026-01-25-heuristic20b \
  --input <your_assets.csv> \
  --output out/asset_gaps.csv
```

```bash
python3 -m msl decode \
  --ruleset-dir $(cat data/rules_normalized/CURRENT.txt) \
  --input out/user_assets_sample.csv \
  --output out/user_assets_sample_decoded_full.csv
```

Optional: emit a row-per-attribute output CSV (better for Excel/Power Query):
```bash
python3 -m msl decode \
  --ruleset-dir $(cat data/rules_normalized/CURRENT.txt) \
  --input out/user_assets_sample.csv \
  --output out/user_assets_sample_decoded_full.csv \
  --attributes-output out/user_assets_sample_attributes.csv
```

Safety: by default, the decoder skips decoded years earlier than 1980 to avoid false decodes from “obsolete-era” styles.
You can disable this if you need older equipment:
```bash
python3 -m msl decode \
  --ruleset-dir $(cat data/rules_normalized/CURRENT.txt) \
  --input out/user_assets_sample.csv \
  --output out/user_assets_sample_decoded_full.csv \
  --min-manufacture-year 0
```

Decade handling: if a rule encodes `YY` for year, Phase 2 expands it to `YYYY` using a pivot around the current year.

Output columns include:
- `ManufactureYear/Month/Week` (when decodable)
- `AttributesCount`, `AttributesJSON`
- `DecodeStatus` (`Decoded|Partial|NotDecoded`)

---

## Known issues / gaps
### 1) Trane "Style 1" has era-dependent logic
The Building-Center Trane page describes:
- **2002–2009**: year = position 1; week = positions 2–3
- **2010+**: year = positions 1–2; week = positions 3–4

Status: **FIXED** in `data/rules_normalized/2026-01-27-trane-fix-v3/` using length-based discrimination:
- `Style 1 (2002-2009)`: Matches 7-9 character serials only via `(?=.{7,9}$)` lookahead
- `Style 1 (2010+)`: Matches 10+ character serials only via `(?=.{10,}$)` lookahead

This prevents overlap between the two formats. Modern 10-digit serials (like `22226NUP4F`) now correctly decode as 2022 instead of 2002.

**Persistence:** This fix must be reapplied after every `phase3-promote` using `scripts/apply_manual_serial_fixes.py`. See `docs/WORKFLOW_RULESET_PROMOTION.md` and `docs/PERSISTENCE_SOLUTION.md` for details.

### 1b) Avoid cross-brand aliasing at decode time
Some brands are related (e.g., American Standard / Trane), but merging them at the `brand` key can cause false matches
across equipment categories (e.g., water heaters vs HVAC). Phase 2 currently keeps:
- `AMERICAN STANDARD` separate from `TRANE`

If we decide to unify brands later, we should do it with explicit equipment-type context.

### 2) Many manufacturers in the provided asset list aren’t in the current seeds
The current discovery seeds focus on HVAC-age pages + tonnage decoder pages.  
Brands like `TACO`, `GREENHECK`, `BAC`, `TELEDYNE`, etc. may require additional Building-Center indexes/pages to be included in discovery to get serial rules.

### 2b) Image archive has a few unreachable hosts
`msl fetch-images` downloads referenced charts/photos. A small number of image URLs point to `staging2.building-center.org` which fails DNS resolution; these remain missing in the local image archive.

### 2c) Optional manual overrides (to reduce guidance)
See `docs/MANUAL_OVERRIDES.md` for how to transcribe chart mappings once into `data/manual_overrides/serial_overrides.jsonl` so the pipeline can convert `chart_required` guidance rules into deterministic decode rules.

### 2d) OCR-assisted overrides (automated chart transcription)
If OCR tooling is installed (`tesseract`, `convert`), you can generate overrides automatically from downloaded images:
```bash
python3 -m msl ocr-overrides \
  --ruleset-dir data/rules_normalized/2026-01-25-heuristic28b \
  --images-log data/logs_images/2026-01-25/fetch_images_log.csv \
  --out-overrides data/manual_overrides/serial_overrides.jsonl \
  --run-id 2026-01-25-ocr1
```

Then re-run validation to emit a new ruleset with those overrides applied:
```bash
python3 -m msl validate \
  --staged-dir data/rules_staged/2026-01-25-heuristic28b \
  --run-date 2026-01-25-heuristic28b-ocr1
```

Impact (last run):
- `requires_chart=true` date fields reduced from 37 → 17 by OCR-derived mappings (more deterministic month/year decoding).

### 3) Attribute rules are capacity-focused so far
`AttributeDecodeRule.csv` is currently mostly `NominalCapacityTons` / `NominalCapacityCode`.
We want to expand to generic attributes (Voltage, MotorHP, FlowGPM, etc.) only when explicitly documented.

Note: for brands where Building-Center text says the tonnage code is “in the middle” / otherwise not anchored,
the Phase 1 heuristic keeps the mapping as `rule_type=guidance` to avoid incorrect automatic extraction.

### 4) Model decoding is not integrated into `msl decode` yet
Status: attribute extraction is integrated into `msl decode` as `AttributesJSON`, but coverage is still limited (capacity-oriented).

---

## In-progress work (next session)
1) Decide next expansion:
   - Add more Building-Center discovery seeds for non-HVAC equipment brands (pumps/fans/boilers), or
   - Expand AttributeDecodeRule extraction beyond capacity where explicitly documented.

2) (Optional) Integrate AttributeDecodeRule into `msl decode` output once Phase 1 attribute rules are expanded and tightened (avoid false matches via `model_regex` constraints).

### Phase 3 Progress (2026-01-26 through 2026-01-27)
- **Current Ruleset:** `data/rules_normalized/2026-01-27-trane-fix-v3/`
- **Major Wins:**
  - **Trane:** Overall accuracy 73.0% → 94.0% (Length-based pattern discrimination fix)
  - **Lochinvar:** Coverage 0% → 59.5% (Manual rules + Typo fix 'LOCHENVAR')
  - **Lennox:** Coverage 0.9% → 89% (Typo fix 'LENOX')
  - **Mitsubishi/AAON:** Attribute coverage ~55-58% (Mined from data)
  - **Carrier:** Accuracy boosted to 93% (Regex fix)
- **Known Gaps:**
  - **Greenheck:** No universal nomenclature found
  - **Goodman:** Attribute gaps need analysis

### New Features

**Detailed Match Analysis (2026-01-26)**
- **Tool:** `python3 -m msl.pipeline.report_matches`
- **Purpose:** Generates a human-readable Markdown report (detailed_match_analysis.md) from decoder output
- **Insight:** Pinpointed Trane Style 1 (2002-2009) as the primary accuracy bottleneck (61.8% matching known labels)

**Manual Fix Persistence (2026-01-27)**
- **Tool:** `scripts/apply_manual_serial_fixes.py`
- **Purpose:** Maintains a registry of critical regex fixes and automatically applies them after ruleset promotion
- **Why needed:** `phase3-promote` uses exact pattern matching, so fixed patterns have different keys than broken originals
- **Usage:** Must be run after every `phase3-promote` to prevent regressions
- **Docs:** See `docs/WORKFLOW_RULESET_PROMOTION.md` and `docs/PERSISTENCE_SOLUTION.md`
