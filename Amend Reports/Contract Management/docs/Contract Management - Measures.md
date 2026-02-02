# Contract Management — Measures

Generated: 2026-01-22 15:09 EST

## Revenue Measures (focus)

⚠️ Warning: the `Revenue Measures` in this dataset reference missing model tables (e.g. `JOBS_D`, `INVOICES_F`) and appear to be copied/orphaned (not bound via `queryRef` in report visuals).

| Measure | Depends on measures | Depends on columns |
|---|---|---|
| `Original Contract` | JOB_NUMBER, ORIG_CONTRACT_AMOUNT | JOBS_D[JOB_NUMBER], JOBS_D[ORIG_CONTRACT_AMOUNT] |
| `Cumulative Revenue` | % Complete, Current Contract Amount | Cost Measures[% Complete] |
| `Current Contract Amount` | Cumulative CO$, Original Contract |  |
| `Forecasted GP $` | Cumulative Forecast, Current Contract Amount |  |
| `Forecasted GP%` | Current Contract Amount, Forecasted GP $ |  |
| `Change Order $` | CHANGE_ORDER_EST_COST, CO, JOB_NUMBER | CHANGE_ORDERS_BY_MONTH[CHANGE_ORDER_EST_COST], JOBS_D[JOB_NUMBER] |
| `Estimated GP $` | Current Contract Amount, Original Cost Estimate |  |
| `Estimated GP%` | Current Contract Amount, Estimated GP $ |  |
| `Cumulative Revenue YTD` | Cumulative Revenue, Fiscal Year, Max Date | Calendar[Fiscal Year] |
| `Cumulative Rev Amount Across Jobs YTD` | Cumulative Revenue YTD, JOB_NUMBER, contract | JOBS_D[JOB_NUMBER] |
| `Change Order $2` | CONFIRMED_CHG_ORDER_AMT, JOB_NUMBER | JOBS_D[CONFIRMED_CHG_ORDER_AMT], JOBS_D[JOB_NUMBER] |
| `Cumulative CO$` | Change Order $, Date, Max Date | Calendar[Date] |
| `Forecasted GP$ Across Jobs` | Estimated GP $, Forecasted GP $, JOB_NUMBER, contract | JOBS_D[JOB_NUMBER] |
| `Cumulative Current Contract` | Current Contract Amount, JOB_NUMBER, contract | JOBS_D[JOB_NUMBER] |
| `Forecasted GP% Across Jobs` | Cumulative Current Contract, Forecasted GP$ Across Jobs |  |
| `Estimated GP$ Across Jobs` | Estimated GP $, JOB_NUMBER, contract | JOBS_D[JOB_NUMBER] |
| `Cumulative Original Contract` | JOB_NUMBER, Original Contract, contract | JOBS_D[JOB_NUMBER] |
| `Estimated GP% Across Jobs` | Cumulative Current Contract, Estimated GP$ Across Jobs |  |
| `Cumulative Rev Amount Across Jobs` | Cumulative Revenue, JOB_NUMBER, contract | JOBS_D[JOB_NUMBER] |
| `Revenue YTD` | Fiscal Year, Max Date, Net Earned Rev Amount Across Jobs | Calendar[Fiscal Year] |
| `Net Earned Revenue` | Cumulative Forecast, Current Contract Amount, Job_Actual Cost | Cost Measures[Job_Actual Cost] |
| `Net Earned Rev Amount Across Jobs` | JOB_NUMBER, Net Earned Revenue, contract | JOBS_D[JOB_NUMBER] |
| `Revenue LY YTD` | Date, Fiscal Year, Max Date, Net Earned Rev Amount Across Jobs, Revenue YTD | Calendar[Date], Calendar[Fiscal Year] |
| `Net Earned Rev Amount TM` | Date, Max Date, Net Earned Rev Amount Across Jobs, Running Total Month | Calendar[Date], Calendar[Running Total Month], Revenue Measures[Net Earned Rev Amount Across Jobs] |
| `Net Earned Rev Amount LM` | Date, Max Date, Net Earned Rev Amount Across Jobs, Running Total Month | Calendar[Date], Calendar[Running Total Month], Revenue Measures[Net Earned Rev Amount Across Jobs] |
| `Revenue Change` | JOB_NUMBER, Net Earned Rev Amount LM, Net Earned Rev Amount TM, contract, lm | JOBS_D[JOB_NUMBER], Revenue Measures[Net Earned Rev Amount LM], Revenue Measures[Net Earned Rev Amount TM] |
| `Forecasted to Est GP Variance $` | Estimated GP $, Forecasted GP $ |  |
| `Forecasted GP $ TM to LM` | Cumulative Forecast, Current Contract Amount, Date, Max Date, Running Total Month | Calendar[Date], Calendar[Running Total Month], Cost Measures[Cumulative Forecast] |
| `Forecast to Est GP Variance %` | Estimated GP $, Forecasted GP $ |  |
| `GP% Difference` | Estimated GP%, Estimated GP% Across Jobs, Forecasted GP%, Forecasted GP% Across Jobs |  |
| `Cumulative Billed Amount` | ACCOUNT_AMOUNT, Date, Max Date | Calendar[Date], INVOICES_F[ACCOUNT_AMOUNT] |
| `Over - Under Billed` | Cumulative Billed Amount, Cumulative Revenue |  |
| `Over Under Billed Across Jobs` | JOB_NUMBER, Over - Under Billed, contract | JOBS_D[JOB_NUMBER] |
| `Over / (Under) Billed Cumulative Across Jobs` | Date, Max Date, Over Under Billed Across Jobs | Calendar[Date] |
| `Cumulative Over Under Billed Amount Across Jobs LM` | Date, Max Date, Over Under Billed Across Jobs, Running Total Month | Calendar[Date], Calendar[Running Total Month] |
| `Count Under Billed Jobs` | JOB_NUMBER, Over - Under Billed, Under Billed | JOBS_D[JOB_NUMBER] |
| `test` | Net Earned Rev Amount Across Jobs, Revenue Rolling 12 | Revenue Measures[Revenue Rolling 12] |
| `Revenue Rolling 12` | Date, Max Date, Net Earned Rev Amount Across Jobs, Running Total Month | Calendar[Date], Calendar[Running Total Month], Revenue Measures[Net Earned Rev Amount Across Jobs] |
| `Revenue Rolling 12 PY` | Date, Max Date, Net Earned Rev Amount Across Jobs, Running Total Month | Calendar[Date], Calendar[Running Total Month] |
| `Actual GP$` | % Complete, Current Contract Amount, Job_Actual Cost |  |
| `Actual GP$ Across Jobs` | Actual GP$, JOB_NUMBER, contract | JOBS_D[JOB_NUMBER] |
| `Display TM to LM Forecasted Change` | Forecasted GP $ TM to LM |  |

