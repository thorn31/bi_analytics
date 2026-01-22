# Current Logic — Amend Reports (Revenue + Gross Profit)

This summarizes how revenue and GP are computed in the three Amend Reports models we documented.

## Mechanical Project Management (Projects — Mechanical division)
### Revenue
The model implements **earned revenue** (not GL revenue) using a cost-based percent complete:
- Earned Revenue = `(Actual Costs / Forecasted Costs) * Contract Amount`

Key mechanics:
- `% Complete` is capped at 1.0.
- Many visuals aggregate job-by-job (SUMX/SUMMARIZE on `JOB`) to maintain job grain.

Lineage (high level):
- Actual costs: `JOB_COST_DETAILS` (`DATA_WAREHOUSE.DW_CLEAN.JOB_COST_DETAILS`)
- Forecasted costs: `JOB FORECAST` (`DATA_WAREHOUSE.DW_FINAL.JOB_COST_FORECASTS_F`)
- Contract amount: `JOB` (`DATA_WAREHOUSE.DW_FINAL.JOBS_D`) plus change orders (`JOB_CHANGE_ORDERS`)
- Date context: model `Calendar` (calculated table) + `Calendar[Max Date]` for “as-of” totals.

### Gross Profit (GP)
Two GP concepts exist:
- Earned GP (project-style): earned revenue logic minus costs (and forecast/estimate variants).
- GL GP (backlog pages): derived from GL postings.

See: `Amend Reports/Mechanical Project Management/docs/Mechanical Project Management - Measure Explanations.md`.

## Contract Management (Service contracts)
### Revenue
This report’s **active** contract revenue is **recognized revenue** (schedule-based), not billings:
- Contract Amount is allocated across months in the contract term.
- Billings are used only for variance (Over/Under).

Key mechanics:
- `Monthly Recognzied Revenue = Contract Amount / (# months in term)`
- `Total Revenue Recognized` multiplies monthly by months since start (calendar-context dependent).

Lineage (high level):
- Contracts: `CONTRACTS_D`
- Billings: `CONTRACTS_BILLING_F[BILLABLE_ALL]`
- Date context: `Calendar[Date]`, `today()` logic

Important note:
- The `Revenue Measures` table exists but is orphaned/broken in this model (references missing tables); it should not be treated as the contract revenue logic.

### Gross Profit (GP)
Contract GP is based on:
- Recognized revenue minus actual costs (service-call-derived), aggregated across contracts.

See: `Amend Reports/Contract Management/docs/Contract Management - Measure Explanations.md`.

## Service Call Management (T&M / service calls)
### Revenue
Revenue is treated as **billings**:
- `Amount Billed = sum('*CALL DETAILS'[BILLING_AMOUNT])`

FYTD versions filter to max selected fiscal year in `*Calendar`.

Lineage (high level):
- Billings: `*CALL DETAILS` (`DATA_WAREHOUSE.DW_FINAL.CALL_DETAILS_F`)
- Date context: `*Calendar` (calculated table)

### Costs
Costs are derived by unpivoting cost columns from `CALLS_F` into `*CALLS COSTS` and summing `[Value]`.

### Gross Profit (GP)
GP is billings minus costs, filtered to CLOSED calls:
- `Actual GP$ = Amount Billed - Actual Costs` (CLOSED only)
- `Actual GP% = Actual GP$ / Amount Billed` (CLOSED only)

See: `Amend Reports/Service Call Management/docs/Service Call Management - Measure Explanations.md`.

