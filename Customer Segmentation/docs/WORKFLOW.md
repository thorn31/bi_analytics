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

Optional: master-level rollups (alias → master) live in `data/governance/MasterMergeOverrides.csv`. This is the preferred way
to handle cases like “same company, different location/entity strings” without maintaining key-level overrides.
Batch imports and override reconciliation also consult this file so analysts can keep using common alias strings in
`data/batches/Batch*.md` while the pipeline writes decisions onto the rolled-up master.

Outputs:
- `output/dedupe/CustomerMasterMap.csv`: bridge table at `Customer Key` grain.
- `output/dedupe/CustomerDeduplicationLog.csv`: audit log (use `IsMerge` + `MergeGroupSize` to focus on rollups).

### Step 2 — Segmentation (Master Classification)

Run:
```bash
python3 segment_customers.py
```

Outputs:
- Final deliverables:
  - `output/final/MasterCustomerSegmentation.csv`: dimension at master grain.
  - `output/final/CustomerSegmentation.csv`: customer-key grain, classification inherited from master.

See `output/README.md` for which `output/` files are final vs workflow artifacts.

Review output:
- `output/final/SegmentationReviewWorklist.csv`: masters still needing review (queued/unclassified/unknown)
- `output/runs/<timestamp>/`: per-run snapshots + `RunSummary.csv`
- `output/RunHistory.csv`: trend log of counts per run

## Governance Inputs

### Master Segmentation Overrides

`data/governance/MasterSegmentationOverrides.csv` is the primary control surface for applying analyst-approved decisions:
- `Industrial Group` is treated as a locked list (import scripts normalize common section headings).
- `Status` is the governance signal:
  - `Final`: approved/accepted decision (high confidence in output)
  - `Queued`: needs research (low confidence in output)
  - `Draft`: provisional (medium confidence in output)
- `Method` is the provenance/technique (e.g. `Rule-Based`, `Entity Inference`, `AI Analyst Research`).

If you see “missing canonical” issues (override rows that don’t match current deduped masters), run:
```bash
python3 reconcile_overrides_to_masters.py
```
This writes:
- `output/work/MasterSegmentationOverrides_reconciled.csv` (preferred by `segment_customers.py` when present)
- `output/work/OverrideMismatchReport.csv` (what still needs manual rename/splitting)

### Import Analyst Batches

To import a markdown batch file (like `data/batches/Batch4.md`) into the overrides CSV:
```bash
python3 import_batch_overrides.py --input-md "data/batches/Batch4.md"
```

Notes:
- Batch imports write to `data/governance/MasterSegmentationOverrides.csv` (source of truth) and also refresh `output/work/MasterSegmentationOverrides_reconciled.csv` for segmentation.
- If Excel/Power BI has a CSV open, the script may write a timestamped fallback file instead of overwriting.

After editing any `data/batches/Batch*.md`, re-run the import for each changed batch file, then run:
```bash
python3 reconcile_overrides_to_masters.py
python3 segment_customers.py
```

## Enrichment

- Verified enrichment (websites + NAICS + detail + audit metadata) lives in `data/enrichment/MasterEnrichment.csv` and is applied via the enrichment queue:
  ```bash
  python3 enrichment/build_master_enrichment_queue.py --limit 50
  python3 enrichment/apply_master_enrichment_queue.py
  python3 segment_customers.py
  ```
- Approved website fallback lives in `data/enrichment/MasterWebsites.csv` (bare domains only).
- Optional helper: `python3 suggest_master_websites.py` writes `output/website_enrichment/MasterWebsiteSuggestions.csv` for review.
