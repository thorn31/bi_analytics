# Contract Management — Tables + Columns

Generated: 2026-01-22 15:09 EST

## Table Summary
| Table | Type | Source | Columns | Measures | Partitions |
|---|---:|---|---:|---:|---:|
| `APPOINTMENTS_F` | Table | DATA_WAREHOUSE.DW_FINAL.APPOINTMENTS_F (Table) | 13 | 0 | 1 |
| `BUDGET_F` | Table | DATA_WAREHOUSE.DW_FINAL.BUDGET_F (Table) | 17 | 3 | 1 |
| `Calendar` | Date |  | 28 | 1 | 1 |
| `CALLS COSTS` | Table | DATA_WAREHOUSE.DW_FINAL.CALLS_F (Table) | 8 | 0 | 1 |
| `CALLS_F` | Table | DATA_WAREHOUSE.DW_FINAL.CALLS_F (Table) | 58 | 3 | 1 |
| `CHANGE_ORDERS_BY_MONTH` | Table | DATA_WAREHOUSE.DW_CLEAN.JOB_CHANGE_ORDERS (View) | 9 | 0 | 1 |
| `Contract Measures` | Measures |  | 0 | 42 | 1 |
| `CONTRACT_Hour_Breakout` | Table | DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table) | 6 | 1 | 1 |
| `CONTRACT_LABOR_HOURS_F` | Table | DATA_WAREHOUSE.DW_FINAL.CONTRACT_LABOR_HOURS_F (Table) | 15 | 0 | 1 |
| `CONTRACTS MAPPING` | Table | DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table) | 10 | 6 | 1 |
| `CONTRACTS_BILLING_F` | Table | DATA_WAREHOUSE.DW_FINAL.CONTRACT_BILLING_F (Table) | 15 | 0 | 1 |
| `CONTRACTS_D` | Table | DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table) | 165 | 5 | 1 |
| `CONTRACTS_TASK_SCHEDULE` | Table | DATA_WAREHOUSE.DW_FINAL.SERV_CONTRACT_TASKS_F (Table) | 23 | 0 | 1 |
| `Cost Measures` | Measures |  | 0 | 18 | 1 |
| `Cost Types` | Table | DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table) | 1 | 0 | 1 |
| `CUSTOMERS_D` | Table | DATA_WAREHOUSE.DW_FINAL.CUSTOMERS_D (Table) | 15 | 0 | 1 |
| `DateTableTemplate_ae1bc3b8-dd10-47c1-913a-5f4a589902e6` | Date |  | 7 | 0 | 1 |
| `DIVISION` | Table | DATA_WAREHOUSE.DW_FINAL.JOBS_D (Table) | 3 | 0 | 1 |
| `FORECASTED CALLS COST` | Table | DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table) | 7 | 0 | 1 |
| `GP Parameter` | Parameter |  | 3 | 0 | 1 |
| `GP Parameter 2` | Parameter |  | 3 | 0 | 1 |
| `Hour Measures` | Measures |  | 0 | 15 | 1 |
| `LocalDateTable_00e51d8d-231f-4d65-881b-7cd775844859` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_1997b5af-fbda-41ee-846d-31f24c5d8bd7` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_287ff984-7355-4b13-9018-95e3a16e18e9` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_2a249574-7315-48a3-bf2c-4c9bbab9a923` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_2e841b8c-c7b1-4df6-aaad-a1a446fc7c01` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_36fb0cc6-3a6a-46f4-99fe-6340fb69c6b3` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_38f12a90-c3e3-476c-8af6-3b87ccdcdb64` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_4ed2ebea-2956-4a45-b593-72e2e76dd90c` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_68db00b3-6e04-4ee2-a4a3-b33365193de7` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_7568775e-9707-49cb-bf23-8bca38b29542` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_7b8a7d6f-03de-4370-ab61-70ffffb79124` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_8931b809-08ab-4252-8179-ca3c21383cd6` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_8d221eb4-201c-477f-89c5-03c6e03aa65e` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_a823d9da-2d68-472e-bea7-b1c1f0ea5afc` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_c357c417-93f4-4ea3-badf-ef0dec761ede` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_de817910-54ca-42f0-b798-d1ae454cca2b` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_dea31c23-1eaa-490c-ab59-1e5b655fb2ca` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_e59f379f-de3d-42a7-bd84-6e80ef7a5ed8` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae` | Date |  | 7 | 0 | 1 |
| `POSTING_DATA_F` | Table | DATA_WAREHOUSE.DW_FINAL.POSTING_DATA_F (Table) | 19 | 0 | 1 |
| `Refresh Date` | Table |  | 2 | 1 | 1 |
| `Revenue Measures` | Measures |  | 0 | 42 | 1 |
| `SERV_TASKS_F` | Table | DATA_WAREHOUSE.DW_FINAL.TASKS_F (Table) | 22 | 0 | 1 |

## Table Details

### APPOINTMENTS_F
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.APPOINTMENTS_F (Table)
- Partitions: `APPOINTMENTS_F` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `SERVICE_CALL_ID` | string | SERVICE_CALL_ID |  | none |  |  |
| `APPOINTMENT` | string | APPOINTMENT |  | none |  |  |
| `TECHNICIAN` | string | TECHNICIAN |  | none |  |  |
| `TASK_DATE` | dateTime | TASK_DATE |  | none | Short Date |  |
| `STRTTIME` | dateTime | STRTTIME |  | none | Long Time |  |
| `ENDTIME` | dateTime | ENDTIME |  | none | Long Time |  |
| `ESTIMATE_HOURS` | double | ESTIMATE_HOURS |  | sum |  |  |
| `ACTUAL_HOURS` | double | ACTUAL_HOURS |  | sum |  |  |
| `APPOINTMENT_STATUS` | string | APPOINTMENT_STATUS |  | none |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `SERVICE_CALL_KEY` | string | SERVICE_CALL_KEY |  | none |  |  |
| `SERVICE_CALL_APPOINTMENT_KEY` | string | SERVICE_CALL_APPOINTMENT_KEY |  | none |  |  |
| `Customer-Contract` | string | Customer-Contract |  | none |  |  |

### BUDGET_F
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.BUDGET_F (Table)
- Partitions: `BUDGET_F` (m, import)
- Measures: 3

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `BUDGETID` | string | BUDGETID |  | none |  |  |
| `PERIODDT` | dateTime | PERIODDT |  | none | Long Date |  |
| `BUDGETAMT` | double | BUDGETAMT |  | sum |  |  |
| `YEAR` | double | YEAR |  | sum |  |  |
| `FISCAL_MONTH` | double | FISCAL_MONTH |  | sum |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `ACCATNUM` | string | ACCATNUM |  | none |  |  |
| `ACTINDX` | string | ACTINDX |  | none |  |  |
| `ACCTNUM_KEY` | string | ACCTNUM_KEY |  | none |  |  |
| `ACCTIDX_KEY` | string | ACCTIDX_KEY |  | none |  |  |
| `ACCOUNT_TYPE` | string | ACCOUNT_TYPE |  | none |  |  |
| `DIVISION` | string | DIVISION |  | none |  |  |
| `ACTNUMBR_1` | string | ACTNUMBR_1 |  | none |  |  |
| `ACTNUMBR_2` | string | ACTNUMBR_2 |  | none |  |  |
| `ACTNUMBR_3` | string | ACTNUMBR_3 |  | none |  |  |
| `ACTNUMST` | string | ACTNUMST |  | none |  |  |
| `CATEGORY` | string | CATEGORY |  | none |  |  |

