# GP Dashboard Context for Gemini Agent

## Key Model Entities:
- **Fact Table:** `QUADRA_JOBS`
- **Dimension Table (Jobs/Divisions):** `JOBS_D`
- **Custom Date Table:** `FYCalendar` (handles Fiscal Year/Month/Week logic)

## Implemented Patterns & Considerations:
- **Time Intelligence:** Implemented using a **Calculation Group** named `Period Select` (containing Current/Previous Week/Month/Fiscal Year).
- **Row Hiding with Calculation Groups:** Due to implicit measures being allowed and one-directional relationships, row-level filtering in table visuals for the `Period Select` Calculation Group is achieved using the `Period Filter Check` measure (set to "is 1" in visual-level filters).
- **Model Preference:** Implicit measures are **ALLOWED**. Avoid suggesting `discourageImplicitMeasures = true`.
- **Relationship Note:** `QUADRA_JOBS` -> `FYCalendar` is **One Direction**.
