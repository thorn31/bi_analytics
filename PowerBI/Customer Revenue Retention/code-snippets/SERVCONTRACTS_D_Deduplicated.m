let
    // 1. Get Source Data
    Source = CONTRACTS_D, 
    
    // 2. Identify Service Projects to Exclude
    Projects_Source = PROJECTS_D,
    Service_Projects = Table.SelectRows(Projects_Source, each [Project Type] = "Service Contract"),
    Service_Project_Numbers = Table.Distinct(Table.SelectColumns(Service_Projects, {"Project Number"})),
    
    // 3. Filter Contracts to Exclude Service Projects
    Merged_For_Filter = Table.NestedJoin(Source, {"Contract Number"}, Service_Project_Numbers, {"Project Number"}, "ServiceProjects", JoinKind.LeftAnti),
    Filtered_Agreements = Table.RemoveColumns(Merged_For_Filter, {"ServiceProjects"}),

    // 4. Explode Years based on Wscontsq
    Add_Year_List = Table.AddColumn(Filtered_Agreements, "YearIndex", each List.Numbers(1, if [Wscontsq] = null or [Wscontsq] < 1 then 1 else [Wscontsq])),
    Expanded_Years = Table.ExpandListColumn(Add_Year_List, "YearIndex"),

    // 5. Create Keys
    Add_Customer_Key = Table.AddColumn(Expanded_Years, "Customer Key Full", each [Custnmbr] & [Source], type text),
    Add_Agreement_Key = Table.AddColumn(Add_Customer_Key, "AgreementKey", each [Customer Key Full] & "_" & [Contract Number] & "_" & Text.From([YearIndex]), type text),

    // 6. Set Types
    Typed_Final = Table.TransformColumnTypes(Add_Agreement_Key, {{"AgreementKey", type text}, {"YearIndex", Int64.Type}}),

    // 7. Group by AgreementKey to Deduplicate (Master/Servant Aggregation)
    Grouped_Agreements = Table.Group(Typed_Final, {"AgreementKey"}, {
        {"Contract Number", each List.Max([Contract Number]), type nullable text},
        {"Customer Number", each List.Max([Custnmbr]), type nullable text},
        {"YearIndex", each List.Max([YearIndex]), type nullable number},
        {"Contract Description", each List.Max([Contract Description]), type nullable text},
        {"Contract Type", each List.Max([Contract Type]), type nullable text},
        {"Divisions", each List.Max([Divisions]), type nullable text},
        {"Contract Status", each List.Max([Contract Status]), type nullable text},
        {"Start Date", each List.Min([Contract Start Date]), type nullable date}, 
        {"End Date", each List.Max([Contract Expiration Date]), type nullable date},
        {"Contract Amount", each List.Sum([Contract Amount]), type nullable number},
        {"Annual Contract Value", each List.Sum([Annual Contract Value]), type nullable number}
    })
in
    Grouped_Agreements