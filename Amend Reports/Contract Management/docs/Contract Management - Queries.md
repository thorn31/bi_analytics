# Contract Management — Partitions + Source Queries

Generated: 2026-01-22 15:09 EST

## Table Partitions

### APPOINTMENTS_F

#### Partition: APPOINTMENTS_F
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    APPOINTMENTS_F_Table = DW_FINAL_Schema{[Name="APPOINTMENTS_F",Kind="Table"]}[Data],

	    #"Changed Type" = Table.TransformColumnTypes(APPOINTMENTS_F_Table,{{"TASK_DATE", type date}, {"STRTTIME", type time}, {"ENDTIME", type time}}),

	    #"Trimmed Text" = Table.TransformColumns(#"Changed Type",{{"SERVICE_CALL_ID", Text.Trim, type text}}),

	    #"Merged Queries" = Table.NestedJoin(#"Trimmed Text", {"SERVICE_CALL_ID"}, CALLS_F, {"SERVICE_CALL_ID"}, "CALLS_F", JoinKind.LeftOuter),

	    #"Expanded CALLS_F" = Table.ExpandTableColumn(#"Merged Queries", "CALLS_F", {"CUSTNMBR", "CONTRACT_NUMBER"}, {"CALLS_F.CUSTNMBR", "CALLS_F.CONTRACT_NUMBER"}),

	    #"Merged Columns" = Table.CombineColumns(#"Expanded CALLS_F",{"CALLS_F.CUSTNMBR", "CALLS_F.CONTRACT_NUMBER"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Customer-Contract")

	in

	    #"Merged Columns"



annotation PBI_ResultType = Table



annotation PBI_NavigationStepName = Navigation
```

### BUDGET_F

#### Partition: BUDGET_F
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    BUDGET_F_Table = DW_FINAL_Schema{[Name="BUDGET_F",Kind="Table"]}[Data],

	    #"Changed Type" = Table.TransformColumnTypes(BUDGET_F_Table,{{"PERIODDT", type date}}),

	    #"Filtered Rows" = Table.SelectRows(#"Changed Type", each ([SOURCE] = "SERV_GP")),

	    #"Replaced Value" = Table.ReplaceValue(#"Filtered Rows","CFS","CFS PROJ JC",Replacer.ReplaceText,{"DIVISION"}),

	    #"Trimmed Text" = Table.TransformColumns(#"Replaced Value",{{"DIVISION", Text.Trim, type text}}),

	    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"DIVISION", Text.Clean, type text}})

	in

	    #"Cleaned Text"



annotation PBI_ResultType = Table
```

### Calendar

#### Partition: Calendar-d7293210-4553-47c2-8825-e570d51daaae
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### CALLS COSTS

#### Partition: CALLS COSTS
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CALLS_F_Table = DW_FINAL_Schema{[Name="CALLS_F",Kind="Table"]}[Data],

	    #"Changed Type" = Table.TransformColumnTypes(CALLS_F_Table,{{"DATE_OF_SERVICE_CALL", type date}}),

	    #"Trimmed Text" = Table.TransformColumns(#"Changed Type",{{"SERVICE_CALL_ID", Text.Trim, type text}, {"CUSTNMBR", Text.Trim, type text}}),

	    #"Duplicated Column" = Table.DuplicateColumn(#"Trimmed Text", "CUSTNMBR", "CUSTNMBR - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "CONTRACT_NUMBER", "CONTRACT_NUMBER - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column1",{"CUSTNMBR - Copy", "CONTRACT_NUMBER - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Customer - Contract"),

	    #"Removed Other Columns" = Table.SelectColumns(#"Merged Columns",{"SERVICE_CALL_ID", "CONTRACT_NUMBER", "WSCONTSQ",

	"COST_EQUIPMENT", "COST_LABOR", "COST_MATERIAL", "COST_OTHER", "COST_SUBS", "COST_TAX", "DATE_OF_SERVICE_CALL", "Customer - Contract"}),

	    #"Unpivoted Columns" = Table.UnpivotOtherColumns(#"Removed Other Columns", {"SERVICE_CALL_ID", "CONTRACT_NUMBER", "WSCONTSQ", "DATE_OF_SERVICE_CALL", "Customer - Contract"}, "Attribute", "Value"),

	    #"Replaced Value" = Table.ReplaceValue(#"Unpivoted Columns","COST_EQUIPMENT","EQUIPMENT",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value1" = Table.ReplaceValue(#"Replaced Value","COST_LABOR","LABOR",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value2" = Table.ReplaceValue(#"Replaced Value1","COST_MATERIAL","MATERIAL",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value3" = Table.ReplaceValue(#"Replaced Value2","COST_OTHER","OTHER",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value4" = Table.ReplaceValue(#"Replaced Value3","COST_SUBS","SUBS",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value5" = Table.ReplaceValue(#"Replaced Value4","COST_TAX","TAX",Replacer.ReplaceText,{"Attribute"}),

	    #"Renamed Columns" = Table.RenameColumns(#"Replaced Value5",{{"Attribute", "Cost Type"}}),

	    #"Filtered Rows" = Table.SelectRows(#"Renamed Columns", each ([Value] <> 0))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### CALLS_F

