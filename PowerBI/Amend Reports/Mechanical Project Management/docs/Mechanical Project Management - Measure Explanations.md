# Mechanical Project Management — Measure Explanations (How/Why)

Generated: 2026-01-22 14:55 EST

This document explains the intent and mechanics of the key measure families, focusing on revenue and the cost measures that drive it.

## Revenue: multiple definitions
### A) Earned revenue (job-level, cost-based percent complete)

#### Earned revenue — data lineage (sources)
- Actual costs (`Cost Measures[Actual Cost]`): model table `JOB_COST_DETAILS` → `DATA_WAREHOUSE.DW_CLEAN.JOB_COST_DETAILS` (View)
- Forecasted costs (`Cost Measures[Cumulative Forecast]`): model table `JOB FORECAST` → `DATA_WAREHOUSE.DW_FINAL.JOB_COST_FORECASTS_F` (Table)
- Contract amount (`Revenue Measures[Current Contract Amount]`): model table `JOB` → `DATA_WAREHOUSE.DW_FINAL.JOBS_D` (Table)
- Change orders (rolled into contract): model table `CHANGE_ORDERS_BY_MONTH` → `DATA_WAREHOUSE.DW_CLEAN.JOB_CHANGE_ORDERS` (View)
- As-of date for cumulative calcs: model table `Calendar` (model-generated date table; not sourced from Snowflake)
Revenue on the `Revenue` page is earned at the job level based on costs incurred multiplied by contract amount. It is not pulled from the General Ledger.

Formula (as implemented in this model):
- Earned Revenue = (Actual Costs / Forecasted Costs) * Contract Amount

Implementation notes:
- `Cost Measures[% Complete]` caps at 1.0: `if(Divide([Cumulative Actual Cost], [Cumulative Forecast], blank()) > 1, 1, Divide([Cumulative Actual Cost], [Cumulative Forecast], blank()))`
- `Revenue Measures[Net Earned Revenue]` uses `Actual Cost / Cumulative Forecast` and multiplies by contract: `var compl = ROUND(divide('Cost Measures'[Actual Cost] , [Cumulative Forecast], blank()),4)
return
[Current Contract Amount] * compl`
- Many visuals intentionally aggregate earned revenue job-by-job using `SUMX(SUMMARIZE(JOB, JOB[JOB_NUMBER], ...))` to enforce job grain and avoid double-counting.

### B) GL revenue (general ledger postings)
Some pages (notably Backlog/Backlog_Old) include GL-based revenue and costs from the `GL POSTING` fact table.

Key GL measures:
- `Backlog Measures[GL Revenue]`: `calculate([Amount], filter('GL POSTING', 'GL POSTING'[ACCOUNT_TYPE] = "REVENUE"))* -1`
- `Cost Measures[GL Cost of Revenue]`: `calculate(sum('GL POSTING'[DEBITAMT]), filter('GL POSTING', 'GL POSTING'[ACTNUMBR_1] = "340"))`

### C) Billed / invoiced amounts (AR / invoices)
Over/Under-billing is based on invoice amounts compared to earned revenue.

- `Revenue Measures[Cumulative Billed Amount]`: `var maxdat = [Max Date]
return
calculate(sum(INVOICES[ACCOUNT_AMOUNT]), filter(all('Calendar'), 'Calendar'[Date] <= maxdat))`
- `Revenue Measures[Over - Under Billed]`: `[Cumulative Billed Amount] - [Cumulative Revenue]`

## Gross Profit (GP)
### A) Earned GP (job/project, cost-based)
This follows the same “earned revenue” logic and uses cost-based percent complete.

- `Revenue Measures[Actual GP$] = (Current Contract Amount * % Complete) - Actual Cost`
- `Revenue Measures[Forecasted GP $] = Current Contract Amount - Cumulative Forecast`
- `Revenue Measures[Estimated GP $] = Current Contract Amount - Original Cost Estimate`
- Percent versions divide by contract: `Forecasted GP%`, `Estimated GP%`.

**GP — data lineage (sources)** (same base inputs as earned revenue):
- Contract amount: `JOB` (+ change orders `CHANGE_ORDERS_BY_MONTH`)
- Actual costs: `JOB_COST_DETAILS`
- Forecasted costs: `JOB FORECAST` (via `Cost Measures[Cost Budget]` → `Cost Measures[Cumulative Forecast]`)
- Date context for cumulative calcs: `Calendar` / `Calendar[Max Date]`

### B) GL GP (ledger-based, backlog)
This GP is derived directly from GL postings (not from earned/forecast costs).

- `Backlog Measures[Actual GP] = GL Revenue - GL costs` (Equipment/Material, Labor, Subcontract, Ops Expense, Vehicle, Discounts)

