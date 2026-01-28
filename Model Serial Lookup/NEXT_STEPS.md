# NEXT_STEPS (<=10)

- Run `python3 scripts/actions.py workflow.improve --input data/equipment_exports/2026-01-25/sdi_equipment_2026_01_25.csv --tag sdi-baseline` and review `NEXT_TARGETS.md`.
- Decide a pinned “golden labeled dataset” path and add a no-regression gate (block promotion if it regresses year accuracy/coverage for top brands).
- Add an explicit `workflow.improve --promote` policy (when to use `--promote-all` vs audit-gated promotion).
- Make `ruleset.promote` write a short `PROMOTION_SUMMARY.md` (top added rules by brand + what was removed).
- Expand `eval.truth` deltas beyond year (capacity first, where labeled columns exist).
- Add a dry-run cleanup action for `data/rules_staged/*` and `data/rules_discovered/*` (no deletes by default).
- Move any remaining one-off utilities into `scripts/_archive/` (now the standard).
