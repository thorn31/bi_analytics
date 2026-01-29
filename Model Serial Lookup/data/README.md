# data/

This folder contains **inputs**, **cached source corpus**, and **generated artifacts**.

## What you should edit
- `data/manual_overrides/`: curated overrides that the pipeline applies during `msl validate`.
- `data/rules_discovered/manual_additions/`: “candidate” rules discovered from real assets and promoted into a ruleset.
- `data/rules_normalized/CURRENT.txt`: pointer to the current “blessed” ruleset (folder name only).
- `data/reports/CURRENT_RUN.txt`: pointer to the latest workflow run id (written by `scripts/actions.py`).
- `data/reports/CURRENT_BASELINE.txt`: pointer to the latest baseline run id (written by `scripts/actions.py`).

## What is generated (don’t hand-edit)
- `data/rules_staged/`: intermediate JSONL rules from normalization.
- `data/rules_normalized/<run-id>/`: exported CSV rulesets (versioned).
- `data/reports/<run-id>/`: baseline/audit reports (versioned).

## What is large/cache-only (often gitignored)
- `data/raw_html/`, `data/raw_images/`, `data/ocr_text/`, `data/logs*`: reproducible caches.

## Pointers
- Current recommended ruleset: `data/rules_normalized/CURRENT.txt` (folder name only)
- Current baseline report run id: `data/reports/CURRENT_BASELINE.txt`
