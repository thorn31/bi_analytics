# Power BI Modeling Session Summary
**Date:** December 9, 2025
**Model:** CRR v02.pbix

## Overview
We are building a **Unified Revenue Model** that consolidates three distinct revenue streams: **Projects**, **Maintenance Contracts**, and **Spot/T&M**. 

Today, we successfully architected and implemented the **Project Stream** and began work on the **Maintenance Agreement Stream**.

## Accomplishments

### 1. Project Stream (Completed)
We unified "Standard Jobs" and "Service Projects" into a cohesive structure.
*   **Dimension (`PROJECTS_D`):** 
    *   Verified the union of `JOBSTRIMMED_D` and `SERVPROJECTS_D`.
    *   Confirmed `SurrogateProjectID` logic (`JOB_[Number]` and `SERV_[Number]`).
*   **Job Financials Staging (`JOB_FINANCIALS_F`):** 
    *   Created a staging table to fix the "Running Total" issue in `JOB_MONTHLY_SUMMARY_F`.
    *   Implemented Power Query "Lag" logic to calculate specific `Monthly Cost`.
*   **Unified Facts:**
    *   **`PROJECT_REVENUE_F`:** Combines monthly earned revenue from Jobs and billing revenue from Service Projects.
    *   **`PROJECT_COSTS_F`:** Combines calculated monthly job costs and daily service call costs for Service Projects.
*   **Relationships:**
    *   Resolved a key mismatch issue where `Job Key` was used instead of `Job Number`. The relationship between `PROJECTS_D` and Fact tables is now valid.

### 2. Maintenance Agreement Stream (In Progress)
We architected the solution for recurring maintenance revenue, handling the "Annual vs. Monthly" grain mismatch.
*   **Dimension (`SERVCONTRACTS_D`):**
    *   Created a new dimension based on `CONTRACTS_D`.
    *   Implemented "Explosion" logic (via `Wscontsq`) to generate one row per Contract Year.
    *   **Issue Identified:** "Master" and "Servant" contracts share the same Contract Number, causing Many-to-Many relationship errors.
    *   **Solution Proposed:** A "Group By" deduplication script (saved as `SERVCONTRACTS_D_Deduplicated.m`) to aggregate these into unique keys.
*   **Fact Definitions:**
    *   M-scripts generated for `SERVCONTRACTS_REVENUE_F` (Billing) and `SERVCONTRACTS_COSTS_F` (Calls), filtering **out** Service Projects.

## Critical Context for Next Session
*   **Master/Servant Contracts:** The source data (`CONTRACTS_D`) contains duplicate Contract Numbers for "Master" and "Servant" agreements. We are handling this by **Grouping/Aggregating** in Power Query to ensure unique keys in the dimension.
*   **Service Project Exclusion:** We rely on `PROJECTS_D` (specifically `Project Type = "Service Contract"`) to identify which contracts to **remove** from the Agreement stream to avoid double counting.
*   **Key Logic:** The `AgreementKey` is constructed as: `[Custnmbr] & [Source] & "_" & [Contract Number] & "_" & Text.From([YearIndex])`.
*   **Naming Convention:** We shifted from `AGREEMENT_...` to `SERVCONTRACTS_...` for table names.

## Next Steps

1.  **Fix `SERVCONTRACTS_D`:**
    *   Apply the deduplication script (`SERVCONTRACTS_D_Deduplicated.m`) to the `SERVCONTRACTS_D` query.
    *   Verify the relationship to Fact tables is 1:*.
2.  **Load & Validate Agreement Facts:**
    *   Create/Load `SERVCONTRACTS_REVENUE_F` and `SERVCONTRACTS_COSTS_F`.
    *   **INVESTIGATE ORPHANS:** Run DAX checks to ensure every row in these Fact tables has a corresponding key in `SERVCONTRACTS_D`. The deduplication logic might exclude or merge rows that the Fact table still expects.
3.  **Spot / T&M Stream:**
    *   Create `SPOT_FINANCIALS_F` from `CALLS_F` (Where `Contract Number` is Null).
4.  **Executive Measures:**
    *   Write the `[Total Revenue]` DAX measure summing across all three streams.
