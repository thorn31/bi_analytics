# Website Enrichment

Goal: populate and maintain `Company Website` as a **bare domain** (e.g. `coldjet.com`) for master customers.

## Source of truth

- Approved websites live in `data/enrichment/MasterWebsites.csv` keyed by `Master Customer Name Canonical`.
- After updates, rerun `python3 segment_customers.py` to propagate to:
  - `output/final/MasterCustomerSegmentation.csv`
  - `output/final/CustomerSegmentation.csv`

## Workflow (recommended)

1) Ensure outputs are current:
```bash
python3 dedupe_customers.py
python3 reconcile_overrides_to_masters.py
python3 segment_customers.py
```

2) Build a ranked queue of masters missing websites:
```bash
python3 website_enrichment/build_website_queue.py --limit 500
```
Output: `output/website_enrichment/WebsiteEnrichmentQueue.csv`

If `data/sources/CUSTOMERS.D_DB.csv` is present, the queue also includes `Example Locations` (City/State) to help disambiguate research targets.

3) Research and fill in `Approved Website (fill in)` (bare hostnames only).

4) Apply approved values into `data/enrichment/MasterWebsites.csv`:
```bash
python3 website_enrichment/apply_website_queue.py
```

5) Refresh outputs:
```bash
python3 segment_customers.py
```

## Optional helpers

- Pull any websites already captured in master overrides (batch imports often include them):
```bash
python3 sync_master_websites_from_overrides.py
```

- Generate suggestion candidates (requires network access):
```bash
python3 suggest_master_websites.py --limit 50
```
Output: `output/website_enrichment/MasterWebsiteSuggestions.csv`
