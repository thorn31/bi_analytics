#!/usr/bin/env python3
"""
Phase 2.2: Validate Merged Ruleset Against SDI Truth Data

Tests merged ruleset (building-center.org + hvacexport) against SDI equipment
to measure attribute decode accuracy improvements.
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

# Add repository root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from msl.decoder.attributes import decode_attributes
from msl.decoder.io import load_attribute_rules_csv
from msl.decoder.normalize import normalize_brand


# Validation mappings: decoded attribute → SDI truth column
VALIDATION_MAPPINGS = {
    "NominalCapacityTons": "KnownCapacityTons",
    "Refrigerant": "Refrigerant",
    "VoltageVoltPhaseHz": "Voltage (Volt-Phase)",
    "Voltage": "Voltage (Volt-Phase)",
    "CoolingEfficiencyValue": "Cooling Efficiency (Value)",
    "HeatingFuel": "Heating Fuel",
}


def load_sdi_equipment(path: Path, brand_filter: str = None) -> List[Dict]:
    """Load SDI equipment with truth data."""
    equipment = []

    # Try multiple encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with path.open("r", encoding=encoding, errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    brand = normalize_brand(row.get("Make", "").strip())

                    # Filter by brand if specified
                    if brand_filter and normalize_brand(brand_filter) != brand:
                        continue

                    equipment.append({
                        "brand": brand,
                        "model": row.get("ModelNumber", "").strip(),
                        "equipment_type": row.get("EquipmentType", "").strip(),
                        "sdi_data": row,  # Keep all SDI columns for validation
                    })
            break  # Success, exit loop
        except UnicodeDecodeError:
            if encoding == 'cp1252':
                raise  # Last attempt failed

    return equipment


def normalize_value(value: str) -> str:
    """Normalize value for comparison (lowercase, strip spaces)."""
    if not value:
        return ""
    return str(value).lower().strip()


def compare_values(decoded: str, truth: str, attribute: str) -> bool:
    """
    Compare decoded value with SDI truth value.

    Returns True if values match (within tolerance).
    """
    decoded_norm = normalize_value(decoded)
    truth_norm = normalize_value(truth)

    if not truth_norm:
        return False  # No truth data to compare

    # Exact match
    if decoded_norm == truth_norm:
        return True

    # Numeric comparison (for capacity, efficiency, etc.)
    if attribute in ["NominalCapacityTons", "CoolingEfficiencyValue"]:
        try:
            decoded_num = float(decoded)
            truth_num = float(truth)

            # Allow 5% tolerance for numeric values
            tolerance = abs(truth_num * 0.05)
            return abs(decoded_num - truth_num) <= tolerance
        except (ValueError, TypeError):
            pass

    # Voltage format variations (e.g., "208-3-60" vs "208V - Three Phase")
    if attribute in ["VoltageVoltPhaseHz", "Voltage"]:
        # Extract voltage number
        decoded_voltage = re.search(r"(\d+)", decoded_norm)
        truth_voltage = re.search(r"(\d+)", truth_norm)

        if decoded_voltage and truth_voltage:
            return decoded_voltage.group(1) == truth_voltage.group(1)

    # Refrigerant variations (e.g., "R410A" vs "R-410A")
    if attribute == "Refrigerant":
        decoded_clean = decoded_norm.replace("-", "").replace(" ", "")
        truth_clean = truth_norm.replace("-", "").replace(" ", "")
        return decoded_clean == truth_clean

    return False


def validate_equipment_decodes(
    equipment: List[Dict],
    rules_path: Path,
    validation_mappings: Dict[str, str]
) -> Dict:
    """
    Validate attribute decodes against SDI truth data.

    Returns:
        {
            "total_equipment": int,
            "by_attribute": {
                attribute_name: {
                    "decoded_count": int,
                    "with_truth": int,
                    "correct": int,
                    "incorrect": int,
                    "accuracy_pct": float,
                    "mismatches": List[Dict]
                }
            }
        }
    """
    print(f"Loading rules from {rules_path}...")
    rules = load_attribute_rules_csv(rules_path)
    print(f"Loaded {len(rules)} attribute rules")

    print(f"\nValidating {len(equipment)} equipment records...")

    results = {
        "total_equipment": len(equipment),
        "by_attribute": defaultdict(lambda: {
            "decoded_count": 0,
            "with_truth": 0,
            "correct": 0,
            "incorrect": 0,
            "mismatches": [],
        })
    }

    for i, eq in enumerate(equipment, 1):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(equipment)} records...")

        brand = eq["brand"]
        model = eq["model"]
        sdi_data = eq["sdi_data"]

        # Decode attributes
        decoded = decode_attributes(brand, model, rules)

        # Validate each decoded attribute
        for attr_name, attr_value in decoded.items():
            if attr_name not in validation_mappings:
                continue  # No validation mapping for this attribute

            sdi_column = validation_mappings[attr_name]
            truth_value = sdi_data.get(sdi_column, "").strip()

            attr_stats = results["by_attribute"][attr_name]
            attr_stats["decoded_count"] += 1

            if truth_value:
                attr_stats["with_truth"] += 1

                # Compare values
                is_correct = compare_values(str(attr_value), truth_value, attr_name)

                if is_correct:
                    attr_stats["correct"] += 1
                else:
                    attr_stats["incorrect"] += 1

                    # Record mismatch (limit to 100 per attribute)
                    if len(attr_stats["mismatches"]) < 100:
                        attr_stats["mismatches"].append({
                            "brand": brand,
                            "model": model,
                            "decoded_value": str(attr_value),
                            "truth_value": truth_value,
                        })

    # Calculate accuracy percentages
    for attr_name, stats in results["by_attribute"].items():
        if stats["with_truth"] > 0:
            stats["accuracy_pct"] = stats["correct"] / stats["with_truth"] * 100
        else:
            stats["accuracy_pct"] = 0.0

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate merged ruleset against SDI truth data"
    )
    parser.add_argument(
        "--sdi-csv",
        required=True,
        type=Path,
        help="Path to SDI equipment normalized CSV",
    )
    parser.add_argument(
        "--baseline-rules",
        required=True,
        type=Path,
        help="Path to baseline AttributeDecodeRule.csv (before hvacexport)",
    )
    parser.add_argument(
        "--merged-rules",
        required=True,
        type=Path,
        help="Path to merged AttributeDecodeRule.csv (after hvacexport)",
    )
    parser.add_argument(
        "--brand",
        help="Filter to specific brand (optional)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/validation/hvacexport"),
        help="Output directory for validation reports",
    )

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading SDI equipment data...")
    equipment = load_sdi_equipment(args.sdi_csv, args.brand)
    print(f"Loaded {len(equipment)} equipment records")

    # Validate baseline rules
    print("\n=== VALIDATING BASELINE RULES ===")
    baseline_results = validate_equipment_decodes(
        equipment, args.baseline_rules, VALIDATION_MAPPINGS
    )

    # Validate merged rules
    print("\n=== VALIDATING MERGED RULES ===")
    merged_results = validate_equipment_decodes(
        equipment, args.merged_rules, VALIDATION_MAPPINGS
    )

    # Generate comparison report
    print("\n=== GENERATING COMPARISON REPORT ===")

    comparison = []
    all_attributes = set(baseline_results["by_attribute"].keys()) | set(merged_results["by_attribute"].keys())

    for attr in sorted(all_attributes):
        baseline_stats = baseline_results["by_attribute"].get(attr, {})
        merged_stats = merged_results["by_attribute"].get(attr, {})

        comparison.append({
            "attribute_name": attr,
            "sdi_column": VALIDATION_MAPPINGS.get(attr, ""),
            "baseline_decoded_count": baseline_stats.get("decoded_count", 0),
            "baseline_with_truth": baseline_stats.get("with_truth", 0),
            "baseline_correct": baseline_stats.get("correct", 0),
            "baseline_accuracy_pct": round(baseline_stats.get("accuracy_pct", 0), 2),
            "merged_decoded_count": merged_stats.get("decoded_count", 0),
            "merged_with_truth": merged_stats.get("with_truth", 0),
            "merged_correct": merged_stats.get("correct", 0),
            "merged_accuracy_pct": round(merged_stats.get("accuracy_pct", 0), 2),
            "improvement_decoded": merged_stats.get("decoded_count", 0) - baseline_stats.get("decoded_count", 0),
            "improvement_correct": merged_stats.get("correct", 0) - baseline_stats.get("correct", 0),
        })

    # Write comparison report
    brand_safe = args.brand.lower().replace("/", "_").replace(" ", "_") if args.brand else None
    comparison_path = args.output_dir / (
        f"{brand_safe}_decode_accuracy_comparison.csv" if brand_safe
        else "decode_accuracy_comparison.csv"
    )

    with comparison_path.open("w", newline="", encoding="utf-8") as f:
        if comparison:
            writer = csv.DictWriter(f, fieldnames=comparison[0].keys())
            writer.writeheader()
            writer.writerows(comparison)

    print(f"Wrote comparison report: {comparison_path}")

    # Write mismatch report (merged only)
    mismatches = []
    for attr, stats in merged_results["by_attribute"].items():
        for mismatch in stats["mismatches"]:
            mismatches.append({
                "attribute_name": attr,
                "sdi_column": VALIDATION_MAPPINGS.get(attr, ""),
                **mismatch
            })

    if mismatches:
        mismatch_path = args.output_dir / (
            f"{brand_safe}_decode_mismatches.csv" if brand_safe
            else "decode_mismatches.csv"
        )

        with mismatch_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=mismatches[0].keys())
            writer.writeheader()
            writer.writerows(mismatches)

        print(f"Wrote mismatch report: {mismatch_path}")

    # Print summary
    print("\n=== VALIDATION SUMMARY ===")
    print(f"Total equipment records: {len(equipment)}")

    for attr in sorted(all_attributes):
        baseline_stats = baseline_results["by_attribute"].get(attr, {})
        merged_stats = merged_results["by_attribute"].get(attr, {})

        print(f"\n{attr}:")
        print(f"  Baseline: {baseline_stats.get('decoded_count', 0)} decoded, "
              f"{baseline_stats.get('correct', 0)} correct "
              f"({baseline_stats.get('accuracy_pct', 0):.1f}% accuracy)")
        print(f"  Merged:   {merged_stats.get('decoded_count', 0)} decoded, "
              f"{merged_stats.get('correct', 0)} correct "
              f"({merged_stats.get('accuracy_pct', 0):.1f}% accuracy)")

        improvement = merged_stats.get("decoded_count", 0) - baseline_stats.get("decoded_count", 0)
        if improvement > 0:
            print(f"  → Improvement: +{improvement} decodes")


if __name__ == "__main__":
    main()
