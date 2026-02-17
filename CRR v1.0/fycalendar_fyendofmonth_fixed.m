let
    // The FiscalYearEnd determines in which month the fiscal year ends. If necessary you can adjust it. 
    FiscalYearEnd = 9,

    // Today is used throughout the fiscal logic and for determining current period flags
    Today = Date.From(DateTime.LocalNow()),

    // Sets the start date for your calendar
    StartDate = #date(2000, 1, 1),

    // The calendar runs until the end of the current year. Change this if you need your calendar to run to another date. 
    EndDate = Date.AddYears(Date.EndOfYear(Today),1),

    // The current Fiscal Year value is a helper value for other calculations
    CurrentFiscalYear = Date.Year( Date.AddMonths( Today, 12 - FiscalYearEnd ) ),

    ListOfDates =
        List.Dates(
            StartDate,
            Duration.Days(EndDate - StartDate) + 1,
            #duration(1, 0, 0, 0)
        ),

    MyDateTable =
        Table.FromList(
            ListOfDates,
            Splitter.SplitByNothing(),
            type table[Date = date],
            null,
            ExtraValues.Error
        ),

    Add_FiscalYearNumber =
        Table.AddColumn(
            MyDateTable,
            "FiscalYear",
            each Date.Year(Date.AddMonths([Date], 12 - FiscalYearEnd)),
            Int64.Type
        ),

    Add_FiscalYearLabel =
        Table.AddColumn(
            Add_FiscalYearNumber,
            "FiscalYearLabel",
            each "FY" & Text.From([FiscalYear]),
            Text.Type
        ),

    Add_FiscalYearDefault =
        Table.AddColumn(
            Add_FiscalYearLabel,
            "FiscalYearDefault",
            each
                if [FiscalYear] = CurrentFiscalYear then "Current"
                else if [FiscalYear] = (CurrentFiscalYear - 1) then "Previous"
                else "FY" & Text.From([FiscalYear]),
            Text.Type
        ),

    Add_FiscalStartOfYear =
        Table.AddColumn(
            Add_FiscalYearDefault,
            "FiscalStartOfYear",
            each [
                Offset = if FiscalYearEnd = 12 then 0 else FiscalYearEnd - 12,
                FiscalStartOfYear = Date.AddMonths(Date.StartOfYear([Date]), Offset)
            ][FiscalStartOfYear],
            Date.Type
        ),

    Add_FiscalEndOfYear =
        Table.AddColumn(
            Add_FiscalStartOfYear,
            "FiscalEndOfYear",
            each Date.AddMonths(Date.EndOfYear([Date]), FiscalYearEnd - 12),
            Date.Type
        ),

    Add_FiscalDayOfYear =
        Table.AddColumn(
            Add_FiscalEndOfYear,
            "FiscalDayOfYear",
            each Number.From([Date] - [FiscalStartOfYear]) + 1,
            Int64.Type
        ),

    Add_FiscalWeekOfYear =
        Table.AddColumn(
            Add_FiscalDayOfYear,
            "FiscalWeekOfYear",
            each Number.RoundUp([FiscalDayOfYear] / 7),
            Int64.Type
        ),

    Add_FiscalWeekLabel =
        Table.AddColumn(
            Add_FiscalWeekOfYear,
            "FiscalWeekLabel",
            each
                "FY" &
                Text.From([FiscalYear]) &
                " W" &
                Text.PadStart(Text.From([FiscalWeekOfYear]), 2, "0"),
            Text.Type
        ),

    Add_FiscalYearOffset =
        Table.AddColumn(
            Add_FiscalWeekLabel,
            "FiscalYearOffset",
            each ([FiscalYear] - CurrentFiscalYear),
            Int64.Type
        ),

    Add_FiscalMonthNumber =
        Table.AddColumn(
            Add_FiscalYearOffset,
            "FiscalMonth",
            each Date.Month(Date.AddMonths([Date], -FiscalYearEnd)),
            Int64.Type
        ),

    // >>> ADD THIS: Fiscal End Of Month (fiscal month boundary)
    Add_FiscalEndOfMonth =
        Table.AddColumn(
            Add_FiscalMonthNumber,
            "FiscalEndOfMonth",
            each Date.EndOfMonth([Date]),
            Date.Type
        ),

    Add_FiscalMonthDefault =
        Table.AddColumn(
            Add_FiscalEndOfMonth,
            "FiscalMonthDefault",
            each
                if Date.IsInCurrentMonth([Date]) then "Current"
                else if Date.IsInPreviousMonth([Date]) then "Previous"
                else Text.From([FiscalMonth]),
            Text.Type
        ),

    Add_FiscalQuarterNumber =
        Table.AddColumn(
            Add_FiscalMonthDefault,
            "FiscalQuarter",
            each Number.RoundUp([FiscalMonth] / 3),
            Int64.Type
        ),

    Add_FiscalQuarterLabel =
        Table.AddColumn(
            Add_FiscalQuarterNumber,
            "FiscalQuarterLabel",
            each "FQ" & Text.From([FiscalQuarter]),
            Text.Type
        ),

    Add_FiscalMonthOfQuarter =
        Table.AddColumn(
            Add_FiscalQuarterLabel,
            "FiscalMonthOfQuarter",
            each [FiscalMonth] - 3 * ([FiscalQuarter] - 1),
            Int64.Type
        ),

    Add_FiscalYearQuarterLabel =
        Table.AddColumn(
            Add_FiscalMonthOfQuarter,
            "FiscalYearQuarterLabel",
            each "FY" & Text.From([FiscalYear]) & " Q" & Text.From([FiscalQuarter]),
            Text.Type
        ),

    Add_FiscalStartOfQuarter =
        Table.AddColumn(
            Add_FiscalYearQuarterLabel,
            "FiscalStartOfQuarter",
            each Date.StartOfMonth(Date.AddMonths([Date], 1 - [FiscalMonthOfQuarter])),
            Date.Type
        ),

    Add_FiscalEndOfQuarter =
        Table.AddColumn(
            Add_FiscalStartOfQuarter,
            "FiscalEndOfQuarter",
            each Date.EndOfMonth(Date.AddMonths([Date], 3 - [FiscalMonthOfQuarter])),
            Date.Type
        ),

    Add_FiscalQuarterOffset =
        Table.AddColumn(
            Add_FiscalEndOfQuarter,
            "FiscalQuarterOffset",
            each [
                CurrentFiscalMonth = Date.Month(Date.AddMonths(Today, -FiscalYearEnd)),
                CurrentFiscalQuarter = Number.RoundUp(CurrentFiscalMonth / 3),
                FiscalQuarterOffset =
                    (([FiscalYear] - CurrentFiscalYear) * 4)
                        + ([FiscalQuarter] - CurrentFiscalQuarter)
            ][FiscalQuarterOffset],
            Int64.Type
        ),

    Add_FiscalQuarterMonthLabel =
        Table.AddColumn(
            Add_FiscalQuarterOffset,
            "FiscalQuarterMonthLabel",
            each
                "FQ"
                    & Text.From([FiscalQuarter])
                    & ": "
                    & Date.ToText([FiscalStartOfQuarter], "MMM yyyy")
                    & " - "
                    & Date.ToText([FiscalEndOfQuarter], "MMM yyyy"),
            Text.Type
        ),

    Add_FiscalDayOfQuarter =
        Table.AddColumn(
            Add_FiscalQuarterMonthLabel,
            "FiscalDayOfQuarter",
            each Number.From([Date] - [FiscalStartOfQuarter]) + 1,
            Int64.Type
        ),

    Add_IsCurrentMonth =
        Table.AddColumn(
            Add_FiscalDayOfQuarter,
            "IsCurrentMonth",
            each Date.Year([Date]) = Date.Year(Today)
                and Date.Month([Date]) = Date.Month(Today),
            type logical
        ),

    Add_IsCurrentCalendarYear =
        Table.AddColumn(
            Add_IsCurrentMonth,
            "IsCurrentCalendarYear",
            each Date.Year([Date]) = Date.Year(Today),
            type logical
        ),

    Add_IsCurrentFiscalYear =
        Table.AddColumn(
            Add_IsCurrentCalendarYear,
            "IsCurrentFiscalYear",
            each [FiscalYear] = CurrentFiscalYear,
            type logical
        ),

    CurrentWeekStart =
        Date.AddDays(Today, 1 - Date.DayOfWeek(Today, Day.Monday)),

    Add_WeekStart =
        Table.AddColumn(
            Add_IsCurrentFiscalYear,
            "WeekStart",
            each Date.AddDays([Date], 1 - Date.DayOfWeek([Date], Day.Monday)),
            type date
        ),

    Add_IsCurrentWeek =
        Table.AddColumn(
            Add_WeekStart,
            "IsCurrentWeek",
            each [WeekStart] = CurrentWeekStart,
            type logical
        ),

    Add_IsPreviousMonth =
        Table.AddColumn(
            Add_IsCurrentWeek,
            "IsPreviousMonth",
            each Date.IsInPreviousMonth([Date]),
            type logical
        ),

    Add_IsPreviousFiscalYear =
        Table.AddColumn(
            Add_IsPreviousMonth,
            "IsPreviousFiscalYear",
            each [FiscalYear] = (CurrentFiscalYear - 1),
            type logical
        ),

    PreviousWeekStart =
        Date.AddDays(Today, 1 - Date.DayOfWeek(Today, Day.Monday) - 7),

    Add_IsPreviousWeek =
        Table.AddColumn(
            Add_IsPreviousFiscalYear,
            "IsPreviousWeek",
            each [WeekStart] = PreviousWeekStart,
            type logical
        ),

    Add_FiscalMonthName =
        Table.AddColumn(
            Add_IsPreviousWeek,
            "FiscalMonthName",
            each "FM" & Text.PadStart(Text.From([FiscalMonth]), 2, "0"),
            Text.Type
        ),

    Add_FiscalMonthNameLong =
        Table.AddColumn(
            Add_FiscalMonthName,
            "FiscalMonthNameLong",
            each "FM" & Text.PadStart(Text.From([FiscalMonth]), 2, "0") 
                & " - " & Date.MonthName([Date]),
            Text.Type
        ),

    Add_FiscalWeekName =
        Table.AddColumn(
            Add_FiscalMonthNameLong,
            "FiscalWeekName",
            each "FW" & Text.PadStart(Text.From([FiscalWeekOfYear]), 2, "0"),
            Text.Type
        ),

    #"Rename Columns" =
        Table.TransformColumnNames(
            Add_FiscalWeekName,
            each [
                SplitTextByTransition =
                    Splitter.SplitTextByCharacterTransition({"a" .. "z"}, {"A" .. "Z"})(_),
                CombineValues = Text.Combine(SplitTextByTransition, " "),
                RemoveUnderscores = Text.Replace(CombineValues, "_", " ")
            ][RemoveUnderscores]
        ),

    #"Inserted Month Name" =
        Table.AddColumn(#"Rename Columns", "Month Name", each Date.MonthName([Date]), type text),
    #"Added Custom" = Table.AddColumn(#"Inserted Month Name", "MMM Label", each Text.Start([Month Name], 3)),
    Add_IsCompletedMonth = Table.AddColumn(#"Added Custom", "Is Completed Month", each Date.EndOfMonth([Date]) < Date.StartOfMonth(Date.From(DateTime.LocalNow())), type logical),
    #"Added Custom1" = Table.AddColumn(Add_IsCompletedMonth, "Is Completed Quarter", each [Fiscal End Of Quarter] < Date.From(DateTime.LocalNow()), type logical)

in
    #"Added Custom1"