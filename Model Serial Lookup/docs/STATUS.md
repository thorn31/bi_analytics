# STATUS — Model/Serial Lookup (Action-Driven Snapshot)

Last updated: 2026-01-30

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
- Added a parse-only snapshot tool for `data/static/hvacexport.xml` (staged under `data/external_sources/hvacexport/<snapshot-id>/`, no integration yet).
- Promoted ruleset `data/rules_normalized/2026-01-30-promoted21-magicaire/` (adds Magic Aire serial styles: Style 2 `YYMM...` (<=1999) and Style 3 `YY-####` (1970s); retains BENCHMARK + AERCO + Trane legacy coverage improvements + EMI + Snyder General + ClimateMaster + McQuay/York/Greenheck/Friedrich fixes + cleanup + earlier promotions).
- Decoder now rejects impossible month/week values (prevents false matches like month=48 from being emitted).

## Reference docs
- `docs/WORKFLOW.md`
- `docs/ACTIONS.md`
- `docs/RULESETS.md`
- `docs/OVERRIDES.md`
- `docs/ARTIFACTS.md`
