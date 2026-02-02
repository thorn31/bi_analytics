# Mechanical Project Management — Revenue Map

Generated: 2026-01-22 14:55 EST

This maps report pages to the revenue definition(s) they use, based on measures referenced in `*.Report/definition/pages/**/visual.json`.

## Earned Revenue Source Tables
- Actual costs: `JOB_COST_DETAILS` (`DATA_WAREHOUSE.DW_CLEAN.JOB_COST_DETAILS` view)
- Forecasted costs: `JOB FORECAST` (`DATA_WAREHOUSE.DW_FINAL.JOB_COST_FORECASTS_F` table)
- Contract amount: `JOB` (`DATA_WAREHOUSE.DW_FINAL.JOBS_D` table) + change orders from `CHANGE_ORDERS_BY_MONTH` (`DATA_WAREHOUSE.DW_CLEAN.JOB_CHANGE_ORDERS` view)
- Date logic: `Calendar` (model-generated)

## Page mapping
| Page | Revenue definition(s) detected | Evidence (measures) |
|---|---|---|
| `Backlog` | Earned revenue (cost-based) | `Revenue Measures[Cumulative Rev Amount Across Jobs]` |
| `Backlog_Old` | GL revenue | `Backlog Measures[GL Revenue]` |
| `Forecasted Profitability` | Earned revenue (cost-based) | `Revenue Measures[Net Earned Rev Amount Across Jobs]` |
| `Job Profit Analysis` | Earned revenue (cost-based) | `Revenue Measures[Cumulative Revenue]` |
| `Over/Underbillings` | Earned revenue (cost-based), Billed/invoiced (vs earned) | `Revenue Measures[Cumulative Rev Amount Across Jobs]`, `Revenue Measures[Count Under Billed Jobs]`, `Revenue Measures[Cumulative Billed Amount]`, `Revenue Measures[Over - Under Billed]`, `Revenue Measures[Over / (Under) Billed Cumulative Across Jobs]` |
| `Revenue` | Earned revenue (cost-based) | `Revenue Measures[Net Earned Rev Amount Across Jobs]`, `Revenue Measures[Net Earned Rev Amount LM]`, `Revenue Measures[Net Earned Rev Amount TM]`, `Revenue Measures[Revenue LY YTD]`, `Revenue Measures[Revenue Rolling 12 PY]`, `Revenue Measures[Revenue Rolling 12]`, `Revenue Measures[Revenue YTD]` |

## Reference: earned revenue formula used in this report
From business definition / model implementation:
- Earned Revenue = (Actual Costs / Forecasted Costs) * Contract Amount
- Actual costs: `Cost Measures[Actual Cost]` = `sum(JOB_COST_DETAILS[COST_AMT])`
- Forecasted costs (as-of): `Cost Measures[Cumulative Forecast]` = `var maxdat = [Max Date]
return
ROUND(calculate([Cost Budget], filter(all('Calendar'), 'Calendar'[Date] <= maxdat)), 2)`
- Contract amount: `Revenue Measures[Current Contract Amount]` = `[Original Contract] + [Cumulative CO$]`
- Earned revenue (model): `Revenue Measures[Net Earned Revenue]` = `var compl = ROUND(divide('Cost Measures'[Actual Cost] , [Cumulative Forecast], blank()),4)
return
[Current Contract Amount] * compl`
