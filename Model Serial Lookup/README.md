# model-serial-lookup

Build an **offline, versioned** rule dictionary (by brand) for extracting useful equipment facts from:
- `Make` (manufacturer normalization)
- `SerialNumber` (manufacture date decoding)
- `ModelNumber` (generic attributes like capacity/voltage when explicitly documented)

Start with `docs/STATUS.md` and `docs/TODO.md`.

## Quick start

Prereqs: Python 3.10+

Most commands are stdlib-only. OCR helpers require `tesseract` + ImageMagick (`convert`).

Current recommended ruleset:
- Folder name is stored in `data/rules_normalized/CURRENT.txt` (see `docs/RULESETS.md`)

Recommended entry point:
- `python3 scripts/actions.py workflow.improve --input <labeled.csv> --tag <tag>`

Decode an equipment export:
- `python3 -m msl decode --input <input.csv> --output out/decoded.csv --attributes-output out/attributes_long.csv`

Continue the enrichment pipeline (high level):
- Phase 1 (Building-Center → rules): discover → fetch → extract → normalize → validate
- Phase 1 OCR (optional): `msl ocr-overrides` / `msl ocr-model-nomenclature` / `msl mine-ocr-attributes` → re-validate
- Phase 3 (assets → candidates): baseline → mine → audit → promote

Notes:
- All outputs are date-stamped folders (`YYYY-MM-DD`) to avoid overwrites.
- `evidence_excerpt` fields in CSVs are intentionally short previews; full context is in cached HTML and `guidance_text` for guidance rows.
