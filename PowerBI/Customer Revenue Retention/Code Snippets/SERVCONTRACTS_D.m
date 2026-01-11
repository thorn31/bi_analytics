let
    // 1. Get Source Data
    Source = CONTRACTS_D, // Assumes this is the raw Snowflake table query
    
    // 2. Identify Service Projects to Exclude
    Projects_Source = PROJECTS_D,
    Service_Projects = Table.SelectRows(Projects_Source, each [Project Type] = "Service Contract"),
    Service_Project_Numbers = Table.Distinct(Table.SelectColumns(Service_Projects, {"Project Number"})),
    
    // 3. Filter Contracts to Exclude Service Projects
    // We use a Left Anti Join approach for speed (better than List.Contains for large sets)
    Merged_For_Filter = Table.NestedJoin(Source, {"Contract Number"}, Service_Project_Numbers, {"Project Number"}, "ServiceProjects", JoinKind.LeftAnti),
    Filtered_Agreements = Table.RemoveColumns(Merged_For_Filter, {"ServiceProjects"}),

    // 4. Explode Years based on Wscontsq
    // Handle nulls in Wscontsq by defaulting to 1 year
    Add_Year_List = Table.AddColumn(Filtered_Agreements, "YearIndex", each List.Numbers(1, if [Wscontsq] = null or [Wscontsq] < 1 then 1 else [Wscontsq])),
    Expanded_Years = Table.ExpandListColumn(Add_Year_List, "YearIndex"),

    // 5. Create Keys
    // Customer Key construction: Custnmbr + Source (e.g., "123" + "SERV_GP" -> "123SERV_GP")
    // Agreement Key construction: Customer Key + "_" + Contract + "_" + YearIndex
    Add_Customer_Key = Table.AddColumn(Expanded_Years, "Customer Key Full", each [Custnmbr] & [Source], type text),
    Add_Agreement_Key = Table.AddColumn(Add_Customer_Key, "AgreementKey", each [Customer Key Full] & "_" & [Contract Number] & "_" & Text.From([YearIndex]), type text),

    // 6. Set Types
    Typed_Final = Table.TransformColumnTypes(Add_Agreement_Key, {{"AgreementKey", type text}, {"YearIndex", Int64.Type}})
in
    Typed_Final