#### Partition: CALLS_F
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CALLS_F_Table = DW_FINAL_Schema{[Name="CALLS_F",Kind="Table"]}[Data],

	    #"Changed Type" = Table.TransformColumnTypes(CALLS_F_Table,{{"DATE_OF_SERVICE_CALL", type date}}),

	    #"Trimmed Text" = Table.TransformColumns(#"Changed Type",{{"SERVICE_CALL_ID", Text.Trim, type text}, {"CUSTNMBR", Text.Trim, type text}}),

	    #"Duplicated Column" = Table.DuplicateColumn(#"Trimmed Text", "CUSTNMBR", "CUSTNMBR - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "CONTRACT_NUMBER", "CONTRACT_NUMBER - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column1",{"CUSTNMBR - Copy", "CONTRACT_NUMBER - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Customer - Contract")

	in

	    #"Merged Columns"



annotation PBI_ResultType = Table



annotation PBI_NavigationStepName = Navigation
```

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

	    #"Filtered Rows" = Table.SelectRows(#"Removed Duplicates", each ([SOURCE] = "SERV_GP"))

	in

	    #"Filtered Rows"



annotation PBI_ResultType = Table
```

### Contract Measures

#### Partition: Contract Measures
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

### CONTRACT_Hour_Breakout

#### Partition: CONTRACT_Hour_Breakout
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CONTRACTS_D_Table = DW_FINAL_Schema{[Name="CONTRACTS_D",Kind="Table"]}[Data],

	    #"Trimmed Text" = Table.TransformColumns(CONTRACTS_D_Table,{{"CUSTNMBR", Text.Trim, type text}, {"CONTRACT_NUMBER", Text.Trim, type text}}),

	    #"Duplicated Column" = Table.DuplicateColumn(#"Trimmed Text", "CUSTNMBR", "CUSTNMBR - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "CONTRACT_NUMBER", "CONTRACT_NUMBER - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column1",{"CUSTNMBR - Copy", "CONTRACT_NUMBER - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Customer-Contract"),

	    #"Removed Other Columns" = Table.SelectColumns(#"Merged Columns",{ "ACTUAL_LABOR_1_HOURS_REPAIR", "ACTUAL_LABOR_2_HOURS_PM", "ACTUAL_LABOR_3_HOURS_TRAVEL", "Customer-Contract", "CONTRACT_START_DATE", "CONTRACT_EXPIRATION_DATE"}),

	    #"Changed Type" = Table.TransformColumnTypes(#"Removed Other Columns",{{"CONTRACT_START_DATE", type date}, {"CONTRACT_EXPIRATION_DATE", type date}}),

	    #"Unpivoted Columns" = Table.UnpivotOtherColumns(#"Changed Type", {"Customer-Contract", "CONTRACT_START_DATE", "CONTRACT_EXPIRATION_DATE"}, "Attribute", "Value"),

	    #"Replaced Value" = Table.ReplaceValue(#"Unpivoted Columns","ACTUAL_LABOR_1_HOURS_REPAIR","REPAIR",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value1" = Table.ReplaceValue(#"Replaced Value","ACTUAL_LABOR_2_HOURS_PM","PM",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value2" = Table.ReplaceValue(#"Replaced Value1","ACTUAL_LABOR_3_HOURS_TRAVEL","TRAVEL",Replacer.ReplaceText,{"Attribute"}),

	    #"Renamed Columns" = Table.RenameColumns(#"Replaced Value2",{{"Attribute", "Type"}, {"Value", "Hours"}})

	in

	    #"Renamed Columns"



