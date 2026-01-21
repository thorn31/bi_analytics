# Customer Segmentation (Deduping + Master Classification)

This repo produces:
- A **customer key → master customer** mapping (dedupe step)
- A **master-level segmentation table** (classification step)
- A **customer key-level join output** for integration back to `CUSTOMERS_D`

## Quickstart

1) Dedupe / master mapping
```bash
python3 dedupe_customers.py
```

2) Segmentation / classification
```bash
python3 segment_customers.py
```

For the current “operating mode” (ongoing enrichment + future customer ingestion), see `docs/PROCESS.md`.

## Key Files

**Inputs (`data/`)**
- `data/sources/CustomerLastBillingDate.csv`: raw customer list from source system.
- `data/governance/ManualOverrides.csv`: key-level overrides for **master naming** (dedupe).
- `data/governance/MasterSegmentationOverrides.csv`: master-level overrides for **segmentation** (governance).
- `data/governance/MasterMergeOverrides.csv`: master-level rollups for canonical naming.
- `data/enrichment/MasterWebsites.csv`: master canonical → approved website domain (bare hostname).
- `data/batches/Batch*.md`: analyst-produced batch classifications (importable).

**Outputs (`output/`)**
- Final deliverables:
  - `output/final/MasterCustomerSegmentation.csv`: master-level dimension (one row per master canonical).
  - `output/final/CustomerSegmentation.csv`: key-level join output (classification inherited from master).
- Review deliverables:
  - `output/final/SegmentationReviewWorklist.csv`: “what’s left to review” for segmentation.
  - `output/RunHistory.csv`: run-to-run trend log (counts).
- Supporting/audit outputs:
  - `output/dedupe/CustomerMasterMap.csv`: customer-level bridge table (dedupe output).
  - `output/dedupe/CustomerDeduplicationLog.csv`: audit log (filter `IsMerge=TRUE` for actual rollups).
- Workflow/helper artifacts are documented in `output/README.md`.

## Batch Workflow (Recommended)

For a detailed guide on the interactive research and classification loop, see [docs/RESEARCH_WORKFLOW.md](docs/RESEARCH_WORKFLOW.md).

1) Put analyst batch decisions in `data/batches/BatchN.md`
2) Import into the governance CSV:
```bash
python3 import_batch_overrides.py --input-md "data/batches/BatchN.md"
```
3) Regenerate outputs:
```bash
python3 segment_customers.py
```

## AI-Assisted Suggestion Helpers

Generate suggestion rows for unclassified masters:
```bash
python3 ai_assisted_suggest.py --limit 200 --sleep-seconds 0.2
```
Output: `output/work/AI_Assisted_Suggestions.csv`

Generate suggested official websites:
```bash
python3 suggest_master_websites.py
```
Output: `output/website_enrichment/MasterWebsiteSuggestions.csv`

## Publish to Azure Blob (Power BI)

Upload the two Power BI dataset inputs to Azure Blob Storage (and nothing else):
- `output/final/CustomerSegmentation.csv`
- `output/final/MasterCustomerSegmentation.csv`

Target path: `stgreen/datasets/customer_segmentation/`

Run:
```bash
py -3 publish_datasets_to_blob.py
```
If `az` is not on PATH:
```bash
py -3 publish_datasets_to_blob.py --az-path "C:\\Program Files\\Microsoft SDKs\\Azure\\CLI2\\wbin\\az.cmd"
```

## Notes
- Windows file locks: if a CSV is open in Excel/Power BI, scripts may write a timestamped fallback file instead of overwriting.
- Segmentation is computed **once per unique master**, then joined back to all customer keys.

## Current Status

From `output/final/MasterCustomerSegmentation.csv` (masters = 2309):
- `Unknown / Needs Review` (Industrial Group): 663
- `Unclassified` (Method): 659
- `AI-Assisted Search` queued: 108

See `docs/HANDOFF.md` and `docs/NEXT_STEPS.md` for the resume plan.
