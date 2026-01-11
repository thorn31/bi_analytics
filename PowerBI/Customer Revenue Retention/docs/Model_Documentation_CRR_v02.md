# CRR v02 Semantic Model – Current Documentation

**Last Updated:** December 11, 2025  
**PBIX:** `CRR v02.pbix` (connected Power BI Desktop session)  
**Purpose:** Unified analysis of revenue and cost across Service Contracts, Projects, and (future) Repair/Spot streams.  

---

## 1. Modeling Objectives
- Provide a consolidated lens over three operational revenue streams:
  - **Projects** – standard jobs plus service projects executed as projects.
  - **Service Contracts** – recurring service agreements with annual/contract-year grain.
  - **Repair/Spot** – ad-hoc work (not yet modeled in facts).
- Align each stream to shared calendar, customer, and measure logic so executives can compare profitability and retention.
- Surface integrity issues (e.g., agreement facts lacking dimension rows) to drive data-quality fixes without blocking reporting.

---

## 2. Source Systems & Naming
- All curated data currently lands in Snowflake (`DATA_WAREHOUSE.DW_FINAL`). Power Query pulls staging tables via the Snowflake connector.
- Naming conventions:
  - `*_D` for dimensions, `*_F` for facts.
  - `SERVCONTRACTS_*` used for maintenance agreement assets (formerly `AGREEMENT_*`).
  - `SurrogateProjectID` / `AgreementKey` act as relationship keys into facts.

---

## 3. Query Organization
| Query Group | Purpose | Key Queries |
|-------------|---------|-------------|
| **Staging** | Thin wrappers over Snowflake objects plus intermediate logic used in multiple downstream steps. | `CONTRACTS_D`, `JOBS_D`, `JOB_FINANCIALS_F`, `SERVPROJECTS_D`, `JOBSTRIMMED_D`, `SV00564`, `SERVCONTRACTS_D_STAGING` |
| **Dim** | Final model dimensions exposed to visuals. | `PROJECTS_D`, `SERVCONTRACTS_D`, `CUSTOMERS_D`, `FYCALENDAR_D`, `Time Intelligence`, etc. |
| **Facts** | Revenue/Cost streams at the analysis grain. | `PROJECT_REVENUE_F`, `PROJECT_COSTS_F`, `SERVCONTRACTS_REVENUE_F`, `SERVCONTRACTS_COSTS_F`, `CALLS_F`, `CONTRACT_BILLABLE_F`, etc. |
| **Diagnostics** | Instrumentation / data-quality helpers (currently minimal). | `Diagnostics` query group placeholder. |

---

## 4. Dimensions

### 4.1 `PROJECTS_D`
- **Sources:** `SERVPROJECTS_D` (service contracts flagged as projects) unioned with `JOBSTRIMMED_D` (standard jobs).
- **Key Fields:** `SurrogateProjectID`, `Project Number`, `Customer Number`, `Customer Key`, `Start Date`, `End Date`, `Project Type`.
- **Highlights:**
  - `SERVPROJECTS_D` pulls Snowflake `CONTRACTS_D`, filters `CONTRACT_DESCRIPTION = "SERVICE PROJECT"`, trims columns, and renames to project semantics.
  - `JOBSTRIMMED_D` selects identifying columns from `JOBS_D`; both staging tables title-case all column names at ingestion.
  - Each half receives `Project Type` (`"Service Contract"` vs `"Job"`) and a derived `SurrogateProjectID` (`SERV_<cust>_<contract>` or `JOB_<customer key>_<job key>`).
  - Combination enforces consistent data types and removes the known bad Surrogate ID `SERV_CN991413_11/21REPEX`.

### 4.2 `SERVCONTRACTS_D_STAGING`
- **Purpose:** Canonical list of service contracts exploded to contract-year grain before orphan handling.
- **Steps:**
  1. **Source:** `CONTRACTS_D` from Snowflake (all contracts).
  2. **Exclude service projects:** Remove any contract whose `Contract Number` is present in `PROJECTS_D` slice where `Project Type = "Service Contract"`, ensuring we don’t double count records that live in the Projects stream.
  3. **Year explosion:** For each remaining row, create `YearIndex` list `List.Numbers(1, Wscontsq)` (defaulting to 1 for null/zero) and expand so each contract year becomes a row.
  4. **Key creation:** `Customer Key Full = Custnmbr & Source`; `AgreementKey = Customer Key Full & "_" & Contract Number & "_" & YearIndex`.
  5. **Aggregation:** Group at `{AgreementKey, Custnmbr Key}` to deduplicate “Master/Servant” contract structures, aggregating descriptive fields and summing `Contract Amount`/`ACV`.

### 4.3 `SERVCONTRACTS_D`
- **Inputs:** `SERVCONTRACTS_D_STAGING`, `SERVCONTRACTS_REVENUE_F`, `SERVCONTRACTS_COSTS_F`.
- **Process:**
  1. **Fact key discovery:** Collect distinct `AgreementKey` values from each fact, marking `IsRevenue`/`IsCost`.
  2. **Consolidate & label:** Full-outer join of keys so each unique contract-year reports `OrphanSource = "Revenue Only"`, `"Cost Only"`, or `"Both"`.
  3. **Orphan detection:** Left anti-join against staged dimension to isolate contract-years that exist in facts but not in source data.
  4. **Inference logic:** Parse `AgreementKey` to reconstruct `Customer Number`, `Contract Number`, and `YearIndex`. Create placeholder dimension rows with:
     - `Contract Description = "Data Integrity - Missing in Source (<OrphanSource>)"`
     - `Contract Type/Divisions = "Unknown"`, `Contract Status = "Orphan"`
     - `Start Date` / `End Date` chosen from min/max of revenue/cost dates tied to the key (falling back to 1/1/1900).
     - Financial fields zeroed.
  5. **Combine:** Append inferred rows to staged dimension, ensuring `OrphanSource` is null for source-backed records and preserving data types (`Start Date`, `End Date`, `Contract Amount`, `ACV`, `YearIndex`).
