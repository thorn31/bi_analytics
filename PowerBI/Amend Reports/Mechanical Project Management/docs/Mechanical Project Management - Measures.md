# Mechanical Project Management — Measures

Generated: 2026-01-22 14:36 EST

## Revenue Measures (focus)
Measures table: `Revenue Measures` (42 measures)

| Measure | Depends on measures | Depends on columns |
|---|---|---|
| `Original Contract` | JOB_NUMBER, ORIG_CONTRACT_AMOUNT | JOB[JOB_NUMBER], JOB[ORIG_CONTRACT_AMOUNT] |
| `Cumulative Revenue` | % Complete, Current Contract Amount | Cost Measures[% Complete] |
| `Current Contract Amount` | Cumulative CO$, Original Contract |  |
| `Forecasted GP $` | Cumulative Forecast, Current Contract Amount |  |
| `Forecasted GP%` | Current Contract Amount, Forecasted GP $ |  |
| `Change Order $` | CHANGE_ORDER_EST_COST, CO, JOB_NUMBER | CHANGE_ORDERS_BY_MONTH[CHANGE_ORDER_EST_COST], JOB[JOB_NUMBER] |
| `Estimated GP $` | Current Contract Amount, Original Cost Estimate |  |
| `Estimated GP%` | Current Contract Amount, Estimated GP $ |  |
| `Cumulative Revenue YTD` | Cumulative Revenue, Fiscal Year, Max Date | Calendar[Fiscal Year] |
| `Cumulative Rev Amount Across Jobs YTD` | Cumulative Revenue YTD, JOB_NUMBER, contract | JOB[JOB_NUMBER] |
| `Change Order $2` | CONFIRMED_CHG_ORDER_AMT, JOB_NUMBER | JOB[CONFIRMED_CHG_ORDER_AMT], JOB[JOB_NUMBER] |
| `Cumulative CO$` | Change Order $, Date, Max Date | Calendar[Date] |
| `Forecasted GP$ Across Jobs` | Estimated GP $, Forecasted GP $, JOB_NUMBER, contract | JOB[JOB_NUMBER] |
| `Cumulative Current Contract` | Current Contract Amount, JOB_NUMBER, contract | JOB[JOB_NUMBER] |
| `Forecasted GP% Across Jobs` | Cumulative Current Contract, Forecasted GP$ Across Jobs |  |
| `Estimated GP$ Across Jobs` | Estimated GP $, JOB_NUMBER, contract | JOB[JOB_NUMBER] |
| `Cumulative Original Contract` | JOB_NUMBER, Original Contract, contract | JOB[JOB_NUMBER] |
| `Estimated GP% Across Jobs` | Cumulative Current Contract, Estimated GP$ Across Jobs |  |
| `Cumulative Rev Amount Across Jobs` | Cumulative Revenue, JOB_NUMBER, contract | JOB[JOB_NUMBER] |
| `Revenue YTD` | Fiscal Year, Max Date, Net Earned Rev Amount Across Jobs | Calendar[Fiscal Year] |
| `Net Earned Revenue` | Actual Cost, Cumulative Forecast, Current Contract Amount | Cost Measures[Actual Cost] |
| `Net Earned Rev Amount Across Jobs` | JOB_NUMBER, Net Earned Revenue, contract | JOB[JOB_NUMBER] |
| `Revenue LY YTD` | Date, Fiscal Year, Max Date, Net Earned Rev Amount Across Jobs, Revenue YTD | Calendar[Date], Calendar[Fiscal Year] |
| `Net Earned Rev Amount TM` | Date, Max Date, Net Earned Rev Amount Across Jobs, Running Total Month | Calendar[Date], Calendar[Running Total Month], Revenue Measures[Net Earned Rev Amount Across Jobs] |
| `Net Earned Rev Amount LM` | Date, Max Date, Net Earned Rev Amount Across Jobs, Running Total Month | Calendar[Date], Calendar[Running Total Month], Revenue Measures[Net Earned Rev Amount Across Jobs] |
| `Revenue Change` | JOB_NUMBER, Net Earned Rev Amount LM, Net Earned Rev Amount TM, contract, lm | JOB[JOB_NUMBER], Revenue Measures[Net Earned Rev Amount LM], Revenue Measures[Net Earned Rev Amount TM] |
| `Forecasted to Est GP Variance $` | Estimated GP $, Forecasted GP $ |  |
| `Forecasted GP $ TM to LM` | Cumulative Forecast, Current Contract Amount, Date, Max Date, Running Total Month | Calendar[Date], Calendar[Running Total Month], Cost Measures[Cumulative Forecast] |
| `Forecast to Est GP Variance %` | Estimated GP $, Forecasted GP $ |  |
| `GP% Difference` | Estimated GP%, Estimated GP% Across Jobs, Forecasted GP%, Forecasted GP% Across Jobs |  |
| `Cumulative Billed Amount` | ACCOUNT_AMOUNT, Date, Max Date | Calendar[Date], INVOICES[ACCOUNT_AMOUNT] |
| `Over - Under Billed` | Cumulative Billed Amount, Cumulative Revenue |  |
| `Over Under Billed Across Jobs` | JOB_NUMBER, Over - Under Billed, contract | JOB[JOB_NUMBER] |
| `Over / (Under) Billed Cumulative Across Jobs` | Date, Max Date, Over Under Billed Across Jobs | Calendar[Date] |
| `Cumulative Over Under Billed Amount Across Jobs LM` | Date, Max Date, Over Under Billed Across Jobs, Running Total Month | Calendar[Date], Calendar[Running Total Month] |
| `Count Under Billed Jobs` | JOB_NUMBER, Over - Under Billed, Under Billed | JOB[JOB_NUMBER] |
| `test` | Net Earned Rev Amount Across Jobs, Revenue Rolling 12 | Revenue Measures[Revenue Rolling 12] |
| `Revenue Rolling 12` | Date, Max Date, Net Earned Rev Amount Across Jobs, Running Total Month | Calendar[Date], Calendar[Running Total Month], Revenue Measures[Net Earned Rev Amount Across Jobs] |
| `Revenue Rolling 12 PY` | Date, Max Date, Net Earned Rev Amount Across Jobs, Running Total Month | Calendar[Date], Calendar[Running Total Month] |
| `Actual GP$` | % Complete, Actual Cost, Current Contract Amount |  |
| `Actual GP$ Across Jobs` | Actual GP$, JOB_NUMBER, contract | JOB[JOB_NUMBER] |
| `Display TM to LM Forecasted Change` | Forecasted GP $ TM to LM |  |

