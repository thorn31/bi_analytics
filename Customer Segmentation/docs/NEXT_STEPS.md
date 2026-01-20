# Next Steps

## 1) Burn Down the AI Queue (Fastest ROI)

Filter `output/final/MasterCustomerSegmentation.csv` where `Method == AI-Assisted Search` (currently 108 masters).
- Research and decide `Industrial Group` / `Industry Detail` / `NAICS` / `Method`
- Persist decisions in `data/governance/MasterSegmentationOverrides.csv`
- Re-run `python3 segment_customers.py`

## 2) Prioritize Remaining Unclassified Masters

Filter `Method == Unclassified` and prioritize by:
- `IsMerge == TRUE` first
- then highest `MergeGroupSize`

These masters roll up multiple customers and have the highest reporting impact.

## 3) Convert Repeated Patterns into Tier 1 Rules

As repeated “unknown” themes emerge (common keywords, suffix patterns, etc.), add deterministic rules in:
- `customer_processing.py` → `classify_customer()`

Goal: prevent future Unknowns rather than only fixing existing ones.

## 4) Improve Website Enrichment

If needed:
- Run `python3 suggest_master_websites.py --limit 50`
- Copy approved URLs into `data/enrichment/MasterWebsites.csv`
- Re-run `python3 segment_customers.py`