**GP — data lineage (sources)**:
- GL revenue and GL cost components come from `GL POSTING` (Snowflake `POSTING_DATA_F`) and are filtered by `ACCOUNT_TYPE` (and specific account segment values in some measures).

## Core building blocks (what other measures depend on)
### Calendar “as-of” date
- `Calendar[Max Date]`: `max('Calendar'[Date])`
A lot of “cumulative” measures use `Max Date` to define the as-of point for running totals.

### Costs (Cost Measures table)
- `Cost Measures[Actual Cost]`: `sum(JOB_COST_DETAILS[COST_AMT])`
- `Cost Measures[Cost Budget]`: `sum('JOB FORECAST'[FORECAST_COSTS])`
- `Cost Measures[Cumulative Forecast]`: `var maxdat = [Max Date]
return
ROUND(calculate([Cost Budget], filter(all('Calendar'), 'Calendar'[Date] <= maxdat)), 2)`
- `Cost Measures[Cumulative Actual Cost]`: `var maxdat = [Max Date]
return
calculate([Actual Cost], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))`
- `Cost Measures[% Complete]`: `if(Divide([Cumulative Actual Cost], [Cumulative Forecast], blank()) > 1, 1, Divide([Cumulative Actual Cost], [Cumulative Forecast], blank()))`
- `Cost Measures[Available Budget]`: `[Cumulative Forecast] - [Cumulative Actual Cost] 
//- [Committed Cost]`
- `Cost Measures[Committed Cost]`: `sum(JOB_COST_SUMMARY[COMMITTED_COST])`
- `Cost Measures[Original Cost Estimate]`: `sum(JOB_COST_SUMMARY[REVISED_ESTIMATED_COST])`

Key semantics:
- `Actual Cost` comes from `JOB_COST_DETAILS[COST_AMT]`.
- `Forecasted Costs` in the earned revenue formula is represented by `Cost Budget` and its running total `Cumulative Forecast` (as-of `Max Date`).
- `% Complete` is `Cumulative Actual Cost / Cumulative Forecast`, capped at 1.0.

### Contract amounts (Revenue Measures table)
- `Revenue Measures[Original Contract]`: `sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[ORIG_CONTRACT_AMOUNT]), JOB[ORIG_CONTRACT_AMOUNT])`
- `Revenue Measures[Change Order $]`: `sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "CO", sum(CHANGE_ORDERS_BY_MONTH[CHANGE_ORDER_EST_COST])), [CO])`
- `Revenue Measures[Cumulative CO$]`: `var maxdat = [Max Date]
return
calculate([Change Order $], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))`
- `Revenue Measures[Current Contract Amount]`: `[Original Contract] + [Cumulative CO$]`

## Earned revenue measure chain (recommended reading order)
| Step | Measure | Notes |
|---:|---|---|
| 1 | `Cost Measures[Actual Cost]` |  |
| 2 | `Cost Measures[Cost Budget]` |  |
| 3 | `Calendar[Max Date]` |  |
| 4 | `Cost Measures[Cumulative Forecast]` | Running total as-of `Max Date`. |
| 5 | `Cost Measures[Cumulative Actual Cost]` | Running total as-of `Max Date`. |
| 6 | `Cost Measures[% Complete]` | Capped at 1.0. |
| 7 | `Revenue Measures[Original Contract]` |  |
| 8 | `Revenue Measures[Cumulative CO$]` | Running total as-of `Max Date`. |
| 9 | `Revenue Measures[Current Contract Amount]` |  |
| 10 | `Revenue Measures[Cumulative Revenue]` | Min(contract, contract × % complete) pattern. |
| 11 | `Revenue Measures[Net Earned Revenue]` | Earned revenue formula (cost ratio × contract). |
| 12 | `Revenue Measures[Net Earned Rev Amount Across Jobs]` | Aggregated job-by-job via SUMX(SUMMARIZE(JOB…)). |
| 13 | `Revenue Measures[Revenue YTD]` |  |
| 14 | `Revenue Measures[Revenue LY YTD]` |  |
| 15 | `Revenue Measures[Revenue Rolling 12]` |  |
| 16 | `Revenue Measures[Revenue Rolling 12 PY]` |  |

## Notes / gotchas to validate with the business
- Some visuals reference `Revenue Measures.Earned Revenue TY/LY` in report metadata, but those names appear to be aliases for `Revenue YTD` and `Revenue LY YTD` rather than actual semantic model measures.
- `Revenue YTD` / `Revenue LY YTD` use Fiscal Year logic (not a strict date-to-date SAMEPERIODLASTYEAR pattern).
