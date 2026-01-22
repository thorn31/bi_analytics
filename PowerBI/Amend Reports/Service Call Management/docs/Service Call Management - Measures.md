# Service Call Management — Measures (Inventory)

Generated: 2026-01-22 EST

## High-signal note (per request)
This report contains many measure tables that look shared/copied from other models. The **service-call measures you care about** live in:
- `Service Call Measures` (36 measures)

## Artifacting / broken references
- Report visuals reference `Cash Flow Measures[...]`, but that table **does not exist** in `Service Call Management.SemanticModel/definition/tables/`. Those references should be treated as broken.

## Measure tables (as defined in the semantic model)
| Measure table | Measure count |
|---|---:|
| `Revenue Measures` | 42 |
| `Contract Measures` | 37 |
| `Service Call Measures` | 36 |
| `Cost Measures` | 18 |
| `Backlog Measures` | 17 |
| `Hour Measures` | 11 |
| `CONTRACTS MAPPING` | 6 |
| `CONTRACTS_D` | 5 |
| `BUDGET_F` | 3 |
| `*Calendar` | 2 |
| `*CALLS_F` | 2 |
| `JOBS_D` | 2 |
| `Refresh Date` | 1 |
| `CONTRACT_Hour_Breakout` | 1 |

## `Service Call Measures` (full list)

### Revenue proxy (billings)
- `Service Call Measures[Amount Billed] = sum('*CALL DETAILS'[BILLING_AMOUNT])`
- `Service Call Measures[Revenue FYTD_] = calculate([Amount Billed], '*Calendar'[Fiscal Year] = maxyear)`
- `Service Call Measures[Amount Billed FYTD] = calculate([Amount Billed], '*Calendar'[Fiscal Year] = maxyear)`
- `Service Call Measures[Average Amount Billed] = average('*CALL DETAILS'[BILLING_AMOUNT])` filtered to CLOSED calls

### Costs
- `Service Call Measures[Actual Costs] = sum('*CALLS COSTS'[Value])`
- `Service Call Measures[Cumulative Actual Costs]` = running total of `Actual Costs` to max selected `*Calendar[Date]` (blank if date > today)
- `Service Call Measures[Actual Costs FYTD]` = FYTD filter on `Actual Costs`

### Gross Profit (GP)
- `Service Call Measures[Actual GP$ _] = calculate([Amount Billed] - [Actual Costs], filter('*CALLS_F', '*CALLS_F'[STATUS_OF_CALL] = \"CLOSED\"))`
- `Service Call Measures[Actual GP%] = divide([Actual GP$ _], calculate([Amount Billed], filter('*CALLS_F', '*CALLS_F'[STATUS_OF_CALL] = \"CLOSED\")), blank())`
- FYTD / LY variants: `GP$ FYTD`, `GP% FYTD`, `GP$ FYTD LY`, `GP% FYTD LY`, plus display helper `GP$ graph max`.

### Operational / service-call KPIs
Includes call counts, late-call logic, days-open metrics, and “billings forward” measures.

## Measure usage by report visuals (what the report actually uses)
Entities referenced in visuals (measure bindings only):
- `Service Call Measures`: 111 references
- `Hour Measures`: 32 references
- `Contract Measures`: 6 references
- `Cost Measures`: 5 references
- `Revenue Measures`: 2 references (only `Change Order $` observed)
- `Cash Flow Measures`: 52 references (but missing from the semantic model)

For the per-page breakdown, see `Amend Reports/Service Call Management/docs/Service Call Management - Revenue Map.md`.

