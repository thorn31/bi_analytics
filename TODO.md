# TODO (Next Steps) — Revenue and Retention / CRR Migration

## 0) Stability / Persistence (PBIP)
- [x] Persist central fact rename in PBIP (`SELECTEDMETHODS_Financials_F` -> `FINANCIALS_F`) across `model.tmdl`, `relationships.tmdl`, table `.tmdl`, and `_Key Measures`.
- [x] After reopen, confirm the rename still holds (Desktop ports/serialization can be inconsistent).
- [ ] If Desktop fails to open PBIP: check for PBIP relationship column-ID issues; remove broken relationships from PBIP and re-add via MCP.

## 1) Naming Cleanup (User Preference)
- Replace `SELECTEDMETHODS_Financials_F` naming everywhere with a clearer centralized table name:
  - Current target: `FINANCIALS_F`
- Confirm/standardize stream naming in the combined fact:
  - `Stream`: `Projects`, `Service Contracts`, `T&M`

## 2) Authoritative Revenue Inputs (Fact Tables)
- Keep these as the authoritative stream facts:
  - `PROJECTS_Financials_F` (Projects; Amend logic)
  - `SERVCONTRACTS_Financials_F` (Service contracts; billings-derived)
  - `TM_Financials_F` (T&M; CRR-based source)
- Centralize via:
  - `FINANCIALS_F` = union of the stream facts at the agreed grain (Customer + Month + Division attributes + Stream)

## 3) Dim Tables (Model Shape)
- Confirm these dims are present and related correctly (star-ish):
  - `CUSTOMERS_D`
  - `DIVISIONS_D`
  - `FYCALENDAR_D`
  - Stream-specific dims remain for detail slicing where needed:
    - `PROJECTS_D`
    - `SERVCONTRACTS_D`
    - (optional) `JOBS_D` / `CONTRACTS_D` only if required for drill paths

## 4) GL Baseline (Always Available)
- Keep `POSTING_DATA_F` + `GL_ACCT_D` as the GL baseline for reconciliation.
- Measure sign convention:
  - `GL Revenue = SUM(POSTING_DATA_F[CRDTAMNT]) - SUM(POSTING_DATA_F[DEBITAMT])`
  - Equivalent for revenue accounts: `GL Revenue = -SUM(POSTING_DATA_F[PERDBLNC])`
- Add/confirm scoped variants:
  - `GL Revenue (Projects)` filtered to the Projects markets
  - Define `GL_ACCT_D[MARKET]` -> Stream mapping for reconciliation buckets:
    - Projects (include both SERV_GP and MECH_GP project-like markets)
    - Service Contracts (ASSURED/CERTIFIED/INSPECTION/O&M as agreed)
    - T&M (SPOT/O&M SPOT/INTERCOMPANY SPOT as agreed)
  - [x] Add `GL Revenue (Service Contracts)` / `GL Revenue (T&M)` measures (STREAM_D-scoped)
  - (later) `GL Revenue (Service Contracts)` / `GL Revenue (T&M)` if definable by account/market mapping

## 4.2) GL Budget (YTD + P&L)
- [x] Import `BUDGET_F` into the `Revenue and Retention` model.
- [x] Ensure relationships exist:
  - `BUDGET_F[ACCTIDX_KEY]` -> `GL_ACCT_D[ACCTIDX_KEY]`
  - `BUDGET_F[PERIODEND]` -> `FYCALENDAR_D[Date]`
  - `BUDGET_F[DIVISION]` -> `DIVISIONS_D[DivisionCode]`
- [x] Add base measure:
  - `GL Budget Revenue` (completed months, sign-flipped, `GL_ACCT_D[ACCOUNT_TYPE]="REVENUE"`)

## 4.1) Stream Dimension (For Visuals)
- [x] Add `STREAM_D` (Projects / Service Contracts / T&M) for legend/slicing.
- [x] Add `GL_MARKET_STREAM_D` mapping table (hidden).
- [x] Add relationships via MCP (PBIP relationship serialization is finicky for new tables):
  - `FINANCIALS_F[Stream]` -> `STREAM_D[Stream]`
  - `GL_MARKET_STREAM_D[Stream]` -> `STREAM_D[Stream]`
  - `GL_ACCT_D[MARKET]` -> `GL_MARKET_STREAM_D[Market]`
