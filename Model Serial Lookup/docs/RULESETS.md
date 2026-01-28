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

## Immutability and updates
- Do not edit an existing ruleset folder.
- Fixes and improvements create a **new** `data/rules_normalized/<ruleset-id>/` folder.
- Producer operations update `CURRENT.txt` to the new folder name by default.

## Validation expectations
- Serial decode rows must include example values that match the regex.
- Candidate promotions are hard-gated: malformed candidate rows block promotion.

