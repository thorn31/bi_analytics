# PLAN_PHASE_2.MD — Build the Decoder Engine (Archived)

## Purpose
Implement a **deterministic decoder engine** that converts `(brand/make, model, serial)` into structured equipment attributes using the Phase 1 rule dictionaries.

Phase 2 focuses only on:
- Loading and validating rule dictionaries
- Decoding manufacture date from serial numbers
- Decoding model-derived attributes (where rules exist)
- Producing structured outputs with confidence + evidence

No Excel / Power Query / UI integration in this phase.

---

## Inputs
### Rule dictionaries (Phase 1 outputs)
- `SerialDecodeRule.csv`
- `AttributeDecodeRule.csv`

### Decoding inputs (for testing and demonstration)
- A small sample dataset (CSV/JSON) containing:
  - `AssetID` (or row id)
  - `Make` (optional but preferred)
  - `ModelNumber`
  - `SerialNumber`
  - `Description` (optional)

---

## Outputs
### A) Decoder library/module
A reusable module providing:
- rule loading
- rule validation
- decoding functions

### B) Decoder results (for sample runs)
- JSONL or CSV output (format doesn’t matter yet), containing:
  - decoded fields
  - confidence
  - evidence
  - source URL
  - decoder version

### C) Test suite + test report
- Unit tests validating decoding correctness using known examples
- Summary metrics for sample runs (decoded/partial/not decoded counts)

---

## Non-Goals
- No web browsing / scraping / external lookups
- No Excel/Power BI/Power Query integration
- No refrigerant inference or efficiency decoding
- No automatic resolution of decade ambiguity
- No “best guess” behavior—ambiguity must be surfaced

---

## Decoder Contract (v1)
For each input record, return:

### Identification
- `AssetID`
- `DetectedBrand` (normalized brand label)
- `MatchedSerialStyle` (nullable)
- `MatchedModelRule` (nullable)

### Manufacture date (from serial)
- `ManufactureYear` (nullable)
- `ManufactureMonth` (nullable)
- `ManufactureWeek` (nullable)
- `ManufactureDateAmbiguousDecade` (`true|false`)
- `ManufactureDateConfidence` (`High|Medium|Low|None`)
- `ManufactureDateEvidence` (short excerpt or structured explanation)
- `ManufactureDateSourceURL`
- (recommended) raw extracts for downstream disambiguation:
  - `ManufactureYearRaw`, `ManufactureMonthRaw`, `ManufactureWeekRaw` (nullable strings)

### Capacity (from model)
### Attributes (from model)
Return 0..N decoded attributes (examples: `NominalCapacityTons`, `MotorHP`, `FlowGPM`, `Voltage`, etc.).

Recommended output shape (one row per asset + JSON column OR one row per asset-attribute):
- `AttributesJSON` (JSON array of objects), where each object contains:
  - `AttributeName`
  - `Value`
  - `Units` (nullable)
  - `Confidence` (`High|Medium|None`)
  - `Evidence`
  - `SourceURL`

### Meta
- `DecoderVersion` (derived from ruleset version/date)
- `DecodeStatus` (`Decoded|Partial|NotDecoded`)
- `DecodeNotes` (optional)

---

## Step 1 — Normalize Inputs
Implement canonical normalization functions:

- `normalize_text(s)`:
  - trim
  - uppercase
  - collapse internal whitespace
- `normalize_serial(s)`:
  - apply `normalize_text`
  - remove spaces and common separators (`-`, `_`, `/`) if rules assume contiguous strings
- `normalize_model(s)`:
  - apply `normalize_text`
  - preserve separators if model rules depend on them; otherwise normalize similarly to serial

The engine must retain the original raw values for debugging but decode using normalized values.

---

## Step 2 — Load Rules
Implement loaders for:
- `SerialDecodeRule.csv`
- `AttributeDecodeRule.csv`

Rules must be loaded into in-memory structures keyed by normalized brand.

Required rule fields:
- Serial rules:
  - `rule_type` (`decode|guidance`)
  - `brand`, `style_name`, `serial_regex`, `date_fields`, `example_serials`,
    `decade_ambiguity.is_ambiguous`, `evidence_excerpt`, `source_url`, `retrieved_on`
  - optional evidence:
    - `image_urls` (JSON list; may contain chart/photo URLs)
  - for `rule_type=guidance`:
    - `guidance_action` (e.g., `contact_manufacturer`, `pattern_no_example`)
    - `guidance_text` (short user-facing message)
- Model rules:
### Attribute rules:
- `rule_type` (`decode|guidance`)
- `brand` or `oem_family`
- `model_regex` (nullable)
- `attribute_name`
- `value_extraction` (positions/pattern + transform)
- `units` (nullable)
- `examples`
- `limitations`, `evidence_excerpt`, `source_url`, `retrieved_on`

If Phase 1 outputs differ, implement a normalization layer that maps columns into the above.

