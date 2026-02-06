# CRR Measure Mapping - Considerations

## Purpose
Document the measure-mapping decisions and considerations identified so far while planning the migration from the existing CRR v05 semantic model to the newer revenue model (Selected Methods).

This is a planning artifact only; it is intended to guide the next step where we define/implement the measure set.

## What We Are Preserving vs Replacing
### Preserve
- CRR report visuals/layout (target UX).
- Retention framework definitions (NRR/GRR/churn) as a concept.

### Replace
- Most of the existing "base revenue" wiring and legacy stream facts in CRR v05.
- Stream revenue logic will be simplified around the authoritative stream facts selected in the Revenue Sandbox.

## Authoritative Stream Facts (Selected Methods)
These tables are the intended authoritative sources for stream revenue/cost in the newer model:

- Projects: `Projects_ProjectMonth_Amend_F`
- Service Contracts: `SERVCONTRACTS_CustomerMonth_Billings_F`
- T&M: `TM_CustomerMonth_CRR_F`
- Legacy Projects: `LEGACYPROJECTS_CustomerMonth_Billings_F` (known to be sparse in sandbox currently; investigate later)
- GL comparator (always available): `POSTING_DATA_F` (via GL measures/buckets)

Notes:
- In the sandbox, `SERVCONTRACTS_CustomerMonth_Billings_F` and `TM_CustomerMonth_CRR_F` already include both `Revenue Amount` and `Cost Amount` populated in Power Query.
- `Projects_ProjectMonth_Amend_F` includes both revenue and cost at job-month granularity.

## Retention Metrics: Service Contracts Only
Decision locked:
- Retention metrics (Retention Base, churn/contraction/upsell, NRR/GRR) are based on **Service Contract revenue only**.

Implications:
- Retention should remain anchored to the service contracts customer-month fact (`SERVCONTRACTS_CustomerMonth_Billings_F`) and its related dimensions (`SERVCONTRACTS_D`, `DIVISIONS_D`, etc.).
- Do not rebuild retention on "Total Revenue" across all streams.

## Existing CRR v05 Base Measures (What They Do Today)
In `Customer Revenue Retention/current/CRR v05.SemanticModel/definition/tables/_Key Measures.tmdl`, the CRR v05 model defines three base streams and then totals them:

- `Project Revenue` = `SUM(PROJECT_REVENUE_F[Amount])` (Completed Month clamped)
- `Service Contract Revenue` = `SUM(SERVCONTRACTS_REVENUE_F[Amount])` (Completed Month clamped)
- `T&M Revenue` = `SUM(SPOT_FINANCIALS_F[Revenue])` (Completed Month clamped)
- `Total Revenue` = Project + Service Contract + T&M

Many downstream measures (including retention) reference these base measures.

## Proposed Base Measure Mapping (New Model)
### 1) Stream base measures (for CRR revenue pages)
Define new stream base measures directly off the selected-method facts:

- Projects Revenue -> sum of `Projects_ProjectMonth_Amend_F[Revenue Amount]` (plus any intended legacy projects inclusion)
- Projects Cost -> sum of `Projects_ProjectMonth_Amend_F[Cost Amount]`
- Service Contracts Revenue -> sum of `SERVCONTRACTS_CustomerMonth_Billings_F[Revenue Amount]`
- Service Contracts Cost -> sum of `SERVCONTRACTS_CustomerMonth_Billings_F[Cost Amount]`
- T&M Revenue -> sum of `TM_CustomerMonth_CRR_F[Revenue Amount]`
- T&M Cost -> sum of `TM_CustomerMonth_CRR_F[Cost Amount]`

Then:
- Stream GP = Revenue - Cost
- Stream GP% = DIVIDE(GP, Revenue)

### 2) Total base measures (for CRR rollups)
Two viable patterns (to choose during implementation):

Pattern A (separate-fact measures):
- `Total Revenue` = Projects Revenue + Service Contracts Revenue + T&M Revenue (+ Legacy Projects if included)
- `Total Cost` = Projects Cost + Service Contracts Cost + T&M Cost (+ Legacy Projects cost if included)

Pattern B (combined selected-method fact):
- Introduce a conformed "Selected Methods" fact at `Customer Key x Month End x Stream` with `Revenue Amount` and `Cost Amount`.
- `Total Revenue` becomes SUM of that table.
- `Revenue by Stream` becomes a simple slice by `Stream`.

Retention measures should still remain on the service contract base measures regardless of which total pattern is chosen.

## Completed-Month and Calendar Window Considerations
### Completed Month clamp
CRR v05 frequently clamps base measures to:
- `FYCALENDAR_D[Is Completed Month] = TRUE`

Plan assumption:
- Keep this convention for Selected Methods base measures unless explicitly overridden for a specific page/use case.

### Fiscal-year boundary awareness
We observed and fixed a failure mode where a calendar `StartDate` (ex: `2021-01-01`) caused fiscal-year totals to omit early fiscal months.

Plan requirement:
- Any hard-coded start date/window in fact shaping must be validated against fiscal-year definitions to avoid silently undercounting FY totals.

## Retention Measure Mapping Notes (CRR v05 -> New Model)
In CRR v05, retention FY Period measures are implemented over:
- `[Service Contract Revenue]` and `[Service Contract Revenue PY (FY Period)]`

Key mapping tasks:
- Replace any references to `SERVCONTRACTS_REVENUE_F` with the new customer-month billings fact as the authoritative input.
- Replace anchor-date logic that uses `MAX(SERVCONTRACTS_REVENUE_F[Date])` with an anchor based on:
  - the customer-month fact's latest available `Month End`, or
  - calendar-driven "as-of" logic clamped to last data month end.

## Known Open Decisions (Not Yet Locked)
- Legacy Projects inclusion:
  - Include in Total Revenue? (likely yes if present in the data)
  - Include in Total Cost/GP? (depends on whether `Cost Amount` is trustworthy/complete for the legacy population)
- Combined selected-methods fact:
  - Build it now for simplicity, or keep separate facts for first pass and add the combined table later.
- Naming standard:
  - We prefer `_F` suffix; we have not yet locked a canonical table naming convention (tokens/order) for the newer model.

