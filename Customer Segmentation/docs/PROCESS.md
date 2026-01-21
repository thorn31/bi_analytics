# Master Process (Current Operating Mode)

This repo is now operated as a **master data product**:
- You maintain **master-level governance state** over time (segmentation + enrichment).
- You re-run the pipeline to regenerate **final deliverables** for downstream use.
- Batch files are now primarily an **intake mechanism** (useful, but not the only way changes happen).

The original “burn down the segmentation worklist via batches” phase is largely complete; the day-to-day work is now:
- refine master merges (identity resolution)
- refine segmentation decisions and rules
- enrich master records (websites today; other attributes later)
- periodically ingest new customer extracts

## Where Things Live

### Source data (inputs)

- Raw customer extract(s): `data/sources/`
  - Current default input: `data/sources/CustomerLastBillingDate.csv`
  - Future: additional extracts can be added here without changing governance history.

### Governance (source of truth)

- Segmentation decisions: `data/governance/MasterSegmentationOverrides.csv`
- Master rollups/aliases (canonical → canonical): `data/governance/MasterMergeOverrides.csv`
- Key-level dedupe exceptions (legacy): `data/governance/ManualOverrides.csv`
- Approved websites (bare domains): `data/enrichment/MasterWebsites.csv`
- Analyst batch intake (markdown): `data/batches/`

### Generated outputs (do not hand-edit)

- Final deliverables: `output/final/`
  - `output/final/MasterCustomerSegmentation.csv`
  - `output/final/CustomerSegmentation.csv`
  - `output/final/SegmentationReviewWorklist.csv`
- Working artifacts: `output/work/`
  - `output/work/MasterSegmentationOverrides_reconciled.csv`
  - `output/work/OverrideMismatchReport.csv`
  - `output/work/OverrideCanonicalReconcile.csv`
- Snapshots: `output/runs/<timestamp>/`
- Dedupe artifacts: `output/dedupe/`
- Website enrichment artifacts: `output/website_enrichment/`

## Canonical Run Order

Run these in order when you’ve changed anything in dedupe/merges or governance:
```bash
python3 dedupe_customers.py
python3 reconcile_overrides_to_masters.py
python3 segment_customers.py
```

## Master-Level Workflow (Day-to-Day)

### A) Identity resolution / dedupe fixes

Use `data/governance/MasterMergeOverrides.csv` for canonical rollups (preferred).
Typical uses:
- fix spelling variations (e.g., `JW MARRIOT` → `JW MARRIOTT`)
- unify related entities to a single reporting master

Then rerun:
```bash
python3 dedupe_customers.py
python3 reconcile_overrides_to_masters.py
python3 segment_customers.py
```

### B) Segmentation tweaks

Master-level segmentation decisions live in `data/governance/MasterSegmentationOverrides.csv`.
How to apply changes:
- Through batch intake: `python3 import_batch_overrides.py --input-md "data/batches/Batch_*.md"`
- Or by editing the CSV directly (when doing small, careful adjustments)

Then rerun:
```bash
python3 reconcile_overrides_to_masters.py
python3 segment_customers.py
```

### C) Website enrichment (current enrichment focus)

There are two website-related sources of truth:
- **Verified enrichment** (web + NAICS + detail + audit metadata): `data/enrichment/MasterEnrichment.csv`
- **Approved websites** (lightweight fallback, bare domains): `data/enrichment/MasterWebsites.csv`

Recommended enrichment loop (Verified vs Deferred):
1) Build a ranked queue:
```bash
python3 enrichment/build_master_enrichment_queue.py --limit 50
```
2) Research and fill approved values in `output/work/enrichment/MasterEnrichmentQueue.csv`:
   - Verified: populate one or more of `Company Website (Approved)`, `NAICS (Approved)`, `Industry Detail (Approved)`
   - Deferred: set `Enrichment Status = Deferred` and fill `Enrichment Rationale` + `Notes` (narrative)
3) Human-in-the-loop check: summarize your intended Verified + Deferred updates and get explicit approval.
4) Apply the queue:
```bash
python3 enrichment/apply_master_enrichment_queue.py
```
5) Regenerate final outputs:
```bash
python3 segment_customers.py
```
6) Verify persistence:
```bash
python3 audit_enrichment_persistence.py
```

Optional helpers:
- Generate website suggestions: `python3 suggest_master_websites.py` (writes `output/website_enrichment/MasterWebsiteSuggestions.csv`)
- Harvest approved websites from overrides: `python3 sync_master_websites_from_overrides.py` (populates `data/enrichment/MasterWebsites.csv`)

Note: older scripts under `deprecated/website_enrichment/` are no longer the primary workflow.

## Publishing Outputs to Azure Blob (Power BI)

Recommended setup:
- Public logos: `stgreen/logos/` (already in place)
- Private datasets: `stgreen/datasets/customer_segmentation/`

After generating outputs, publish the two Power BI inputs:
```bash
py -3 publish_datasets_to_blob.py
```
If `az` is not on PATH:
```bash
py -3 publish_datasets_to_blob.py --az-path "C:\\Program Files\\Microsoft SDKs\\Azure\\CLI2\\wbin\\az.cmd"
```
This uploads only:
- `output/final/CustomerSegmentation.csv`
- `output/final/MasterCustomerSegmentation.csv`

## Adding New Customers (Future-Proofing)

Right now the pipeline reads a single extract: `data/sources/CustomerLastBillingDate.csv`.
When the ingestion process is formalized, the recommended approach is:
- keep raw extracts versioned by date in `data/sources/`
- update the default input pointer (or add a CLI flag) rather than rewriting governance history

Governance files should remain stable across new extracts:
- merges and segmentation overrides continue to apply to the evolving master list
- reconciliation reports highlight any mismatches introduced by new data

## What “Reconcile” Means

`python3 reconcile_overrides_to_masters.py` aligns override canonicals to the *current* master canonical list produced by dedupe.
Outputs:
- `output/work/MasterSegmentationOverrides_reconciled.csv` (used by segmentation when present)
- `output/work/OverrideMismatchReport.csv` (items needing manual attention)
