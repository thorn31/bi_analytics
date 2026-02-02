let
    // 1. Get the Current Dimension
    SourceDim = SERVCONTRACTS_D,
    
    // 2. Get Keys from Facts (Optimize by selecting distinct keys only)
    FactRevenue_Keys = Table.Distinct(Table.SelectColumns(SERVCONTRACTS_REVENUE_F, {"AgreementKey"})),
    FactCosts_Keys = Table.Distinct(Table.SelectColumns(SERVCONTRACTS_COSTS_F, {"AgreementKey"})),
    
    // Union Fact Keys
    All_Fact_Keys = Table.Distinct(Table.Combine({FactRevenue_Keys, FactCosts_Keys})),
    
    // 3. Find Orphans (Keys in Fact that are NOT in Dim)
    // Left Anti Join: Keep Fact Keys that don't match Dim
    Orphans = Table.NestedJoin(All_Fact_Keys, {"AgreementKey"}, SourceDim, {"AgreementKey"}, "DimMatch", JoinKind.LeftAnti),
    Orphans_Clean = Table.RemoveColumns(Orphans, {"DimMatch"}),
    
    // 4. Transform Orphans into Dimension Schema
    // We create a dummy record for each orphan
    Inferred_Members = Table.AddColumn(Orphans_Clean, "NewRecord", each [
        AgreementKey = [AgreementKey],
        #"Contract Number" = "Unknown (" & [AgreementKey] & ")",
        #"Contract Description" = "Data Integrity - Missing in Source",
        #"Customer Key Full" = "Unknown",
        #"Customer Number" = "Unknown",
        #"YearIndex" = 0,
        #"Contract Type" = "Unknown",
        #"Divisions" = "Unknown",
        #"Contract Status" = "Orphan",
        #"Start Date" = #date(1900, 1, 1),
        #"End Date" = #date(1900, 1, 1),
        #"Contract Amount" = 0,
        #"Annual Contract Value" = 0
    ]),
    
    Inferred_Table = Table.FromRecords(Inferred_Members[NewRecord]),
    
    // Ensure Column Types Match SourceDim before union
    // (This is a simplified type mapping; Power Query usually handles nulls ok in unions)
    
    // 5. Append
    Final_Dimension = Table.Combine({SourceDim, Inferred_Table})
in
    Final_Dimension