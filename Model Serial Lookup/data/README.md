# data/

This folder contains **inputs**, **cached source corpus**, and **generated artifacts**.

## What you should edit
- `data/manual_overrides/`: curated overrides that the pipeline applies during `msl validate`.
- `data/rules_discovered/manual_additions/`: “candidate” rules discovered from real assets and promoted into a ruleset.
- `data/rules_normalized/CURRENT*.txt`: pointers to the current “blessed” rulesets/reports.

## What is generated (don’t hand-edit)
- `data/rules_staged/`: intermediate JSONL rules from normalization.
- `data/rules_normalized/<run-id>/`: exported CSV rulesets (versioned).
- `data/reports/<run-id>/`: baseline/audit reports (versioned).

## What is large/cache-only (often gitignored)
- `data/raw_html/`, `data/raw_images/`, `data/ocr_text/`, `data/logs*`: reproducible caches.

## Pointers
- Current recommended ruleset: `data/rules_normalized/CURRENT.txt`
- Current Phase 1 ruleset: `data/rules_normalized/CURRENT_PHASE1.txt`
- Current baseline report: `data/reports/CURRENT_BASELINE.txt`