### Calendar
- Type: Date
- Partitions: `Calendar-d7293210-4553-47c2-8825-e570d51daaae` (calculated, import)
- Measures: 1

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `Date` |  | [Date] |  | none | Long Date |  |
| `Year` |  | [Year] |  | sum | 0 |  |
| `Quarter` |  | [Quarter] |  | none |  |  |
| `Month` |  | [Month] |  | none |  |  |
| `MonthSort` |  | [MonthSort] |  | none |  |  |
| `YearMonthnumber` |  | [YearMonthnumber] |  | none |  |  |
| `YearMonthShort` |  | [YearMonthShort] |  | none |  |  |
| `MonthNumber` |  | [MonthNumber] |  | sum | 0 |  |
| `MonthNameShort` |  | [MonthNameShort] |  | none |  |  |
| `MonthNameLong` |  | [MonthNameLong] |  | none |  |  |
| `DayOfWeekNumber` |  | [DayOfWeekNumber] |  | sum | 0 |  |
| `DayOfWeek` |  | [DayOfWeek] |  | none |  |  |
| `DayOfWeekShort` |  | [DayOfWeekShort] |  | none |  |  |
| `YearQuarter` |  | [YearQuarter] |  | none |  |  |
| `WeekNumber` |  | [WeekNumber] |  | sum | 0 |  |
| `DisplayMonth` |  | [DisplayMonth] |  | none |  |  |
| `WeekBeginDate` |  | [WeekBeginDate] |  | none | General Date |  |
| `WeekEndDate` |  | [WeekEndDate] |  | none | Short Date |  |
| `IsWeekday` |  | [IsWeekday] |  | none | """TRUE"";""TRUE"";""FALSE""" |  |
| `1` |  |  | (calc) | sum | 0 |  |
| `Future Flag` |  |  | (calc) | sum | 0 |  |
| `New Month Flag` |  |  | (calc) | sum | 0 |  |
| `Running Total Month` |  |  | (calc) | sum | 0 |  |
| `Last Month Filter` |  |  | (calc) | none |  |  |
| `Fiscal Year` |  | [Fiscal Year] |  | sum | 0 |  |
| `Fiscal Calendar` |  |  | (calc) | sum | 0 |  |
| `Year Filter` |  |  | (calc) | sum | 0 |  |
| `TT` |  |  | (calc) | none |  |  |

### CALLS COSTS
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.CALLS_F (Table)
- Partitions: `CALLS COSTS` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `SERVICE_CALL_ID` | string | SERVICE_CALL_ID |  | none |  |  |
| `CONTRACT_NUMBER` | string | CONTRACT_NUMBER |  | none |  |  |
| `DATE_OF_SERVICE_CALL` | dateTime | DATE_OF_SERVICE_CALL |  | none | Long Date |  |
| `Customer - Contract` | string | Customer - Contract |  | none |  |  |
| `Cost Type` | string | Cost Type |  | none |  |  |
| `Value` | double | Value |  | sum | \$#,0;(\$#,0);\$#,0 |  |
| `In Current Contract` |  |  | (calc) | sum | 0 |  |
| `WSCONTSQ` | double | WSCONTSQ |  | sum |  |  |

### CALLS_F
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.CALLS_F (Table)
- Partitions: `CALLS_F` (m, import)
- Measures: 3

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `SERVICE_CALL_ID` | string | SERVICE_CALL_ID |  | none |  |  |
| `SERVICE_DESCRIPTION` | string | SERVICE_DESCRIPTION |  | none |  |  |
| `CUSTNMBR` | string | CUSTNMBR |  | none |  |  |
| `TECHNICIAN` | string | TECHNICIAN |  | none |  |  |
| `TYPE_OF_PROBLEM` | string | TYPE_OF_PROBLEM |  | none |  |  |
| `RESOLUTION_DESCRIPTION` | string | RESOLUTION_DESCRIPTION |  | none |  |  |
| `TYPE_OF_CALL` | string | TYPE_OF_CALL |  | none |  |  |
| `DATE_OF_SERVICE_CALL` | dateTime | DATE_OF_SERVICE_CALL |  | none | Long Date |  |
| `BILLING_AMOUNT_FIXED` | double | BILLING_AMOUNT_FIXED |  | sum |  |  |
| `BILLING_AMOUNT_NTE` | double | BILLING_AMOUNT_NTE |  | sum |  |  |
| `BILLABLE_ALL` | double | BILLABLE_ALL |  | sum |  |  |
| `COST_ALL` | double | COST_ALL |  | sum |  |  |
| `TAX_AMOUNT1` | double | TAX_AMOUNT1 |  | sum |  |  |
| `TAX_AMOUNT2` | double | TAX_AMOUNT2 |  | sum |  |  |
| `TAX_AMOUNT3` | double | TAX_AMOUNT3 |  | sum |  |  |
| `LABOR_BILLING_CATAGORY_1` | double | LABOR_BILLING_CATAGORY_1 |  | sum |  |  |
| `LABOR_BILLING_CATAGORY_2` | double | LABOR_BILLING_CATAGORY_2 |  | sum |  |  |
| `LABOR_BILLING_CATAGORY_3` | double | LABOR_BILLING_CATAGORY_3 |  | sum |  |  |
| `LABOR_BILLING_CATAGORY_4` | double | LABOR_BILLING_CATAGORY_4 |  | sum |  |  |
| `LABOR_BILLING_CATAGORY_5` | double | LABOR_BILLING_CATAGORY_5 |  | sum |  |  |
| `BILLABLE_EQUIPMENT` | double | BILLABLE_EQUIPMENT |  | sum |  |  |
| `BILLABLE_LABOR` | double | BILLABLE_LABOR |  | sum |  |  |
| `BILLABLE_MATERIAL` | double | BILLABLE_MATERIAL |  | sum |  |  |
| `BILLABLE_OTHER` | double | BILLABLE_OTHER |  | sum |  |  |
| `BILLABLE_SUBS` | double | BILLABLE_SUBS |  | sum |  |  |
| `BILLABLE_TAX` | double | BILLABLE_TAX |  | sum |  |  |
| `LABOR_COST_CATAGORY_1` | double | LABOR_COST_CATAGORY_1 |  | sum |  |  |
| `LABOR_COST_CATAGORY_2` | double | LABOR_COST_CATAGORY_2 |  | sum |  |  |
| `LABOR_COST_CATAGORY_3` | double | LABOR_COST_CATAGORY_3 |  | sum |  |  |
| `LABOR_COST_CATAGORY_4` | double | LABOR_COST_CATAGORY_4 |  | sum |  |  |
| `LABOR_COST_CATAGORY_5` | double | LABOR_COST_CATAGORY_5 |  | sum |  |  |
| `COST_EQUIPMENT` | double | COST_EQUIPMENT |  | sum |  |  |
| `COST_LABOR` | double | COST_LABOR |  | sum |  |  |
| `COST_MATERIAL` | double | COST_MATERIAL |  | sum |  |  |
| `COST_OTHER` | double | COST_OTHER |  | sum |  |  |
| `COST_SUBS` | double | COST_SUBS |  | sum |  |  |
| `COST_TAX` | double | COST_TAX |  | sum |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `SERVICE_CALL_KEY` | string | SERVICE_CALL_KEY |  | none |  |  |
| `CUSTOMERNBR_KEY` | string | CUSTOMERNBR_KEY |  | none |  |  |
| `STATUS_OF_CALL` | string | STATUS_OF_CALL |  | none |  |  |
| `COMPLETION_DATE` | dateTime | COMPLETION_DATE |  | none | General Date |  |
| `CREATED_DATE` | dateTime | CREATED_DATE |  | none | Short Date |  |
| `BILLING_STATUS` | string | BILLING_STATUS |  | none |  |  |
| `INVOICE_STYLE` | double | INVOICE_STYLE |  | sum |  |  |
| `INVOICE_TYPE` | double | INVOICE_TYPE |  | sum |  |  |
| `Completion_Date_Cleaned` |  |  | (calc) | none | Long Date |  |
| `Calculated_Days_Open` |  |  | (calc) | sum | 0 |  |
| `CONTRACT_NUMBER` | string | CONTRACT_NUMBER |  | none |  |  |
| `DIVISIONS` | string | DIVISIONS |  | none |  |  |
| `Customer - Contract` | string | Customer - Contract |  | none |  |  |
| `In Current Contract` |  |  | (calc) | sum | 0 |  |
| `Monthly Revenue` |  |  | (calc) | sum | \$#,0;(\$#,0);\$#,0 |  |
| `WSCONTSQ` | double | WSCONTSQ |  | sum |  |  |
| `INVOICE_TYPE_UDF1A` | string | INVOICE_TYPE_UDF1A |  | none |  |  |
| `BILLING_TYPE_UDF2A` | string | BILLING_TYPE_UDF2A |  | none |  |  |
| `DIVISIONS_CLEAN` | string | DIVISIONS_CLEAN |  | none |  |  |
| `ESTIMATED_HOURS` | double | ESTIMATED_HOURS |  | sum |  |  |

