# Mechanical Project Management — Partitions + Source Queries

Generated: 2026-01-22 14:36 EST

## Table Partitions

### Backlog Measures

#### Partition: Backlog Measures
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Column1 = _t]),

	    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Column1", type text}}),

	    #"Removed Columns" = Table.RemoveColumns(#"Changed Type",{"Column1"})

	in

	    #"Removed Columns"



annotation PBI_ResultType = Table
```

### Backlog Parameter

#### Partition: Backlog Parameter
- Kind: calculated
- Mode: import

```powerquery
	{

	    ("Backlog Months", NAMEOF('Backlog Measures'[Backlog Months]), 0),

	    ("Cost to Complete", NAMEOF('Backlog Measures'[Cost to Complete - Backlog]), 1),

	    ("Revenue", NAMEOF('Backlog Measures'[GL Revenue]), 1),

	    ("GP $", NAMEOF('Backlog Measures'[Actual GP]), 1)

	}



annotation PBI_Id = a2739a5c682248849d7c3ec9bca8f95d
```

### Backlog Parameter 2

#### Partition: Backlog Parameter 2
- Kind: calculated
- Mode: import

```powerquery
	{

	    ("Backlog Revenue $", NAMEOF('Backlog Measures'[Backlog_Remaining Monthly Revenue]), 0),

	    ("Backlog GP $", NAMEOF('Backlog Measures'[Monthly GP Backlog]), 1)

	}



annotation PBI_Id = 98df2085dbfc4d56a7f90f3a92f75ef4
```

### BUDGET

#### Partition: BUDGET
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    BUDGET_F_Table = DW_FINAL_Schema{[Name="BUDGET_F",Kind="Table"]}[Data],

	    #"Changed Type" = Table.TransformColumnTypes(BUDGET_F_Table,{{"PERIODDT", type date}}),

	    #"Filtered Rows" = Table.SelectRows(#"Changed Type", each ([SOURCE] = "MECH_GP"))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### Calendar

#### Partition: Calendar-d7293210-4553-47c2-8825-e570d51daaae
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### CHANGE_ORDERS_BY_MONTH

#### Partition: CHANGE_ORDERS_BY_MONTH
- Kind: m
- Mode: import

```powerquery
	let

	     Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_CLEAN_Schema = DATA_WAREHOUSE_Database{[Name="DW_CLEAN",Kind="Schema"]}[Data],

	    JOB_CHANGE_ORDERS_View = DW_CLEAN_Schema{[Name="JOB_CHANGE_ORDERS",Kind="View"]}[Data],

	    #"Removed Duplicates" = Table.Distinct(JOB_CHANGE_ORDERS_View),

	    #"Filtered Rows" = Table.SelectRows(#"Removed Duplicates", each ([SOURCE] = "MECH_GP"))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### Cost Measures

#### Partition: Cost Measures
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Column1 = _t]),

	    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Column1", type text}}),

	    #"Removed Columns" = Table.RemoveColumns(#"Changed Type",{"Column1"})

	in

	    #"Removed Columns"



annotation PBI_ResultType = Table
```

### COST_CODE_MAPPING

#### Partition: COST_CODE_MAPPING
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    JOB_COST_DESCRIPTION_D_Table = DW_FINAL_Schema{[Name="JOB_COST_DESCRIPTION_D",Kind="Table"]}[Data],

	    #"Renamed Columns" = Table.RenameColumns(JOB_COST_DESCRIPTION_D_Table,{{"COST_ELEMENT_DESC", "Cost Code Element"}, {"COST_DESCRIPTION", "Cost Code Description"}, {"CONTINGENCY_FLAG", "Contingency Flag"}, {"JOB_COST_CODE", "Job_Cost Code"}}),

	    #"Filtered Rows" = Table.SelectRows(#"Renamed Columns", each ([SOURCE] = "MECH_GP"))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### CUSTOMERS

#### Partition: CUSTOMERS
- Kind: m
- Mode: import

```powerquery
	let

	        Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CUSTOMERS_D_Table = DW_FINAL_Schema{[Name="CUSTOMERS_D",Kind="Table"]}[Data],

	    #"Capitalized Each Word" = Table.TransformColumns(CUSTOMERS_D_Table,{{"CUSTOMER_NAME", Text.Proper, type text}}),

	    #"Filtered Rows" = Table.SelectRows(#"Capitalized Each Word", each ([SOURCE] = "MECH_GP"))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### DateTableTemplate_ae1bc3b8-dd10-47c1-913a-5f4a589902e6

