# Model-Wide Measure & Time-Logic Guidelines (v2)

**Version date:** December 30, 2025  
**Supersedes:** `model_wide_measure_time_logic_guidelines.md` (kept for historical reference)

This document defines the **authoritative rules** for how measures in this model are designed, named, and interpreted. It exists to prevent semantic drift, avoid contradictory KPIs, and make the model defensible to finance, executives, and future maintainers.

If a measure violates any rule below, it should be **renamed, refactored, or hidden**.

---

## 0. What changed in v2 (high level)

1. Retention metrics are standardized on **Rolling 12 Months, As-Of** semantics (`R12M As Of`) rather than “TTM/Snapshot” terminology.
2. Retention is computed from a **stable cohort fact** that supports slicers:
   - Primary: `SC_AgreementMonth_Revenue` (AgreementKey × Month End, sliceable by `SERVCONTRACTS_D`)
3. Anchor dates are computed **once per filter slice** and must **ignore customer filters** to avoid per-customer anchors in customer tables.
4. The model’s generic `Time Intelligence` calculation group is intended for **period measures** and must not be used to “time-shift” retention snapshots.

---

## 1. Core Philosophy

### 1.1 One measure answers one question

A measure must encode:
- **What** it measures (revenue, retention, churn, status)
- **When** it measures (rolling snapshot vs period performance)
- **Anchor** (As-Of data month end vs As-Of today vs fiscal period boundaries)

If any of those are ambiguous, the measure is invalid.

---

### 1.2 Time logic belongs in the measure, not the visual

- KPI cards must be correct with **no slicers applied**
- Time semantics must be **explicitly encoded in DAX**
- Visual context must never be relied on to imply meaning

---

## 2. The Four Measure Categories

All measures fall into exactly **one** of the following categories.

```
A. Core Financials (Absolute)
B. Period Performance (Calendar / FY)
C. Retention & Health (Rolling / R12M As Of)
D. Operational Status & Lifecycle
```

Measures from different categories **must not be mixed** on the same KPI surface without explicit labeling.

---

## 3. Category A — Core Financials (Absolute)

### Purpose
> "How much revenue, cost, or profit exists in the current filter context?"

### Characteristics
- No embedded time logic
- Fully slicer-driven
- Additive and reconcilable

### Examples
- Service Contract Revenue
- Project Revenue
- T&M Revenue
- Total Revenue
- Gross Profit
- GP %

### Rules
- Safe everywhere
- Never interpreted as retention or churn
- Never imply trend or health by themselves

---

## 4. Category B — Period Performance (Calendar / FY)

### Purpose
> "What happened *during* this fiscal period compared to another period?"

### Characteristics
- Calendar-driven
- Uses SAMEPERIODLASTYEAR, YTD, FY boundaries
- Sensitive to partial fiscal years

### Naming Rules (Required)
Measure names must include one of:
- (FY)
- (FY Period)
- (Calendar)
- (YoY)
- (YTD)

### Examples
- Service Contract Revenue PY (FY Period)
- (Legacy) Net Revenue Retention % (FY Period)

### Rules
- Used only in FY tables, YoY charts, YTD visuals
- Never used on current-state KPI cards
- Never mixed with `R12M As Of` measures in the same KPI visual without explicit labeling

---

## 5. Category C — Retention & Health (Rolling / R12M As Of)

### Purpose
> "What is the retention state as of a specific month-end anchor, using rolling 12-month windows?"

### Terminology
- **R12M** = Rolling 12 Months (preferred term)
- **As Of** = month-end anchor date used to define the rolling window
- “TTM” may appear in legacy measures, but new measures should use `R12M As Of`.

### Characteristics
- Rolling 12-month windows
- Snapshot-based, not period-based
- Executive-facing retention KPIs

### Anchor Rules (Mandatory)
- Anchor is always **month-end**.
- Anchor is capped to data availability in the *current slice*:
  - `As Of Month End = MIN(Selected Month End, Last Data Month End)`
- The anchor must be computed **once per slice** and must **ignore customer filters**.
  - Otherwise customer tables can accidentally compute a different anchor per customer.

