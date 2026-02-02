# Service Call Management — Queries (Power Query / Partitions)

Generated: 2026-01-22 EST

This document focuses on the service-call tables and how their data is shaped in Power Query.

## `*CALL DETAILS` (M partition)
Source: Snowflake `DATA_WAREHOUSE.DW_FINAL.CALL_DETAILS_F`

```powerquery
let
       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),
    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],
    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],
    CALL_DETAILS_F_Table = DW_FINAL_Schema{[Name="CALL_DETAILS_F",Kind="Table"]}[Data],
    #"Filtered Rows" = Table.SelectRows(CALL_DETAILS_F_Table, each ([SERVICE_CALL_ID] <> ""))
in
    #"Filtered Rows"
```

## `*CALLS_F` (M partition)
Source: Snowflake `DATA_WAREHOUSE.DW_FINAL.CALLS_F`

This is the base service call fact table. It is also used as the source for `*CALLS COSTS` (see below).

## `*CALLS COSTS` (M partition)
Source base table: Snowflake `DATA_WAREHOUSE.DW_FINAL.CALLS_F` (Table)

This query unpivots cost columns from `CALLS_F` into a `[Cost Type]` / `[Value]` structure.

```powerquery
let
       Source = Snowflake.Databases("ws53155.central-us.azure.snowflakecomputing.com","COMPUTE_WH"),
    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],
    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],
    CALLS_F_Table = DW_FINAL_Schema{[Name="CALLS_F",Kind="Table"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(CALLS_F_Table,{{"DATE_OF_SERVICE_CALL", type date}}),
    #"Trimmed Text" = Table.TransformColumns(#"Changed Type",{{"SERVICE_CALL_ID", Text.Trim, type text}, {"CUSTNMBR", Text.Trim, type text}}),
    #"Replaced Value6" = Table.ReplaceValue(#"Trimmed Text","","Billable Repair",Replacer.ReplaceValue,{"CONTRACT_NUMBER"}),
    #"Duplicated Column" = Table.DuplicateColumn(#"Replaced Value6", "CUSTNMBR", "CUSTNMBR - Copy"),
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
```

## `*Calendar`
This is a calculated date table (not sourced from Snowflake). It is used for fiscal-year logic in `Service Call Measures` and for relationship-based measures using `USERELATIONSHIP` to `*CALLS_F[CREATED_DATE]`.