## Full Measure Catalog

### Backlog Measures

#### Cost to Complete - Backlog
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	//sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "Proj", [Cumulative Forecast], "Actual", 'Cost Measures'[Cumulative Actual Cost]), [Proj] - [Actual] )

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "Proj", [Available Budget]), [Proj]  )
```

#### Actual Monthly Cost (GL)
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
//[Actual Cost] 

calculate(sum('GL POSTING'[PERDBLNC]), filter('GL POSTING', 'GL POSTING'[ACTNUMBR_1] = "340"))
```

#### Average Cost (Prior 6 Mo)
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
DIVIDE(CALCULATE([Actual Monthly Cost (GL)], FILTER(ALL('Calendar'), 'Calendar'[Running Total Month] <= MAX('Calendar'[Running Total Month]) - 1 && 'Calendar'[Running Total Month] >= MAX('Calendar'[Running Total Month]) - 6)), 6, BLANK())
```

#### Backlog Months
```dax
DIVIDE([Available Budget], [Average Cost (Prior 6 Mo)] , BLANK())
```

#### Backlog TM
- Format string: `0.0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	

	return

	calculate([Backlog Months], filter(all('Calendar'), 'Calendar'[Running Total Month] = runtot))
```

#### Backlog LM
- Format string: `0.0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	var lm = runtot - 1

	return

	calculate([Backlog Months], filter(all('Calendar'), 'Calendar'[Running Total Month] = lm))
