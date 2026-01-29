# STATUS — Model/Serial Lookup (Action-Driven Snapshot)

Last updated: 2026-01-29

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

## Recent changes
- Equipment type context is now supported at decode-time (uses input `Equipment` / `EquipmentType` when present) and is reflected in reports.
- Rulesets may include optional `equipment_types` scoping columns in `SerialDecodeRule.csv` / `AttributeDecodeRule.csv` (missing/empty means cross-type).
- Truth and candidate audits now emit additional by-type artifacts (see `docs/REPORTS.md`).

## Reference docs
- `docs/WORKFLOW.md`
- `docs/ACTIONS.md`
- `docs/RULESETS.md`
- `docs/OVERRIDES.md`
- `docs/ARTIFACTS.md`
