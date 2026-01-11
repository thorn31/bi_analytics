let
    // --- Define Service Projects for exclusion ---
    Projects_Source = PROJECTS_D,
    Service_Projects = Table.SelectRows(Projects_Source, each [Project Type] = "Service Contract"),
    Service_Project_Numbers = Table.Distinct(Table.SelectColumns(Service_Projects, {"Project Number"})),
    
    // --- Maintenance Call Stream (Costs) ---
    Calls_Source = CALLS_F,
    // Filter out Service Projects from CALLS_F and ensure Contract Number is not null
    Calls_Filtered_ServiceProjects = Table.SelectRows(Calls_Source, each not List.Contains(Service_Project_Numbers[Project Number], [Contract Number])),
    Calls_Filtered_NonContract = Table.SelectRows(Calls_Filtered_ServiceProjects, each [Contract Number] <> null and [Contract Number] <> ""),

    // --- Maintenance Call Costs Stream ---
    Call_Cost_Selected = Table.SelectColumns(Calls_Filtered_NonContract, {"Date Of Service Call", "Customer_Contract_Year Key", "Cost All"}),
    Call_Cost_Renamed = Table.RenameColumns(Call_Cost_Selected, {{"Date Of Service Call", "Date"}, {"Customer_Contract_Year Key", "AgreementKey"}, {"Cost All", "Amount"}}),
    Call_Cost_Typed = Table.TransformColumnTypes(Call_Cost_Renamed, {{"Date", type date}, {"AgreementKey", type text}, {"Amount", Currency.Type}}),
    
    SERVCONTRACTS_COSTS_F = Table.AddColumn(Call_Cost_Typed, "Source Type", each "Contract Call Cost", type text)
in
    SERVCONTRACTS_COSTS_F