### CHANGE_ORDERS_BY_MONTH
- Type: Table
- Source: DATA_WAREHOUSE.DW_CLEAN.JOB_CHANGE_ORDERS (View)
- Partitions: `CHANGE_ORDERS_BY_MONTH` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `CHANGE_ORDER_EST_COST` | double | CHANGE_ORDER_EST_COST |  | sum |  |  |
| `Date` |  |  | (calc) | none | Long Date |  |
| `JOB_NUMBER` | string | JOB_NUMBER |  | none |  |  |
| `CHANGE_ORDER_NUMBER` | string | CHANGE_ORDER_NUMBER |  | none |  |  |
| `FIRSCAL_YEAR` | double | FIRSCAL_YEAR |  | sum |  |  |
| `FISCAL_MONTH` | double | FISCAL_MONTH |  | sum |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `RN` | double | RN |  | sum |  |  |
| `JOB_KEY` | string | JOB_KEY |  | none |  |  |

### Contract Measures
- Type: Measures
- Partitions: `Contract Measures` (m, import)
- Measures: 42

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|

### CONTRACT_Hour_Breakout
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table)
- Partitions: `CONTRACT_Hour_Breakout` (m, import)
- Measures: 1

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `Customer-Contract` | string | Customer-Contract |  | none |  |  |
| `CONTRACT_START_DATE` | dateTime | CONTRACT_START_DATE |  | none | Long Date |  |
| `CONTRACT_EXPIRATION_DATE` | dateTime | CONTRACT_EXPIRATION_DATE |  | none | Long Date |  |
| `Type` | string | Type |  | none |  |  |
| `Hours` | double | Hours |  | sum |  |  |
| `In Current Contract` |  |  | (calc) | sum | 0 |  |

### CONTRACT_LABOR_HOURS_F
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.CONTRACT_LABOR_HOURS_F (Table)
- Partitions: `CONTRACT_LABOR_HOURS_F` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `SERVICE_CALL_ID` | string | SERVICE_CALL_ID |  | none |  |  |
| `APPOINTMENT` | string | APPOINTMENT |  | none |  |  |
| `ENTRYDATE` | dateTime | ENTRYDATE |  | none | Long Date |  |
| `EMPLOYID` | string | EMPLOYID |  | none |  |  |
| `BILLING_TYPE` | string | BILLING_TYPE |  | none |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `HOURS` | double | HOURS |  | sum |  |  |
| `MONDAY` | double | MONDAY |  | sum |  |  |
| `TUESDAY` | double | TUESDAY |  | sum |  |  |
| `WEDNESDAY` | double | WEDNESDAY |  | sum |  |  |
| `THURSDAY` | double | THURSDAY |  | sum |  |  |
| `FRIDAY` | double | FRIDAY |  | sum |  |  |
| `SATURDAY` | double | SATURDAY |  | sum |  |  |
| `SUNDAY` | double | SUNDAY |  | sum |  |  |
| `SERVICE_CALL_KEY` | string | SERVICE_CALL_KEY |  | none |  |  |

### CONTRACTS MAPPING
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table)
- Partitions: `CONTRACTS MAPPING` (m, import)
- Measures: 6

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `CUSTNMBR` | string | CUSTNMBR |  | none |  |  |
| `CONTRACT_NUMBER` | string | CONTRACT_NUMBER |  | none |  |  |
| `Customer-Contract` | string | Customer-Contract |  | none |  |  |
| `Contract Status` |  |  | (calc) | none |  |  |
| `Contract Type` |  |  | (calc) | none |  |  |
| `Divisions` |  |  | (calc) | none |  |  |
| `Sales Rep` |  |  | (calc) | none |  |  |
| `Current Contract Start` |  |  | (calc) | none | General Date |  |
| `Current Contract Expiration` |  |  | (calc) | none | General Date |  |
| `Contract Cancelled` |  |  | (calc) | none | """TRUE"";""TRUE"";""FALSE""" |  |