- **Outcome:** Every fact row has dimensional coverage, and analysts can filter on `OrphanSource` to focus on data-quality gaps.

---

## 5. Fact Tables

### 5.1 `PROJECT_REVENUE_F`
- **Streams:**
  - **Job Earned Revenue:** From `JOB_FINANCIALS_F` -> select `{Period Date, SurrogateProjectID, Customer Number, Customer Key, Contract Earned Curr Mo}` -> rename to `{Date, Amount}` and tag `Source Type = "Job Earned"`.
  - **Service Project Billing:** Identify service projects within `PROJECTS_D`, join to `CONTRACT_BILLABLE_F` on `Contract Number`, keep `{Date, SurrogateProjectID, Customer Number, Customer Key, Amount = BILLABLE_ALL}`, tag `Source Type = "Service Billing"`.
- **Purpose:** Aligns both job and service project billing into a single fact for consistent DAX treatment.

### 5.2 `PROJECT_COSTS_F`
- **Streams:**
  - **Job Costs:** Use `Monthly Cost` derived in `JOB_FINANCIALS_F` (delta of running totals); retain `{Date, SurrogateProjectID, Amount}`, tag `Source Type = "Job Cost"`.
  - **Service Project Call Costs:** Filter `CALLS_F` to records tied to service projects (via `PROJECTS_D` join) and keep `{Date, SurrogateProjectID, Amount = Cost All}`, tag `Source Type = "Service Call Cost"`.
- **Goal:** Provide cost coverage for both job and service project execution while leveraging unified surrogate keys.

### 5.3 `SERVCONTRACTS_REVENUE_F`
- **Source:** `CONTRACT_BILLABLE_F` (maintenance billing).
- **Filters:** Left anti-join against service projects to remove any rows already modeled under Projects. Require non-null `Customer_Contract_Year Key`.
- **Schema:** `{Date = WENNSOFT_BILLING_DATE, AgreementKey = Customer_Contract_Year Key, Amount = BILLABLE_ALL, Source Type = "Service Contract Billing"}`.
- **Grain:** Individual billing transactions at service contract-year level.

### 5.4 `SERVCONTRACTS_COSTS_F`
- **Source:** `CALLS_F` (service call history).
- **Filters:** Remove rows tied to service projects and drop blank contract numbers to keep only genuine maintenance-contract calls.
- **Schema:** `{Date = Date Of Service Call, AgreementKey = Customer_Contract_Year Key, Amount = Cost All, Source Type = "Contract Call Cost"}`.
- **Result:** Maintenance cost facts that can roll up over the same `AgreementKey` dimension grain.

---

## 6. Key Calculations & Logic Highlights
- **Monthly Cost Calculation (`JOB_FINANCIALS_F`):** Within each `Job Key`, rows are sorted by `Period Date`; Power Query adds an index to compute `Monthly Cost = Current Cumulative Cost - Previous Cumulative Cost`. Rows where both `Monthly Cost` and `Contract Earned Curr Mo` equal zero are dropped to keep the fact slim.
- **Agreement Key Parsing:** `AgreementKey = <Custnmbr + Source> "_" <Contract Number> "_" <YearIndex>`; parsing logic reverses this pattern to rebuild orphan dimension rows and is reused anywhere we need to inspect components of the key.
- **Service Project Exclusion:** Consistently uses `PROJECTS_D` slice where `Project Type = "Service Contract"` to remove those contracts from the maintenance stream, preventing double-counting between project and agreement reporting.
- **Data-Type Reapplication:** Critical transformations (`SERVCONTRACTS_D`) end by explicitly reassigning column types to avoid type drift during table combines.

---

## 7. Known Data-Quality/Design Considerations
- **Orphans:** Fact rows lacking source dimension records are intentionally surfaced with `OrphanSource` metadata; need follow-up with business owners to backfill or flag the originating contracts.
- **Master vs. Servant Contracts:** Deduplication via `Table.Group` ensures one record per `AgreementKey`, but we should monitor for cases where merging master/servant rows suppresses important attributes.
- **Repair/Spot Stream:** Not yet implemented. Future work will carve spot/repair transactions from `CALLS_F` where `Contract Number` is null and ensure they integrate with the same calendar and measure framework.
- **Measure Layer:** `_Key Measures` table currently holds shared measures; once repair stream lands, expect composite `[Total Revenue]`, `[Total Cost]`, etc., to span all three streams.
- **Service Project Duplicate Keys:** Some `Contract Number` values appear under multiple customers in `PROJECTS_D`, which can fan out billing and call joins. We now deduplicate service-project keys on `Project Number` before joining billing (`PROJECT_REVENUE_F`) and calls (`PROJECT_COSTS_F`) so each contract number maps to a single SurrogateProjectID when reconciling revenue and costs.

---

## 8. Next Modeling Steps
1. Finalize orphan diagnostics (e.g., visuals highlighting `OrphanSource`) and confirm all remaining fact keys reconcile.
2. Extend documentation once Repair/Spot facts and any new dimensions are added.
3. Evaluate whether shared customer, calendar, and time-intelligence tables require additional columns to support agreement renewal analysis (e.g., fiscal periods aligned to contract years).