## Contract Measures (focus)

| Measure | Depends on measures | Depends on columns |
|---|---|---|
| `% Complete Costs` | Actual Costs, Estimated Call Costs |  |
| `Actual Costs` | COST_ALL, In Current Contract, Value | CALLS COSTS[In Current Contract], CALLS COSTS[Value], CALLS_F[COST_ALL], CALLS_F[In Current Contract] |
| `Forecasted Costs` | Current Contract Flag, Estimated Total Costs, FORECAST_TOTAL_COST | CONTRACTS_D[Current Contract Flag], CONTRACTS_D[FORECAST_TOTAL_COST] |
| `Cost Check` | Actual Costs, YTD Total Cost |  |
| `Cumulative Actual Costs` | Actual Costs, Date, Max Date | Calendar[Date] |
| `Estimated Total Costs` | Current Contract Flag, ESTIMATE_TOTAL_COST | CONTRACTS_D[Current Contract Flag], CONTRACTS_D[ESTIMATE_TOTAL_COST] |
| `Contract Amount` | ANNUAL_CONTRACT_VALUE, Current Contract Flag | CONTRACTS_D[ANNUAL_CONTRACT_VALUE], CONTRACTS_D[Current Contract Flag] |
| `Estimated GP$` | Contract Amount, Estimated Total Costs |  |
| `Forecasted GP$` | Contract Amount, Forecasted Costs |  |
| `Monthly Recognzied Revenue` | CONTRACT_EXPIRATION_DATE, CONTRACT_START_DATE, Contract Amount | CONTRACTS_D[CONTRACT_EXPIRATION_DATE], CONTRACTS_D[CONTRACT_START_DATE] |
| `YTD Total Cost` | Current Contract Flag, YTD_TOTAL_COST | CONTRACTS_D[Current Contract Flag], CONTRACTS_D[YTD_TOTAL_COST] |
| `Total Revenue Recognized` | CONTRACT_START_DATE, Date, Monthly Recognzied Revenue, Number of months since start | CONTRACTS_D[CONTRACT_START_DATE], Calendar[Date] |
| `Months Recognized` | CONTRACT_START_DATE, Date | CONTRACTS_D[CONTRACT_START_DATE], Calendar[Date] |
| `YTD Recognized Revenue` | Current Contract Flag, YTD_REVENUE_RECOGNIZED | CONTRACTS_D[Current Contract Flag], CONTRACTS_D[YTD_REVENUE_RECOGNIZED] |
| `% Complete Schedule` | CONTRACT_EXPIRATION_DATE, CONTRACT_START_DATE | CONTRACTS_D[CONTRACT_EXPIRATION_DATE], CONTRACTS_D[CONTRACT_START_DATE] |
| `YTD Billed Amount` | YTD_BILLED | CONTRACTS_D[YTD_BILLED] |
| `Over-Under Billed` | Amount Billed, Total Revenue Recognized Across Jobs |  |
| `Contract Over Under Billed Across Jobs` | Customer-Contract, Over-Under Billed, contract | CONTRACTS MAPPING[Customer-Contract] |
| `Over/(Under) Billed Cumulative Across Jobs` | Contract Over Under Billed Across Jobs, Date, Max Date | Calendar[Date] |
| `Count Under Billed Contracts` | Contract Over Under Billed Across Jobs, Customer-Contract, Under Billed | CONTRACTS MAPPING[Customer-Contract] |
| `Total Revenue Recognized Across Jobs` | CONTRACT_EXPIRATION_DATE, CONTRACT_START_DATE, Contract Amount, Customer-Contract, Date, Monthly Recognzied Revenue, rev, start_ | CONTRACTS MAPPING[Customer-Contract], CONTRACTS_D[CONTRACT_EXPIRATION_DATE], CONTRACTS_D[CONTRACT_START_DATE], CONTRACTS_D[Customer-Contract], Calendar[Date] |
| `Estimated GP$ Across Contract` | Customer-Contract, Estimated GP$, contract | CONTRACTS MAPPING[Customer-Contract] |
| `Estimated GP%_Contract` | Contract Amount, Estimated GP$ Across Contract |  |
| `Forecasted GP$ Across Contract` | Customer-Contract, Forecasted GP$, contract | CONTRACTS MAPPING[Customer-Contract] |
| `Forecasted GP%_Contract` | Contract Amount, Forecasted GP$ Across Contract |  |
| `GP% Difference_Contract` | Actual GP%_Contract, Estimated GP%_Contract |  |
| `Actual GP$ Across Jobs_Contract` | Cumulative Actual Costs, Customer-Contract, Total Revenue Recognized Across Jobs, contract, cost | CONTRACTS MAPPING[Customer-Contract] |
| `Actual GP%_Contract` | Actual GP$ Across Jobs_Contract, Total Revenue Recognized Across Jobs |  |
| `% Complete Variance` | % Complete Costs, % Complete Schedule |  |
| `Forecasted Cost by Month` | CONTRACT_EXPIRATION_DATE, CONTRACT_START_DATE, Costs, Customer-Contract, Date, End, Forecasted Costs, Start | CONTRACTS MAPPING[Customer-Contract], CONTRACTS_D[CONTRACT_EXPIRATION_DATE], CONTRACTS_D[CONTRACT_START_DATE], CONTRACTS_D[Customer-Contract], Calendar[Date] |
| `Cumulative Estimated Costs` | CONTRACT_EXPIRATION_DATE, CONTRACT_START_DATE, Date, Estimated Call Costs, Max Date | CONTRACTS_D[CONTRACT_EXPIRATION_DATE], CONTRACTS_D[CONTRACT_START_DATE], Calendar[Date] |
| `Date filter` | CONTRACT_EXPIRATION_DATE, CONTRACT_START_DATE, Date | CONTRACTS_D[CONTRACT_EXPIRATION_DATE], CONTRACTS_D[CONTRACT_START_DATE], Calendar[Date] |
| `Actual Labor Costs` | COST_LABOR, In Current Contract | CALLS_F[COST_LABOR], CALLS_F[In Current Contract] |
| `Amount Billed` | BILLABLE_ALL, In Current Contract | CONTRACTS_BILLING_F[BILLABLE_ALL], CONTRACTS_BILLING_F[In Current Contract] |
| `Number of months since start` | CONTRACT_EXPIRATION_DATE, CONTRACT_START_DATE, Customer-Contract, Date, start, start_ | CONTRACTS MAPPING[Customer-Contract], CONTRACTS_D[CONTRACT_EXPIRATION_DATE], CONTRACTS_D[CONTRACT_START_DATE], CONTRACTS_D[Customer-Contract], Calendar[Date] |
| `Available Budget_Contract` | Actual Costs, Estimated Call Costs |  |
| `Months Remaining` | CONTRACT_EXPIRATION_DATE | CONTRACTS_D[CONTRACT_EXPIRATION_DATE] |
| `Costs Remaining - Current Run Rate` | Actual Costs, Customer-Contract, Months Recognized, Months Remaining, actual, months, remaining | CONTRACTS MAPPING[Customer-Contract] |
| `Available - Run Rate` | Available Budget_Contract Calls, Costs Remaining - Current Run Rate |  |
| `Estimated Call Costs` | Cost Type, In Current Contract, Value | FORECASTED CALLS COST[Cost Type], FORECASTED CALLS COST[In Current Contract], FORECASTED CALLS COST[Value] |
| `Available Budget_Contract Calls` | Actual Costs, Estimated Call Costs |  |
| `Months test` | CONTRACT_EXPIRATION_DATE, CONTRACT_START_DATE | CONTRACTS_D[CONTRACT_EXPIRATION_DATE], CONTRACTS_D[CONTRACT_START_DATE] |

