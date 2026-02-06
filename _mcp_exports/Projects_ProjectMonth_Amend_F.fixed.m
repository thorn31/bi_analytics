let
    // ----------------------------
    // Job Cost (Amend inputs at Job × Month)
    // ----------------------------
    StartDate = #date(2021, 1, 1),

    // Map Job Cost projects (Project Number = Job Number)
    JobDim = Table.SelectRows(PROJECTS_D, each [Project Type] = "Job Cost"),
    JobDimKeysRaw = Table.SelectColumns(JobDim,{"Project Number","Customer Number","Customer Key","SurrogateProjectID"}),
    JobDimKeys = Table.TransformColumns(
        JobDimKeysRaw,
        {
            {"Project Number", each if _ = null then null else Text.Upper(Text.Trim(Text.From(_))), type text},
            {"Customer Number", each if _ = null then null else Text.Upper(Text.Trim(Text.From(_))), type text}
        }
    ),
    // Fallback map: Job Number only when unique
    JobDimByJob = Table.Group(
        JobDimKeys,
        {"Project Number"},
        {
            {"Customer Key", each List.Distinct([Customer Key]), type list},
            {"SurrogateProjectID", each List.Distinct([SurrogateProjectID]), type list}
        }
    ),
    JobDimByJobUnique = Table.SelectRows(JobDimByJob, each List.Count([SurrogateProjectID]) = 1 and List.Count([Customer Key]) = 1),
    JobDimByJobFlat = Table.TransformColumns(
        JobDimByJobUnique,
        {
            {"Customer Key", each _{0}, type text},
            {"SurrogateProjectID", each _{0}, type text}
        }
    ),

    // Build JobKey -> Job Number + Customer Number bridge from JOB_MONTHLY_SUMMARY_F
    JobMapBase = Table.SelectRows(JOB_MONTHLY_SUMMARY_F, each [Period Date] >= StartDate),
    JobMapBaseSlim = Table.SelectColumns(JobMapBase,{"Job Key","Job Number","Customer Number"}),
    JobMapBaseClean = Table.TransformColumns(
        JobMapBaseSlim,
        {
            {"Job Number", each if _ = null then null else Text.Upper(Text.Trim(Text.From(_))), type text},
            {"Customer Number", each if _ = null then null else Text.Upper(Text.Trim(Text.From(_))), type text}
        }
    ),
    JobMapGrouped =
        Table.Group(
            JobMapBaseClean,
            {"Job Key"},
            {
                {"Job Number", each List.Max([Job Number]), type text},
                {"Customer Number", each List.Max([Customer Number]), type text}
            }
        ),

    // Build JobKey -> Job Number map directly from cost tables (fallback)
    CostJobMapBase =
        Table.Combine({
            Table.SelectColumns(JOB_COST_DETAILS, {"JOB_KEY","JOB_NUMBER"}),
            Table.SelectColumns(JOB_COST_FORECASTS_F, {"JOB_KEY","JOB_NUMBER"})
        }),
    CostJobMapClean = Table.TransformColumns(
        CostJobMapBase,
        {
            {"JOB_KEY", each if _ = null then null else Text.Upper(Text.Trim(Text.From(_))), type text},
            {"JOB_NUMBER", each if _ = null then null else Text.Upper(Text.Trim(Text.From(_))), type text}
        }
    ),
    CostJobMapGrouped = Table.Group(
        CostJobMapClean,
        {"JOB_KEY"},
        {{"JOB_NUMBER", each List.Max([JOB_NUMBER]), type text}}
    ),

    // Amend contract source (JOBS_D) — use Orig Contract + Confirmed CO if present
    JobsDBase = Table.SelectColumns(JOBS_D, {"Job Number","Orig Contract Amount","Confirmed Chg Order Amt","Customer Number"}, MissingField.UseNull),
    JobsDClean = Table.TransformColumns(
        JobsDBase,
        {
            {"Job Number", each if _ = null then null else Text.Upper(Text.Trim(Text.From(_))), type text},
            {"Customer Number", each if _ = null then null else Text.Upper(Text.Trim(Text.From(_))), type text}
        }
    ),

    ActualSrc = Table.SelectRows(JOB_COST_DETAILS, each Date.From([TRAN_DATE]) >= StartDate),
    ActualWithMonthEnd =
        Table.AddColumn(
            Table.SelectColumns(ActualSrc,{"JOB_KEY","TRAN_DATE","COST_AMT"}),
            "Month End",
            each Date.EndOfMonth(Date.From([TRAN_DATE])),
            type date
        ),
    ActualGrouped = Table.Group(ActualWithMonthEnd,{"JOB_KEY","Month End"},{{"ActualCost_Mo", each List.Sum([COST_AMT]), type number}}),

    FcstSrc = Table.SelectRows(JOB_COST_FORECASTS_F, each Date.From([Date]) >= StartDate),
    FcstWithMonthEnd =
        Table.AddColumn(
            Table.SelectColumns(FcstSrc,{"JOB_KEY","Date","FORECAST_COSTS"}),
            "Month End",
            each Date.EndOfMonth(Date.From([Date])),
            type date
        ),
    FcstGrouped = Table.Group(FcstWithMonthEnd,{"JOB_KEY","Month End"},{{"ForecastCost_Mo", each List.Sum([FORECAST_COSTS]), type number}}),

    // Align Actual/Forecast by Job+Month
    ActualLabeled = Table.RenameColumns(Table.AddColumn(ActualGrouped, "Kind", each "ActualCost_Mo", type text), {{"ActualCost_Mo", "Amount"}}),
    FcstLabeled = Table.RenameColumns(Table.AddColumn(FcstGrouped, "Kind", each "ForecastCost_Mo", type text), {{"ForecastCost_Mo", "Amount"}}),
    CostsCombined = Table.Combine({ActualLabeled, FcstLabeled}),
    CostsGrouped = Table.Group(CostsCombined, {"JOB_KEY","Month End","Kind"}, {{"Amount", each List.Sum([Amount]), type number}}),
    CostsPivoted = Table.Pivot(CostsGrouped, List.Distinct(CostsGrouped[Kind]), "Kind", "Amount", List.Sum),
    EnsureActual = if List.Contains(Table.ColumnNames(CostsPivoted), "ActualCost_Mo") then CostsPivoted else Table.AddColumn(CostsPivoted, "ActualCost_Mo", each 0, type number),
    EnsureForecast = if List.Contains(Table.ColumnNames(EnsureActual), "ForecastCost_Mo") then EnsureActual else Table.AddColumn(EnsureActual, "ForecastCost_Mo", each 0, type number),

    // Join to JobMap to get Job Number + Customer Number
    WithJobMap = Table.NestedJoin(EnsureForecast, {"JOB_KEY"}, JobMapGrouped, {"Job Key"}, "JM", JoinKind.LeftOuter),
    ExpandedJobMap = Table.ExpandTableColumn(WithJobMap, "JM", {"Job Number","Customer Number"}, {"Job Number","Customer Number"}),

    // Fallback: if Job Number missing from summary, get from cost tables
    WithCostJobMap = Table.NestedJoin(ExpandedJobMap, {"JOB_KEY"}, CostJobMapGrouped, {"JOB_KEY"}, "CJM", JoinKind.LeftOuter),
    ExpandedCostJobMap = Table.ExpandTableColumn(WithCostJobMap, "CJM", {"JOB_NUMBER"}, {"JOB_NUMBER_from_cost"}),
    WithJobNumFinal = Table.AddColumn(ExpandedCostJobMap, "Job Number Final", each if [Job Number] = null then [JOB_NUMBER_from_cost] else [Job Number], type text),
    WithCustNumFinal = Table.AddColumn(WithJobNumFinal, "Customer Number Final", each [Customer Number], type text),
    WithJobNumClean = Table.RemoveColumns(WithCustNumFinal, {"Job Number","Customer Number","JOB_NUMBER_from_cost"}),
    ExpandedJobNum = Table.RenameColumns(WithJobNumClean, {{"Job Number Final","Job Number"},{"Customer Number Final","Customer Number"}}),

    // Join to JOBS_D for contract amounts and customer number fallback
    WithJobsD = Table.NestedJoin(ExpandedJobNum, {"Job Number"}, JobsDClean, {"Job Number"}, "JD", JoinKind.LeftOuter),
    ExpandedJobsD = Table.ExpandTableColumn(WithJobsD, "JD", {"Orig Contract Amount","Confirmed Chg Order Amt","Customer Number"}, {"Orig Contract Amount","Confirmed Chg Order Amt","Customer Number_JOBS"}),
    WithCustomerFinal = Table.AddColumn(ExpandedJobsD, "Customer Number Final2", each if [Customer Number] = null then [Customer Number_JOBS] else [Customer Number], type text),
    WithCustomerClean = Table.RemoveColumns(WithCustomerFinal, {"Customer Number","Customer Number_JOBS"}),
    ExpandedCustomer = Table.RenameColumns(WithCustomerClean, {{"Customer Number Final2","Customer Number"}}),

    WithContract = Table.AddColumn(
        ExpandedCustomer,
        "Contract Amount",
        each
            let
                orig = try Number.From([Orig Contract Amount]) otherwise null,
                co = try Number.From([Confirmed Chg Order Amt]) otherwise null
            in
                if orig = null and co = null then null
                else (if orig = null then 0 else orig) + (if co = null then 0 else co),
        type number
    ),

    // Join to PROJECTS_D using Project Number + Customer Number, then fallback to Job Number only
    WithDimPrimary = Table.NestedJoin(WithContract, {"Job Number","Customer Number"}, JobDimKeys, {"Project Number","Customer Number"}, "D", JoinKind.LeftOuter),
    ExpandedDimPrimary = Table.ExpandTableColumn(WithDimPrimary, "D", {"Customer Key","SurrogateProjectID"}, {"Customer Key","SurrogateProjectID"}),
    WithDimFallback = Table.NestedJoin(ExpandedDimPrimary, {"Job Number"}, JobDimByJobFlat, {"Project Number"}, "D2", JoinKind.LeftOuter),
    ExpandedDimFallback = Table.ExpandTableColumn(WithDimFallback, "D2", {"Customer Key","SurrogateProjectID"}, {"Customer Key_fallback","SurrogateProjectID_fallback"}),
    WithDimFinal = Table.AddColumn(ExpandedDimFallback, "Customer Key_Final", each if [Customer Key] = null then [Customer Key_fallback] else [Customer Key], type text),
    WithDimFinal2 = Table.AddColumn(WithDimFinal, "SurrogateProjectID_Final", each if [SurrogateProjectID] = null then [SurrogateProjectID_fallback] else [SurrogateProjectID], type text),
    WithDimClean = Table.RemoveColumns(WithDimFinal2, {"Customer Key","SurrogateProjectID","Customer Key_fallback","SurrogateProjectID_fallback"}),
    ExpandedDim = Table.RenameColumns(WithDimClean, {{"Customer Key_Final","Customer Key"},{"SurrogateProjectID_Final","SurrogateProjectID"}}),

    // Compute earned revenue (Amend) per Job × Month
    JobsForCalc = Table.SelectColumns(
        ExpandedDim,
        {"Month End","Job Number","Customer Number","Customer Key","SurrogateProjectID","ActualCost_Mo","ForecastCost_Mo","Orig Contract Amount","Confirmed Chg Order Amt","Contract Amount"}
    ),
    JobsGrouped = Table.Group(
        JobsForCalc,
        {"Job Number"},
        {
            {"Data", (t) =>
                let
                    t0 = Table.Sort(t, {{"Month End", Order.Ascending}}),
                    t1 = Table.TransformColumns(t0,
                        {
                            {"ActualCost_Mo", each if _ = null then 0 else Number.From(_), type number},
                            {"ForecastCost_Mo", each if _ = null then 0 else Number.From(_), type number}
                        }
                    ),
                    actualList = List.Buffer(t1[ActualCost_Mo]),
                    forecastList = List.Buffer(t1[ForecastCost_Mo]),
                    actualCum = List.Accumulate(actualList, {}, (s,c) => s & {(if List.Count(s)=0 then 0 else List.Last(s)) + c}),
                    forecastCum = List.Accumulate(forecastList, {}, (s,c) => s & {(if List.Count(s)=0 then 0 else List.Last(s)) + c}),
                    // Match Mechanical: round cumulative forecast to cents so tiny float residue becomes 0.
                    forecastCumRounded = List.Transform(forecastCum, each if _ = null then null else Number.Round(_, 2, RoundingMode.AwayFromZero)),
                    contractList = List.RemoveNulls(t1[Contract Amount]),
                    contract = if List.Count(contractList) > 0 then contractList{0} else null,
                    earnedCum = List.Transform(List.Positions(actualCum), (i) =>
                        let
                            a = actualCum{i},
                            f = forecastCumRounded{i},
                            pct = if f = null or f = 0 then null else a / f,
                            pctCap = if pct = null then null else if pct > 1 then 1 else pct,
                            earned = if pctCap = null or contract = null then null else contract * pctCap
                        in
                            earned
                    ),
                    earnedMo = List.Transform(List.Positions(earnedCum), (i) =>
                        if i = 0 then earnedCum{0}
                        else if earnedCum{i} = null then null
                        else earnedCum{i} - (if earnedCum{i-1} = null then 0 else earnedCum{i-1})
                    ),
                    t2 = Table.AddIndexColumn(t1, "idx", 0, 1, Int64.Type),
                    t3 = Table.AddColumn(t2, "Revenue Amount", each earnedMo{[idx]}, type number),
                    t4 = Table.RemoveColumns(t3, {"idx","Contract Amount"})
                in
                    t4,
                type table
            }
        }
    ),
    JobsExpanded = Table.ExpandTableColumn(
        JobsGrouped,
        "Data",
        {"Month End","Customer Key","SurrogateProjectID","ActualCost_Mo","ForecastCost_Mo","Orig Contract Amount","Confirmed Chg Order Amt","Revenue Amount"},
        {"Month End","Customer Key","SurrogateProjectID","ActualCost_Mo","ForecastCost_Mo","Orig Contract Amount","Confirmed Chg Order Amt","Revenue Amount"}
    ),

    JobsBase =
        Table.AddColumn(
            Table.AddColumn(
                Table.AddColumn(
                    Table.AddColumn(JobsExpanded, "Project Subsegment", each "Job Cost", type text),
                    "Stream", each "Projects", type text
                ),
                "Methodology", each "Amend", type text
            ),
            "Cost Amount", each [ActualCost_Mo], type number
        ),
    JobsSelect =
        Table.SelectColumns(
            JobsBase,
            {"Month End","Customer Key","SurrogateProjectID","Project Subsegment","Stream","Methodology","Revenue Amount","Cost Amount","ActualCost_Mo","ForecastCost_Mo","Orig Contract Amount","Confirmed Chg Order Amt"}
        ),

    // ----------------------------
    // Service Project billings (same for both methodologies)
    // ----------------------------
    ServiceProjects = Table.SelectRows(PROJECTS_D, each [Project Type] = "Service Project"),
    ServiceKeys = Table.Distinct(Table.SelectColumns(ServiceProjects,{"Project Number","SurrogateProjectID"}),{"Project Number"}),
    Billing = Table.SelectRows(CONTRACT_BILLABLE_F, each [WENNSOFT_BILLING_DATE] >= StartDate),
    Joined = Table.NestedJoin(Billing, {"CONTRACT_NUMBER"}, ServiceKeys, {"Project Number"}, "P", JoinKind.Inner),
    ExpandedSP = Table.ExpandTableColumn(Joined, "P", {"SurrogateProjectID"}, {"SurrogateProjectID"}),
    WithMonthEndSP = Table.AddColumn(ExpandedSP, "Month End", each Date.EndOfMonth([WENNSOFT_BILLING_DATE]), type date),
    ServiceSlim = Table.SelectColumns(WithMonthEndSP,{"Month End","Customer Key","SurrogateProjectID","BILLABLE_ALL"}),
    ServiceGrouped = Table.Group(ServiceSlim,{"Customer Key","SurrogateProjectID","Month End"},{{"Revenue Amount", each List.Sum([BILLABLE_ALL]), type number}}),
    ServiceWithCost = Table.AddColumn(ServiceGrouped, "Cost Amount", each null, type number),
    ServiceWithInputs =
        Table.AddColumn(
            Table.AddColumn(
                Table.AddColumn(ServiceWithCost, "ActualCost_Mo", each null, type number),
                "ForecastCost_Mo", each null, type number
            ),
            "Orig Contract Amount", each null, type number
        ),
    ServiceFinal = Table.AddColumn(
        Table.AddColumn(
            Table.AddColumn(ServiceWithInputs, "Project Subsegment", each "Service Project", type text),
            "Stream", each "Projects", type text
        ),
        "Methodology", each "Amend", type text
    ),
    ServiceSelect = Table.SelectColumns(ServiceFinal,{"Month End","Customer Key","SurrogateProjectID","Project Subsegment","Stream","Methodology","Revenue Amount","Cost Amount","ActualCost_Mo","ForecastCost_Mo","Orig Contract Amount"}),

    Combined = Table.Combine({JobsSelect, ServiceSelect}),
    Typed = Table.TransformColumnTypes(
        Combined,
        {
            {"Revenue Amount", type number},
            {"Cost Amount", type number},
            {"ActualCost_Mo", type number},
            {"ForecastCost_Mo", type number},
            {"Orig Contract Amount", type number},
            {"Confirmed Chg Order Amt", type number},
            {"Month End", type date}
        }
    )
in
    Typed