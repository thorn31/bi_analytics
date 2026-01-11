let
    // --- Define Service Projects for exclusion ---
    Projects_Source = PROJECTS_D,
    Service_Projects = Table.SelectRows(Projects_Source, each [Project Type] = "Service Contract"),
    // Get list and Normalize to UPPERCASE
    Service_Project_Numbers = List.Transform(Table.Distinct(Table.SelectColumns(Service_Projects, {"Project Number"}))[Project Number], Text.Upper),
    
    // --- Maintenance Billing Revenue Stream ---
    Billing_Source = CONTRACT_BILLABLE_F,
    
    // Filter out Service Projects (Case Insensitive Check)
    Billing_Filtered = Table.SelectRows(Billing_Source, each not List.Contains(Service_Project_Numbers, Text.Upper([CONTRACT_NUMBER]))),

    Billing_Selected = Table.SelectColumns(Billing_Filtered, {"WENNSOFT_BILLING_DATE", "Customer_Contract_Year Key", "BILLABLE_ALL"}),
    Billing_Renamed = Table.RenameColumns(Billing_Selected, {{"WENNSOFT_BILLING_DATE", "Date"}, {"Customer_Contract_Year Key", "AgreementKey"}, {"BILLABLE_ALL", "Amount"}}),
    Billing_Typed = Table.TransformColumnTypes(Billing_Renamed, {{"Date", type date}, {"AgreementKey", type text}, {"Amount", Currency.Type}}),
    
    AGREEMENT_REVENUE_F = Table.AddColumn(Billing_Typed, "Source Type", each "Agreement Billing", type text)
in
    AGREEMENT_REVENUE_F