## Cost Measures (focus)

| Measure | Depends on measures | Depends on columns |
|---|---|---|
| `Job_Actual Cost` | COST_AMT | JOB_COST_DETAILS_F[COST_AMT] |
| `Cost Budget` | FORECAST_COSTS | JOB_COST_FORECASTS_F[FORECAST_COSTS] |
| `Original Cost Estimate` | REVISED_ESTIMATED_COST | JOB_COST_SUMMARY_F[REVISED_ESTIMATED_COST] |
| `Cumulative Forecast` | Cost Budget, Date, Max Date | Calendar[Date] |
| `Cumulative Actual Cost` | Date, Job_Actual Cost, Max Date | Calendar[Date] |
| `% Complete` | Cumulative Actual Cost, Cumulative Forecast |  |
| `Available Budget` | Committed Cost, Cumulative Actual Cost, Cumulative Forecast |  |
| `Estimated to Forecasted Variance` | Cumulative Forecast, Original Cost Estimate |  |
| `Cost Change LM to TM` | Cumulative Forecast, Date, Max Date, Running Total Month | Calendar[Date], Calendar[Running Total Month] |
| `Contingency` | Contingency Flag, Cumulative Forecast | JOB_COST_DESCRIPTION_D[Contingency Flag] |
| `Contingency TM` | Contingency, Date, Max Date, Running Total Month | Calendar[Date], Calendar[Running Total Month], Cost Measures[Contingency] |
| `Contingency LM` | Contingency, Date, Max Date, Running Total Month | Calendar[Date], Calendar[Running Total Month], Cost Measures[Contingency] |
| `GL Cost of Revenue` | ACTNUMBR_1, DEBITAMT | POSTING_DATA_F[ACTNUMBR_1], POSTING_DATA_F[DEBITAMT] |
| `Estimated Hours` | COST_CODE_EST_UNIT, COST_ELEMENT | JOB_COST_SUMMARY_F[COST_CODE_EST_UNIT], JOB_COST_SUMMARY_F[COST_ELEMENT] |
| `Total Hours` | Cost Element, FRIDAY, MONDAY, THURSDAY, TOTAL_HOURS, TUESDAY, WEDNESDAY | JOB_LABOR_HOURS[FRIDAY], JOB_LABOR_HOURS[MONDAY], JOB_LABOR_HOURS[THURSDAY], JOB_LABOR_HOURS[TUESDAY], JOB_LABOR_HOURS[WEDNESDAY], JOB_LABOR_HOURS_F[Cost Element], JOB_LABOR_HOURS_F[TOTAL_HOURS] |
| `Hours Remaining` | Estimated Hours, Total Hours |  |
| `Committed Cost` | COMMITTED_COST | JOB_COST_SUMMARY_F[COMMITTED_COST] |
| `Cumulative Hours` | Date, Max Date, Total Hours | Calendar[Date] |

