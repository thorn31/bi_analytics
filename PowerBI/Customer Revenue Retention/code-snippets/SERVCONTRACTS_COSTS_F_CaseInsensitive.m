let
    // --- Define Service Projects for exclusion ---
    Projects_Source = PROJECTS_D,
    Service_Projects = Table.SelectRows(Projects_Source, each [Project Type] = "Service Contract"),
    // Get list and Normalize to UPPERCASE
    Service_Project_Numbers = List.Transform(Table.Distinct(Table.SelectColumns(Service_Projects, {"Project Number"}))[Project Number], Text.Upper),
    
    // --- Maintenance Call Stream (Costs) ---
    Calls_Source = CALLS_F,
    
    // Filter out Service Projects (Case Insensitive) and ensure Contract Number is not null
    Calls_Filtered_ServiceProjects = Table.SelectRows(Calls_Source, each 
        ([Contract Number] <> null and [Contract Number] <> "") and 
        not List.Contains(Service_Project_Numbers, Text.Upper([Contract Number]))
    ),

    // --- Maintenance Call Costs Stream ---
    Call_Cost_Selected = Table.SelectColumns(Calls_Filtered_ServiceProjects, {"Date Of Service Call", "Customer_Contract_Year Key", "Cost All"}),
    Call_Cost_Renamed = Table.RenameColumns(Call_Cost_Selected, {{"Date Of Service Call", "Date"}, {"Customer_Contract_Year Key", "AgreementKey"}, {"Cost All", "Amount"}}),
    Call_Cost_Typed = Table.TransformColumnTypes(Call_Cost_Renamed, {{"Date", type date}, {"AgreementKey", type text}, {"Amount", Currency.Type}}),
    
    SERVCONTRACTS_COSTS_F = Table.AddColumn(Call_Cost_Typed, "Source Type", each "Contract Call Cost", type text)
in
    SERVCONTRACTS_COSTS_F