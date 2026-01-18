# Customer Segmentation Session Summary - Jan 16, 2026

## Goal
To create a clean, deduplicated, and segmented "Master Customer" dimension for the Customer Revenue Retention project. The objective is to group disparate billing entities (e.g., "Amazon Data Services", "Amazon.com") under a single Master Name and classify them into industry segments (Medical, Industrial, Office, etc.).

## Work Completed

### 1. Project Structure
Created a dedicated workspace folder: `powerbi/Customer Segmentation/`
*   `input/`: Contains source data (`CustomerLastBillingDate.csv`) and `ManualOverrides.csv`.
*   `output/`: Contains the processed results (`CustomerSegmentation.csv`) and audit logs (`CustomerDeduplicationLog.csv`).
*   `segment_customers.py`: The Python logic engine.
*   `CUSTOMERS_D.m`: Power Query script for model integration.

### 2. Logic Implemented (`segment_customers.py`)

#### A. Pre-Processing & Cleaning
*   **C/O Handling**: Splits names containing "C/O" (Care Of). 
    *   *Default*: Takes the **Left** side (Tenant/Customer).
    *   *Exception*: If the **Right** side matches a known Property Manager chain (e.g., "Flagship Healthcare"), it promotes that manager to the Master Name.
*   **Chain/Brand Normalization**: Explicitly maps variations of known large entities to a single Master Name.
    *   Example: `Orange Theory West`, `Orangetheory Fitness` -> **ORANGETHEORY FITNESS**.
    *   Example: `Flagship New Albany` -> **FLAGSHIP HEALTHCARE PROPERTIES**.

#### B. Segmentation Logic
Assigns a segment based on keywords in the **Original Name** (to capture suffixes like "LLC" or context like "Hospital") or the **Master Name** (if a Chain Rule was applied).

**Hierarchy (Order of Operations):**
1.  **College/University**: `University`, `College`, `Higher Ed`.
2.  **Private Schools**: `Academy`, `Prep`, `Catholic School` (Contextual).
3.  **Public Schools**: `ISD`, `School Dist`, `City Schools`.
4.  **Religious**: `Church`, `Archdiocese`, `Ministry`.
5.  **Medical**: `Hospital`, `Clinic`, `Dental`, `Pathology`, `Amerimed`.
6.  **Hospitality**: `Hotel`, `Inn`, `Resort`.
7.  **Municipal**: Strict `City Of`, `Fire Dept`, `County` (with exclusions for "YMCA", "Bank").
8.  **Data Center**: `Compute`, `Hosting`, `Cloud`.
9.  **Industrial**: `Manufacturing`, `Logistics`, `Packaging`, `Steel`, `Automotive`.
10. **Office**: Specific white-collar terms (`Realty`, `Financial`, `Law`, `Consulting`, `Insurance`).
11. **Other**: Fallback for generic names or "LLC"s without specific industry context.

#### C. Deduplication
*   **Fuzzy Matching**: Groups names that are >95% similar.
*   **Safety**: Uses a "Comparison Key" that strips generic business suffixes (`LLC`, `Inc`) but **preserves** entity-defining terms (`County`, `School`, `City`) to prevent merging "Boone County Fiscal Court" with "Boone County Schools".
*   **Lock**: Rows present in `ManualOverrides.csv` are immune to fuzzy renaming.

### 3. Manual Overrides
A key-based system allows precise user control.
*   File: `input/ManualOverrides.csv`
*   Format: `Customer Key, Manual Master Name, Manual Segment`
*   Usage: Forces a specific outcome for a customer, bypassing automated logic.

## Current Status (Distribution)
*   **Other**: ~1,690
*   **Industrial**: ~290
*   **Office**: ~220
*   **Medical**: ~145
*   **Municipal**: ~125
*   **Religious**: ~90
*   **Schools (Public/Private)**: ~50
*   **College/University**: ~25
*   **Hospitality**: ~25 (support category; not a primary industrial group)

## Next Steps

1.  **"Other" Category Analysis**: 
    *   Use AI/Web Search to classify top "Other" customers (e.g. "American Fuji Seal" -> Industrial).
    *   Generate a `SuggestedOverrides.csv` for bulk approval.
2.  **Refine "Office" Segment**: Review the strict keyword list to see if valid corporate entities are being missed.
3.  **Model Integration**:
    *   Import `CUSTOMERS_D.m` into Power BI.
    *   Validate relationships and visual results.

---

## Update Note (Current Repo)

This session summary reflects the initial prototype. The current workflow is documented in:
- `README.md`
- `docs/WORKFLOW.md`