annotation PBI_ResultType = Table
```

### CONTRACT_LABOR_HOURS_F

#### Partition: CONTRACT_LABOR_HOURS_F
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CALLS_F_Table = DW_FINAL_Schema{[Name="CONTRACT_LABOR_HOURS_F",Kind="Table"]}[Data]

	in

	    CALLS_F_Table



annotation PBI_NavigationStepName = Navigation



annotation PBI_ResultType = Table
```

### CONTRACTS MAPPING

#### Partition: CONTRACTS MAPPING
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CONTRACTS_D_Table = DW_FINAL_Schema{[Name="CONTRACTS_D",Kind="Table"]}[Data],

	    #"Trimmed Text" = Table.TransformColumns(CONTRACTS_D_Table,{{"CUSTNMBR", Text.Trim, type text}, {"CONTRACT_NUMBER", Text.Trim, type text}}),

	    #"Removed Other Columns" = Table.SelectColumns(#"Trimmed Text",{"CUSTNMBR", "CONTRACT_NUMBER"}),

	    #"Duplicated Column" = Table.DuplicateColumn(#"Removed Other Columns", "CUSTNMBR", "CUSTNMBR - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "CONTRACT_NUMBER", "CONTRACT_NUMBER - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column1",{"CUSTNMBR - Copy", "CONTRACT_NUMBER - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Customer-Contract"),

	    #"Removed Duplicates" = Table.Distinct(#"Merged Columns")

	in

	    #"Removed Duplicates"



annotation PBI_ResultType = Table
```

### CONTRACTS_BILLING_F

#### Partition: CONTRACTS_BILLING_F
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CONTRACT_BILLING_F_Table = DW_FINAL_Schema{[Name="CONTRACT_BILLING_F",Kind="Table"]}[Data],

	    #"Changed Type" = Table.TransformColumnTypes(CONTRACT_BILLING_F_Table,{{"DATE1", type date}, {"WENNSOFT_BILLING_DATE", type date}}),

	    #"Duplicated Column" = Table.DuplicateColumn(#"Changed Type", "CUSTNMBR", "CUSTNMBR - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "CONTRACT_NUMBER", "CONTRACT_NUMBER - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column1",{"CUSTNMBR - Copy", "CONTRACT_NUMBER - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Customer-Contract")

	in

	    #"Merged Columns"



annotation PBI_ResultType = Table
```

### CONTRACTS_D

#### Partition: CONTRACTS_D
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CONTRACTS_D_Table = DW_FINAL_Schema{[Name="CONTRACTS_D",Kind="Table"]}[Data],

	    #"Trimmed Text" = Table.TransformColumns(CONTRACTS_D_Table,{{"CUSTNMBR", Text.Trim, type text}, {"CONTRACT_NUMBER", Text.Trim, type text}}),

	    #"Duplicated Column" = Table.DuplicateColumn(#"Trimmed Text", "CUSTNMBR", "CUSTNMBR - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "CONTRACT_NUMBER", "CONTRACT_NUMBER - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column1",{"CUSTNMBR - Copy", "CONTRACT_NUMBER - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Customer-Contract")

	in

	    #"Merged Columns"



