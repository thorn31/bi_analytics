let
    // 1. Get the Current Dimension (Ensure this is the RAW/STAGING one to avoid cycles)
    SourceDim = SERVCONTRACTS_D_RAW, 
    
    // 2. Get Keys from Facts with Source Tagging
    FactRevenue_Keys = Table.Distinct(Table.SelectColumns(SERVCONTRACTS_REVENUE_F, {"AgreementKey"})),
    FactRevenue_Tagged = Table.AddColumn(FactRevenue_Keys, "IsRevenue", each true, type logical),
    
    FactCosts_Keys = Table.Distinct(Table.SelectColumns(SERVCONTRACTS_COSTS_F, {"AgreementKey"})),
    FactCosts_Tagged = Table.AddColumn(FactCosts_Keys, "IsCost", each true, type logical),
    
    // 3. Merge Fact Keys to find Union and Source
    FactCosts_Renamed = Table.RenameColumns(FactCosts_Tagged, {{"AgreementKey", "AgreementKey_Cost"}}),
    All_Fact_Keys = Table.Join(FactRevenue_Tagged, "AgreementKey", FactCosts_Renamed, "AgreementKey_Cost", JoinKind.FullOuter),
    Consolidated_Keys = Table.AddColumn(All_Fact_Keys, "AgreementKey_Final", each if [AgreementKey] <> null then [AgreementKey] else [AgreementKey_Cost], type text),
    
    Add_Source_Label = Table.AddColumn(Consolidated_Keys, "OrphanSource", each 
        if [IsRevenue] = true and [IsCost] = true then "Both"
        else if [IsRevenue] = true then "Revenue Only"
        else "Cost Only", type text
    ),
    
    Fact_Keys_Clean = Table.SelectColumns(Add_Source_Label, {"AgreementKey_Final", "OrphanSource"}),
    Fact_Keys_Renamed = Table.RenameColumns(Fact_Keys_Clean, {{"AgreementKey_Final", "AgreementKey"}}),

    // 4. Find Orphans
    Orphans = Table.NestedJoin(Fact_Keys_Renamed, {"AgreementKey"}, SourceDim, {"AgreementKey"}, "DimMatch", JoinKind.LeftAnti),
    Orphans_Clean = Table.RemoveColumns(Orphans, {"DimMatch"}),
    
    // 5. Transform Orphans into Dimension Schema (With Parsing)
    Inferred_Members = Table.AddColumn(Orphans_Clean, "NewRecord", each [
        // Parse Logic
        ParsedCustomer = Text.BeforeDelimiter([AgreementKey], "SERV_GP"),
        CustomerKey = ParsedCustomer & "SERV_GP",
        RestOfKey = Text.AfterDelimiter([AgreementKey], "SERV_GP_"),
        ParsedYear = try Number.From(Text.AfterDelimiter(RestOfKey, "_", {0, RelativePosition.FromEnd})) otherwise 0,
        ParsedContract = Text.BeforeDelimiter(RestOfKey, "_", {0, RelativePosition.FromEnd}),

        // Record Construction
        AgreementKey = [AgreementKey],
        #"Contract Number" = ParsedContract, 
        #"Contract Description" = "Data Integrity - Missing in Source (" & [OrphanSource] & ")",
        #"Customer Key Full" = CustomerKey, 
        #"Customer Number" = ParsedCustomer,
        #"YearIndex" = ParsedYear, 
        #"Contract Type" = "Unknown",
        #"Divisions" = "Unknown",
        #"Contract Status" = "Orphan",
        #"Start Date" = #date(1900, 1, 1),
        #"End Date" = #date(1900, 1, 1),
        #"Contract Amount" = 0,
        #"Annual Contract Value" = 0,
        #"OrphanSource" = [OrphanSource] 
    ]),
    
    Inferred_Table = Table.FromRecords(Inferred_Members[NewRecord]),
    
    // Add OrphanSource column to Original Dim
    SourceDim_Ready = Table.AddColumn(SourceDim, "OrphanSource", each null, type text),

    // 6. Append
    Final_Dimension = Table.Combine({SourceDim_Ready, Inferred_Table})
in
    Final_Dimension