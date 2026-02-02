# Service Contract Retention Model – Overview

## Objective

Provide **consistent, auditable, and scalable** retention metrics (NRR, GRR, churn, contraction, upsell, logo retention) for **Service Contracts**, while remaining compatible with:

- Multi-stream revenue model (Service Contracts, Spot, Projects)
- Customer-level and company-wide reporting
- Modern Power BI features (Calculation Groups, Field Parameters)
- Existing base revenue / cost / GP measures

---

## Core Design Principles

1. **Retention is a cohort problem, not a raw fact problem**
2. **Cohort grain must be stable across views**
3. **Descriptive dimensions must not decide data existence**
4. **Time anchoring must respect data availability, not slicer selection**

---

## New Retention Architecture

### 1. Dedicated Retention Fact Tables (Power Query)

#### Primary table (sliceable by contract attributes)

**Table:** `SC_AgreementMonth_Revenue`

**Grain**
```
AgreementKey × Month End
```

**Key Columns**
- `AgreementKey`
- `Customer Key` (e.g. `CN991805SERV_GP`)
- `Month End` (EOMONTH-based)
- `SC Revenue`

**Characteristics**
- Built in **Power Query**, not DAX
- One row per agreement per billing month
- Enables retention to respect slicers on `SERVCONTRACTS_D` (Division, Contract Type, etc.)
- Stable grain for cohort math (no dependence on descriptive dimensions like Customer Name)

**Model relationships (required for slicing)**
- `SC_AgreementMonth_Revenue[AgreementKey]` → `SERVCONTRACTS_D[AgreementKey]`
- `SC_AgreementMonth_Revenue[Month End]` → `FYCALENDAR_D[Date]`

This table exists **only** to support retention calculations.

#### Secondary table (legacy / transitional)

**Table:** `SC_CustomerMonth_Revenue`

**Grain**
```
Customer Key × Month End
```

**Purpose**
- Kept temporarily for backwards compatibility and ad-hoc validation
- Planned to be removed after refactor is fully validated
- If retained long-term, it should be treated as a rollup derived from `SC_AgreementMonth_Revenue` (single source of truth)

---

### 2. Time Anchoring (“As Of” Logic)

Retention metrics do **not** rely directly on slicer-selected dates for meaning.

Instead:
- Anchor to the **last month with actual Service Contract data**
- Cap user-selected periods at that month

**Conceptual Flow**
```
Selected Month End (from calendar context)
    ↓
Last SC Data Month End (in current contract slice)
    ↓
As Of Month End = MIN(Selected, Last Data)
```

**Critical rule (prevents per-customer anchors)**
- The anchor is computed **once per filter slice** (division/contract type/date context), and must **ignore customer-level filters**.
- Without this, customer tables can accidentally evaluate retention using each customer's last billing month, which is not a portfolio-consistent anchor.

This prevents:
- Future periods returning blanks
- Partial-period distortion
- Inconsistent totals between company and customer views

---

### 3. Retention Measure Pattern

All retention KPIs follow the same structure.

#### Base Definitions (Per Customer)

- **Base Revenue (PY)**  
  Revenue in the comparison window (TTM or FY)

- **Current Revenue (CY)**  
  Revenue in the current window

#### Revenue Components

| Component | Definition |
|---------|------------|
| Churn | PY > 0 AND CY = 0 |
| Contraction | PY > CY |
| Upsell | CY > PY |

#### KPI Formulas

```
GRR = (Base - Churn - Contraction) / Base
NRR = (Base - Churn - Contraction + Upsell) / Base
```

All aggregation occurs **after** customer-level evaluation.

---

## Slicer Semantics (Important)

### “Slice revenue only” (implemented behavior)

When a user filters to a Division / Contract Type, retention is computed using **only the service contract revenue that belongs to that slice**.

This is achieved by anchoring retention on `SC_AgreementMonth_Revenue` and allowing slicers to flow:
`SERVCONTRACTS_D` → `AgreementKey` → `SC_AgreementMonth_Revenue`.

**Expected outcome**
- A customer can be “churned” in Division A (no longer billing there) while still active overall in other divisions/streams. This is correct for slice-level retention.

### “Customer overall” (optional alternate)

If a report page needs “customer overall retention regardless of division/contract slicers”, that should be implemented as **separate, explicitly labeled measures** (never ambiguous reuse).

---

## Interaction with Existing Model

- Existing **00 Base / 01 Revenue / 02 Cost / 03 Gross Profit** measures remain unchanged
- Division slicing (e.g., Nashville, Knoxville) continues to apply to standard revenue visuals
- Retention KPIs source Service Contract cohort data **exclusively** from `SC_AgreementMonth_Revenue`

Retention logic is intentionally isolated from:
- Project revenue
- Spot revenue
- Contract-level operational attributes

---

## Logo Retention Strategy

Two intentional definitions:

### Service Contract Logo Retention
- Based solely on service contract activity
- Answers: *Did the customer retain service contracts?*

### Any-Revenue Logo Retention
- Based on activity across all revenue streams
- Answers: *Did we lose the customer entirely?*

These are modeled as **separate measures**, not parameterized logic.

---

## Differences vs Previous Implementation

### Prior Approach

- Retention logic embedded directly in fact-table measures
- Heavy use of `VALUES(CUSTOMERS_D)` and `SAMEPERIODLASTYEAR`
- Anchor dates derived from fact context
- Report-level descriptive filters affecting retention math
- High measure coupling and limited transparency

### Current Approach

| Area | Previous | Current |
|----|----|----|
| Cohort Definition | Implicit | Explicit table |
| Grain | Dynamic | Fixed |
| Time Anchor | Context-driven | Data-driven |
| Filter Stability | Fragile | Controlled |
| Debuggability | Low | High |
| Reuse | Limited | High |

---

## Scope Boundaries

- `SC_AgreementMonth_Revenue` is **not** used for:
  - Gross profit calculations
  - Division-based financial reporting
  - Revenue mix visuals
- Retention KPIs should not rely on descriptive attributes such as Customer Name for data existence

---

## Naming and Measure Inventory

### Naming convention

Retention measures should use:
- `R12M As Of` to mean “rolling 12 months ending at an anchored month end”
- Explicit “FY Period” naming when a measure answers a true fiscal period question (legacy measures may remain temporarily)

### Key measures (current implementation)

**Anchor helpers**
- `Last SC Data Month End (In Slice)`
- `As Of Month End (SC)`

**R12M windows**
- `SC Revenue (R12M As Of)`
- `SC Revenue PY (R12M As Of)`

**Components**
- `Retention Base PY (R12M As Of)`
- `Churn Revenue (R12M As Of)`
- `Contraction Revenue (R12M As Of)`
- `Upsell Revenue (R12M As Of)`

**KPIs**
- `Net Revenue Retention % (R12M As Of)`
- `Gross Revenue Retention % (R12M As Of)`

**Relationship intensity (aligned to the same anchor)**
- `Project Spend per Maintenance $ (R12M As Of)`
- `T&M Spend per Maintenance $ (R12M As Of)`

---

## Outcome

This design produces retention metrics that are:
- Consistent across customer and portfolio views
- Auditable and explainable
- Extensible to additional time windows and future logo retention definitions (SC-only vs Any-Revenue)