```

#### Cost of Contract Rev TM
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	

	return

	calculate([Actual Monthly Cost (GL)], filter(all('Calendar'), 'Calendar'[Running Total Month] = runtot))
```

#### Cost to Complete LM
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	var lm = runtot - 1

	return

	calculate([Available Budget], filter(all('Calendar'), 'Calendar'[Running Total Month] = lm))
```

#### GL Revenue
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
calculate([Amount], filter('GL POSTING', 'GL POSTING'[ACCOUNT_TYPE] = "REVENUE"))* -1
```

#### Amount
```dax
sum('GL POSTING'[PERDBLNC])
```

#### GL Equipment and Material
```dax
calculate([Amount], filter('GL POSTING', 'GL POSTING'[ACCOUNT_TYPE] = "EQUIP & MATERIAL"))
```

#### GL Labor
```dax
calculate([Amount], filter('GL POSTING', 'GL POSTING'[ACCOUNT_TYPE] = "LABOR & BURDEN"))
```

#### GL Subcontract
```dax
calculate([Amount], filter('GL POSTING', 'GL POSTING'[ACCOUNT_TYPE] = "SUBCONTRACT"))
```

#### GL Operations Expense
```dax
calculate([Amount], filter('GL POSTING', 'GL POSTING'[ACCOUNT_TYPE] = "OPERATIONS EXPENSE"))
```

#### GL Vehicle
```dax
calculate([Amount], filter('GL POSTING', 'GL POSTING'[ACCOUNT_TYPE] = "Vehicle"))
```

#### GL Discounts
```dax
calculate([Amount], filter('GL POSTING', 'GL POSTING'[ACCOUNT_TYPE] = "Discounts"))
```

#### Actual GP
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[GL Revenue] - [GL Equipment and Material] -[GL Labor] -  [GL Subcontract] - [GL Operations Expense] - [GL Vehicle] - [GL Discounts]
```

#### Backlog $ Deferred_Table
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE], "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date]), "Rev", [Cumulative Rev Amount Across Jobs], "Contract", [Backlog_Cumulative Current Contract]), if( JOB[TARGET_COMPLETION_DATE] >= today() && [Start Date] > today() , [Contract] - [Rev] , blank()))
```

#### Backlog $_Table
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE], "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date]), "Rev", [Cumulative Rev Amount Across Jobs], "Contract", [Backlog_Cumulative Current Contract]), if( JOB[TARGET_COMPLETION_DATE] >= today() , [Contract] - [Rev] , blank()))
```

#### Backlog Months_Contract
- Format string: `#,0.00`
```dax
	

	//minx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE], "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date])), if([Start Date] <= Today() && [Start Date] <= min('Calendar'[Date]) && JOB[TARGET_COMPLETION_DATE] >= today() , divide(DATEDIFF( today(), JOB[TARGET_COMPLETION_DATE],  Day), 30), blank()))

	minx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE], "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date])), if([Start Date] <= Today() && [Start Date] <= min('Calendar'[Date]) && JOB[TARGET_COMPLETION_DATE] >= today() , divide(DATEDIFF( today(), JOB[TARGET_COMPLETION_DATE],  Day), 30), if([Start Date] > today() && [TARGET_COMPLETION_DATE] >= today(), divide(DATEDIFF([Start Date], JOB[TARGET_COMPLETION_DATE], DAY), 30), blank())))
```

#### Backlog_Cumulative Current Contract
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE], "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date]), "contract", [Current Contract Amount]), 

//if(min('Calendar'[Date]) >= [Start Date], [contract], 0))

