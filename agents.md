# AGENTS.md  
**Power BI (PBIP) Development — Modeling MCP**

## 1. Scope
This repository uses **Power BI Project (PBIP)** format.

The agent is authorized to create, modify, rename, and delete:
- measures
- columns
- tables
- relationships
- calculation groups
- perspectives
- display folders
- formatting strings and descriptions

Sweeping refactors are **allowed**, provided they are explicitly approved in chat.

---

## 2. Read vs Write Contract (Critical)
**Read / Inspect**
- The agent may read PBIP artifacts (including `.tmdl`) to understand:
  - model structure
  - dependencies
  - existing DAX
  - naming and foldering patterns

**Write / Apply Changes**
- All **semantic model changes** must be applied via the **Power BI Modeling MCP server connected to Power BI Desktop**.
- The agent must **not directly hand-edit `.tmdl` files** to implement logic.
- PBIP files are treated as **serialized outputs** of Desktop/model tooling.

**Intent:** ensure all changes are validated by the tabular engine and remain Desktop-compatible.

---

## 3. Change Workflow (Plan-Gated)
Sweeping changes are allowed, but must follow this sequence:

### 3.1 Plan (Required)
Before execution, the agent must propose:
- objects affected (tables, measures, relationships, calc groups)
- naming and foldering approach
- dependency impacts
- expected benefit (clarity, performance, consistency, etc.)

The agent must wait for explicit approval such as:
> “Approved”, “Proceed”, “Do it”

### 3.2 Execute
- Apply changes using Modeling MCP.
- If unexpected constraints arise, stop and request guidance.

### 3.3 Verify (Required)
After execution, the agent must:
- confirm the model loads successfully
- check for broken references
- validate a small representative set of measures
- summarize what changed and how it was validated

---

## 4. Measure Organization (General, Hierarchical)
All measures **must** be assigned to a display folder.

Use a **numbered, hierarchical folder system** so ordering is deterministic and portable.

### Folder Pattern
<Category>

1.1 <Subcategory>
2. <Category>
...

Examples (illustrative, not prescriptive):
- `1. Revenue`
- `2. Cost`
- `3. Gross Profit`
- `4. Operational Metrics`
- `5. Time Intelligence`
- `6. Parameters`
- `7. Helper`
- `8. Deprecated`

Rules:
- every measure goes in **exactly one** folder
- numbering controls order; names may evolve
- “Helper” = intermediate/non-reporting measures
- “Deprecated” = temporary compatibility; note in description

---

## 5. Measure Standards
- Measures should be **business-readable**.
- All measures must include:
  - description (purpose + assumptions)
  - format string (or documented intent)
  - display folder
- Prefer measures over calculated columns unless required for:
  - relationships
  - slicers
  - row-level behavior

---

## 6. DAX Best Practices
### 6.1 Validation
- After modifying measures, the agent must **execute DAX via MCP** to confirm correctness against the live model.

### 6.2 Design Guidance
Modeling MCP may apply some best-practice checks, but coverage is not assumed complete.

For non-trivial DAX design/refactors, the agent must follow established guidance from:
- SQLBI (filter context, relationships, performance)
- DAX Patterns (pattern-driven measure design)

### 6.3 Baseline Conventions
Unless overridden in the approved plan:
- prefer variables (`VAR`) for clarity and reuse
- avoid duplicated logic; refactor shared logic into helper measures
- avoid heavy iterators over large tables unless justified
- make filter context explicit where ambiguity exists
- include description + formatting for all measures

Performance-sensitive patterns (large iterators, ambiguous filter paths, many-to-many relationships) must be called out in the plan.

---

## 7. Relationships & Model Shape
- Prefer star schema patterns.
- Default to single-direction filtering.
- Many-to-many relationships require explicit justification.
- Hide technical keys and non-reporting columns by default.

---

## 8. DAX User-Defined Functions (UDFs)
DAX supports explicit **User-Defined Functions (UDFs)** (preview). If the feature is enabled in the connected Desktop model, the agent may define and use UDFs to reduce duplicated DAX logic. UDFs are defined with the `FUNCTION` keyword and can be called like native DAX functions. 

### 8.1 When to use UDFs
Prefer a DAX UDF when:
- the same logic is repeated across multiple measures
- the logic is stable and benefits from a single canonical definition
- using a UDF will materially improve maintainability and reduce copy/paste

Do **not** introduce UDFs for one-off measures.

### 8.2 Guardrails
- UDFs must be created/edited via **Modeling MCP** (engine-validated), not by hand-editing `.tmdl`.
- Keep UDFs small and single-purpose; avoid hidden dependencies on specific tables/columns unless necessary.
- If a UDF is model-dependent, document that dependency in its description.
- After introducing or changing a UDF, validate downstream measures by executing representative DAX via MCP.

### 8.3 Organization
- Store UDFs under a dedicated folder (example):
  - `7. Functions`
  - `7.1 Functions – Generic`
  - `7.2 Functions – Model-dependent`

---

## 9. Renames & Deletions
Renames and deletions are allowed **if included in the approved plan**.

The plan must specify:
- old → new name (if applicable)
- dependent objects affected
- whether deprecated compatibility objects are required temporarily

---

## 10. Report Layout Guardrail
- Do **not** modify report pages, visuals, bookmarks, or interactions unless explicitly requested.
- Focus on the **semantic model** by default.

---

## 11. Power Query (M) Guidance
Power Query edits are allowed but must remain **minimal and performance-aware**.

Rules:
- prefer folding-friendly steps; filter and remove columns early
- avoid row-by-row custom columns unless justified
- do not `Table.Buffer` by default
- keep step names meaningful
- reuse existing parameters; do not duplicate
- do not introduce machine-specific local file paths
- do not change credential or privacy behavior

If a change impacts folding or refresh duration, call it out in the plan.

---

## 12. Agent Behavior Expectations
- Do not invent business meaning without evidence in the model.
- Ask clarifying questions when intent is ambiguous.
- Keep changes intentional, explainable, and reversible.