- [x] Add disconnected visual-helper tables for CRR v05 layout reuse:
  - `UI_BarFillParts`
  - `UI_Customer Status Selector`
  - `UI_CustomerProfileRows`
  - `UI_Waterfall - NRR Breakdown`
- [x] Refactor measures off `Revenue_Stream_D` (safe to delete table; visuals can be rewired to `STREAM_D`).

## 5) Measures Home + Foldering
- Measures live in `definition/tables/_Key Measures.tmdl` (`_Key Measures` table in the model).
- Implement deterministic display folder structure (numbered, hierarchical), e.g.:
  - `1. Revenue`
  - `1.1 Revenue\1.1.1 Selected Methods`
  - `1.1 Revenue\1.1.2 GL`
  - `2. Cost`
  - `3. Gross Profit`
  - `5. Retention`
  - `7. Helper`
  - `8. Deprecated`
- Every measure must have:
  - Display folder
  - Description (purpose + assumptions)
  - Format string (or documented intent)

## 6) Retention Measure Migration (CRR v05 -> New Model)
- Port retention logic from `Customer Revenue Retention/current/` key measures into `_Key Measures`.
- Retention metrics must be based on **service contract revenue only**:
  - Use `SERVCONTRACTS_Financials_F` (or `FINANCIALS_F` filtered to `Stream = Service Contracts`) as the base.
- Define base building blocks first:
  - Service-contract Revenue
  - Prior-year Service-contract Revenue
  - Retained / Lost / New / Churn components (as per CRR definitions)
- Then port KPI measures (retention %, NRR/GRR variants, etc.).

### Implemented (Snapshot FY Period)
- [x] Base: `Service Contract Revenue` (completed months), `Service Contract Revenue PY (FY Period)`
- [x] Components: `Retention Base PY (FY Period)`, `Churn Revenue (FY Period)`, `Contraction Revenue (FY Period)`, `Upsell Revenue (FY Period)`
- [x] KPIs: `Net Revenue Retention % (FY Period)`, `Gross Revenue Retention % (FY Period)`, `Churn Rate % (FY Period)`
- [x] Deprecated FY Period folders under `8. Deprecated\8.1 Retention\FY Period\...`

### Implemented (R12M As Of)
- [x] Helpers (hidden): `As Of Month End (SC)`, `Last SC Data Month End (In Slice)`
- [x] Base: `Service Contract Revenue (R12M As Of)`, `Service Contract Revenue PY (R12M As Of)`
- [x] Components: `Retention Base PY (R12M As Of)`, `Churn Revenue (R12M As Of)`, `Contraction Revenue (R12M As Of)`, `Upsell Revenue (R12M As Of)`
- [x] KPIs: `Net Revenue Retention % (R12M As Of)`, `Gross Revenue Retention % (R12M As Of)`, `Churn Rate % (R12M As Of)`
- [x] KPI PY: `Net Revenue Retention % PY (R12M As Of)`, `Gross Revenue Retention % PY (R12M As Of)`
- [x] KPI Trend: `Net Revenue Retention Trend vs PY (R12M As Of)`, `Gross Revenue Retention Trend vs PY (R12M As Of)`
- [x] Logo (SC): `Retention Base Count PY (SC) (R12M As Of)`, `Logo Churn Count (SC) (R12M As Of)`, `Logo Retention % (SC) (R12M As Of)` and PY/trend variants
- [x] Anchor clamp: `As Of Month End (SC)` now also caps at `FYCALENDAR_D[Is Completed Month]=TRUE()` to prevent partial-month distortion
- [x] Component %: `Churn Revenue % (R12M As Of)`, `Contraction Revenue % (R12M As Of)`, `Upsell Revenue % (R12M As Of)`
- [x] Logo churn %: `Logo Churn % (SC) (R12M As Of)`
- [x] Waterfall: table `Waterfall - NRR Breakdown` + measure `NRR Waterfall Value (R12M As Of)` (validated step totals)
- [x] Classification (SC): customer retention category helper + customer counts by churn/contraction/upsell/retained
- [x] CRR v05 visual-compat aliases created:
  - `NRR Waterfall Value`
  - `Customer Retention Category (R12M)`
  - `SC Revenue (R12M As Of)`
  - `NRR Logic Explanation.MD`
- [x] Sparklines (SVG images) for KPI cards:
  - `NRR Sparkline (SVG)`
  - `GRR Sparkline (SVG)`
  - `Logo Sparkline (SVG)`

