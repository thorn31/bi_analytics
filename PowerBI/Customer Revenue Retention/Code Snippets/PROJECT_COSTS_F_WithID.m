let
    //
    // ==========================================
    //     JOB COST STREAM (From JOB_FINANCIALS_F)
    // ==========================================
    //
    Job_Cost_Source =
        JOB_FINANCIALS_F,   // Table containing Monthly Cost + Job Earned Revenue

    Job_Cost_Slim =
        Table.SelectColumns(
            Job_Cost_Source,
            {"Period Date", "SurrogateProjectID", "Monthly Cost"}
        ),

    Job_Cost_Renamed =
        Table.RenameColumns(
            Job_Cost_Slim,
            {
                {"Period Date", "Date"},
                {"Monthly Cost", "Amount"}
            }
        ),

    Job_Cost_Typed =
        Table.TransformColumnTypes(
            Job_Cost_Renamed,
            {
                {"Date", type date},
                {"SurrogateProjectID", type text},
                {"Amount", Currency.Type}
            }
        ),

    Job_Cost_Label =
        Table.AddColumn(
            Job_Cost_Typed,
            "Source Type",
            each "Job Cost",
            type text
        ),

    // Add NULL Service Call Id to match schema
    Job_Cost_Final = 
        Table.AddColumn(
            Job_Cost_Label,
            "Service Call Id",
            each null,
            type text
        ),


    //
    // ==========================================
    //     SERVICE PROJECT COST STREAM
    // ==========================================
    //

    // Filter PROJECTS_D for service contracts
    Service_Projects =
        Table.SelectRows(
            PROJECTS_D,
            each [Project Type] = "Service Contract"
        ),

    // Keep the surrogate key + project number for joining
    Service_Project_Keys =
        Table.SelectColumns(
            Service_Projects,
            {"Project Number", "SurrogateProjectID"}
        ),

    // Slim CALLS_F table
    Calls_Slim =
        Table.SelectColumns(
            CALLS_F,
            {
                "Date Of Service Call",
                "Contract Number",
                "Cost All",
                "Service Call Id" // Added ID
            }
        ),

    // Fast JOIN
    Joined =
        Table.NestedJoin(
            Calls_Slim,
            {"Contract Number"},
            Service_Project_Keys,
            {"Project Number"},
            "Matched",
            JoinKind.Inner
        ),

    // Expand key fields from PROJECTS_D
    Expanded =
        Table.ExpandTableColumn(
            Joined,
            "Matched",
            {"SurrogateProjectID"},
            {"SurrogateProjectID"}
        ),

    // Cleanup and type transform
    Cleaned =
        Table.TransformColumnTypes(
            Table.RenameColumns(
                Expanded,
                {
                    {"Date Of Service Call", "Date"},
                    {"Cost All", "Amount"}
                }
            ),
            {
                {"Date", type date},
                {"SurrogateProjectID", type text},
                {"Amount", Currency.Type},
                {"Service Call Id", type text}
            }
        ),

    // Add source label
    Service_Cost_Final =
        Table.AddColumn(
            Cleaned,
            "Source Type",
            each "Service Call Cost",
            type text
        ),

    // Final column selection
    Service_Cost_Formatted =
        Table.SelectColumns(
            Service_Cost_Final,
            {
                "Date",
                "SurrogateProjectID",
                "Amount",
                "Source Type",
                "Service Call Id" // Keep ID
            }
        ),


    //
    // ==========================================
    //          COMBINE BOTH STREAMS
    // ==========================================
    //
    FACT_UNIFIED_COSTS =
        Table.Combine({
            Job_Cost_Final,
            Service_Cost_Formatted
        })
in
    FACT_UNIFIED_COSTS