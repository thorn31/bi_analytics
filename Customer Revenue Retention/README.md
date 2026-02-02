# Customer Revenue Retention

## Overview
This report is a consolidated view of company performance across **Service Contracts**, **Projects**, and **T&M**. It combines revenue, gross profit, customer health, and retention into a single experience that can start at the executive dashboard level and drill down into customer and stream-specific details.

Retention KPIs currently focus on **Service Contracts (SC)** using a **Rolling 12‑Month As‑Of (R12M As Of)** methodology. As the report expands into Projects and T&M detail, retention becomes less central and stream-specific operational metrics take over.

## Report structure
- **Dashboard**: High-level KPI cards and trend visuals, including total revenue/gross profit by stream, retention KPIs, top customers, NPS, and division performance.
- **Customer**: Customer-level view of metrics spanning the three revenue streams.
- **Future drilldowns**: Dedicated views for **Contracts**, **Projects**, and **T&M** with stream-specific metrics and logic.

## Core concepts
- **Revenue streams**: Service Contracts, Projects, and T&M are tracked and analyzed separately.
- **Customer grain**: `CUSTOMERS_D[Customer Key]`.
- **Completed Month**: `FYCALENDAR_D[Is Completed Month] = TRUE` is used to gate financials in core measures.
- **Dashboard time context**: The Dashboard page is driven by a **Fiscal Year** slicer; revenue and GP KPIs reflect the selected FY.
- **Top customers**: Based on `Client Revenue Rank`, scoped by the selected time window and stream filters.

## Retention methodology (SC-only, R12M As Of)
Anchor logic:
- **As Of Month End (SC)** chooses the earlier of:
  - the selected month end from calendar context, and
  - the last SC data month end within slice.

Key measures:
- **SC Revenue (R12M As Of)**
  - `DATESINPERIOD(FYCALENDAR_D[Date], AnchorDate, -12, MONTH)` over `SC Revenue (Agreement Month)`.
- **SC Revenue PY (R12M As Of)**
  - Same window, anchored to `EDATE(AnchorDate, -12)`.
- **Retention Base PY (R12M As Of)**
  - Sum of prior-period revenue for customers where `RevPY > 0`.
- **Churn Revenue (R12M As Of)**
  - `RevPY > 0` and `RevCY = 0` for each customer.
- **Contraction Revenue (R12M As Of)**
  - `RevPY > 0` and `0 < RevCY < RevPY` for each customer.
- **Upsell Revenue (R12M As Of)**
  - `RevPY > 0` and `RevCY > RevPY` for each customer.

Retention KPIs:
- **Net Revenue Retention % (R12M As Of)**
  - `(Retention Base PY - Churn - Contraction + Upsell) / Retention Base PY`
- **Gross Revenue Retention % (R12M As Of)**
  - `(Retention Base PY - Churn - Contraction) / Retention Base PY`

## Retention design notes (from model docs)
- Retention is treated as a **cohort problem** with a stable grain.
- Cohort grain uses `SC_AgreementMonth_Revenue` (AgreementKey x Month End) so slicers on `SERVCONTRACTS_D` properly affect retention.
- The anchor date is computed once per filter slice and **ignores customer-level filters** to avoid per-customer anchors.
- Retention KPIs should not rely on descriptive attributes (like customer name) for data existence.
- Logo retention has two separate definitions in the model: **SC-only** vs **Any-Revenue** (kept as separate measures).

## Data model highlights
Core fact tables:
- `SERVCONTRACTS_REVENUE_F`
- `SERVCONTRACTS_COSTS_F`
- `PROJECT_REVENUE_F`
- `PROJECT_COSTS_F`
- `SPOT_FINANCIALS_F` (T&M)
- `NPS_F`

Key dimension tables:
- `CUSTOMERS_D`
- `DIVISIONS_D`
- `FYCALENDAR_D`

Cohort/retention tables:
- `SC_AgreementMonth_Revenue` (SC retention by agreement/month, cohort-safe)
- `SC_CustomerMonth_Revenue`

## Dashboard KPIs (current)
- **Retention (SC-only)**: NRR%, GRR%, and Logo Retention % (Service Contracts).
- **Financials**: Revenue and gross profit by stream (Service Contracts, Projects, T&M).
- **Customer/NPS**: Top customers and Net Promoter Score highlights.

## Measures to know
Dashboard and stream metrics:
- `Total Revenue`, `Total Cost`, `Total Gross Profit`, `Total GP %`
- `Project Revenue`, `Project Cost`, `Project GP`, `Project GP %`
- `Service Contract Revenue`, `Service Contract Cost`, `Service Contract Gross Profit`, `Service Contract Gross Profit %`
- `T&M Revenue`, `T&M Cost`, `T&M Gross Profit`, `T&M GP %`
- `Revenue (By Stream)`, `Gross Profit (By Stream)`, `GP % (By Stream)`
- `Client Revenue Rank`
- `Net Promoter Score`

Retention (R12M As Of):
- `Last SC Data Month End (In Slice)`
- `As Of Month End (SC)`
- `SC Revenue (R12M As Of)`
- `SC Revenue PY (R12M As Of)`
- `Retention Base PY (R12M As Of)`
- `Churn Revenue (R12M As Of)`
- `Contraction Revenue (R12M As Of)`
- `Upsell Revenue (R12M As Of)`
- `Net Revenue Retention % (R12M As Of)`
- `Gross Revenue Retention % (R12M As Of)`

## Notes and scope
- Retention metrics are **SC-only** at this time.
- The Dashboard includes cross-stream revenue and gross profit views plus customer and NPS highlights.
- Stream-specific drilldowns will introduce their own KPIs and logic, especially for Projects and T&M.
- Future tabs are expected to include retention trends over time and NPS over time.

## Open questions / TBD
- What are the primary KPIs for the Projects drilldown (beyond revenue, GP, and likely job costs by cost code)?
- What are the primary KPIs for the Contracts drilldown (beyond renewals, revenue, and GP)?
