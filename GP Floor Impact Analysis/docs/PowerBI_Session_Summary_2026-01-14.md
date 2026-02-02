# PowerBI Session Summary — 2026-01-14

## Context
- Report: **Booking GP Floor Analysis** (PBIDesktop model: **Booking GP V02**)
- Purpose: analyze sold **Jobs** and **Contracts** against a user-selected **GP Floor** and compare performance to a **Baseline Year**.
- Visual reference: `PowerBI/GP Floor Impact Analysis/docs/Screenshot 2026-01-14 094417.png`

## Connectivity / validation
- Connected to the open Power BI Desktop instance for **Booking GP V02** via XMLA.
- Ran a sample DAX query (`EVALUATE ROW("Status","OK")`) to confirm query execution and metrics capture.

## Model review (high level)
Reviewed `_Key Measures` to understand how the report works:
- **Source toggle (Jobs vs Contracts)**: driven by `fp_SourceSelector`; core “Total …” measures switch between job/contract base measures.
- **Metric lens selector (# Bookings / $ Sales / $ GP)**: driven by `fp_ViewSelector`; chart measures use `SWITCH` to return the selected lens.
- **Floor logic**:
  - `Is Below Floor` compares rounded `[Total GP %]` to `[GP Floor Value]`.
  - Above/below floor Sell Price and GP$ measures filter underlying QUADRA tables using GP% ≥/＜ floor.
- **Baseline logic**: baseline measures re-evaluate the same KPIs in the selected baseline year using `ALLSELECTED` on Division + Fiscal Year and filtering Fiscal Year to the chosen baseline.

## Changes made (measures/columns)

### Fix: make “% Sale Price Below Floor” dynamic
- Updated `% Sale Price Below Floor` to use the dynamic denominator:
  - Old logic: divided by `[Project Price]` (Jobs-only)
  - New logic: `DIVIDE([Sell Price Below Floor], [Total Sell Price])` (respects Jobs/Contracts selection)

### Fix: make “Impact on Sell Price % vs Baseline” respect Source selection
- Updated `Impact on Sell Price % vs Baseline` to compute global current sales using `[Total Sell Price]` (instead of `[Project Price]`), so it respects Jobs/Contracts selection.

### Added: Division short labels
- Added calculated column `DIVISIONS_D[Division Short]` mapping:
  - Indianapolis → Indy, Knoxville → Knox, Nashville → Nash, Dayton → Day, Cincinnati → Cincy, Louisville → Lou, Lexington → Lex,
    West Virginia → WV, Chattanooga → Chatt, Columbus → Col, Design Build → DB, Green → Green
  - Fallback: original `DIVISIONS_D[Division]`
- Note: Power BI indicated a refresh is required to populate this new column.

### Table/status + “profit opportunity” measures
Added measures to support clearer end-user interpretation in the detail table:
- `Floor Status`
  - Returns `At/Above Floor`, `Below Floor`, or `N/A` when GP%/floor is blank.
  - Updated to return `BLANK()` when there are no fact rows in the current context to avoid bringing in empty rows (e.g., contracts with no data).
- `GP $ Shortfall to Floor`
  - Reworked to behave intuitively:
    - Row-level: matches the magnitude of negative `GP $ Δ Floor` for below-floor bookings (blank otherwise).
    - Total: sums booking-level shortfalls so totals match the sum of visible rows.
- `GP $ At Floor (Below-Floor Bookings)`
  - Target GP$ at the floor for below-floor bookings only (dynamic Jobs/Contracts).
- `GP $ Simulated At Floor`
  - Simulated GP$ if below-floor bookings achieved the floor (holds sell price constant):
  - Defined as: `[Total GP] + [GP $ Shortfall to Floor]`

## Documentation added
- Added `PowerBI/GP Floor Impact Analysis/README.md` describing:
  - report purpose, lenses, KPI meanings, common confusion points, and interpretation tips.

## Findings / gotchas discovered
- **Why “% Bookings Above Floor” can be 100% while “% Sales Above Floor” isn’t**:
  - Current logic can treat **blank GP%** as “not below floor” for counting, while the $-based “above floor” measures exclude blanks due to `GP% >= floor` filtering.
- **Example investigation: “Redstone Engineering” (`JC1593`)**
  - `QUADRA_JOBS` contains both a positive and a reversal row for the same job, resulting in **Total Sell Price = 0** and **Total GP% = BLANK()** at the job level.
  - Because `Sell Price At Or Above Floor` filters at the row level using GP%, the positive row can be included while the reversal row is excluded, which can cause unintuitive numerator/denominator behavior.
  - Follow-up needed: decide stakeholder-preferred handling for reversals/credits and for bookings where `Total Sell Price = 0`.

## UI/visual experiments (not finalized)
- Prototyped a “single label on baseline line” approach using measures:
  - `Baseline Line Label` (card-based text label)
  - `Baseline Line Label Point` (single-point series label)
- You decided to remove/simplify this approach for now and will clean it up manually.

## Open follow-ups (decision needed)
- Define business rules for:
  - booking classification when GP% is blank / sell price is zero,
  - handling reversal/credit rows in Jobs/Contracts,
  - whether “above floor” logic should be evaluated at booking (net) grain vs row grain.

