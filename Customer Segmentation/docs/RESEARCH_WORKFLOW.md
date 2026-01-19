# Research & Batching Workflow

This document outlines the interactive process for researching and classifying "Unknown" or "Unclassified" master customers to burn down the review worklist.

## Prerequisites

- Ensure the pipeline has been run recently (`dedupe_customers.py` -> `reconcile_overrides_to_masters.py` -> `segment_customers.py`) so `output/final/SegmentationReviewWorklist.csv` is up to date.
- Have `find_next_batch.py` available in the root directory.

## The Loop

### 1. Identify Candidates
Run the helper script to find the next set of actionable customers (default 20, or specify a number).
```bash
python find_next_batch.py 40
```
*Note: This script filters out records that are already "Final" or "Queued" to avoid reworking settled items.*

### 2. Research
For each customer in the list, perform web searches to determine:
- **Industrial Group:** (e.g., Manufacturing, Commercial Services, Construction, Healthcare / Senior Living)
- **Industry Detail:** A brief, specific description (e.g., "HVAC Contractor", "Plastic Injection Molding").
- **NAICS Code:** The 6-digit NAICS code best matching their primary activity.
- **Domain:** The official company website domain (e.g., `company.com`).

*Tip: Use "AI-Assisted Search" as the `Method` for these batches.*

### 3. Create Batch File
Create a new markdown file in `data/batches/` (e.g., `data/batches/Batch_YYYYMMDD_BatchN.md`).
Format it as a series of markdown tables, grouped by `Industrial Group` for readability.

**Format:**
```markdown
# Batch Review YYYY-MM-DD Batch N

## Manufacturing

| Customer | Industry Detail | NAICS | Domain | Method |
|---|---|---|---|---|
| CUSTOMER NAME | Widget Mfg | 339999 | widget.com | AI-Assisted Search |

## Commercial Services

| Customer | Industry Detail | NAICS | Domain | Method |
|---|---|---|---|---|
| SERVICE CO | Janitorial | 561720 | service.com | AI-Assisted Search |
```

### 4. Import Decisions
Run the import script to apply these decisions to the master overrides file.
```bash
python import_batch_overrides.py --input-md "data/batches/Batch_YYYYMMDD_BatchN.md"
```

### 5. Reconcile & Refresh
Run the pipeline to match these new overrides to the latest masters and regenerate the worklist.
```bash
python reconcile_overrides_to_masters.py
python segment_customers.py
```

### 6. Repeat
Go back to **Step 1** to pull the next batch of unclassified records.

## Handling Specific Cases

- **Invalid Records:** Mark `Industrial Group` as `Individual / Misc` and `Industry Detail` as `Invalid Record` or `Do Not Use`.
- **Unknowns:** If a customer cannot be identified after reasonable search, mark as `Unknown / Needs Review` in the batch file (or leave them out if you want to retry later, though marking them "Unclassified" explicitly helps track them).
- **Ambiguity:** If a name matches multiple companies (e.g., "Standard Oil"), look for context clues (location, "Inc", "LLC") or mark as `Unknown`.