[contract])
```

#### Backlog_Remaining Monthly Costs_Table
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE],  "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date]), "Months", [Backlog Months_Contract], "forecast", [Cumulative Forecast], "actual", [Cumulative Actual Cost]), 

if(min('Calendar'[Date]) > JOB[TARGET_COMPLETION_DATE], blank(), if([Months] < 1.25 , [forecast] - [actual],

 Divide([forecast] - [actual], [Months]))))
```

#### Backlog_Remaining Monthly Revenue_Table
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
//sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE],  "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date]), "Months", [Backlog Months_Contract]), if(min('Calendar'[Date]) > JOB[TARGET_COMPLETION_DATE], blank(), if([Start Date] <= Today() && [Start Date] <= min('Calendar'[Date]) && [Months] < 1 , [Backlog_Cumulative Current Contract] - [Cumulative Rev Amount Across Jobs], if([Start Date] <= Today() && [Start Date] <= min('Calendar'[Date]) , Divide([Backlog_Cumulative Current Contract] - [Cumulative Rev Amount Across Jobs], [Months], blank())))))

sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE],  "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date]), "Months", [Backlog Months_Contract]), if(min('Calendar'[Date]) > JOB[TARGET_COMPLETION_DATE], blank(), if([Months] < 1.25 , [Backlog_Cumulative Current Contract] - [Cumulative Rev Amount Across Jobs],  

Divide([Backlog_Cumulative Current Contract] - [Cumulative Rev Amount Across Jobs], [Months]))))
```

#### Monthly GP Backlog _ Table
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Backlog_Remaining Monthly Revenue_Table] - [Backlog_Remaining Monthly Costs_Table]
```

#### Target Completion Date Flag
- Format string: `0`
```dax
if(or(min(JOB[TARGET_COMPLETION_DATE]) = blank(),min(JOB[TARGET_COMPLETION_DATE]) < today()) && ([Backlog_Cumulative Current Contract] - [Cumulative Rev Amount Across Jobs]) > 5, 1, 0)
```

#### Total Backlog $
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER],  "Rev", [Cumulative Rev Amount Across Jobs], "Contract", [Backlog_Cumulative Current Contract]),  [Contract] - [Rev])
```

#### Backlog_Remaining Monthly Revenue
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
//sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE], "Completion", if(JOB[TARGET_COMPLETION_DATE] = blank(), date(2024, 11, 30), JOB[TARGET_COMPLETION_DATE]), "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date])), if([Start Date] <= Today() && [Start Date] <= min('Calendar'[Date]) , Divide([Cumulative Current Contract _ Backlog] - [Cumulative Rev Amount Across Jobs], DATEDIFF( min('Calendar'[Date]), [Completion],  MONTH)), blank()))

sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE],  "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date]), "Months", [Backlog Months_Contract]), 

if(min('Calendar'[Date]) > JOB[TARGET_COMPLETION_DATE], blank(), if( [Start Date] <= max('Calendar'[Date]) && [Months] <= 2  && month([Start Date]) <> Month([TARGET_COMPLETION_DATE]), divide([Backlog_Cumulative Current Contract] - [Cumulative Rev Amount Across Jobs], 2, blank()),

if( [Start Date] <= max('Calendar'[Date]) && [Months] < 1.25 , [Backlog_Cumulative Current Contract] - [Cumulative Rev Amount Across Jobs],

if( [Start Date] <= max('Calendar'[Date]) , Divide([Backlog_Cumulative Current Contract] - [Cumulative Rev Amount Across Jobs], [Months], blank()))))))
```

#### Monthly GP Backlog
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Backlog_Remaining Monthly Revenue] - [Backlog_Remaining Monthly Costs]
```

#### Backlog_Remaining Monthly Costs
```dax
//sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE],  "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date]), "Months", [Backlog Months_Contract], "forecast", [Cumulative Forecast], "actual", [Cumulative Actual Cost]), if(min('Calendar'[Date]) > JOB[TARGET_COMPLETION_DATE], blank(), if([Start Date] <= Today() && [Start Date] <= min('Calendar'[Date]) && [Months] < 1 , [forecast] - [actual],if([Start Date] <= Today() && [Start Date] <= min('Calendar'[Date]) , Divide([forecast] - [actual], [Months], blank())))))

sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[START_DATE], JOB[Min Transaction Date], JOB[TARGET_COMPLETION_DATE],  "Start Date", if(JOB[START_DATE] > Date(2000, 1, 1), JOB[START_DATE], JOB[Min Transaction Date]), "Months", [Backlog Months_Contract], "forecast", [Cumulative Forecast], "actual", [Cumulative Actual Cost]), 

if(min('Calendar'[Date]) > JOB[TARGET_COMPLETION_DATE], blank(), 

if( [Start Date] <= max('Calendar'[Date]) && [Months] <= 2  && month([Start Date]) <> Month([TARGET_COMPLETION_DATE]), divide([forecast] - [actual], 2, blank()),

if([Start Date] <= max('Calendar'[Date]) && [Months] < 1.25 , [forecast] - [actual],

if( [Start Date] <= max('Calendar'[Date]) , Divide([forecast] - [actual], [Months], blank()))))))
```

#### Remaining Costs
```dax
sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER],  "Forecast", [Cumulative Forecast], "Actual", [Cumulative Actual Cost]),  [Forecast] - [Actual])
```

#### Total Backlog GP $
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Total Backlog $] - [Remaining Costs]
```

### BUDGET

#### Revenue Budget YTD
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var maxyear = calculate(max('Calendar'[Fiscal Year]), ALLSELECTED('Calendar'))

	return

	calculate([Revenue Budget], 'Calendar'[Fiscal Year] = maxyear) * -1
```

#### Buffer
```dax
if(BUDGET[Revenue Budget YTD] > [Revenue YTD], BUDGET[Revenue Budget YTD] * 1.1, [Revenue YTD] * 1.1)
```

#### Revenue Budget
```dax
calculate(sum(BUDGET[BUDGETAMT]), filter(BUDGET, BUDGET[ACCOUNT_TYPE] = "REVENUE"))
```

### Calendar

#### Max Date
- Format string: `General Date`
```dax
max('Calendar'[Date])
```

### Cost Measures

#### Actual Cost
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sum(JOB_COST_DETAILS[COST_AMT])
```

#### Cost Budget
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sum('JOB FORECAST'[FORECAST_COSTS])
```

#### Original Cost Estimate
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sum(JOB_COST_SUMMARY[REVISED_ESTIMATED_COST])
```

#### Cumulative Forecast
```dax
	

	var maxdat = [Max Date]

	return

	ROUND(calculate([Cost Budget], filter(all('Calendar'), 'Calendar'[Date] <= maxdat)), 2)
```

#### Cumulative Actual Cost
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	return

	calculate([Actual Cost], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))
```

#### % Complete
- Format string: `0%;-0%;0%`
```dax
if(Divide([Cumulative Actual Cost], [Cumulative Forecast], blank()) > 1, 1, Divide([Cumulative Actual Cost], [Cumulative Forecast], blank()))
```

#### Available Budget
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Cumulative Forecast] - [Cumulative Actual Cost] 

//- [Committed Cost]
```

#### Estimated to Forecasted Variance
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Cumulative Forecast] - [Original Cost Estimate]
```

#### Cost Change LM to TM
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	var tm = calculate([Cumulative Forecast], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))

	var costlm = calculate([Cumulative Forecast], filter(all('Calendar'), 'Calendar'[Running Total Month] < runtot))

	return

	tm - costlm
```

#### Contingency
```dax
calculate([Cumulative Forecast], COST_CODE_MAPPING[Contingency Flag] = "CONTINGENCY")
```

#### Contingency TM
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	var tm = calculate('Cost Measures'[Contingency], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))

	var costlm = calculate('Cost Measures'[Contingency], filter(all('Calendar'), 'Calendar'[Running Total Month] < runtot))

	return

	tm
