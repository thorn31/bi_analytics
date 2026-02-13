# Measure Folder Mapping Proposal

## Scope
- Source model: `PBIDesktop-Revenue and Retention_Unlaligned 2-11-2026-60285`
- Total measures inventoried: `238`
- Full nested folder paths inventoried: `72`

## Mapping Rules
- Keep business logic in domain folders (`1`, `2`, `3`, `4`, `6`).
- Keep section `6` visible (per request).
- Use section `5. UI` only for cross-domain presentation assets:
  - sparklines
  - color/conditional-formatting outputs
  - explanatory/doc text measures
- Keep domain-specific labels/trends with their domain metric family where practical.
- Keep `8. Deprecated` and `9. Not Implemented` structurally unchanged in this proposal.

## Folder-Level Mapping (Current -> Proposed)
| Current Folder | Proposed Folder | Notes |
|---|---|---|
| 1. GL Financials\\1. Revenue | 1. GL Financials\\1. Revenue | Keep |
| 1. GL Financials\\1. Revenue\\5. Budget | 1. GL Financials\\1. Revenue\\5. Budget | Keep |
| 1. GL Financials\\1. Revenue\\5. Budget\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\5. Budget\\7. Time Intelligence | Keep |
| 1. GL Financials\\1. Revenue\\6. Variance | 1. GL Financials\\1. Revenue\\6. Variance | Keep |
| 1. GL Financials\\1. Revenue\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\7. Time Intelligence | Keep |
| 1. GL Financials\\2. Cost | 1. GL Financials\\2. Cost | Keep |
| 1. GL Financials\\3. Gross Profit | 1. GL Financials\\3. Gross Profit | Keep |
| 1. GL Financials\\3. Gross Profit\\6. Variance | 1. GL Financials\\3. Gross Profit\\6. Variance | Keep |
| 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | Keep |
| 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep |
| 1. GL Financials\\4. P&L\\2. Period | 1. GL Financials\\4. P&L\\2. Period | Keep |
| 2. Customer Financials\\1. Revenue | 2. Customer Financials\\1. Revenue | Keep |
| 2. Customer Financials\\1. Revenue\\6. Variance\\FY As Of | 2. Customer Financials\\1. Revenue\\6. Variance\\FY As Of | Keep |
| 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\FY As Of | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\FY As Of | Keep |
| 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\Period | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\Period | Keep |
| 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of | Keep |
| 2. Customer Financials\\1. Revenue\\By Stream | 2. Customer Financials\\1. Revenue\\By Stream | Keep |
| 2. Customer Financials\\1. Revenue\\Streams | 2. Customer Financials\\1. Revenue\\Streams | Keep |
| 2. Customer Financials\\1. Revenue\\Time Intelligence | 2. Customer Financials\\1. Revenue\\Time Intelligence | Keep |
| 2. Customer Financials\\2. Cost | 2. Customer Financials\\2. Cost | Keep |
| 2. Customer Financials\\2. Cost\\By Stream | 2. Customer Financials\\2. Cost\\By Stream | Keep |
| 2. Customer Financials\\2. Cost\\Streams | 2. Customer Financials\\2. Cost\\Streams | Keep |
| 2. Customer Financials\\3. Gross Profit | 2. Customer Financials\\3. Gross Profit | Keep |
| 2. Customer Financials\\3. Gross Profit\\6. Variance\\FY As Of | 2. Customer Financials\\3. Gross Profit\\6. Variance\\FY As Of | Keep |
| 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\FY As Of | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\FY As Of | Keep |
| 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\R12M As Of | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\R12M As Of | Keep |
| 2. Customer Financials\\3. Gross Profit\\By Stream | 2. Customer Financials\\3. Gross Profit\\By Stream | Keep |
| 2. Customer Financials\\3. Gross Profit\\Streams | 2. Customer Financials\\3. Gross Profit\\Streams | Keep |
| 2. Customer Financials\\3. Gross Profit\\Time Intelligence | 2. Customer Financials\\3. Gross Profit\\Time Intelligence | Keep |
| 3. Retention (Service Contracts)\\R12M As Of\\Base | 3. Retention (Service Contracts)\\R12M As Of\\Base | Keep |
| 3. Retention (Service Contracts)\\R12M As Of\\Components | 3. Retention (Service Contracts)\\R12M As Of\\Components | Keep |
| 3. Retention (Service Contracts)\\R12M As Of\\KPIs | 3. Retention (Service Contracts)\\R12M As Of\\KPIs | Keep |
| 4. Customer Metrics\\4.1 Profile | 4. Customer Metrics\\4.1 Profile | Keep |
| 4. Customer Metrics\\4.2 Rank | 4. Customer Metrics\\4.2 Rank | Keep |
| 4. Customer Metrics\\4.3 NPS | 4. Customer Metrics\\4.3 NPS | Keep |
| 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep |
| 4. Time Intelligence\\4.1 R12M As Of\\Helpers | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Labels | Move |
| 4. Time Intelligence\\4.1 R12M As Of\\Revenue\\Mix | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Mix | Move |
| 4. Time Intelligence\\4.1 R12M As Of\\Revenue\\Streams | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Streams | Move |
| 5. Retention\\5.4 R12M As Of\\5.4.0 Documentation | 5. UI\\Retention\\Documentation | Move |
| 5. Retention\\5.4 R12M As Of\\5.4.3 KPIs\\GRR | 3. Retention (Service Contracts)\\R12M As Of\\KPIs\\GRR (numeric), 3. Retention (Service Contracts)\\R12M As Of\\KPIs\\GRR\\Labels (text) | Split |
| 5. Retention\\5.4 R12M As Of\\5.4.3 KPIs\\NRR | 3. Retention (Service Contracts)\\R12M As Of\\KPIs\\NRR (numeric), 3. Retention (Service Contracts)\\R12M As Of\\KPIs\\NRR\\Labels (text) | Split |
| 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo (numeric), 3. Retention (Service Contracts)\\R12M As Of\\Logo\\Labels (text) | Split |
| 5. Retention\\5.4 R12M As Of\\5.4.5 Waterfall | 3. Retention (Service Contracts)\\R12M As Of\\Waterfall | Move |
| 5. Retention\\5.4 R12M As Of\\5.4.6 Classification | 3. Retention (Service Contracts)\\R12M As Of\\Classification | Move |
| 5. Retention\\5.4 R12M As Of\\5.4.7 Sparklines | 5. UI\\Retention\\Sparklines | Move |
| 5. UI\\5.1 Customer Financials | 2. Customer Financials\\1. Revenue\\8. Labels (revenue), 2. Customer Financials\\3. Gross Profit\\8. Labels (GP) | Split |
| 5. UI\\5.1 Customer Financials\\R12M As Of | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Labels, 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\R12M As Of\\Labels | Split |
| 5. UI\\Customer Metrics | 4. Customer Metrics\\4.2 Rank\\Labels | Move |
| 5. UI\\GL Financials | 1. GL Financials\\1. Revenue\\6. Variance\\Labels, 1. GL Financials\\3. Gross Profit\\6. Variance\\Labels | Split |
| 6. Customer Experience\\6.0 Helpers | 6. Customer Experience\\6.0 Helpers | Keep |
| 6. Customer Experience\\6.1 NPS | 6. Customer Experience\\6.1 NPS | Keep |
| 6. Customer Experience\\6.1 NPS\\R12M | 6. Customer Experience\\6.1 NPS\\R12M | Keep |
| 6. Customer Experience\\6.2 Service Quality | 6. Customer Experience\\6.2 Service Quality | Keep |
| 6. Customer Status\\6.0 UI | 6. Customer Status\\6.0 UI | Keep |
| 6. Customer Status\\6.1 Helpers | 6. Customer Status\\6.1 Helpers | Keep |
| 6. Customer Status\\6.2 Contract | 6. Customer Status\\6.2 Contract | Keep |
| 6. Customer Status\\6.3 Projects | 6. Customer Status\\6.3 Projects | Keep |
| 6. Helper\\GL Financials\\Anchors | 6. Helper\\GL Financials\\Anchors | Keep |
| 6. Helper\\Misc | 6. Helper\\Misc | Keep |
| 6. Helper\\Retention\\Anchors | 6. Helper\\Retention\\Anchors | Keep |
| 6. Helper\\Retention\\R12M As Of | 6. Helper\\Retention\\R12M As Of | Keep |
| 6. Helper\\UI\\Active Items | 6. Helper\\UI\\Active Items | Keep |
| 7. Helper\\7.0 Date | 7. Helper\\7.0 Date | Keep |
| 7. Helper\\7.3 P&L\\YTD | 7. Helper\\7.3 P&L\\YTD | Keep |
| 7. Helper\\7.4 UI\\Conditional Formatting | 5. UI\\Conditional Formatting (color outputs), otherwise keep | Partial |
| 8. Deprecated\\8.1 Retention\\FY Period\\Base | 8. Deprecated\\8.1 Retention\\FY Period\\Base | Keep |
| 8. Deprecated\\8.1 Retention\\FY Period\\Components | 8. Deprecated\\8.1 Retention\\FY Period\\Components | Keep |
| 8. Deprecated\\8.1 Retention\\FY Period\\KPIs | 8. Deprecated\\8.1 Retention\\FY Period\\KPIs | Keep |
| 8. Deprecated\\8.1 Sandbox\\GL Financials | 8. Deprecated\\8.1 Sandbox\\GL Financials | Keep |
| 8. Deprecated\\Customer Financials\\Base | 8. Deprecated\\Customer Financials\\Base | Keep |
| 9. Not Implemented\\9.2 Operations | 9. Not Implemented\\9.2 Operations | Keep |

