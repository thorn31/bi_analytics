#!/usr/bin/env bash
set -euo pipefail

# End-to-end spec-sheet workflow:
# 1) Extract embedded PDF text -> specs snapshot
# 2) Mine deterministic AttributeDecodeRule candidates (supported miners)
# 3) Audit candidates against SDI where comparable
#
# Usage:
#   ./scripts/run_specs_snapshot_workflow.sh --snapshot-id 2026-01-30-specs-batch1 --tag specs

TAG="default"
SNAPSHOT_ID=""
SDI_CSV="data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) TAG="$2"; shift 2 ;;
    --snapshot-id) SNAPSHOT_ID="$2"; shift 2 ;;
    --sdi-csv) SDI_CSV="$2"; shift 2 ;;
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

echo "[2/3] Mine candidates from snapshot"
$PY scripts/actions.py specs.mine_snapshot --tag "$TAG" --snapshot-id "$SNAPSHOT_ID" --sdi-csv "$SDI_CSV"

OUT_DIR="data/rules_discovered/spec_sheets/$SNAPSHOT_ID/candidates"

echo "[3/3] Audit candidates vs SDI (where comparable)"
$PY scripts/actions.py eval.candidates --input "$SDI_CSV" --candidates-dir "$OUT_DIR" --tag "$TAG"

echo "Done."
echo "- candidates: $OUT_DIR"

