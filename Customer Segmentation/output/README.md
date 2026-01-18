# Outputs

## Final deliverables (for Power BI / `CUSTOMERS_D` integration)

- `MasterCustomerSegmentation.csv`: **master-grain** customer dimension (one row per `Master Customer Name Canonical`)
- `CustomerSegmentation.csv`: **customer-key grain** join output (classification inherited from master)

These two files are the primary “final outputs” of the segmentation pipeline.

## Review outputs (what’s left to classify)

- `SegmentationReviewWorklist.csv`: masters that still need review (any of: `Method=Unclassified`, `Method=AI-Assisted Search`, or `Industrial Group=Unknown / Needs Review`)
- `runs/<timestamp>/SegmentationReviewWorklist.csv`: per-run snapshot copy of the worklist
- `runs/<timestamp>/RunSummary.csv`: per-run counts
- `RunHistory.csv`: append-only trend log of per-run counts

## Status / Method semantics

- `Status` represents governance state (`Final`, `Draft`, `Queued`) and primarily drives output confidence.
- `Method` represents how the classification was determined (e.g., `Rule-Based`, `Entity Inference`, `AI Analyst Research`).

## Supporting pipeline outputs (used to build / audit the deliverables)

- `dedupe/CustomerMasterMap.csv`: `Customer Key → Master Customer` bridge produced by the dedupe step
- `dedupe/CustomerDeduplicationLog.csv`: dedupe audit trail (use `IsMerge` + `MergeGroupSize` to focus on rollups)

## Workflow / helper artifacts (not final model outputs)

- `OverrideMismatchReport*.csv`, `OverrideCanonicalReconcile.csv`: help keep overrides aligned to the current master list
- `AI_Assisted_Suggestions.csv`: optional research queue / suggestion sheet
- `MasterWebsiteSuggestions.csv`: optional website suggestion sheet

## File locks

If Excel/Power BI has a CSV open, scripts may write a timestamped fallback file (same folder) instead of overwriting.
Those timestamped fallbacks are safe to delete once you’ve captured the run snapshot in `runs/<timestamp>/`.