### CONTRACTS_BILLING_F
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.CONTRACT_BILLING_F (Table)
- Partitions: `CONTRACTS_BILLING_F` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `CUSTNMBR` | string | CUSTNMBR |  | none |  |  |
| `CONTRACT_NUMBER` | string | CONTRACT_NUMBER |  | none |  |  |
| `DATE1` | dateTime | DATE1 |  | none | Long Date |  |
| `WENNSOFT_BILLING_DATE` | dateTime | WENNSOFT_BILLING_DATE |  | none | Long Date |  |
| `WENNSOFT_PERIOD_ID` | double | WENNSOFT_PERIOD_ID |  | count |  |  |
| `BILLABLE_ALL` | double | BILLABLE_ALL |  | sum |  |  |
| `BILLABLE_SUBTOTAL` | double | BILLABLE_SUBTOTAL |  | sum |  |  |
| `PORDNMBR` | string | PORDNMBR |  | none |  |  |
| `WS_GL_POSTING_DATE` | dateTime | WS_GL_POSTING_DATE |  | none | General Date |  |
| `MAX_WSCONTSQ` | double | MAX_WSCONTSQ |  | sum |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `CONTRACT_NUMBER_KEY` | string | CONTRACT_NUMBER_KEY |  | none |  |  |
| `CUSTNMBR_KEY` | string | CUSTNMBR_KEY |  | none |  |  |
| `Customer-Contract` | string | Customer-Contract |  | none |  |  |
| `In Current Contract` |  |  | (calc) | sum | 0 |  |

