#!/usr/bin/env python3
"""
Phase 1.1: Validate HVAC Export Regex Quality Against SDI

Tests whether hvacexport regex patterns actually match real SDI model numbers.
Generates quality reports to filter high-confidence rules for integration.
"""

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Add repository root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from msl.decoder.normalize import normalize_brand


# Equipment type mapping: HVAC export Category → SDI EquipmentType
EQUIPMENT_TYPE_MAPPING = {
    'air handler': ['Air Handling Unit', 'Air Handler'],
    'condenser': ['Cooling Condensing Unit', 'Heat Pump Condensing Unit'],
    'coil': ['Coil', 'Evaporator Coil'],
    'furnace': ['Furnace'],
    'package': ['Packaged Unit', 'Packaged Rooftop Unit'],
    'mini-split': ['Ductless Split System', 'Mini Split'],
    'multi': ['Multi-Zone', 'VRF'],
    'chiller': ['Chiller'],
    'boiler': ['Boiler'],
    'heat pump': ['Heat Pump Condensing Unit'],
    'ptac': ['PTAC', 'Packaged Terminal Air Conditioner'],
}


def extract_equipment_type_from_limitations(limitations: str) -> str:
    """
    Extract equipment type from limitations field.

    HVAC export stores category as "Category=Air Handler" in limitations.
    Returns normalized equipment type or empty string if not found.
    """
    if not limitations:
        return ""

    # Look for "Category=X" pattern
    if "Category=" in limitations:
        parts = limitations.split("Category=")
        if len(parts) > 1:
            # Extract up to first period or next sentence
            category = parts[1].split(".")[0].strip()
            # Normalize: lowercase, no extra spaces
            return category.lower().strip()

    return ""


def map_hvac_to_sdi_equipment_type(hvac_category: str) -> List[str]:
    """
    Map HVAC export category to SDI equipment type(s).

    Returns list of SDI equipment types that match the HVAC category.
    """
    if not hvac_category:
        return []

    hvac_norm = hvac_category.lower().strip()
    return EQUIPMENT_TYPE_MAPPING.get(hvac_norm, [])


def load_jsonl_candidates(path: Path) -> List[Dict]:
    """Load JSONL candidate rules."""
    candidates = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    return candidates


def load_sdi_equipment(path: Path, brand_filter: str = None) -> Dict[str, List[Dict]]:
    """
    Load SDI equipment model numbers grouped by brand.

    Returns:
        Dict[brand, List[{model, equipment_type}]]
    """
    equipment_by_brand = defaultdict(list)

    # Try multiple encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with path.open("r", encoding=encoding, errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    brand = normalize_brand(row.get("Make", "").strip())
                    model = row.get("ModelNumber", "").strip()
                    equipment_type = row.get("EquipmentType", "").strip()

                    if not brand or not model:
                        continue

                    # Filter by brand if specified
                    if brand_filter and normalize_brand(brand_filter) != brand:
                        continue

                    equipment_by_brand[brand].append({
                        'model': model,
                        'equipment_type': equipment_type
                    })
            break  # Success, exit loop
        except UnicodeDecodeError:
            if encoding == 'cp1252':
                raise  # Last attempt failed

    return equipment_by_brand


def test_regex_quality(
    rule: Dict,
    sdi_models: List[Dict]
) -> Tuple[int, int, List[str], List[str], int, str]:
    """
    Test a regex pattern against SDI model numbers (filtered by equipment type if applicable).

    Returns:
        (total_models, match_count, sample_matches, sample_non_matches, filtered_count, equipment_filter)
    """
    pattern = rule.get("model_regex", "")

    # Extract equipment type from rule
    limitations = rule.get("limitations", "")
    hvac_eq_type = extract_equipment_type_from_limitations(limitations)
    sdi_eq_types = map_hvac_to_sdi_equipment_type(hvac_eq_type)

    # Filter SDI models by equipment type if specified
    if sdi_eq_types:
        filtered_models = [
            m for m in sdi_models
            if m['equipment_type'] in sdi_eq_types
        ]
        equipment_filter = hvac_eq_type
    else:
        filtered_models = sdi_models
        equipment_filter = ""

    total_before_filter = len(sdi_models)
    total_after_filter = len(filtered_models)

    if not pattern:
        model_strings = [m['model'] for m in filtered_models[:5]]
        return total_after_filter, 0, [], model_strings, total_before_filter, equipment_filter

    try:
        regex = re.compile(pattern)
    except re.error:
        model_strings = [m['model'] for m in filtered_models[:5]]
        return total_after_filter, 0, [], model_strings, total_before_filter, equipment_filter

    matches = []
    non_matches = []

    for model_dict in filtered_models:
        model = model_dict['model']
        if regex.search(model):
            matches.append(model)
        else:
            non_matches.append(model)

    # Return samples
    sample_matches = matches[:10]
    sample_non_matches = non_matches[:10]

    return total_after_filter, len(matches), sample_matches, sample_non_matches, total_before_filter, equipment_filter


def calculate_status(match_rate: float, sample_size: int, min_threshold: float = 90.0) -> str:
    """
    Calculate rule status based on match rate and sample size.

    Status:
        GOOD: 90%+ match rate (if >10 samples) or 30%+ (if <=10 samples)
        WEAK: 10-30% match rate (needs review)
        POOR: <10% match rate (likely broken)
        NO_DATA: No SDI models to test against
    """
    if sample_size == 0:
        return "NO_DATA"

    if sample_size > 10:
        # High sample size: strict 90% threshold
        if match_rate >= min_threshold:
            return "GOOD"
        elif match_rate >= 30.0:
            return "WEAK"
        else:
            return "POOR"
    else:
        # Low sample size: relaxed threshold
        if match_rate >= 30.0:
            return "GOOD"
        elif match_rate >= 10.0:
            return "WEAK"
        else:
            return "POOR"


