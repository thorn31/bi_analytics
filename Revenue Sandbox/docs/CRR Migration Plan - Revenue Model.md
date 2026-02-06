# CRR Migration Plan - Revenue Model (Selected Methods)

## Purpose
Migrate the **Customer Revenue Retention (CRR)** report to a newer revenue semantic model using the **authoritative stream methodologies** selected and validated in the Revenue Sandbox model.

This document is a **planning artifact only** (no new measures are defined here yet).

## Scope / Guardrails
- Keep **GL revenue** available at all times as the finance baseline comparator.
- Define and implement a single set of **authoritative methodologies per stream**.
- CRR visuals/layout are considered valuable; DAX logic is expected to be simplified/rewritten based on the new setup.
- Do not change CRR report pages/visuals until the model layer is ready and validated.
- Prefer a star-schema approach and consistent filtering behavior through shared dimensions.

## Authoritative Stream Method Selections
These selections define the "Selected Methods" revenue used for CRR migration:

- **Projects**: `Projects_ProjectMonth_Amend_F`
  - Use exactly the logic currently implemented in the sandbox table (earned revenue at job-month, including change orders and carry-in handling).
- **Service Contracts**: `SERVCONTRACTS_CustomerMonth_Billings_F`
  - Billings-based methodology.
- **T&M**: `TM_CustomerMonth_CRR_F`
  - CRR methodology as implemented in the sandbox.
- **Legacy Projects**: `LEGACYPROJECTS_CustomerMonth_Billings_F`
  - Billings-based methodology; best approximation of GL project revenue for legacy population.
- **GL (always present)**: `POSTING_DATA_F` (via existing GL measures/buckets)

## Tables Utilized (Revenue Sandbox)
### Facts (authoritative inputs)
- `Projects_ProjectMonth_Amend_F`
- `SERVCONTRACTS_CustomerMonth_Billings_F`
- `TM_CustomerMonth_CRR_F`
- `LEGACYPROJECTS_CustomerMonth_Billings_F`
- `POSTING_DATA_F` (GL)

### Dimensions (conformed slicing)
- `FYCALENDAR_D` (fiscal calendar; completed-month logic lives here)
- `CUSTOMERS_D` (or the current customer dimension used for `Customer Key`)
- `DIVISIONS_D` (DivisionCode rollups to Company/Region/Division buckets)
- `PROJECTS_D` (projects attributes; stream-specific detail)
- `SERVCONTRACTS_D` (contract attributes; stream-specific detail)
- Other existing GL dims as currently used (ex: `GL_ACCT_D`) for market bucketing and reconciliation

### Method-selector / mapping tables
Current sandbox contains method-selector style tables (examples):
- `CustomerMonth_Stream_Method_F`
- `DivisionMonth_Stream_Method_F`

**Plan assumption:** these become **unnecessary** in the newer model if we are not doing per-customer/per-division/per-month method switching. Keep them only if needed for transition validation or explicit future overrides.

## Target Model Design (Recommended)
### A) Conformed "Totals" Layer (for CRR top-level reporting)
Goal: make "Total Revenue" and "Revenue by Stream" simple, consistent, and fast.

Preferred approach:
- Create a single reporting fact (name TBD), conceptually:
  - Grain: `Customer Key` x `Month End` x `Stream` (optional `Methodology`)
  - Columns: `Revenue Amount`, optional `Cost Amount` (nullable where not applicable)
  - Populated as a union of the authoritative stream facts listed above
- Relationships:
  - Join to shared dimensions only: `FYCALENDAR_D`, customer dimension, `DIVISIONS_D`

Notes:
- This table is intended for **CRR totals and stream mix**.
- This table is not required to carry every stream-specific attribute (project name, contract year, etc.).

### B) Stream-Specific Detail Layer (for drillthrough and operational context)
Keep stream facts related to their native dimensions for detail analysis:
- `Projects_ProjectMonth_Amend_F` -> `PROJECTS_D`
- `SERVCONTRACTS_CustomerMonth_Billings_F` -> `SERVCONTRACTS_D`
- `TM_CustomerMonth_Amend_F` -> existing T&M dimensions
- `TM_CustomerMonth_CRR_F` -> existing T&M dimensions
- `LEGACYPROJECTS_CustomerMonth_Billings_F` -> its natural legacy dimension(s)

