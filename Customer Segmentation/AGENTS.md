# Agent Instructions (Customer Segmentation repo)

## What this repo does

This repo generates:
- Dedupe: `Customer Key → Master Customer Name`
- Segmentation: master-level customer classification with auditability

## Entry points

Run in this order:
```bash
python3 dedupe_customers.py
python3 segment_customers.py
```

## Governance

- Master-level decisions live in `input/MasterSegmentationOverrides.csv`.
- Analyst batch markdowns are imported via:
```bash
python3 import_batch_overrides.py --input-md "input/BatchN.md"
```

## Notes

- Retail/Hospitality are treated as secondary `Support Category`, not a primary `Industrial Group`.
- Windows file locks (Excel/Power BI) can block overwriting CSV outputs.

