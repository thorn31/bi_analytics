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

## Key Files

**Inputs (`input/`)**
- `input/CustomerLastBillingDate.csv`: raw customer list from source system.
- `input/ManualOverrides.csv`: key-level overrides for **master naming** (dedupe).
- `input/MasterSegmentationOverrides.csv`: master-level overrides for **segmentation** (governance).
- `input/MasterWebsites.csv`: master canonical → official website.
- `input/Batch*.md`: analyst-produced batch classifications (importable).

**Outputs (`output/`)**
- Final deliverables:
  - `output/MasterCustomerSegmentation.csv`: master-level dimension (one row per master canonical).
  - `output/CustomerSegmentation.csv`: key-level join output (classification inherited from master).
- Review deliverables:
  - `output/SegmentationReviewWorklist.csv`: “what’s left to review” for segmentation.
  - `output/RunHistory.csv`: run-to-run trend log (counts).
- Supporting/audit outputs:
  - `output/dedupe/CustomerMasterMap.csv`: customer-level bridge table (dedupe output).
  - `output/dedupe/CustomerDeduplicationLog.csv`: audit log (filter `IsMerge=TRUE` for actual rollups).
- Workflow/helper artifacts are documented in `output/README.md`.

## Batch Workflow (Recommended)

1) Put analyst batch decisions in `input/BatchN.md`
2) Import into the governance CSV:
```bash
python3 import_batch_overrides.py --input-md "input/BatchN.md"
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
Output: `output/AI_Assisted_Suggestions.csv`

Generate suggested official websites:
```bash
python3 suggest_master_websites.py
```
Output: `output/MasterWebsiteSuggestions.csv`

## Notes
- Windows file locks: if a CSV is open in Excel/Power BI, scripts may write a timestamped fallback file instead of overwriting.
- Segmentation is computed **once per unique master**, then joined back to all customer keys.

## Current Status

From `output/MasterCustomerSegmentation.csv` (masters = 2309):
- `Unknown / Needs Review` (Industrial Group): 663
- `Unclassified` (Method): 659
- `AI-Assisted Search` queued: 108

See `docs/HANDOFF.md` and `docs/NEXT_STEPS.md` for the resume plan.
