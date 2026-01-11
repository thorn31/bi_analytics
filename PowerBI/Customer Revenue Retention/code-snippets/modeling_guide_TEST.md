# POWER BI MODELING GUIDE — Unified Revenue Model (Actual Implementation)
**Version:** 5.0 (Reflecting CRR v02.pbix State)
**Date:** December 12, 2025

---

## 0. Table of Contents
1. Overview & Architecture
2. Data Flow: Snowflake to Power BI
3. Fact Tables (Final State)
4. Dimension Tables (Final State)
5. Revenue Stream Definitions
6. Data Integrity & Orphan Handling
7. Reconciliation Checks
8. DAX Measures Library (Current State)
9. Gap Analysis: v5.0 vs v4.0 (Pending Implementation)

---

## 1. Overview & Architecture

This model unifies three distinct revenue streams into a coherent financial reporting structure. Unlike the raw Snowflake schema, the Power BI model transforms and splits data based on **Business Logic** rather than **Source System** tables.

### The Three Streams
1.  **Projects (Jobs + Service Projects):** Long-term, defined scope work.
2.  **Agreements (Maintenance Contracts):** Recurring revenue and associated service costs.
3.  **Spot (T&M):** One-off, transactional service calls not tied to a contract or project.

---

## 2. Data Flow: Snowflake to Power BI

The model does not simply load the Snowflake tables. It transforms them into logical streams.

### 2.1 Project Stream Transformation
*   **Source:**
    *   `JOB_MONTHLY_SUMMARY_F` (Job Revenue/Cost)
    *   `CONTRACT_BILLING_F` (Service Project Billing)
    *   `CALLS_F` (Service Project Costs)
    *   `JOBS_D` + `CONTRACTS_D` (Service Projects)
*   **Transformation:**
    *   **Dimension:** `PROJECTS_D` constructed by unioning `JOBS_D` and `CONTRACTS_D` (where type = "Service Contract"). Key: `SurrogateProjectID`.
    *   **Revenue:** `PROJECT_REVENUE_F` combines Job Revenue + Service Project Billing.
    *   **Cost:** `PROJECT_COSTS_F` combines Job Costs + Service Project Calls (filtered by Project Number).
    *   **Logic:** Deduplication applied to `PROJECTS_D` keys to prevent "Fan Out" when joining billing/calls.

### 2.2 Agreement Stream Transformation
*   **Source:**
    *   `CONTRACT_BILLING_F` (Recurring Revenue)
    *   `CALLS_F` (Service Call Costs)
    *   `CONTRACTS_D`
*   **Transformation:**
    *   **Dimension:** `SERVCONTRACTS_D` derived from `CONTRACTS_D`. Uses **Inferred Members** to handle missing keys.
    *   **Revenue:** `SERVCONTRACTS_REVENUE_F` reads `CONTRACT_BILLING_F`, excludes Service Projects.
    *   **Cost:** `SERVCONTRACTS_COSTS_F` reads `CALLS_F`, excludes Service Projects, requires valid Contract Number.

### 2.3 Spot Stream Transformation
*   **Source:** `CALLS_F`
*   **Transformation:**
    *   **Fact:** `SPOT_FINANCIALS_F`.
    *   **Logic:** Filters `CALLS_F` where `Contract Number` IS NULL or BLANK.

---

## 3. Fact Tables (Final State)

| Table Name | Grain | Source Logic | Measures |
| :--- | :--- | :--- | :--- |
| **PROJECT_REVENUE_F** | Project × Month | Union(Job Earned, Service Billing) | `Amount` |
| **PROJECT_COSTS_F** | Project × Date | Union(Job Cost, Call Cost) | `Amount` |
| **SERVCONTRACTS_REVENUE_F** | Agreement × Month | `CONTRACT_BILLING_F` (excl. Projects) | `Amount` |
| **SERVCONTRACTS_COSTS_F** | Agreement × Call | `CALLS_F` (Linked to Contract) | `Amount` |
| **SPOT_FINANCIALS_F** | Call | `CALLS_F` (No Contract) | `Revenue`, `Cost` |

---

## 4. Dimension Tables (Final State)

### 4.1 PROJECTS_D
*   **Description:** Unified dimension for all "Project" type work.
*   **Key:** `SurrogateProjectID` (Format: `Type_Customer_Number`).
*   **Sources:** `JOBS_D` (Type="Job"), `CONTRACTS_D` (Type="Service Contract").

### 4.2 SERVCONTRACTS_D
*   **Description:** Dimension for Maintenance Agreements.
*   **Key:** `AgreementKey` (Format: `Customer_Contract_Year`).
*   **Handling:**
    *   **RAW:** Loaded from `CONTRACTS_D`.
    *   **FINAL:** Adds **Inferred Rows** for orphaned keys found in Fact tables (Customer Mismatches or Missing Contracts).