```

#### Contingency LM
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	var tm = calculate('Cost Measures'[Contingency], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))

	var costlm = calculate('Cost Measures'[Contingency], filter(all('Calendar'), 'Calendar'[Running Total Month] < runtot))

	return

	costlm
```

#### GL Cost of Revenue
```dax
calculate(sum('GL POSTING'[DEBITAMT]), filter('GL POSTING', 'GL POSTING'[ACTNUMBR_1] = "340"))
```

#### Estimated Hours
- Format string: `#,0.0`
```dax
calculate(sum(JOB_COST_SUMMARY[COST_CODE_EST_UNIT]), JOB_COST_SUMMARY[COST_ELEMENT] = 1)
```

#### Total Hours
- Format string: `#,0.0`
```dax
	//sum(JOB_LABOR_HOURS[MONDAY]) + sum(JOB_LABOR_HOURS[TUESDAY]) + sum(JOB_LABOR_HOURS[WEDNESDAY]) + sum(JOB_LABOR_HOURS[THURSDAY]) + sum(JOB_LABOR_HOURS[FRIDAY])

	calculate(sum(JOB_LABOR_HOURS[TOTAL_HOURS]), JOB_LABOR_HOURS[Cost Element] = "Labor")
```

#### Hours Remaining
- Format string: `#,0.0`
```dax
[Estimated Hours] - [Total Hours]
```

#### Committed Cost
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sum(JOB_COST_SUMMARY[COMMITTED_COST])
```

#### Cumulative Hours
- Format string: `0.0`
```dax
	

	var maxdat = [Max Date]

	return

	calculate([Total Hours], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))
```

### JOB

#### Selected Project Name
```dax
"Name : " & selectedvalue(JOB[Job Number - Name], "Multiple Jobs")
```

#### Selected Division
```dax
"Division : " & selectedvalue(JOB[DIVISIONS], "Multiple")
```

#### Selected PM
```dax
"PM : " & selectedvalue(JOB[Project Manager], "Multiple")
```

#### Selected Sup
```dax
"Superintendent : " & selectedvalue(JOB[Superintendent], "Multiple")
```

#### Selected Sales Rep
```dax
"Sales Rep : " & selectedvalue(JOB[Sales Rep], "Multiple")
```

### Refresh Date

#### Refresh Date
```dax
var tim2 = max('Refresh Date'[Time]) - TIME(4, 0, 0)

 var tim = max('Refresh Date'[Time]) 

return

"Last Refresh: " & max('Refresh Date'[Date]) & " " & tim2
```

### Revenue Measures

#### Original Contract
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[ORIG_CONTRACT_AMOUNT]), JOB[ORIG_CONTRACT_AMOUNT])
```

#### Cumulative Revenue
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
if([Current Contract Amount] * 'Cost Measures'[% Complete] > [Current Contract Amount], [Current Contract Amount], [Current Contract Amount] * 'Cost Measures'[% Complete])
```

#### Current Contract Amount
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Original Contract] + [Cumulative CO$]
```

#### Forecasted GP $
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
if([Cumulative Forecast] = blank(), blank(), [Current Contract Amount] - [Cumulative Forecast])
```

#### Forecasted GP%
- Format string: `0.0%;-0.0%;0.0%`
```dax
divide([Forecasted GP $], [Current Contract Amount], blank())
```

#### Change Order $
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "CO", sum(CHANGE_ORDERS_BY_MONTH[CHANGE_ORDER_EST_COST])), [CO])
```

#### Estimated GP $
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Current Contract Amount] - [Original Cost Estimate]
```

#### Estimated GP%
- Format string: `0.0%;-0.0%;0.0%`
```dax
if([Estimated GP $] = blank(), blank(), divide([Estimated GP $], [Current Contract Amount], blank()))
```

#### Cumulative Revenue YTD
```dax
	

	var maxdat = [Max Date]

	var maxyear = calculate(max('Calendar'[Fiscal Year]), ALLSELECTED('Calendar'))

	return

	calculate([Cumulative Revenue], 'Calendar'[Fiscal Year] = maxyear)
