# Comparison Notes — Amend Reports vs CRR (Why numbers differ)

This is a short “why different totals” guide.

## Contracts: recognized vs billed
- Amend Contract Management revenue is **recognized** (schedule-based across contract term); billings are variance only.
- CRR service contract revenue is **billings** (`CONTRACT_BILLABLE_F → SERVCONTRACTS_REVENUE_F`).
Implication: month-by-month and customer totals can differ materially even if both are “correct” for their definitions.

## Projects: in-model earned vs precomputed monthly earned
- Amend Mechanical earned revenue is computed from costs/forecast/contract amount in the semantic model.
- CRR project revenue is a blend:
  - Job-costed projects: `JOB_MONTHLY_SUMMARY_F[Contract Earned Curr Mo]` (precomputed monthly earned)
  - Service projects: billing rows from `CONTRACT_BILLABLE_F[BILLABLE_ALL]` joined into the project stream
Implication: mismatches can arise from upstream vs in-model differences (forecast basis, CO handling, caps, timing).

## T&M: call-details billings vs call-level billable
- Amend Service Call Management uses `CALL_DETAILS_F[BILLING_AMOUNT]` (“amount billed”).
- CRR T&M uses `CALLS_F[Billable All]` for calls with no contract number.
Implication: if these fields are aligned in the warehouse, totals should match; if not, differences usually come from grain (detail vs call) or missing/duplicate call detail rows.

## Stream boundaries (double-count risks)
CRR includes explicit handling for “service projects” and contract-year keys:
- Excludes service projects from service contract billing/cost facts.
- Also includes some service billing as project revenue.
Amend Reports treat these boundaries differently (and some models include copied/orphaned measure tables), so stream totals may not be directly comparable without aligning classification rules.

## Calendar logic differences
CRR frequently uses `FYCALENDAR_D[Is Completed Month] = TRUE` in base measures.
Amend Reports frequently use `Max Date`, FYTD logic, and report page context filters.
Implication: partial-month and “as-of” behavior can differ.
