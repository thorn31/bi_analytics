#!/bin/bash
#
# HVAC Export Integration Workflow
# Complete automation of Phase 1-3 integration process
#
# Usage:
#   ./scripts/run_hvacexport_integration_workflow.sh --brand TRANE [--dry-run]
#

set -e  # Exit on error

# Parse arguments
BRAND=""
DRY_RUN=false
MIN_QUALITY="GOOD"
NO_QUALITY_FILTER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --brand)
            BRAND="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --min-quality)
            MIN_QUALITY="$2"
            shift 2
            ;;
        --no-quality-filter)
            NO_QUALITY_FILTER=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 --brand BRAND [--dry-run] [--min-quality GOOD|WEAK] [--no-quality-filter]"
            exit 1
            ;;
    esac
done

if [ -z "$BRAND" ]; then
    echo "Error: --brand is required"
    echo "Usage: $0 --brand BRAND [--dry-run]"
    exit 1
fi

# Paths
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CANDIDATES_JSONL="$BASE_DIR/data/external_sources/hvacexport/2026-01-24_v3.84_enriched2/derived/runs/candidates__20260129T2245Z_relax_codes/AttributeDecodeRule.hvacexport.candidates.jsonl"
SDI_CSV="$BASE_DIR/data/equipment_exports/2026-01-25/sdi_equipment_normalized.csv"
CURRENT_RULES_DIR=$(cat "$BASE_DIR/data/rules_normalized/CURRENT.txt" | tr -d '\n\r')
CURRENT_RULES="$BASE_DIR/data/rules_normalized/$CURRENT_RULES_DIR/AttributeDecodeRule.csv"
VALIDATION_DIR="$BASE_DIR/data/validation/hvacexport"
BRAND_LOWER=$(echo "$BRAND" | tr '[:upper:]' '[:lower:]' | tr '/' '_' | tr ' ' '_')
OUTPUT_DIR="$BASE_DIR/data/rules_normalized/$(date +%Y-%m-%d)-hvacexport-${BRAND_LOWER}"

echo "=========================================="
echo "HVAC Export Integration Workflow"
echo "=========================================="
echo "Brand: $BRAND"
echo "Candidates: $CANDIDATES_JSONL"
echo "SDI Data: $SDI_CSV"
echo "Current Rules: $CURRENT_RULES"
echo "Output: $OUTPUT_DIR"
echo "Dry Run: $DRY_RUN"
echo "Quality Filter: $([ "$NO_QUALITY_FILTER" = true ] && echo 'DISABLED (supplementary mode)' || echo "ENABLED ($MIN_QUALITY)")"
echo ""

# Check dependencies
if [ ! -f "$CANDIDATES_JSONL" ]; then
    echo "Error: Candidates JSONL not found: $CANDIDATES_JSONL"
    exit 1
fi

if [ ! -f "$SDI_CSV" ]; then
    echo "Error: SDI CSV not found: $SDI_CSV"
    exit 1
fi

if [ ! -f "$CURRENT_RULES" ]; then
    echo "Error: Current rules not found: $CURRENT_RULES"
    exit 1
fi

mkdir -p "$VALIDATION_DIR"

# Phase 1.1: Validate Regex Quality
echo "=========================================="
echo "Phase 1.1: Validating Regex Quality"
echo "=========================================="

python3 scripts/validate_hvacexport_regex_quality.py \
    --candidates-jsonl "$CANDIDATES_JSONL" \
    --sdi-csv "$SDI_CSV" \
    --brand "$BRAND" \
    --min-threshold 90.0 \
    --output-dir "$VALIDATION_DIR"

QUALITY_REPORT="$VALIDATION_DIR/${BRAND_LOWER}_regex_quality_report.csv"

if [ ! -f "$QUALITY_REPORT" ]; then
    echo "Error: Quality report not generated"
    exit 1
fi

# Check if we have enough GOOD rules
GOOD_COUNT=$(grep -c ",GOOD$" "$QUALITY_REPORT" || echo 0)
echo ""
echo "Quality Report Summary:"
echo "  GOOD rules: $GOOD_COUNT"

if [ "$GOOD_COUNT" -eq 0 ]; then
    echo "Warning: No GOOD rules found for $BRAND"
    echo "Consider lowering --min-quality or reviewing regex patterns"
fi

# Phase 1.2: SDI Column Alignment
echo ""
echo "=========================================="
echo "Phase 1.2: SDI Column Alignment Analysis"
echo "=========================================="

python3 scripts/analyze_hvacexport_sdi_alignment.py \
    --candidates-jsonl "$CANDIDATES_JSONL" \
    --sdi-csv "$SDI_CSV" \
    --current-rules "$CURRENT_RULES" \
    --brand "$BRAND" \
    --output-dir "$VALIDATION_DIR"

ALIGNMENT_REPORT="$VALIDATION_DIR/${BRAND_LOWER}_sdi_column_alignment.csv"

if [ ! -f "$ALIGNMENT_REPORT" ]; then
    echo "Error: Alignment report not generated"
    exit 1
fi

# Check for conflicts
CONFLICT_REPORT="$VALIDATION_DIR/${BRAND_LOWER}_attribute_conflicts.csv"
if [ -f "$CONFLICT_REPORT" ]; then
    CONFLICT_COUNT=$(tail -n +2 "$CONFLICT_REPORT" | wc -l)
    echo ""
    echo "Conflicts found: $CONFLICT_COUNT"

    if [ "$CONFLICT_COUNT" -gt 0 ]; then
        echo "Review conflicts in: $CONFLICT_REPORT"
    fi
