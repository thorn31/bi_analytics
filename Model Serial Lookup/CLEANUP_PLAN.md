# CLEANUP_PLAN — Action-Driven Workflow Refactor

This repo is operated via standardized actions with one canonical entry point: `scripts/actions.py`.

Canonical docs:
- `docs/WORKFLOW.md`
- `docs/ACTIONS.md`
- `docs/RULESETS.md`
- `docs/OVERRIDES.md`
- `docs/ARTIFACTS.md`

## Inventory (canonical decisions)
| Path | Category | Keep / Archive |
|---|---|---|
| `scripts/actions.py` | UTIL (operator) | KEEP (canonical entry point) |
| `msl/decoder/` | ENGINE | KEEP |
| `msl/pipeline/*` | RULESET/EVAL/MINING | KEEP (canonical implementations) |
| `scripts/apply_manual_serial_fixes.py` | RULESET (post-promote fix) | KEEP (until integrated) |
| `scripts/_archive/2026-01-28/*` | UTIL | ARCHIVED (one-off Trane/SDI utilities) |
| `data/_archive/analysis_trane_2026-01-27/*` | UTIL scratch | ARCHIVED (Trane investigation artifacts) |
| `docs/_archive/*` | docs history | KEEP (archived) |

## Pointer contracts (canonical)
- Current ruleset id: `data/rules_normalized/CURRENT.txt` (folder name only)
- Latest run id: `data/reports/CURRENT_RUN.txt`
- Latest baseline id: `data/reports/CURRENT_BASELINE.txt`

## Output standards (canonical)
- CSV: tables
- JSONL: record streams
- JSON: small metadata and summaries
- Markdown: human reports

## Migration checklist (repo state)
- Update CURRENT pointer contract to folder name only (done: `data/rules_normalized/CURRENT.txt`, `msl/pipeline/ruleset_manager.py`).
- Add action wrapper CLI (done: `scripts/actions.py`).
- Track “latest” pointers in `data/reports/` and allowlist them in `.gitignore` (done).
- Refactor docs to action-driven set and move stale docs to `docs/_archive/` (done).
- Archive one-off utilities (done):
  - `scripts/*trane*`, `scripts/debug_*`, `scripts/normalize_sdi.py` → `scripts/_archive/2026-01-28/`
  - `data/analysis/*` → `data/_archive/analysis_trane_2026-01-27/`
