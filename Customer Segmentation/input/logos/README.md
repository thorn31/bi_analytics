Place local logo image files here when you want to source logos from disk (instead of web URLs).

Recommended:
- Use common formats: `.png` (preferred), `.jpg`
- Keep filenames simple; you will reference them from `logo_enrichment/TargetLogoHosted.csv` via the `Logo Path` column (relative paths are OK).

The pipeline will copy/rename these into `output/work/logos/staged_target/` using canonical-based blob names for upload.