### 4.3 CUSTOMERS_D
*   **Description:** Standard Customer dimension.
*   **Key:** `Customer Key`.
*   **Role:** Conformed dimension linking all 3 streams.

### 4.4 DIM_DATE
*   **Description:** Standard Calendar.
*   **Role:** Conformed dimension linking all 3 streams.

---

## 5. Data Integrity & Orphan Handling

### 5.1 The "Inferred Member" Strategy
To resolve Referential Integrity failures (where Fact has a key not in Dim):
1.  **Scan Facts:** Identify all unique `AgreementKey`s in Revenue/Cost facts.
2.  **Compare:** Subtract keys present in `SERVCONTRACTS_D`.
3.  **Infer:** For missing keys, parse the key string to extract `Customer`, `Contract`, `Year`.
4.  **Append:** Add these "Ghost" rows to `SERVCONTRACTS_D` with status "Inferred".

### 5.2 Project Duplication (Fan Out)
*   **Issue:** `PROJECTS_D` contains duplicate `Project Number`s (same project, different customer/division).
*   **Fix:** Fact queries (`PROJECT_REVENUE_F`, `PROJECT_COSTS_F`) **deduplicate** the Dimension side on `Project Number` before joining.
*   **Result:** Ensures 1:1 match for Costs/Revenue, preventing double-counting.

---

## 6. Reconciliation Checks

Standard DAX measures exist in `_Key Measures` to verify data integrity:

*   **Revenue Check:**
    *   `Check_Source_Revenue_Total`: Sum(Job Earned + Contract Billable + Spot Calls)
    *   `Check_Dest_Revenue_Total`: Sum(Project Rev + Agreement Rev + Spot Rev)
    *   `Check_Revenue_Variance`: Must be **0**.

*   **Cost Check:**
    *   `Check_Source_Calls`: Sum(Call Costs)
    *   `Check_Dest_Total`: Sum(Project Call Costs + Agreement Call Costs + Spot Costs)
    *   `Check_Variance`: Must be **0**.

---

## 7. DAX Measures Library (Current State)

### 7.1 Project Stream
```DAX
Project Revenue = SUM('PROJECT_REVENUE_F'[Amount])
Project Cost = SUM('PROJECT_COSTS_F'[Amount])
Project GP = [Project Revenue] - [Project Cost]
Project GP % = DIVIDE([Project GP], [Project Revenue])
```

### 7.2 Agreement Stream
```DAX
Agreement Revenue = SUM('SERVCONTRACTS_REVENUE_F'[Amount])
Agreement Cost = SUM('SERVCONTRACTS_COSTS_F'[Amount])
Agreement GP = [Agreement Revenue] - [Agreement Cost]
Agreement GP % = DIVIDE([Agreement GP], [Agreement Revenue])
```

### 7.3 Spot Stream
```DAX
Spot Revenue = SUM('SPOT_FINANCIALS_F'[Revenue])
Spot Cost = SUM('SPOT_FINANCIALS_F'[Cost])
Spot GP = [Spot Revenue] - [Spot Cost]
Spot GP % = DIVIDE([Spot GP], [Spot Revenue])
```

### 7.4 Total Company (Executive)
```DAX
Total Revenue = [Project Revenue] + [Agreement Revenue] + [Spot Revenue]
Total Cost = [Project Cost] + [Agreement Cost] + [Spot Cost]
Gross Profit = [Total Revenue] - [Total Cost]
Gross Profit % = DIVIDE([Gross Profit], [Total Revenue])
```

---

## 8. Gap Analysis: v5.0 vs v4.0 (Pending Implementation)

The following items were defined in the v4.0 Modeling Guide but have **not yet been implemented** in the current v5.0 model:

### 8.1 Retention Modeling (NRR / GRR / Churn)
*   **Status:** Not Started.
*   **Missing Measures:** `Customer NRR`, `Customer GRR`, `Churn Customers`, `Upsell`, `Contraction`.
*   **Prerequisites:** Requires robust Time Intelligence logic (Prior Period Revenue) and potentially a "Snapshot" or "Cohort" logic.

### 8.2 Renewal Modeling
*   **Status:** Not Started.
*   **Missing Columns:** `Contract Start Date` (Inferred), `Contract End Date` (Inferred).
*   **Missing Measures:** `Renewal Status` (Active, Expiring, Expired).

### 8.3 Segmentation Mapping
*   **Status:** Not Started.
*   **Requirement:** Normalizing `Job_Division`, `Agreement_Subtype` into a unified `UnifiedCategory` (e.g., SVC, DB, GREEN) for cross-stream reporting.

### 8.4 T&M Spend per Maintenance Dollar
*   **Status:** Not Started.
*   **Missing Measure:** `DIVIDE([Spot Revenue], [Agreement Revenue])`.

### 8.5 Executive Dashboarding
*   **Status:** Pending.
*   **Requirement:** Visuals for Top 10 Clients, GP Trends, and Renewal Timelines.
