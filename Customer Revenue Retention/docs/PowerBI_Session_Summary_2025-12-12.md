# Power BI Modeling Session Summary
**Date:** December 12, 2025  
**Model:** CRR v02.pbix

## Overview
Focused on revenue variance cleanup, total measures, division mapping, orphan-handling improvements, and documentation updates. No model files were modified in this summary step.

## Accomplishments
1. **Revenue variance fixed**  
   - Deduped service projects on `Project Number` before joining `CONTRACT_BILLABLE_F` in `PROJECT_REVENUE_F`, eliminating the -$80,696 variance.
   - Verified `Check_Revenue_Variance` goes to 0.

2. **Total measures added**  
   - `_Key Measures`: `Total Revenue`, `Total Cost`, `Total Gross Profit`, `Total GP %` (using totals), in the `Total` folder.

3. **Modeling guide updated** (`Code Snippets/modeling_guide_full.md`)  
   - Aligned to current facts/dims (Projects, Service Contracts, Spot), dedup/orphan strategies, and current DAX.  
   - Planned items (retention/renewal/segmentation) preserved in a “Planned” section.

4. **Division mapping**  
   - Built `DIVISIONS_D` from the provided mapping file; relationships intended to Projects/Service/Spot.  
   - Identified orphan rows causing “Unknown” division in visuals; proposed enriched orphan logic to look up division by contract number from staging.

## Issues / Risks
- **Orphan division “Unknown”:** Orphan rows set `Divisions = "Unknown"`, causing a blank division row (~$794k). Needs either mapping `UNKNOWN` or improved orphan logic.  
- **SERVCONTRACTS_D orphan logic:** Proposed M change needs the join fix (drop duplicate `AgreementKey` before full outer join) and a division lookup to reduce Unknowns.  
- **Accidental deletion (not restored here):** `SERVCONTRACTS_D.tmdl` was deleted in an earlier step; no restoration performed in this summary. (User will handle recovery.)

## Proposed Next Steps
1. **Orphan division enrichment:** Implement contract→division lookup from staging in orphan inference; fallback to “Unknown”; optionally add `UNKNOWN` to `DIVISIONS_D` to avoid blank rows.  
2. **By-Level reporting measures:** Add `Revenue by Level`, `Cost by Level`, `GP by Level`, `GP % by Level` using a disconnected `Level` table + `ISINSCOPE` to fix totals in visuals.  
3. **Optional Metrics calc group:** Revenue/Cost/GP/GP% for cleaner visual setup and centralized formatting.  
4. **Retention/Renewal:** Build when business rules are finalized (plans preserved in the guide).
