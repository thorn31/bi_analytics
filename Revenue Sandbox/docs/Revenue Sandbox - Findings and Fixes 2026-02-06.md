# Revenue Sandbox - Findings and Fixes 2026-02-06

## Purpose
Capture what was discovered and fixed in the **Revenue Sandbox** model during alignment work, and document the resulting **authoritative revenue methodology selections** for the next model/CRR migration phase.

## High-Level Outcome
- Projects revenue using the Amend methodology is now stable and aligns materially better with the Amend report once fiscal windowing and carry-in logic are handled correctly.
- The remaining gaps observed during debugging were explainable (primarily **fiscal-year boundary** and **missing carry-in inputs**), not mysterious report filters.

## What Was Broken (Symptoms)
### 1) Early-year Projects earned revenue outliers (extreme values)
- In early fiscal years, `Projects_ProjectMonth_Amend_F` contained extreme earned revenue values (orders of magnitude larger than expected).
- These outliers caused Amend-vs-CRR and Amend-vs-GL comparisons to look "random" in early years.

### 2) FY2021 mechanical discrepancy that looked like a calculation mismatch
- Under a Mechanical slice, FY2021 showed a large delta between:
  - Projects revenue (Amend - Job Cost) and
  - GL Revenue (Projects)
- Initial suspicion was gating or mapping issues; it was ultimately a **calendar windowing** issue (see below).

## Root Causes
### A) Floating-point residue and near-zero denominators
- Earned revenue percent complete is fundamentally a ratio of cumulative actual to cumulative forecast.
- In practice, cumulative forecast could be extremely small (or small negative) due to floating-point residue and/or missing carry-in forecast inputs.
- Dividing by near-zero produced extreme percent completes, which then exploded revenue when multiplied by contract amounts.

### B) Missing carry-in forecast inputs due to start-date filtering
- The sandbox was filtering forecast inputs to a reporting start date, but percent complete needs the cumulative baseline that may exist prior to that date.
- When baseline forecast months existed before the reporting window, cumulative forecast inside the reporting window could be wrong (including negative drift), creating unstable earned revenue behavior.

### C) Fiscal-year boundaries were not respected by calendar start dates
- A reporting start date like `2021-01-01` does not align with fiscal year boundaries when FY starts earlier (e.g., FY months in CY2020).
- This manifested as FY totals missing early fiscal months, which looked like a "method mismatch" but was actually missing rows.

## Fixes Applied
All fixes were implemented in the sandbox model using the Power BI Modeling MCP workflow.

### 1) Stabilize percent-complete denominator (rounding)
- The cumulative forecast denominator was rounded to 2 decimals prior to division.
- This removed the near-zero float residue that was generating extreme ratios.

### 2) Add carry-in for cumulative forecast (and keep reporting window output)
- Forecast inputs were extended back prior to the reporting window to supply correct cumulative baselines.
- Output rows remain filtered to the reporting window, but the cumulative calculations use earlier months as carry-in.

### 3) Implement time-phased change orders for job-cost projects
- `JOB_CHANGE_ORDERS_F` was added and used to compute a cumulative contract-as-of per job and month.
- Earned revenue now uses:
  - `contractAsOf = origContract + cumulativeChangeOrders`
  - `earnedTTD = pctComplete * contractAsOf`
  - monthly earned = delta of earnedTTD

### 4) Carry-in policy for projects
- Carry-in for job-cost projects was pushed back to `2015-01-01` to capture sufficient baseline for forecasts and change orders.
- Reporting window start date must remain **fiscal-year aware** to avoid missing fiscal months.

### 5) Resolved Desktop refresh error encountered during edits
- A refresh error was encountered:
  - `OLE DB or ODBC error: [Expression.Error] We cannot convert a value of type List to type Text..`
- This was caused by an incorrect M expression during an intermediate edit and was corrected by reverting to a clean, deterministic expression structure.

## Validations Performed (How We Confirmed It)
### DAX spot checks
- Queried FY totals for:
  - Projects revenue (Amend - Job Cost) vs GL Revenue (Projects)
- Reproduced the FY2021 delta under explicit Mechanical filters and decomposed it.

### Key reconciliation finding (FY2021 mechanical)
- Under `DIVISIONS_D[Company] = "Mechanical"` and `Fiscal Year = 2021`:
  - The large delta was largely driven by Projects Amend being **blank for fiscal months 1-3** due to a reporting StartDate that began mid-fiscal-year.
- Adjusting the reporting window to align with the fiscal year start resolved the apparent "calculation mismatch."

## Authoritative Revenue Determinations (Selected Methods)
These are the methodological decisions that will drive the newer revenue model and the eventual CRR migration.

### Always available comparator
- **GL revenue** remains a baseline comparator and must always be available in the model and report.

### Stream authorities
- **Projects (earned)**: `Projects_ProjectMonth_Amend_F`
  - Use the sandbox implementation (earned from costs/forecast, contract-as-of includes time-phased change orders, carry-in included).
- **Service Contracts (billings)**: `SERVCONTRACTS_CustomerMonth_Billings_F`
- **T&M (CRR)**: `TM_CustomerMonth_CRR_F`
- **Legacy Projects (billings approximation of GL)**: `LEGACYPROJECTS_CustomerMonth_Billings_F`

## Implications / Design Notes
- The selected authorities imply a clean separation:
  - "Selected Methods" revenue for operational/CRR reporting
  - GL revenue for finance baseline and reconciliation
- Method-selector tables (e.g., `CustomerMonth_Stream_Method_F`, `DivisionMonth_Stream_Method_F`) are likely unnecessary in the newer model unless per-customer/division/month overrides are a product requirement.
- Fiscal-year awareness is not optional: any stream table that filters by a hard StartDate must be checked against fiscal boundaries to avoid silent FY undercounts.

## Next Steps
1) Confirm global policies for the newer model:
   - completed-month clamping convention
   - fiscal window defaults (how far back / forward)
   - projects carry-in start date policy (currently 2015-01-01)
2) Use the migration plan document to implement the newer revenue model structure.
3) Only after the newer model validates: plan the CRR report cutover (side-by-side comparisons first).
