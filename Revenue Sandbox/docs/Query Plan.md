# Revenue Sandbox — Query Plan (Customer × Month)

Goal: compute monthly totals per customer for four revenue streams, with parallel “alternate” methods for reconciliation.

## 0) Canonical keys and grain
**Grain:** one row per:
- `Customer Key`
- `Month End` (or fiscal month end)
- `Revenue Stream` ∈ {Project, Service Contract, T&M, Legacy Service Projects (Contracts)}

**Required columns (minimum):**
- `Customer Key`
- `Month End`
- `Revenue Stream`
- `Revenue Amount`
- `Cost Amount` (optional at first; needed for GP)

**Recommended traceability columns (optional):**
- `AgreementKey` (contract-year)
- `SurrogateProjectID` (job/service-project)
- `Source Type` (to explain how a row was generated)

## 1) Shared dimensions
### 1.1 Calendar
Use a single month bucket definition for everything:
- `Month End = Date.EndOfMonth([Date])`
- Include fiscal attributes if needed (FY, fiscal month index).
Optional: include `Is Completed Month` for guardrails.

### 1.2 Customer
Canonical customer identifier:
- `Customer Key` (string) used consistently across all facts.

## 2) Stream 1 — Projects
### 2.1 Primary (CRR-style, month-grain earned)
Source:
- Snowflake `DATA_WAREHOUSE.DW_FINAL.JOB_MONTHLY_SUMMARY_F`

Definition:
- Revenue = `Contract Earned Curr Mo` aggregated to `(Customer Key, Month End)`

Implementation:
- Import `JOB_MONTHLY_SUMMARY_F` (or a slim view) with: `Period Date`, `Customer Key`, `Contract Earned Curr Mo`, plus job/project identifiers.
- Build `PROJECT_CustomerMonth_Revenue_Primary`:
  - `Month End = Date.EndOfMonth([Period Date])`
  - Group by `Customer Key`, `Month End`
  - Sum `Contract Earned Curr Mo`

Costs (optional for GP):
- Use monthly cost from `JOB_MONTHLY_SUMMARY_F` or the derived “Monthly Cost” logic (delta of `Total Actual Cost`), aggregated to customer-month.

### 2.2 Alternate (Amend-style earned revenue from percent complete)
Goal: replicate Mechanical earned revenue behavior at month grain:
- Earned Revenue = `(Actual Costs / Forecasted Costs) * Contract Amount` (with cap behavior as implemented)

Implementation approach (recommended):
- Compute **as-of** earned revenue by Month End (job grain), then delta:
  - `Earned_AsOf(MonthEnd) - Earned_AsOf(PriorMonthEnd)`

Inputs (Snowflake tables used in Amend reports):
- `JOB_COST_DETAILS(_F)`
- `JOB_COST_FORECASTS(_F)`
- `JOBS_D`
- change orders (if required to match): `JOB_CHANGE_ORDERS` or monthly change order view

Output:
- `PROJECT_CustomerMonth_Revenue_Alt`
- plus variance table/measures vs primary.

## 3) Stream 2 — Service Contracts
### 3.1 Primary (billings-based, history-preserving)
Source:
- Contract billing fact (CRR uses `CONTRACT_BILLABLE_F` derived from staging `SV00564`)

Definition:
- Revenue = billings (`BILLABLE_ALL`) aggregated to `(Customer Key, Month End)`

Keying:
- Use contract-year key:
  - `AgreementKey = CustomerKeyFull + '_' + ContractNumber + '_' + YearIndex`
  - `YearIndex` expanded using `Wscontsq` (1..Wscontsq)

Output:
- `SERVCONTRACT_CustomerMonth_Revenue_Primary`

Costs (optional for GP):
- contract call costs aggregated to customer-month (from calls, contract-backed only).

### 3.2 Alternate (recognized revenue, schedule-based)
Goal: replicate Contract Management “recognized revenue” behavior.

Definition:
- Monthly recognized revenue = Contract value allocated across contract term months.

Key requirements:
- Historical contract-year coverage (cannot rely on `CONTRACTS_D` being complete).
- Use contract-year keys (AgreementKey) and contract-year term dates/value as-of that year.

Output:
- `SERVCONTRACT_CustomerMonth_Revenue_Alt`
- `Over/Under` style variance = billed - recognized.

## 4) Stream 3 — T&M (service-call-driven)
### 4.1 Primary (call-billing based)
Candidate sources (need to reconcile which is authoritative):
- `CALLS_F[Billable All]` (call-level)
- `CALL_DETAILS_F[BILLING_AMOUNT]` (call detail-level)

Stream ownership rules (initial assumption):
- include only `TYPE_OF_CALL ∈ {"REPAIR","QUOTED SERVICE"}`
- exclude contract-backed calls (calls that have a valid contract-year key / contract number that maps to a contract stream)

Outputs:
- `TM_CustomerMonth_Revenue_Primary` (choose one source)
- `TM_CustomerMonth_Revenue_Alt` (the other source), if both exist

Costs (optional for GP):
- from calls cost columns (or unpivoted cost table), filtered to the same stream ownership.

## 5) Stream 4 — Legacy Service Projects (stored as contracts)
Definition:
- Legacy service projects are contracts where either:
  - `Contract Type = "PROJECT"` **OR**
  - `Contract Number` starts with `"P"` (case-insensitive, trimmed)

Primary method (CRR-style):
- Revenue = billings from `CONTRACT_BILLABLE_F[BILLABLE_ALL]`
- Month End = `Date.EndOfMonth([WENNSOFT_BILLING_DATE])`
- No costs (revenue-only)

Output:
- `LEGACYPROJECTS_CustomerMonth_Billings_F`

## 6) Conformed output tables
`CustomerMonth_Stream_Method_F` = union of:
- `PROJECT_CustomerMonth_Revenue_Primary` (CRR)
- `PROJECT_CustomerMonth_Revenue_Alt` (Amend)
- `SERVCONTRACT_CustomerMonth_Revenue_Primary` (CRR)
- `SERVCONTRACT_CustomerMonth_Revenue_Alt` (Amend)
- `TM_CustomerMonth_Revenue_Primary` (CRR)
- `TM_CustomerMonth_Revenue_Alt` (Amend)
- `LEGACYPROJECTS_CustomerMonth_Billings_F` (CRR)

## 7) Required reconciliation checks
At minimum:
- `Variance = Primary - Alt` by stream / customer / month
- “Source totals” vs “dest totals” checks (CRR already includes patterns like this for calls/revenue).