### CONTRACTS_D
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table)
- Partitions: `CONTRACTS_D` (m, import)
- Measures: 5

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `Backlog Amount` |  |  | (calc) | none | \$#,0;(\$#,0);\$#,0 |  |
| `Backlog GP` |  |  | (calc) | none | \$#,0;(\$#,0);\$#,0 |  |
| `Backlog Raw Hours Contract` |  |  | (calc) | none | 0 |  |
| `% to Complete` |  |  | (calc) | none | 0%;-0%;0% |  |
| `Contract Status Date` |  |  | (calc) | none |  |  |
| `Hours Owed` |  |  | (calc) | sum | 0 |  |
| `YTD Expected GP` |  |  | (calc) | sum | \$#,0.00;(\$#,0.00);\$#,0.00 |  |
| `Calculated Gross Profit` |  |  | (calc) | none | \$#,0.00;(\$#,0.00);\$#,0.00 |  |
| `GP Margin %` |  |  | (calc) | none | 0.0%;-0.0%;0.0% |  |
| `Customer-Contract` | string | Customer-Contract |  | none |  |  |
| `Current Contract Flag` |  |  | (calc) | none | 0 |  |
| `CLEANED_DIVISIONS` | string | CLEANED_DIVISIONS |  | none |  |  |
| `CONTRACT_TYPE` | string | CONTRACT_TYPE |  | none |  |  |
| `CUSTNMBR` | string | CUSTNMBR |  | none |  |  |
| `CONTRACT_NUMBER` | string | CONTRACT_NUMBER |  | none |  |  |
| `CONTRACT_DESCRIPTION` | string | CONTRACT_DESCRIPTION |  | none |  |  |
| `CONTRACT_STATUS` | string | CONTRACT_STATUS |  | none |  |  |
| `CONTRACT_INTERNAL_NAME` | string | CONTRACT_INTERNAL_NAME |  | none |  |  |
| `CANCEL_BOX` | boolean | CANCEL_BOX |  | none | """TRUE"";""TRUE"";""FALSE""" |  |
| `DIVISIONS` | string | DIVISIONS |  | none |  |  |
| `CONTRACT_AMOUNT` | double | CONTRACT_AMOUNT |  | sum |  |  |
| `WSCONTRACTRENEWALVALUE` | double | WSCONTRACTRENEWALVALUE |  | sum |  |  |
| `BILL_FREQ` | double | BILL_FREQ |  | sum |  |  |
| `WENNSOFT_CLOSE_DATE` | dateTime | WENNSOFT_CLOSE_DATE |  | none | General Date |  |
| `AMOUNT_BILLED` | double | AMOUNT_BILLED |  | sum |  |  |
| `SLPRSNID` | string | SLPRSNID |  | none |  |  |
| `TAXSCHID` | string | TAXSCHID |  | none |  |  |
| `ANNUAL_CONTRACT_VALUE` | double | ANNUAL_CONTRACT_VALUE |  | sum |  |  |
| `REVENUE_REC_METHOD_ID` | double | REVENUE_REC_METHOD_ID |  | count |  |  |
| `INVOICE_STYLE` | double | INVOICE_STYLE |  | sum |  |  |
| `MULTIYEAR_CONTRACT_FLAG` | double | MULTIYEAR_CONTRACT_FLAG |  | sum |  |  |
| `CONTRACT_START_DATE` | dateTime | CONTRACT_START_DATE |  | none | Short Date |  |
| `CONTRACT_EXPIRATION_DATE` | dateTime | CONTRACT_EXPIRATION_DATE |  | none | Short Date |  |
| `FORECAST_ORIGINAL_EQUIP` | double | FORECAST_ORIGINAL_EQUIP |  | sum |  |  |
| `FORECAST_ORIGINAL_LABOR` | double | FORECAST_ORIGINAL_LABOR |  | sum |  |  |
| `FORE_ORIG_MATERIAL` | double | FORE_ORIG_MATERIAL |  | sum |  |  |
| `FORECAST_ORIGINAL_OTHER` | double | FORECAST_ORIGINAL_OTHER |  | sum |  |  |
| `FORECAST_ORIGINAL_SUBS` | double | FORECAST_ORIGINAL_SUBS |  | sum |  |  |
| `FORECAST_ORIG_LABOR_1` | double | FORECAST_ORIG_LABOR_1 |  | sum |  |  |
| `FORECAST_ORIG_LABOR1_HRS_REPAIR` | double | FORECAST_ORIG_LABOR1_HRS_REPAIR |  | sum |  |  |
| `FORECAST_ORIG_LABOR_2` | double | FORECAST_ORIG_LABOR_2 |  | sum |  |  |
| `FORE_ORIG_LABOR_2_HRS_PM` | double | FORE_ORIG_LABOR_2_HRS_PM |  | sum |  |  |
| `FORECAST_ORIG_LABOR_3` | double | FORECAST_ORIG_LABOR_3 |  | sum |  |  |
| `FORECAST_ORIG_LABOR3_HRS_TRAVEL` | double | FORECAST_ORIG_LABOR3_HRS_TRAVEL |  | sum |  |  |
| `FORECAST_ORIG_LABOR_4` | double | FORECAST_ORIG_LABOR_4 |  | sum |  |  |
| `FORECAST_ORIG_LABOR4_HRS` | double | FORECAST_ORIG_LABOR4_HRS |  | sum |  |  |
| `FORECAST_ORIG_LABOR_5` | double | FORECAST_ORIG_LABOR_5 |  | sum |  |  |
| `FORECAST_ORIG_LABOR5_HRS` | double | FORECAST_ORIG_LABOR5_HRS |  | sum |  |  |
| `FORECAST_ORIG_TOT_LABOR` | double | FORECAST_ORIG_TOT_LABOR |  | sum |  |  |
| `FORE_ORIG_TOT_LBR_HRS` | double | FORE_ORIG_TOT_LBR_HRS |  | sum |  |  |
| `ACTUAL_EQUIPMENT` | double | ACTUAL_EQUIPMENT |  | sum |  |  |
| `ACTUAL_LABOR` | double | ACTUAL_LABOR |  | sum |  |  |
| `ACTUAL_MATERIAL` | double | ACTUAL_MATERIAL |  | sum |  |  |
| `ACTUAL_SUBS` | double | ACTUAL_SUBS |  | sum |  |  |
| `ACTUAL_OTHER` | double | ACTUAL_OTHER |  | sum |  |  |
| `TOTAL_COST_TAX` | double | TOTAL_COST_TAX |  | sum |  |  |
| `ACTUAL_TOTAL_COST` | double | ACTUAL_TOTAL_COST |  | sum |  |  |
| `ACTUAL_HOURS` | double | ACTUAL_HOURS |  | sum |  |  |
| `ACTUAL_LABOR_1` | double | ACTUAL_LABOR_1 |  | sum |  |  |
| `ACTUAL_LABOR_1_HOURS_REPAIR` | double | ACTUAL_LABOR_1_HOURS_REPAIR |  | sum |  |  |
| `ACTUAL_LABOR_2` | double | ACTUAL_LABOR_2 |  | sum |  |  |
| `ACTUAL_LABOR_2_HOURS_PM` | double | ACTUAL_LABOR_2_HOURS_PM |  | sum |  |  |
| `ACTUAL_LABOR_3` | double | ACTUAL_LABOR_3 |  | sum |  |  |
| `ACTUAL_LABOR_3_HOURS_TRAVEL` | double | ACTUAL_LABOR_3_HOURS_TRAVEL |  | sum |  |  |
| `ACTUAL_LABOR_4` | double | ACTUAL_LABOR_4 |  | sum |  |  |
| `ACTUAL_LABOR_4_HOURS` | double | ACTUAL_LABOR_4_HOURS |  | sum |  |  |
| `ACTUAL_LABOR_5` | double | ACTUAL_LABOR_5 |  | sum |  |  |
| `ACTUAL_LABOR_5_HOURS` | double | ACTUAL_LABOR_5_HOURS |  | sum |  |  |
| `ACTUAL_TOTAL_LABOR` | double | ACTUAL_TOTAL_LABOR |  | sum |  |  |
| `ACTUAL_TOTAL_LABOR_HRS` | double | ACTUAL_TOTAL_LABOR_HRS |  | sum |  |  |
| `ACTUAL_CONTRACT_EARNED` | double | ACTUAL_CONTRACT_EARNED |  | sum |  |  |
| `ACTUAL_GROSS_PROFIT` | double | ACTUAL_GROSS_PROFIT |  | sum |  |  |
| `ACTUA_REVENUE_RECOGNIZED` | double | ACTUA_REVENUE_RECOGNIZED |  | sum |  |  |
| `ACTUAL_BILLED` | double | ACTUAL_BILLED |  | sum |  |  |
| `ESTIMATE_EQUIPMENT` | double | ESTIMATE_EQUIPMENT |  | sum |  |  |
| `ESTIMATE_LABOR` | double | ESTIMATE_LABOR |  | sum |  |  |
| `ESTIMATE_MATERIAL` | double | ESTIMATE_MATERIAL |  | sum |  |  |
| `ESTIMATE_SUBS` | double | ESTIMATE_SUBS |  | sum |  |  |
| `ESTIMATE_OTHER` | double | ESTIMATE_OTHER |  | sum |  |  |
| `ESTIMATE_TOTAL_COST` | double | ESTIMATE_TOTAL_COST |  | sum |  |  |
| `ESTIMATE_HOURS` | double | ESTIMATE_HOURS |  | sum |  |  |
| `ESTIMATE_LABOR_1` | double | ESTIMATE_LABOR_1 |  | sum |  |  |
| `ESTIMATE_LABOR_1_HOURS_REPAIR` | double | ESTIMATE_LABOR_1_HOURS_REPAIR |  | sum |  |  |
| `ESTIMATE_LABOR_2` | double | ESTIMATE_LABOR_2 |  | sum |  |  |
| `ESTIMATE_LABOR_2_HOURS_PM` | double | ESTIMATE_LABOR_2_HOURS_PM |  | sum |  |  |
| `ESTIMATE_LABOR_3` | double | ESTIMATE_LABOR_3 |  | sum |  |  |
| `ESTIMATE_LABOR_3_HOURS_TRAVEL` | double | ESTIMATE_LABOR_3_HOURS_TRAVEL |  | sum |  |  |
| `ESTIMATE_LABOR_4` | double | ESTIMATE_LABOR_4 |  | sum |  |  |
| `ESTIMATE_LABOR_4_HOURS` | double | ESTIMATE_LABOR_4_HOURS |  | sum |  |  |
| `ESTIMATE_LABOR_5` | double | ESTIMATE_LABOR_5 |  | sum |  |  |
| `ESTIMATE_LABOR_5_HOURS` | double | ESTIMATE_LABOR_5_HOURS |  | sum |  |  |
| `ESTIMATE_TOTAL_LABOR` | double | ESTIMATE_TOTAL_LABOR |  | sum |  |  |
| `ESTIMATE_TOTAL_LABOR_HRS` | double | ESTIMATE_TOTAL_LABOR_HRS |  | sum |  |  |
| `FORECAST_LABOR` | double | FORECAST_LABOR |  | sum |  |  |
| `FORECAST_EQUIPMENT` | double | FORECAST_EQUIPMENT |  | sum |  |  |
| `FORECAST_MATERIAL` | double | FORECAST_MATERIAL |  | sum |  |  |
| `FORECAST_SUBS` | double | FORECAST_SUBS |  | sum |  |  |
| `FORECAST_OTHER` | double | FORECAST_OTHER |  | sum |  |  |
| `FORECAST_TOTAL_COST` | double | FORECAST_TOTAL_COST |  | sum |  |  |
| `FORECAST_HOURS` | double | FORECAST_HOURS |  | sum |  |  |
| `FORECAST_LABOR_1` | double | FORECAST_LABOR_1 |  | sum |  |  |
| `FORECAST_LABOR_1_HOURS_REPAIR` | double | FORECAST_LABOR_1_HOURS_REPAIR |  | sum |  |  |
| `FORECAST_LABOR_2` | double | FORECAST_LABOR_2 |  | sum |  |  |
| `FORECAST_LABOR_2_HOURS_PM` | double | FORECAST_LABOR_2_HOURS_PM |  | sum |  |  |
| `FORECAST_LABOR_3` | double | FORECAST_LABOR_3 |  | sum |  |  |
| `FORECAST_LABOR_3_HOURS_TRAVEL` | double | FORECAST_LABOR_3_HOURS_TRAVEL |  | sum |  |  |
| `FORECAST_LABOR_4` | double | FORECAST_LABOR_4 |  | sum |  |  |
| `FORECAST_LABOR_4_HOURS` | double | FORECAST_LABOR_4_HOURS |  | sum |  |  |
| `FORECAST_LABOR_5` | double | FORECAST_LABOR_5 |  | sum |  |  |
| `FORECAST_LABOR_5_HOURS` | double | FORECAST_LABOR_5_HOURS |  | sum |  |  |
| `FORECAST_TOTAL_LABOR` | double | FORECAST_TOTAL_LABOR |  | sum |  |  |
| `FORECAST_TOTAL_LABOR_HRS` | double | FORECAST_TOTAL_LABOR_HRS |  | sum |  |  |
| `PY_LABOR` | double | PY_LABOR |  | sum |  |  |
| `PY_MATERIAL` | double | PY_MATERIAL |  | sum |  |  |
| `PY_EQUIPMENT` | double | PY_EQUIPMENT |  | sum |  |  |
| `PY_SUBCONTRACTOR` | double | PY_SUBCONTRACTOR |  | sum |  |  |
| `PY_OTHER` | double | PY_OTHER |  | sum |  |  |
| `PY_TOTAL_COST` | double | PY_TOTAL_COST |  | sum |  |  |
| `PY_BILLED` | double | PY_BILLED |  | sum |  |  |
| `PY_CONTRACT_EARNED` | double | PY_CONTRACT_EARNED |  | sum |  |  |
| `PY_GROSS_PROFIT` | double | PY_GROSS_PROFIT |  | sum |  |  |
| `PY_REVENUE_RECOGNIZED` | double | PY_REVENUE_RECOGNIZED |  | sum |  |  |
| `PY_HOURS` | double | PY_HOURS |  | sum |  |  |
| `PY_LABOR_1` | double | PY_LABOR_1 |  | sum |  |  |
| `PY_LABOR_1_HOURS_REPAIR` | double | PY_LABOR_1_HOURS_REPAIR |  | sum |  |  |
| `PY_LABOR_2` | double | PY_LABOR_2 |  | sum |  |  |
| `PY_LABOR_2_HOURS_PM` | double | PY_LABOR_2_HOURS_PM |  | sum |  |  |
| `PY_LABOR_3` | double | PY_LABOR_3 |  | sum |  |  |
| `PY_LABOR_3_HOURS_TRAVEL` | double | PY_LABOR_3_HOURS_TRAVEL |  | sum |  |  |
| `PY_LABOR_4` | double | PY_LABOR_4 |  | sum |  |  |
| `PY_LABOR_4_HOURS` | double | PY_LABOR_4_HOURS |  | sum |  |  |
| `PY_LABOR_5` | double | PY_LABOR_5 |  | sum |  |  |
| `PY_LABOR_5_HOURS` | double | PY_LABOR_5_HOURS |  | sum |  |  |
| `PY_TOTAL_LABOR` | double | PY_TOTAL_LABOR |  | sum |  |  |
| `PY_TOTAL_LABOR_HRS` | double | PY_TOTAL_LABOR_HRS |  | sum |  |  |
| `YTD_LABOR` | double | YTD_LABOR |  | sum |  |  |
| `YTD_MATERIAL` | double | YTD_MATERIAL |  | sum |  |  |
| `YTD_EQUIPMENT` | double | YTD_EQUIPMENT |  | sum |  |  |
| `YTD_SUBCONTRACTOR` | double | YTD_SUBCONTRACTOR |  | sum |  |  |
| `YTD_OTHER` | double | YTD_OTHER |  | sum |  |  |
| `YTD_TOTAL_COST` | double | YTD_TOTAL_COST |  | sum |  |  |
| `YTD_BILLED` | double | YTD_BILLED |  | sum |  |  |
| `YTD_CONTRACT_EARNED` | double | YTD_CONTRACT_EARNED |  | sum |  |  |
| `YTD_GROSS_PROFIT` | double | YTD_GROSS_PROFIT |  | sum |  |  |
| `YTD_REVENUE_RECOGNIZED` | double | YTD_REVENUE_RECOGNIZED |  | sum |  |  |
| `YTDHOURS` | double | YTDHOURS |  | sum |  |  |
| `YTD_LABOR_1` | double | YTD_LABOR_1 |  | sum |  |  |
| `YTD_LABOR_1_HOURS_REPAIR` | double | YTD_LABOR_1_HOURS_REPAIR |  | sum |  |  |
| `YTD_LABOR_2` | double | YTD_LABOR_2 |  | sum |  |  |
| `YTD_LABOR_2_HOURS_PM` | double | YTD_LABOR_2_HOURS_PM |  | sum |  |  |
| `YTD_LABOR_3` | double | YTD_LABOR_3 |  | sum |  |  |
| `YTD_LABOR_3_HOURS_TRAVEL` | double | YTD_LABOR_3_HOURS_TRAVEL |  | sum |  |  |
| `YTD_LABOR_4` | double | YTD_LABOR_4 |  | sum |  |  |
| `YTD_LABOR_4_HOURS` | double | YTD_LABOR_4_HOURS |  | sum |  |  |
| `YTD_LABOR_5` | double | YTD_LABOR_5 |  | sum |  |  |
| `YTD_LABOR_5_HOURS` | double | YTD_LABOR_5_HOURS |  | sum |  |  |
| `YTD_TOTAL_LABOR` | double | YTD_TOTAL_LABOR |  | sum |  |  |
| `YTD_TOTAL_LABOR_HRS` | double | YTD_TOTAL_LABOR_HRS |  | sum |  |  |
| `USER_DEFINE_1A_PERSON` | string | USER_DEFINE_1A_PERSON |  | none |  |  |
| `USER_DEFINE_2A_COMPLETED` | string | USER_DEFINE_2A_COMPLETED |  | none |  |  |
| `USER_DEFINE_3A_STATUS` | string | USER_DEFINE_3A_STATUS |  | none |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `CONTRACT_NUMBER_KEY` | string | CONTRACT_NUMBER_KEY |  | none |  |  |
| `CUSTNMBR_KEY` | string | CUSTNMBR_KEY |  | none |  |  |
| `WSCONTSQ` | double | WSCONTSQ |  | sum |  |  |

