# Manual overrides (optional, archived)

Phase 1 normalization is conservative. When Building-Center uses charts/images for critical mappings (month-letter tables, etc.), the pipeline will emit `guidance` rules (often `chart_required`) rather than guessing.

To reduce guidance and make Phase 2 more effective, you can optionally provide **manual overrides** (transcribed once) that the validator will apply to convert guidance → deterministic decode rules.

## Serial overrides
File: `data/manual_overrides/serial_overrides.jsonl` (optional)

Each line is a JSON object:
```json
{
  "brand": "AllStyle",
  "style_name": "Style 1: 3 C 2 29 8461",
  "field": "month",
  "mapping": { "A": 1, "B": 2, "C": 3 },
  "positions": { "start": 2, "end": 2 }
}
```

Rules:
- `brand` and `style_name` must match the normalized rule row.
- `field` must be one of: `year`, `month`, `week`, `day`.
- Provide either:
  - `mapping` (code → value) plus `positions` or `pattern`, OR
  - just `positions`/`pattern` if the field was missing but is deterministically known.

## What the pipeline does with overrides
- During `msl validate`, overrides are applied *before* validation/export.
- If an override supplies a mapping for a `requires_chart=true` field, the field becomes deterministic.
- If a rule becomes fully deterministic, it may remain `decode`; otherwise it stays `guidance` with improved `date_fields`.

