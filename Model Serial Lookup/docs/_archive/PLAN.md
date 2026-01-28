# PLAN.MD — Building-Center Rule Dictionary Build (Archived)

## Objective
Build a **local, versioned rule dictionary** by brand (Carrier/ICP, Trane, York/JCI, Lennox, Rheem/Ruud, Goodman/Amana/Daikin, AAON, Mitsubishi, LG) by extracting and normalizing relevant content from Building-Center (https://www.building-center.org/).

This is a **one-time ingestion** intended to seed:
- Serial number manufacture date decoding rules (primary)
- Model/tonnage decoding rules where explicitly documented (secondary)

The resulting dictionary will be used **offline** (no runtime dependency on Building-Center).

Project checklist / TODOs: `docs/TODO.md`

## Non-Goals
- Do not build a “live lookup” that scrapes Building-Center at runtime.
- Do not infer refrigerant, efficiency, voltage, etc. unless explicitly stated in the extracted source text.
- Do not “guess” decade/year in ambiguous serial formats; flag ambiguity.
- Do not rely on Building-Center as authoritative; treat as seed/reference. Store evidence and source URLs.

---

## Inputs
- Seed entry point: Building-Center HVAC table of contents page(s)
- Target brand list:
  - Carrier + ICP
  - Trane
  - York / Johnson Controls
  - Lennox
  - Rheem / Ruud
  - Goodman / Amana / Daikin
  - AAON
  - Mitsubishi
  - LG

## Outputs
### A) Raw archive (audit)
Store raw HTML (and any referenced images if needed) to ensure reproducibility.
- `data/raw_html/YYYY-MM-DD/<slug>.html`

### B) Extracted sections (semi-structured)
Per page, extract “style” sections and examples into JSONL:
- `data/extracted_sections/YYYY-MM-DD/<brand>__<page_type>.jsonl`

Each JSONL record should include:
- `brand`
- `page_type` (`hvac_age`, `tonnage_decoder`, `other`)
- `source_url`
- `retrieved_on` (ISO date)
- `section_title` (e.g., “Style 1”)
- `example_values` (serial examples or model examples)
- `section_text` (cleaned text)
- `section_html` (optional, but recommended)
- `has_images` (bool)
- `image_urls` (list)

### C) Normalized rule dictionary (machine-usable)
Produce two normalized datasets:

1) `SerialDecodeRule` (manufacture date parsing)
2) `AttributeDecodeRule` (model-derived attributes; capacity/tonnage is one attribute)

Store as CSV (or SQLite) under:
- `data/rules_normalized/YYYY-MM-DD/SerialDecodeRule.csv`
- `data/rules_normalized/YYYY-MM-DD/AttributeDecodeRule.csv`

---

## Strategy Overview
Use a **deterministic crawler + deterministic section extractor**, then an **agent-only normalization step** constrained to a strict schema, then a **deterministic validator** that rejects invalid or hallucinated rules.

### Pipeline
1. Discover target pages (TOC crawl)
2. Download and archive HTML
3. Extract relevant sections (styles/examples)
4. Agent: normalize extracted sections into strict rule JSON
5. Validate rules deterministically
6. Emit versioned rule dictionary artifacts + exception report

---

## Step 1 — Page Discovery
### Goal
Enumerate candidate pages for the target brands and classify them by type:
- HVAC age / serial decoding pages
- Tonnage decoder pages
- Other (ignore unless obviously relevant)

### Requirements
- Start from the HVAC TOC page(s).
- Collect URLs for each brand (prefer HVAC age pages).
- Record:
  - `brand`
  - `url`
  - `page_type_guess`
  - `discovered_on`

### Output
- `data/page_index/YYYY-MM-DD/page_index.csv`

---

## Step 2 — Deterministic HTML Download + Archival
### Goal
Fetch each URL once and cache locally.

### Requirements
- Cache every response (HTML) exactly as received.
- Use polite rate limiting and retries:
  - Single-threaded
  - Delay between requests (e.g., 1–2 seconds)
  - Retry with exponential backoff for transient failures
- Record HTTP status and timestamp.

### Output
- `data/raw_html/YYYY-MM-DD/*.html`
- `data/logs/YYYY-MM-DD/fetch_log.csv`

---

## Step 3 — Deterministic Section Extraction
### Goal
Convert each relevant page into sections that can be normalized into rules.

### HVAC Age pages (serial decoding)
Extract:
- “Style” sections (e.g., “Style 1”, “Style 2”, etc.)
- Any “Examples” list near top
- Any charts/tables references (month code mapping, etc.)
- Any warnings about ambiguity (e.g., “decade must be presumed”)

Heuristics (do not hardcode exact HTML unless necessary):
- Identify headings containing “Style” or equivalent repeated pattern.
- For each style heading:
  - collect text until next style heading of same level
- Extract serial examples:
  - from bullets containing patterns resembling serial strings
  - or explicit “Example:” blocks

### Tonnage decoder pages (model decoding)
Extract:
- Any explicit statement about which digits encode tonnage/capacity
- Any mapping logic or examples (e.g., “060 = 60,000 BTU/h”)
- Caveats/limitations (which product families it applies to)

### Output
- `data/extracted_sections/YYYY-MM-DD/<brand>__<page_type>.jsonl`