### CONTRACTS_TASK_SCHEDULE
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.SERV_CONTRACT_TASKS_F (Table)
- Partitions: `CONTRACTS_TASK_SCHEDULE` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `ADRSCODE` | string | ADRSCODE |  | none |  |  |
| `WSCONTSQ` | double | WSCONTSQ |  | sum |  |  |
| `EQUIPMENT_ID` | string | EQUIPMENT_ID |  | none |  |  |
| `SCHEDULE_DATE` | dateTime | SCHEDULE_DATE |  | none | Long Date |  |
| `ORIGINAL_SCHEDULE_DATE` | dateTime | ORIGINAL_SCHEDULE_DATE |  | none | Long Date |  |
| `SCHEDULE_MODIFIED_FLAG` | string | SCHEDULE_MODIFIED_FLAG |  | none |  |  |
| `WEEK_OF_MONTH` | string | WEEK_OF_MONTH |  | none |  |  |
| `DAY_OF_THE_WEEK` | string | DAY_OF_THE_WEEK |  | none |  |  |
| `CONTRACT_YEAR` | string | CONTRACT_YEAR |  | none |  |  |
| `SCHEDULED_TIME` | string | SCHEDULED_TIME |  | none |  |  |
| `SERVICE_CALL_ID` | string | SERVICE_CALL_ID |  | none |  |  |
| `ESTIMATE_HOURS` | double | ESTIMATE_HOURS |  | sum |  |  |
| `TASK_CODE` | string | TASK_CODE |  | none |  |  |
| `TASK_HIERARCHY` | string | TASK_HIERARCHY |  | none |  |  |
| `CONTRACT_TASK_LIST_ID` | string | CONTRACT_TASK_LIST_ID |  | none |  |  |
| `REQUIRED` | string | REQUIRED |  | none |  |  |
| `DEX_ROW_ID` | double | DEX_ROW_ID |  | count |  |  |
| `Estimated Hours_` |  |  | (calc) | sum | 0.00 |  |
| `Customer-Contract` | string | Customer-Contract |  | none |  |  |
| `In Current Contract` |  |  | (calc) | sum | 0 |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `CUSTNMBR_KEY` | string | CUSTNMBR_KEY |  | none |  |  |
| `CONTRACT_NUMBER_KEY` | string | CONTRACT_NUMBER_KEY |  | none |  |  |

