# OVERRIDES — Precedence and Schemas

Overrides exist to keep the system deterministic when source documentation is incomplete or chart-based.

Rule: **Overrides always win**.

## Override sources
Primary override inputs:
- `data/manual_overrides/serial_overrides.jsonl`
- `data/manual_overrides/attribute_overrides.jsonl`

Post-promotion fix registry (currently implemented as a script):
- `scripts/apply_manual_serial_fixes.py`

Manual candidate additions (promoted rules):
- `data/rules_discovered/manual_additions/`
  - These are treated as **always-on** for promotions by the wrapper unless `--no-manual-additions` is passed.

## Precedence (highest to lowest)
1. Manual overrides in `data/manual_overrides/*` (applied during ruleset validation/export)
2. Post-promotion fix registry (applied immediately after promotion to ensure persistence)
3. Promoted manual additions (`data/rules_discovered/manual_additions/`) when promotion occurs
4. Normalized rules derived from extracted source text

## `serial_overrides.jsonl` schema (record stream)
Each line is a JSON object. Minimum keys:
- `brand` (string)
- `style_name` (string)
- `field` (one of: `year|month|week|day`)

Optional keys (at least one required to make a change):
- `mapping` (object)
- `positions` (object with `start`/`end`)
- `pattern` (object with `regex` and optional `group`)
- `transform` (object)

## `attribute_overrides.jsonl` schema (record stream)
Each line is a JSON object in `AttributeDecodeRule`-like shape. Minimum keys:
- `rule_type` (usually `decode`)
- `brand`
- `attribute_name`
- `value_extraction` (dict; must include `positions` or `pattern`)
- `source_url`
- `retrieved_on`

## Operational note
Promotion should always be followed by:
- applying post-promotion fixes
- re-validating the new ruleset
- re-running truth evaluation on the baseline dataset to confirm no regressions
