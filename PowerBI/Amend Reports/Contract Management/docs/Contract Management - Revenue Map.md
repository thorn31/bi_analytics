# Contract Management — Revenue Map

Generated: 2026-01-22 15:10 EST

This maps report pages to the revenue definition(s) they use, based on measures referenced in `*.Report/definition/pages/**/visual.json`.

Note: this report contains some `metadata` strings referencing `Revenue Measures.*`, but there are no `queryRef` bindings to those measures in visuals, and the `Revenue Measures` DAX references missing model tables (e.g. `JOBS_D`). Treat them as copied/orphaned.

## Page mapping
| Page | Revenue definition(s) detected | Evidence (measures) |
|---|---|---|
| `Contract Profit Analysis` | Contract recognized revenue (schedule-based) | `Contract Measures[Contract Amount]`, `Contract Measures[Total Revenue Recognized Across Jobs]` |
| `Late PMs` | Contract recognized revenue (schedule-based) | `Contract Measures[Contract Amount]`, `Contract Measures[Total Revenue Recognized Across Jobs]`, `Contract Measures[Total Revenue Recognized]` |
| `Profitability & Revenue` | Contract recognized revenue (schedule-based) | `Contract Measures[Contract Amount]`, `Contract Measures[Total Revenue Recognized Across Jobs]`, `Contract Measures[Total Revenue Recognized]` |

## Quick reference formulas
- Contract revenue recognized (model): `Contract Measures[Total Revenue Recognized Across Jobs]` = `var mx = max('Calendar'[Date])
var mn = min('Calendar'[Date])
return
sumx(SUMMARIZE('CONTRACTS MAPPING', 'CONTRACTS MAPPING'[Customer-Contract], 
"amount", [Contract Amount], 
"rev", [Monthly Recognzied Revenue],
"xxx", Divide([Contract Amount] , dat...`
