---
name: spec-sheet-attribute-mining
description: Extract HVAC model-number attribute rules from spec sheet PDFs (data/external_sources/specs) into AttributeDecodeRule candidates, audit vs SDI normalized exports, and promote into rulesets.
metadata:
  short-description: Mine spec sheet PDFs into attribute rules
---

# Spec Sheet Attribute Mining (PDF → AttributeDecodeRule)

This skill captures the repo workflow for turning **spec sheet/nomenclature PDFs** into **model-number attribute decode candidates** that can be audited against SDI exports and promoted into versioned rulesets.

## Where to put new knowledge

- **Add PDFs (source of truth):** `data/external_sources/specs/`
- **Snapshot + extracted text (immutable run input):** `data/external_sources/specs_snapshots/<snapshot-id>/`
- **Discovered candidates (review/promote):** `data/rules_discovered/spec_sheets/<snapshot-id>/candidates/AttributeDecodeRule.candidates.jsonl`

## Quickstart (recommended)

1) Add one or more PDFs to `data/external_sources/specs/`.
2) Create a new snapshot folder under `data/external_sources/specs_snapshots/<snapshot-id>/` (copy PDFs + write `manifest.json`).
   - If unsure, follow `docs/WORKFLOW.md` → “Spec sheets”.
3) Extract embedded PDF text into the snapshot:
   - `python3 scripts/actions.py specs.extract_text --snapshot-id <snapshot-id>`
4) Mine the snapshot to produce `AttributeDecodeRule` candidates:
   - `python3 scripts/actions.py specs.mine_snapshot --snapshot-id <snapshot-id>`
5) Audit candidates vs SDI normalized export (when an SDI “truth” column exists for that attribute):
   - `python3 scripts/actions.py eval.candidates --candidates-dir data/rules_discovered/spec_sheets/<snapshot-id>/candidates --sdi-path data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv`
6) Promote reviewed candidates into a new versioned ruleset:
   - `python3 scripts/actions.py ruleset.promote --candidates-dir data/rules_discovered/spec_sheets/<snapshot-id>/candidates --new-ruleset-id <id>`

## Expanding what we extract (new fields)

When a PDF includes additional nomenclature fields that map cleanly to SDI (or to a new canonical field we want), prefer extracting **more** rather than less—*as long as we can do it deterministically and scope it tightly*.

Rule of thumb:

- If you can express it as: “for this model pattern, substring X maps to canonical value Y”, extract it.
- If SDI has a corresponding truth column, wire it into the audit step for that attribute.
- If SDI doesn’t have truth, still emit it, but mark it clearly as spec-backed (so it’s reviewable and doesn’t get mistaken for SDI-validated truth).

## How to add a new “miner” (new PDF / new unit type)

Miners live in `scripts/specs_mine_snapshot.py`.

Workflow:

1) Add a new function (pattern: `_mine_<brand>_<family>()`) that:
   - Reads from the snapshot manifest + extracted text
   - Outputs a list of `AttributeDecodeRule` candidate dicts
2) Scope aggressively:
   - Narrow `brand` (and `brand_family` if available)
   - Add `equipment_types` when known
   - Use a model regex that matches the nomenclature structure you extracted
3) For each mined attribute:
   - Emit canonical attribute names (e.g., `VoltageVoltPhaseHz`, `NominalCapacityTons`, `SupplyFanHP`, `ReturnFanHP`, `UnitEnvironment`)
   - Normalize values to repo canonical formats (e.g., voltage `480-3-60`)
   - Include `evidence_excerpt` (short), `source_path`, and at least one `example_models`
4) Add a focused unit test under `tests/` that:
   - Skips if the snapshot isn’t present
   - Validates that the expected candidate(s) exist (brand, attribute, regex, mapping keys)

## Canonical values and “truth” tiers

- Spec sheets are treated as **high-trust** sources, but promotion is still gated by:
  - Audit vs SDI truth columns when available (Tier A).
  - Clear limitation metadata when SDI has no truth column for that attribute (Tier B).

## Notes / limitations

- This pipeline currently relies on **embedded PDF text** via `pypdf`.
  - If a PDF is scanned (no embedded text), add OCR as a separate enhancement (don’t invent values).

## Reference docs

- `docs/WORKFLOW.md` (end-to-end spec sheet workflow)
- `docs/ACTIONS.md` (CLI entrypoints)
- `docs/ARTIFACTS.md` (where outputs live)
