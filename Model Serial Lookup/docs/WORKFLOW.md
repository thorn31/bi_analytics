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

See:
- `docs/RULESETS.md`
- `docs/ARTIFACTS.md`
- `docs/ACTIONS.md`