### Cost Measures
- Type: Measures
- Partitions: `Cost Measures` (m, import)
- Measures: 18

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|

### Cost Types
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table)
- Partitions: `Cost Types` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `Cost Type` | string | Cost Type |  | none |  |  |

### CUSTOMERS_D
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.CUSTOMERS_D (Table)
- Partitions: `CUSTOMERS_D` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `CUSTOMER_NUMBER` | string | CUSTOMER_NUMBER |  | none |  |  |
| `CUSTOMER_NAME` | string | CUSTOMER_NAME |  | none |  |  |
| `CUSTOMER_CLASS` | string | CUSTOMER_CLASS |  | none |  |  |
| `ADDRESS1` | string | ADDRESS1 |  | none |  |  |
| `ADDRESS2` | string | ADDRESS2 |  | none |  |  |
| `COUNTRY` | string | COUNTRY |  | none |  |  |
| `CITY` | string | CITY |  | none |  |  |
| `STATE` | string | STATE |  | none |  |  |
| `ZIP` | string | ZIP |  | none |  |  |
| `PHONE1` | string | PHONE1 |  | none |  |  |
| `PAYMENT_TERM` | string | PAYMENT_TERM |  | none |  |  |
| `CREATED` | dateTime | CREATED |  | none | General Date |  |
| `UPDATED` | dateTime | UPDATED |  | none | General Date |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `CUSTOMER_KEY` | string | CUSTOMER_KEY |  | none |  |  |

### DateTableTemplate_ae1bc3b8-dd10-47c1-913a-5f4a589902e6
- Type: Date
- Partitions: `DateTableTemplate_ae1bc3b8-dd10-47c1-913a-5f4a589902e6-ca257ed7-7cd6-4f16-a2e4-af90b5b39931` (calculated, import)

(Auto-generated date table; 7 columns)

### DIVISION
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.JOBS_D (Table)
- Partitions: `DIVISION` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `DIVISION KEY` | string | DIVISION KEY |  | none |  |  |
| `Division` | string | Division |  | none |  |  |
| `Division_Final` |  |  | (calc) | none |  |  |

### FORECASTED CALLS COST
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.CONTRACTS_D (Table)
- Partitions: `FORECASTED CALLS COST` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `CONTRACT_NUMBER` | string | CONTRACT_NUMBER |  | none |  |  |
| `Customer - Contract` | string | Customer - Contract |  | none |  |  |
| `Cost Type` | string | Cost Type |  | none |  |  |
| `Value` | double | Value |  | sum |  |  |
| `CONTRACT_START_DATE` | dateTime | CONTRACT_START_DATE |  | none | Long Date |  |
| `CONTRACT_EXPIRATION_DATE` | dateTime | CONTRACT_EXPIRATION_DATE |  | none | Long Date |  |
| `In Current Contract` |  |  | (calc) | sum | 0 |  |

