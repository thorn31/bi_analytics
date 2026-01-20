# Handoff (Resume Notes)

For the up-to-date operating mode (enrichment + iterative master maintenance), see `docs/PROCESS.md`.

## Current Pipeline

1) Dedupe / master mapping
```bash
python3 dedupe_customers.py
```
Outputs:
- `output/CustomerMasterMap.csv`
- `output/CustomerDeduplicationLog.csv`

2) Segmentation / classification (master-level, then joined back to keys)
```bash
python3 segment_customers.py
```
Outputs:
- `output/final/MasterCustomerSegmentation.csv` (master dimension)
- `output/final/CustomerSegmentation.csv` (key-level join output)

## Governance Inputs (What to Edit)

- `data/governance/MasterSegmentationOverrides.csv`: master-level segmentation governance (imported from batch markdowns).
- `data/governance/ManualOverrides.csv`: key-level dedupe override (master naming only).
- `data/enrichment/MasterWebsites.csv`: optional website enrichment (canonical → domain).

## Batch Import Workflow

Batch markdown files live in `data/batches/` (e.g. `data/batches/Batch4.md`).

Import a batch into the governance CSV:
```bash
python3 import_batch_overrides.py --input-md "data/batches/Batch4.md"
python3 segment_customers.py
```

Notes:
- Import normalizes section headings into the locked Industrial Group list.
- Retail/Hospitality are treated as **Support Category** (secondary), not a primary Industrial Group.
- Rows with `Method=AI-Assisted Search` are treated as “queued” (low confidence).

## Current Status (As of last run)

From `output/final/MasterCustomerSegmentation.csv` (masters = 2309):
- `Unknown / Needs Review` (Industrial Group): 663
- `Unclassified` (Method): 659
- `AI-Assisted Search` queued: 108

## Operational Notes

- If a CSV is open in Excel/Power BI, scripts may fail to overwrite it due to Windows file locks. Close the file and rerun.

