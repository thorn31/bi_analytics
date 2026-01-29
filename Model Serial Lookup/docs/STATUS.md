# STATUS — Model/Serial Lookup (Action-Driven Snapshot)

Last updated: 2026-01-28

## Current pointers
- Ruleset (CURRENT): `data/rules_normalized/$(cat data/rules_normalized/CURRENT.txt)`
- Latest run: `data/reports/$(cat data/reports/CURRENT_RUN.txt)` (when present)
- Latest baseline: `data/reports/$(cat data/reports/CURRENT_BASELINE.txt)` (when present)

## Recommended entry point
```bash
python3 scripts/actions.py workflow.improve \
  --input data/equipment_exports/2026-01-25/sdi_equipment_2026_01_25.csv \
  --tag sdi-smoke
```

## Known issues (current checkout)
- None

## Reference docs
- `docs/WORKFLOW.md`
- `docs/ACTIONS.md`
- `docs/RULESETS.md`
- `docs/OVERRIDES.md`
- `docs/ARTIFACTS.md`

