# Measure Folder Mapping - V2 (Full Explicit Map)

## Final Section Order
1. `1. GL Financials`
2. `2. Customer Financials`
3. `3. Retention (Service Contracts)`
4. `4. Customer Metrics`
5. `5. Customer Experience`
6. `6. Customer Status`
7. `7. Helper`
8. `8. UI`
9. `9. Deprecated`
10. `10. Not Implemented`

## Scope
- Total mapped measures: `238`
- This table is fully explicit (one row per measure).

## Mapping Table
| Measure | Current Folder | Proposed Folder | Change Type | Reason |
|---|---|---|---|---|
| Active Contracts | `6. Customer Status\6.2 Contract` | `6. Customer Status\6.2 Contract` | Keep | Keep: unchanged |
| Active Item % Complete | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Item Contract Value | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Item End Date | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Item Estimated Cost | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Item Is Active (Flag) | `6. Helper\UI\Active Items` | `7. Helper\UI\Active Items` | Move | Move: section renumber |
| Active Item Revenue (ITD) | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Item Revenue (R12M As Of) | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Item Show Row | `6. Helper\UI\Active Items` | `7. Helper\UI\Active Items` | Move | Move: section renumber |
| Active Item Sold GP % | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Item Start Date | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Items Has Rows (Flag) | `6. Helper\UI\Active Items` | `7. Helper\UI\Active Items` | Move | Move: section renumber |
| Active Items Total Cost | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Items Total GP % | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Items Total Gross Profit | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Items Total Revenue | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Items Total Revenue (ITD) | `4. Customer Metrics\Active Items` | `4. Customer Metrics\Active Items` | Keep | Keep: unchanged |
| Active Projects | `6. Customer Status\6.3 Projects` | `6. Customer Status\6.3 Projects` | Keep | Keep: unchanged |
| As Of Date (Financials) | `7. Helper\7.0 Date` | `7. Helper\7.0 Date` | Keep | Keep: unchanged |
| As Of Date (Revenue) | `7. Helper\7.0 Date` | `7. Helper\7.0 Date` | Keep | Keep: unchanged |
| As Of Month End (Financials) | `7. Helper\7.0 Date` | `7. Helper\7.0 Date` | Keep | Keep: unchanged |
| As Of Month End (SC) | `6. Helper\Retention\Anchors` | `7. Helper\Retention\Anchors` | Move | Move: section renumber |
| Avg NPS Rating | `6. Customer Experience\6.1 NPS` | `5. Customer Experience\6.1 NPS` | Move | Move: section renumber |
| Churn Rate % (FY Period) | `8. Deprecated\8.1 Retention\FY Period\KPIs` | `9. Deprecated\8.1 Retention\FY Period\KPIs` | Move | Move: section renumber |
| Churn Rate % (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\KPIs` | `3. Retention (Service Contracts)\R12M As Of\KPIs` | Keep | Keep: unchanged |
| Churn Revenue % (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\Components` | `3. Retention (Service Contracts)\R12M As Of\Components` | Keep | Keep: unchanged |
| Churn Revenue (FY Period) | `8. Deprecated\8.1 Retention\FY Period\Components` | `9. Deprecated\8.1 Retention\FY Period\Components` | Move | Move: section renumber |
| Churn Revenue (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\Components` | `3. Retention (Service Contracts)\R12M As Of\Components` | Keep | Keep: unchanged |
| Contract Billing Period (Months Inclusive) | `6. Customer Status\6.2 Contract` | `6. Customer Status\6.2 Contract` | Keep | Keep: unchanged |
| Contraction Revenue % (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\Components` | `3. Retention (Service Contracts)\R12M As Of\Components` | Keep | Keep: unchanged |
| Contraction Revenue (FY Period) | `8. Deprecated\8.1 Retention\FY Period\Components` | `9. Deprecated\8.1 Retention\FY Period\Components` | Move | Move: section renumber |
| Contraction Revenue (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\Components` | `3. Retention (Service Contracts)\R12M As Of\Components` | Keep | Keep: unchanged |
| Cost | `8. Deprecated\Customer Financials\Base` | `9. Deprecated\Customer Financials\Base` | Move | Move: section renumber |
| Cost (By Stream) | `2. Customer Financials\2. Cost\By Stream` | `2. Customer Financials\2. Cost\By Stream` | Keep | Keep: unchanged |
| Customer Has Revenue | `6. Customer Status\6.0 UI` | `6. Customer Status\6.0 UI` | Keep | Keep: unchanged |
| Customer Lifecycle Status | `6. Customer Status\6.1 Helpers` | `6. Customer Status\6.1 Helpers` | Keep | Keep: unchanged |
| Customer Lifecycle Status Color | `7. Helper\7.4 UI\Conditional Formatting` | `8. UI\Conditional Formatting` | Move | Move: UI color output |
| Customer Profile Metric Value | `4. Customer Metrics\4.1 Profile` | `4. Customer Metrics\4.1 Profile` | Keep | Keep: unchanged |
| Customer Rank Context String | `5. UI\Customer Metrics` | `8. UI\Customer Metrics` | Move | Move: UI grouping |
| Customer Rank Context String (R12M As Of) | `5. UI\Customer Metrics` | `8. UI\Customer Metrics` | Move | Move: UI grouping |
| Customer Retention Category (R12M) | `5. Retention\5.4 R12M As Of\5.4.6 Classification` | `3. Retention (Service Contracts)\R12M As Of\Classification` | Move | Move: retention business logic |
| Customer Retention Category (SC) (R12M As Of) | `6. Helper\Retention\R12M As Of` | `7. Helper\Retention\R12M As Of` | Move | Move: section renumber |
| Customer Revenue Rank (All Time) | `4. Customer Metrics\4.2 Rank` | `4. Customer Metrics\4.2 Rank` | Keep | Keep: unchanged |
| Customer Revenue Rank (R12M As Of) | `4. Customer Metrics\4.2 Rank` | `4. Customer Metrics\4.2 Rank` | Keep | Keep: unchanged |
| Customer Status | `6. Customer Status\6.0 UI` | `6. Customer Status\6.0 UI` | Keep | Keep: unchanged |
| Customers CY (SC) (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Customers Churned (SC) (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Customers Contraction (SC) (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Customers PY (SC) (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Customers Retained (SC) (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Customers Upsell (SC) (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Dashboard As Of Month End (FY) | `6. Helper\GL Financials\Anchors` | `7. Helper\GL Financials\Anchors` | Move | Move: section renumber |
| Debug - NPS R12M Start Date | `6. Customer Experience\6.0 Helpers` | `5. Customer Experience\6.0 Helpers` | Move | Move: section renumber |
| Debug - R12M End Date | `7. Helper\7.0 Date` | `7. Helper\7.0 Date` | Keep | Keep: unchanged |
| Debug – Anchor Date | `7. Helper\7.0 Date` | `7. Helper\7.0 Date` | Keep | Keep: unchanged |
| Detractors Count | `6. Customer Experience\6.1 NPS` | `5. Customer Experience\6.1 NPS` | Move | Move: section renumber |
| First Contract Billing Date | `6. Customer Status\6.2 Contract` | `6. Customer Status\6.2 Contract` | Keep | Keep: unchanged |
| First Time Fix Rate | `6. Customer Experience\6.2 Service Quality` | `5. Customer Experience\6.2 Service Quality` | Move | Move: section renumber |
| GL Budget Revenue | `1. GL Financials\1. Revenue\5. Budget` | `1. GL Financials\1. Revenue\5. Budget` | Keep | Keep: unchanged |
| GL Budget Revenue (Projects) | `1. GL Financials\1. Revenue\5. Budget` | `1. GL Financials\1. Revenue\5. Budget` | Keep | Keep: unchanged |
| GL Budget Revenue (Selected Stream) | `1. GL Financials\1. Revenue\5. Budget` | `1. GL Financials\1. Revenue\5. Budget` | Keep | Keep: unchanged |
| GL Budget Revenue (Service Contracts) | `1. GL Financials\1. Revenue\5. Budget` | `1. GL Financials\1. Revenue\5. Budget` | Keep | Keep: unchanged |
| GL Budget Revenue (T&M) | `1. GL Financials\1. Revenue\5. Budget` | `1. GL Financials\1. Revenue\5. Budget` | Keep | Keep: unchanged |
| GL Budget Revenue FYTD (As Of) | `1. GL Financials\1. Revenue\5. Budget\7. Time Intelligence` | `1. GL Financials\1. Revenue\5. Budget\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Budget Revenue FYTD PY (As Of) | `1. GL Financials\1. Revenue\5. Budget\7. Time Intelligence` | `1. GL Financials\1. Revenue\5. Budget\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Cost of Sales | `1. GL Financials\2. Cost` | `1. GL Financials\2. Cost` | Keep | Keep: unchanged |
| GL Cost of Sales (Projects) | `1. GL Financials\2. Cost` | `1. GL Financials\2. Cost` | Keep | Keep: unchanged |
| GL Cost of Sales (Service Contracts) | `1. GL Financials\2. Cost` | `1. GL Financials\2. Cost` | Keep | Keep: unchanged |
| GL Cost of Sales (T&M) | `1. GL Financials\2. Cost` | `1. GL Financials\2. Cost` | Keep | Keep: unchanged |
| GL Gross Profit | `1. GL Financials\3. Gross Profit` | `1. GL Financials\3. Gross Profit` | Keep | Keep: unchanged |
| GL Gross Profit (Cumulative FYTD) | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Gross Profit (Monthly) | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Gross Profit (Monthly/Cumulative) | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Gross Profit (Projects) | `1. GL Financials\3. Gross Profit` | `1. GL Financials\3. Gross Profit` | Keep | Keep: unchanged |
| GL Gross Profit (Selected Stream) | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Gross Profit (Service Contracts) | `1. GL Financials\3. Gross Profit` | `1. GL Financials\3. Gross Profit` | Keep | Keep: unchanged |
| GL Gross Profit (T&M) | `1. GL Financials\3. Gross Profit` | `1. GL Financials\3. Gross Profit` | Keep | Keep: unchanged |
| GL Gross Profit FYTD (As Of) | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Gross Profit FYTD PY (As Of) | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Gross Profit PY (Monthly/Cumulative) | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | `1. GL Financials\3. Gross Profit\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Gross Profit PY (Period) | `1. GL Financials\3. Gross Profit\6. Variance` | `1. GL Financials\3. Gross Profit\6. Variance` | Keep | Keep: unchanged |
| GL Gross Profit Δ vs PY % (FYTD) | `1. GL Financials\3. Gross Profit\6. Variance` | `1. GL Financials\3. Gross Profit\6. Variance` | Keep | Keep: unchanged |
| GL Gross Profit Δ vs PY % (Period) | `1. GL Financials\3. Gross Profit\6. Variance` | `1. GL Financials\3. Gross Profit\6. Variance` | Keep | Keep: unchanged |
| GL Gross Profit Δ vs PY % (Period) Label | `5. UI\GL Financials` | `1. GL Financials\3. Gross Profit\6. Variance\Labels` | Move | Move: domain-specific label |
| GL Gross Profit Δ vs PY (FYTD) | `1. GL Financials\3. Gross Profit\6. Variance` | `1. GL Financials\3. Gross Profit\6. Variance` | Keep | Keep: unchanged |
| GL Revenue | `1. GL Financials\1. Revenue` | `1. GL Financials\1. Revenue` | Keep | Keep: unchanged |
| GL Revenue (Cumulative FYTD) | `1. GL Financials\1. Revenue\7. Time Intelligence` | `1. GL Financials\1. Revenue\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Revenue (Monthly) | `1. GL Financials\1. Revenue\7. Time Intelligence` | `1. GL Financials\1. Revenue\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Revenue (Monthly/Cumulative) | `1. GL Financials\1. Revenue\7. Time Intelligence` | `1. GL Financials\1. Revenue\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Revenue (Projects - Amend Markets) | `1. GL Financials\1. Revenue` | `1. GL Financials\1. Revenue` | Keep | Keep: unchanged |
| GL Revenue (Projects - Sandbox) | `8. Deprecated\8.1 Sandbox\GL Financials` | `9. Deprecated\8.1 Sandbox\GL Financials` | Move | Move: section renumber |
| GL Revenue (Projects) | `1. GL Financials\1. Revenue` | `1. GL Financials\1. Revenue` | Keep | Keep: unchanged |
| GL Revenue (Selected Stream) | `1. GL Financials\1. Revenue\7. Time Intelligence` | `1. GL Financials\1. Revenue\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Revenue (Service Contracts) | `1. GL Financials\1. Revenue` | `1. GL Financials\1. Revenue` | Keep | Keep: unchanged |
| GL Revenue (T&M) | `1. GL Financials\1. Revenue` | `1. GL Financials\1. Revenue` | Keep | Keep: unchanged |
| GL Revenue (Total - Sandbox) | `8. Deprecated\8.1 Sandbox\GL Financials` | `9. Deprecated\8.1 Sandbox\GL Financials` | Move | Move: section renumber |
| GL Revenue FYTD (As Of) | `1. GL Financials\1. Revenue\7. Time Intelligence` | `1. GL Financials\1. Revenue\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Revenue FYTD PY (As Of) | `1. GL Financials\1. Revenue\7. Time Intelligence` | `1. GL Financials\1. Revenue\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Revenue PY (Monthly/Cumulative) | `1. GL Financials\1. Revenue\7. Time Intelligence` | `1. GL Financials\1. Revenue\7. Time Intelligence` | Keep | Keep: unchanged |
| GL Revenue PY (Period) | `1. GL Financials\1. Revenue\6. Variance` | `1. GL Financials\1. Revenue\6. Variance` | Keep | Keep: unchanged |
| GL Revenue vs Budget % (FYTD) | `1. GL Financials\1. Revenue\6. Variance` | `1. GL Financials\1. Revenue\6. Variance` | Keep | Keep: unchanged |
| GL Revenue vs Budget (FYTD) | `1. GL Financials\1. Revenue\6. Variance` | `1. GL Financials\1. Revenue\6. Variance` | Keep | Keep: unchanged |
| GL Revenue Δ vs PY % (FYTD) | `1. GL Financials\1. Revenue\6. Variance` | `1. GL Financials\1. Revenue\6. Variance` | Keep | Keep: unchanged |
| GL Revenue Δ vs PY % (Period) | `1. GL Financials\1. Revenue\6. Variance` | `1. GL Financials\1. Revenue\6. Variance` | Keep | Keep: unchanged |
| GL Revenue Δ vs PY % (Period) Label | `5. UI\GL Financials` | `1. GL Financials\1. Revenue\6. Variance\Labels` | Move | Move: domain-specific label |
| GL Revenue Δ vs PY (FYTD) | `1. GL Financials\1. Revenue\6. Variance` | `1. GL Financials\1. Revenue\6. Variance` | Keep | Keep: unchanged |
| GP % (By Stream) | `2. Customer Financials\3. Gross Profit\By Stream` | `2. Customer Financials\3. Gross Profit\By Stream` | Keep | Keep: unchanged |
| GRR % Δ vs PY (R12M As Of) | `7. Helper\7.4 UI\Conditional Formatting` | `7. Helper\Conditional Formatting` | Move | Move: helper numeric delta |
| GRR Sparkline (SVG) | `5. Retention\5.4 R12M As Of\5.4.7 Sparklines` | `8. UI\Sparklines\Retention` | Move | Move: UI output |
| GRR Trend Color (R12M As Of) | `7. Helper\7.4 UI\Conditional Formatting` | `8. UI\Conditional Formatting` | Move | Move: UI color output |
| Gross Profit | `8. Deprecated\Customer Financials\Base` | `9. Deprecated\Customer Financials\Base` | Move | Move: section renumber |
| Gross Profit (By Stream) | `2. Customer Financials\3. Gross Profit\By Stream` | `2. Customer Financials\3. Gross Profit\By Stream` | Keep | Keep: unchanged |
| Gross Revenue Retention % (FY Period) | `8. Deprecated\8.1 Retention\FY Period\KPIs` | `9. Deprecated\8.1 Retention\FY Period\KPIs` | Move | Move: section renumber |
| Gross Revenue Retention % (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\KPIs` | `3. Retention (Service Contracts)\R12M As Of\KPIs` | Keep | Keep: unchanged |
| Gross Revenue Retention % PY (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.3 KPIs\GRR` | `3. Retention (Service Contracts)\R12M As Of\KPIs\GRR` | Move | Move: retention business logic |
| Gross Revenue Retention Trend vs PY (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.3 KPIs\GRR` | `3. Retention (Service Contracts)\R12M As Of\KPIs\GRR\Labels` | Move | Move: domain-specific label |
| Industrial Rank Context String | `5. UI\Customer Metrics` | `8. UI\Customer Metrics` | Move | Move: UI grouping |
| Industrial Rank Context String (R12M As Of) | `5. UI\Customer Metrics` | `8. UI\Customer Metrics` | Move | Move: UI grouping |
| Industrial Revenue Rank | `4. Customer Metrics\4.2 Rank` | `4. Customer Metrics\4.2 Rank` | Keep | Keep: unchanged |
| Industrial Revenue Rank (R12M As Of) | `4. Customer Metrics\4.2 Rank` | `4. Customer Metrics\4.2 Rank` | Keep | Keep: unchanged |
| Last Billing Date (Any Stream) | `6. Customer Status\6.1 Helpers` | `6. Customer Status\6.1 Helpers` | Keep | Keep: unchanged |
| Last Contract Billing Date | `6. Customer Status\6.2 Contract` | `6. Customer Status\6.2 Contract` | Keep | Keep: unchanged |
| Last NPS Date | `6. Customer Experience\6.0 Helpers` | `5. Customer Experience\6.0 Helpers` | Move | Move: section renumber |
| Last SC Data Month End (In Slice) | `6. Helper\Retention\Anchors` | `7. Helper\Retention\Anchors` | Move | Move: section renumber |
| Logo Churn % (SC) (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Logo Churn Count (SC) (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Logo Retention % (SC) (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Logo Retention % (SC) PY (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Logo Retention Trend (SC) vs PY (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo\Labels` | Move | Move: domain-specific label |
| Logo Sparkline (SVG) | `5. Retention\5.4 R12M As Of\5.4.7 Sparklines` | `8. UI\Sparklines\Retention` | Move | Move: UI output |
| Months Since Last Billing | `6. Customer Status\6.1 Helpers` | `6. Customer Status\6.1 Helpers` | Keep | Keep: unchanged |
| NPS Response Count | `6. Customer Experience\6.1 NPS` | `5. Customer Experience\6.1 NPS` | Move | Move: section renumber |
| NRR % Δ vs PY (R12M As Of) | `7. Helper\7.4 UI\Conditional Formatting` | `7. Helper\Conditional Formatting` | Move | Move: helper numeric delta |
| NRR Logic Explanation.MD | `5. Retention\5.4 R12M As Of\5.4.0 Documentation` | `8. UI\Documentation\Retention` | Move | Move: UI documentation |
| NRR Sparkline (SVG) | `5. Retention\5.4 R12M As Of\5.4.7 Sparklines` | `8. UI\Sparklines\Retention` | Move | Move: UI output |
| NRR Trend Color (R12M As Of) | `7. Helper\7.4 UI\Conditional Formatting` | `8. UI\Conditional Formatting` | Move | Move: UI color output |
| NRR Waterfall Value | `5. Retention\5.4 R12M As Of\5.4.5 Waterfall` | `3. Retention (Service Contracts)\R12M As Of\Waterfall` | Move | Move: retention business logic |
| NRR Waterfall Value (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.5 Waterfall` | `3. Retention (Service Contracts)\R12M As Of\Waterfall` | Move | Move: retention business logic |
| Net Promoter Score | `6. Customer Experience\6.1 NPS` | `5. Customer Experience\6.1 NPS` | Move | Move: section renumber |
| Net Promoter Score (R12M) | `4. Customer Metrics\4.3 NPS` | `4. Customer Metrics\4.3 NPS` | Keep | Keep: unchanged |
| Net Promoter Score PY (R12M) | `6. Customer Experience\6.1 NPS\R12M` | `5. Customer Experience\6.1 NPS\R12M` | Move | Move: section renumber |
| Net Promoter Score Trend vs PY | `6. Customer Experience\6.1 NPS\R12M` | `5. Customer Experience\6.1 NPS\R12M` | Move | Move: section renumber |
| Net Revenue Retention % (FY Period) | `8. Deprecated\8.1 Retention\FY Period\KPIs` | `9. Deprecated\8.1 Retention\FY Period\KPIs` | Move | Move: section renumber |
| Net Revenue Retention % (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\KPIs` | `3. Retention (Service Contracts)\R12M As Of\KPIs` | Keep | Keep: unchanged |
| Net Revenue Retention % PY (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.3 KPIs\NRR` | `3. Retention (Service Contracts)\R12M As Of\KPIs\NRR` | Move | Move: retention business logic |
| Net Revenue Retention Trend vs PY (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.3 KPIs\NRR` | `3. Retention (Service Contracts)\R12M As Of\KPIs\NRR\Labels` | Move | Move: domain-specific label |
| P&L % of Revenue (YTD) | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L % of Revenue Budget (YTD) | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L % of Revenue PY (YTD) | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L Amount (YTD) | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L Amount (YTD) (Line) | `7. Helper\7.3 P&L\YTD` | `7. Helper\7.3 P&L\YTD` | Keep | Keep: unchanged |
| P&L Amount PY (YTD) | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L Amount PY (YTD) (Line) | `7. Helper\7.3 P&L\YTD` | `7. Helper\7.3 P&L\YTD` | Keep | Keep: unchanged |
| P&L Budget Amount (YTD) | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L Budget Amount (YTD) (Line) | `7. Helper\7.3 P&L\YTD` | `7. Helper\7.3 P&L\YTD` | Keep | Keep: unchanged |
| P&L Divider | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L Gross Profit | `1. GL Financials\4. P&L\2. Period` | `1. GL Financials\4. P&L\2. Period` | Keep | Keep: unchanged |
| P&L Gross Profit Budget | `1. GL Financials\4. P&L\2. Period` | `1. GL Financials\4. P&L\2. Period` | Keep | Keep: unchanged |
| P&L Gross Profit PY | `1. GL Financials\4. P&L\2. Period` | `1. GL Financials\4. P&L\2. Period` | Keep | Keep: unchanged |
| P&L Net Profit | `1. GL Financials\4. P&L\2. Period` | `1. GL Financials\4. P&L\2. Period` | Keep | Keep: unchanged |
| P&L Net Profit Budget | `1. GL Financials\4. P&L\2. Period` | `1. GL Financials\4. P&L\2. Period` | Keep | Keep: unchanged |
| P&L Net Profit PY | `1. GL Financials\4. P&L\2. Period` | `1. GL Financials\4. P&L\2. Period` | Keep | Keep: unchanged |
| P&L Operator | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L Row Sign | `7. Helper\7.3 P&L\YTD` | `7. Helper\7.3 P&L\YTD` | Keep | Keep: unchanged |
| P&L Var vs Budget $ (YTD) | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L Var vs Budget % (YTD) | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L Var vs PY $ (YTD) | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| P&L Var vs PY % (YTD) | `1. GL Financials\4. P&L\1. YTD` | `1. GL Financials\4. P&L\1. YTD` | Keep | Keep: unchanged |
| Placeholder v1 | `6. Helper\Misc` | `7. Helper\Misc` | Move | Move: section renumber |
| Placeholder v2 | `6. Helper\Misc` | `7. Helper\Misc` | Move | Move: section renumber |
| Project Cost | `2. Customer Financials\2. Cost\Streams` | `2. Customer Financials\2. Cost\Streams` | Keep | Keep: unchanged |
| Project GP | `2. Customer Financials\3. Gross Profit\Streams` | `2. Customer Financials\3. Gross Profit\Streams` | Keep | Keep: unchanged |
| Project Revenue | `2. Customer Financials\1. Revenue\Streams` | `2. Customer Financials\1. Revenue\Streams` | Keep | Keep: unchanged |
| Project Revenue (R12M As Of) | `4. Time Intelligence\4.1 R12M As Of\Revenue\Streams` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of\Streams` | Move | Move: consolidate TI under Customer Financials |
| Project Spend per Maintenance $ (TTM) | `9. Not Implemented\9.2 Operations` | `10. Not Implemented\9.2 Operations` | Move | Move: section renumber |
| Promoters Count | `6. Customer Experience\6.1 NPS` | `5. Customer Experience\6.1 NPS` | Move | Move: section renumber |
| Prompt and On Time % | `6. Customer Experience\6.2 Service Quality` | `5. Customer Experience\6.2 Service Quality` | Move | Move: section renumber |
| R12M Period Label | `4. Time Intelligence\4.1 R12M As Of\Helpers` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of\Labels` | Move | Move: consolidate TI under Customer Financials |
| Recurring Mix % (SC) (R12M) | `4. Time Intelligence\4.1 R12M As Of\Revenue\Mix` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of\Mix` | Move | Move: consolidate TI under Customer Financials |
| Retention Base Count PY (SC) (R12M As Of) | `5. Retention\5.4 R12M As Of\5.4.4 Logo (SC)` | `3. Retention (Service Contracts)\R12M As Of\Logo` | Move | Move: retention business logic |
| Retention Base PY (FY Period) | `8. Deprecated\8.1 Retention\FY Period\Components` | `9. Deprecated\8.1 Retention\FY Period\Components` | Move | Move: section renumber |
| Retention Base PY (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\Components` | `3. Retention (Service Contracts)\R12M As Of\Components` | Keep | Keep: unchanged |
| Revenue | `8. Deprecated\Customer Financials\Base` | `9. Deprecated\Customer Financials\Base` | Move | Move: section renumber |
| Revenue (By Stream) | `2. Customer Financials\1. Revenue\By Stream` | `2. Customer Financials\1. Revenue\By Stream` | Keep | Keep: unchanged |
| Revenue Momentum % (R12M vs PY) | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of` | Keep | Keep: unchanged |
| Revenue PY (Dynamic) | `2. Customer Financials\1. Revenue\Time Intelligence` | `2. Customer Financials\1. Revenue\Time Intelligence` | Keep | Keep: unchanged |
| Revenue Stream Share Fill (R12M) | `4. Time Intelligence\4.1 R12M As Of\Revenue\Mix` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of\Mix` | Move | Move: consolidate TI under Customer Financials |
| Revenue Trend Color (R12M As Of) | `7. Helper\7.4 UI\Conditional Formatting` | `8. UI\Conditional Formatting` | Move | Move: UI color output |
| Revenue Δ vs PY (R12M As Of) | `7. Helper\7.4 UI\Conditional Formatting` | `7. Helper\Conditional Formatting` | Move | Move: helper numeric delta |
| SC Revenue (R12M As Of) | `4. Time Intelligence\4.1 R12M As Of\Revenue\Streams` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of\Streams` | Move | Move: consolidate TI under Customer Financials |
| Selected Customer Name | `6. Customer Status\6.0 UI` | `6. Customer Status\6.0 UI` | Keep | Keep: unchanged |
| Selected FY End Date | `7. Helper\7.0 Date` | `7. Helper\7.0 Date` | Keep | Keep: unchanged |
| Selected FY Start Date | `7. Helper\7.0 Date` | `7. Helper\7.0 Date` | Keep | Keep: unchanged |
| Selected Fiscal Year (Single) | `7. Helper\7.0 Date` | `7. Helper\7.0 Date` | Keep | Keep: unchanged |
| Service Contract Cost | `2. Customer Financials\2. Cost\Streams` | `2. Customer Financials\2. Cost\Streams` | Keep | Keep: unchanged |
| Service Contract Gross Profit | `2. Customer Financials\3. Gross Profit\Streams` | `2. Customer Financials\3. Gross Profit\Streams` | Keep | Keep: unchanged |
| Service Contract Gross Profit % | `2. Customer Financials\3. Gross Profit\Streams` | `2. Customer Financials\3. Gross Profit\Streams` | Keep | Keep: unchanged |
| Service Contract Revenue | `2. Customer Financials\1. Revenue\Streams` | `2. Customer Financials\1. Revenue\Streams` | Keep | Keep: unchanged |
| Service Contract Revenue (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\Base` | `3. Retention (Service Contracts)\R12M As Of\Base` | Keep | Keep: unchanged |
| Service Contract Revenue PY (FY Period) | `8. Deprecated\8.1 Retention\FY Period\Base` | `9. Deprecated\8.1 Retention\FY Period\Base` | Move | Move: section renumber |
| Service Contract Revenue PY (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\Base` | `3. Retention (Service Contracts)\R12M As Of\Base` | Keep | Keep: unchanged |
| Stream Concentration % (R12M) | `4. Time Intelligence\4.1 R12M As Of\Revenue\Mix` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of\Mix` | Move | Move: consolidate TI under Customer Financials |
| T&M Cost | `2. Customer Financials\2. Cost\Streams` | `2. Customer Financials\2. Cost\Streams` | Keep | Keep: unchanged |
| T&M Gross Profit | `2. Customer Financials\3. Gross Profit\Streams` | `2. Customer Financials\3. Gross Profit\Streams` | Keep | Keep: unchanged |
| T&M Revenue | `2. Customer Financials\1. Revenue\Streams` | `2. Customer Financials\1. Revenue\Streams` | Keep | Keep: unchanged |
| T&M Revenue (R12M As Of) | `4. Time Intelligence\4.1 R12M As Of\Revenue\Streams` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of\Streams` | Move | Move: consolidate TI under Customer Financials |
| T&M Spend per Maintenance $ (TTM) | `9. Not Implemented\9.2 Operations` | `10. Not Implemented\9.2 Operations` | Move | Move: section renumber |
| Total Cost | `2. Customer Financials\2. Cost` | `2. Customer Financials\2. Cost` | Keep | Keep: unchanged |
| Total GP % | `2. Customer Financials\3. Gross Profit` | `2. Customer Financials\3. Gross Profit` | Keep | Keep: unchanged |
| Total GP % (FY As Of) | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\FY As Of` | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\FY As Of` | Keep | Keep: unchanged |
| Total GP % (R12M As Of) | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\R12M As Of` | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\R12M As Of` | Keep | Keep: unchanged |
| Total GP % PY (R12M As Of) | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\R12M As Of` | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\R12M As Of` | Keep | Keep: unchanged |
| Total GP % Trend Color (R12M As Of) | `7. Helper\7.4 UI\Conditional Formatting` | `8. UI\Conditional Formatting` | Move | Move: UI color output |
| Total GP % Trend vs PY (R12M As Of) | `5. UI\5.1 Customer Financials\R12M As Of` | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\R12M As Of\Labels` | Move | Move: domain-specific label |
| Total GP % Δ vs PY (R12M As Of) | `7. Helper\7.4 UI\Conditional Formatting` | `7. Helper\Conditional Formatting` | Move | Move: helper numeric delta |
| Total Gross Profit | `2. Customer Financials\3. Gross Profit` | `2. Customer Financials\3. Gross Profit` | Keep | Keep: unchanged |
| Total Gross Profit (FY As Of) | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\FY As Of` | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\FY As Of` | Keep | Keep: unchanged |
| Total Gross Profit (R12M As Of) | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\R12M As Of` | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\R12M As Of` | Keep | Keep: unchanged |
| Total Gross Profit PY | `2. Customer Financials\3. Gross Profit\Time Intelligence` | `2. Customer Financials\3. Gross Profit\Time Intelligence` | Keep | Keep: unchanged |
| Total Gross Profit PY (FY As Of) | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\FY As Of` | `2. Customer Financials\3. Gross Profit\7. Time Intelligence\FY As Of` | Keep | Keep: unchanged |
| Total Gross Profit Trend vs PY | `5. UI\5.1 Customer Financials` | `2. Customer Financials\3. Gross Profit\8. Labels` | Move | Move: domain-specific label |
| Total Gross Profit YoY % (FY As Of) | `2. Customer Financials\3. Gross Profit\6. Variance\FY As Of` | `2. Customer Financials\3. Gross Profit\6. Variance\FY As Of` | Keep | Keep: unchanged |
| Total Gross Profit YoY Δ (FY As Of) | `2. Customer Financials\3. Gross Profit\6. Variance\FY As Of` | `2. Customer Financials\3. Gross Profit\6. Variance\FY As Of` | Keep | Keep: unchanged |
| Total Project Spend per Total Maintenance $ (Snapshot) | `9. Not Implemented\9.2 Operations` | `10. Not Implemented\9.2 Operations` | Move | Move: section renumber |
| Total Revenue | `2. Customer Financials\1. Revenue` | `2. Customer Financials\1. Revenue` | Keep | Keep: unchanged |
| Total Revenue (FY As Of) | `2. Customer Financials\1. Revenue\7. Time Intelligence\FY As Of` | `2. Customer Financials\1. Revenue\7. Time Intelligence\FY As Of` | Keep | Keep: unchanged |
| Total Revenue (R12M As Of) | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of` | Keep | Keep: unchanged |
| Total Revenue PY | `2. Customer Financials\1. Revenue\7. Time Intelligence\Period` | `2. Customer Financials\1. Revenue\7. Time Intelligence\Period` | Keep | Keep: unchanged |
| Total Revenue PY (FY As Of) | `2. Customer Financials\1. Revenue\7. Time Intelligence\FY As Of` | `2. Customer Financials\1. Revenue\7. Time Intelligence\FY As Of` | Keep | Keep: unchanged |
| Total Revenue PY (R12M As Of) | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of` | Keep | Keep: unchanged |
| Total Revenue Trend vs PY | `5. UI\5.1 Customer Financials` | `2. Customer Financials\1. Revenue\8. Labels` | Move | Move: domain-specific label |
| Total Revenue Trend vs PY (R12M As Of) | `5. UI\5.1 Customer Financials\R12M As Of` | `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of\Labels` | Move | Move: domain-specific label |
| Total Revenue YoY % (FY As Of) | `2. Customer Financials\1. Revenue\6. Variance\FY As Of` | `2. Customer Financials\1. Revenue\6. Variance\FY As Of` | Keep | Keep: unchanged |
| Total Revenue YoY Δ (FY As Of) | `2. Customer Financials\1. Revenue\6. Variance\FY As Of` | `2. Customer Financials\1. Revenue\6. Variance\FY As Of` | Keep | Keep: unchanged |
| Total T&M Spend per Total Maintenance $ (Snapshot) | `9. Not Implemented\9.2 Operations` | `10. Not Implemented\9.2 Operations` | Move | Move: section renumber |
| Upsell Revenue % (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\Components` | `3. Retention (Service Contracts)\R12M As Of\Components` | Keep | Keep: unchanged |
| Upsell Revenue (FY Period) | `8. Deprecated\8.1 Retention\FY Period\Components` | `9. Deprecated\8.1 Retention\FY Period\Components` | Move | Move: section renumber |
| Upsell Revenue (R12M As Of) | `3. Retention (Service Contracts)\R12M As Of\Components` | `3. Retention (Service Contracts)\R12M As Of\Components` | Keep | Keep: unchanged |

## Implementation Plan
1. Create a safety snapshot.
- Export TMDL before any writes (`ExportToTmdlFolder`) so folder/name metadata can be restored quickly.

2. Apply section renumber moves first (low risk, high clarity).
- Move all `8. Deprecated\...` -> `9. Deprecated\...`
- Move all `9. Not Implemented\...` -> `10. Not Implemented\...`
- Move all `6. Customer Experience\...` -> `5. Customer Experience\...`
- Move all `6. Helper\...` -> `7. Helper\...`

3. Consolidate Time Intelligence under Customer Financials.
- Move `4. Time Intelligence\4.1 R12M As Of\...` into `2. Customer Financials\1. Revenue\7. Time Intelligence\R12M As Of\...`

4. Consolidate Retention business logic into section 3.
- Move `5. Retention\5.4 R12M As Of\...` business measures into `3. Retention (Service Contracts)\R12M As Of\...`
- Keep labels with retention domain paths as mapped in this file.

5. Rehome UI outputs.
- Move UI-only outputs (documentation text, sparklines, conditional-format colors, selected UI grouping measures) to `8. UI\...`

6. Rehome domain-specific labels.
- Move label/trend measures from `5. UI\...` to their owning domain label folders (GL, Customer Financials) except `Customer Metrics` context strings which go to `8. UI\Customer Metrics`.

7. Normalize helper conditional-format structure.
- Move numeric helper deltas to `7. Helper\Conditional Formatting`
- Keep UI color outputs in `8. UI\Conditional Formatting`

8. Validate after each batch.
- Re-list measures by folder and compare counts vs this mapping.
- Smoke-test key report pages/cards:
  - GL Revenue / GL Gross Profit visuals
  - Customer Financials Revenue/GP visuals
  - Retention KPI cards + waterfall + sparklines
  - Customer profile/rank visuals

9. Final QA + cleanup.
- Confirm no measure has an out-of-scheme section prefix.
- Confirm no business logic measure remains in `8. UI`.
- Confirm no UI output remains in helper/domain folders unless intentionally domain label.

## Rollback Plan
1. If issues are detected mid-migration, stop further writes.
2. Re-import the pre-change TMDL snapshot to restore original measure metadata.
3. Re-run inventory and compare row-by-row with this file before attempting migration again.
