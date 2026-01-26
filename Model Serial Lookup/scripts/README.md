# scripts/

One-off utilities.

Current:
- `scripts/normalize_sdi.py`: legacy SDI export “column rename” helper.

Preferred (pipeline-native) approach:
- Use `python3 -m msl phase3-baseline` which automatically infers column mappings and writes
  a canonicalized dataset + baseline reports under `data/reports/<run-id>/`.