fi

# Phase 2.1: Merge Supplementary Rules
echo ""
echo "=========================================="
echo "Phase 2.1: Merging Supplementary Rules"
echo "=========================================="

if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] Would merge rules to: $OUTPUT_DIR/AttributeDecodeRule.csv"
    echo "[DRY RUN] Skipping actual merge"
else
    mkdir -p "$OUTPUT_DIR"

    # Build merge command
    MERGE_CMD="python3 scripts/merge_hvacexport_supplementary.py \
        --current-rules \"$CURRENT_RULES\" \
        --hvacexport-candidates \"$CANDIDATES_JSONL\" \
        --sdi-alignment \"$ALIGNMENT_REPORT\" \
        --brand \"$BRAND\" \
        --output \"$OUTPUT_DIR/AttributeDecodeRule.csv\" \
        --log \"$VALIDATION_DIR/${BRAND_LOWER}_integration_log.csv\""

    # Add quality filter args if not disabled
    if [ "$NO_QUALITY_FILTER" = false ]; then
        MERGE_CMD="$MERGE_CMD --quality-report \"$QUALITY_REPORT\" --min-quality \"$MIN_QUALITY\""
    else
        MERGE_CMD="$MERGE_CMD --no-quality-filter"
    fi

    # Execute merge
    eval $MERGE_CMD

    MERGED_RULES="$OUTPUT_DIR/AttributeDecodeRule.csv"

    if [ ! -f "$MERGED_RULES" ]; then
        echo "Error: Merged rules not generated"
        exit 1
    fi

    # Count added rules
    INTEGRATION_LOG="$VALIDATION_DIR/${BRAND_LOWER}_integration_log.csv"
    ADDED_COUNT=$(grep -c ",ADDED," "$INTEGRATION_LOG" || echo 0)

    echo ""
    echo "Integration Summary:"
    echo "  Rules added: $ADDED_COUNT"
    echo "  Merged ruleset: $MERGED_RULES"
fi

# Phase 2.2: Validate Against SDI
echo ""
echo "=========================================="
echo "Phase 2.2: Validating Against SDI Truth"
echo "=========================================="

if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] Would validate merged rules against SDI"
    echo "[DRY RUN] Skipping validation"
else
    python3 scripts/validate_merged_ruleset_attributes.py \
        --sdi-csv "$SDI_CSV" \
        --baseline-rules "$CURRENT_RULES" \
        --merged-rules "$MERGED_RULES" \
        --brand "$BRAND" \
        --output-dir "$VALIDATION_DIR"

    COMPARISON_REPORT="$VALIDATION_DIR/${BRAND_LOWER}_decode_accuracy_comparison.csv"

    if [ -f "$COMPARISON_REPORT" ]; then
        echo ""
        echo "Validation complete. Review:"
        echo "  Accuracy comparison: $COMPARISON_REPORT"

        MISMATCH_REPORT="$VALIDATION_DIR/${BRAND_LOWER}_decode_mismatches.csv"
        if [ -f "$MISMATCH_REPORT" ]; then
            MISMATCH_COUNT=$(tail -n +2 "$MISMATCH_REPORT" | wc -l)
            echo "  Mismatches: $MISMATCH_COUNT (see $MISMATCH_REPORT)"
        fi
    fi
fi

# Phase 3: Capacity Mapping (Optional)
echo ""
echo "=========================================="
echo "Phase 3: Capacity Code Mapping (Optional)"
echo "=========================================="
echo "To generate capacity code→tons mappings, run:"
echo ""
echo "  python scripts/hvacexport_generate_capacity_from_code_suggestions.py \\"
echo "    --snapshot-id 2026-01-24_v3.84_enriched2 \\"
echo "    --alignment-run-id <alignment_run_id> \\"
echo "    --min-support 10 \\"
echo "    --min-purity 90.0 \\"
echo "    --require-unique-truth \\"
echo "    --brands $BRAND"
echo ""
echo "Then re-run this workflow with the augmented candidates."

# Summary
echo ""
echo "=========================================="
echo "Integration Workflow Complete!"
echo "=========================================="

if [ "$DRY_RUN" = true ]; then
    echo "Dry run completed. Review validation reports in:"
    echo "  $VALIDATION_DIR"
    echo ""
    echo "To proceed with integration, run without --dry-run flag."
else
    echo "Validation reports:"
    echo "  Quality: $QUALITY_REPORT"
    echo "  Alignment: $ALIGNMENT_REPORT"
    echo "  Integration Log: $VALIDATION_DIR/${BRAND_LOWER}_integration_log.csv"
    echo "  Accuracy: $VALIDATION_DIR/${BRAND_LOWER}_decode_accuracy_comparison.csv"
    echo ""
    echo "Merged ruleset: $MERGED_RULES"
    echo ""
    echo "Next steps:"
    echo "  1. Review validation reports"
    echo "  2. If accuracy is good (>85%), update CURRENT.txt:"
    echo "     echo \"$(basename $OUTPUT_DIR)\" > data/rules_normalized/CURRENT.txt"
    echo "  3. Commit to git:"
    echo "     git add data/rules_normalized/$(basename $OUTPUT_DIR)/"
    echo "     git add data/validation/hvacexport/"
    echo "     git commit -m \"Integrate HVAC export rules for $BRAND\""
fi