## Hour Measures (focus)

| Measure | Depends on measures | Depends on columns |
|---|---|---|
| `Actual Hours` | ACTUAL_HOURS | CONTRACTS_D[ACTUAL_HOURS] |
| `Forecast Hours` | FORECAST_HOURS | CONTRACTS_D[FORECAST_HOURS] |
| `Estimate Hours` | ESTIMATE_HOURS | CONTRACTS_D[ESTIMATE_HOURS] |
| `Hour Difference` | SERVICE_CALL_ID, Service Call Actual, Service Call Estimated, actual, estimate | CALLS_F[SERVICE_CALL_ID] |
| `Hour Variance` | Service Call Actual, Service Call Estimated |  |
| `Service Call Actual` | ACTUAL_HOURS | APPOINTMENTS_F[ACTUAL_HOURS] |
| `Service Call Estimated` | Estimated Hours_, SERVICE_CALL_ID | CALLS_F[SERVICE_CALL_ID], CONTRACTS_TASK_SCHEDULE[Estimated Hours_], CONTRACTS_TASK_SCHEDULE[SERVICE_CALL_ID] |
| `Available Hours` | Contract Estimated Hours, STATUS_OF_CALL, Service Call Actual | CALLS_F[STATUS_OF_CALL] |
| `Cumulative Actual Hours` | Date, Max Date, Service Call Actual | Calendar[Date] |
| `Cumulative Estimated Hours` | Date, Max Date, Service Call Estimated | Calendar[Date] |
| `Actual - Estimate Variance` | Estimate Hours, Service Call Actual |  |
| `Contract Estimated Hours` | Customer-Contract, Date, Estimated Hours_, SCHEDULE_DATE | CONTRACTS MAPPING[Customer-Contract], CONTRACTS_TASK_SCHEDULE[Customer-Contract], CONTRACTS_TASK_SCHEDULE[Estimated Hours_], CONTRACTS_TASK_SCHEDULE[SCHEDULE_DATE], Calendar[Date] |
| `Hour Table Filter` | Contract Estimated Hours, Service Call Actual, Service Call Estimated |  |
| `Contract to Date to Actual Hour Variance` | Estimated Contract Hours to Date, Service Call Actual |  |
| `Estimated Contract Hours to Date` | Contract Estimated Hours, Date | Calendar[Date] |

## Full Measure Catalog

