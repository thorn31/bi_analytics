# Contract Management — Measure Explanations (How/Why)

Generated: 2026-01-22 15:10 EST

This model contains two main revenue concepts:
- Contract revenue recognized (service contract-style) in `Contract Measures` driven by contract term + billing/calls costs.
- A set of job/project-style measures exist under `Revenue Measures`, but they reference missing model tables (e.g. `JOBS_D`) and appear to be copied/orphaned (not used by visuals).

## Revenue definitions
### A) Orphaned job/project revenue measures (not active in this report)
The semantic model contains a `Revenue Measures` table, but those measures reference model tables that do not exist in this dataset (for example `JOBS_D`, `JOB_COST_DETAILS_F`, `JOB_COST_FORECASTS_F`, `INVOICES_F`). They also do not appear as `queryRef` bindings in report visuals (only as some `metadata` strings), so they should be treated as copied/orphaned rather than the actual revenue logic used by this report.

### B) Contract revenue recognized (schedule-based)

**Billings are not treated as revenue in this report.**
- Revenue is the schedule-based recognized revenue (see `Contract Measures[Total Revenue Recognized]` / `Contract Measures[Total Revenue Recognized Across Jobs]`).
- Billings are used only for variance: `Contract Measures[Over-Under Billed] = Contract Measures[Amount Billed] - Contract Measures[Total Revenue Recognized Across Jobs]`.
This model also calculates recognized revenue across contract periods (month-based allocation) and compares that to billed amounts.

- `Contract Measures[Contract Amount]`: `calculate(sum(CONTRACTS_D[ANNUAL_CONTRACT_VALUE]), CONTRACTS_D[Current Contract Flag] = 1)`
- `Contract Measures[Monthly Recognzied Revenue]`: `Divide([Contract Amount] , datediff(max(CONTRACTS_D[CONTRACT_START_DATE]), max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), MONTH)+1, blank())`
- `Contract Measures[Number of months since start]`: `//minx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "start", calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract]))), (Datediff([start], calculate(max('Calendar'[Date]),  'Calendar'[Date] <= today()), MONTH) ))
var mx = max('Calendar'[Date])
var mn = min('Calendar'[Date])
return
maxx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "start_", calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract])), "end_", calculate(max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract]))), if([start_] >= mx, blank(), (Datediff([start_], mx, MONTH)+1)))`
- `Contract Measures[Total Revenue Recognized]`: `//[Monthly Recognzied Revenue] * (Datediff(max(CONTRACTS_D[CONTRACT_START_DATE]), calculate(max('Calendar'[Date]), 'Calendar'[Date] <= today()), MONTH) )
[Number of months since start] * [Monthly Recognzied Revenue]`
- `Contract Measures[Total Revenue Recognized Across Jobs]`: `var mx = max('Calendar'[Date])
var mn = min('Calendar'[Date])
return
sumx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], 
"amount", [Contract Amount], 
"rev", [Monthly Recognzied Revenue],
"xxx", Divide([Contract Amount] , datediff(max(CONTRACTS_D[CONTRACT_START_DATE]), max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), MONTH), blank()), 
"start_", calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract])), 
"months_", if(calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract])) >= max('Calendar'[Date]), blank(), (Datediff(calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract])), mx, MONTH))),
"end_", calculate(max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract]))), 
if([start_] >= max('Calendar'[Date]), blank(), (Datediff([start_], mx, MONTH)+ 1)* [rev]))`
- `Contract Measures[Amount Billed]`: `calculate(sum(CONTRACTS_BILLING_F[BILLABLE_ALL]), CONTRACTS_BILLING_F[In Current Contract] = 1)`
- `Contract Measures[Over-Under Billed]`: `[Amount Billed] - [Total Revenue Recognized Across Jobs]`

### C) GL-based costs (and possibly revenue)
The model includes GL-based cost-of-revenue in `Cost Measures[GL Cost of Revenue]` sourced from `POSTING_DATA_F`.
- `Cost Measures[GL Cost of Revenue]`: `calculate(sum('POSTING_DATA_F'[DEBITAMT]), filter('POSTING_DATA_F', 'POSTING_DATA_F'[ACTNUMBR_1] = "340"))`

## Gross Profit (GP)
### A) Contract GP (recognized revenue minus actual costs)
Contract GP in this report is based on **recognized revenue** (schedule-based) minus **actual costs** (service-call-derived costs), aggregated across contracts.

- `Contract Measures[Actual GP$ Across Jobs_Contract] = Total Revenue Recognized Across Jobs - Cumulative Actual Costs`
- `Contract Measures[Actual GP%_Contract] = Actual GP$ Across Jobs_Contract / Total Revenue Recognized Across Jobs`

### B) Estimated vs forecast GP (contract-level)
These are “contract amount minus cost” style measures:

- `Contract Measures[Estimated GP$] = Contract Amount - Estimated Total Costs`
- `Contract Measures[Forecasted GP$] = Contract Amount - Forecasted Costs` (note: in this model `Forecasted Costs` currently points to `[Estimated Total Costs]`)
- `%` variants divide by `Contract Amount`: `Estimated GP%_Contract`, `Forecasted GP%_Contract`

### C) Additional GP fields on CONTRACTS_D
There are also precomputed/derived GP measures and columns on `CONTRACTS_D`, e.g.:
- `CONTRACTS_D[YTD GP] = SUM(CONTRACTS_D[Calculated Gross Profit])`
- `CONTRACTS_D[Calculated Gross Profit] = YTD_REVENUE_RECOGNIZED - YTD_TOTAL_COST` (column)
- `CONTRACTS_D[GP Margin %] = Calculated Gross Profit / YTD_REVENUE_RECOGNIZED` (column)

### D) Orphaned job/project GP measures
The `Revenue Measures` GP measures (e.g. `Actual GP$`, `Forecasted GP $`) follow a job/project model pattern, but in this dataset they reference missing tables (e.g. `JOBS_D`) and should be treated as copied/orphaned rather than active GP logic.

## Calendar “as-of” date
- `Calendar[Max Date]`: `max('Calendar'[Date])`

## Notes / gotchas to validate
- The `Revenue Measures` table in this dataset appears to be copied from a job/project model and currently references missing tables (broken/unresolved DAX).
- Contract measures mix two notions of costs: call/costs (`CALLS COSTS`, `FORECASTED CALLS COST`) and contract summary columns (`CONTRACTS_D`).
