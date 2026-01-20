# Master Enrichment

Unified enrichment workflow for master customers. This is the preferred path for improving:
- `Company Website`
- `NAICS`
- `Industry Detail`

## Source of truth

- `data/enrichment/MasterEnrichment.csv` stores **verified** enrichment values and the confidence/rationale behind them.
- `data/enrichment/MasterWebsites.csv` can remain as a simple website-only store, but `MasterEnrichment.csv` is the long-term home.

## Workflow

1) Build a queue (prioritized by merge impact and missing fields):
```bash
python3 enrichment/build_master_enrichment_queue.py --limit 500
```
Output: `output/work/enrichment/MasterEnrichmentQueue.csv`

2) Fill in the approved fields:
- `Company Website (Approved)` (bare domain)
- `NAICS (Approved)`
- `Industry Detail (Approved)`
- `Enrichment Confidence` / `Enrichment Rationale`
- Optionally record attempt metadata:
  - `Attempt Outcome` (e.g. `No Web Presence`, `Ambiguous`, `Needs More Context`)
  - `Notes`

3) Apply to the enrichment source-of-truth:
```bash
python3 enrichment/apply_master_enrichment_queue.py
```

4) Regenerate final outputs:
```bash
python3 segment_customers.py
```