## 6.1) CRR v05 Measures Used In Visuals (Port/Stub)
- [x] Ported financial base measures required by CRR v05 visuals (Totals + By Stream + R12M As Of + FY As Of).
- [x] Ported customer status/profile measures required by CRR v05 visuals.
- [x] Implemented NPS measures after importing `NPS_F`:
  - Relationships:
    - `NPS_F[Customernbr Key]` -> `CUSTOMERS_D[Customer Key]`
    - `NPS_F[SERVICE CALL COMPLETED DATE]` -> `FYCALENDAR_D[Date]`
  - Measures: `NPS Response Count`, `Avg NPS Rating`, `Promoters Count`, `Detractors Count`, `Net Promoter Score`, `Net Promoter Score (R12M)`, `Net Promoter Score PY (R12M)`, `Net Promoter Score Trend vs PY`, `Prompt and On Time %`, `First Time Fix Rate`
  - Helpers: `Last NPS Date`, `Debug - NPS R12M Start Date`
- [ ] Remaining “not implemented” KPIs: spend-per-maintenance + snapshot KPIs (need a confirmed source table/definition).

## 6.2) DAX UDFs (IBCS / SVG)
- [x] Port Power BI custom calendar compatibility fixes completed (model opens cleanly).
- [x] Port DAX UDF pack into `Revenue and Retention` (verified visible in Desktop + via MCP function listing).
- [ ] Create initial IBCS SVG wrapper measures for matrix visuals (start with Revenue vs Budget variance bars).

## 10) P&L Page (YTD First)
- Goal: mirror the system P&L layout using a disconnected row structure + YTD measures (monthly view later).
- [x] Add disconnected structure table: `UI_P&L Structure` with ordered rows:
  - Revenue (by stream): Projects / Service Contracts / T&M
  - Cost of Sales: Labor & Burden, Equipment & Material, Subcontract, Discounts
  - Total Cost of Sales, Gross Profit
  - Operations Expense, Actual Gross Profit
  - Sales Expense, G & A Expense, Total SG & A Expense
  - Other Income & Expense, Net Profit
- [x] Add measures in `_Key Measures` under `4. P&L\\4.1 YTD`:
  - `P&L Amount (YTD)`
  - `P&L Amount PY (YTD)`
  - `P&L Budget Amount (YTD)`
- [x] Add % of revenue measures for the YTD columns (e.g., each line / Total Revenue).
- [x] Add variance measures: vs PY, vs Budget ($ and %) for the YTD view.
- [x] Fix matrix section totals: section header rows now total correctly when collapsed/expanded (excludes subtotal lines to avoid double-counting).
- [x] Revenue split: REVENUE section broken into Projects / Service Contracts / T&M using `GL_MARKET_STREAM_D` mapping (ties to GL revenue YTD).
- [x] COS tie-out fix: added `Tax Expense` line (maps to `GL_ACCT_D[COSTOFSALES_SUBCATEGORY] = \"TAX EXPENSE\"`).
- [x] Clamp extreme budget % variance when abs(budget) < $1,000 (Ops Expense budget near 0).
- [ ] (Optional) Add SVG columns using the IBCS UDFs once the numeric matrix is stable.

## 7) Power Query (M) Readiness
- Ensure the M expressions required by the curated stream facts are present and stable.
- Keep M changes minimal and folding-friendly where possible.
- Note: Desktop “Apply changes” behavior can be finicky; prefer PBIP-defined tables for durability.

## 8) Verification Checklist (MCP)
- Reconnect via Modeling MCP after any reopen (Desktop port changes).
- [x] Run representative DAX validations:
  - Row counts for each stream fact + combined fact
  - Min/max Month for each stream and combined
  - Sanity totals for `[Revenue]`, `[Cost]`, `[GP]`, `[GL Revenue]`
  - Cross-check Projects-only totals vs “Amend” baseline visual (where applicable)
- [x] If MCP starts returning `Transport closed`, reconnect (or restart the Modeling MCP server) before continuing.

## 9) De-scope / Remove Redundancies (Later)
- Identify and remove redundant computed tables that were useful for exploration but not needed in the final model:
  - `CustomerMonth_Stream_Method_F`
  - `DivisionMonth_Stream_Method_F`
  - Any other “method selection” intermediate tables once `FINANCIALS_F` is canonical
