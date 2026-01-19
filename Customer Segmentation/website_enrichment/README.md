# Website Enrichment

Goal: populate and maintain `Company Website` as a **bare domain** (e.g. `coldjet.com`) for master customers.

## Source of truth

- Approved websites live in `input/MasterWebsites.csv` keyed by `Master Customer Name Canonical`.
- After updates, rerun `python3 segment_customers.py` to propagate to:
  - `output/MasterCustomerSegmentation.csv`
  - `output/CustomerSegmentation.csv`

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

3) Research and fill in `Approved Website (fill in)` (bare hostnames only).

4) Copy approved values into `input/MasterWebsites.csv`.

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
Output: `output/MasterWebsiteSuggestions.csv`
