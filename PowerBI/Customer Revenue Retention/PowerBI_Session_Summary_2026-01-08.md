# PowerBI Session Summary - 2026-01-08

## 1. Global Refactoring: "The Safe Reporting Standard"
We implemented a model-wide policy to exclude incomplete (current) month data from all financial calculations to prevent "dips" in trend reporting.

*   **Action:** Updated 7 Base Measures (`Project Revenue`, `Service Contract Revenue`, `T&M Revenue`, and their Cost counterparts).
*   **Logic:** Wrapped all base SUMs in `CALCULATE( ..., 'FYCALENDAR_D'[Is Completed Month] = TRUE )`.
*   **Impact:** 
    *   **Charts:** January (partial month) bars automatically disappear.
    *   **Tables:** Totals align with completed periods.
    *   **Retention:** `NRR` remains accurate as its anchor logic (`As Of Month End`) naturally aligns with this new base restriction.
*   **Clean Up:** Retired temporary "Patch" measures (`Revenue (Completed Months Only)`) as they are now redundant.

## 2. Customer Detail Page Strategy
### A. The "Profile Card" Pattern
*   **Objective:** Create a clean "Field : Value" list for Customer Identity.
*   **Implementation:** 
    *   Created Disconnected Table: `UI_CustomerProfileRows`.
    *   Created Switch Measure: `[Customer Profile Metric Value]`.
    *   Features: Handles mixed formatting (Currency, Date, Text) and includes a dynamic **Revenue Rank** ("#55 of 1,200").

### B. Top N Contracts
*   **Objective:** Show the largest *active* contracts for a customer (or globally).
*   **Logic:** Created `[Is In Top N (Active Contracts Value)]` which ranks contracts based on `Contract Amount` but strictly filters for `IsActiveContract = TRUE`.

## 3. Net Promoter Score (NPS) Module
We integrated the `NPS_F` fact table and built a robust Time Intelligence suite.

*   **R12M Logic:** Created `Net Promoter Score (R12M)` and `PY`.
    *   **The "Smart Anchor" Fix:** Implemented logic to handle Fiscal Year slicers correctly.
    *   *Issue:* Selecting "FY 2026" (future) broke standard R12M calculations.
    *   *Solution:* Anchored to `MIN( MAX(Calendar), [Last NPS Date] )` and used `REMOVEFILTERS('FYCALENDAR_D')` to allow the window to span back into previous fiscal years.
*   **Trends:** Created Trend indicators (Arrows) for NPS to match the financial cards.
*   **Operational Metrics:** Added `Prompt and On Time %` and `First Time Fix Rate`, explicitly calculating `Yes / (Yes + No)` to exclude blanks.

## 4. Visual Enhancements
### A. Monthly vs. Cumulative Toggle
*   **Feature:** Allowed users to toggle the Revenue Chart between "Monthly Bars" and "Cumulative YTD Area".
*   **Implementation:** Used **Field Parameters** (`UI_Revenue View Mode`).
*   **The "Dynamic Line" Fix:** The PY Line did not automatically switch to Cumulative when the Bars did.
    *   *Solution:* Created `[Revenue PY (Dynamic)]` which reads the Field Parameter selection and swaps the measure between `[Revenue PY]` and `[Revenue Cumulative PY]`.

### B. Fiscal Performance Table
*   **Logic:** Decided to use `(FY As Of)` measures for Annual tables (ensuring apples-to-apples YTD comparison for partial years) but **Standard** measures for Quarterly tables (to allow distinct quarter values).
*   **Formatting:** Replaced text-based Trend Arrows with **Numeric YoY %** measures and Conditional Formatting (Icons) for cleaner density.

## 5. Model Organization & Hygiene
*   **Fiscal Folder Split:** Separated measures into:
    *   **Standard:** For Charts/Trends (Context-aware).
    *   **FY As Of:** For Scorecards/Annual Tables (Forced YTD).
*   **Documentation:** Added Description strings to measures to warn future developers ("Use ONLY for Annual Tables...").
*   **Data Hygiene:** Agreed to use **Report Level Filters** to exclude "Misc" Divisions (Burden/Training) rather than complex Power Query joins.

## 6. Future Considerations (Phase 2)
*   **Calculation Groups:** The model is becoming complex with permutations of `Current`, `PY`, `Cumulative`, `Dynamic`, `(FY As Of)`. Migrating to Calculation Groups (Time Intelligence, Unit Selector) is the recommended next step to reduce measure count and maintenance overhead.
