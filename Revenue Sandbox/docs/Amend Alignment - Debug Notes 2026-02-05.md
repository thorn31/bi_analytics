# Amend Alignment - Debug Notes 2026-02-05

## Context
Goal: align Revenue Sandbox to Amend methodology and reconcile GL vs Amend vs CRR streams. Focus on Projects (Amend) and stream mapping (Projects / Contracts / T&M) with GL markets.

## Key Model Changes Applied Today
### 1) DivisionMonth_Stream_Method_F (analysis table)
- Added GL stream mapping with market buckets.
- Added DESIGN BUILD to Projects mapping.
- Reclassified PROJECT REPAIR from Projects to T&M.
- GL mapping lists (current):
  - Projects: O&M PROJECTS, SPECIAL PROJECT, PROJECTS, PLAN SPEC, CONTROLS, INDUSTRIAL, PERFORMANCE CONTRACT, DESIGN BUILD
  - T&M: SPOT, O&M SPOT, INTERCOMPANY SPOT, PROJECT REPAIR
  - Contracts: ASSURED, CERTIFIED, INSPECTION, O&M
- Relationships created:
  - DivisionMonth_Stream_Method_F[Month End] -> FYCALENDAR_D[Date]
  - DivisionMonth_Stream_Method_F[Divisions] -> DIVISIONS_D[DivisionCode]

### 2) GL measures
- GL Revenue (Projects) updated to remove PROJECT REPAIR and include DESIGN BUILD.
- GL Revenue (Spot/T&M) updated to include PROJECT REPAIR.

### 3) Amend Projects measure alignment
- Projects Revenue (Amend - Job Cost) changed to use precomputed column:
  - SUM(Projects_ProjectMonth_Amend_F[Revenue Amount])
  - Filtered to Project Subsegment = Job Cost
  - Completed months only
- Helper measures deleted (no longer used):
  - Amend Cum Actual (PerProject)
  - Amend Cum Forecast (PerProject)
  - Amend % Complete (PerProject)
  - Amend Contract Amount (PerProject)
  - Amend Earned TTD (PerProject)
  - Amend Earned TTD (Start-1) (PerProject)
  - Amend Earned Revenue (Mo) (PerProject)

Result: Projects Revenue (Amend) now matches Projects_ProjectMonth_Amend_F[Revenue Amount] under completed-month filter.

## Findings
### A) FY2026 mismatch resolved by measure change
- Before: Projects Revenue (Amend) measure was ~21.5M higher than table in FY2026.
- After: Measure matches table when completed months applied.

### B) GL stream mapping improved
- Adding DESIGN BUILD materially improved GL Projects alignment (especially Mechanical).
- Reclassifying PROJECT REPAIR to T&M reduced FY2024 T&M delta by about 6.0M.

### C) Remaining FY2024 deltas
- FY2024 (TFS + Service) still shows GL lower than Amend in T&M and Projects.
- No unmapped GL markets in FY2024 (Other/Unmapped ~ 0).
- Remaining delta appears to be classification or source differences, not missing markets.

### D) Early years (2020-2021) are broken for Amend Projects
- Projects_ProjectMonth_Amend_F shows extreme outliers in FY2020-2021.
- Audit indicates major data-quality issues in Job Cost inputs (MECH_GP):
  - ForecastCost_Mo is often zero/blank or negative.
  - ActualCost_Mo has negative values.
- These conditions cause earned revenue to blow up when using cost-based percent complete.

## Data Quality Audit (Job Cost rows)
FY2020-2023 (Projects_ProjectMonth_Amend_F, Job Cost rows):
- FY2020: Forecast zero/blank 472; Forecast negative 199; Actual negative 32; Revenue negative 116
- FY2021: Forecast zero/blank 669; Forecast negative 238; Actual negative 41; Revenue negative 90
- FY2022: Forecast zero/blank 807; Forecast negative 231; Actual negative 43; Revenue negative 87
- FY2023: Forecast zero/blank 956; Forecast negative 276; Actual negative 57; Revenue negative 119

Forecast table (JOB_COST_FORECASTS_F, MECH_GP):
- FY2020: 10,356 rows; 740 negative; 5,646 zero
- FY2021: 10,046 rows; 714 negative; 5,965 zero
- FY2022: 11,231 rows; 698 negative; 6,216 zero
- FY2023: 12,467 rows; 972 negative; 7,377 zero

Actuals (JOB_COST_DETAILS, MECH_GP):
- FY2020: 28,644 rows; 1,319 negative
- FY2021: 27,238 rows; 957 negative
- FY2022: 31,541 rows; 1,317 negative
- FY2023: 32,338 rows; 971 negative

## Why Mechanical Project Management Report Looks Normal (Hypotheses)
- The Amend report does not appear to handle negative/zero forecasts explicitly.
- It likely looks normal because:
  - bad jobs may be filtered out in visuals (job status/start date), or
  - users filter to later years or specific job subsets.
- COST_CODE_MAPPING exists but is only used for contingency measures, not the core earned revenue calc.

## Open Questions
1) Should negative/zero forecast values be filtered or corrected for earned revenue? If yes, define the rule.
2) Does the Amend Mechanical Project Management report implicitly filter out problematic jobs (status, date, etc.)?
3) Should Projects_ProjectMonth_Amend_F enforce a rule like:
   - if cumForecast <= 0 then blank
   - pctComplete = min(1, max(0, cumActual / cumForecast))

## Next Steps (for tomorrow)
1) Compare Amend Mechanical Project Management report visuals for FY2020-2021 and identify any implicit filters.
2) Decide on business rule for handling forecast <= 0 or negative actuals.
3) If rule approved, update M query for Projects_ProjectMonth_Amend_F to stabilize early years.
4) Re-run FY2020-2023 sanity check after any rule changes.


## Additional Note (per user)
- Amend Mechanical report Net Earned Revenue formula:
  - `Net Earned Revenue = ROUND(DIVIDE(Actual Cost, Cumulative Forecast, BLANK()), 4) * Current Contract Amount`
- Cumulative Forecast definition:
  - `Cumulative Forecast = ROUND(CALCULATE([Cost Budget], FILTER(ALL(Calendar), Calendar[Date] <= [Max Date])), 2)`
- This formula has no guardrail for negative/zero forecasts and does **not** cap at 1.0, which aligns with the observed extreme values when forecast is invalid.

## Calendar Window Note
- Amend Mechanical report Calendar uses a rolling 5-year window:
  - Start: Jan 1 of (Today - 5 years)
  - End: Today + 365
- As of 2026-02-05, this starts at 2021-01-01, so 2020 data is excluded.
- Our M query currently starts at 2020-01-01, which pulls 2020 data and surfaces forecast/actual anomalies.
- Hard-setting 2021-01-01 may stabilize early years but would diverge from a rolling window used in the Amend report.
- Outcome note: shifting the start date/window does not fix the 2021 issues; it only moves which years are included.
- Reminder: if we test changing the start date/window, reset StartDate back to 2020-01-01 afterward.
- Note: Mechanical report uses "Net Earned Rev Across Jobs" (job-grain SUMX/SUMMARIZE). This enforces job-level aggregation and can avoid double-counting when fact tables have multiple rows per job. Our model currently sums precomputed job-month revenue, which should already be at job grain, but differences can arise if job grain is not enforced in visuals/measures.
