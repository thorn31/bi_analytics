# Contract Management — Semantic Model Inventory

Generated: 2026-01-22 15:09 EST

## Contents
- Tables + columns: `Contract Management - Tables.md`
- Source queries / partitions: `Contract Management - Queries.md`
- Measures catalog: `Contract Management - Measures.md`
- Measure explanations: `Contract Management - Measure Explanations.md`
- Revenue map: `Contract Management - Revenue Map.md`

## High-Level Counts
- Tables: 49
- Columns: 610
- Measures: 137
- Partitions: 49
- Relationships: 46 (42 active, 4 inactive)

## Data Sources (from M queries)
### Snowflake
- Hosts: ws53155.central-us.azure.snowflakecomputing.com
- Warehouses: COMPUTE_WH
- Databases referenced: DATA_WAREHOUSE, DATA_WAREHOUSE_DEV
- Schemas referenced: DW_CLEAN, DW_FINAL, PUBLIC
- Tables referenced: APPOINTMENTS_F, BUDGET_F, CALLS_F, CONTRACTS_D, CONTRACT_BILLING_F, CONTRACT_LABOR_HOURS_F, CUSTOMERS_D, EMPLOYEES_D, JOBS_D, POSTING_DATA_F, PO_JOB_DETAILS_F, SERV_CONTRACT_TASKS_F, TASKS_F
- Views referenced: JOB_CHANGE_ORDERS, JOB_PROFILE

## Table Groups
### Date
- Calendar, DateTableTemplate_ae1bc3b8-dd10-47c1-913a-5f4a589902e6, LocalDateTable_00e51d8d-231f-4d65-881b-7cd775844859, LocalDateTable_1997b5af-fbda-41ee-846d-31f24c5d8bd7, LocalDateTable_287ff984-7355-4b13-9018-95e3a16e18e9, LocalDateTable_2a249574-7315-48a3-bf2c-4c9bbab9a923, LocalDateTable_2e841b8c-c7b1-4df6-aaad-a1a446fc7c01, LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f, LocalDateTable_36fb0cc6-3a6a-46f4-99fe-6340fb69c6b3, LocalDateTable_38f12a90-c3e3-476c-8af6-3b87ccdcdb64, LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f, LocalDateTable_4ed2ebea-2956-4a45-b593-72e2e76dd90c, LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356, LocalDateTable_68db00b3-6e04-4ee2-a4a3-b33365193de7, LocalDateTable_7568775e-9707-49cb-bf23-8bca38b29542, LocalDateTable_7b8a7d6f-03de-4370-ab61-70ffffb79124, LocalDateTable_8931b809-08ab-4252-8179-ca3c21383cd6, LocalDateTable_8d221eb4-201c-477f-89c5-03c6e03aa65e, LocalDateTable_a823d9da-2d68-472e-bea7-b1c1f0ea5afc, LocalDateTable_c357c417-93f4-4ea3-badf-ef0dec761ede, LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98, LocalDateTable_de817910-54ca-42f0-b798-d1ae454cca2b, LocalDateTable_dea31c23-1eaa-490c-ab59-1e5b655fb2ca, LocalDateTable_e59f379f-de3d-42a7-bd84-6e80ef7a5ed8, LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae
### Measures
- Contract Measures, Cost Measures, Hour Measures, Revenue Measures
### Parameter
- GP Parameter, GP Parameter 2
### Table
- APPOINTMENTS_F, BUDGET_F, CALLS COSTS, CALLS_F, CHANGE_ORDERS_BY_MONTH, CONTRACT_Hour_Breakout, CONTRACT_LABOR_HOURS_F, CONTRACTS MAPPING, CONTRACTS_BILLING_F, CONTRACTS_D, CONTRACTS_TASK_SCHEDULE, Cost Types, CUSTOMERS_D, DIVISION, FORECASTED CALLS COST, POSTING_DATA_F, Refresh Date, SERV_TASKS_F