## Measure-Level Full Mapping (238 rows)
| Measure | Current Folder | Proposed Folder | Move Reason |
|---|---|---|---|
| GL Revenue | 1. GL Financials\\1. Revenue | 1. GL Financials\\1. Revenue | Keep: Domain business logic |
| GL Revenue (Projects - Amend Markets) | 1. GL Financials\\1. Revenue | 1. GL Financials\\1. Revenue | Keep: Domain business logic |
| GL Revenue (Projects) | 1. GL Financials\\1. Revenue | 1. GL Financials\\1. Revenue | Keep: Domain business logic |
| GL Revenue (Service Contracts) | 1. GL Financials\\1. Revenue | 1. GL Financials\\1. Revenue | Keep: Domain business logic |
| GL Revenue (T&M) | 1. GL Financials\\1. Revenue | 1. GL Financials\\1. Revenue | Keep: Domain business logic |
| GL Budget Revenue | 1. GL Financials\\1. Revenue\\5. Budget | 1. GL Financials\\1. Revenue\\5. Budget | Keep: Domain business logic |
| GL Budget Revenue (Projects) | 1. GL Financials\\1. Revenue\\5. Budget | 1. GL Financials\\1. Revenue\\5. Budget | Keep: Domain business logic |
| GL Budget Revenue (Selected Stream) | 1. GL Financials\\1. Revenue\\5. Budget | 1. GL Financials\\1. Revenue\\5. Budget | Keep: Domain business logic |
| GL Budget Revenue (Service Contracts) | 1. GL Financials\\1. Revenue\\5. Budget | 1. GL Financials\\1. Revenue\\5. Budget | Keep: Domain business logic |
| GL Budget Revenue (T&M) | 1. GL Financials\\1. Revenue\\5. Budget | 1. GL Financials\\1. Revenue\\5. Budget | Keep: Domain business logic |
| GL Budget Revenue FYTD (As Of) | 1. GL Financials\\1. Revenue\\5. Budget\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\5. Budget\\7. Time Intelligence | Keep: Domain business logic |
| GL Budget Revenue FYTD PY (As Of) | 1. GL Financials\\1. Revenue\\5. Budget\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\5. Budget\\7. Time Intelligence | Keep: Domain business logic |
| GL Revenue PY (Period) | 1. GL Financials\\1. Revenue\\6. Variance | 1. GL Financials\\1. Revenue\\6. Variance | Keep: Domain business logic |
| GL Revenue vs Budget % (FYTD) | 1. GL Financials\\1. Revenue\\6. Variance | 1. GL Financials\\1. Revenue\\6. Variance | Keep: Domain business logic |
| GL Revenue vs Budget (FYTD) | 1. GL Financials\\1. Revenue\\6. Variance | 1. GL Financials\\1. Revenue\\6. Variance | Keep: Domain business logic |
| GL Revenue Δ vs PY % (FYTD) | 1. GL Financials\\1. Revenue\\6. Variance | 1. GL Financials\\1. Revenue\\6. Variance | Keep: Domain business logic |
| GL Revenue Δ vs PY % (Period) | 1. GL Financials\\1. Revenue\\6. Variance | 1. GL Financials\\1. Revenue\\6. Variance | Keep: Domain business logic |
| GL Revenue Δ vs PY (FYTD) | 1. GL Financials\\1. Revenue\\6. Variance | 1. GL Financials\\1. Revenue\\6. Variance | Keep: Domain business logic |
| GL Revenue (Cumulative FYTD) | 1. GL Financials\\1. Revenue\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\7. Time Intelligence | Keep: Domain business logic |
| GL Revenue (Monthly) | 1. GL Financials\\1. Revenue\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\7. Time Intelligence | Keep: Domain business logic |
| GL Revenue (Monthly/Cumulative) | 1. GL Financials\\1. Revenue\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\7. Time Intelligence | Keep: Domain business logic |
| GL Revenue (Selected Stream) | 1. GL Financials\\1. Revenue\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\7. Time Intelligence | Keep: Domain business logic |
| GL Revenue FYTD (As Of) | 1. GL Financials\\1. Revenue\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\7. Time Intelligence | Keep: Domain business logic |
| GL Revenue FYTD PY (As Of) | 1. GL Financials\\1. Revenue\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\7. Time Intelligence | Keep: Domain business logic |
| GL Revenue PY (Monthly/Cumulative) | 1. GL Financials\\1. Revenue\\7. Time Intelligence | 1. GL Financials\\1. Revenue\\7. Time Intelligence | Keep: Domain business logic |
| GL Cost of Sales | 1. GL Financials\\2. Cost | 1. GL Financials\\2. Cost | Keep: Domain business logic |
| GL Cost of Sales (Projects) | 1. GL Financials\\2. Cost | 1. GL Financials\\2. Cost | Keep: Domain business logic |
| GL Cost of Sales (Service Contracts) | 1. GL Financials\\2. Cost | 1. GL Financials\\2. Cost | Keep: Domain business logic |
| GL Cost of Sales (T&M) | 1. GL Financials\\2. Cost | 1. GL Financials\\2. Cost | Keep: Domain business logic |
| GL Gross Profit | 1. GL Financials\\3. Gross Profit | 1. GL Financials\\3. Gross Profit | Keep: Domain business logic |
| GL Gross Profit (Projects) | 1. GL Financials\\3. Gross Profit | 1. GL Financials\\3. Gross Profit | Keep: Domain business logic |
| GL Gross Profit (Service Contracts) | 1. GL Financials\\3. Gross Profit | 1. GL Financials\\3. Gross Profit | Keep: Domain business logic |
| GL Gross Profit (T&M) | 1. GL Financials\\3. Gross Profit | 1. GL Financials\\3. Gross Profit | Keep: Domain business logic |
| GL Gross Profit PY (Period) | 1. GL Financials\\3. Gross Profit\\6. Variance | 1. GL Financials\\3. Gross Profit\\6. Variance | Keep: Domain business logic |
| GL Gross Profit Δ vs PY % (FYTD) | 1. GL Financials\\3. Gross Profit\\6. Variance | 1. GL Financials\\3. Gross Profit\\6. Variance | Keep: Domain business logic |
| GL Gross Profit Δ vs PY % (Period) | 1. GL Financials\\3. Gross Profit\\6. Variance | 1. GL Financials\\3. Gross Profit\\6. Variance | Keep: Domain business logic |
| GL Gross Profit Δ vs PY (FYTD) | 1. GL Financials\\3. Gross Profit\\6. Variance | 1. GL Financials\\3. Gross Profit\\6. Variance | Keep: Domain business logic |
| GL Gross Profit (Cumulative FYTD) | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | Keep: Domain business logic |
| GL Gross Profit (Monthly) | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | Keep: Domain business logic |
| GL Gross Profit (Monthly/Cumulative) | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | Keep: Domain business logic |
| GL Gross Profit (Selected Stream) | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | Keep: Domain business logic |
| GL Gross Profit FYTD (As Of) | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | Keep: Domain business logic |
| GL Gross Profit FYTD PY (As Of) | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | Keep: Domain business logic |
| GL Gross Profit PY (Monthly/Cumulative) | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | 1. GL Financials\\3. Gross Profit\\7. Time Intelligence | Keep: Domain business logic |
| P&L % of Revenue (YTD) | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L % of Revenue Budget (YTD) | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L % of Revenue PY (YTD) | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L Amount (YTD) | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L Amount PY (YTD) | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L Budget Amount (YTD) | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L Divider | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L Operator | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L Var vs Budget $ (YTD) | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L Var vs Budget % (YTD) | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L Var vs PY $ (YTD) | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L Var vs PY % (YTD) | 1. GL Financials\\4. P&L\\1. YTD | 1. GL Financials\\4. P&L\\1. YTD | Keep: Domain business logic |
| P&L Gross Profit | 1. GL Financials\\4. P&L\\2. Period | 1. GL Financials\\4. P&L\\2. Period | Keep: Domain business logic |
| P&L Gross Profit Budget | 1. GL Financials\\4. P&L\\2. Period | 1. GL Financials\\4. P&L\\2. Period | Keep: Domain business logic |
| P&L Gross Profit PY | 1. GL Financials\\4. P&L\\2. Period | 1. GL Financials\\4. P&L\\2. Period | Keep: Domain business logic |
| P&L Net Profit | 1. GL Financials\\4. P&L\\2. Period | 1. GL Financials\\4. P&L\\2. Period | Keep: Domain business logic |
| P&L Net Profit Budget | 1. GL Financials\\4. P&L\\2. Period | 1. GL Financials\\4. P&L\\2. Period | Keep: Domain business logic |
| P&L Net Profit PY | 1. GL Financials\\4. P&L\\2. Period | 1. GL Financials\\4. P&L\\2. Period | Keep: Domain business logic |
| Total Revenue | 2. Customer Financials\\1. Revenue | 2. Customer Financials\\1. Revenue | Keep: Domain business logic |
| Total Revenue YoY % (FY As Of) | 2. Customer Financials\\1. Revenue\\6. Variance\\FY As Of | 2. Customer Financials\\1. Revenue\\6. Variance\\FY As Of | Keep: Domain business logic |
| Total Revenue YoY Δ (FY As Of) | 2. Customer Financials\\1. Revenue\\6. Variance\\FY As Of | 2. Customer Financials\\1. Revenue\\6. Variance\\FY As Of | Keep: Domain business logic |
| Total Revenue (FY As Of) | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\FY As Of | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\FY As Of | Keep: Domain business logic |
| Total Revenue PY (FY As Of) | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\FY As Of | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\FY As Of | Keep: Domain business logic |
| Total Revenue PY | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\Period | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\Period | Keep: Domain business logic |
| Revenue Momentum % (R12M vs PY) | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of | Keep: Domain business logic |
| Total Revenue (R12M As Of) | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of | Keep: Domain business logic |
| Total Revenue PY (R12M As Of) | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of | Keep: Domain business logic |
| Revenue (By Stream) | 2. Customer Financials\\1. Revenue\\By Stream | 2. Customer Financials\\1. Revenue\\By Stream | Keep: Domain business logic |
| Project Revenue | 2. Customer Financials\\1. Revenue\\Streams | 2. Customer Financials\\1. Revenue\\Streams | Keep: Domain business logic |
| Service Contract Revenue | 2. Customer Financials\\1. Revenue\\Streams | 2. Customer Financials\\1. Revenue\\Streams | Keep: Domain business logic |
| T&M Revenue | 2. Customer Financials\\1. Revenue\\Streams | 2. Customer Financials\\1. Revenue\\Streams | Keep: Domain business logic |
| Revenue PY (Dynamic) | 2. Customer Financials\\1. Revenue\\Time Intelligence | 2. Customer Financials\\1. Revenue\\Time Intelligence | Keep: Domain business logic |
| Total Cost | 2. Customer Financials\\2. Cost | 2. Customer Financials\\2. Cost | Keep: Domain business logic |
| Cost (By Stream) | 2. Customer Financials\\2. Cost\\By Stream | 2. Customer Financials\\2. Cost\\By Stream | Keep: Domain business logic |
| Project Cost | 2. Customer Financials\\2. Cost\\Streams | 2. Customer Financials\\2. Cost\\Streams | Keep: Domain business logic |
| Service Contract Cost | 2. Customer Financials\\2. Cost\\Streams | 2. Customer Financials\\2. Cost\\Streams | Keep: Domain business logic |
| T&M Cost | 2. Customer Financials\\2. Cost\\Streams | 2. Customer Financials\\2. Cost\\Streams | Keep: Domain business logic |
| Total GP % | 2. Customer Financials\\3. Gross Profit | 2. Customer Financials\\3. Gross Profit | Keep: Domain business logic |
| Total Gross Profit | 2. Customer Financials\\3. Gross Profit | 2. Customer Financials\\3. Gross Profit | Keep: Domain business logic |
| Total Gross Profit YoY % (FY As Of) | 2. Customer Financials\\3. Gross Profit\\6. Variance\\FY As Of | 2. Customer Financials\\3. Gross Profit\\6. Variance\\FY As Of | Keep: Domain business logic |
| Total Gross Profit YoY Δ (FY As Of) | 2. Customer Financials\\3. Gross Profit\\6. Variance\\FY As Of | 2. Customer Financials\\3. Gross Profit\\6. Variance\\FY As Of | Keep: Domain business logic |
| Total GP % (FY As Of) | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\FY As Of | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\FY As Of | Keep: Domain business logic |
| Total Gross Profit (FY As Of) | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\FY As Of | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\FY As Of | Keep: Domain business logic |
| Total Gross Profit PY (FY As Of) | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\FY As Of | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\FY As Of | Keep: Domain business logic |
| Total GP % (R12M As Of) | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\R12M As Of | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\R12M As Of | Keep: Domain business logic |
| Total GP % PY (R12M As Of) | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\R12M As Of | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\R12M As Of | Keep: Domain business logic |
| Total Gross Profit (R12M As Of) | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\R12M As Of | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\R12M As Of | Keep: Domain business logic |
| GP % (By Stream) | 2. Customer Financials\\3. Gross Profit\\By Stream | 2. Customer Financials\\3. Gross Profit\\By Stream | Keep: Domain business logic |
| Gross Profit (By Stream) | 2. Customer Financials\\3. Gross Profit\\By Stream | 2. Customer Financials\\3. Gross Profit\\By Stream | Keep: Domain business logic |
| Project GP | 2. Customer Financials\\3. Gross Profit\\Streams | 2. Customer Financials\\3. Gross Profit\\Streams | Keep: Domain business logic |
| Service Contract Gross Profit | 2. Customer Financials\\3. Gross Profit\\Streams | 2. Customer Financials\\3. Gross Profit\\Streams | Keep: Domain business logic |
| Service Contract Gross Profit % | 2. Customer Financials\\3. Gross Profit\\Streams | 2. Customer Financials\\3. Gross Profit\\Streams | Keep: Domain business logic |
| T&M Gross Profit | 2. Customer Financials\\3. Gross Profit\\Streams | 2. Customer Financials\\3. Gross Profit\\Streams | Keep: Domain business logic |
| Total Gross Profit PY | 2. Customer Financials\\3. Gross Profit\\Time Intelligence | 2. Customer Financials\\3. Gross Profit\\Time Intelligence | Keep: Domain business logic |
| Service Contract Revenue (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\Base | 3. Retention (Service Contracts)\\R12M As Of\\Base | Keep: Domain business logic |
| Service Contract Revenue PY (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\Base | 3. Retention (Service Contracts)\\R12M As Of\\Base | Keep: Domain business logic |
| Churn Revenue % (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\Components | 3. Retention (Service Contracts)\\R12M As Of\\Components | Keep: Domain business logic |
| Churn Revenue (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\Components | 3. Retention (Service Contracts)\\R12M As Of\\Components | Keep: Domain business logic |
| Contraction Revenue % (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\Components | 3. Retention (Service Contracts)\\R12M As Of\\Components | Keep: Domain business logic |
| Contraction Revenue (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\Components | 3. Retention (Service Contracts)\\R12M As Of\\Components | Keep: Domain business logic |
| Retention Base PY (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\Components | 3. Retention (Service Contracts)\\R12M As Of\\Components | Keep: Domain business logic |
| Upsell Revenue % (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\Components | 3. Retention (Service Contracts)\\R12M As Of\\Components | Keep: Domain business logic |
| Upsell Revenue (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\Components | 3. Retention (Service Contracts)\\R12M As Of\\Components | Keep: Domain business logic |
| Churn Rate % (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\KPIs | 3. Retention (Service Contracts)\\R12M As Of\\KPIs | Keep: Domain business logic |
| Gross Revenue Retention % (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\KPIs | 3. Retention (Service Contracts)\\R12M As Of\\KPIs | Keep: Domain business logic |
| Net Revenue Retention % (R12M As Of) | 3. Retention (Service Contracts)\\R12M As Of\\KPIs | 3. Retention (Service Contracts)\\R12M As Of\\KPIs | Keep: Domain business logic |
| Customer Profile Metric Value | 4. Customer Metrics\\4.1 Profile | 4. Customer Metrics\\4.1 Profile | Keep: Domain business logic |
| Customer Revenue Rank (All Time) | 4. Customer Metrics\\4.2 Rank | 4. Customer Metrics\\4.2 Rank | Keep: Domain business logic |
| Customer Revenue Rank (R12M As Of) | 4. Customer Metrics\\4.2 Rank | 4. Customer Metrics\\4.2 Rank | Keep: Domain business logic |
| Industrial Revenue Rank | 4. Customer Metrics\\4.2 Rank | 4. Customer Metrics\\4.2 Rank | Keep: Domain business logic |
| Industrial Revenue Rank (R12M As Of) | 4. Customer Metrics\\4.2 Rank | 4. Customer Metrics\\4.2 Rank | Keep: Domain business logic |
| Net Promoter Score (R12M) | 4. Customer Metrics\\4.3 NPS | 4. Customer Metrics\\4.3 NPS | Keep: Domain business logic |
| Active Item % Complete | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Item Contract Value | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Item End Date | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Item Estimated Cost | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Item Revenue (ITD) | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Item Revenue (R12M As Of) | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Item Sold GP % | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Item Start Date | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Items Total Cost | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Items Total GP % | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Items Total Gross Profit | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Items Total Revenue | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| Active Items Total Revenue (ITD) | 4. Customer Metrics\\Active Items | 4. Customer Metrics\\Active Items | Keep: Domain business logic |
| R12M Period Label | 4. Time Intelligence\\4.1 R12M As Of\\Helpers | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Labels | Move: consolidate TI under customer revenue |
| Recurring Mix % (SC) (R12M) | 4. Time Intelligence\\4.1 R12M As Of\\Revenue\\Mix | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Mix | Move: consolidate TI under customer revenue |
| Revenue Stream Share Fill (R12M) | 4. Time Intelligence\\4.1 R12M As Of\\Revenue\\Mix | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Mix | Move: consolidate TI under customer revenue |
| Stream Concentration % (R12M) | 4. Time Intelligence\\4.1 R12M As Of\\Revenue\\Mix | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Mix | Move: consolidate TI under customer revenue |
| Project Revenue (R12M As Of) | 4. Time Intelligence\\4.1 R12M As Of\\Revenue\\Streams | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Streams | Move: consolidate TI under customer revenue |
| SC Revenue (R12M As Of) | 4. Time Intelligence\\4.1 R12M As Of\\Revenue\\Streams | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Streams | Move: consolidate TI under customer revenue |
| T&M Revenue (R12M As Of) | 4. Time Intelligence\\4.1 R12M As Of\\Revenue\\Streams | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Streams | Move: consolidate TI under customer revenue |
| NRR Logic Explanation.MD | 5. Retention\\5.4 R12M As Of\\5.4.0 Documentation | 5. UI\\Retention\\Documentation | Move: presentation/documentation text |
| Gross Revenue Retention % PY (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.3 KPIs\\GRR | 3. Retention (Service Contracts)\\R12M As Of\\KPIs\\GRR | Move: retention KPI logic |
| Gross Revenue Retention Trend vs PY (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.3 KPIs\\GRR | 3. Retention (Service Contracts)\\R12M As Of\\KPIs\\GRR\\Labels | Move: domain-specific label |
| Net Revenue Retention % PY (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.3 KPIs\\NRR | 3. Retention (Service Contracts)\\R12M As Of\\KPIs\\NRR | Move: retention KPI logic |
| Net Revenue Retention Trend vs PY (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.3 KPIs\\NRR | 3. Retention (Service Contracts)\\R12M As Of\\KPIs\\NRR\\Labels | Move: domain-specific label |
| Customers Churned (SC) (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| Customers Contraction (SC) (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| Customers CY (SC) (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| Customers PY (SC) (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| Customers Retained (SC) (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| Customers Upsell (SC) (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| Logo Churn % (SC) (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| Logo Churn Count (SC) (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| Logo Retention % (SC) (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| Logo Retention % (SC) PY (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| Logo Retention Trend (SC) vs PY (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo\\Labels | Move: domain-specific label |
| Retention Base Count PY (SC) (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.4 Logo (SC) | 3. Retention (Service Contracts)\\R12M As Of\\Logo | Move: retention logo logic |
| NRR Waterfall Value | 5. Retention\\5.4 R12M As Of\\5.4.5 Waterfall | 3. Retention (Service Contracts)\\R12M As Of\\Waterfall | Move: retention logic |
| NRR Waterfall Value (R12M As Of) | 5. Retention\\5.4 R12M As Of\\5.4.5 Waterfall | 3. Retention (Service Contracts)\\R12M As Of\\Waterfall | Move: retention logic |
| Customer Retention Category (R12M) | 5. Retention\\5.4 R12M As Of\\5.4.6 Classification | 3. Retention (Service Contracts)\\R12M As Of\\Classification | Move: retention logic |
| GRR Sparkline (SVG) | 5. Retention\\5.4 R12M As Of\\5.4.7 Sparklines | 5. UI\\Retention\\Sparklines | Move: cross-domain UI output |
| Logo Sparkline (SVG) | 5. Retention\\5.4 R12M As Of\\5.4.7 Sparklines | 5. UI\\Retention\\Sparklines | Move: cross-domain UI output |
| NRR Sparkline (SVG) | 5. Retention\\5.4 R12M As Of\\5.4.7 Sparklines | 5. UI\\Retention\\Sparklines | Move: cross-domain UI output |
| Total Gross Profit Trend vs PY | 5. UI\\5.1 Customer Financials | 2. Customer Financials\\3. Gross Profit\\8. Labels | Move: domain-specific label |
| Total Revenue Trend vs PY | 5. UI\\5.1 Customer Financials | 2. Customer Financials\\1. Revenue\\8. Labels | Move: domain-specific label |
| Total GP % Trend vs PY (R12M As Of) | 5. UI\\5.1 Customer Financials\\R12M As Of | 2. Customer Financials\\3. Gross Profit\\7. Time Intelligence\\R12M As Of\\Labels | Move: domain-specific label |
| Total Revenue Trend vs PY (R12M As Of) | 5. UI\\5.1 Customer Financials\\R12M As Of | 2. Customer Financials\\1. Revenue\\7. Time Intelligence\\R12M As Of\\Labels | Move: domain-specific label |
| Customer Rank Context String | 5. UI\\Customer Metrics | 4. Customer Metrics\\4.2 Rank\\Labels | Move: domain-specific label |
| Customer Rank Context String (R12M As Of) | 5. UI\\Customer Metrics | 4. Customer Metrics\\4.2 Rank\\Labels | Move: domain-specific label |
| Industrial Rank Context String | 5. UI\\Customer Metrics | 4. Customer Metrics\\4.2 Rank\\Labels | Move: domain-specific label |
| Industrial Rank Context String (R12M As Of) | 5. UI\\Customer Metrics | 4. Customer Metrics\\4.2 Rank\\Labels | Move: domain-specific label |
| GL Gross Profit Δ vs PY % (Period) Label | 5. UI\\GL Financials | 1. GL Financials\\3. Gross Profit\\6. Variance\\Labels | Move: domain-specific label |
| GL Revenue Δ vs PY % (Period) Label | 5. UI\\GL Financials | 1. GL Financials\\1. Revenue\\6. Variance\\Labels | Move: domain-specific label |
| Debug - NPS R12M Start Date | 6. Customer Experience\\6.0 Helpers | 6. Customer Experience\\6.0 Helpers | Keep: section 6 remains visible |
| Last NPS Date | 6. Customer Experience\\6.0 Helpers | 6. Customer Experience\\6.0 Helpers | Keep: section 6 remains visible |
| Avg NPS Rating | 6. Customer Experience\\6.1 NPS | 6. Customer Experience\\6.1 NPS | Keep: section 6 remains visible |
| Detractors Count | 6. Customer Experience\\6.1 NPS | 6. Customer Experience\\6.1 NPS | Keep: section 6 remains visible |
| Net Promoter Score | 6. Customer Experience\\6.1 NPS | 6. Customer Experience\\6.1 NPS | Keep: section 6 remains visible |
| NPS Response Count | 6. Customer Experience\\6.1 NPS | 6. Customer Experience\\6.1 NPS | Keep: section 6 remains visible |
| Promoters Count | 6. Customer Experience\\6.1 NPS | 6. Customer Experience\\6.1 NPS | Keep: section 6 remains visible |
| Net Promoter Score PY (R12M) | 6. Customer Experience\\6.1 NPS\\R12M | 6. Customer Experience\\6.1 NPS\\R12M | Keep: section 6 remains visible |
| Net Promoter Score Trend vs PY | 6. Customer Experience\\6.1 NPS\\R12M | 6. Customer Experience\\6.1 NPS\\R12M | Keep: section 6 remains visible |
| First Time Fix Rate | 6. Customer Experience\\6.2 Service Quality | 6. Customer Experience\\6.2 Service Quality | Keep: section 6 remains visible |
| Prompt and On Time % | 6. Customer Experience\\6.2 Service Quality | 6. Customer Experience\\6.2 Service Quality | Keep: section 6 remains visible |
| Customer Has Revenue | 6. Customer Status\\6.0 UI | 6. Customer Status\\6.0 UI | Keep: section 6 remains visible |
| Customer Status | 6. Customer Status\\6.0 UI | 6. Customer Status\\6.0 UI | Keep: section 6 remains visible |
| Selected Customer Name | 6. Customer Status\\6.0 UI | 6. Customer Status\\6.0 UI | Keep: section 6 remains visible |
| Customer Lifecycle Status | 6. Customer Status\\6.1 Helpers | 6. Customer Status\\6.1 Helpers | Keep: section 6 remains visible |
| Last Billing Date (Any Stream) | 6. Customer Status\\6.1 Helpers | 6. Customer Status\\6.1 Helpers | Keep: section 6 remains visible |
| Months Since Last Billing | 6. Customer Status\\6.1 Helpers | 6. Customer Status\\6.1 Helpers | Keep: section 6 remains visible |
| Active Contracts | 6. Customer Status\\6.2 Contract | 6. Customer Status\\6.2 Contract | Keep: section 6 remains visible |
| Contract Billing Period (Months Inclusive) | 6. Customer Status\\6.2 Contract | 6. Customer Status\\6.2 Contract | Keep: section 6 remains visible |
| First Contract Billing Date | 6. Customer Status\\6.2 Contract | 6. Customer Status\\6.2 Contract | Keep: section 6 remains visible |
| Last Contract Billing Date | 6. Customer Status\\6.2 Contract | 6. Customer Status\\6.2 Contract | Keep: section 6 remains visible |
| Active Projects | 6. Customer Status\\6.3 Projects | 6. Customer Status\\6.3 Projects | Keep: section 6 remains visible |
| Dashboard As Of Month End (FY) | 6. Helper\\GL Financials\\Anchors | 6. Helper\\GL Financials\\Anchors | Keep: section 6 remains visible |
| Placeholder v1 | 6. Helper\\Misc | 6. Helper\\Misc | Keep: section 6 remains visible |
| Placeholder v2 | 6. Helper\\Misc | 6. Helper\\Misc | Keep: section 6 remains visible |
| As Of Month End (SC) | 6. Helper\\Retention\\Anchors | 6. Helper\\Retention\\Anchors | Keep: section 6 remains visible |
| Last SC Data Month End (In Slice) | 6. Helper\\Retention\\Anchors | 6. Helper\\Retention\\Anchors | Keep: section 6 remains visible |
| Customer Retention Category (SC) (R12M As Of) | 6. Helper\\Retention\\R12M As Of | 6. Helper\\Retention\\R12M As Of | Keep: section 6 remains visible |
| Active Item Is Active (Flag) | 6. Helper\\UI\\Active Items | 6. Helper\\UI\\Active Items | Keep: section 6 remains visible |
| Active Item Show Row | 6. Helper\\UI\\Active Items | 6. Helper\\UI\\Active Items | Keep: section 6 remains visible |
| Active Items Has Rows (Flag) | 6. Helper\\UI\\Active Items | 6. Helper\\UI\\Active Items | Keep: section 6 remains visible |
| As Of Date (Financials) | 7. Helper\\7.0 Date | 7. Helper\\7.0 Date | Keep: technical helper |
| As Of Date (Revenue) | 7. Helper\\7.0 Date | 7. Helper\\7.0 Date | Keep: technical helper |
| As Of Month End (Financials) | 7. Helper\\7.0 Date | 7. Helper\\7.0 Date | Keep: technical helper |
| Debug – Anchor Date | 7. Helper\\7.0 Date | 7. Helper\\7.0 Date | Keep: technical helper |
| Debug - R12M End Date | 7. Helper\\7.0 Date | 7. Helper\\7.0 Date | Keep: technical helper |
| Selected Fiscal Year (Single) | 7. Helper\\7.0 Date | 7. Helper\\7.0 Date | Keep: technical helper |
| Selected FY End Date | 7. Helper\\7.0 Date | 7. Helper\\7.0 Date | Keep: technical helper |
| Selected FY Start Date | 7. Helper\\7.0 Date | 7. Helper\\7.0 Date | Keep: technical helper |
| P&L Amount (YTD) (Line) | 7. Helper\\7.3 P&L\\YTD | 7. Helper\\7.3 P&L\\YTD | Keep: technical helper |
| P&L Amount PY (YTD) (Line) | 7. Helper\\7.3 P&L\\YTD | 7. Helper\\7.3 P&L\\YTD | Keep: technical helper |
| P&L Budget Amount (YTD) (Line) | 7. Helper\\7.3 P&L\\YTD | 7. Helper\\7.3 P&L\\YTD | Keep: technical helper |
| P&L Row Sign | 7. Helper\\7.3 P&L\\YTD | 7. Helper\\7.3 P&L\\YTD | Keep: technical helper |
| Customer Lifecycle Status Color | 7. Helper\\7.4 UI\\Conditional Formatting | 5. UI\\Conditional Formatting | Move: cross-domain UI output |
| GRR % Δ vs PY (R12M As Of) | 7. Helper\\7.4 UI\\Conditional Formatting | 7. Helper\\7.4 UI\\Conditional Formatting | Keep: helper numeric delta |
| GRR Trend Color (R12M As Of) | 7. Helper\\7.4 UI\\Conditional Formatting | 5. UI\\Conditional Formatting | Move: cross-domain UI output |
| NRR % Δ vs PY (R12M As Of) | 7. Helper\\7.4 UI\\Conditional Formatting | 7. Helper\\7.4 UI\\Conditional Formatting | Keep: helper numeric delta |
| NRR Trend Color (R12M As Of) | 7. Helper\\7.4 UI\\Conditional Formatting | 5. UI\\Conditional Formatting | Move: cross-domain UI output |
| Revenue Trend Color (R12M As Of) | 7. Helper\\7.4 UI\\Conditional Formatting | 5. UI\\Conditional Formatting | Move: cross-domain UI output |
| Revenue Δ vs PY (R12M As Of) | 7. Helper\\7.4 UI\\Conditional Formatting | 7. Helper\\7.4 UI\\Conditional Formatting | Keep: helper numeric delta |
| Total GP % Trend Color (R12M As Of) | 7. Helper\\7.4 UI\\Conditional Formatting | 5. UI\\Conditional Formatting | Move: cross-domain UI output |
| Total GP % Δ vs PY (R12M As Of) | 7. Helper\\7.4 UI\\Conditional Formatting | 7. Helper\\7.4 UI\\Conditional Formatting | Keep: helper numeric delta |
| Service Contract Revenue PY (FY Period) | 8. Deprecated\\8.1 Retention\\FY Period\\Base | 8. Deprecated\\8.1 Retention\\FY Period\\Base | Keep: deprecated |
| Churn Revenue (FY Period) | 8. Deprecated\\8.1 Retention\\FY Period\\Components | 8. Deprecated\\8.1 Retention\\FY Period\\Components | Keep: deprecated |
| Contraction Revenue (FY Period) | 8. Deprecated\\8.1 Retention\\FY Period\\Components | 8. Deprecated\\8.1 Retention\\FY Period\\Components | Keep: deprecated |
| Retention Base PY (FY Period) | 8. Deprecated\\8.1 Retention\\FY Period\\Components | 8. Deprecated\\8.1 Retention\\FY Period\\Components | Keep: deprecated |
| Upsell Revenue (FY Period) | 8. Deprecated\\8.1 Retention\\FY Period\\Components | 8. Deprecated\\8.1 Retention\\FY Period\\Components | Keep: deprecated |
| Churn Rate % (FY Period) | 8. Deprecated\\8.1 Retention\\FY Period\\KPIs | 8. Deprecated\\8.1 Retention\\FY Period\\KPIs | Keep: deprecated |
| Gross Revenue Retention % (FY Period) | 8. Deprecated\\8.1 Retention\\FY Period\\KPIs | 8. Deprecated\\8.1 Retention\\FY Period\\KPIs | Keep: deprecated |
| Net Revenue Retention % (FY Period) | 8. Deprecated\\8.1 Retention\\FY Period\\KPIs | 8. Deprecated\\8.1 Retention\\FY Period\\KPIs | Keep: deprecated |
| GL Revenue (Projects - Sandbox) | 8. Deprecated\\8.1 Sandbox\\GL Financials | 8. Deprecated\\8.1 Sandbox\\GL Financials | Keep: deprecated |
| GL Revenue (Total - Sandbox) | 8. Deprecated\\8.1 Sandbox\\GL Financials | 8. Deprecated\\8.1 Sandbox\\GL Financials | Keep: deprecated |
| Cost | 8. Deprecated\\Customer Financials\\Base | 8. Deprecated\\Customer Financials\\Base | Keep: deprecated |
| Gross Profit | 8. Deprecated\\Customer Financials\\Base | 8. Deprecated\\Customer Financials\\Base | Keep: deprecated |
| Revenue | 8. Deprecated\\Customer Financials\\Base | 8. Deprecated\\Customer Financials\\Base | Keep: deprecated |
| Project Spend per Maintenance $ (TTM) | 9. Not Implemented\\9.2 Operations | 9. Not Implemented\\9.2 Operations | Keep: not implemented |
| T&M Spend per Maintenance $ (TTM) | 9. Not Implemented\\9.2 Operations | 9. Not Implemented\\9.2 Operations | Keep: not implemented |
| Total Project Spend per Total Maintenance $ (Snapshot) | 9. Not Implemented\\9.2 Operations | 9. Not Implemented\\9.2 Operations | Keep: not implemented |
| Total T&M Spend per Total Maintenance $ (Snapshot) | 9. Not Implemented\\9.2 Operations | 9. Not Implemented\\9.2 Operations | Keep: not implemented |

> Note: The remaining rows beyond those listed above are currently in stable domain folders and map 1:1 to the same folder with reason `Keep: Domain business logic`.
> This preserves complete coverage for all 238 measures while highlighting non-trivial move/split decisions.

## Recommended Execution Order (if approved later)
1. Move pure folder-level consolidations (no splits).
2. Move split folders by measure-level assignment (labels vs numeric).
3. Validate report visuals.
4. Optionally hide `8`/`9` when you're ready.
