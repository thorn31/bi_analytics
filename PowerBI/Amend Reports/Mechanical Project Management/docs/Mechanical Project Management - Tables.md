# Mechanical Project Management — Tables + Columns

Generated: 2026-01-22 14:42 EST

## Table Summary
| Table | Type | Source | Columns | Measures | Partitions |
|---|---:|---|---:|---:|---:|
| `Backlog Measures` | Measures |  | 0 | 31 | 1 |
| `Backlog Parameter` | Parameter |  | 3 | 0 | 1 |
| `Backlog Parameter 2` | Parameter |  | 3 | 0 | 1 |
| `BUDGET` | Fact | DATA_WAREHOUSE.DW_FINAL.BUDGET_F (Table) | 17 | 3 | 1 |
| `Calendar` | Date |  | 28 | 1 | 1 |
| `CHANGE_ORDERS_BY_MONTH` | Fact | DATA_WAREHOUSE.DW_CLEAN.JOB_CHANGE_ORDERS (View) | 9 | 0 | 1 |
| `Cost Measures` | Measures |  | 0 | 18 | 1 |
| `COST_CODE_MAPPING` | Dim | DATA_WAREHOUSE.DW_FINAL.JOB_COST_DESCRIPTION_D (Table) | 10 | 0 | 1 |
| `CUSTOMERS` | Dim | DATA_WAREHOUSE.DW_FINAL.CUSTOMERS_D (Table) | 15 | 0 | 1 |
| `DateTableTemplate_ae1bc3b8-dd10-47c1-913a-5f4a589902e6` | Date |  | 7 | 0 | 1 |
| `DIVISION` | Dim |  | 1 | 0 | 1 |
| `GL POSTING` | Fact | DATA_WAREHOUSE.DW_FINAL.POSTING_DATA_F (Table) | 19 | 0 | 1 |
| `GP Parameter` | Parameter |  | 3 | 0 | 1 |
| `INVOICES` | Fact | DATA_WAREHOUSE.DW_FINAL.INVOICES_F (Table) | 41 | 0 | 1 |
| `JOB` | Dim | DATA_WAREHOUSE.DW_FINAL.JOBS_D (Table) | 80 | 5 | 1 |
| `JOB FORECAST` | Fact | DATA_WAREHOUSE.DW_FINAL.JOB_COST_FORECASTS_F (Table) | 16 | 0 | 1 |
| `JOB_COST_DETAILS` | Fact | DATA_WAREHOUSE.DW_CLEAN.JOB_COST_DETAILS (View) | 13 | 0 | 1 |
| `JOB_COST_SUMMARY` | Fact | DATA_WAREHOUSE.DW_FINAL.JOB_COST_SUMMARY_F (Table) | 22 | 0 | 1 |
| `JOB_LABOR_HOURS` | Fact | DATA_WAREHOUSE.DW_FINAL.JOB_LABOR_HOURS_F (Table) | 22 | 0 | 1 |
| `LocalDateTable_103d4237-3f13-4fb8-908e-8f990ad5f6f8` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_26e0a611-4938-40bf-8444-deab64adf683` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_288a7e21-8bfa-49ce-90b0-3f281030da3e` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_3068354c-1934-4176-9b53-101d178cc7da` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_39148a68-5226-4488-8b67-dc23f90c2fda` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_4d5c68a9-1016-4c7f-8bd6-94b091483340` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_69547476-3a6b-4a5f-8fcf-f5f0ffbaa28e` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_7c0dba22-51a6-475f-9385-01ea578d2301` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_820e8c9a-6a47-49de-b350-058a53302479` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_82986f2d-45c5-4243-bb17-c0844f70692b` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_8f32177c-7b7f-4b5c-afda-6d8a43f3b74a` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_a1304e08-f471-47dc-bbfc-f6653e634bfb` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_d9746aa8-c787-46e8-a0b0-2e5477439e51` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_dbc8e48e-68af-4633-963c-bd15e3755808` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_dc9a7e8b-973c-4d72-ad27-3eff05a132d9` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_df4ab1e5-1799-472a-b536-48d903e2a6f1` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_e2d949a2-51a9-4559-aff7-c4bc089c82a9` | Date |  | 7 | 0 | 1 |
| `LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae` | Date |  | 7 | 0 | 1 |
| `Refresh Date` | Dim |  | 2 | 1 | 1 |
| `Revenue Measures` | Measures |  | 0 | 42 | 1 |