### BUDGET_F

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
if(BUDGET_F[Revenue Budget YTD] > [Revenue YTD], BUDGET_F[Revenue Budget YTD] * 1.1, [Revenue YTD] * 1.1)
```

#### Revenue Budget
```dax
calculate(sum(BUDGET_F[BUDGETAMT]), filter(BUDGET_F, BUDGET_F[ACCOUNT_TYPE] = "Revenue"))
```

### Calendar

#### Max Date
- Format string: `General Date`
```dax
max('Calendar'[Date])
```

### CALLS_F

#### Number of Calls
- Format string: `0`
```dax
CALCULATE(COUNT(CALLS_F[SERVICE_CALL_ID]))
```

#### Late PMs
- Format string: `0`
```dax
CALCULATE( 

    COUNT(CALLS_F[SERVICE_CALL_ID]), 

    CALLS_F[TYPE_OF_CALL]="GENERATED MC",

    CALLS_F[STATUS_OF_CALL]="Open",

    CALLS_F[Calculated_Days_Open] > 60)
```

#### Late PM Revenue
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
CALCULATE( 

    sum(CALLS_F[Monthly Revenue]), 

    CALLS_F[TYPE_OF_CALL]="GENERATED MC",

    CALLS_F[STATUS_OF_CALL]="Open",

    CALLS_F[Calculated_Days_Open] > 60)
```

### Contract Measures

#### % Complete Costs
- Format string: `0%;-0%;0%`
```dax
Divide([Actual Costs], [Estimated Call Costs], blank())
```

#### Actual Costs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	//calculate(sum(CALLS_F[COST_ALL]), CALLS_F[In Current Contract] = 1)

	 calculate(sum('CALLS COSTS'[Value]), 'CALLS COSTS'[In Current Contract]= 1)
```

#### Forecasted Costs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	//calculate(sum(CONTRACTS_D[FORECAST_TOTAL_COST]), CONTRACTS_D[Current Contract Flag] = 1)

	[Estimated Total Costs]
```

#### Cost Check
```dax
[YTD Total Cost] - [Actual Costs]
```

#### Cumulative Actual Costs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	return

	 if(max('Calendar'[Date]) > today(), blank(), calculate([Actual Costs], filter(all('Calendar'), 'Calendar'[Date] <= max('Calendar'[Date]))))
```

#### Estimated Total Costs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
calculate(sum(CONTRACTS_D[ESTIMATE_TOTAL_COST]), CONTRACTS_D[Current Contract Flag] = 1)
```

#### Contract Amount
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
calculate(sum(CONTRACTS_D[ANNUAL_CONTRACT_VALUE]), CONTRACTS_D[Current Contract Flag] = 1)
```

#### Estimated GP$
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Contract Amount] - [Estimated Total Costs]
```

#### Forecasted GP$
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Contract Amount] - [Forecasted Costs]
```

#### Monthly Recognzied Revenue
```dax
Divide([Contract Amount] , datediff(max(CONTRACTS_D[CONTRACT_START_DATE]), max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), MONTH)+1, blank())
```

#### YTD Total Cost
```dax
CALCULATE(sum(CONTRACTS_D[YTD_TOTAL_COST]), CONTRACTS_D[Current Contract Flag] = 1)
```

#### Total Revenue Recognized
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	//[Monthly Recognzied Revenue] * (Datediff(max(CONTRACTS_D[CONTRACT_START_DATE]), calculate(max('Calendar'[Date]), 'Calendar'[Date] <= today()), MONTH) )

	[Number of months since start] * [Monthly Recognzied Revenue]
```

#### Months Recognized
- Format string: `0`
```dax
Datediff(max(CONTRACTS_D[CONTRACT_START_DATE]), calculate(max('Calendar'[Date]), 'Calendar'[Date] <= today()), MONTH) + 1
```

#### YTD Recognized Revenue
```dax
CALCULATE(sum(CONTRACTS_D[YTD_REVENUE_RECOGNIZED]), CONTRACTS_D[Current Contract Flag] = 1)
```

#### % Complete Schedule
- Format string: `0%;-0%;0%`
```dax
	divide(

	    datediff(max(CONTRACTS_D[CONTRACT_START_DATE]), today(), DAY),

	    datediff(max(CONTRACTS_D[CONTRACT_START_DATE]), max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), DAY), blank())
```

#### YTD Billed Amount
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sum(CONTRACTS_D[YTD_BILLED])
```

#### Over-Under Billed
```dax
[Amount Billed] - [Total Revenue Recognized Across Jobs]
```

#### Contract Over Under Billed Across Jobs
```dax
	

	sumx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "contract", [Over-Under Billed]), [contract])
```

#### Over/(Under) Billed Cumulative Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	return

	calculate([Contract Over Under Billed Across Jobs], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))
```

#### Count Under Billed Contracts
- Format string: `0`
```dax
COUNTROWS(filter(summarize('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "Under Billed", [Contract Over Under Billed Across Jobs]), [Under Billed] < 0))
```

#### Total Revenue Recognized Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
var mx = max('Calendar'[Date])

var mn = min('Calendar'[Date])

return

sumx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], 

"amount", [Contract Amount], 

"rev", [Monthly Recognzied Revenue],

"xxx", Divide([Contract Amount] , datediff(max(CONTRACTS_D[CONTRACT_START_DATE]), max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), MONTH), blank()), 

"start_", calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract])), 

"months_", if(calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract])) >= max('Calendar'[Date]), blank(), (Datediff(calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract])), mx, MONTH))),

