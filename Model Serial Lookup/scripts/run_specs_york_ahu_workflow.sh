#!/usr/bin/env bash
set -euo pipefail

# End-to-end pilot workflow for YORK/JCI XT Air Handler spec sheets:
# 1) Extract embedded PDF text -> specs snapshot
# 2) Mine model-coded attribute candidates
# 3) Audit candidates against SDI where comparable
#
# Usage:
#   ./scripts/run_specs_york_ahu_workflow.sh --snapshot-id 2026-01-30-york-ahu --tag york-ahu
#
# Optional:
#   --sdi-csv <path>  (defaults to SDI normalized sample)
#   --candidates-dir <dir> (override default output candidates dir)

TAG="default"
SNAPSHOT_ID=""
SDI_CSV="data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv"
CANDIDATES_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) TAG="$2"; shift 2 ;;
    --snapshot-id) SNAPSHOT_ID="$2"; shift 2 ;;
    --sdi-csv) SDI_CSV="$2"; shift 2 ;;
    --candidates-dir) CANDIDATES_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$SNAPSHOT_ID" ]]; then
  echo "--snapshot-id is required" >&2
  exit 2
fi

PY="python3"
if [[ -x ".venv/bin/python" ]]; then
  PY=".venv/bin/python"
fi

echo "[1/3] Extract spec sheet text (snapshot: $SNAPSHOT_ID)"
$PY scripts/actions.py specs.extract_text --tag "$TAG" --snapshot-id "$SNAPSHOT_ID"

echo "[2/3] Mine York AHU candidates"
ARGS=(specs.mine_york_ahu --tag "$TAG" --snapshot-id "$SNAPSHOT_ID" --sdi-csv "$SDI_CSV")
if [[ -n "$CANDIDATES_DIR" ]]; then
  ARGS+=(--out-candidates-dir "$CANDIDATES_DIR")
fi
$PY scripts/actions.py "${ARGS[@]}"

OUT_DIR="$CANDIDATES_DIR"
if [[ -z "$OUT_DIR" ]]; then
  OUT_DIR="data/rules_discovered/spec_sheets/$SNAPSHOT_ID/candidates"
fi

echo "[3/3] Audit candidates vs SDI (where comparable)"
$PY scripts/actions.py eval.candidates --input "$SDI_CSV" --candidates-dir "$OUT_DIR" --tag "$TAG"

echo "Done."
echo "- candidates: $OUT_DIR"
