# PowerBI Session Summary - 2026-01-02

## 1. Retention Model Refinements
*   **Logo Retention:** Created two new sets of measures to track customer count retention alongside revenue retention.
    *   **Service Contract (SC):** Measures retention of customers specifically within the Service Contract stream (slice-aware).
    *   **Total (Any Stream):** Measures retention of customers across *any* revenue stream (Projects + SC + T&M).
    *   **Insight:** Discovered that "SC Only" retention is often higher than "Total" retention due to the volatile nature of project-only customers.
*   **Prior Year (PY) Fix:** Updated NRR/GRR/Logo PY measures to use **Explicit Anchor Logic**.
    *   *Old Logic:* `CALCULATE( [Measure], SAMEPERIODLASTYEAR(...) )` (Failed when no slicer was active).
    *   *New Logic:* `CALCULATE( [Measure], 'FYCALENDAR_D'[Date] = PriorAnchorDate )`. This forces the internal "As Of" logic to evaluate correctly even in "All Time" contexts.

## 2. Trend Indicators
*   Created `Trend vs PY` measures for **Revenue**, **Gross Profit**, **NRR**, **GRR**, and **Logo Retention**.
*   **Features:**
    *   Uses Unicode Arrows (▲, ▼, ▬).
    *   **Churn Handling:** Explicitly handles cases where `CY=0` but `PY>0` to show "-100%" instead of Blank.
    *   **Alignment:** Implemented `UNICHAR(8199)` (Figure Space) padding for positive values to ensure perfect center-alignment in visuals.

## 3. Data Quality & Calendar Logic
*   **Future Date Guard:** Updated Power Query scripts for all 5 fact tables (`PROJECT_REVENUE/COSTS`, `SERVCONTRACTS_REVENUE/COSTS`, `SPOT`) to filter out dates `> Date.From(DateTime.LocalNow())`.
    *   *Reason:* Found typos in source data (Year 2202, 9202) causing the calendar to stretch and "Ghost Months" to appear.
*   **Current Month Skew:** Addressed the issue where partial month data (e.g., Jan 1-2) makes current performance look bad.
    *   **Solution:** Created `Is Completed Month` column in `FYCALENDAR_D`.
    *   **Measure Update:** Wrapped core measures (`Revenue (By Stream)`, `Cost (By Stream)`) in `CALCULATE( ..., 'FYCALENDAR_D'[Is Completed Month] = TRUE )`.
    *   *Hybrid Logic:* For Card visuals (Total context), it sums *only* completed months. For Chart visuals (Month context), it returns Blank for incomplete months.
*   **Activity Definition:** Updated `Last Billing Date (Any Stream)` to exclude rows with `$0.00` billing amount.

## 4. Visual Strategy (Customer Detail Page)
*   **Header:**
    *   **Identity:** Name + Lifecycle Status Badge (with Muted Color Palette).
    *   **KPIs:** Revenue, GP%, NRR, Months Since Billing (all R12M Rolling).
*   **Row 2 (Story):** Standard Stacked Column Chart showing Revenue Mix (Project/SC/T&M) over last 24 months + Total Revenue PY Line.
*   **Row 3 (Planned):** Active Contracts Table + Service Call Cost Intensity Scatter Plot.

## 5. Next Steps
*   Verify the **Active Contracts** table logic (check `SERVCONTRACTS_D` fields).
*   Build out **Row 3 visuals** (Scatter plot for call intensity).
*   Finalize the **Customer Detail** report page layout.