## Relationships
| From | To | Active | Join behavior |
|---|---|---:|---|
| `CUSTOMERS_D.CREATED` | `LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f.Date` | true | datePartOnly |
| `CUSTOMERS_D.UPDATED` | `LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356.Date` | true | datePartOnly |
| `BUDGET_F.DIVISION` | `DIVISION.'DIVISION KEY'` | true |  |
| `POSTING_DATA_F.DIVISION` | `DIVISION.'DIVISION KEY'` | true |  |
| `'Refresh Date'.Date` | `LocalDateTable_8931b809-08ab-4252-8179-ca3c21383cd6.Date` | true | datePartOnly |
| `APPOINTMENTS_F.SERVICE_CALL_KEY` | `CALLS_F.SERVICE_CALL_KEY` | true |  |
| `SERV_TASKS_F.CUSTNMBR_KEY` | `CUSTOMERS_D.CUSTOMER_KEY` | true |  |
| `CALLS_F.COMPLETION_DATE` | `LocalDateTable_8d221eb4-201c-477f-89c5-03c6e03aa65e.Date` | true | datePartOnly |
| `CONTRACTS_D.Customer-Contract` | `'CONTRACTS MAPPING'.Customer-Contract` | true |  |
| `CALLS_F.'Customer - Contract'` | `'CONTRACTS MAPPING'.Customer-Contract` | true |  |
| `'CONTRACTS MAPPING'.CUSTNMBR` | `CUSTOMERS_D.CUSTOMER_NUMBER` | true |  |
| `'CALLS COSTS'.DATE_OF_SERVICE_CALL` | `LocalDateTable_2a249574-7315-48a3-bf2c-4c9bbab9a923.Date` | true | datePartOnly |
| `'CALLS COSTS'.SERVICE_CALL_ID` | `CALLS_F.SERVICE_CALL_ID` | true |  |
| `CONTRACTS_BILLING_F.DATE1` | `LocalDateTable_c357c417-93f4-4ea3-badf-ef0dec761ede.Date` | true | datePartOnly |
| `CONTRACTS_BILLING_F.WS_GL_POSTING_DATE` | `LocalDateTable_e59f379f-de3d-42a7-bd84-6e80ef7a5ed8.Date` | true | datePartOnly |
| `CONTRACTS_BILLING_F.Customer-Contract` | `'CONTRACTS MAPPING'.Customer-Contract` | true |  |
| `Calendar.Date` | `LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae.Date` | true | datePartOnly |
| `CHANGE_ORDERS_BY_MONTH.Date` | `Calendar.Date` | true |  |
| `BUDGET_F.PERIODDT` | `Calendar.Date` | true |  |
| `POSTING_DATA_F.Date` | `Calendar.Date` | true |  |
| `CONTRACTS_BILLING_F.WENNSOFT_BILLING_DATE` | `Calendar.Date` | true |  |
| `Calendar.WeekBeginDate` | `LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98.Date` | true | datePartOnly |
| `Calendar.WeekEndDate` | `LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f.Date` | true | datePartOnly |
| `'FORECASTED CALLS COST'.'Customer - Contract'` | `'CONTRACTS MAPPING'.Customer-Contract` | true |  |
| `'CALLS COSTS'.'Cost Type'` | `'Cost Types'.'Cost Type'` | true |  |
| `'FORECASTED CALLS COST'.'Cost Type'` | `'Cost Types'.'Cost Type'` | true |  |
| `'FORECASTED CALLS COST'.CONTRACT_START_DATE` | `LocalDateTable_287ff984-7355-4b13-9018-95e3a16e18e9.Date` | true | datePartOnly |
| `'FORECASTED CALLS COST'.CONTRACT_EXPIRATION_DATE` | `LocalDateTable_68db00b3-6e04-4ee2-a4a3-b33365193de7.Date` | true | datePartOnly |
| `APPOINTMENTS_F.TASK_DATE` | `Calendar.Date` | false |  |
| `CALLS_F.DATE_OF_SERVICE_CALL` | `LocalDateTable_de817910-54ca-42f0-b798-d1ae454cca2b.Date` | true | datePartOnly |
| `CONTRACT_Hour_Breakout.CONTRACT_START_DATE` | `LocalDateTable_36fb0cc6-3a6a-46f4-99fe-6340fb69c6b3.Date` | true | datePartOnly |
| `CONTRACT_Hour_Breakout.CONTRACT_EXPIRATION_DATE` | `LocalDateTable_4ed2ebea-2956-4a45-b593-72e2e76dd90c.Date` | true | datePartOnly |
| `CONTRACTS_D.WENNSOFT_CLOSE_DATE` | `LocalDateTable_1997b5af-fbda-41ee-846d-31f24c5d8bd7.Date` | true | datePartOnly |
| `CONTRACTS_D.CONTRACT_START_DATE` | `LocalDateTable_7568775e-9707-49cb-bf23-8bca38b29542.Date` | true | datePartOnly |
| `CONTRACTS_D.CONTRACT_EXPIRATION_DATE` | `LocalDateTable_a823d9da-2d68-472e-bea7-b1c1f0ea5afc.Date` | true | datePartOnly |
| `CONTRACT_Hour_Breakout.Customer-Contract` | `'CONTRACTS MAPPING'.Customer-Contract` | true |  |
| `'CONTRACTS MAPPING'.'Current Contract Start'` | `LocalDateTable_dea31c23-1eaa-490c-ab59-1e5b655fb2ca.Date` | true | datePartOnly |
| `'CONTRACTS MAPPING'.'Current Contract Expiration'` | `LocalDateTable_2e841b8c-c7b1-4df6-aaad-a1a446fc7c01.Date` | true | datePartOnly |
| `CONTRACTS_TASK_SCHEDULE.ORIGINAL_SCHEDULE_DATE` | `LocalDateTable_7b8a7d6f-03de-4370-ab61-70ffffb79124.Date` | true | datePartOnly |
| `CONTRACTS_TASK_SCHEDULE.SCHEDULE_DATE` | `Calendar.Date` | false |  |
| `CONTRACTS_TASK_SCHEDULE.SERVICE_CALL_ID` | `CALLS_F.SERVICE_CALL_ID` | false |  |
| `CONTRACTS_TASK_SCHEDULE.Customer-Contract` | `'CONTRACTS MAPPING'.Customer-Contract` | false |  |
| `CALLS_F.CREATED_DATE` | `LocalDateTable_00e51d8d-231f-4d65-881b-7cd775844859.Date` | true | datePartOnly |
| `CALLS_F.Completion_Date_Cleaned` | `Calendar.Date` | true |  |
| `CONTRACT_LABOR_HOURS_F.ENTRYDATE` | `LocalDateTable_38f12a90-c3e3-476c-8af6-3b87ccdcdb64.Date` | true | datePartOnly |
| `CONTRACT_LABOR_HOURS_F.SERVICE_CALL_ID` | `CALLS_F.SERVICE_CALL_ID` | true |  |
