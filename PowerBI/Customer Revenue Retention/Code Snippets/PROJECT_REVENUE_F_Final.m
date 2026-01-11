let
    //
    // ============================
    //     JOB REVENUE STREAM
    // ============================
    //
    Job_Revenue =
        let
            // Select needed columns including Customer Key + Number
            Slim =
                Table.SelectColumns(
                    JOB_FINANCIALS_F,
                    {
                        "Period Date",
                        "SurrogateProjectID",
                        "Customer Number",
                        "Customer Key",
                        "Contract Earned Curr Mo"
                    }
                ),

            Renamed =
                Table.RenameColumns(
                    Slim,
                    {
                        {"Period Date", "Date"},
                        {"Contract Earned Curr Mo", "Amount"}
                    }
                ),

            Typed =
                Table.TransformColumnTypes(
                    Renamed,
                    {
                        {"Date", type date},
                        {"SurrogateProjectID", type text},
                        {"Customer Number", type text},
                        {"Customer Key", type text},
                        {"Amount", Currency.Type}
                    }
                ),

            WithType =
                Table.AddColumn(
                    Typed,
                    "Source Type",
                    each "Job Earned",
                    type text
                )
        in
            WithType,


    //
    // ============================
    //   SERVICE PROJECT REVENUE
    // ============================
    //

    // Filter PROJECTS_D to only service contracts
    Service_Projects =
        Table.SelectRows(
            PROJECTS_D,
            each [Project Type] = "Service Contract"
        ),

    // Keep Project Number, SurrogateProjectID, Customer Number, Customer Key
    Service_Project_Keys =
        Table.SelectColumns(
            Service_Projects,
            {
                "Project Number",
                "SurrogateProjectID",
                "Customer Number",
                "Customer Key"
            }
        ),

    // --- DEDUPLICATION STEP ---
    // Prevent Fan-Out by ensuring unique Project Numbers
    Service_Project_Unique = 
        Table.Distinct(
            Service_Project_Keys, 
            {"Project Number"}
        ),

    // Slim billing table for performance
    Billing_Slim =
        Table.SelectColumns(
            CONTRACT_BILLABLE_F,
            {
                "WENNSOFT_BILLING_DATE",
                "CONTRACT_NUMBER",
                "BILLABLE_ALL"
            }
        ),

    // Join billing rows to DEDUPLICATED PROJECTS_D slice
    Joined =
        Table.NestedJoin(
            Billing_Slim,
            {"CONTRACT_NUMBER"},
            Service_Project_Unique,
            {"Project Number"},
            "Matched",
            JoinKind.Inner
        ),

    // Expand: Project Number, SurrogateProjectID, Customer Number, Customer Key
    Expanded =
        Table.ExpandTableColumn(
            Joined,
            "Matched",
            {
                "Project Number",
                "SurrogateProjectID",
                "Customer Number",
                "Customer Key"
            },
            {
                "Project Number",
                "SurrogateProjectID",
                "Customer Number",
                "Customer Key"
            }
        ),

    // Rename + type
    Cleaned =
        Table.TransformColumnTypes(
            Table.RenameColumns(
                Expanded,
                {
                    {"WENNSOFT_BILLING_DATE", "Date"},
                    {"BILLABLE_ALL", "Amount"}
                }
            ),
            {
                {"Date", type date},
                {"Project Number", type text},
                {"SurrogateProjectID", type text},
                {"Customer Number", type text},
                {"Customer Key", type text},
                {"Amount", Currency.Type}
            }
        ),

    // Add source label
    Service_Revenue_Final =
        Table.AddColumn(
            Cleaned,
            "Source Type",
            each "Service Billing",
            type text
        ),

    // Unified schema output
    Service_Revenue_Formatted =
        Table.SelectColumns(
            Service_Revenue_Final,
            {
                "Date",
                "SurrogateProjectID",
                "Customer Number",
                "Customer Key",
                "Amount",
                "Source Type"
            }
        ),


    //
    // ============================
    //   COMBINE STREAMS
    // ============================
    //
    PROJECT_REVENUE_F =
        Table.Combine({
            Job_Revenue,
            Service_Revenue_Formatted
        })
in
    PROJECT_REVENUE_F