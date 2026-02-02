# Service Call Management — Inventory

Generated: 2026-01-22 EST

## PBIP contents
- PBIP: `Amend Reports/Service Call Management/Service Call Management.pbip`
- Report: `Amend Reports/Service Call Management/Service Call Management.Report`
- Semantic model: `Amend Reports/Service Call Management/Service Call Management.SemanticModel`

## Report pages (display names)
- Service Call Summary
- Profitability & Revenue
- Late Calls
- Costing
- Profit Analysis
- Data Review
- Duplicate of Data Review
- Labor Hours
- Late TT
- SumTT

## Model size (from TMDL)
- Tables: 81
- Columns: 1016
- Measures: 183

## Scope note (per request)
This report’s semantic model includes many job/contract/backlog tables and measure tables, but the **service-call logic** is implemented primarily in:
- `Service Call Measures` (measures)
- `*CALL DETAILS`, `*CALLS_F`, `*CALLS COSTS`, `*Calendar` (core service-call facts/date table)

## Artifacting / broken references (important)
- The report visuals reference a measure table named `Cash Flow Measures` in multiple visuals, but **no `Cash Flow Measures` table exists in the included semantic model TMDL**. Those visuals/measures should be treated as orphaned/broken until the model is reconciled.

