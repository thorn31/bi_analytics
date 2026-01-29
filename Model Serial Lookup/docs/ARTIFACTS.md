# ARTIFACTS — Where Outputs Live

This repo writes outputs under `data/` with a small number of tracked pointer files so “latest” is obvious.

## Canonical output root
- `data/reports/<run-id>/`

The contents of `data/reports/` are mostly gitignored. Tracked pointers:
- `data/reports/CURRENT_RUN.txt` → latest wrapper run id
- `data/reports/CURRENT_BASELINE.txt` → latest baseline run id

## Candidates
- `data/rules_discovered/<run-id>/candidates/`

## Rulesets (published, versioned)
- `data/rules_normalized/<ruleset-id>/`
- `data/rules_normalized/CURRENT.txt` (folder name only)

## Intermediate artifacts
- `data/page_index/<run>/page_index.csv`
- `data/extracted_sections/<run>/extracted_sections.jsonl`
- `data/rules_staged/<run>/*.jsonl`

