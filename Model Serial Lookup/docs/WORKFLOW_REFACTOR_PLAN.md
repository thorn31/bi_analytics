# WORKFLOW REFACTOR PLAN (Saved)

This document captures the agreed implementation plan for the action-driven workflow refactor.

## Goals
- Fewer entry points; one canonical wrapper CLI (`scripts/actions.py`).
- Deterministic operation: no guessing; all improvements are explicit rules with evidence.
- Versioned immutable rulesets; “latest” is obvious via pointer files.
- Standardized artifacts and a single consolidated workflow run report.

## Locked decisions
- `data/rules_normalized/CURRENT.txt` contains **only** the ruleset folder name.
- Canonical output root for runs is `data/reports/` with tracked pointer files:
  - `data/reports/CURRENT_RUN.txt`
  - `data/reports/CURRENT_BASELINE.txt`
- Remove “phase” terminology from docs and confusing code comments; archive stale docs to `docs/_archive/`.
- Output standards: CSV (tables), JSONL (streams), JSON (small metadata), Markdown (human reports).
- Promotion is hard-gated: invalid candidate rows block promotion.

## Canonical actions
See `docs/ACTIONS.md` for the full contracts and command examples.

