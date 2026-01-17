let
    // 1. Original CUSTOMERS_D Source (Snowflake)
    Source = Snowflake.Databases("ufwarhx-qo50284.snowflakecomputing.com", "COMPUTE_WH", []),
    DATA_WAREHOUSE_Database = Source{[Name="DATA_WAREHOUSE",Kind="Database"]}[Data],
    DW_FINAL_Schema = DATA_WAREHOUSE_Database{[Name="DW_FINAL",Kind="Schema"]}[Data],
    CUSTOMERS_D_Table = DW_FINAL_Schema{[Name="CUSTOMERS_D",Kind="Table"]}[Data], 
    
    // 2. Initial Formatting (Matches current CRR v05 logic)
    ProperCase = Table.RenameColumns(CUSTOMERS_D_Table, List.Transform(Table.ColumnNames(CUSTOMERS_D_Table), each {_, Text.Proper(Text.Replace(_, "_", " "))})),
    #"Capitalized Each Word" = Table.TransformColumns(ProperCase,{{"Customer Name", Text.Proper, type text}}),

    // 3. Load Segmentation Data (Generated via Python script)
    // NOTE: Change the folder path to match your environment if moving to production/service
    SegmentationFilePath = "C:\Users\thorn\documents\projects\powerbi\Customer Revenue Retention\data\CustomerSegmentation.csv",
    SegmentationSource = Csv.Document(File.Contents(SegmentationFilePath),[Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(SegmentationSource, [PromoteAllScalars=true]),
    #"Typed Segmentation" = Table.TransformColumnTypes(#"Promoted Headers",{{"Customer Key", type text}, {"Original Name", type text}, {"Master Customer Name", type text}, {"Segment", type text}, {"Source", type text}}),
    
    // 4. Merge Segmentation and Master Name onto Dimension
    #"Merged Queries" = Table.NestedJoin(#"Capitalized Each Word", {"Customer Key"}, #"Typed Segmentation", {"Customer Key"}, "Segmentation", JoinKind.LeftOuter),
    #"Expanded Segmentation" = Table.ExpandTableColumn(#"Merged Queries", "Segmentation", {"Master Customer Name", "Segment"}, {"Master Customer Name", "Segment"}),
    
    // 5. Cleanup and Null Handling
    // Fill "Other" for any customers that didn't match the segmentation file
    #"Filled Segment" = Table.ReplaceValue(#"Expanded Segmentation", null, "Other", Replacer.ReplaceValue, {"Segment"}),
    
    // If Master Name is null, fall back to the original Customer Name
    #"Added Final Master Name" = Table.AddColumn(#"Filled Segment", "Final Master Name", each if [Master Customer Name] = null or [Master Customer Name] = "" then [Customer Name] else [Master Customer Name], type text),
    
    // Final Selection
    #"Removed Temporary Columns" = Table.RemoveColumns(#"Added Final Master Name", {"Master Customer Name"}),
    #"Renamed Final Columns" = Table.RenameColumns(#"Removed Temporary Columns", {{"Final Master Name", "Master Customer Name"}})
in
    #"Renamed Final Columns"