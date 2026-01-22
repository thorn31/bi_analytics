# Mechanical Project Management — Semantic Model Inventory

Generated: 2026-01-22 14:36 EST

## Contents
- Tables + columns: `Mechanical Project Management - Tables.md`
- Source queries / partitions: `Mechanical Project Management - Queries.md`
- Measures catalog: `Mechanical Project Management - Measures.md`
- Measure explanations: `Mechanical Project Management - Measure Explanations.md`
- Revenue map: `Mechanical Project Management - Revenue Map.md`

## High-Level Counts
- Tables: 43
- Columns: 465
- Measures: 101
- Partitions: 43
- Relationships: 43 (42 active, 1 inactive)

## Data Sources (from M queries)
### Snowflake
- Hosts: ws53155.central-us.azure.snowflakecomputing.com
- Warehouses: COMPUTE_WH
- Databases referenced: DATA_WAREHOUSE, DATA_WAREHOUSE_DEV
- Schemas referenced: DW_CLEAN, DW_FINAL, PUBLIC
- Tables referenced: BUDGET_F, CUSTOMERS_D, EMPLOYEES_D, INVOICES_F, JOBS_D, JOB_COST_DESCRIPTION_D, JOB_COST_FORECASTS_F, JOB_COST_SUMMARY_F, JOB_LABOR_HOURS_F, POSTING_DATA_F, PO_JOB_DETAILS_F
- Views referenced: JOB_CHANGE_ORDERS, JOB_COST_DETAILS, JOB_PROFILE

## Table Groups
### Date
- Calendar, DateTableTemplate_ae1bc3b8-dd10-47c1-913a-5f4a589902e6, LocalDateTable_103d4237-3f13-4fb8-908e-8f990ad5f6f8, LocalDateTable_26e0a611-4938-40bf-8444-deab64adf683, LocalDateTable_288a7e21-8bfa-49ce-90b0-3f281030da3e, LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f, LocalDateTable_3068354c-1934-4176-9b53-101d178cc7da, LocalDateTable_39148a68-5226-4488-8b67-dc23f90c2fda, LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f, LocalDateTable_4d5c68a9-1016-4c7f-8bd6-94b091483340, LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356, LocalDateTable_69547476-3a6b-4a5f-8fcf-f5f0ffbaa28e, LocalDateTable_7c0dba22-51a6-475f-9385-01ea578d2301, LocalDateTable_820e8c9a-6a47-49de-b350-058a53302479, LocalDateTable_82986f2d-45c5-4243-bb17-c0844f70692b, LocalDateTable_8f32177c-7b7f-4b5c-afda-6d8a43f3b74a, LocalDateTable_a1304e08-f471-47dc-bbfc-f6653e634bfb, LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98, LocalDateTable_d9746aa8-c787-46e8-a0b0-2e5477439e51, LocalDateTable_dbc8e48e-68af-4633-963c-bd15e3755808, LocalDateTable_dc9a7e8b-973c-4d72-ad27-3eff05a132d9, LocalDateTable_df4ab1e5-1799-472a-b536-48d903e2a6f1, LocalDateTable_e2d949a2-51a9-4559-aff7-c4bc089c82a9, LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae
### Dim
- COST_CODE_MAPPING, CUSTOMERS, DIVISION, JOB, Refresh Date
### Fact
- BUDGET, CHANGE_ORDERS_BY_MONTH, GL POSTING, INVOICES, JOB FORECAST, JOB_COST_DETAILS, JOB_COST_SUMMARY, JOB_LABOR_HOURS
### Measures
- Backlog Measures, Cost Measures, Revenue Measures
### Parameter
- Backlog Parameter, Backlog Parameter 2, GP Parameter

