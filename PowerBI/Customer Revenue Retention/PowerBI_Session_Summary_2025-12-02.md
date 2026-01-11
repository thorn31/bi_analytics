# Power BI Session Summary - December 2, 2025

## Overview
This session focused on advanced time-intelligence filtering, Calculation Groups, and user interface controls in Power BI. We moved from standard separate slicers to a unified "Period Select" toggle and solved complex interaction issues involving implicit measures and table relationships.

## Key Technical Accomplishments

### 1. Calculation Groups for Time Intelligence
We replaced standalone boolean columns (`Is Current Week`, `Is Current Month`) with a unified **Calculation Group** named `Period Select`.

*   **Goal:** Create a single slicer to toggle between "Current Week", "Current Fiscal Year", "Previous Week", etc.
*   **Implementation:**
    *   Created Calculation Items for each time period.
    *   **Logic Used:** `CALCULATE(SELECTEDMEASURE(), KEEPFILTERS('FYCalendar'[Is Current Week] = TRUE))`
    *   **Why `KEEPFILTERS`?** It adds the boolean flag to the existing filter context rather than replacing it, ensuring compatibility with other visuals.

### 2. The "Row Hiding" Problem & Solution
**The Issue:** Selecting a Calculation Item (e.g., "Current Week") correctly filtered the *measures* (returning BLANK for dates outside the week), but **did not hide the rows** in the Table visual.
*   **Root Cause:** The table contained Dimension columns (e.g., `Job Name`) and implicit measures. Calculation Groups only affect explicit measures. Dimension columns remain visible if the relationship does not filter them out.
*   **Relationship Check:** `FYCalendar` filtered `QUADRA_JOBS` (Fact), but the relationship was **One Direction**. Therefore, filtering `FYCalendar` did *not* propagate back up to filter `JOBS_D` (Dimension), leaving all Job rows visible.

**The Solution:** A dedicated "Filter Measure".
*   **Measure:** `Period Filter Check = IF( NOT(ISEMPTY('QUADRA_JOBS')), 1, 0 )`
*   **Logic:** Checks if the **Fact Table** (`QUADRA_JOBS`) has any rows for the current context (Job + Selected Time Period).
*   **Usage:** Added to the **"Filters on this visual"** pane of the Table visual, set to **"is 1"**. This forces the visual to check the fact table and hide rows with no matching transactions.

### 3. Surfacing "Previous" Period Logic
We expanded the `Period Select` group to include "Previous Week", "Previous Month", and "Previous Fiscal Year".
*   **Discovery:** The logic was already calculated in the Power Query (M) script for `FYCalendar` but was being dropped in the final `Rename Columns` step.
*   **Fix:** Adjusted the M script to reference the correct step (`Add_IsPreviousWeek`) before renaming, exposing these boolean columns to the model.

### 4. Dynamic "Current Filters" Card
We created a smart text measure to display the active filters contextually.
*   **Feature:** If the "Period Select" slicer is active, the card simplifies to show only the Period and Division. If inactive, it shows detailed Fiscal Year/Month information.
*   **DAX Pattern:**
    ```dax
    VAR PeriodSelection = SELECTEDVALUE('Period Select'[Period])
    RETURN
    IF( NOT(ISBLANK(PeriodSelection)),
        "Divisions: " & ... & " | Period: " & PeriodSelection,
        "Divisions: " & ... & " | Fiscal: " & ... & " | Months: " & ...
    )
    ```

### 5. UI: Toggling Slicers with Bookmarks
**Concept:** Switching between "Simple" (Period Select) and "Advanced" (Year/Month/Qtr) slicer views.
*   **Method:** **Bookmarks** + **Selection Pane**.
*   **Execution:**
    1.  Group visual elements into `Simple Filter Group` and `Advanced Filter Group`.
    2.  Create two Bookmarks (`Simple View`, `Advanced View`) that toggle the **Visibility** (Show/Hide) of these groups.
    3.  **Critical Setting:** Uncheck **"Data"** on the bookmarks so they only affect visibility, not the actual filter selections.
    4.  Use Buttons (or a "Toggle Switch" simulation with two buttons) linked to these bookmarks to allow user switching.

## Concepts Learned for Future Projects

1.  **Implicit Measures vs. Calculation Groups:** Calculation Groups do not natively filter implicit measures unless `discourageImplicitMeasures` is set to `true`. Workarounds (like the Filter Measure) are required if you keep implicit measures.
2.  **Relationship Direction Matters:** Visual filtering behavior depends heavily on Cross-Filter Direction. One-way filters stops dimension filtering; `ISEMPTY()` on the Fact table is a reliable bridge.
3.  **Power Query Step Dependencies:** Always check the `in` statement and previous step references in M scripts when columns appear missing.
4.  **Bookmark Scope:** Bookmarks capture *everything* by default (Data, Display, Page). For UI toggles, **always disable "Data"** to prevent resetting user inputs.
