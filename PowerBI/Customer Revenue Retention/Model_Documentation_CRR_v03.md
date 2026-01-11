# CRR v03 Semantic Model – Current Documentation

**Last Updated:** December 30, 2025  
**PBIP:** `Customer Revenue Retention/CRR v03.pbip`  
**Semantic Model:** `Customer Revenue Retention/CRR v03.SemanticModel`  
**Purpose:** Unified analysis of revenue, cost, profitability, customer activity, and service-contract retention across Projects, Service Contracts, and T&M (Spot).

---

## 1. Modeling Objectives

- Provide a consolidated view over three revenue streams:
  - **Projects** (jobs + service projects modeled as projects)
  - **Service Contracts** (agreement billing + agreement costs)
  - **T&M / Spot** (non-contract calls billed as ad-hoc work)
- Support both **company-wide** and **customer-level** analysis with consistent totals and slicer behavior.
- Provide a retention framework that is:
  - **Cohort-based**
  - **Auditable (components available)**
  - **Stable across visuals**
  - **Sliceable by Service Contract attributes** (e.g., Division, Contract Type) as “slice revenue only”.

---

## 2. Source Systems & Naming

- Primary source is Snowflake (curated warehouse objects accessed via Power Query).
- Naming conventions:
  - `*_D` for dimensions, `*_F` for facts.
  - `AgreementKey` is the service-contract/year grain key used throughout Service Contract facts and dimensions.
  - `SurrogateProjectID` is the unified project grain key used throughout project facts and dimensions.
  - Measures are centralized in the `_Key Measures` table.

---

## 3. Query Organization (Power Query)

The model uses query groups to keep staging logic separate from dimensional/fact outputs.

| Query Group | Purpose | Examples |
|-------------|---------|----------|
| **Staging** | Upstream/base tables and intermediate queries that feed multiple downstream tables. | `CALLS_F`, `SERVPROJECTS_D`, `JOBSTRIMMED_D`, `JOB_FINANCIALS_F`, `SERVCONTRACTS_D_STAGING` |
| **Dim** | Final dimensions exposed to the model. | `CUSTOMERS_D`, `FYCALENDAR_D`, `PROJECTS_D`, `SERVCONTRACTS_D`, `DIVISIONS_D` |
| **Facts** | Revenue/cost facts and retention cohort facts. | `PROJECT_REVENUE_F`, `PROJECT_COSTS_F`, `SERVCONTRACTS_REVENUE_F`, `SERVCONTRACTS_COSTS_F`, `SPOT_FINANCIALS_F`, `ALL_BILLINGS_F`, `SC_AgreementMonth_Revenue` |
| **Diagnostics** | Helpers and QA checks (limited). | measure-based checks in `_Key Measures` |

---

## 4. Core Dimensions

### 4.1 `CUSTOMERS_D`
- Customer master dimension keyed by `Customer Key`.
- Used for customer-level filtering, drilldowns, and cohort aggregation.

### 4.2 `FYCALENDAR_D`
- Date table (daily grain) with fiscal attributes (Fiscal Year, Fiscal Month, etc.).
- Used as the primary calendar for all time filtering and time-intelligence calculations.

### 4.3 `PROJECTS_D`
- Unified project dimension spanning:
  - **Service Projects** (sourced from contracts marked as “SERVICE PROJECT”)
  - **Jobs** (standard job dimension rows)
- Key: `SurrogateProjectID`
  - Service projects: `SERV_<Customer Number>_<Project/Contract Number>`
  - Jobs: `JOB_<Customer Key>_<Job Key>`

### 4.4 `SERVCONTRACTS_D_STAGING`
- Staging contract-year exploded dimension (agreement billing grain) used as the base for the final service contract dimension and orphan handling.

### 4.5 `SERVCONTRACTS_D`
- Final service contract dimension keyed by `AgreementKey`.
- Includes orphan-handling logic so agreement keys that appear in facts but not in the source dimension are surfaced with an `OrphanSource` label.
- Important descriptive slicers live here (e.g., `Divisions`, `Contract Type`), and are intentionally used to slice retention (see Section 7).

### 4.6 Stream/Metric helper dimensions (disconnected, used by measures)

#### `Revenue_Stream_D`
Disconnected stream selector table with the canonical set:
- `Project`, `Service Contract`, `T&M`

#### `Stream_Subsegment_D`
Disconnected “subsegment” table used for stream-specific breakdowns:
- Projects: `DIVISIONS_D[Region]`
  - Service Contracts: `SERVCONTRACTS_D[Contract Type]`
  - T&M: a single `T&M` row

#### `FINANCIAL_METRIC_D` and `Metric Selector`
Supports metric selection (e.g., Revenue vs GP %) and correct routing by stream/subsegment via measure logic (using `TREATAS` patterns and validity checks).

---

## 5. Fact Tables (Revenue/Cost)

### 5.1 Projects

#### `PROJECT_REVENUE_F`
Unifies:
- Job earned revenue (from job financials)
- Service project billing (from contract billing joined to service projects)

#### `PROJECT_COSTS_F`
Unifies:
- Job costs (monthly deltas from job cumulative cost)
- Service project call costs (from calls joined to service projects)

Fan-out risk is mitigated by deduplicating service-project join keys before joining billing/calls (prevents double counting).

### 5.2 Service Contracts

#### `SERVCONTRACTS_REVENUE_F`
- Service contract billing, excluding service-project contracts to prevent double counting across streams.
- Grain: billing transactions at agreement-year (`AgreementKey`) level.