"end_", calculate(max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract]))), 

if([start_] >= max('Calendar'[Date]), blank(), (Datediff([start_], mx, MONTH)+ 1)* [rev]))
```

#### Estimated GP$ Across Contract
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "contract", [Estimated GP$]), [contract])
```

#### Estimated GP%_Contract
- Format string: `0.0%;-0.0%;0.0%`
```dax
divide([Estimated GP$ Across Contract], [Contract Amount], blank())
```

#### Forecasted GP$ Across Contract
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "contract", [Forecasted GP$]), [contract])
```

#### Forecasted GP%_Contract
- Format string: `0.0%;-0.0%;0.0%`
```dax
divide([Forecasted GP$ Across Contract], [Contract Amount], blank())
```

#### GP% Difference_Contract
- Format string: `0.0%;-0.0%;0.0%`
```dax
if([Actual GP%_Contract] <> 0 && [Estimated GP%_Contract] <> 0, [Actual GP%_Contract] - [Estimated GP%_Contract], blank())
```

#### Actual GP$ Across Jobs_Contract
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "contract", [Total Revenue Recognized Across Jobs] , "cost", [Cumulative Actual Costs]),  [contract]-[cost])
```

#### Actual GP%_Contract
- Format string: `0.0%;-0.0%;0.0%`
```dax
divide([Actual GP$ Across Jobs_Contract], [Total Revenue Recognized Across Jobs], blank())
```

#### % Complete Variance
- Format string: `0.00%;-0.00%;0.00%`
```dax
if([% Complete Costs] > 0, [% Complete Schedule] - [% Complete Costs])
```

#### Forecasted Cost by Month
```dax
sumx(summarize('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "Start", calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract])), "End", calculate(max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract])), "Costs", divide([Forecasted Costs], 12, blank())), if([Start] >= min('Calendar'[Date]) && [End] <= max('Calendar'[Date]), [Costs], 0))
```

#### Cumulative Estimated Costs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	var start_ = calculate(max(CONTRACTS_D[CONTRACT_START_DATE]))

	var end_ = max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE])

	return

	calculate([Estimated Call Costs], filter(all('Calendar'), 'Calendar'[Date] >= start_ && 'Calendar'[Date] <= end_))
```

#### Date filter
- Format string: `0`
```dax
if(min('Calendar'[Date]) >= max(CONTRACTS_D[CONTRACT_START_DATE]) && max('Calendar'[Date]) <= max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), 1, 0)
```

#### Actual Labor Costs
```dax
calculate(sum(CALLS_F[COST_LABOR]), CALLS_F[In Current Contract] = 1)
```

#### Amount Billed
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
calculate(sum(CONTRACTS_BILLING_F[BILLABLE_ALL]), CONTRACTS_BILLING_F[In Current Contract] = 1)
```

#### Number of months since start
```dax
	

	//minx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "start", calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract]))), (Datediff([start], calculate(max('Calendar'[Date]),  'Calendar'[Date] <= today()), MONTH) ))

	var mx = max('Calendar'[Date])

	var mn = min('Calendar'[Date])

	return

	maxx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "start_", calculate(max(CONTRACTS_D[CONTRACT_START_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract])), "end_", calculate(max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), filter(CONTRACTS_D, CONTRACTS_D[Customer-Contract] = 'CONTRACTS MAPPING'[Customer-Contract]))), if([start_] >= mx, blank(), (Datediff([start_], mx, MONTH)+1)))
```

#### Available Budget_Contract
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Estimated Call Costs] - [Actual Costs]
```

#### Months Remaining
- Format string: `0`
```dax
if(max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]) = blank(), blank(), Datediff(today(), max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), MONTH) +1)
```

#### Costs Remaining - Current Run Rate
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
//Divide([Actual Costs], [Months Recognized], blank()) * [Months Remaining]

sumx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], "actual", [Actual Costs], "months", [Months Recognized], "remaining", [Months Remaining]), 

divide([actual], [months], blank()) * [remaining])
```

#### Available - Run Rate
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Available Budget_Contract Calls] - [Costs Remaining - Current Run Rate]
```

#### Estimated Call Costs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
 //Forecasted calls cost was originally built on forecast values but then after errors were found with Winnsoft, it was switched to estimated for the time being

calculate(sum('FORECASTED CALLS COST'[Value]), filter('FORECASTED CALLS COST', 'FORECASTED CALLS COST'[Cost Type] <> "HOURS" && 'FORECASTED CALLS COST'[In Current Contract] = 1))
```

