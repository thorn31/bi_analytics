# TODO / CHECKLIST — Model/Serial Lookup

This file is the **single checklist** for what remains in Phase 1, Phase 2, and Phase 3.

Update rules:
- Keep this file current whenever Phase 1/2/3 work changes scope or reaches a milestone.
- When a checklist item is completed, mark it done and add a short note (run-id, ruleset folder, output path).
- Keep `docs/STATUS.md` aligned with the current “last known good” ruleset.

Last updated: 2026-01-27

---

## Current baselines
- Phase 1 ruleset: `data/rules_normalized/CURRENT_PHASE1.txt`
- Phase 2 sample output: `out/user_assets_sample_decoded_full_28b_latest.csv`
- Phase 2 recommended ruleset (Phase 3 promoted additions): `data/rules_normalized/2026-01-27-trane-fix-v3/` (see CURRENT.txt)
- Phase 3 baseline "next targets": `data/reports/trane-fix-v3/next_targets.md`
- **Current Trane accuracy: 94.0%** (up from 73.0%)

---

## Phase 1 — Building-Center ingestion → versioned rules

### Definition of done (Phase 1)
- [ ] Coverage: `msl report` shows broad decode coverage (brands/styles) and no obvious false-positive explosions.
- [ ] Validation: `msl validate` produces **0 validation exceptions** for the chosen release ruleset.
- [ ] Artifacts: `SerialDecodeRule.csv` + `AttributeDecodeRule.csv` present, plus `data/raw_html/<run>/` for reproducibility.
- [ ] Charts: OCR/overrides pipeline reduces `chart_required` where images are locally available.
- [ ] Documentation: `docs/STATUS.md` points to the correct latest ruleset and how to reproduce it.

### Remaining work (Phase 1)
- [ ] Expand discovery seeds to cover non-HVAC brands from real asset exports (e.g., pumps/fans/towers) if Building-Center has relevant pages.
- [ ] Run `fetch-images` for the chosen ruleset and resolve missing image hosts where possible (or record as permanent gaps).
- [ ] Run OCR end-to-end (normalize → validate → `msl ocr-overrides` → re-validate) to reduce `chart_required`.
- [ ] Attribute extraction: expand beyond capacity where Building-Center text is deterministic (Voltage, HP, GPM, etc.) while staying safe (anchored regex/positions).
- [x] Attribute extraction: capture `ModelNomenclature` references (PDF/image) as guidance when the tonnage decoder page has no deterministic text rule. (ruleset: `data/rules_normalized/2026-01-25-heuristic29a/`)
- [x] OCR model nomenclature images into text artifacts for later deterministic rule transcription. (`python3 -m msl ocr-model-nomenclature`, output: `data/manual_overrides/model_nomenclature_ocr_2026-01-25.csv`)
- [x] Mine OCR text into deterministic attribute overrides (Voltage + limited capacity/stage/refrigerant). (ruleset: `data/rules_normalized/2026-01-25-heuristic29a-ocrattrs2/`, overrides: `data/manual_overrides/attribute_overrides.jsonl`)
- [x] OCR serial charts into deterministic serial overrides (reduces `requires_chart`). (ruleset: `data/rules_normalized/2026-01-26-heuristic29a-ocrserial1-ocrattrs2/`, overrides: `data/manual_overrides/serial_overrides.jsonl`, run-id: `2026-01-26-ocrserial1`)
- [x] OCR additional serial charts + merge into overrides (ruleset: `data/rules_normalized/2026-01-26-heuristic35a-ocrserial2-ocrattrs2/`, overrides: `data/manual_overrides/serial_overrides.jsonl`, run-id: `2026-01-26-ocrserial2`)
- [x] Increase `evidence_excerpt` length so key instructions aren’t cut off mid-sentence. (ruleset regenerated: `data/rules_normalized/2026-01-26-heuristic36a-ocrserial2-ocrattrs2-prune1/`)
- [ ] Produce a “release” ruleset folder for Phase 2 consumption (new run-id once stabilized).

---

## Phase 2 — Deterministic decoder engine

### Definition of done (Phase 2)
- [ ] Input: Accepts a CSV export from equipment lists (Make/Model/Serial + optional type/description).
- [ ] Output: Emits decoded manufacture date + **generic Attributes** (not tons-only) with confidence + evidence + source.
- [ ] Safety: Avoids cross-brand false matches (brand normalization is explicit and testable).
- [ ] Explainability: Every decoded value includes a `SourceURL`/evidence excerpt.

