# Model-Wide Measure & Time-Logic Guidelines

This document defines the **authoritative rules** for how measures in this model are designed, named, and interpreted. It exists to prevent semantic drift, avoid contradictory KPIs, and make the model defensible to finance, executives, and future maintainers.

If a measure violates any rule below, it should be **renamed, refactored, or hidden**.

---

## 1. Core Philosophy

### 1.1 One measure answers one question

A measure must encode:
- **What** it measures (revenue, retention, churn, status)
- **When** it measures (rolling vs period)
- **Who** it applies to (cohort vs population)

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
C. Retention & Health (Rolling / TTM)
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
- Service Contract Revenue PY (FY)
- Net Revenue Retention % (FY Period)
- Churn Rate % (FY Period)

### Rules
- Used only in FY tables, YoY charts, YTD visuals
- Never used on current-state KPI cards
- Never mixed with TTM measures in the same visual

---

## 5. Category C — Retention & Health (Rolling / TTM)

### Purpose
> "What is the retention state as of a specific snapshot in time?"

### Characteristics
- Rolling 12-month windows
- Snapshot-based, not period-based
- Executive-facing retention KPIs

### Anchor Rules (Mandatory)
- Anchor = **EOMONTH(last billing date)**
- PY window = 12 months prior to the same anchor
- Retention outcomes **freeze after churn**

### Canonical Measures
- Service Contract Revenue (TTM)
- Service Contract Revenue PY (TTM)
- Net Revenue Retention % (TTM)
- Gross Revenue Retention % (TTM)

### Optional Decomposition
- Contraction Revenue (TTM)
- Upsell Revenue (TTM)

### Explicitly Excluded
- Revenue Churn (TTM)
- Churn Rate % (TTM)

These are redundant once NRR / GRR exist in a fact-anchored model.

---

## 6. Category D — Operational Status & Lifecycle

### Purpose
> "Is the customer active *right now*?"

### Characteristics
- Today-anchored
- Month-end snapped
- State-based, not cohort-based

### Canonical Measures
- Service Contract Revenue (TTM – As Of Today)
- Months Since Last Contract Billing
- Customers Inactive 12+ Months
- Customers Churned (TTM)
- Logo Churn Rate % (TTM)
- Customer Contract Status

### Rules
- Safe for operational and CS dashboards
- Must not be used to explain revenue retention directly
- Can coexist with logo churn metrics

---

## 7. Anchor Date Conventions (Non-Negotiable)

| Metric Type | Anchor | Snapped? |
|-----------|-------|---------|
| Retention (TTM) | Last billing date | Yes (Month-end) |
| FY Performance | Calendar period | Yes (FY boundaries) |
| Operational Status | Today | Yes (Month-end) |

Mixing anchors inside a single measure is prohibited.

---

## 8. New Customers Handling

### Definition
A new customer satisfies:
- Service Contract Revenue (TTM) > 0
- Service Contract Revenue PY (TTM) = BLANK

### Behavior
- Included in revenue
- Excluded from retention
- Excluded from churn

This is correct and intentional.

---

## 9. Churn Semantics

### Revenue churn
- Expressed implicitly via NRR / GRR
- Not shown as a standalone TTM metric

### Logo churn
- Explicitly today-anchored
- Count-based
- Separate from revenue retention

These must never be conflated.

---

## 10. Fiscal Year Views

### Two valid questions

1. "What did retention look like **as of FY-end**?" → Use TTM snapshot logic
2. "What happened **during** the fiscal year?" → Use calendar/FY measures

TTM measures must never be repurposed to answer period questions.

---

## 11. Naming Rules (Enforced)

If a measure name does not explicitly indicate:
- Rolling vs Period
- Anchor type

…it is considered invalid.

---

## 12. Final Guiding Principle

> **Retention is a snapshot.**  
> **Fiscal years are periods.**  
> **Operational status is state-based.**

As long as these concepts remain separated, the model will remain correct, explainable, and trustworthy.