#### Partition: DateTableTemplate_ae1bc3b8-dd10-47c1-913a-5f4a589902e6-ca257ed7-7cd6-4f16-a2e4-af90b5b39931
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### DIVISION

#### Partition: DIVISION
- Kind: m
- Mode: import

```powerquery
	let

	      Source = JOB,

	    #"Replaced Value" = Table.ReplaceValue(Source,"PERF CONTRACT","GREEN",Replacer.ReplaceText,{"DIVISIONS"}),

	    #"Removed Other Columns" = Table.SelectColumns(#"Replaced Value",{"DIVISIONS"}),

	    #"Removed Duplicates" = Table.Distinct(#"Removed Other Columns"),

	    #"Trimmed Text1" = Table.TransformColumns(#"Removed Duplicates",{{"DIVISIONS", Text.Trim, type text}}),

	    #"Cleaned Text1" = Table.TransformColumns(#"Trimmed Text1",{{"DIVISIONS", Text.Clean, type text}})

	in

	    #"Cleaned Text1"



annotation PBI_ResultType = Table
```

### GL POSTING

#### Partition: GL POSTING
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    POSTING_DATA_F_Table = DW_FINAL_Schema{[Name="POSTING_DATA_F",Kind="Table"]}[Data],

	    #"Filtered Rows" = Table.SelectRows(POSTING_DATA_F_Table, each ([SOURCE] = "MECH_GP"))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### GP Parameter

#### Partition: GP Parameter
- Kind: calculated
- Mode: import

```powerquery
	{

	    ("GP% Difference", NAMEOF('Revenue Measures'[GP% Difference]), 0),

	    ("Forecasted GP%", NAMEOF('Revenue Measures'[Forecasted GP% Across Jobs]), 1),

	    ("Forecasted GP$", NAMEOF('Revenue Measures'[Forecasted GP$ Across Jobs]), 2)

	}



annotation PBI_Id = 8c7af060a7904f79ae2ea75dd738b373
```

### INVOICES

#### Partition: INVOICES
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    INVOICES_F_Table = DW_FINAL_Schema{[Name="INVOICES_F",Kind="Table"]}[Data],

	    #"Filtered Rows" = Table.SelectRows(INVOICES_F_Table, each ([SOURCE] = "MECH_GP"))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### JOB

#### Partition: JOB
- Kind: m
- Mode: import

