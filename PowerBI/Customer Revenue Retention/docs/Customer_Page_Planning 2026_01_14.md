# Customer Dashboard – Design & Logic Instructions

## Purpose
This page exists to answer four questions for any customer:
1. Who is this customer?
2. What are they worth?
3. What is changing?
4. Where is the risk or opportunity?

The design must work for:
- Customers with 1, 2, or all 3 revenue streams (Projects, Service Contracts, T&M)
- Both small and large customers
- A fixed 1920×1080 Power BI canvas

---

## Page Structure

The page is divided into five zones.

### A) Left Rail — Customer Identity
This section answers: **Who is this?**

Show:
- Customer name
- Status (Active, Dormant, Churned)
- Last billing date
- Active contracts
- Active projects
- Lifetime revenue
- Lifetime GP%
- Revenue rank

No charts or trends here. This is a static identity and scale anchor.

---

### B) Top KPI Strip — Customer Health (Rolling 12 Months)
This answers: **What are they worth and how are they performing right now?**

Always show:
- R12M Revenue  
- R12M GP%  
- NRR (Service Contracts only)  
- GRR (Service Contracts only)

Each KPI must display:
- Prior year value  
- Δ vs prior year  

This row should make it obvious whether the customer is improving or degrading.

---

### C) Hero Visual — What Is Changing?
This is the primary analytical visual on the page.

It must be driven by **Field Parameters**.

**X-axis:**  
Fiscal Year (e.g., FY2023, FY2024, FY2025, FY2026 YTD)

**Time context note:**  
This hero visual is intended to be **fiscal-year based** (aligned to the FY slicer and FY labels on the axis).  
The top KPI strip remains **R12M** to provide a “current health” view.

**Metric parameter (Values):**
- Revenue  
- Gross Profit $  
- GP %  

**Breakdown parameter (Legend):**
- Total (single-series)  
- By Stream (Projects, Service Contracts, T&M)  
- By Division  

This single visual replaces all separate “Revenue by Stream”, “Revenue by Division”, and “GP by Division” charts.

**Implementation note (to keep it 100% field-parameter-driven):**
- For the **Total (single-series)** option, use a disconnected 1-row “All” field (e.g., `Breakdown_All[All] = "Total"`) as a legend choice in the breakdown field parameter.
  - This produces a single series without requiring bookmarks or formatting toggles.
- The other legend choices should be connected dimensions (Stream/Division) so they correctly slice the measures.

---

### D) Risk & Opportunity Panel
This answers: **Where is the customer fragile or promising?**

Show small card-style metrics only. No large charts.

Include:
- % of revenue that is Service Contract (recurring base)
- Largest contract as % of total revenue (concentration risk)
- % of revenue from Projects (volatility)
- YoY change in Service Contract revenue (growth or decay)

These must work for customers with any combination of streams.

**Time context note:**  
Default these to **fiscal-year context** (to match the hero chart). If we later want a rolling perspective here, we can add R12M variants.

---

### E) Customer Matrix — Proof Layer
This is the detailed reconciliation table.

Show:
- Revenue, GP$, and GP%
- By Stream → Subsegment → Fiscal Year

The matrix must remain visible but compact. It supports trust and validation; it should not dominate the page.

---

## Design Rules

- Use fewer visuals with more meaning.
- One hero chart, one matrix, everything else supports them.
- Never assume all three revenue streams exist.
- Avoid visuals that go blank when a stream is missing.
- Prefer fiscal-year comparisons over month-level timelines.
- The page should tell a story before showing details.

---

## What the Page Must Communicate

At a glance, the user should be able to answer:
- Is this customer large or small?
- Are they growing or shrinking?
- Are they stable (contract-based) or volatile (project-driven)?
- Where is the risk or opportunity?

If a visual does not help answer one of these, it does not belong on this page.