annotation PBI_ResultType = Table
```

### CONTRACTS_TASK_SCHEDULE

#### Partition: CONTRACTS_TASK_SCHEDULE
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    SERV_CONTRACT_TASKS_F_Table = DW_FINAL_Schema{[Name="SERV_CONTRACT_TASKS_F",Kind="Table"]}[Data],

	    #"Changed Type" = Table.TransformColumnTypes(SERV_CONTRACT_TASKS_F_Table,{{"SCHEDULE_DATE", type date},{"WSCONTSQ", type number} ,{"ORIGINAL_SCHEDULE_DATE", type date}}),

	    #"Trimmed Text" = Table.TransformColumns(#"Changed Type",{{"CUSTNMBR", Text.Trim, type text}, {"CONTRACT_NUMBER", Text.Trim, type text}}),

	    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"CUSTNMBR", Text.Clean, type text}, {"CONTRACT_NUMBER", Text.Clean, type text}}),

	    #"Merged Columns" = Table.CombineColumns(#"Cleaned Text",{"CUSTNMBR", "CONTRACT_NUMBER"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Customer-Contract")

	in

	    #"Merged Columns"



annotation PBI_NavigationStepName = Navigation



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

### Cost Types

#### Partition: Cost Types
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CALLS_F_Table = DW_FINAL_Schema{[Name="CONTRACTS_D",Kind="Table"]}[Data],

	    #"Duplicated Column" = Table.DuplicateColumn(CALLS_F_Table, "CUSTNMBR", "CUSTNMBR - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "CONTRACT_NUMBER", "CONTRACT_NUMBER - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column1",{"CUSTNMBR - Copy", "CONTRACT_NUMBER - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Customer - Contract"),

	    #"Removed Other Columns" = Table.SelectColumns(#"Merged Columns",{ "CONTRACT_NUMBER", "FORECAST_HOURS", "FORECAST_LABOR", "FORECAST_EQUIPMENT", "FORECAST_MATERIAL", "FORECAST_SUBS", "FORECAST_OTHER",  "Customer - Contract"}),

	    #"Unpivoted Columns" = Table.UnpivotOtherColumns(#"Removed Other Columns", { "CONTRACT_NUMBER",  "Customer - Contract"}, "Attribute", "Value"),

	    #"Replaced Value" = Table.ReplaceValue(#"Unpivoted Columns","FORECAST_EQUIPMENT","EQUIPMENT",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value1" = Table.ReplaceValue(#"Replaced Value","FORECAST_LABOR","LABOR",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value2" = Table.ReplaceValue(#"Replaced Value1","FORECAST_MATERIAL","MATERIAL",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value3" = Table.ReplaceValue(#"Replaced Value2","FORECAST_OTHER","OTHER",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value4" = Table.ReplaceValue(#"Replaced Value3","FORECAST_SUBS","SUBS",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value5" = Table.ReplaceValue(#"Replaced Value4","FORECAST_HOURS","HOURS",Replacer.ReplaceText,{"Attribute"}),

	    #"Renamed Columns" = Table.RenameColumns(#"Replaced Value5",{{"Attribute", "Cost Type"}}),

	    #"Removed Other Columns1" = Table.SelectColumns(#"Renamed Columns",{"Cost Type"}),

	    #"Removed Duplicates" = Table.Distinct(#"Removed Other Columns1")

	in

	    #"Removed Duplicates"



annotation PBI_ResultType = Table
```

### CUSTOMERS_D

#### Partition: CUSTOMERS_D
- Kind: m
- Mode: import

```powerquery
	let

	        Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CUSTOMERS_D_Table = DW_FINAL_Schema{[Name="CUSTOMERS_D",Kind="Table"]}[Data],

	    #"Capitalized Each Word" = Table.TransformColumns(CUSTOMERS_D_Table,{{"CUSTOMER_NAME", Text.Proper, type text}}),

	    #"Filtered Rows" = Table.SelectRows(#"Capitalized Each Word", each ([SOURCE] = "SERV_GP")),

	    #"Trimmed Text" = Table.TransformColumns(#"Filtered Rows",{{"CUSTOMER_NUMBER", Text.Trim, type text}}),

	    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"CUSTOMER_NUMBER", Text.Clean, type text}})

	in

	    #"Cleaned Text"



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

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    JOBS_D_Table = DW_FINAL_Schema{[Name="JOBS_D",Kind="Table"]}[Data],

	    #"Filtered Rows" = Table.SelectRows(JOBS_D_Table, each ([SOURCE] = "SERV_GP")),

	    #"Removed Other Columns" = Table.SelectColumns(#"Filtered Rows",{"DIVISIONS", "CLEANED_DIVISIONS"}),

	    #"Removed Duplicates" = Table.Distinct(#"Removed Other Columns"),

	    #"Renamed Columns" = Table.RenameColumns(#"Removed Duplicates",{{"DIVISIONS", "DIVISION KEY"}, {"CLEANED_DIVISIONS", "Division"}}),

	    #"Trimmed Text" = Table.TransformColumns(#"Renamed Columns",{{"Division", Text.Trim, type text}}),

	    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"Division", Text.Clean, type text}})

	in

	    #"Cleaned Text"



annotation PBI_ResultType = Table
```

### FORECASTED CALLS COST