```powerquery
	let

	      Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    JOBS_D_Table = DW_FINAL_Schema{[Name="JOBS_D",Kind="Table"]}[Data],

	    #"Trimmed Text" = Table.TransformColumns(JOBS_D_Table,{{"JOB_NUMBER", Text.Trim, type text}}),

	    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"JOB_NUMBER", Text.Clean, type text}}),

	    #"Replaced Value" = Table.ReplaceValue(#"Cleaned Text","PERF CONTRACT","GREEN",Replacer.ReplaceText,{"DIVISIONS"}),

	    #"Replaced Value1" = Table.ReplaceValue(#"Replaced Value",#date(1900, 1, 1),null,Replacer.ReplaceValue,{"TARGET_COMPLETION_DATE"}),

	    #"Replaced Value2" = Table.ReplaceValue(#"Replaced Value1",#date(1900, 1, 1),null,Replacer.ReplaceValue,{"ACT_COMPLETION_DATE"}),

	    #"Replaced Value3" = Table.ReplaceValue(#"Replaced Value2",#date(1900, 1, 1),null,Replacer.ReplaceValue,{"WARRANTY_START"}),

	    #"Replaced Value4" = Table.ReplaceValue(#"Replaced Value3",#date(1900, 1, 1),null,Replacer.ReplaceValue,{"WARRANTY_END"}),

	        #"Filtered Rows" = Table.SelectRows(#"Replaced Value4", each ([SOURCE] = "MECH_GP")),

	    #"Merged Queries" = Table.NestedJoin(#"Filtered Rows", {"MANAGER_KEY"}, EMPLOYEES, {"EMPLOYEE_KEY"}, "EMPLOYEES", JoinKind.LeftOuter),

	    #"Expanded EMPLOYEES" = Table.ExpandTableColumn(#"Merged Queries", "EMPLOYEES", {"Active Employees"}, {"Project Manager"}),

	    #"Merged Queries1" = Table.NestedJoin(#"Expanded EMPLOYEES", {"ESTIMATOR_KEY"}, EMPLOYEES, {"EMPLOYEE_KEY"}, "EMPLOYEES", JoinKind.LeftOuter),

	    #"Expanded EMPLOYEES1" = Table.ExpandTableColumn(#"Merged Queries1", "EMPLOYEES", {"Active Employees"}, {"Sales Rep"}),

	    #"Merged Queries2" = Table.NestedJoin(#"Expanded EMPLOYEES1", {"SUPERINT_KEY"}, EMPLOYEES, {"EMPLOYEE_KEY"}, "EMPLOYEES", JoinKind.LeftOuter),

	    #"Expanded EMPLOYEES2" = Table.ExpandTableColumn(#"Merged Queries2", "EMPLOYEES", {"FULL_NAME"}, {"FULL_NAME"}),

	    #"Renamed Columns" = Table.RenameColumns(#"Expanded EMPLOYEES2",{{"SUPERINTENDENT", "SUPERINTENDENT ID"}, {"FULL_NAME", "Superintendent"}})

	in

	    #"Renamed Columns"



annotation PBI_ResultType = Table
```

### JOB FORECAST

#### Partition: JOB FORECAST
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    JOB_COST_FORECASTS_F_Table = DW_FINAL_Schema{[Name="JOB_COST_FORECASTS_F",Kind="Table"]}[Data],

	    #"Trimmed Text" = Table.TransformColumns(JOB_COST_FORECASTS_F_Table,{{"COST_CODE_1", Text.Trim, type text}, {"COST_CODE_2", Text.Trim, type text}, {"COST_CODE_3", Text.Trim, type text}, {"COST_CODE", Text.Trim, type text}}),

	    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"COST_CODE_1", Text.Clean, type text}, {"COST_CODE_2", Text.Clean, type text}, {"COST_CODE_3", Text.Clean, type text}, {"JOB_NUMBER", Text.Clean, type text}, {"COST_CODE", Text.Clean, type text}}),

	    #"Duplicated Column" = Table.DuplicateColumn(#"Cleaned Text", "JOB_NUMBER", "WS_JOB_NUMBER - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "COST_CODE", "COST_CODE - Copy"),

	    #"Merged Columns1" = Table.CombineColumns(#"Duplicated Column1",{"WS_JOB_NUMBER - Copy", "COST_CODE - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Job_Cost Code"),

	    #"Filtered Rows" = Table.SelectRows(#"Merged Columns1", each ([SOURCE] = "MECH_GP"))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### JOB_COST_DETAILS

#### Partition: JOB_COST_DETAILS
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_CLEAN_Schema = DATA_WAREHOUSE_Database{[Name="DW_CLEAN",Kind="Schema"]}[Data],

	    JOB_COST_DETAILS_View = DW_CLEAN_Schema{[Name="JOB_COST_DETAILS",Kind="View"]}[Data],

	    #"Trimmed Text" = Table.TransformColumns(JOB_COST_DETAILS_View,{{"JOB_NUMBER", Text.Trim, type text}}),

	    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"JOB_NUMBER", Text.Clean, type text}}),

	    #"Duplicated Column" = Table.DuplicateColumn(#"Cleaned Text", "JOB_NUMBER", "JOB_NUMBER - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "COST_CODE", "COST_CODE - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column1",{"JOB_NUMBER - Copy", "COST_CODE - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Job_Cost Code"),

	        #"Filtered Rows" = Table.SelectRows(#"Merged Columns", each ([SOURCE] = "MECH_GP"))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### JOB_COST_SUMMARY