```

#### Cumulative Rev Amount Across Jobs YTD
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "contract", [Cumulative Revenue YTD]), [contract])
```

#### Change Order $2
```dax
sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], JOB[CONFIRMED_CHG_ORDER_AMT]), sum(JOB[CONFIRMED_CHG_ORDER_AMT]))
```

#### Cumulative CO$
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	var maxdat = [Max Date]

	return

	calculate([Change Order $], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))
```

#### Forecasted GP$ Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "contract", if([Forecasted GP $] <> BLank(), [Forecasted GP $], [Estimated GP $])), [contract])
```

#### Cumulative Current Contract
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "contract", [Current Contract Amount]), [contract])
```

#### Forecasted GP% Across Jobs
- Format string: `0.0%;-0.0%;0.0%`
```dax
divide([Forecasted GP$ Across Jobs], [Cumulative Current Contract], blank())
```

#### Estimated GP$ Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "contract", [Estimated GP $]), [contract])
```

#### Cumulative Original Contract
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "contract", [Original Contract]), [contract])
```

#### Estimated GP% Across Jobs
- Format string: `0.0%;-0.0%;0.0%`
```dax
divide([Estimated GP$ Across Jobs], [Cumulative Current Contract], blank())
```

#### Cumulative Rev Amount Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "contract", [Cumulative Revenue]), [contract])
```

#### Revenue YTD
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var maxyear = calculate(max('Calendar'[Fiscal Year]), ALLSELECTED('Calendar'))

	return

	calculate([Net Earned Rev Amount Across Jobs], 'Calendar'[Fiscal Year] = maxyear)
```

#### Net Earned Revenue
```dax
	

	var compl = ROUND(divide('Cost Measures'[Actual Cost] , [Cumulative Forecast], blank()),4)

	return

	[Current Contract Amount] * compl
```

#### Net Earned Rev Amount Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "contract", [Net Earned Revenue]), [contract])
```

#### Revenue LY YTD
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var maxyear = calculate(max('Calendar'[Fiscal Year]), ALLSELECTED('Calendar'))

	return

	//calculate([Revenue YTD], SAMEPERIODLASTYEAR('Calendar'[Date]))

	calculate([Net Earned Rev Amount Across Jobs], 'Calendar'[Fiscal Year] = maxyear - 1)
```

#### Net Earned Rev Amount TM
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	

	return

	if(calculate('Revenue Measures'[Net Earned Rev Amount Across Jobs], filter(all('Calendar'), 'Calendar'[Running Total Month] = runtot)) = blank(), 0, calculate('Revenue Measures'[Net Earned Rev Amount Across Jobs], filter(all('Calendar'), 'Calendar'[Running Total Month] = runtot)))
```

#### Net Earned Rev Amount LM
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	var lm = runtot - 1

	return

	calculate('Revenue Measures'[Net Earned Rev Amount Across Jobs], filter(all('Calendar'), 'Calendar'[Running Total Month] = lm))
```

#### Revenue Change
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "contract", 'Revenue Measures'[Net Earned Rev Amount TM], "lm", 'Revenue Measures'[Net Earned Rev Amount LM]), [contract] - [lm])
```

#### Forecasted to Est GP Variance $
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Forecasted GP $] - [Estimated GP $]
```

#### Forecasted GP $ TM to LM
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	var runtotlm = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat) - 1

	var contracttm =  calculate([Current Contract Amount],'Calendar'[Running Total Month] = runtot)

	var contractlm =  calculate([Current Contract Amount],'Calendar'[Running Total Month] = runtotlm)

	var costtm = calculate('Cost Measures'[Cumulative Forecast], filter(all('Calendar'), 'Calendar'[Running Total Month] <= runtot))

	var costlm = calculate([Cumulative Forecast], filter(all('Calendar'), 'Calendar'[Running Total Month] < runtot))

	return

	if(costlm <> blank(), (contracttm - costtm) - (contractlm - costlm))
```

