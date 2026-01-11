let
    Source = CALLS_F,
    // Filter for calls where Contract Number is NULL (Spot/T&M)
    Filtered_Spot_Calls = Table.SelectRows(Source, each [Contract Number] = null or [Contract Number] = ""),

    // Select and rename columns
    Selected_Columns = Table.SelectColumns(Filtered_Spot_Calls, {
        "Date Of Service Call",
        "Customernbr Key", // Customer dimension key
        "Billable All",    // Revenue
        "Cost All",        // Cost
        "Service Call Id"  // Unique ID for the transaction
    }),
    Renamed_Columns = Table.RenameColumns(Selected_Columns, {
        {"Date Of Service Call", "Date"},
        {"Customernbr Key", "Customer Key"},
        {"Billable All", "Revenue"},
        {"Cost All", "Cost"},
        {"Service Call Id", "ServiceCallKey"}
    }),
    
    // Set data types
    Typed_Columns = Table.TransformColumnTypes(Renamed_Columns, {
        {"Date", type date},
        {"Customer Key", type text},
        {"Revenue", Currency.Type},
        {"Cost", Currency.Type},
        {"ServiceCallKey", type text}
    }),
    
    // Add Source Type for categorization in reports
    SPOT_FINANCIALS_F = Table.AddColumn(Typed_Columns, "Source Type", each "Spot T&M", type text)
in
    SPOT_FINANCIALS_F