### Cohort Source Rules (Mandatory)
- Retention must be computed from a stable cohort fact (not from raw facts directly).
- For Service Contract retention, the canonical cohort fact is:
  - `SC_AgreementMonth_Revenue` (AgreementKey × Month End; sliceable by `SERVCONTRACTS_D`)

### Slicer Semantics (Mandatory)
Retention measures are **“slice revenue only”**:
- If a user filters Division / Contract Type, retention is computed using only the service contract revenue within that slice.
- This is achieved by allowing filters to flow:
  - `SERVCONTRACTS_D` → `AgreementKey` → `SC_AgreementMonth_Revenue`

### Canonical Measures (Examples)
- SC Revenue (R12M As Of)
- SC Revenue PY (R12M As Of)
- Net Revenue Retention % (R12M As Of)
- Gross Revenue Retention % (R12M As Of)

### Optional Decomposition (Allowed)
These are allowed as *components* to audit NRR/GRR and build bridges:
- Churn Revenue (R12M As Of)
- Contraction Revenue (R12M As Of)
- Upsell Revenue (R12M As Of)

### Explicitly Discouraged
- Using generic time-intelligence calc items (MTD/QTD/YTD/PY) on `R12M As Of` measures.
  - These measures already encode time windows and an anchor; time-shifting them often produces misleading semantics.

---

## 6. Category D — Operational Status & Lifecycle

### Purpose
> "Is the customer active right now, and what is their lifecycle state?"

### Characteristics
- Today-anchored or data-month-end anchored (must be explicit)
- Month-end snapped
- State-based, not cohort-based

### Naming Rules (Required)
Names must explicitly state the anchor:
- `(As Of Today)` or `(As Of Data Month End)` or similar.

### Rules
- Safe for operational and CS dashboards
- Must not be used to explain revenue retention directly
- Can coexist with logo churn metrics

---

## 7. Anchor Date Conventions (Non-Negotiable)

| Metric Type | Anchor | Snapped? |
|-----------|--------|---------|
| Retention & Health | Month-end **As Of** (capped to last data month-end in slice) | Yes |
| FY Performance | Fiscal boundaries / calendar period | Yes |
| Operational Status | Today (month-end snapped) | Yes |

Mixing anchors inside a single measure is prohibited.

---

## 8. New Customers Handling (Retention)

### Definition (slice-aware)
A “new” customer in the current slice satisfies:
- `PY (R12M As Of) = BLANK() or 0`
- `CY (R12M As Of) > 0`

### Behavior
- Included in revenue
- Excluded from retention denominator and churn (for retention KPIs)

This is correct and intentional.

---

## 9. Churn Semantics

### Revenue churn (Service Contract churn)
- Represented via NRR/GRR and component measures (churn/contraction/upsell).
- A customer can be “churned” in a slice (e.g., Division A service contracts) while still billing elsewhere. This is expected under “slice revenue only”.

### Logo churn
- Count-based, separate from revenue retention
- Two valid definitions (keep separate measures):
  - **Service Contract logo churn** (SC-only)
  - **Any-revenue logo churn** (across all streams)

These must never be conflated.

---

## 10. Fiscal Year Views (How to interpret R12M As Of by FY)

Two valid questions:

1. "What did retention look like **as of FY-end**?"  
   - Use `R12M As Of` measures in a visual grouped by Fiscal Year.
   - Interpretation: each FY row anchors to the last date of that FY, then caps to last available data month-end.

2. "What happened **during** the fiscal year?"  
   - Use Category B period measures (FY/YTD), not `R12M As Of`.

---

## 11. Calculation Groups (Usage Rules)

### `Time Intelligence` calculation group
- Intended for Category A and Category B measures.
- Must not be relied on to provide the meaning of Category C/D measures.
- Do not apply it to `R12M As Of` retention KPIs unless a calc item is explicitly authored for snapshot semantics.

---

## 12. Naming Rules (Enforced)

If a measure name does not explicitly indicate:
- Rolling vs Period
- Anchor type

…it is considered invalid.

---

## 13. Final Guiding Principle

> **Retention is a snapshot (As Of).**  
> **Fiscal years are periods.**  
> **Operational status is state-based.**

As long as these concepts remain separated, the model will remain correct, explainable, and trustworthy.