#### Available Budget_Contract Calls
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Estimated Call Costs] - [Actual Costs]
```

#### Months test
- Format string: `0`
```dax
datediff(max(CONTRACTS_D[CONTRACT_START_DATE]), max(CONTRACTS_D[CONTRACT_EXPIRATION_DATE]), MONTH)
```

### CONTRACT_Hour_Breakout

#### Hour Breakout Sum
```dax
calculate(sum(CONTRACT_Hour_Breakout[Hours]), filter(CONTRACT_Hour_Breakout,  CONTRACT_Hour_Breakout[In Current Contract] = 1))
```

### CONTRACTS MAPPING

#### Selected Division
```dax
"Division : " & selectedvalue('CONTRACTS MAPPING'[Divisions], "Multiple")
```

#### Selected Sales Rep
```dax
"Sales Rep : " & selectedvalue('CONTRACTS MAPPING'[Sales Rep], "Multiple")
```

#### Selected Contract Name
```dax
"Contract : " & selectedvalue('CONTRACTS MAPPING'[CONTRACT_NUMBER], "Multiple Contracts")
```

#### Selected Customer Name
```dax
"Customer : " & selectedvalue(CUSTOMERS_D[CUSTOMER_NAME], "Multiple Customers")
```

#### Contract Start Date
```dax
"Start Date : " & max('CONTRACTS MAPPING'[Current Contract Start])
```

#### Contract Exp Date
```dax
"Exp Date : " & min('CONTRACTS MAPPING'[Current Contract Expiration])
```

### CONTRACTS_D

#### GP Percentage
- Format string: `0.00%;-0.00%;0.00%`
```dax
CALCULATE(SUM(CONTRACTS_D[Backlog GP])/SUM(CONTRACTS_D[Backlog Amount]))
```

#### Number of Projects
- Format string: `0`
```dax
CALCULATE(COUNT(CONTRACTS_D[CONTRACT_NUMBER_KEY]), CONTRACTS_D[Contract Status Date]="Active", CONTRACTS_D[CONTRACT_TYPE]="P")
```

#### Project Value
```dax
CALCULATE(SUM(CONTRACTS_D[ANNUAL_CONTRACT_VALUE]), CONTRACTS_D[Contract Status Date]="Active")
```

#### ROW_COUNT
- Format string: `0`
```dax
COUNTROWS(CONTRACTS_D)
```

#### YTD GP
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
SUM(CONTRACTS_D[Calculated Gross Profit])
```

### Cost Measures

#### Job_Actual Cost
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sum(JOB_COST_DETAILS_F[COST_AMT])
```

#### Cost Budget
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sum('JOB_COST_FORECASTS_F'[FORECAST_COSTS])
```

#### Original Cost Estimate
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sum(JOB_COST_SUMMARY_F[REVISED_ESTIMATED_COST])
```

#### Cumulative Forecast
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	return

	calculate([Cost Budget], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))
```

#### Cumulative Actual Cost
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	var maxdat = [Max Date]

	return

	calculate([Job_Actual Cost], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))
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
calculate([Cumulative Forecast], JOB_COST_DESCRIPTION_D[Contingency Flag] = "CONTINGENCY")
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
calculate(sum('POSTING_DATA_F'[DEBITAMT]), filter('POSTING_DATA_F', 'POSTING_DATA_F'[ACTNUMBR_1] = "340"))
```

#### Estimated Hours
- Format string: `#,0.0`
```dax
calculate(sum(JOB_COST_SUMMARY_F[COST_CODE_EST_UNIT]), JOB_COST_SUMMARY_F[COST_ELEMENT] = 1)
```

#### Total Hours
- Format string: `#,0.0`
```dax
	//sum(JOB_LABOR_HOURS[MONDAY]) + sum(JOB_LABOR_HOURS[TUESDAY]) + sum(JOB_LABOR_HOURS[WEDNESDAY]) + sum(JOB_LABOR_HOURS[THURSDAY]) + sum(JOB_LABOR_HOURS[FRIDAY])

	calculate(sum(JOB_LABOR_HOURS_F[TOTAL_HOURS]), JOB_LABOR_HOURS_F[Cost Element] = "Labor")
```

#### Hours Remaining
- Format string: `#,0.0`
```dax
[Estimated Hours] - [Total Hours]
```

#### Committed Cost
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
sum(JOB_COST_SUMMARY_F[COMMITTED_COST])
```

#### Cumulative Hours
- Format string: `0.0`
```dax
	

	var maxdat = [Max Date]

	return

	calculate([Total Hours], filter(all('Calendar'), 'Calendar'[Date] <= maxdat))
```

### Hour Measures

#### Actual Hours
```dax
sum(CONTRACTS_D[ACTUAL_HOURS])
```

#### Forecast Hours
- Format string: `#,0`
```dax
sum(CONTRACTS_D[FORECAST_HOURS])
```

#### Estimate Hours
- Format string: `#,0.00`
```dax
sum(CONTRACTS_D[ESTIMATE_HOURS])
```

#### Hour Difference
```dax
sumx(SUMMARIZE(CALLS_F, CALLS_F[SERVICE_CALL_ID], "estimate", [Service Call Estimated], "actual", [Service Call Actual]), [estimate] - [actual])
```

#### Hour Variance
- Format string: `0%;-0%;0%`
```dax
divide([Service Call Estimated] - [Service Call Actual], [Service Call Actual], blank())
```

#### Service Call Actual
- Format string: `#,0.00`
```dax
sum(APPOINTMENTS_F[ACTUAL_HOURS])
```

