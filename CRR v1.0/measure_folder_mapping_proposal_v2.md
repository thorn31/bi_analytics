# Measure Folder Mapping Proposal - V2

## Locked Decisions
- `8. UI`, `9. Deprecated`, and `10. Not Implemented` are the final top-level order for those sections.
- Domain-specific labels stay with their domain metrics.
- Keep `6. Customer Status\UI` naming as-is.
- Move items to where they belong, even if churn is higher.

## Target Numbering (Single Domain Per Number)
1. `1. GL Financials`
2. `2. Customer Financials`
3. `3. Retention (Service Contracts)`
4. `4. Customer Metrics`
5. `5. Customer Experience`
6. `6. Customer Status`
7. `7. Helper`
8. `8. UI`
9. `9. Deprecated`
10. `10. Not Implemented`

## Core Rules
1. One number = one domain only.
2. No duplicate numeric prefixes inside nested folder names.
3. Maximum folder depth = 4 levels.
4. All helper logic goes in `7.*`.
5. UI-only artifacts go in `8.*`.
6. All retention business logic is consolidated into `3.*`.

## Target Folder Shape
- `1. GL Financials\Revenue|Cost|Gross Profit|P&L`
- `2. Customer Financials\Revenue|Cost|Gross Profit`
- `3. Retention (Service Contracts)\R12M As Of\Base|Components|KPIs|Logo|Waterfall|Classification`
- `4. Customer Metrics\Profile|Rank|Active Items`
- `5. Customer Experience\NPS|Service Quality`
- `6. Customer Status\UI|Lifecycle|Contract|Projects`
- `7. Helper\Date|Retention|GL|P&L|UI Active Items|Conditional Formatting (numeric helper measures)`
- `8. UI\Sparklines|Conditional Formatting (color/text outputs)|Documentation|Cross-Domain Display`

## Where Key Existing Areas Move
- `4. Time Intelligence\4.1 R12M As Of\Revenue\*`
  -> `2. Customer Financials\Revenue\Time Intelligence\R12M As Of\*`

- `5. Retention\5.4 R12M As Of\5.4.0 Documentation`
  -> `8. UI\Documentation\Retention`

- `5. Retention\5.4 R12M As Of\5.4.7 Sparklines`
  -> `8. UI\Sparklines\Retention`

- `5. UI\5.1 Customer Financials*`
  -> Domain labels under `2. Customer Financials\...\Labels`

- `5. UI\Customer Metrics`
  -> `4. Customer Metrics\Rank\Labels`

- `5. UI\GL Financials`
  -> `1. GL Financials\Revenue\Variance\Labels` and `1. GL Financials\Gross Profit\Variance\Labels`

- `7. Helper\7.4 UI\Conditional Formatting`
  -> Split:
  - Color/text outputs -> `8. UI\Conditional Formatting`
  - Numeric delta helpers -> `7. Helper\Conditional Formatting`

## Execution Plan
1. Move full-folder groups first (no splits).
2. Apply split-folder measure moves (labels/text/SVG/colors vs numeric logic).
3. Normalize folder names to remove duplicate numbering segments.
4. Validate report visuals after each domain batch.

## Validation Checklist
- No business logic measure remains in `8. UI`.
- No UI-only measure remains in domain folders unless explicitly domain label.
- No helper measure remains outside `7.*`.
- All retention business logic exists only in `3.*`.
- `9.*` and `10.*` remain isolated.

## Next Deliverable
- Build a measure-by-measure V2 mapping table for all 238 measures:
  - `Measure`
  - `Current Folder`
  - `Proposed Folder`
  - `Reason`