## Table Details

### Backlog Measures
- Type: Measures
- Partitions: `Backlog Measures` (m, import)
- Measures: 31

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|

### Backlog Parameter
- Type: Parameter
- Partitions: `Backlog Parameter` (calculated, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `Parameter` |  | [Value1] |  | none |  |  |
| `Parameter Fields` |  | [Value2] |  | none |  |  |
| `Parameter Order` |  | [Value3] |  | sum | 0 |  |

### Backlog Parameter 2
- Type: Parameter
- Partitions: `Backlog Parameter 2` (calculated, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `Backlog Parameter 2` |  | [Value1] |  | none |  |  |
| `Backlog Parameter 2 Fields` |  | [Value2] |  | none |  |  |
| `Backlog Parameter 2 Order` |  | [Value3] |  | sum | 0 |  |

### BUDGET
- Type: Fact
- Source: DATA_WAREHOUSE.DW_FINAL.BUDGET_F (Table)
- Partitions: `BUDGET` (m, import)
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

### CHANGE_ORDERS_BY_MONTH
- Type: Fact
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

### Cost Measures
- Type: Measures
- Partitions: `Cost Measures` (m, import)
- Measures: 18

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|

### COST_CODE_MAPPING
- Type: Dim
- Source: DATA_WAREHOUSE.DW_FINAL.JOB_COST_DESCRIPTION_D (Table)
- Partitions: `COST_CODE_MAPPING` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `COST_CODE` | string | COST_CODE |  | none |  |  |
| `JOB_NUMBER` | string | JOB_NUMBER |  | none |  |  |
| `Cost Code Element` | string | Cost Code Element |  | none |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `JOB_KEY` | string | JOB_KEY |  | none |  |  |
| `JOB_COST_KEY` | string | JOB_COST_KEY |  | none |  |  |
| `Job_Cost Code` | string | Job_Cost Code |  | none |  |  |
| `RN` | double | RN |  | sum |  |  |
| `Cost Code Description` | string | Cost Code Description |  | none |  |  |
| `Contingency Flag` | string | Contingency Flag |  | none |  |  |

### CUSTOMERS
- Type: Dim
- Source: DATA_WAREHOUSE.DW_FINAL.CUSTOMERS_D (Table)
- Partitions: `CUSTOMERS` (m, import)

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
- Type: Dim
- Partitions: `DIVISION` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `DIVISIONS` | string | DIVISIONS |  | none |  |  |

### GL POSTING
- Type: Fact
- Source: DATA_WAREHOUSE.DW_FINAL.POSTING_DATA_F (Table)
- Partitions: `GL POSTING` (m, import)

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

### GP Parameter
- Type: Parameter
- Partitions: `GP Parameter` (calculated, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `GP Parameter` |  | [Value1] |  | none |  |  |
| `GP Parameter Fields` |  | [Value2] |  | none |  |  |
| `GP Parameter Order` |  | [Value3] |  | sum | 0 |  |

### INVOICES
- Type: Fact
- Source: DATA_WAREHOUSE.DW_FINAL.INVOICES_F (Table)
- Partitions: `INVOICES` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `JOB_NUMBER` | string | JOB_NUMBER |  | none |  |  |
| `PROJECT_NUMBER` | string | PROJECT_NUMBER |  | none |  |  |
| `RM_DOCUMENT_NUMBER_WORK` | string | RM_DOCUMENT_NUMBER_WORK |  | none |  |  |
| `RM_DOCUMENT_TYPE_ALL` | double | RM_DOCUMENT_TYPE_ALL |  | sum |  |  |
| `APPLICATION_NUMBER` | string | APPLICATION_NUMBER |  | none |  |  |
| `DOCUMENT_NUMBER` | string | DOCUMENT_NUMBER |  | none |  |  |
| `TRX_SOURCE` | string | TRX_SOURCE |  | none |  |  |
| `DYNAMICS_STATUS` | string | DYNAMICS_STATUS |  | none |  |  |
| `DOCUMENT_TYPE` | double | DOCUMENT_TYPE |  | sum |  |  |
| `BATCH_NUMBER` | string | BATCH_NUMBER |  | none |  |  |
| `BATCH_SOURCE` | string | BATCH_SOURCE |  | none |  |  |
| `ACCOUNT_AMOUNT` | double | ACCOUNT_AMOUNT |  | sum |  |  |
| `PAYMENT_TERMS_ID` | string | PAYMENT_TERMS_ID |  | none |  |  |
| `TAX_SCHEDULE_ID` | string | TAX_SCHEDULE_ID |  | none |  |  |
| `CASH_AMOUNT` | double | CASH_AMOUNT |  | sum |  |  |
| `DOCUMENT_DATE` | dateTime | DOCUMENT_DATE |  | none | Long Date |  |
| `POST_DATE` | dateTime | POST_DATE |  | none | Long Date |  |
| `POST_USER_ID` | string | POST_USER_ID |  | none |  |  |
| `GL_POSTING_DATE` | dateTime | GL_POSTING_DATE |  | none | General Date |  |
| `CUSTOMER_NUMBER` | string | CUSTOMER_NUMBER |  | none |  |  |
| `ADDRESS_CODE` | string | ADDRESS_CODE |  | none |  |  |
| `SALESPERSON_ID` | string | SALESPERSON_ID |  | none |  |  |
| `COMMISSION_PERCENT` | double | COMMISSION_PERCENT |  | sum |  |  |
| `COMMISSION_EARNINGS` | double | COMMISSION_EARNINGS |  | sum |  |  |
| `SALES_TERRITORY` | string | SALES_TERRITORY |  | none |  |  |
| `CUSTOMER_PO_NUMBER` | string | CUSTOMER_PO_NUMBER |  | none |  |  |
| `TRADE_DISCOUNT_AMOUNT` | double | TRADE_DISCOUNT_AMOUNT |  | sum |  |  |
| `DISCOUNT_DATE` | dateTime | DISCOUNT_DATE |  | none | Long Date |  |
| `DUE_DATE` | dateTime | DUE_DATE |  | none | Long Date |  |
| `DATE_PAID` | dateTime | DATE_PAID |  | none | Long Date |  |
| `AMOUNT_RECEIVED` | double | AMOUNT_RECEIVED |  | sum |  |  |
| `FREIGHT_TAX_AMOUNT` | double | FREIGHT_TAX_AMOUNT |  | sum |  |  |
| `MISC_TAX_AMOUNT` | double | MISC_TAX_AMOUNT |  | sum |  |  |
| `TAX_AMOUNT` | double | TAX_AMOUNT |  | sum |  |  |
| `TAX_DETAIL_ID` | string | TAX_DETAIL_ID |  | none |  |  |
| `SUBTOTAL` | double | SUBTOTAL |  | sum |  |  |
| `DOCUMENT_AMOUNT` | double | DOCUMENT_AMOUNT |  | sum |  |  |
| `COMMENT_ID` | string | COMMENT_ID |  | none |  |  |
| `CURRENCY_ID` | string | CURRENCY_ID |  | none |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `JOB_KEY` | string | JOB_KEY |  | none |  |  |

### JOB
- Type: Dim
- Source: DATA_WAREHOUSE.DW_FINAL.JOBS_D (Table)
- Partitions: `JOB` (m, import)
- Measures: 5

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `JOB_NUMBER` | string | JOB_NUMBER |  | none |  |  |
| `PROJECT_NUMBER` | string | PROJECT_NUMBER |  | none |  |  |
| `JOB_NAME` | string | JOB_NAME |  | none |  |  |
| `DIVISIONS` | string | DIVISIONS |  | none |  |  |
| `CUSTOMER_NUMBER` | string | CUSTOMER_NUMBER |  | none |  |  |
| `START_DATE` | dateTime | START_DATE |  | none | Short Date |  |
| `TARGET_COMPLETION_DATE` | dateTime | TARGET_COMPLETION_DATE |  | none | Short Date |  |
| `ACT_COMPLETION_DATE` | dateTime | ACT_COMPLETION_DATE |  | none | Long Date |  |
| `EST_LABOR_COST` | double | EST_LABOR_COST |  | sum |  |  |
| `EST_MATERIAL_COST` | double | EST_MATERIAL_COST |  | sum |  |  |
| `EST_EQUIPMENT_COST` | double | EST_EQUIPMENT_COST |  | sum |  |  |
| `EST_SUBS_COST` | double | EST_SUBS_COST |  | sum |  |  |
| `EST_MISC_OTHER_COST` | double | EST_MISC_OTHER_COST |  | sum |  |  |
| `EST_COST_USERDEF1` | double | EST_COST_USERDEF1 |  | sum |  |  |
| `EST_COST_USERDEF2` | double | EST_COST_USERDEF2 |  | sum |  |  |
| `EST_COST_USERDEF3` | double | EST_COST_USERDEF3 |  | sum |  |  |
| `EST_COST_USERDEF4` | double | EST_COST_USERDEF4 |  | sum |  |  |
| `TOTAL_ESTIMATED_COST` | double | TOTAL_ESTIMATED_COST |  | sum |  |  |
| `EST_LABOR_COST_MKUP` | double | EST_LABOR_COST_MKUP |  | sum |  |  |
| `EST_EQUIP_COST_MKUP` | double | EST_EQUIP_COST_MKUP |  | sum |  |  |
| `EST_MATERIALS_COST_MKUP` | double | EST_MATERIALS_COST_MKUP |  | sum |  |  |
| `EST_SUBS_COST_MARKUP` | double | EST_SUBS_COST_MARKUP |  | sum |  |  |
| `EST_MISC_OTHER_CST_MKUP` | double | EST_MISC_OTHER_CST_MKUP |  | sum |  |  |
| `EST_USERDEF1_COST_MKUP` | double | EST_USERDEF1_COST_MKUP |  | sum |  |  |
| `EST_USERDEF2_COST_MKUP` | double | EST_USERDEF2_COST_MKUP |  | sum |  |  |
| `EST_USERDEF3_COST_MKUP` | double | EST_USERDEF3_COST_MKUP |  | sum |  |  |
| `EST_USERDEF4_COST_MKUP` | double | EST_USERDEF4_COST_MKUP |  | sum |  |  |
| `TOTAL_EST_PLUS_MARKUP` | double | TOTAL_EST_PLUS_MARKUP |  | sum |  |  |
| `CONTRACT_TYPE` | double | CONTRACT_TYPE |  | sum |  |  |
| `WS_BILLING_TYPE` | double | WS_BILLING_TYPE |  | sum |  |  |
| `ORIG_CONTRACT_AMOUNT` | double | ORIG_CONTRACT_AMOUNT |  | sum | \$#,0.###############;(\$#,0.###############);\$#,0.############### |  |
| `ORIGINATING_CONTRACT_AMT` | double | ORIGINATING_CONTRACT_AMT |  | sum |  |  |
| `CONTRACT_MAX_BILL_AMT` | double | CONTRACT_MAX_BILL_AMT |  | sum |  |  |
| `CONFIRMED_CHG_ORDER_AMT` | double | CONFIRMED_CHG_ORDER_AMT |  | sum | \$#,0.###############;(\$#,0.###############);\$#,0.############### |  |
| `IN_PROCESS_CHG_ORD_AMT` | double | IN_PROCESS_CHG_ORD_AMT |  | sum |  |  |
| `FORECAST_EQUIPMENT_TTD` | double | FORECAST_EQUIPMENT_TTD |  | sum |  |  |
| `FORECASTED_LABOR_TTD` | double | FORECASTED_LABOR_TTD |  | sum |  |  |
| `FORECAST_MATERIALS_TTD` | double | FORECAST_MATERIALS_TTD |  | sum |  |  |
| `FORECAST_MISC_OTHER_TTD` | double | FORECAST_MISC_OTHER_TTD |  | sum |  |  |
| `FORECASTED_SUBS_TTD` | double | FORECASTED_SUBS_TTD |  | sum |  |  |
| `FORECAST_USERDEF1` | double | FORECAST_USERDEF1 |  | sum |  |  |
| `FORECAST_USERDEF2` | double | FORECAST_USERDEF2 |  | sum |  |  |
| `FORECAST_USERDEF3` | double | FORECAST_USERDEF3 |  | sum |  |  |
| `FORECAST_USERDEF4` | double | FORECAST_USERDEF4 |  | sum |  |  |
| `TOTAL_FORECASTED_COST` | double | TOTAL_FORECASTED_COST |  | sum |  |  |
| `REVSD_EQUIP_FORECASTED` | double | REVSD_EQUIP_FORECASTED |  | sum |  |  |
| `REVSD_LABOR_FORECASTED` | double | REVSD_LABOR_FORECASTED |  | sum |  |  |
| `REVSD_MATERIALS_FORECST` | double | REVSD_MATERIALS_FORECST |  | sum |  |  |
| `REVSD_SUBS_FORECAST_CST` | double | REVSD_SUBS_FORECAST_CST |  | sum |  |  |
| `REVSD_OTHER_FORECST_CST` | double | REVSD_OTHER_FORECST_CST |  | sum |  |  |
| `REVSD_FORECAST_USERDEF1` | double | REVSD_FORECAST_USERDEF1 |  | sum |  |  |
| `REVSD_FORECAST_USERDEF2` | double | REVSD_FORECAST_USERDEF2 |  | sum |  |  |
| `REVSD_FORECAST_USERDEF3` | double | REVSD_FORECAST_USERDEF3 |  | sum |  |  |
| `REVSD_FORECAST_USERDEF4` | double | REVSD_FORECAST_USERDEF4 |  | sum |  |  |
| `TOT_REVSD_FORECAST_COST` | double | TOT_REVSD_FORECAST_COST |  | sum |  |  |
| `EST_LABOR_UNITS_TTD` | double | EST_LABOR_UNITS_TTD |  | sum |  |  |
| `ACT_LABOR_UNITS_TTD` | double | ACT_LABOR_UNITS_TTD |  | sum |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `Job Status` |  |  | (calc) | none |  |  |
| `ESTIMATOR_ID` | string | ESTIMATOR_ID |  | none |  |  |
| `MANAGER_ID` | string | MANAGER_ID |  | none |  |  |
| `WARRANTY_START` | dateTime | WARRANTY_START |  | none | Short Date |  |
| `WARRANTY_END` | dateTime | WARRANTY_END |  | none | Short Date |  |
| `Max Transaction Date` |  |  | (calc) | none | Short Date |  |
| `JOB_KEY` | string | JOB_KEY |  | none |  |  |
| `CUSTOMER_KEY` | string | CUSTOMER_KEY |  | none |  |  |
| `Job Number - Name` |  |  | (calc) | none |  |  |
| `INACTIVE` | boolean | INACTIVE |  | none | """TRUE"";""TRUE"";""FALSE""" |  |
| `Status Check` |  |  | (calc) | none |  |  |
| `ESTIMATOR_KEY` | string | ESTIMATOR_KEY |  | none |  |  |
| `MANAGER_KEY` | string | MANAGER_KEY |  | none |  |  |
| `Project Manager` | string | Project Manager |  | none |  |  |
| `Sales Rep` | string | Sales Rep |  | none |  |  |
| `SUPERINTENDENT ID` | string | SUPERINTENDENT ID |  | none |  |  |
| `SUPERINT_KEY` | string | SUPERINT_KEY |  | none |  |  |
| `Superintendent` | string | Superintendent |  | none |  |  |
| `JOB_TYPE_FLAG` | string | JOB_TYPE_FLAG |  | none |  |  |
| `CLEANED_DIVISIONS` | string | CLEANED_DIVISIONS |  | none |  |  |
| `Min Transaction Date` |  |  | (calc) | none | General Date |  |
| `Start Date_Revised` |  |  | (calc) | none | Short Date |  |

### JOB FORECAST
- Type: Fact
- Source: DATA_WAREHOUSE.DW_FINAL.JOB_COST_FORECASTS_F (Table)
- Partitions: `JOB FORECAST` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `COST_CODE` | string | COST_CODE |  | none |  |  |
| `Date` |  |  | (calc) | none | Long Date |  |
| `Job_Cost Code` | string | Job_Cost Code |  | none |  |  |
| `JOB_NUMBER` | string | JOB_NUMBER |  | none |  |  |
| `COST_CODE_1` | string | COST_CODE_1 |  | none |  |  |
| `COST_CODE_2` | string | COST_CODE_2 |  | none |  |  |
| `COST_CODE_3` | string | COST_CODE_3 |  | none |  |  |
| `MODIFIED_DATE` | dateTime | MODIFIED_DATE |  | none | Long Date |  |
| `CURRENT_COST_AMT` | double | CURRENT_COST_AMT |  | sum |  |  |
| `FORECAST_COSTS` | double | FORECAST_COSTS |  | sum |  |  |
| `FORECAST_UNTIS` | double | FORECAST_UNTIS |  | sum |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `YEAR` | double | YEAR |  | sum |  |  |
| `FISCAL_MONTH` | double | FISCAL_MONTH |  | sum |  |  |
| `JOB_KEY` | string | JOB_KEY |  | none |  |  |
| `JOB_COST_KEY` | string | JOB_COST_KEY |  | none |  |  |

### JOB_COST_DETAILS
- Type: Fact
- Source: DATA_WAREHOUSE.DW_CLEAN.JOB_COST_DETAILS (View)
- Partitions: `JOB_COST_DETAILS` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `JOB_NUMBER` | string | JOB_NUMBER |  | none |  |  |
| `COST_CODE` | string | COST_CODE |  | none |  |  |
| `COST_DESCRIPTION` | string | COST_DESCRIPTION |  | none |  |  |
| `TRAN_DATE` | dateTime | TRAN_DATE |  | none | Long Date |  |
| `COST_AMT` | double | COST_AMT |  | sum |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `COST_CODE_1` | string | COST_CODE_1 |  | none |  |  |
| `COST_CODE_2` | string | COST_CODE_2 |  | none |  |  |
| `COST_CODE_3` | string | COST_CODE_3 |  | none |  |  |
| `Job_Cost Code` | string | Job_Cost Code |  | none |  |  |
| `JOB_KEY` | string | JOB_KEY |  | none |  |  |
| `JOB_COST_KEY` | string | JOB_COST_KEY |  | none |  |  |
| `COST_ELEMENT_DESC` | string | COST_ELEMENT_DESC |  | none |  |  |

### JOB_COST_SUMMARY
- Type: Fact
- Source: DATA_WAREHOUSE.DW_FINAL.JOB_COST_SUMMARY_F (Table)
- Partitions: `JOB_COST_SUMMARY` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `JOB_NUMBER` | string | JOB_NUMBER |  | none |  |  |
| `COST_CODE_DESCRIPTION` | string | COST_CODE_DESCRIPTION |  | none |  |  |
| `COST_ELEMENT` | double | COST_ELEMENT |  | sum |  |  |
| `INACTIVE` | boolean | INACTIVE |  | none | """TRUE"";""TRUE"";""FALSE""" |  |
| `COSTS_TO_DATE` | double | COSTS_TO_DATE |  | sum |  |  |
| `COSTS_UNITS_TO_DATE` | double | COSTS_UNITS_TO_DATE |  | sum |  |  |
| `ESTIMTED_COST` | double | ESTIMTED_COST |  | sum |  |  |
| `CHANGE_ORDER_EST_COST` | double | CHANGE_ORDER_EST_COST |  | sum |  |  |
| `REVISED_ESTIMATED_COST` | double | REVISED_ESTIMATED_COST |  | sum |  |  |
| `FORECAST_COST` | double | FORECAST_COST |  | sum |  |  |
| `REVISED_FORECAST_COST` | double | REVISED_FORECAST_COST |  | sum |  |  |
| `FORECASTED_UNITS` | double | FORECASTED_UNITS |  | sum |  |  |
| `COMMITTED_COST` | double | COMMITTED_COST |  | sum |  |  |
| `COMMITTED_UNITS` | double | COMMITTED_UNITS |  | sum |  |  |
| `COST_CODE_EST_UNIT` | double | COST_CODE_EST_UNIT |  | sum |  |  |
| `ESTIMATED_AMT_UNITS` | double | ESTIMATED_AMT_UNITS |  | sum |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `JOB_KEY` | string | JOB_KEY |  | none |  |  |
| `JOB_COST_KEY` | string | JOB_COST_KEY |  | none |  |  |
| `AVAILABLE_BUDGET` | double | AVAILABLE_BUDGET |  | sum |  |  |
| `HOURS_REMAING` | double | HOURS_REMAING |  | sum |  |  |
| `Job Cost Code` | string | Job Cost Code |  | none |  |  |

### JOB_LABOR_HOURS
- Type: Fact
- Source: DATA_WAREHOUSE.DW_FINAL.JOB_LABOR_HOURS_F (Table)
- Partitions: `JOB_LABOR_HOURS` (m, import)

| Column | Data type | Source | Expression | Summarize | Format | Hidden |
|---|---|---|---|---|---|---|
| `JOB_NUMBER` | string | JOB_NUMBER |  | none |  |  |
| `COST_CODE` | string | COST_CODE |  | none |  |  |
| `ENTRYDATE` | dateTime | ENTRYDATE |  | none | Long Date |  |
| `EMPLOYID` | string | EMPLOYID |  | none |  |  |
| `UPRTRXCD` | string | UPRTRXCD |  | none |  |  |
| `FIRST_DAY` | dateTime | FIRST_DAY |  | none | Long Date |  |
| `LAST_DAY` | dateTime | LAST_DAY |  | none | Long Date |  |
| `MONDAY` | double | MONDAY |  | sum |  |  |
| `TUESDAY` | double | TUESDAY |  | sum |  |  |
| `WEDNESDAY` | double | WEDNESDAY |  | sum |  |  |
| `THURSDAY` | double | THURSDAY |  | sum |  |  |
| `FRIDAY` | double | FRIDAY |  | sum |  |  |
| `Job_Cost Code` | string | Job_Cost Code |  | none |  |  |
| `SOURCE` | string | SOURCE |  | none |  |  |
| `JOB_KEY` | string | JOB_KEY |  | none |  |  |
| `JOB_COST_KEY` | string | JOB_COST_KEY |  | none |  |  |
| `HOURS` | double | HOURS |  | sum |  |  |
| `MANUAL_ADJUSMENTS` | double | MANUAL_ADJUSMENTS |  | sum |  |  |
| `SATURDAY` | double | SATURDAY |  | sum |  |  |
| `SUNDAY` | double | SUNDAY |  | sum |  |  |
| `TOTAL_HOURS` | double | TOTAL_HOURS |  | sum |  |  |
| `Cost Element` |  |  | (calc) | none |  |  |

### LocalDateTable_103d4237-3f13-4fb8-908e-8f990ad5f6f8
- Type: Date
- Partitions: `LocalDateTable_103d4237-3f13-4fb8-908e-8f990ad5f6f8` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_26e0a611-4938-40bf-8444-deab64adf683
- Type: Date
- Partitions: `LocalDateTable_26e0a611-4938-40bf-8444-deab64adf683` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_288a7e21-8bfa-49ce-90b0-3f281030da3e
- Type: Date
- Partitions: `LocalDateTable_288a7e21-8bfa-49ce-90b0-3f281030da3e` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f
- Type: Date
- Partitions: `LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_3068354c-1934-4176-9b53-101d178cc7da
- Type: Date
- Partitions: `LocalDateTable_3068354c-1934-4176-9b53-101d178cc7da` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_39148a68-5226-4488-8b67-dc23f90c2fda
- Type: Date
- Partitions: `LocalDateTable_39148a68-5226-4488-8b67-dc23f90c2fda` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f
- Type: Date
- Partitions: `LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_4d5c68a9-1016-4c7f-8bd6-94b091483340
- Type: Date
- Partitions: `LocalDateTable_4d5c68a9-1016-4c7f-8bd6-94b091483340` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356
- Type: Date
- Partitions: `LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_69547476-3a6b-4a5f-8fcf-f5f0ffbaa28e
- Type: Date
- Partitions: `LocalDateTable_69547476-3a6b-4a5f-8fcf-f5f0ffbaa28e` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_7c0dba22-51a6-475f-9385-01ea578d2301
- Type: Date
- Partitions: `LocalDateTable_7c0dba22-51a6-475f-9385-01ea578d2301` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_820e8c9a-6a47-49de-b350-058a53302479
- Type: Date
- Partitions: `LocalDateTable_820e8c9a-6a47-49de-b350-058a53302479` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_82986f2d-45c5-4243-bb17-c0844f70692b
- Type: Date
- Partitions: `LocalDateTable_82986f2d-45c5-4243-bb17-c0844f70692b` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_8f32177c-7b7f-4b5c-afda-6d8a43f3b74a
- Type: Date
- Partitions: `LocalDateTable_8f32177c-7b7f-4b5c-afda-6d8a43f3b74a` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_a1304e08-f471-47dc-bbfc-f6653e634bfb
- Type: Date
- Partitions: `LocalDateTable_a1304e08-f471-47dc-bbfc-f6653e634bfb` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98
- Type: Date
- Partitions: `LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_d9746aa8-c787-46e8-a0b0-2e5477439e51
- Type: Date
- Partitions: `LocalDateTable_d9746aa8-c787-46e8-a0b0-2e5477439e51` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_dbc8e48e-68af-4633-963c-bd15e3755808
- Type: Date
- Partitions: `LocalDateTable_dbc8e48e-68af-4633-963c-bd15e3755808` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_dc9a7e8b-973c-4d72-ad27-3eff05a132d9
- Type: Date
- Partitions: `LocalDateTable_dc9a7e8b-973c-4d72-ad27-3eff05a132d9` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_df4ab1e5-1799-472a-b536-48d903e2a6f1
- Type: Date
- Partitions: `LocalDateTable_df4ab1e5-1799-472a-b536-48d903e2a6f1` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_e2d949a2-51a9-4559-aff7-c4bc089c82a9
- Type: Date
- Partitions: `LocalDateTable_e2d949a2-51a9-4559-aff7-c4bc089c82a9` (calculated, import)

(Auto-generated date table; 7 columns)

### LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae
- Type: Date
- Partitions: `LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae` (calculated, import)

(Auto-generated date table; 7 columns)

### Refresh Date
- Type: Dim
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

## Shared Queries (not loaded as model tables)
These appear in `definition/expressions.tmdl` but are not present as `table` definitions in the model.

| Expression | Source |
|---|---|
| `EMPLOYEES` | DATA_WAREHOUSE.DW_FINAL.EMPLOYEES_D (Table) |
| `JOB PROFILE _ PROJECTION TRENDS` | DATA_WAREHOUSE_DEV.PUBLIC.JOB_PROFILE (View) |
| `PO JOB DETAILS` | DATA_WAREHOUSE.DW_FINAL.PO_JOB_DETAILS_F (Table) |
| `Tables` | DATA_WAREHOUSE.DW_FINAL.JOB_LABOR_HOURS_F (Table) |
