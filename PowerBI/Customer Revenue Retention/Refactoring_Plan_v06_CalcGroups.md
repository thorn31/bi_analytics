# Refactoring Plan: Migrating CRR Model to Calculation Groups (v06)

**Objective:** Simplify the semantic model by replacing repetitive Time Intelligence variations (PY, YTD, YoY, Cumulative, FY As Of) with a unified **Calculation Group** architecture. This will reduce the measure count by ~60% and ensure absolute consistency across all visuals.

---

## 1. Core Concept
Instead of creating `Total Revenue PY`, `Total Cost PY`, `Total GP PY`, `Project Revenue PY`... we create **ONE** generic `PY` calculation item that applies to *any* selected measure.

**Current State (Combinatorial Explosion):**
*   Base Measures (Revenue, Cost, GP) x Time Variations (CY, PY, YoY, YTD, R12M) = **15+ Measures per Base Metric**.

**Future State (Unified):**
*   Base Measures (Revenue, Cost, GP) = **3 Measures**.
*   Time Intelligence Group (CY, PY, YoY, etc.) = **1 Group**.
*   **Result:** Drag `Time Intelligence` to columns/legend to generate all variations instantly.

---

## 2. Proposed Calculation Groups

### A. Group: `Time Intelligence`
This is the primary engine for the report.

| Item Name | DAX Logic (Concept) | Notes |
| :--- | :--- | :--- |
| **Current** | `SELECTEDMEASURE()` | The default view. |
| **PY** | `CALCULATE( SELECTEDMEASURE(), SAMEPERIODLASTYEAR('FYCALENDAR_D'[Date]) )` | Standard prior period. |
| **YoY Delta** | `[Current] - [PY]` | Replaces `Total Revenue YoY Δ`. |
| **YoY %** | `DIVIDE( [YoY Delta], [PY] )` | Replaces `Total Revenue YoY %`. |
| **YTD** | `TOTALYTD( SELECTEDMEASURE(), 'FYCALENDAR_D'[Date], "09-30" )` | Replaces `Cumulative` measures. |
| **YTD PY** | `CALCULATE( [YTD], SAMEPERIODLASTYEAR(...) )` | Replaces `Cumulative PY`. |
| **R12M** | `CALCULATE( SELECTEDMEASURE(), DATESINPERIOD(..., MAX(Date), -12, MONTH) )` | Standard rolling window. |
| **FY As Of (Scorecard)** | *Custom Logic with Anchor Date* | **CRITICAL:** Replaces the `(FY As Of)` suite. |

**The "FY As Of" Logic in Calc Group:**
```dax
VAR StartDate = [Selected FY Start Date]
VAR EndDate = [As Of Date (Financials)] -- Uses the "Completed Month" anchor
RETURN
    CALCULATE(
        SELECTEDMEASURE(),
        REMOVEFILTERS('FYCALENDAR_D'),
        DATESBETWEEN('FYCALENDAR_D'[Date], StartDate, EndDate)
    )
```
*   **Benefit:** This single item immediately creates `Revenue (FY As Of)`, `GP (FY As Of)`, `Cost (FY As Of)` without writing them.

### B. Group: `Revenue Stream Selector` (Optional but Recommended)
To replace the `Revenue (By Stream)` switch measure.

| Item Name | DAX Logic |
| :--- | :--- |
| **Total** | `SELECTEDMEASURE()` |
| **Project** | `CALCULATE( SELECTEDMEASURE(), 'Revenue_Stream_D'[Stream] = "Project" )` |
| **Service** | `CALCULATE( SELECTEDMEASURE(), 'Revenue_Stream_D'[Stream] = "Service Contract" )` |
| **T&M** | `CALCULATE( SELECTEDMEASURE(), 'Revenue_Stream_D'[Stream] = "T&M" )` |

*   **Impact:** You delete `Revenue (By Stream)`. You just use `[Total Revenue]` and filter by this Calculation Group.

---