#### Forecast to Est GP Variance %
- Format string: `0%;-0%;0%`
```dax
Divide([Forecasted GP $] - [Estimated GP $], [Estimated GP $], blank())
```

#### GP% Difference
- Format string: `0.0%;-0.0%;0.0%`
```dax
	[Forecasted GP% Across Jobs] - [Estimated GP% Across Jobs]

	//if([Forecasted GP%] = blank(), blank(), [Forecasted GP%] - [Estimated GP%])
```

#### Cumulative Billed Amount
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	return

	calculate(sum(INVOICES[ACCOUNT_AMOUNT]), filter(all('Calendar'), 'Calendar'[Date] <= maxdat))
```

#### Over - Under Billed
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Cumulative Billed Amount] - [Cumulative Revenue]
```

#### Over Under Billed Across Jobs
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "contract", [Over - Under Billed]), [contract])
```

#### Over / (Under) Billed Cumulative Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	return

	calculate([Over Under Billed Across Jobs], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))
```

#### Cumulative Over Under Billed Amount Across Jobs LM
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var runningtotal = lookupvalue('Calendar'[Running Total Month],'Calendar'[Date] , maxdat)

	var runtot = calculate(max('Calendar'[Running Total Month]),'Calendar'[Date] = maxdat)

	

	return

	calculate([Over Under Billed Across Jobs], filter(all('Calendar'), 'Calendar'[Running Total Month] < runtot))
```

#### Count Under Billed Jobs
- Format string: `0`
```dax
COUNTROWS(filter(summarize('JOB', JOB[JOB_NUMBER], "Under Billed", [Over - Under Billed]), [Under Billed] < 0))
```

#### test
```dax
[Net Earned Rev Amount Across Jobs] - 'Revenue Measures'[Revenue Rolling 12]
```

#### Revenue Rolling 12
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
var maxdat = [Max Date]

var nextdate = maxdat + 1

//calculate('Revenue Measures'[Net Earned Rev Amount Across Jobs], filter('Calendar', 'Calendar'[Date] > date(year(nextdate) - 1, month(nextdate), day(nextdate))))

var maxrunningtotal = calculate(max('Calendar'[Running Total Month]), filter('Calendar', 'Calendar'[Date] = [Max Date])) 

var monmin = maxrunningtotal 

var monminly = monmin - 12

return if(year(today()) = year([Max Date]) && MONTH(today()) = month([Max Date]), 

calculate([Net Earned Rev Amount Across Jobs], filter(all('Calendar'), 'Calendar'[Running Total Month] >= monminly && 'Calendar'[Running Total Month] < monmin)),

calculate([Net Earned Rev Amount Across Jobs], filter(all('Calendar'), 'Calendar'[Running Total Month] > monminly && 'Calendar'[Running Total Month] <= monmin)))
```

#### Revenue Rolling 12 PY
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
var maxrunningtotal = calculate(max('Calendar'[Running Total Month]), filter('Calendar', 'Calendar'[Date] = [Max Date])) 

var monmin = maxrunningtotal - 12

var monminly = monmin - 12

return if(year(today()) = year([Max Date]) && MONTH(today()) = month([Max Date]), 

calculate([Net Earned Rev Amount Across Jobs], filter(all('Calendar'), 'Calendar'[Running Total Month] >= monminly && 'Calendar'[Running Total Month] < monmin)),

calculate([Net Earned Rev Amount Across Jobs], filter(all('Calendar'), 'Calendar'[Running Total Month] > monminly && 'Calendar'[Running Total Month] <= monmin)))
```

#### Actual GP$
```dax
([Current Contract Amount] * [% Complete]) - [Actual Cost]
```

#### Actual GP$ Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOB, JOB[JOB_NUMBER], "contract", [Actual GP$]), [contract])
```

#### Display TM to LM Forecasted Change
```dax
"Total Change = " & Format([Forecasted GP $ TM to LM], "$#,##")
```
