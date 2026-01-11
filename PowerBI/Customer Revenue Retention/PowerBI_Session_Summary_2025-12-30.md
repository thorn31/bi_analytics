# Power BI Modeling Session Summary
**Date:** December 30, 2025  
**Model:** CRR v03.pbip (Power BI Project)

## Overview
Refactored Service Contract retention to a cohort-based, slicer-respecting framework using a new agreement-grain monthly table and a standardized **R12M As-Of** measure pattern. Updated documentation to match the implemented design and resolved PBIP load issues caused by unsupported TMDL properties.

## Accomplishments
1. **Connected + model review**
   - Connected to the open Power BI Desktop file `CRR v03`.
   - Reviewed `CRR v03.SemanticModel` TMDL definitions and existing retention measures in `_Key Measures`.
2. **New retention foundation (agreement-grain)**
   - Added `SC_AgreementMonth_Revenue` (Power Query) at `AgreementKey × Month End` with `Customer Key` and `SC Revenue`.
   - Added relationships so slicers flow as “slice revenue only”:
     - `SC_AgreementMonth_Revenue[AgreementKey]` → `SERVCONTRACTS_D[AgreementKey]`
     - `SC_AgreementMonth_Revenue[Month End]` → `FYCALENDAR_D[Date]`
   - Kept `SC_CustomerMonth_Revenue` temporarily as legacy/transitional until the refactor is fully validated.
3. **R12M As-Of measure set created**
   - Implemented anchor + rolling window measures:
     - `Last SC Data Month End (In Slice)`
     - `As Of Month End (SC)`
     - `SC Revenue (R12M As Of)` and `SC Revenue PY (R12M As Of)`
   - Implemented customer-level component measures aggregated after per-customer evaluation:
     - `Retention Base PY (R12M As Of)`
     - `Churn / Contraction / Upsell Revenue (R12M As Of)`
   - Implemented KPIs:
     - `Net Revenue Retention % (R12M As Of)`
     - `Gross Revenue Retention % (R12M As Of)`
4. **Relationship intensity alignment**
   - Added aligned measures anchored to the same As-Of date:
     - `Project Revenue (R12M As Of)`
     - `T&M Revenue (R12M As Of)`
     - `Project Spend per Maintenance $ (R12M As Of)`
     - `T&M Spend per Maintenance $ (R12M As Of)`
5. **Anchor correctness fix**
   - Fixed the anchor to avoid “per-customer anchors” in customer tables by ensuring customer filters are removed when computing the As-Of date and last-data cap.
6. **Documentation updated**
   - Updated `Service_Contract_Retention_Model Revision 12-30-2025.md` to reflect the agreement-grain retention fact table, slicer semantics (“slice revenue only”), anchor rules, naming (`R12M As Of`), and a measure inventory.
7. **PBIP load error resolved**
   - Fixed a TMDL parsing error (`description` unsupported in table context) by removing the `description:` property from `SC_AgreementMonth_Revenue.tmdl`.

## Issues / Risks
- **Standalone MCP write operations failed in this environment:** metadata write calls returned `Failed to handle confirm request` (null reference). Workaround used: PBIP/TMDL edits + reload in Desktop. Running the standalone server with `--skipconfirmation` should avoid the confirm handshake issue.
- **Customer status measures may be skewed by $0 billings:** `ALL_BILLINGS_F` activity measures can treat 0.00 rows as “latest billing” unless filtered to non-zero activity.

## Proposed Next Steps
1. Add **Logo Retention** measures in the new framework:
   - Service Contract logo retention (slice-aware)
   - Any-revenue logo retention (across `ALL_BILLINGS_F`)
2. Audit and revise activity/status measures to ignore **zero billings** (define “activity” as non-zero billing amount).
3. Validate retention results with slicers (Division/Contract Type) and compare against legacy measures before hiding/retiring the Snapshot/TTM retention sets.
4. After validation, rebuild or remove `SC_CustomerMonth_Revenue` (derive it from `SC_AgreementMonth_Revenue` if still needed) and clean up legacy measures for clarity.
