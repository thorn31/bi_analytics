# Service Call Management — Revenue / GP Map (by Page)

Generated: 2026-01-22 EST

This map shows which pages actually use the service-call revenue/GP measures (based on report visual bindings).

## Revenue + GP measures of interest (Service Calls)
- Revenue proxy: `Service Call Measures[Amount Billed]` and FYTD variants (`Revenue FYTD_`, `Amount Billed FYTD`)
- Costs: `Service Call Measures[Actual Costs]`
- GP: `Service Call Measures[Actual GP$ _]`, `Service Call Measures[Actual GP%]` and FYTD variants (`GP$ FYTD`, `GP% FYTD`)

## Profitability & Revenue
Measure tables used: `CONTRACTS MAPPING`, `Service Call Measures`, plus broken/orphaned references to `Cash Flow Measures` in some visuals.

Top `Service Call Measures` used:
- `Actual GP$ _`
- `GP$ FYTD`
- `Actual GP%`
- `Amount Billed`
- `Actual Costs`
- `Billings Forward_Created Date`

## Service Call Summary
Measure tables used: `Service Call Measures`, `Contract Measures`, `Refresh Date`, plus broken/orphaned references to `Cash Flow Measures` in some visuals.

Top `Service Call Measures` used:
- `Number of Calls FYTD`
- `Average Amount Billed FYTD`
- `GP$ FYTD`
- `GP% FYTD`
- `Revenue FYTD_`
- `Billings Forward_Created Date`

## Profit Analysis
Measure tables used: `Service Call Measures`, `Contract Measures`, `*Calendar`, plus broken/orphaned references to `Cash Flow Measures` in some visuals.

Top `Service Call Measures` used:
- `GP$ FYTD`
- `GP% FYTD`
- `Amount Billed`
- `Amount Billed FYTD`
- `Actual Costs FYTD`

## Costing
Top `Service Call Measures` used:
- `Actual Costs` (and type-specific variants)

## Late Calls
Top `Service Call Measures` used:
- `Late Open Calls` (and created-date variant)
- `Average Days Open` (FYTD / LY variants)

## Duplicate of Data Review
This page includes a small number of bindings to `Service Call Measures` and also one observed `Revenue Measures[Change Order $]` binding; it does not appear to be part of the core service-call revenue definition.

## Data Review / Labor Hours / Late TT / SumTT
These pages do not materially define revenue/GP; they focus on operational and labor-hour views (and may include broken/orphaned measure references).