#### Partition: JOB_COST_SUMMARY
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    JOB_COST_SUMMARY_F_Table = DW_FINAL_Schema{[Name="JOB_COST_SUMMARY_F",Kind="Table"]}[Data],

	    #"Filtered Rows" = Table.SelectRows(JOB_COST_SUMMARY_F_Table, each ([SOURCE] = "MECH_GP")),

	    #"Duplicated Column" = Table.DuplicateColumn(#"Filtered Rows", "JOB_NUMBER", "JOB_NUMBER - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column",{"JOB_NUMBER - Copy", "COST_CODE"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Job Cost Code")

	in

	    #"Merged Columns"



annotation PBI_ResultType = Table
```

### JOB_LABOR_HOURS

#### Partition: JOB_LABOR_HOURS
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    JOB_LABOR_HOURS_F_Table = DW_FINAL_Schema{[Name="JOB_LABOR_HOURS_F",Kind="Table"]}[Data],

	    #"Duplicated Column" = Table.DuplicateColumn(JOB_LABOR_HOURS_F_Table, "JOB_NUMBER", "JOB_NUMBER - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "COST_CODE", "COST_CODE - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column1",{"JOB_NUMBER - Copy", "COST_CODE - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Job_Cost Code"),

	    #"Filtered Rows" = Table.SelectRows(#"Merged Columns", each ([SOURCE] = "MECH_GP"))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### LocalDateTable_103d4237-3f13-4fb8-908e-8f990ad5f6f8

#### Partition: LocalDateTable_103d4237-3f13-4fb8-908e-8f990ad5f6f8
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_26e0a611-4938-40bf-8444-deab64adf683

#### Partition: LocalDateTable_26e0a611-4938-40bf-8444-deab64adf683
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_288a7e21-8bfa-49ce-90b0-3f281030da3e

#### Partition: LocalDateTable_288a7e21-8bfa-49ce-90b0-3f281030da3e
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f

#### Partition: LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_3068354c-1934-4176-9b53-101d178cc7da

#### Partition: LocalDateTable_3068354c-1934-4176-9b53-101d178cc7da
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_39148a68-5226-4488-8b67-dc23f90c2fda

#### Partition: LocalDateTable_39148a68-5226-4488-8b67-dc23f90c2fda
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f

#### Partition: LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_4d5c68a9-1016-4c7f-8bd6-94b091483340

#### Partition: LocalDateTable_4d5c68a9-1016-4c7f-8bd6-94b091483340
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356

#### Partition: LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_69547476-3a6b-4a5f-8fcf-f5f0ffbaa28e

#### Partition: LocalDateTable_69547476-3a6b-4a5f-8fcf-f5f0ffbaa28e
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_7c0dba22-51a6-475f-9385-01ea578d2301

#### Partition: LocalDateTable_7c0dba22-51a6-475f-9385-01ea578d2301
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_820e8c9a-6a47-49de-b350-058a53302479

#### Partition: LocalDateTable_820e8c9a-6a47-49de-b350-058a53302479
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_82986f2d-45c5-4243-bb17-c0844f70692b

#### Partition: LocalDateTable_82986f2d-45c5-4243-bb17-c0844f70692b
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_8f32177c-7b7f-4b5c-afda-6d8a43f3b74a

#### Partition: LocalDateTable_8f32177c-7b7f-4b5c-afda-6d8a43f3b74a
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_a1304e08-f471-47dc-bbfc-f6653e634bfb

#### Partition: LocalDateTable_a1304e08-f471-47dc-bbfc-f6653e634bfb
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98

#### Partition: LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_d9746aa8-c787-46e8-a0b0-2e5477439e51

#### Partition: LocalDateTable_d9746aa8-c787-46e8-a0b0-2e5477439e51
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_dbc8e48e-68af-4633-963c-bd15e3755808

#### Partition: LocalDateTable_dbc8e48e-68af-4633-963c-bd15e3755808
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_dc9a7e8b-973c-4d72-ad27-3eff05a132d9

#### Partition: LocalDateTable_dc9a7e8b-973c-4d72-ad27-3eff05a132d9
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_df4ab1e5-1799-472a-b536-48d903e2a6f1

#### Partition: LocalDateTable_df4ab1e5-1799-472a-b536-48d903e2a6f1
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_e2d949a2-51a9-4559-aff7-c4bc089c82a9

#### Partition: LocalDateTable_e2d949a2-51a9-4559-aff7-c4bc089c82a9
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae

#### Partition: LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### Refresh Date

#### Partition: Refresh Date
- Kind: m
- Mode: import

```powerquery
	let

	    Source = DateTimeZone.SwitchZone(DateTimeZone.UtcNow(), -5, 0),

	    #"Converted to Table1" = #table(1, {{Source}}),

	    #"Changed Type" = Table.TransformColumnTypes(#"Converted to Table1",{{"Column1", type datetime}}),

	    #"Duplicated Column" = Table.DuplicateColumn(#"Changed Type", "Column1", "Column1 - Copy"),

	    #"Changed Type1" = Table.TransformColumnTypes(#"Duplicated Column",{{"Column1", type date}, {"Column1 - Copy", type time}}),

	    #"Renamed Columns" = Table.RenameColumns(#"Changed Type1",{{"Column1", "Date"}, {"Column1 - Copy", "Time"}})

	in

	    #"Renamed Columns"