---

## Step 4 — Agent Normalization (Constrained)
### Goal
Translate each extracted section into strict rule objects without web access and without inference.

### Key Rule
The agent must only use the provided `section_text` / `example_values` and must not add facts.

### A) SerialDecodeRule schema (minimum viable)
Each rule MUST include:
- `brand`
- `style_name`
- `serial_regex` (string)
- `date_fields` (object)
  - `year` (object) with one of:
    - `positions` (1-based inclusive range, e.g., `{"start": 3, "end": 4}`)
    - OR `pattern` (regex + capture group for variable/relative extraction)
    - OR `mapping` (e.g., letter → month; referenced inline)
    - OR `requires_chart: true` when the page indicates a letter-code but the mapping table is only in an image/chart
  - `month` or `week` or `day` (object) same structure
  - optional `transform` when explicitly stated (e.g., reverse digits)
- `example_serials` (array)
- `decade_ambiguity` (object)
  - `is_ambiguous` (bool)
  - `notes` (string)
- `evidence_excerpt` (<= 200 chars; direct quote fragment)
- `source_url`
- `retrieved_on`
 - `image_urls` (optional; evidence links for charts/photos)

### B) ModelDecodeRule schema (minimum viable)
### B) AttributeDecodeRule schema (minimum viable)
Each rule MUST include:
- `rule_type` (`decode|guidance`)
- `brand` or `oem_family`
- `model_regex` (optional; if not safe, set null)
- `attribute_name` (e.g., `NominalCapacityTons`, `MotorHP`, `FlowGPM`, `Voltage`)
- `value_extraction` (object)
  - `positions` (range) OR `pattern`
  - `data_type` (`Number` or `Text`)
  - `mapping` (optional; e.g., code → value)
  - `transform` (optional; e.g., `value = code * 1000`, `value = value/12000`)
- `units` (optional; e.g., `Tons`, `BTUH`, `HP`, `GPM`, `V`)
- `examples` (array)
- `limitations` (string)
- `evidence_excerpt`
- `source_url`
- `retrieved_on`

### Output
- `data/rules_staged/YYYY-MM-DD/serial_rules.jsonl`
- `data/rules_staged/YYYY-MM-DD/model_rules.jsonl`

---

## Step 5 — Deterministic Validation (Reject Hallucinations)
### Goal
Ensure staged rules are internally consistent and match provided examples.

### SerialDecodeRule validation
For each rule:
1. `serial_regex` compiles
2. Each `example_serial` matches `serial_regex`
3. Any declared `positions` are within bounds of example serial lengths
4. Extracted `year/month/week/day` values are numeric where expected
5. Range checks:
   - `month` 1–12
   - `week` 1–53
   - `year` within configurable bounds (e.g., 1960–current year)
6. If `decade_ambiguity.is_ambiguous = true`, ensure the output marks the decoded year as “needs disambiguation” in downstream usage (dictionary flag)

### ModelDecodeRule validation
### AttributeDecodeRule validation
For each rule:
1. If `model_regex` provided, it compiles
2. Each example model matches `model_regex` (if present)
3. Value extraction works on examples
4. If numeric, transformation yields plausible outputs (configurable per attribute)

### Outputs
- `data/rules_normalized/YYYY-MM-DD/SerialDecodeRule.csv`
- `data/rules_normalized/YYYY-MM-DD/AttributeDecodeRule.csv`
- `data/reports/YYYY-MM-DD/validation_exceptions.jsonl`

Only validated rules progress into the normalized dictionary.

---

## Step 6 — Exception Handling Workflow
### Goal
Keep the process unattended; only surface records requiring human review.

Exception categories:
- Section contains image-based mapping with insufficient text to encode mapping
- Serial style ambiguous and cannot be represented deterministically (must be flagged)
- Page structure prevents style extraction
- Agent output fails schema or validation

Output:
- `data/reports/YYYY-MM-DD/review_queue.csv` with:
  - `brand`
  - `source_url`
  - `section_title`
  - `issue_type`
  - `notes`
  - `raw_html_path`

---

## Data Governance and Versioning
- Every run writes to a new date-stamped folder.
- Rules include `retrieved_on` and `source_url`.
- Maintain a `decoder_version` in downstream usage (derived from folder date).
- Do not overwrite previous runs.

---

## Quality Gates
A run is considered successful if:
- ≥ 90% of target brand pages are fetched and archived
- ≥ 80% of extracted style sections produce validated `SerialDecodeRule` objects
- All validated rules have evidence + source URL + retrieved date
- Review queue is generated and non-empty when needed (no silent failures)

---

## Downstream Integration Notes (for later)
- Join rules to assets by `brand` first, then test serial against `serial_regex` to select style.
- Output decoded fields with:
  - `DecodedManufactureYear`
  - `DecodedManufactureMonth` or `Week`
  - `DecodeConfidence` (High/Medium/Low)
  - `DecodeEvidence` and `SourceURL`
- Do not auto-resolve decade ambiguity; require a separate disambiguation rule or contextual data.

---

## Deliverables Summary
1. Raw HTML archive (audit trail)
2. Extracted section JSONL files (replayable intermediate)
3. Validated normalized rule CSVs
4. Exception report + review queue

End of plan.