## Relationships
| From | To | Active | Join behavior |
|---|---|---:|---|
| `JOB.START_DATE` | `LocalDateTable_820e8c9a-6a47-49de-b350-058a53302479.Date` | true | datePartOnly |
| `JOB.TARGET_COMPLETION_DATE` | `LocalDateTable_8f32177c-7b7f-4b5c-afda-6d8a43f3b74a.Date` | true | datePartOnly |
| `JOB.ACT_COMPLETION_DATE` | `LocalDateTable_dbc8e48e-68af-4633-963c-bd15e3755808.Date` | true | datePartOnly |
| `JOB_COST_DETAILS.JOB_NUMBER` | `JOB.JOB_NUMBER` | true |  |
| `INVOICES.GL_POSTING_DATE` | `LocalDateTable_a1304e08-f471-47dc-bbfc-f6653e634bfb.Date` | true | datePartOnly |
| `INVOICES.DISCOUNT_DATE` | `LocalDateTable_7c0dba22-51a6-475f-9385-01ea578d2301.Date` | true | datePartOnly |
| `INVOICES.DUE_DATE` | `LocalDateTable_df4ab1e5-1799-472a-b536-48d903e2a6f1.Date` | true | datePartOnly |
| `INVOICES.DATE_PAID` | `LocalDateTable_4d5c68a9-1016-4c7f-8bd6-94b091483340.Date` | true | datePartOnly |
| `CUSTOMERS.CREATED` | `LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f.Date` | true | datePartOnly |
| `CUSTOMERS.UPDATED` | `LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356.Date` | true | datePartOnly |
| `INVOICES.JOB_NUMBER` | `JOB.JOB_NUMBER` | true |  |
| `JOB.CUSTOMER_NUMBER` | `CUSTOMERS.CUSTOMER_NUMBER` | true |  |
| `INVOICES.CUSTOMER_NUMBER` | `CUSTOMERS.CUSTOMER_NUMBER` | false |  |
| `JOB_LABOR_HOURS.FIRST_DAY` | `LocalDateTable_69547476-3a6b-4a5f-8fcf-f5f0ffbaa28e.Date` | true | datePartOnly |
| `JOB.WARRANTY_START` | `LocalDateTable_3068354c-1934-4176-9b53-101d178cc7da.Date` | true | datePartOnly |
| `JOB.WARRANTY_END` | `LocalDateTable_dc9a7e8b-973c-4d72-ad27-3eff05a132d9.Date` | true | datePartOnly |
| `JOB.'Max Transaction Date'` | `LocalDateTable_103d4237-3f13-4fb8-908e-8f990ad5f6f8.Date` | true | datePartOnly |
| `'JOB FORECAST'.MODIFIED_DATE` | `LocalDateTable_26e0a611-4938-40bf-8444-deab64adf683.Date` | true | datePartOnly |
| `'JOB FORECAST'.JOB_NUMBER` | `JOB.JOB_NUMBER` | true |  |
| `JOB.DIVISIONS` | `DIVISION.DIVISIONS` | true |  |
| `JOB_LABOR_HOURS.JOB_KEY` | `JOB.JOB_KEY` | true |  |
| `CHANGE_ORDERS_BY_MONTH.JOB_NUMBER` | `JOB.JOB_NUMBER` | true |  |
| `BUDGET.DIVISION` | `DIVISION.DIVISIONS` | true |  |
| `JOB_COST_SUMMARY.JOB_NUMBER` | `JOB.JOB_NUMBER` | true |  |
| `JOB_LABOR_HOURS.LAST_DAY` | `LocalDateTable_39148a68-5226-4488-8b67-dc23f90c2fda.Date` | true | datePartOnly |
| `INVOICES.POST_DATE` | `LocalDateTable_e2d949a2-51a9-4559-aff7-c4bc089c82a9.Date` | true | datePartOnly |
| `'JOB FORECAST'.'Job_Cost Code'` | `COST_CODE_MAPPING.'Job_Cost Code'` | true |  |
| `JOB_COST_DETAILS.'Job_Cost Code'` | `COST_CODE_MAPPING.'Job_Cost Code'` | true |  |
| `JOB_LABOR_HOURS.'Job_Cost Code'` | `COST_CODE_MAPPING.'Job_Cost Code'` | true |  |
| `JOB_COST_SUMMARY.'Job Cost Code'` | `COST_CODE_MAPPING.'Job_Cost Code'` | true |  |
| `'Refresh Date'.Date` | `LocalDateTable_d9746aa8-c787-46e8-a0b0-2e5477439e51.Date` | true | datePartOnly |
| `JOB.'Min Transaction Date'` | `LocalDateTable_82986f2d-45c5-4243-bb17-c0844f70692b.Date` | true | datePartOnly |
| `JOB.'Start Date_Revised'` | `LocalDateTable_288a7e21-8bfa-49ce-90b0-3f281030da3e.Date` | true | datePartOnly |
| `Calendar.Date` | `LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae.Date` | true | datePartOnly |
| `JOB_COST_DETAILS.TRAN_DATE` | `Calendar.Date` | true |  |
| `'JOB FORECAST'.Date` | `Calendar.Date` | true |  |
| `CHANGE_ORDERS_BY_MONTH.Date` | `Calendar.Date` | true |  |
| `BUDGET.PERIODDT` | `Calendar.Date` | true |  |
| `JOB_LABOR_HOURS.ENTRYDATE` | `Calendar.Date` | true |  |
| `'GL POSTING'.Date` | `Calendar.Date` | true |  |
| `INVOICES.DOCUMENT_DATE` | `Calendar.Date` | true |  |
| `Calendar.WeekBeginDate` | `LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98.Date` | true | datePartOnly |
| `Calendar.WeekEndDate` | `LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f.Date` | true | datePartOnly |
