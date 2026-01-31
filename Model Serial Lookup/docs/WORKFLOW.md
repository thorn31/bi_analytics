# WORKFLOW — Model/Serial Lookup (Action-Driven)

This repo is operated via a small set of deterministic **actions**. The canonical operator entry point is:

```bash
python3 scripts/actions.py --help
```

## Quick start (improve loop)
Run the end-to-end improvement workflow on a **labeled** dataset (must include `KnownManufactureYear`):

```bash
python3 scripts/actions.py workflow.improve \
  --input data/equipment_exports/2026-01-25/sdi_equipment_2026_01_25.csv \
  --tag sdi-smoke
```

This writes a single run folder under `data/reports/<run-id>/` with a consolidated report:
- `data/reports/<run-id>/WORKFLOW_REPORT.md`

To promote candidates (creates a new immutable ruleset folder and updates CURRENT by default):

```bash
python3 scripts/actions.py workflow.improve \
  --input data/equipment_exports/2026-01-25/sdi_equipment_2026_01_25.csv \
  --tag sdi-promote \
  --promote \
  --new-ruleset-id 2026-01-28-sdi-master-v4
```

Promotion is **hard-gated**: malformed candidate rows block promotion (e.g., serial decode candidates must include `example_serials`).

## Adding new knowledge (where to put it)
There are two “manual input” paths. Pick the one that matches what you learned:

### A) Add a new decode rule from an outside resource (recommended)
Use `data/rules_discovered/manual_additions/` to add *candidate rules* that flow through the same promotion path as mined rules:
- Serial: `data/rules_discovered/manual_additions/SerialDecodeRule.candidates.jsonl`
- Attributes: `data/rules_discovered/manual_additions/AttributeDecodeRule.candidates.jsonl`
- Brand normalization: `data/rules_discovered/manual_additions/BrandNormalizeRule.candidates.csv`

Equipment type scoping (optional but recommended for attributes):
- Add `equipment_types` as a JSON list of canonical strings (from SDI `Equipment` values / `data/static/equipment_types.csv`).
  - Example: `["Cooling Condensing Unit"]`

Then publish safely (audit + optional promotion):
```bash
python3 scripts/actions.py workflow.improve \
  --input <labeled_sdi_style.csv> \
  --tag <tag> \
  --promote \
  --new-ruleset-id YYYY-MM-DD-your-ruleset-name
```

Example (serial, type-scoped): “Daikin‑McQuay condensing unit serial rule”
- Add a JSONL row with keys like: `brand`, `style_name`, `serial_regex`, `equipment_types`, `date_fields`, `example_serials`, `source_url`, `retrieved_on`.

Example (attribute, type-scoped): “Trane condensing unit model capacity token”
- Add a JSONL row with keys like: `brand`, `attribute_name`, `model_regex`, `equipment_types`, `value_extraction`, `examples`, `source_url`, `retrieved_on`.

### B) Transcribe chart-based mappings (overrides)
If documentation requires a chart/image mapping (month letters, etc.), use:
- `data/manual_overrides/serial_overrides.jsonl`
- `data/manual_overrides/attribute_overrides.jsonl`

Overrides are applied during ruleset validation/export and always win. See `docs/OVERRIDES.md`.

## Guidance rows vs decode rows (why “fixed” rules may still appear)
Rulesets can contain both:
- `rule_type=decode` rows (used by the decoder)
- `rule_type=guidance` rows (never used for decode; used for explainability + gap triage)

Because rulesets are created by *merging* multiple sources over time, it’s normal for older guidance rows
to remain present even after you add a deterministic decode rule for the same brand/style.

To keep rulesets readable, publish steps (`msl validate` and `phase3-promote`) apply a conservative cleanup:
- **Serial guidance suppression:** if a deterministic decode rule exists for `Style N` for a brand, guidance rows for that same `Style N` are removed.
- **Attribute guidance suppression:** brand-wide `chart_required` guidance rows with empty `model_regex`/`value_extraction` are removed once at least one decode rule exists for that brand+attribute.

## Decode only (unlabeled)
Decode an arbitrary asset export:

```bash
python3 scripts/actions.py decode.run \
  --input data/samples/sample_assets.csv \
  --tag sample
```

## Where “latest” is stored
- Current ruleset: `data/rules_normalized/CURRENT.txt` (folder name only)
- Latest run: `data/reports/CURRENT_RUN.txt` (run id)
- Latest baseline: `data/reports/CURRENT_BASELINE.txt` (run id)

## External sources (parse-only snapshots)
Some sources are richer than Building-Center pages and should be staged as **snapshots** first (no decoder/ruleset integration yet).

### HVACExport XML snapshot
Input: `data/static/hvacexport.xml`

Parse into a versioned snapshot folder (manual id):
```bash
python3 scripts/hvacexport_parse.py \
  --input data/static/hvacexport.xml \
  --snapshot-id 2026-01-24_v3.84
```

Outputs:
- `data/external_sources/hvacexport/<snapshot-id>/records.csv`
- `data/external_sources/hvacexport/<snapshot-id>/segments.csv`
- `data/external_sources/hvacexport/<snapshot-id>/options.csv`
- `data/external_sources/hvacexport/<snapshot-id>/metadata.json`
- `data/external_sources/hvacexport/<snapshot-id>/summary.md`

See:
- `docs/RULESETS.md`
- `docs/ARTIFACTS.md`
- `docs/ACTIONS.md`

### Spec sheet PDF snapshots
Spec sheets can contain model nomenclature/code breakdown tables (voltage, refrigerant, capacity codes, etc.).

Put raw PDFs in:
- `data/external_sources/specs/`

Extract embedded text into a versioned snapshot folder:
```bash
python3 scripts/actions.py specs.extract_text --tag specs
```

Outputs:
- `data/external_sources/specs_snapshots/<snapshot-id>/text/*.txt`
- `data/external_sources/specs_snapshots/<snapshot-id>/manifest.json`

Note: this step does not OCR scanned PDFs. If the extracted text is empty/garbled, the PDF likely needs OCR before mining.

#### Pilot: YORK/JCI XT Air Handler nomenclature
Mine deterministic model-coded attributes from the spec snapshot:
```bash
python3 scripts/actions.py specs.mine_york_ahu --snapshot-id <snapshot-id> --tag york-ahu
```

This writes candidates to:
- `data/rules_discovered/spec_sheets/<snapshot-id>/candidates/AttributeDecodeRule.candidates.jsonl`

Audit against SDI (where SDI has a comparable truth column):
```bash
python3 scripts/actions.py eval.candidates \
  --input data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv \
  --candidates-dir data/rules_discovered/spec_sheets/<snapshot-id>/candidates \
  --tag york-ahu
```

Promotion strategy (tiered):
- SDI-auditable attributes (e.g., `SupplyFanHP`) can be promoted after audit review.
- Spec-backed attributes with no SDI truth column (e.g., `ReturnFanHP`, `UnitEnvironment`, nominal dimensions) can still be promoted as additional attributes, but should be clearly labeled in `limitations` and reviewed for false positives (tight regex + equipment type scoping).

#### Mine all supported spec miners for a snapshot
Once you have multiple spec sheets in a snapshot, use:
```bash
python3 scripts/actions.py specs.mine_snapshot --snapshot-id <snapshot-id> --tag specs
```

Convenience script (extract → mine → audit):
```bash
./scripts/run_specs_snapshot_workflow.sh --snapshot-id <snapshot-id> --tag specs
```