#### `SERVCONTRACTS_COSTS_F`
- Service contract costs from calls tied to contract numbers (excluding service projects and excluding null/blank contract numbers).
- Grain: call rows mapped to agreement-year (`AgreementKey`) level.

### 5.3 T&M / Spot

#### `SPOT_FINANCIALS_F`
- Spot/T&M is modeled from calls where contract number is null/blank.
- Provides `Revenue` and `Cost` at call-level grain with `Customer Key` and `Divisions`.

### 5.4 Unified billing/activity

#### `ALL_BILLINGS_F`
Monthly activity support table built by combining:
- Service Contract billings
- Project billings
- T&M billings

Used for “customer activity/recency” measures (e.g., last billing date across any stream).

---

## 6. Retention Cohort Facts (Power Query)

### 6.1 `SC_AgreementMonth_Revenue` (primary retention fact)

**Grain:** `AgreementKey × Month End`  
**Columns:** `AgreementKey`, `Customer Key`, `Month End`, `SC Revenue`

This table exists only to support cohort-based retention KPIs and to ensure retention respects service contract slicers:
- `SERVCONTRACTS_D` filters AgreementKey
- AgreementKey filters `SC_AgreementMonth_Revenue`

### 6.2 `SC_CustomerMonth_Revenue` (legacy/transitional)

**Grain:** `Customer Key × Month End`  
Kept temporarily for backwards compatibility; planned to be removed after refactor validation. If retained long-term, it should be derived from `SC_AgreementMonth_Revenue` to maintain a single source of truth.

---

## 7. Retention & Time Logic (Measure Layer)

All measures are defined under `_Key Measures`.

### 7.1 R12M As-Of retention framework (current canonical approach)

- Retention KPIs are defined as **Rolling 12 Months (R12M)** ending at an **As-Of month end anchor**.
- The anchor is capped at last available month-end with Service Contract data within the current contract slice.
- Customer-level evaluation is performed before aggregation (ensures company totals match customer-level math).

Key measures (current implementation):
- Anchor helpers:
  - `Last SC Data Month End (In Slice)`
  - `As Of Month End (SC)`
- Windows:
  - `SC Revenue (R12M As Of)`
  - `SC Revenue PY (R12M As Of)`
- Components:
  - `Retention Base PY (R12M As Of)`
  - `Churn Revenue (R12M As Of)`
  - `Contraction Revenue (R12M As Of)`
  - `Upsell Revenue (R12M As Of)`
- KPIs:
  - `Net Revenue Retention % (R12M As Of)`
  - `Gross Revenue Retention % (R12M As Of)`

### 7.2 FY Period (“Snapshot”) measures (legacy)

The model still contains FY-period retention measures and older “TTM” measures for compatibility while validation is ongoing. The intent is to standardize on `R12M As Of` naming and semantics for retention/health KPIs and keep FY-period measures only where the question is explicitly “what happened during the period”.

### 7.3 Relationship intensity measures (aligned)

The model includes relationship intensity measures (e.g., project/T&M spend per maintenance dollar). New versions are aligned to the same `R12M As Of` anchor (e.g., `Project Spend per Maintenance $ (R12M As Of)`).

---

## 8. Relationships (High-Level)

### 8.1 Shared dimensions
- Most facts relate to `FYCALENDAR_D[Date]` for time filtering.
- Customer filtering is centered on `CUSTOMERS_D[Customer Key]`.

### 8.2 Project stream
- `PROJECT_REVENUE_F[SurrogateProjectID]` → `PROJECTS_D[SurrogateProjectID]`
- `PROJECT_COSTS_F[SurrogateProjectID]` → `PROJECTS_D[SurrogateProjectID]`

### 8.3 Service contract stream
- `SERVCONTRACTS_REVENUE_F[AgreementKey]` → `SERVCONTRACTS_D[AgreementKey]`
- `SERVCONTRACTS_COSTS_F[AgreementKey]` → `SERVCONTRACTS_D[AgreementKey]`
- `SERVCONTRACTS_D[Custnmbr Key]` → `CUSTOMERS_D[Customer Key]`

### 8.4 Retention cohort fact
- `SC_AgreementMonth_Revenue[AgreementKey]` → `SERVCONTRACTS_D[AgreementKey]`
- `SC_AgreementMonth_Revenue[Month End]` → `FYCALENDAR_D[Date]`

---

## 9. Known Data-Quality / Design Considerations

- **Service contract orphans:** `SERVCONTRACTS_D` includes explicit orphan handling to surface agreement keys that exist in facts but not in source dimension rows.
- **Fan-out risks on service project mapping:** Some `Project Number` values can map to multiple project keys; project revenue/cost queries deduplicate keys before joining to avoid double counting.
- **$0 billing activity rows:** Customer activity/recency logic can be skewed if “latest billing” includes 0.00 billing amounts; activity measures should eventually filter to non-zero billing amounts.
- **As-Of anchoring:** Retention KPIs are snapshots; fiscal-year grouping implies “as of FY-end” snapshots for historical years and caps to last available data for the current year.

---

## 10. Next Documentation/Modeling Steps

1. Add and document **Logo Retention** measures in the new framework:
   - Service Contract logo retention (slice-aware)
   - Any-revenue logo retention (across all streams)
2. Decide and document a canonical definition of “activity” for customer status measures (exclude $0 billings).
3. After validation, hide/retire legacy retention measures and remove or rebuild `SC_CustomerMonth_Revenue` from `SC_AgreementMonth_Revenue`.

