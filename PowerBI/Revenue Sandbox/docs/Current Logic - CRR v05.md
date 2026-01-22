# Current Logic — Customer Revenue Retention (CRR v05) (Revenue + Gross Profit)

This summarizes how CRR v05 currently defines revenue/GP for the three streams.

## Projects
### Revenue (two sources)
CRR “Projects” revenue is coming from **two distinct sources** inside `PROJECT_REVENUE_F`:

1) **Job-costed projects (newer / job earned, monthly)**
- `PROJECT_REVENUE_F` uses `JOB_FINANCIALS_F[Contract Earned Curr Mo]` as `Amount` (labeled `Source Type = "Job Earned"`).
- This is sourced from the job monthly summary and treated as “earned this month”.

2) **Service projects (older / billing-based)**
- `PROJECT_REVENUE_F` also includes “service billing” rows (labeled `Source Type = "Service Billing"`) by joining contract billing (`CONTRACT_BILLABLE_F[BILLABLE_ALL]`) to `PROJECTS_D` rows where `Project Type = "Service Contract"`.
- In CRR, `PROJECTS_D` itself is an append of:
  - `SERVPROJECTS_D` (derived from `CONTRACTS_D` rows tagged as service projects), and
  - job projects from `JOBSTRIMMED_D` (derived from `JOBS_D`).

Lineage:
- `JOB_MONTHLY_SUMMARY_F` is imported from Snowflake `DATA_WAREHOUSE.DW_FINAL.JOB_MONTHLY_SUMMARY_F`.
- `JOB_FINANCIALS_F` is a Power Query expression that slims and reshapes `JOB_MONTHLY_SUMMARY_F`.

### Costs (for GP)
CRR derives monthly job costs from the job monthly summary by computing deltas of `Total Actual Cost` per job (Power Query logic in `JOB_FINANCIALS_F`), then uses those outputs in `PROJECT_COSTS_F`.

### Service projects inside “Projects”
CRR includes a “Service Billing” project substream:
- For `PROJECTS_D[Project Type] = "Service Contract"`, it joins contract billing rows (`CONTRACT_BILLABLE_F`) to those projects and treats `BILLABLE_ALL` as project revenue (labeled `Source Type = "Service Billing"`).

## Service Contracts
### Revenue (billings-based)
CRR service contract revenue is billings:
- `SERVCONTRACTS_REVENUE_F` comes from `CONTRACT_BILLABLE_F[BILLABLE_ALL]` (filtered to exclude service projects).

CRR measures then apply completed-month logic:
- `Service Contract Revenue = CALCULATE(SUM(SERVCONTRACTS_REVENUE_F[Amount]), FYCALENDAR_D[Is Completed Month] = TRUE)`

### Costs (billings-associated contract call costs)
CRR contract costs come from contract-backed calls:
- `SERVCONTRACTS_COSTS_F` is derived from `CALLS_F`, filtered to exclude service projects and to require a non-null/non-empty `Contract Number`.
- It uses `Cost All` as `Amount` and carries `Customer_Contract_Year Key` as `AgreementKey`.

## T&M (Spot / non-contract calls)
### Revenue and cost (call-level)
CRR “T&M” is derived from calls where `Contract Number` is blank/null:
- `SPOT_FINANCIALS_F` filters `CALLS_F` to `[Contract Number] = null or ""`
- Revenue = `Billable All`
- Cost = `Cost All`
- `Source Type = "Spot T&M"`

CRR measures apply completed-month logic:
- `T&M Revenue = CALCULATE(SUM(SPOT_FINANCIALS_F[Revenue]), FYCALENDAR_D[Is Completed Month] = TRUE)`
- `T&M Cost = CALCULATE(SUM(SPOT_FINANCIALS_F[Cost]), FYCALENDAR_D[Is Completed Month] = TRUE)`
- `T&M Gross Profit = T&M Revenue - T&M Cost`

## Contract-year keys + orphan handling (stability feature)
CRR creates contract-year coverage and protects against missing dimension rows:
- `Customer_Contract_Year Key` is built from calls/billing using `Wscontsq`.
- `SERVCONTRACTS_D_STAGING` expands “years” using `List.Numbers(1, Wscontsq)` and creates `AgreementKey`.
- `SERVCONTRACTS_D` adds inferred/orphan dimension rows for any contract-year keys present in facts but missing from the source dimension, tagging whether the orphan was “Revenue Only”, “Cost Only”, or “Both”.

Primary references:
- `Customer Revenue Retention/current/CRR v05.SemanticModel/definition/tables/PROJECT_REVENUE_F.tmdl`
- `Customer Revenue Retention/current/CRR v05.SemanticModel/definition/tables/SERVCONTRACTS_REVENUE_F.tmdl`
- `Customer Revenue Retention/current/CRR v05.SemanticModel/definition/tables/SERVCONTRACTS_COSTS_F.tmdl`
- `Customer Revenue Retention/current/CRR v05.SemanticModel/definition/tables/SPOT_FINANCIALS_F.tmdl`
- `Customer Revenue Retention/current/CRR v05.SemanticModel/definition/tables/_Key Measures.tmdl`