Implementation note:
- `date_fields`, `example_serials`, `decade_ambiguity`, and other nested columns are stored as JSON strings in CSV and must be parsed.

---

## Step 3 — Validate Rules (Hard Gate)
Before decoding any assets, validate rules:

### Serial rule validation
- `serial_regex` compiles
- for `rule_type=decode`:
  - at least one example serial exists
  - example serials match `serial_regex`
  - `date_fields` extraction:
    - `positions` ranges (if used) are within example lengths
    - `pattern` regex (if used) compiles and matches examples
    - `requires_chart=true` means the field is not decodable without a chart/manual mapping
    - `mapping` tables (if used) are complete and non-empty
- for `rule_type=guidance`:
  - `guidance_action` and `guidance_text` present
  - `serial_regex` may be empty
  - `example_serials` may be empty

### Attribute rule validation
- if `model_regex` exists, it compiles
- examples match `model_regex` (if defined)
- position ranges (if used) are valid
- transforms yield plausible values on examples (attribute-specific bounds if applicable)

Rules failing validation must be excluded and written to a `rules_rejected` report.

---

## Step 4 — Brand Detection (Minimal v1)
Phase 2 should assume `Make` is provided most of the time.

Implement:
- `normalize_brand(make)`:
  - standardized labels (e.g., “CARRIER”, “TRANE”, “YORK”, “LENNOX”, “RHEEM”, “RUUD”, “GOODMAN”, “DAIKIN”, “AMANA”, “AAON”, “MITSUBISHI”, “LG”, “ICP”)
- if `Make` missing:
  - optional keyword detection using model/description (simple contains match)
  - otherwise brand = `Unknown`

Do not attempt complex manufacturer inference in Phase 2.

---

## Step 5 — Decode Manufacture Date from Serial
Algorithm:

1) Select candidate serial rules for brand
2) For each rule (deterministic order):
   - only consider `rule_type=decode` for matching
   - test `serial_regex` against normalized serial
   - if match:
     - extract year/month/week via `date_fields` definitions
     - set ambiguity flag if decade ambiguous
     - assign confidence:
       - `High` if unambiguous + complete date fields present
       - `Medium` if ambiguous decade OR partial mapping
       - `Low` if year only
     - record `MatchedSerialStyle`, evidence, source URL
     - stop (first-match-wins)
3) If none match:
   - if any `rule_type=guidance` rules exist for the brand, attach their `guidance_text` into `DecodeNotes` (or a dedicated field) and keep `ManufactureDateConfidence=None`
   - otherwise return nulls, `ManufactureDateConfidence=None`

No decade disambiguation is allowed in Phase 2.

Implementation note:
- When rules specify a 2-digit year (or other ambiguous encoding), Phase 2 may return `ManufactureYear` as the extracted integer value and MUST set `ManufactureDateAmbiguousDecade=true` and lower confidence accordingly. Downstream disambiguation (Phase 3+) can map to a full year using context.

---

## Step 6 — Decode Attributes from Model
Algorithm:

1) Select candidate attribute rules for brand
2) For each rule (deterministic order):
   - if `model_regex` provided, require match
   - extract attribute value from defined positions/pattern
   - apply transform (if defined)
   - assign confidence:
     - `High` if explicit digit-position rule with examples
     - `Medium` if limited scope or weaker constraints
     - `None` if no match
   - append attribute result (do not stop; multiple attributes may apply)
3) If none match: return empty attribute list

---

## Step 7 — Determine DecodeStatus
- `Decoded`: manufacture year present OR at least one attribute present, and no critical errors
- `Partial`: attempted but only some requested fields produced
- `NotDecoded`: no rules matched or inputs empty

(Exact criteria can be refined, but must be deterministic.)

---

## Step 8 — Testing
Create a unit test suite with:

### Rule-level tests
- regex compiles
- examples match
- extraction produces expected values (where known)

### Engine-level tests
- known serials for each major brand decode correctly
- decade ambiguous examples produce `ManufactureDateAmbiguousDecade = true`
- invalid serials do not decode (avoid false positives)
- normalization handles separators and casing

Produce a short test report:
- total tests
- pass/fail counts
- list of failing cases

---

## Step 9 — Minimal CLI (Optional but Useful)
Provide a small CLI to run decoding on a sample file:

- `decode --ruleset <path> --input <file> --output <file>`

CLI is optional, but if implemented:
- it must not fetch data from the internet
- it must log version, rule counts, and rejected rule counts

---

## Deliverables
1) Decoder module/library
2) Rule loader + validator
3) Unit tests + report
4) Sample decoding run output

---

## Exit Criteria
Phase 2 is complete when:
- Rules load and validate deterministically
- Decoder produces stable, repeatable outputs
- Test suite covers the top 10 brands and key edge cases
- Decoding does not produce false positives on invalid/unknown serials

End of Phase 2 Plan.
