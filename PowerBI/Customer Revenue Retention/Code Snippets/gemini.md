# Gemini Agent Instructions

## Protocol & Interaction
- **Explain First:** Explain the process and plan first before making any changes to the codebase or model. Wait for user confirmation.
- **Tool Usage:** Always explain the specific tools and operations you intend to use *before* actually calling the MCP server or executing the tool.
- **Explicit Permission for Model Operations:** I require explicit permission before running any `mcp` server operations that interact directly with the model (e.g., `measure_operations`, `table_operations`, `relationship_operations`, `calculation_group_operations`, etc.).

## General Power BI Constraints & Preferences
- **Connection Naming:** Ensure Power BI file names (and window titles) do **not** contain periods `.` (e.g., use `v01` instead of `v0.1`). The connection tool fails validation if periods are present in the auto-generated connection name.
- **Modeling Philosophy:**
    - **Implicit Measures:** Default to allowing implicit measures (`discourageImplicitMeasures = false`). The user prefers dragging raw columns to visuals.
    - **Time Intelligence:** Prefer **Calculation Groups** for handling Time Intelligence patterns (e.g., Current/Previous periods).
- **UI/UX Standards:**
    - **Toggling:** Use **Bookmarks** (with "Data" unchecked) for toggling between different visual states (e.g., Simple vs. Advanced views).