def main():
    parser = argparse.ArgumentParser(
        description="Validate HVAC export regex patterns against SDI model numbers"
    )
    parser.add_argument(
        "--candidates-jsonl",
        required=True,
        type=Path,
        help="Path to HVAC export candidates JSONL file",
    )
    parser.add_argument(
        "--sdi-csv",
        required=True,
        type=Path,
        help="Path to SDI equipment normalized CSV",
    )
    parser.add_argument(
        "--brand",
        help="Filter to specific brand (optional)",
    )
    parser.add_argument(
        "--min-threshold",
        type=float,
        default=90.0,
        help="Minimum match rate %% for GOOD status (default: 90.0, for >10 samples)",
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

    print("Loading HVAC export candidates...")
    candidates = load_jsonl_candidates(args.candidates_jsonl)
    print(f"Loaded {len(candidates)} candidate rules")

    # Filter candidates by brand if specified
    if args.brand:
        brand_norm = normalize_brand(args.brand)
        candidates = [c for c in candidates if normalize_brand(c.get("brand", "")) == brand_norm]
        print(f"Filtered to {len(candidates)} rules for brand: {args.brand}")

    print("\nLoading SDI equipment data...")
    equipment_by_brand = load_sdi_equipment(args.sdi_csv, args.brand)
    print(f"Loaded {len(equipment_by_brand)} brands from SDI")

    if args.brand:
        brand_norm = normalize_brand(args.brand)
        if brand_norm in equipment_by_brand:
            print(f"Filter: {brand_norm} has {len(equipment_by_brand[brand_norm])} models in SDI")
        else:
            print(f"Warning: Brand '{args.brand}' not found in SDI data")
            return

    # Test each rule
    print("\nValidating regex patterns...")
    quality_results = []
    detail_results = []

    for i, rule in enumerate(candidates, 1):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(candidates)} rules...")

        brand = normalize_brand(rule.get("brand", ""))
        attribute = rule.get("attribute_name", "")
        regex = rule.get("model_regex", "")

        # Get SDI models for this brand
        sdi_models = equipment_by_brand.get(brand, [])

        # Test regex (with equipment type filtering)
        total, matches, sample_matches, sample_non_matches, total_unfiltered, eq_filter = test_regex_quality(
            rule, sdi_models
        )

        match_rate = (matches / total * 100) if total > 0 else 0.0
        status = calculate_status(match_rate, total, args.min_threshold)

        # Quality report entry
        quality_results.append({
            "brand": brand,
            "attribute_name": attribute,
            "model_regex": regex,
            "equipment_filter": eq_filter,
            "sdi_models_total": total_unfiltered,
            "sdi_models_filtered": total,
            "matches_count": matches,
            "match_rate_pct": round(match_rate, 2),
            "status": status,
        })

        # Detail report entry (only for interesting cases)
        if matches > 0 or total <= 20:  # Include if has matches or small sample
            detail_results.append({
                "brand": brand,
                "attribute_name": attribute,
                "model_regex": regex,
                "equipment_filter": eq_filter,
                "status": status,
                "sdi_models_total": total_unfiltered,
                "sdi_models_filtered": total,
                "matches_count": matches,
                "match_rate_pct": round(match_rate, 2),
                "sample_matches": "; ".join(sample_matches[:5]),
                "sample_non_matches": "; ".join(sample_non_matches[:5]),
            })

    # Write quality report
    brand_safe = args.brand.lower().replace("/", "_").replace(" ", "_") if args.brand else None
    quality_report_path = args.output_dir / (
        f"{brand_safe}_regex_quality_report.csv" if brand_safe
        else "regex_quality_report.csv"
    )

    with quality_report_path.open("w", newline="", encoding="utf-8") as f:
        if quality_results:
            writer = csv.DictWriter(f, fieldnames=quality_results[0].keys())
            writer.writeheader()
            writer.writerows(quality_results)

    print(f"\nWrote quality report: {quality_report_path}")

    # Write detail report
    detail_report_path = args.output_dir / (
        f"{brand_safe}_regex_quality_details.csv" if brand_safe
        else "regex_quality_details.csv"
    )

    with detail_report_path.open("w", newline="", encoding="utf-8") as f:
        if detail_results:
            writer = csv.DictWriter(f, fieldnames=detail_results[0].keys())
            writer.writeheader()
            writer.writerows(detail_results)

    print(f"Wrote detail report: {detail_report_path}")

    # Summary statistics
    print("\n=== SUMMARY ===")
    status_counts = defaultdict(int)
    for result in quality_results:
        status_counts[result["status"]] += 1

    total_rules = len(quality_results)
    print(f"Total rules tested: {total_rules}")
    print(f"  GOOD: {status_counts['GOOD']} ({status_counts['GOOD']/total_rules*100:.1f}%)")
    print(f"  WEAK: {status_counts['WEAK']} ({status_counts['WEAK']/total_rules*100:.1f}%)")
    print(f"  POOR: {status_counts['POOR']} ({status_counts['POOR']/total_rules*100:.1f}%)")
    print(f"  NO_DATA: {status_counts['NO_DATA']} ({status_counts['NO_DATA']/total_rules*100:.1f}%)")

    # High-quality subset
    good_rules = [r for r in quality_results if r["status"] == "GOOD"]
    print(f"\nHigh-quality rules (GOOD status): {len(good_rules)}")
    print(f"Recommendation: Use {len(good_rules)} rules for integration")


if __name__ == "__main__":
    main()
