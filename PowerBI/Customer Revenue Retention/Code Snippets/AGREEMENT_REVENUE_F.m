let
    // --- Define Service Projects for exclusion ---
    Projects_Source = PROJECTS_D,
    Service_Projects = Table.SelectRows(Projects_Source, each [Project Type] = "Service Contract"),
    Service_Project_Numbers = Table.Distinct(Table.SelectColumns(Service_Projects, {"Project Number"})),
    
    // --- Maintenance Billing Revenue Stream ---
    Billing_Source = CONTRACT_BILLABLE_F,
    // Filter out Service Projects from CONTRACT_BILLABLE_F
    Merged_For_Filter = Table.NestedJoin(Billing_Source, {"CONTRACT_NUMBER"}, Service_Project_Numbers, {"Project Number"}, "ServiceProjects", JoinKind.LeftAnti),
    Billing_Filtered = Table.RemoveColumns(Merged_For_Filter, {"ServiceProjects"}),

    Billing_Selected = Table.SelectColumns(Billing_Filtered, {"WENNSOFT_BILLING_DATE", "Customer_Contract_Year Key", "BILLABLE_ALL"}),
    Billing_Renamed = Table.RenameColumns(Billing_Selected, {{"WENNSOFT_BILLING_DATE", "Date"}, {"Customer_Contract_Year Key", "AgreementKey"}, {"BILLABLE_ALL", "Amount"}}),
    Billing_Typed = Table.TransformColumnTypes(Billing_Renamed, {{"Date", type date}, {"AgreementKey", type text}, {"Amount", Currency.Type}}),
    
    AGREEMENT_REVENUE_F = Table.AddColumn(Billing_Typed, "Source Type", each "Agreement Billing", type text)
in
    AGREEMENT_REVENUE_F