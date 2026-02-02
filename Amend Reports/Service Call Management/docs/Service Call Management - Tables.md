# Service Call Management — Tables + Columns

Generated: 2026-01-22 EST

## Table Summary
| Table | Type | Source | Columns | Measures | Partitions |
|---|---:|---|---:|---:|---:|
| `*Calendar` | Date |  | 29 | 2 | 1 |
| `'*CALL DETAILS'` | Fact | DATA_WAREHOUSE.DW_FINAL.CALL_DETAILS_F (Table) | 3 | 0 | 1 |
| `'*CALLS COSTS'` | Fact | DATA_WAREHOUSE.DW_FINAL.CALLS_F (Table) | 8 | 0 | 1 |
| `*CALLS_F` | Fact | DATA_WAREHOUSE.DW_FINAL.CALLS_F (Table) | 58 | 2 | 1 |
| `'*Cost Types'` |  | DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table) | 1 | 0 | 1 |
| `APPOINTMENTS_F` | Fact | DATA_WAREHOUSE.DW_FINAL.APPOINTMENTS_F (Table) | 13 | 0 | 1 |
| `'Backlog Measures'` | Measures |  | 0 | 17 | 1 |
| `BUDGET_F` | Fact | DATA_WAREHOUSE.DW_FINAL.BUDGET_F (Table) | 17 | 3 | 1 |
| `CHANGE_ORDERS_BY_MONTH` |  | DATA_WAREHOUSE.DW_CLEAN.JOB_CHANGE_ORDERS (View) | 9 | 0 | 1 |
| `'Contract Measures'` | Measures |  | 0 | 37 | 1 |
| `CONTRACT_Hour_Breakout` |  | DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table) | 6 | 1 | 1 |
| `'CONTRACTS MAPPING'` |  | DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table) | 10 | 6 | 1 |
| `CONTRACTS_BILLING_F` | Fact | DATA_WAREHOUSE.DW_FINAL.CONTRACT_BILLING_F (Table) | 15 | 0 | 1 |
| `CONTRACTS_D` | Dim | DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table) | 165 | 5 | 1 |
| `'Cost Measures'` | Measures |  | 0 | 18 | 1 |
| `CUSTOMERS_D` | Dim | DATA_WAREHOUSE.DW_FINAL.CUSTOMERS_D (Table) | 15 | 0 | 1 |
| `DateTableTemplate_ae1bc3b8-dd10-47c1-913a-5f4a589902e6` |  |  | 7 | 0 | 1 |
| `DIVISION` |  | DATA_WAREHOUSE.DW_FINAL.JOBS_D (Table) | 3 | 0 | 1 |
| `'FORECASTED CALLS COST'` |  | DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table) | 7 | 0 | 1 |
| `'GP Parameter'` | Parameter |  | 3 | 0 | 1 |
| `'GP Parameter 2'` | Parameter |  | 3 | 0 | 1 |
| `'Hour Measures'` | Measures |  | 0 | 11 | 1 |
| `INVOICES_F` | Fact | DATA_WAREHOUSE.DW_FINAL.INVOICES_F (Table) | 41 | 0 | 1 |
| `JOB_COST_DESCRIPTION_D` | Dim | DATA_WAREHOUSE.DW_FINAL.JOB_COST_DESCRIPTION_D (Table) | 10 | 0 | 1 |
| `JOB_COST_DETAILS_F` | Fact | DATA_WAREHOUSE.DW_FINAL.JOB_COST_DETAILS_F (Table) | 13 | 0 | 1 |
| `JOB_COST_FORECASTS_F` | Fact | DATA_WAREHOUSE.DW_FINAL.JOB_COST_FORECASTS_F (Table) | 16 | 0 | 1 |
| `JOB_COST_SUMMARY_F` | Fact | DATA_WAREHOUSE.DW_FINAL.JOB_COST_SUMMARY_F (Table) | 22 | 0 | 1 |
| `JOB_LABOR_HOURS_F` | Fact | DATA_WAREHOUSE.DW_FINAL.JOB_LABOR_HOURS_F (Table) | 22 | 0 | 1 |
| `JOBS_D` | Dim | DATA_WAREHOUSE.DW_FINAL.JOBS_D (Table) | 78 | 2 | 1 |
| `LocalDateTable_067dc315-6c09-4dec-b7f8-83a4621f9538` |  |  | 7 | 0 | 1 |
| `LocalDateTable_103d4237-3f13-4fb8-908e-8f990ad5f6f8` |  |  | 7 | 0 | 1 |
| `LocalDateTable_1997b5af-fbda-41ee-846d-31f24c5d8bd7` |  |  | 7 | 0 | 1 |
| `LocalDateTable_26e0a611-4938-40bf-8444-deab64adf683` |  |  | 7 | 0 | 1 |
| `LocalDateTable_287ff984-7355-4b13-9018-95e3a16e18e9` |  |  | 7 | 0 | 1 |
| `LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f` |  |  | 7 | 0 | 1 |
| `LocalDateTable_3068354c-1934-4176-9b53-101d178cc7da` |  |  | 7 | 0 | 1 |
| `LocalDateTable_36fb0cc6-3a6a-46f4-99fe-6340fb69c6b3` |  |  | 7 | 0 | 1 |
| `LocalDateTable_39148a68-5226-4488-8b67-dc23f90c2fda` |  |  | 7 | 0 | 1 |
| `LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f` |  |  | 7 | 0 | 1 |
| `LocalDateTable_47a0a9ed-d6a7-45b3-8712-f282871bb09b` |  |  | 7 | 0 | 1 |
| `LocalDateTable_4d5c68a9-1016-4c7f-8bd6-94b091483340` |  |  | 7 | 0 | 1 |
| `LocalDateTable_4ed2ebea-2956-4a45-b593-72e2e76dd90c` |  |  | 7 | 0 | 1 |
| `LocalDateTable_50ba8d0a-c214-4c60-9636-91d2b083e293` |  |  | 7 | 0 | 1 |
| `LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356` |  |  | 7 | 0 | 1 |
| `LocalDateTable_5d34ecff-b08a-4195-96aa-bbe1838c84a1` |  |  | 7 | 0 | 1 |
| `LocalDateTable_5d8bdd04-066c-4f23-a512-15bb2e1f01ca` |  |  | 7 | 0 | 1 |
| `LocalDateTable_642e469c-fa06-4889-a5c5-da80969ee27d` |  |  | 7 | 0 | 1 |
| `LocalDateTable_64fe1dd5-f9b1-4852-a834-01f2f06edc86` |  |  | 7 | 0 | 1 |
| `LocalDateTable_68db00b3-6e04-4ee2-a4a3-b33365193de7` |  |  | 7 | 0 | 1 |
| `LocalDateTable_69547476-3a6b-4a5f-8fcf-f5f0ffbaa28e` |  |  | 7 | 0 | 1 |
| `LocalDateTable_6f07f3db-d19d-48bb-b5ed-282740e59d98` |  |  | 7 | 0 | 1 |
| `LocalDateTable_7568775e-9707-49cb-bf23-8bca38b29542` |  |  | 7 | 0 | 1 |
| `LocalDateTable_7c0dba22-51a6-475f-9385-01ea578d2301` |  |  | 7 | 0 | 1 |
| `LocalDateTable_820e8c9a-6a47-49de-b350-058a53302479` |  |  | 7 | 0 | 1 |
| `LocalDateTable_8931b809-08ab-4252-8179-ca3c21383cd6` |  |  | 7 | 0 | 1 |
| `LocalDateTable_8f32177c-7b7f-4b5c-afda-6d8a43f3b74a` |  |  | 7 | 0 | 1 |
| `LocalDateTable_94301b25-21a8-4b87-85fd-d52dcf5a2675` |  |  | 7 | 0 | 1 |
| `LocalDateTable_99560294-9e13-479c-8ec0-753af2fa9a9a` |  |  | 7 | 0 | 1 |
| `LocalDateTable_a1304e08-f471-47dc-bbfc-f6653e634bfb` |  |  | 7 | 0 | 1 |
| `LocalDateTable_a823d9da-2d68-472e-bea7-b1c1f0ea5afc` |  |  | 7 | 0 | 1 |
| `LocalDateTable_baee53e5-31d8-4e45-9586-0421c65b3c1b` |  |  | 7 | 0 | 1 |
| `LocalDateTable_bb15f284-7b12-463e-a9c4-99deba2bdfad` |  |  | 7 | 0 | 1 |
| `LocalDateTable_bbf43f8a-d468-47fb-ac04-f39d8ec857ca` |  |  | 7 | 0 | 1 |
| `LocalDateTable_c357c417-93f4-4ea3-badf-ef0dec761ede` |  |  | 7 | 0 | 1 |
| `LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98` |  |  | 7 | 0 | 1 |
| `LocalDateTable_d0b0fafd-2a43-42cf-b4c1-2da93e58802e` |  |  | 7 | 0 | 1 |
| `LocalDateTable_dbc8e48e-68af-4633-963c-bd15e3755808` |  |  | 7 | 0 | 1 |
| `LocalDateTable_dc9a7e8b-973c-4d72-ad27-3eff05a132d9` |  |  | 7 | 0 | 1 |
| `LocalDateTable_de817910-54ca-42f0-b798-d1ae454cca2b` |  |  | 7 | 0 | 1 |
| `LocalDateTable_df4ab1e5-1799-472a-b536-48d903e2a6f1` |  |  | 7 | 0 | 1 |
| `LocalDateTable_e2d949a2-51a9-4559-aff7-c4bc089c82a9` |  |  | 7 | 0 | 1 |
| `LocalDateTable_e59f379f-de3d-42a7-bd84-6e80ef7a5ed8` |  |  | 7 | 0 | 1 |
| `LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae` |  |  | 7 | 0 | 1 |
| `LocalDateTable_ef2c59c0-67cf-4d48-a6f0-98880a30fca3` |  |  | 7 | 0 | 1 |
| `LocalDateTable_f01fab4d-aa91-41ef-a8c9-deae6fe393db` |  |  | 7 | 0 | 1 |
| `OPEN_TRANSACTIONS_F` | Fact | DATA_WAREHOUSE.DW_FINAL.OPEN_TRANSACTIONS_F (Table) | 77 | 0 | 1 |
| `POSTING_DATA_F` | Fact | DATA_WAREHOUSE.DW_FINAL.POSTING_DATA_F (Table) | 19 | 0 | 1 |
| `'Refresh Date'` |  |  | 2 | 1 | 1 |
| `'Revenue Measures'` | Measures |  | 0 | 42 | 1 |
| `SERV_TASKS_F` | Fact | DATA_WAREHOUSE.DW_FINAL.TASKS_F (Table) | 22 | 0 | 1 |
| `'Service Call Measures'` | Measures |  | 0 | 36 | 1 |

