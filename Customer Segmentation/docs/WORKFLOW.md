# Workflow

## Goals

1) Produce a stable **Customer Key → Master Customer** mapping for reporting rollups.
2) Produce a stable **Master Customer segmentation dimension** for analysis.

## Pipeline

### Step 1 — Dedupe (Identity Resolution)

Run:
```bash
python3 dedupe_customers.py
```

Outputs:
- `output/CustomerMasterMap.csv`: bridge table at `Customer Key` grain.
- `output/CustomerDeduplicationLog.csv`: audit log (use `IsMerge` + `MergeGroupSize` to focus on rollups).

### Step 2 — Segmentation (Master Classification)

Run:
```bash
python3 segment_customers.py
```

Outputs:
- `output/MasterCustomerSegmentation.csv`: dimension at master grain.
- `output/CustomerSegmentation.csv`: customer-key grain, classification inherited from master.

## Governance Inputs

### Master Segmentation Overrides

`input/MasterSegmentationOverrides.csv` is the primary control surface for applying analyst-approved decisions:
- `Industrial Group` is treated as a locked list (import scripts normalize common section headings).
- `Method=AI-Assisted Search` is treated as a queue item (low confidence, needs further research).

### Import Analyst Batches

To import a markdown batch file (like `input/Batch4.md`) into the overrides CSV:
```bash
python3 import_batch_overrides.py --input-md "input/Batch4.md"
```

## Enrichment

- `input/MasterWebsites.csv` can be used to populate `Company Website` in the master dimension.
- `suggest_master_websites.py` generates a suggestion sheet you can review before approving.

