# PowerBI Session Summary - 2026-01-15

## 1. MCP Server Fix (Write Enablement)
Reconfigured the MCP server to allow write operations without interactive confirmations.

*   **Action:** Updated Codex config to run `powerbi-modeling-mcp` with `--skipconfirmation`.
*   **Result:** Reconnected to the local Power BI Desktop model and verified execution with a basic DAX “ping” query.

## 2. Financial “R12M As Of” Anchor Refactor (Option B)
We aligned *financial* R12M measures to a **global any-stream anchor** (instead of the Service Contract retention anchor), while keeping SC retention measures unchanged.

### A. New global financials anchor (last closed month)
*   **Created measures (not hidden):**
    *   `Financials Max Allowed Month End`  
        *Logic:* `EOMONTH(TODAY(), -1)` to cap calculations to the last fully closed month.
    *   `As Of Month End (Financials)`  
        *Logic:* Uses `ALL_BILLINGS_F` to find the last billing date `<= Financials Max Allowed Month End` (and non-zero billing), then converts it to month end via `EOMONTH`.
*   **Validation:** Confirmed anchor resolves to `2025-12-31` for the current date context (1/14/2026).

### B. Updated R12M financial measures to use the new anchor
*   **Updated (anchor swap):**
    *   `Total Revenue (R12M As Of)`
    *   `Total Revenue PY (R12M As Of)`
    *   `Total Gross Profit (R12M As Of)`
    *   `Total Gross Profit PY (R12M As Of)`
    *   `Project Revenue (R12M As Of)`
    *   `T&M Revenue (R12M As Of)`
*   **Aligned GP% measures to the updated bases:**
    *   `Total GP % (R12M As Of)` = `DIVIDE([Total Gross Profit (R12M As Of)], [Total Revenue (R12M As Of)])`
    *   `Total GP % PY (R12M As Of)` = `DIVIDE([Total Gross Profit PY (R12M As Of)], [Total Revenue PY (R12M As Of)])`
*   **Scope boundary:** SC retention measures (NRR/GRR/logo) remain SC-anchored via `As Of Month End (SC)` and `SC_AgreementMonth_Revenue`.

## 3. Customer Page: “Summary by Stream (R12M)” Visual Buildout
We implemented the model components needed to support a 3-bar (Projects / Service Contracts / T&M) 100% normalized visual with stream-specific fills and a remainder segment.

*   **Created disconnected legend table:** `UI_BarFillParts`
    * Values: `Project`, `Service Contract`, `T&M`, `Remainder`
    * Sorting: `Part` is sorted by `Sort` so `Remainder` renders last.
*   **Created measure:** `Revenue Stream Share Fill (R12M)`
    * Updated from “% share” to **$ values** so bar labels can be displayed in currency:
        * Filled segment = stream revenue (R12M)
        * Remainder segment = total revenue (R12M) − stream revenue (R12M)
*   **Created measure:** `Revenue (R12M As Of) (By Stream)`
    * Returns per-stream revenue under `Revenue_Stream_D` axis.
*   **Validation:** Confirmed results for “Greater Clark County Schools” match expected R12M stream mix and totals.

## 4. Customer Page: Risk & Opportunity Metrics (R12M)
Defined a first-pass set of high-level customer metrics designed to avoid blanks across customers with different stream participation.

*   **Created measures (folder: `UI\\Customer\\Risk & Opportunity (R12M)`):**
    *   `Recurring Mix % (SC) (R12M)` = SC share of total R12M revenue (SC derived as `Total - Project - T&M`)
    *   `Stream Concentration % (R12M)` = max stream share of total R12M revenue
    *   `Revenue Momentum % (R12M vs PY)` = total R12M revenue % change vs PY

## 5. Open Items / Next Steps
*   Decide final formatting pattern for Risk & Opportunity cards (icons, thresholds, and when to display $ vs %).
*   Confirm whether any other pages rely on the updated financial R12M measures in unintended ways (visual QA in Desktop).
*   Continue Customer page buildout left-to-right per `Customer_Page_Planning 2026_01_14.md`.

