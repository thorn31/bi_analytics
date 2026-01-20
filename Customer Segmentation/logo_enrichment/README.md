# Logo enrichment (Logo.dev)

This repo already maintains a clean `Company Website` domain for each master customer. The next step for Power BI branding is to map those domains to logo images.

Logo.dev supports a simple image CDN URL pattern:

`https://img.logo.dev/<domain>?token=<PUBLISHABLE_KEY>&size=128&format=png&retina=true&fallback=404`

Apistemic Logos supports a keyless URL pattern:

`https://logos-api.apistemic.com/domain:<domain>?fallback=404`

## Recommended workflow (no Power BI yet)

1) Build a queue from the current master output:
```bash
python3 logo_enrichment/build_logo_queue.py --limit 500
```
Output: `output/work/logos/LogoQueue.csv`

2) Verify a subset using a publishable key (stored in an environment variable):
```bash
export LOGO_DEV_PUBLISHABLE_KEY="..."
python3 logo_enrichment/verify_logo_queue.py --max-rows 50
```
Output: `output/work/logos/LogoVerifyReport_<timestamp>.csv`

Or verify against Apistemic (no token required):
```bash
python3 logo_enrichment/verify_logo_queue.py --provider apistemic --max-rows 50
```

Notes:
- Don’t pass tokens as CLI args (they can end up in shell history / logs). Use `LOGO_DEV_PUBLISHABLE_KEY`.
- `fallback=404` is used so “no logo” is detectable (HTTP 404) instead of a generated monogram.

## Long-term storage

If you decide to self-host cached logos later, store the hosted URL per master in `data/enrichment/MasterLogos.csv` (`Hosted Logo URL`) and point Power BI at that column.