## 3. The "Bridge Measures" (Wrappers)
While Calculation Groups handle most scenarios via slicers, specific visuals (like Combo Charts with a Legend) still require explicit measures for the secondary axis (Lines).

**Strategy:** Create minimal "Wrapper" measures that simply call the Calculation Group item. This keeps the logic centralized in the Group but exposes a physical measure for the visual.

| Wrapper Name | Definition | Usage |
| :--- | :--- | :--- |
| **Revenue PY** | `CALCULATE( [Total Revenue], 'Time Intelligence'[Item] = "PY" )` | Combo Chart Line (Target) |
| **GP PY** | `CALCULATE( [Total Gross Profit], 'Time Intelligence'[Item] = "PY" )` | Combo Chart Line (Target) |
| **Revenue YoY %** | `CALCULATE( [Total Revenue], 'Time Intelligence'[Item] = "YoY %" )` | Sorting tables by growth |

*   **Magic Behavior:** These wrappers are **Context Aware**. If you apply a "Cumulative" slicer to the page, `Revenue PY` *automatically* becomes "Cumulative PY". You don't need a separate measure.

---

## 4. The "Do Not Touch" List (Risk Mitigation)

Some logic is too complex or specific to be genericized. We will **KEEP** these as standalone measures:

1.  **Retention Logic (NRR / GRR / Churn):**
    *   These rely on specific cohort definitions (`Retention Base`) and specific Anchors (`As Of Month End (SC)`).
    *   Applying a generic `PY` to `NRR` might break the delicate "Prior Cohort" logic.
    *   **Decision:** Keep `06 Retention KPIs` and `07 Retention KPIs - R12M` as standalone measures.

2.  **NPS R12M (Smart Anchor):**
    *   The `NPS` R12M logic uses a different anchor (`Last NPS Date`) than the Financials.
    *   It *could* fit into the Calc Group if we make the Anchor dynamic based on the measure name (Advanced), but simpler to keep separate for now.

---

## 4. Refactoring Map (What gets Deleted)

**Phase 1: Financials**
*   **Delete:** `Total Revenue PY`, `Total Gross Profit PY`, `Total Cost PY`.
*   **Delete:** `Total Revenue YoY %`, `Total Gross Profit YoY %`...
*   **Delete:** `Total Revenue (FY As Of)`, `Total Gross Profit (FY As Of)`, and all their PY/Delta variants.
*   **Delete:** `Revenue Cumulative (By Stream)`, `Revenue Cumulative PY`.

**Phase 2: Visuals Update**
*   **Charts:** Replace `[Total Revenue PY]` with `[Total Revenue]` + Calc Group `PY`.
*   **Tables:** Replace `[Total Revenue (FY As Of)]` with `[Total Revenue]` + Calc Group `FY As Of (Scorecard)`.
*   **Field Parameters:** Update the "Revenue View Mode" parameter to toggle the *Calculation Group Item* (`Current` vs `YTD`) instead of swapping measures.

---

## 5. Implementation Steps (v06 Branch)

1.  **Backup:** Save `CRR v05.pbip` as `CRR v06.pbip`.
2.  **Create Groups:** Use Power BI Model Explorer or Tabular Editor to create `Time Intelligence` group.
3.  **Test:** Create a "Validation Page". Put `[Total Revenue]` in a matrix and drop `Time Intelligence` on columns. Verify all values match `v05`.
4.  **Swap:** Systematically go through visuals and replace specific measures with the generic pattern.
5.  **Purge:** Delete the old measures once usage count is 0.

## 6. Formatting Strategy
Calculation Groups can technically control formatting strings (e.g. `%` for YoY), but since `[Total Revenue]` is Currency and `[Total GP %]` is Percent, we need **Dynamic Format Strings** in the Calculation Items.
*   **Logic:** `SELECTEDMEASUREFORMATSTRING()` usually works, but for `YoY %`, we force `"0.0%"`.

---
**Status:** Plan Ready.
**Next Action:** Execute Step 1 (Save as v06) when ready to start work.