#### Service Call Estimated
- Format string: `#,0.00`
```dax
calculate(sum(CONTRACTS_TASK_SCHEDULE[Estimated Hours_]), USERELATIONSHIP(CALLS_F[SERVICE_CALL_ID], CONTRACTS_TASK_SCHEDULE[SERVICE_CALL_ID]))
```

#### Available Hours
- Format string: `#,0.00`
```dax
    calculate([Contract Estimated Hours] - [Service Call Actual])

    //, all(CALLS_F[STATUS_OF_CALL])) -- this fill ignore calls that are not completed and closed
```

#### Cumulative Actual Hours
```dax
	

	var maxdat = [Max Date]

	return

	  calculate([Service Call Actual], filter(all('Calendar'), 'Calendar'[Date] <= max('Calendar'[Date])))
```

#### Cumulative Estimated Hours
```dax
	

	var maxdat = [Max Date]

	return

	  calculate([Service Call Estimated], filter(all('Calendar'), 'Calendar'[Date] <= max('Calendar'[Date])))
```

#### Actual - Estimate Variance
- Format string: `0%;-0%;0%`
```dax
divide([Estimate Hours] - [Service Call Actual], [Service Call Actual], blank())
```

#### Contract Estimated Hours
```dax
calculate(sum(CONTRACTS_TASK_SCHEDULE[Estimated Hours_]), USERELATIONSHIP('CONTRACTS MAPPING'[Customer-Contract], CONTRACTS_TASK_SCHEDULE[Customer-Contract]), USERELATIONSHIP('Calendar'[Date], CONTRACTS_TASK_SCHEDULE[SCHEDULE_DATE]))
```

#### Hour Table Filter
- Format string: `0`
```dax
if([Service Call Actual] = blank() && [Service Call Estimated] = blank() && [Contract Estimated Hours] = blank(), 0, 1)
```

#### Contract to Date to Actual Hour Variance
- Format string: `0%;-0%;0%`
```dax
divide([Estimated Contract Hours to Date] - [Service Call Actual], [Service Call Actual], blank())
```

#### Estimated Contract Hours to Date
```dax
calculate([Contract Estimated Hours], filter('Calendar', 'Calendar'[Date] < today()))
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
sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], JOBS_D[ORIG_CONTRACT_AMOUNT]), JOBS_D[ORIG_CONTRACT_AMOUNT])
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
sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "CO", sum(CHANGE_ORDERS_BY_MONTH[CHANGE_ORDER_EST_COST])), [CO])
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
	

	sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "contract", [Cumulative Revenue YTD]), [contract])
```

#### Change Order $2
```dax
sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], JOBS_D[CONFIRMED_CHG_ORDER_AMT]), sum(JOBS_D[CONFIRMED_CHG_ORDER_AMT]))
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
	

	sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "contract", if([Forecasted GP $] <> BLank(), [Forecasted GP $], [Estimated GP $])), [contract])
```

#### Cumulative Current Contract
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "contract", [Current Contract Amount]), [contract])
```

#### Forecasted GP% Across Jobs
- Format string: `0.0%;-0.0%;0.0%`
```dax
divide([Forecasted GP$ Across Jobs], [Cumulative Current Contract], blank())
```

#### Estimated GP$ Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "contract", [Estimated GP $]), [contract])
```

#### Cumulative Original Contract
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "contract", [Original Contract]), [contract])
```

#### Estimated GP% Across Jobs
- Format string: `0.0%;-0.0%;0.0%`
```dax
divide([Estimated GP$ Across Jobs], [Cumulative Current Contract], blank())
```

#### Cumulative Rev Amount Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "contract", [Cumulative Revenue]), [contract])
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
	

	var compl = ROUND(divide('Cost Measures'[Job_Actual Cost] , [Cumulative Forecast], blank()),4)

	return

	[Current Contract Amount] * compl
```

#### Net Earned Rev Amount Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "contract", [Net Earned Revenue]), [contract])
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
sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "contract", 'Revenue Measures'[Net Earned Rev Amount TM], "lm", 'Revenue Measures'[Net Earned Rev Amount LM]), [contract] - [lm])
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

	calculate(sum(INVOICES_F[ACCOUNT_AMOUNT]), filter(all('Calendar'), 'Calendar'[Date] <= maxdat))
```

#### Over - Under Billed
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
[Cumulative Billed Amount] - [Cumulative Revenue]
```

#### Over Under Billed Across Jobs
```dax
	

	sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "contract", [Over - Under Billed]), [contract])
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
COUNTROWS(filter(summarize('JOBS_D', JOBS_D[JOB_NUMBER], "Under Billed", [Over - Under Billed]), [Under Billed] < 0))
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
([Current Contract Amount] * [% Complete]) - [Job_Actual Cost]
```

#### Actual GP$ Across Jobs
- Format string: `\$#,0;(\$#,0);\$#,0`
```dax
	

	sumx(SUMMARIZE(JOBS_D, JOBS_D[JOB_NUMBER], "contract", [Actual GP$]), [contract])
```

#### Display TM to LM Forecasted Change
```dax
"Total Change = " & Format([Forecasted GP $ TM to LM], "$#,##")
```
