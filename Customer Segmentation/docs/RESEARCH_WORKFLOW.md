# Research & Batching Workflow

This document outlines two related (but distinct) interactive workflows:

1) **Segmentation classification batching** (Industrial Group / Industry Detail / NAICS / Method) that flows into the segmentation overrides.
2) **Master enrichment batching** (Company Website + enrichment metadata) that flows into `data/enrichment/MasterEnrichment.csv`.

## Prerequisites

- Ensure the pipeline has been run recently (`dedupe_customers.py` -> `reconcile_overrides_to_masters.py` -> `segment_customers.py`) so `output/final/SegmentationReviewWorklist.csv` is up to date.
- Have `find_next_batch.py` available in the root directory.

For the enrichment queue workflow, also ensure `output/final/MasterCustomerSegmentation.csv` exists (run `python segment_customers.py` first).

## A) Segmentation Classification Loop (Overrides)

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

## B) Master Enrichment Loop (Websites / Verified vs Deferred)

This loop produces auditable master-level enrichment in `data/enrichment/MasterEnrichment.csv` and propagates into `output/final/MasterCustomerSegmentation.csv` on the next segmentation run.

If you are using Codex skills, this loop corresponds to `skills/batch_enrichment/SKILL.md`.

### 1. Build the Enrichment Queue
Generate a prioritized queue of masters that are missing website and/or have generic NAICS/detail.
```bash
python enrichment/build_master_enrichment_queue.py --limit 50
```
This writes `output/work/enrichment/MasterEnrichmentQueue.csv`.

### 2. Research & Populate Approved Fields
For each row you work:
- **Verified** (high confidence): fill one or more of:
  - `Company Website (Approved)`
  - `NAICS (Approved)`
  - `Industry Detail (Approved)`
  - set `Enrichment Status = Verified` and `Enrichment Source = Analyst`
- **Deferred** (ambiguous / no website): do not leave it blank:
  - set `Enrichment Status = Deferred`
  - fill `Enrichment Rationale` (short reason)
  - fill `Notes` (research narrative)

**Rule:** a `Verified` row must include at least one approved value, otherwise it will not be applied.

### 3. Human-In-The-Loop Review (Required)
Before applying, summarize what you’re about to apply (Verified list + Deferred list) and get an explicit “go” from the analyst/user.

### 4. Apply the Queue (Persist to MasterEnrichment)
Apply the queue into `data/enrichment/MasterEnrichment.csv`:
```bash
python enrichment/apply_master_enrichment_queue.py
```
Notes:
- Deferred-only rows are persisted (prevents “ghost deferrals” that only exist in markdown logs).
- The apply script writes a timestamped backup (`data/enrichment/MasterEnrichment_backup_before_apply_*.csv`) and refuses to massively shrink the file unless explicitly allowed.

### 5. Regenerate Final Outputs
```bash
python segment_customers.py
```

### 6. Verify Persistence
```bash
python audit_enrichment_persistence.py
```
Confirm `output/work/enrichment/EnrichmentPersistenceAudit_missing.csv` is empty.

## Handling Specific Cases

- **Invalid Records:** Mark `Industrial Group` as `Individual / Misc` and `Industry Detail` as `Invalid Record` or `Do Not Use`.
- **Unknowns:** If a customer cannot be identified after reasonable search, mark as `Unknown / Needs Review` in the batch file (or leave them out if you want to retry later, though marking them "Unclassified" explicitly helps track them).
- **Ambiguity:** If a name matches multiple companies (e.g., "Standard Oil"), look for context clues (location, "Inc", "LLC") or mark as `Unknown`.
