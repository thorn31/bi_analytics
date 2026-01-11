# Unified Revenue Model: Orphan Handling Strategy
**Date:** December 10, 2025
**Model:** CRR v02.pbix

## 1. The Problem: "Orphaned" Facts
In our unified model, we have Fact tables (`SERVCONTRACTS_REVENUE_F`, `SERVCONTRACTS_COSTS_F`) that link to a Dimension table (`SERVCONTRACTS_D`) via an `AgreementKey`.

**Orphans** occur when a row in the Fact table has an `AgreementKey` that does not exist in the Dimension table. This results in:
*   Incomplete reporting (rows are blank/filtered out when slicing by Customer/Contract).
*   Referential Integrity failure.

### Root Causes Identified
1.  **Missing Contracts:** Some Contract Numbers exist in billing/service history (`CONTRACT_BILLABLE_F`, `CALLS_F`) but are completely absent from the source Dimension (`CONTRACTS_D`).
2.  **Customer Mismatch (Ownership Change):**
    *   Fact tables link Contract X to Customer A (historical owner).
    *   Dimension table links Contract X to Customer B (current owner).
    *   Since our Key logic includes `[Customer Key]`, Key A != Key B, resulting in a mismatch.
3.  **Service Project Leakage (Resolved):**
    *   "Project" type contracts were leaking into the Agreement stream due to case-sensitivity issues in filtering. (Resolved by uppercasing keys).

---

## 2. The Solution: Inferred Dimension Members
We cannot modify the source data. Therefore, we implement an **Inferred Member** logic in Power Query to dynamically "rescue" these orphans and add them to the Dimension.

### Architecture
To avoid "Cyclic Reference" errors (Dimension reading Fact reading Dimension), we split the dimension query:

1.  **`SERVCONTRACTS_D_RAW` (Staging):**
    *   Standard extraction from `CONTRACTS_D`.
    *   Filters out Service Projects.
    *   Explodes rows by Contract Year (`Wscontsq`).
    *   Deduplicates Master/Servant contracts (Group By).

2.  **`SERVCONTRACTS_D` (Final):**
    *   Reads `SERVCONTRACTS_D_RAW`.
    *   Reads `SERVCONTRACTS_REVENUE_F` and `SERVCONTRACTS_COSTS_F`.
    *   Calculates the **Set Difference** (Keys in Facts - Keys in Dim).
    *   Creates "Mock Rows" for the missing keys and appends them to the dimension.

---

## 3. Inferred Member Logic

### 3.1 Key Identification & Source Tagging
We scan both Fact tables to find all unique keys. We tag them to track where the orphan came from:
*   `IsRevenue`: Key exists in Revenue Fact.
*   `IsCost`: Key exists in Cost Fact.
*   **`OrphanSource`**: Calculated column ("Revenue Only", "Cost Only", or "Both").

### 3.2 Member Construction (Parsing)
Instead of creating a generic "Unknown" record, we parse the `AgreementKey` (which contains embedded metadata) to reconstruct valid attributes.

**Key Format:** `[CustomerKey]SERV_GP_[ContractNumber]_[YearIndex]`

**Parsed Attributes:**
*   **Customer Key / Number:** Extracted from the prefix (before `SERV_GP`). This ensures the Orphan links to the correct `CUSTOMERS_D` row, preserving historical ownership visibility.
*   **Contract Number:** Extracted from the middle segment.
*   **Year Index:** Extracted from the suffix.

### 3.3 Date Inference
We calculate the `Min(Date)` and `Max(Date)` from the Fact tables for each orphan key.
*   **Start Date:** Set to the earliest billing/service date found in Facts.
*   **End Date:** Set to the latest billing/service date found in Facts.
*   *Benefit:* This provides a realistic timeline for the "Missing" contract rather than a default `1900-01-01`.

### 3.4 Visual Indicator
In the report, these Inferred Members are clearly flagged:
*   **Contract Description:** `"Data Integrity - Missing in Source (Revenue Only)"`
*   **Contract Status:** `"Orphan"`

---

## 4. Summary of Data Integrity Fixes

| Issue Type | Symptom | Fix Applied | Result |
| :--- | :--- | :--- | :--- |
| **Missing Contract** | Check = 0 | Inferred Member created | Revenue/Cost visible, linked to Customer, labeled "Missing in Source". |
| **Customer Mismatch** | Check = 1 | Inferred Member created | Creates a "Historical" contract row linked to the original Customer (from Fact), separate from the "Current" contract row (from Dim). |
| **Project Leakage** | Type = PROJECT | Upstream Filter | Filtered out of Agreement stream entirely; moved to Project stream. |

## 5. M-Code Reference
The logic is encapsulated in the file: `SERVCONTRACTS_D_Orphans_Final.m`.