This avoids forcing a polymorphic "one dimension fits all streams" design while still enabling deep detail views.

### C) If Mixed-Stream "Name/Type" Becomes Required
Defer this until a concrete report requirement exists.

Two escalation options:
1) Use a disconnected selector table + measures (lowest commitment).
2) Introduce a true unified `WORKITEM_D` dimension (higher commitment; requires stable keys and sparse attributes).

## Time Window + Calendar Rules (Important)
### Fiscal-year awareness
- Revenue windows must align to the fiscal calendar, not simply `#date(YYYY,1,1)`.
- Example: FY2021 includes months in late CY2020; if a fact table starts at `2021-01-01`, FY2021 totals will be incomplete.

### Completed-month behavior
- CRR measures commonly clamp to `FYCALENDAR_D[Is Completed Month] = TRUE`.
- Selected Methods should either:
  - adopt the same clamping consistently across streams, or
  - clearly separate "as-of" measures vs "full period" measures.

## Validation Plan (Before CRR Cutover)
### 1) Stream-level validation (Selected Methods)
- Projects (Amend): reconcile against known Amend benchmarks (job-cost and service project components).
- Service Contracts (Billings): reconcile against existing CRR service contract billings totals.
- T&M (Amend): reconcile against sandbox Amend totals and ensure expected variance vs CRR call-level if applicable.
- Legacy Projects (Billings): reconcile against its GL-approximation expectations (by company/region/division).

### 2) GL reconciliation
For each fiscal month and key rollups (Company/Region/Division):
- Compare:
  - `Selected Methods Revenue (by stream)`
  - `GL Revenue (bucketed: Projects / Contracts / Spot-T&M / Other)`
- Establish accepted tolerance and documented drivers for remaining deltas (timing/WIP, classification, unmapped markets).

### 3) Regression checks for known failure modes
- Early-year and carry-in: confirm carry-in windows are far enough back (current carry-in is 2015 for job-cost forecasts/change orders).
- Fiscal-year boundaries: confirm FY totals include all fiscal months.
- Division slicing: verify filters via `DIVISIONS_D` behave identically across streams and GL.

## Migration Phases (Deliverables)
### Phase 0: Lock definitions (this step)
- Confirm authoritative stream sources (done above).
- Confirm global rules:
  - completed-month clamping policy
  - fiscal-year window policy
  - carry-in start policy (projects)
- Confirm which method-selector tables are retired vs kept for transition.

### Phase 1: Build the newer revenue model
- Implement the authoritative stream facts and conformed dimensions.
- Optionally add the conformed "Totals" table for CRR top-level reporting.
- Keep GL measures/buckets for reconciliation.
- Add minimal "validation" measures only (no report redesign yet).

### Phase 2: Report Migration (preserve layout, replace logic)
Model-first, report-second:
- Keep the CRR report visuals/layout as the target UX where practical.
- Replace legacy/experimental DAX with the new "Selected Methods" measure set.
- Two implementation options (choose after Phase 1 validation):
  - **Rewire**: point the existing unfinished CRR report at the new semantic model, then remap fields/measures as needed while preserving pages.
  - **Recreate**: start a clean report on the new model and copy/import only the CRR pages that are worth keeping (layout-first), then bind visuals to new measures.

Validation during this phase:
- Parallel-run: keep legacy CRR measures available temporarily (deprecated) to compare side-by-side.
- Validate totals and key cuts (by fiscal year/month, company/region/division, top customers).
- Document and resolve remaining differences.

### Phase 3: Cutover
- Swap CRR visuals to point to new "Selected Methods" measures.
- Keep legacy measures temporarily as deprecated for reconciliation during a stabilization window.

### Phase 4: Cleanup
- Remove/retire legacy-only tables and measures that are no longer referenced.
- Finalize naming, folders, and documentation.

## Open Questions (To Answer Before Implementation)
- Do we standardize on a single date column name (ex: `Month End`) across all stream facts used in CRR?
- Do we require the conformed "Totals" table, or can CRR stay measure-based across separate facts for the first migration iteration?
- What is the official definition of "Total Revenue" in CRR:
  - sum of Selected Methods streams only, plus separate GL comparator
  - or include additional revenue categories outside these streams?
 - Report-layer choice after Phase 1:
   - Rewire the unfinished CRR report to the new model, or recreate the report on the new model while preserving the best pages/layout?