### GP Parameter
- Type: Parameter
- Partitions: `GP Parameter` (calculated, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `GP Parameter` |  | [Value1] |  | none |  |  |
| `GP Parameter Fields` |  | [Value2] |  | none |  |  |
| `GP Parameter Order` |  | [Value3] |  | sum | 0 |  |

### GP Parameter 2
- Type: Parameter
- Partitions: `GP Parameter 2` (calculated, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `GP Parameter` |  | [Value1] |  | none |  |  |
| `GP Parameter Fields` |  | [Value2] |  | none |  |  |
| `GP Parameter Order` |  | [Value3] |  | sum | 0 |  |

### Hour Measures
- Type: Measures
- Partitions: `Hour Measures` (m, import)
- Measures: 15

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|

### LocalDateTable_00e51d8d-231f-4d65-881b-7cd775844859
- Type: Date
- Partitions: `LocalDateTable_00e51d8d-231f-4d65-881b-7cd775844859` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_1997b5af-fbda-41ee-846d-31f24c5d8bd7
- Type: Date
- Partitions: `LocalDateTable_1997b5af-fbda-41ee-846d-31f24c5d8bd7` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_287ff984-7355-4b13-9018-95e3a16e18e9
- Type: Date
- Partitions: `LocalDateTable_287ff984-7355-4b13-9018-95e3a16e18e9` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_2a249574-7315-48a3-bf2c-4c9bbab9a923
- Type: Date
- Partitions: `LocalDateTable_2a249574-7315-48a3-bf2c-4c9bbab9a923` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_2e841b8c-c7b1-4df6-aaad-a1a446fc7c01
- Type: Date
- Partitions: `LocalDateTable_2e841b8c-c7b1-4df6-aaad-a1a446fc7c01` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f
- Type: Date
- Partitions: `LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_36fb0cc6-3a6a-46f4-99fe-6340fb69c6b3
- Type: Date
- Partitions: `LocalDateTable_36fb0cc6-3a6a-46f4-99fe-6340fb69c6b3` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_38f12a90-c3e3-476c-8af6-3b87ccdcdb64
- Type: Date
- Partitions: `LocalDateTable_38f12a90-c3e3-476c-8af6-3b87ccdcdb64` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f
- Type: Date
- Partitions: `LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_4ed2ebea-2956-4a45-b593-72e2e76dd90c
- Type: Date
- Partitions: `LocalDateTable_4ed2ebea-2956-4a45-b593-72e2e76dd90c` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356
- Type: Date
- Partitions: `LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_68db00b3-6e04-4ee2-a4a3-b33365193de7
- Type: Date
- Partitions: `LocalDateTable_68db00b3-6e04-4ee2-a4a3-b33365193de7` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_7568775e-9707-49cb-bf23-8bca38b29542
- Type: Date
- Partitions: `LocalDateTable_7568775e-9707-49cb-bf23-8bca38b29542` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_7b8a7d6f-03de-4370-ab61-70ffffb79124
- Type: Date
- Partitions: `LocalDateTable_7b8a7d6f-03de-4370-ab61-70ffffb79124` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_8931b809-08ab-4252-8179-ca3c21383cd6
- Type: Date
- Partitions: `LocalDateTable_8931b809-08ab-4252-8179-ca3c21383cd6` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_8d221eb4-201c-477f-89c5-03c6e03aa65e
- Type: Date
- Partitions: `LocalDateTable_8d221eb4-201c-477f-89c5-03c6e03aa65e` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_a823d9da-2d68-472e-bea7-b1c1f0ea5afc
- Type: Date
- Partitions: `LocalDateTable_a823d9da-2d68-472e-bea7-b1c1f0ea5afc` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_c357c417-93f4-4ea3-badf-ef0dec761ede
- Type: Date
- Partitions: `LocalDateTable_c357c417-93f4-4ea3-badf-ef0dec761ede` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98
- Type: Date
- Partitions: `LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_de817910-54ca-42f0-b798-d1ae454cca2b
- Type: Date
- Partitions: `LocalDateTable_de817910-54ca-42f0-b798-d1ae454cca2b` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_dea31c23-1eaa-490c-ab59-1e5b655fb2ca
- Type: Date
- Partitions: `LocalDateTable_dea31c23-1eaa-490c-ab59-1e5b655fb2ca` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_e59f379f-de3d-42a7-bd84-6e80ef7a5ed8
- Type: Date
- Partitions: `LocalDateTable_e59f379f-de3d-42a7-bd84-6e80ef7a5ed8` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae
- Type: Date
- Partitions: `LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae` (calculated, import)

(Auto-generated date table; 7 columns)

### POSTING_DATA_F
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.POSTING_DATA_F (Table)
- Partitions: `POSTING_DATA_F` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `ACTINDX` | string | ACTINDX |  | none |  |  |
| `ACTNUMBR_1` | string | ACTNUMBR_1 |  | none |  |  |
| `ACTNUMBR_2` | string | ACTNUMBR_2 |  | none |  |  |
| `ACTNUMBR_3` | string | ACTNUMBR_3 |  | none |  |  |
| `ACTNUMST` | string | ACTNUMST |  | none |  |  |
| `YEAR` | double | YEAR |  | sum |  |  |
| `FISCAL_MONTH` | double | FISCAL_MONTH |  | sum |  |  |
| `LEDGER_ID` | double | LEDGER_ID |  | count |  |  |
| `PERDBLNC` | double | PERDBLNC |  | sum |  |  |
| `DEBITAMT` | double | DEBITAMT |  | sum |  |  |
| `CRDTAMNT` | double | CRDTAMNT |  | sum |  |  |
| `ACCATNUM` | string | ACCATNUM |  | none |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `TRANSACTION_STATUS` | string | TRANSACTION_STATUS |  | none |  |  |
| `ACCTNUM_KEY` | string | ACCTNUM_KEY |  | none |  |  |
| `ACCTIDX_KEY` | string | ACCTIDX_KEY |  | none |  |  |
| `ACCOUNT_TYPE` | string | ACCOUNT_TYPE |  | none |  |  |
| `DIVISION` | string | DIVISION |  | none |  |  |
| `Date` |  |  | (calc) | none | Long Date |  |

### Refresh Date
- Type: Table
- Partitions: `Refresh Date` (m, import)
- Measures: 1

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `Date` | dateTime | Date |  | none | Long Date |  |
| `Time` | dateTime | Time |  | none | Long Time |  |

### Revenue Measures
- Type: Measures
- Partitions: `Revenue Measures` (m, import)
- Measures: 42

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|

### SERV_TASKS_F
- Type: Table
- Source: DATA_WAREHOUSE.DW_FINAL.TASKS_F (Table)
- Partitions: `SERV_TASKS_F` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `CUSTNMBR` | string | CUSTNMBR |  | none |  |  |
| `CONTRACT_NUMBER` | string | CONTRACT_NUMBER |  | none |  |  |
| `TECHNICIAN_ID` | string | TECHNICIAN_ID |  | none |  |  |
| `WSCONTSQ` | double | WSCONTSQ |  | sum |  |  |
| `EQUIPMENT_ID` | string | EQUIPMENT_ID |  | none |  |  |
| `EQUIPMENT_TYPE` | string | EQUIPMENT_TYPE |  | none |  |  |
| `TASK_CODE` | string | TASK_CODE |  | none |  |  |
| `TASK_HIERARCHY` | string | TASK_HIERARCHY |  | none |  |  |
| `TASK_DESCRIPTION` | string | TASK_DESCRIPTION |  | none |  |  |
| `INACTIVE` | double | INACTIVE |  | sum |  |  |
| `ESTIMATE_HOURS` | double | ESTIMATE_HOURS |  | sum |  |  |
| `ESTIMATE_LABOR` | double | ESTIMATE_LABOR |  | sum |  |  |
| `ESTIMATE_LABOR_1` | double | ESTIMATE_LABOR_1 |  | sum |  |  |
| `ESTIMATE_LABOR_1_HOURS` | double | ESTIMATE_LABOR_1_HOURS |  | sum |  |  |
| `ESTIMATE_LABOR_2` | double | ESTIMATE_LABOR_2 |  | sum |  |  |
| `ESTIMATE_LABOR_2_HOURS` | double | ESTIMATE_LABOR_2_HOURS |  | sum |  |  |
| `BILLABLE_LABOR_1` | double | BILLABLE_LABOR_1 |  | sum |  |  |
| `BILLABLE_LABOR_2` | double | BILLABLE_LABOR_2 |  | sum |  |  |
| `FREQUENCY` | string | FREQUENCY |  | none |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `CUSTNMBR_KEY` | string | CUSTNMBR_KEY |  | none |  |  |
| `CONTRACT_NUMBER_KEY` | string | CONTRACT_NUMBER_KEY |  | none |  |  |

## Shared Queries (not loaded as model tables)
These appear in `definition/expressions.tmdl` but are not present as `table` definitions in the model.

| Expression | Source |
|---|---|
| `EMPLOYEES_D` | DATA_WAREHOUSE.DW_FINAL.EMPLOYEES_D (Table) |
| `JOB PROFILE _ PROJECTION TRENDS` | DATA_WAREHOUSE_DEV.PUBLIC.JOB_PROFILE (View) |
| `PO_JOB _DETAILS_F` | DATA_WAREHOUSE.DW_FINAL.PO_JOB_DETAILS_F (Table) |
