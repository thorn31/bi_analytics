# Service Call Management — Measure Explanations (How/Why)

Generated: 2026-01-22 EST

This document focuses on the **service-call** logic (per request) and explains how revenue and gross profit are computed in this report.

## Revenue definition (Service Calls)
This report does not appear to implement an “earned revenue” definition like the Mechanical Project Management model. Instead, revenue is effectively treated as **billings**:

- Revenue proxy = `Service Call Measures[Amount Billed] = sum('*CALL DETAILS'[BILLING_AMOUNT])`

### Revenue — data lineage (sources)
- Billings: model table `*CALL DETAILS` → Snowflake `DATA_WAREHOUSE.DW_FINAL.CALL_DETAILS_F` (Table) → column `BILLING_AMOUNT`
- Date context / fiscal year: model table `*Calendar` (model-generated date table; not sourced from Snowflake)

### FYTD revenue
- `Service Call Measures[Revenue FYTD_]` filters `Amount Billed` to the max selected fiscal year:
  - `var maxyear = calculate(max('*Calendar'[Fiscal Year]), ALLSELECTED('*Calendar'))`
  - `return calculate([Amount Billed], '*Calendar'[Fiscal Year] = maxyear)`

## Costs (Service Calls)
Costs are computed from an **unpivoted cost table** derived from the service call fact.

- `Service Call Measures[Actual Costs] = sum('*CALLS COSTS'[Value])`

### Costs — data lineage (sources)
- Base call fact: model table `*CALLS_F` → Snowflake `DATA_WAREHOUSE.DW_FINAL.CALLS_F` (Table)
- Cost breakdown: model table `*CALLS COSTS` is built in Power Query by unpivoting `CALLS_F` cost columns into `[Cost Type]` / `[Value]`
- Date context: `*Calendar` for FYTD calculations

### “Cumulative” cost behavior
- `Service Call Measures[Cumulative Actual Costs]` is a running total through the current selected date and returns blank for future dates (`if(max('*Calendar'[Date]) > today(), blank(), ...)`).

## Gross Profit (GP) — Service Calls
GP is computed as billings minus costs, and is constrained to **closed** calls.

### GP$ (dollars)
- `Service Call Measures[Actual GP$ _] = calculate([Amount Billed] - [Actual Costs], filter('*CALLS_F', '*CALLS_F'[STATUS_OF_CALL] = \"CLOSED\"))`

### GP% (margin)
- `Service Call Measures[Actual GP%] = divide([Actual GP$ _], calculate([Amount Billed], filter('*CALLS_F', '*CALLS_F'[STATUS_OF_CALL] = \"CLOSED\")), blank())`

### GP — data lineage (sources)
- Billings input: `*CALL DETAILS[BILLING_AMOUNT]` (`CALL_DETAILS_F`)
- Costs input: `*CALLS COSTS[Value]` (unpivoted from `CALLS_F`)
- Closed-call filter: `*CALLS_F[STATUS_OF_CALL]`
- Date context: `*Calendar` for FYTD / LY filters

### FYTD / LY GP
The model provides FYTD / LY variants that apply fiscal-year logic using `*Calendar[Fiscal Year]`:
- `GP$ FYTD`, `GP% FYTD`
- `GP$ FYTD LY`, `GP% FYTD LY`

## Notes / gotchas
- The report visuals reference a `Cash Flow Measures` table, but it does not exist in the exported semantic model TMDL. Any calculations depending on it should be treated as broken/orphaned until reconciled.
- `Revenue Measures` exists, but it is not the primary service-call revenue logic; it is barely used by visuals (only `Change Order $` observed).

