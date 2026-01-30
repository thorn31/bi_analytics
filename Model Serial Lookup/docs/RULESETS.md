# RULESETS — Contract and “Current”

Rulesets are **versioned** and treated as **immutable** once published.

## Where rulesets live
- `data/rules_normalized/<ruleset-id>/`

## CURRENT pointer (canonical)
- `data/rules_normalized/CURRENT.txt` contains **ONLY the folder name**:
  - Example: `2026-01-27-trane-fix-v3`

Resolution:
- `ruleset_dir = data/rules_normalized/$(cat CURRENT.txt)`

## Ruleset folder contents (v1)
Required:
- `SerialDecodeRule.csv`

Optional:
- `AttributeDecodeRule.csv`
- `BrandNormalizeRule.csv`

## Optional equipment type scoping
Both `SerialDecodeRule.csv` and `AttributeDecodeRule.csv` may include an optional column:
- `equipment_types`: JSON list of canonical equipment type strings (example: `["Cooling Condensing Unit"]`)

Semantics:
- Missing/empty/invalid → treat as `[]` meaning “applies to all equipment types”.
- Non-empty list → rule is eligible only when the input row’s `Equipment`/`EquipmentType` matches one of the listed types.

## Immutability and updates
- Do not edit an existing ruleset folder.
- Fixes and improvements create a **new** `data/rules_normalized/<ruleset-id>/` folder.
- Producer operations update `CURRENT.txt` to the new folder name by default.

## Validation expectations
- Serial decode rows must include example values that match the regex.
- Candidate promotions are hard-gated: malformed candidate rows block promotion.

## Cleanup at publish time
When a ruleset is published (either via `msl validate` from `data/rules_staged/...` or via `phase3-promote`),
we apply conservative cleanup so `rules_normalized/*.csv` stays readable:
- Guidance rows that are clearly superseded by deterministic decode rules are dropped.
- This does not change decoder behavior (decoder never uses guidance rows for decoding).