#### Partition: FORECASTED CALLS COST
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    CALLS_F_Table = DW_FINAL_Schema{[Name="CONTRACTS_D",Kind="Table"]}[Data],

	    #"Duplicated Column" = Table.DuplicateColumn(CALLS_F_Table, "CUSTNMBR", "CUSTNMBR - Copy"),

	    #"Duplicated Column1" = Table.DuplicateColumn(#"Duplicated Column", "CONTRACT_NUMBER", "CONTRACT_NUMBER - Copy"),

	    #"Merged Columns" = Table.CombineColumns(#"Duplicated Column1",{"CUSTNMBR - Copy", "CONTRACT_NUMBER - Copy"},Combiner.CombineTextByDelimiter(":", QuoteStyle.None),"Customer - Contract"),

	    #"Removed Other Columns" = Table.SelectColumns(#"Merged Columns",{ "CONTRACT_NUMBER", "CONTRACT_START_DATE", "CONTRACT_EXPIRATION_DATE", "ESTIMATE_HOURS", "ESTIMATE_LABOR", "ESTIMATE_EQUIPMENT", "ESTIMATE_MATERIAL", "ESTIMATE_SUBS", "ESTIMATE_OTHER",  "Customer - Contract"}),

	    #"Changed Type" = Table.TransformColumnTypes(#"Removed Other Columns",{{"CONTRACT_START_DATE", type date}, {"CONTRACT_EXPIRATION_DATE", type date}}),

	    #"Unpivoted Columns" = Table.UnpivotOtherColumns(#"Changed Type", { "CONTRACT_NUMBER",  "Customer - Contract", "CONTRACT_START_DATE", "CONTRACT_EXPIRATION_DATE"}, "Attribute", "Value"),

	    #"Replaced Value" = Table.ReplaceValue(#"Unpivoted Columns","ESTIMATE_EQUIPMENT","EQUIPMENT",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value1" = Table.ReplaceValue(#"Replaced Value","ESTIMATE_LABOR","LABOR",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value2" = Table.ReplaceValue(#"Replaced Value1","ESTIMATE_MATERIAL","MATERIAL",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value3" = Table.ReplaceValue(#"Replaced Value2","ESTIMATE_OTHER","OTHER",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value4" = Table.ReplaceValue(#"Replaced Value3","ESTIMATE_SUBS","SUBS",Replacer.ReplaceText,{"Attribute"}),

	    #"Replaced Value5" = Table.ReplaceValue(#"Replaced Value4","ESTIMATE_HOURS","HOURS",Replacer.ReplaceText,{"Attribute"}),

	    #"Renamed Columns" = Table.RenameColumns(#"Replaced Value5",{{"Attribute", "Cost Type"}}),

	    #"Filtered Rows" = Table.SelectRows(#"Renamed Columns", each ([Value] <> 0))

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

### GP Parameter 2

#### Partition: GP Parameter 2
- Kind: calculated
- Mode: import

```powerquery
	{

	    ("Actual GP$", NAMEOF('Contract Measures'[Actual GP$ Across Jobs_Contract]), 0),

	    ("Actual GP%", NAMEOF('Contract Measures'[Actual GP%_Contract]), 1)

	}



annotation PBI_Id = 37472477551243e581638d22477dba6d
```

### Hour Measures

#### Partition: Hour Measures
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

### LocalDateTable_00e51d8d-231f-4d65-881b-7cd775844859

#### Partition: LocalDateTable_00e51d8d-231f-4d65-881b-7cd775844859
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_1997b5af-fbda-41ee-846d-31f24c5d8bd7

#### Partition: LocalDateTable_1997b5af-fbda-41ee-846d-31f24c5d8bd7
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_287ff984-7355-4b13-9018-95e3a16e18e9

#### Partition: LocalDateTable_287ff984-7355-4b13-9018-95e3a16e18e9
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_2a249574-7315-48a3-bf2c-4c9bbab9a923

#### Partition: LocalDateTable_2a249574-7315-48a3-bf2c-4c9bbab9a923
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_2e841b8c-c7b1-4df6-aaad-a1a446fc7c01

#### Partition: LocalDateTable_2e841b8c-c7b1-4df6-aaad-a1a446fc7c01
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f

#### Partition: LocalDateTable_2f4d25e8-226e-4bdb-90b8-80d5e36a201f
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_36fb0cc6-3a6a-46f4-99fe-6340fb69c6b3

#### Partition: LocalDateTable_36fb0cc6-3a6a-46f4-99fe-6340fb69c6b3
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_38f12a90-c3e3-476c-8af6-3b87ccdcdb64

#### Partition: LocalDateTable_38f12a90-c3e3-476c-8af6-3b87ccdcdb64
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f

#### Partition: LocalDateTable_45849c3c-e06d-451f-8616-e45b735dd37f
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_4ed2ebea-2956-4a45-b593-72e2e76dd90c

#### Partition: LocalDateTable_4ed2ebea-2956-4a45-b593-72e2e76dd90c
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356

#### Partition: LocalDateTable_5b54adca-a1fe-49cb-afdc-803881595356
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_68db00b3-6e04-4ee2-a4a3-b33365193de7