### Remaining work (Phase 2)
- [x] Add stable output schema for attributes (row-per-attribute export in addition to `AttributesJSON`). (via `msl decode --attributes-output`, 2026-01-25)
- [x] Best-rule selection/tie-breaking when multiple rules match. (attributes: pick best per `AttributeName`; serial: century-expand `YY`, continue past matches that can’t decode year, `--min-manufacture-year` guard, 2026-01-25)
- [x] Add decode-time support for `BrandNormalizeRule.csv` (Phase 3 output) without hardcoding aliases in code. (ruleset-local file, 2026-01-25-sdi-promoted5)
- [ ] Add decode-time support for equipment-type context (if/when Phase 3 produces `EquipmentTypeRule.csv`).

---

## Phase 3 — Rule discovery from labeled asset reports

Plan reference: `docs/PLAN_PHASE3.md`

### Definition of done (Phase 3 MVP)
- [x] Ingest 1+ labeled asset reports and map columns → canonical schema (SDI export: `data/equipment_exports/2026-01-25/sdi_equipment_2026_01_25.csv`, run: `data/reports/2026-01-25-sdi-baseline2/`).
- [x] Produce baseline scorecard for current Phase 2 decoder vs ground truth (see `data/reports/2026-01-25-sdi-baseline2/baseline_decoder_scorecard.csv`).
- [x] Mine initial candidate rules (brand normalization + serial year + model capacity) (latest run: `data/rules_discovered/2026-01-25-sdi-mine8/candidates/`).
- [x] Promote passing candidates into a new versioned ruleset folder (latest promoted ruleset: `data/rules_normalized/2026-01-26-sdi-promoted18-2026-01-26-heuristic36a-manualadds3/`).
- [x] Emit validation/audit reports (holdout + false positives) for review (latest: `data/reports/2026-01-26-sdi-audit9/`).

### Remaining work (Phase 3)
- [ ] Expand mining beyond capacity: voltage, motor HP, flow GPM, etc. (only when model-coded patterns are strong and auditable).
- [ ] Improve promotion metadata: store audit metrics in a dedicated column/file (currently embedded in `limitations` to keep CSV schemas stable).
- [ ] Add brand-normalization audit: ensure BrandNormalizeRule promotions never reduce decode coverage for top brands.
- [x] Add AAON serial date decoding from SDI evidence (YYYYMM prefix). (ruleset: `data/rules_normalized/2026-01-26-sdi-promoted19-2026-01-26-heuristic36a-aaonserial`, baseline: `data/reports/2026-01-26-sdi-baseline13-aaonserial`)
- [x] Add Mitsubishi serial year decoding from SDI evidence (W/YW/ZW formats). (ruleset: `data/rules_normalized/2026-01-26-sdi-promoted20-2026-01-26-heuristic36a-mitsu`, baseline: `data/reports/2026-01-26-sdi-baseline14-mitsu`)

## Phase 3 Tasks (2026-01-26 through 2026-01-27)
- [x] Fix Column Mapping for 'Manuf.\nYear'
- [x] Enable Brand Normalization (Lowered thresholds)
- [x] Fix Carrier Style 1 Regex
- [x] Promote Manual Rules (ACE, Lochinvar)
- [x] **Trane:** Investigate 10-digit serials (Priority 1) - COMPLETED 2026-01-27
- [x] **AAON:** Discover Serial Year rules (Priority 2)
- [ ] **Goodman:** Analyze Attribute gaps (Priority 3)
- [x] Create detailed match reporting tool (msl/pipeline/report_matches.py)
- [x] **Trane Accuracy Fix:** Fixed length-based discrimination for Style 1 patterns (ruleset: `2026-01-27-trane-fix-v3`, accuracy: 73.0% → 94.0%)

## Phase 3 Maintenance Tasks
- [ ] **Apply manual fixes after every promotion:** Run `scripts/apply_manual_serial_fixes.py` after `phase3-promote` to ensure critical fixes persist (see `docs/WORKFLOW_RULESET_PROMOTION.md`)
- [ ] Consider integrating manual fixes into phase3-promote command for automation