## Service-call tables (expanded)

### `*CALL DETAILS`
- Source: `DATA_WAREHOUSE.DW_FINAL.CALL_DETAILS_F`
- Used for billings (Revenue proxy): `*CALL DETAILS[BILLING_AMOUNT]`
- Columns:
  - `SERVICE_CALL_ID` (string)
  - `DATE` (date)
  - `BILLING_AMOUNT` (double)

### `*CALLS_F`
- Source: `DATA_WAREHOUSE.DW_FINAL.CALLS_F`
- Primary service call fact table (status/type, dates, and cost columns).
- Notes:
  - `Service Call Measures` commonly filters `*CALLS_F[STATUS_OF_CALL] = "CLOSED"` for “actual” GP.
  - This table also defines two measures that are not part of the core revenue/GP logic: `*CALLS_F[Late PMs]` and `*CALLS_F[Late PM Revenue]` (both filter open “GENERATED MC” calls with days open > 60).

### `*CALLS COSTS`
- Source base table: `DATA_WAREHOUSE.DW_FINAL.CALLS_F` (unpivoted)
- This table is created in Power Query by selecting cost columns from `CALLS_F` (`COST_EQUIPMENT`, `COST_LABOR`, `COST_MATERIAL`, `COST_OTHER`, `COST_SUBS`, `COST_TAX`) and unpivoting them into:
  - `Cost Type` (text: EQUIPMENT/LABOR/MATERIAL/OTHER/SUBS/TAX)
  - `Value` (numeric)
- Key fields:
  - `SERVICE_CALL_ID`, `CONTRACT_NUMBER`, `DATE_OF_SERVICE_CALL`, `Customer - Contract`, `WSCONTSQ`, `In Current Contract`, `Cost Type`, `Value`

### `*Calendar`
- Model-generated date table used for fiscal year filters and “as-of date” logic.

## Non-service-call tables
This semantic model includes job/project (`JOBS_D`, `JOB_COST_*`, `INVOICES_F`) and contract/backlog (`CONTRACTS_*`, `POSTING_DATA_F`) tables which appear to be shared/copy artifacts across reports. They are included in the table summary above but are not expanded here, per the “focus on service call” request.