annotation PBI_ResultType = Table
```

### Revenue Measures

#### Partition: Revenue Measures
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Column1 = _t]),

	    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Column1", type text}}),

	    #"Removed Columns" = Table.RemoveColumns(#"Changed Type",{"Column1"})

	in

	    #"Removed Columns"



annotation PBI_ResultType = Table
```

## Shared Power Query Expressions
(From `definition/expressions.tmdl` — these may be staging / disabled-load queries.)

### EMPLOYEES
```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    EMPLOYEES_D_Table = DW_FINAL_Schema{[Name="EMPLOYEES_D",Kind="Table"]}[Data],

	    #"Capitalized Each Word" = Table.TransformColumns(EMPLOYEES_D_Table,{{"FULL_NAME", Text.Proper, type text}}),

	    #"Filtered Rows" = Table.SelectRows(#"Capitalized Each Word", each ([SOURCE] = "MECH_GP")),

	    #"Added Custom" = Table.AddColumn(#"Filtered Rows", "Active Employees", each if [INACTIVE] = true then null else [FULL_NAME])

	in

	    #"Added Custom"
```

### JOB PROFILE _ PROJECTION TRENDS
```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_DEV_Database = Source{[Name="DATA_WAREHOUSE_DEV",Kind="Database"]}[Data],

	    PUBLIC_Schema = DATA_WAREHOUSE_DEV_Database{[Name="PUBLIC",Kind="Schema"]}[Data],

	    JOB_PROFILE_View = PUBLIC_Schema{[Name="JOB_PROFILE",Kind="View"]}[Data]

	in

	    JOB_PROFILE_View
```

### PO JOB DETAILS
```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    PO_JOB_DETAILS_F_Table = DW_FINAL_Schema{[Name="PO_JOB_DETAILS_F",Kind="Table"]}[Data],

	    #"Filtered Rows1" = Table.SelectRows(PO_JOB_DETAILS_F_Table, each ([SOURCE] = "MECH_GP")),

	    #"Sorted Rows" = Table.Sort(#"Filtered Rows1",{{"COMMITTED_COST", Order.Descending}}),

	    #"Filtered Rows" = Table.SelectRows(#"Sorted Rows", each [JOB_NUMBER] = "23056")

	in

	    #"Filtered Rows"
```

### Tables
```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    JOB_LABOR_HOURS_F_Table = DW_FINAL_Schema{[Name="JOB_LABOR_HOURS_F",Kind="Table"]}[Data]

	in

	    JOB_LABOR_HOURS_F_Table
```