#### Partition: LocalDateTable_68db00b3-6e04-4ee2-a4a3-b33365193de7
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_7568775e-9707-49cb-bf23-8bca38b29542

#### Partition: LocalDateTable_7568775e-9707-49cb-bf23-8bca38b29542
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_7b8a7d6f-03de-4370-ab61-70ffffb79124

#### Partition: LocalDateTable_7b8a7d6f-03de-4370-ab61-70ffffb79124
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_8931b809-08ab-4252-8179-ca3c21383cd6

#### Partition: LocalDateTable_8931b809-08ab-4252-8179-ca3c21383cd6
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_8d221eb4-201c-477f-89c5-03c6e03aa65e

#### Partition: LocalDateTable_8d221eb4-201c-477f-89c5-03c6e03aa65e
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_a823d9da-2d68-472e-bea7-b1c1f0ea5afc

#### Partition: LocalDateTable_a823d9da-2d68-472e-bea7-b1c1f0ea5afc
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_c357c417-93f4-4ea3-badf-ef0dec761ede

#### Partition: LocalDateTable_c357c417-93f4-4ea3-badf-ef0dec761ede
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98

#### Partition: LocalDateTable_ca9e521e-a39c-4bbf-a6fd-098d037b5a98
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_de817910-54ca-42f0-b798-d1ae454cca2b

#### Partition: LocalDateTable_de817910-54ca-42f0-b798-d1ae454cca2b
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_dea31c23-1eaa-490c-ab59-1e5b655fb2ca

#### Partition: LocalDateTable_dea31c23-1eaa-490c-ab59-1e5b655fb2ca
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_e59f379f-de3d-42a7-bd84-6e80ef7a5ed8

#### Partition: LocalDateTable_e59f379f-de3d-42a7-bd84-6e80ef7a5ed8
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae

#### Partition: LocalDateTable_e8656d71-0ea4-4096-9b0f-9ce7240092ae
- Kind: calculated
- Mode: import
- Source: (none in TMDL; may reference a shared expression)

### POSTING_DATA_F

#### Partition: POSTING_DATA_F
- Kind: m
- Mode: import

```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    POSTING_DATA_F_Table = DW_FINAL_Schema{[Name="POSTING_DATA_F",Kind="Table"]}[Data],

	    #"Filtered Rows" = Table.SelectRows(POSTING_DATA_F_Table, each ([SOURCE] = "SERV_GP")),

	    #"Replaced Value" = Table.ReplaceValue(#"Filtered Rows","CFS","CFS PROJ JC",Replacer.ReplaceText,{"DIVISION"})

	in

	    #"Replaced Value"



annotation PBI_ResultType = Table
```

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

### SERV_TASKS_F

#### Partition: SERV_TASKS_F
- Kind: m
- Mode: import

```powerquery
	let

	       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    TASKS_F_Table = DW_FINAL_Schema{[Name="TASKS_F",Kind="Table"]}[Data],

	    #"Trimmed Text" = Table.TransformColumns(TASKS_F_Table,{{"CUSTNMBR", Text.Trim, type text}, {"CONTRACT_NUMBER", Text.Trim, type text}})

	in

	    #"Trimmed Text"



annotation PBI_ResultType = Table
```

## Shared Power Query Expressions
(From `definition/expressions.tmdl` — these may be staging / disabled-load queries.)

### EMPLOYEES_D
```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    EMPLOYEES_D_Table = DW_FINAL_Schema{[Name="EMPLOYEES_D",Kind="Table"]}[Data],

	    #"Capitalized Each Word" = Table.TransformColumns(EMPLOYEES_D_Table,{{"FULL_NAME", Text.Proper, type text}}),

	    #"Filtered Rows" = Table.SelectRows(#"Capitalized Each Word", each ([SOURCE] = "SERV_GP")),

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

### PO_JOB _DETAILS_F
```powerquery
	let

	    Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),

	    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],

	    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],

	    PO_JOB_DETAILS_F_Table = DW_FINAL_Schema{[Name="PO_JOB_DETAILS_F",Kind="Table"]}[Data],

	    #"Filtered Rows2" = Table.SelectRows(PO_JOB_DETAILS_F_Table, each ([SOURCE] = "SERV_GP")),

	    #"Sorted Rows" = Table.Sort(#"Filtered Rows2",{{"COMMITTED_COST", Order.Descending}}),

	    #"Filtered Rows" = Table.SelectRows(#"Sorted Rows", each ([COST_CODE] <> ""))

	in

	    #"Filtered Rows"
```
