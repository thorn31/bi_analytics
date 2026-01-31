#!/usr/bin/env python3
"""
Phase 2.1: Merge HVAC Export Supplementary Rules

Adds hvacexport rules to existing AttributeDecodeRule.csv without duplicating
or conflicting with building-center.org rules.

Integration Strategy:
1. Building-center.org rules = priority 1 (keep as-is)
2. HVAC export high-quality rules = priority 2 (add if no conflict)
3. Never overwrite existing building-center.org rules
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

# Add repository root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from msl.decoder.normalize import normalize_brand


def load_jsonl_candidates(path: Path) -> List[Dict]:
    """Load JSONL candidate rules."""
    candidates = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    return candidates


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


def normalize_equipment_types(equipment_types_json: str) -> set:
    """
    Parse and normalize equipment_types from JSON field.

    Returns set of lowercase, normalized equipment types.
    """
    if not equipment_types_json:
        return set()

    try:
        types = json.loads(equipment_types_json)
        if not isinstance(types, list):
            return set()
        return {t.lower().strip() for t in types if t and str(t).strip()}
    except (json.JSONDecodeError, ValueError):
        return set()


def load_current_rules(path: Path) -> tuple[List[Dict], Dict[str, Dict[str, Set[str]]]]:
    """
    Load existing AttributeDecodeRule.csv.

    Returns:
        (rules_list, coverage_index)
        coverage_index: Dict[brand, Dict[attribute_name, Set[equipment_types]]]
    """
    rules = []
    coverage = defaultdict(lambda: defaultdict(set))

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rules.append(row)

            brand = normalize_brand(row.get("brand", ""))
            attribute = row.get("attribute_name", "").strip()

            # Get equipment types from building-center.org rules
            eq_types = normalize_equipment_types(row.get("equipment_types", ""))

            if brand and attribute:
                # Store all equipment types for this brand+attribute
                coverage[brand][attribute].update(eq_types)
                # Also track if rule has no equipment type specified (applies to all)
                if not eq_types:
                    coverage[brand][attribute].add("")  # Empty = applies to all

    return rules, coverage


def load_alignment_mapping(path: Path) -> Dict[str, Dict]:
    """
    Load SDI column alignment mapping.

    Returns:
        Dict[hvacexport_attribute, alignment_info]
    """
    mapping = {}

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            attr = row.get("hvacexport_attribute", "").strip()
            if attr:
                mapping[attr] = {
                    "action": row.get("action", "").strip(),
                    "target_name": row.get("target_name", "").strip(),
                    "sdi_column": row.get("sdi_column", "").strip(),
                    "needs_mapping": row.get("needs_mapping", "").lower() == "true",
                    "needs_format_conversion": row.get("needs_format_conversion", "").lower() == "true",
                }

    return mapping


def load_quality_filter(path: Path, min_status: str = "GOOD") -> Set[tuple]:
    """
    Load regex quality report and filter for high-quality rules.

    Returns:
        Set[(brand, attribute, regex)] for rules meeting quality threshold
    """
    quality_set = set()

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get("status", "").strip()

            if status == min_status or (min_status == "GOOD" and status in ["GOOD", "WEAK"]):
                brand = normalize_brand(row.get("brand", ""))
                attribute = row.get("attribute_name", "").strip()
                regex = row.get("model_regex", "").strip()

                quality_set.add((brand, attribute, regex))

    return quality_set


def should_skip_rule(
    rule: Dict,
    current_coverage: Dict[str, Dict[str, Set[str]]],
    alignment: Dict[str, Dict],
    quality_filter: Set[tuple] = None,
    enforce_quality: bool = True,
    allow_conflicts: bool = False
) -> tuple[bool, str]:
    """
    Determine if an HVAC export rule should be skipped.

    Considers brand + attribute + equipment_type for conflicts.

    Returns:
        (should_skip, reason)
    """
    brand = normalize_brand(rule.get("brand", ""))
    attribute = rule.get("attribute_name", "").strip()
    regex = rule.get("model_regex", "").strip()

    # Extract equipment type from HVAC export rule
    limitations = rule.get("limitations", "")
    hvac_eq_type = extract_equipment_type_from_limitations(limitations)

    # Check alignment action (always enforce)
    if attribute in alignment:
        action = alignment[attribute].get("action")
        if action == "SKIP":
            return True, "SDI_ALIGNMENT_SKIP"

        # Get target name (may be renamed)
        target_name = alignment[attribute].get("target_name", attribute)
    else:
        target_name = attribute

    # Check if brand+attribute+equipment_type already exists in building-center.org (unless conflicts allowed)
    if not allow_conflicts and brand in current_coverage:
        # Check original attribute name
        if attribute in current_coverage[brand]:
            existing_eq_types = current_coverage[brand][attribute]
            # Conflict if:
            # 1. Building-center has no equipment type (applies to all)
            # 2. Building-center has same equipment type
            # 3. HVAC export has no equipment type (applies to all) and building-center has any
            if "" in existing_eq_types:
                # Building-center rule applies to all equipment types
                return True, "BUILDING_CENTER_HAS_ATTRIBUTE"
            elif hvac_eq_type and hvac_eq_type in existing_eq_types:
                # Same equipment type exists
                return True, f"BUILDING_CENTER_HAS_ATTRIBUTE_FOR_{hvac_eq_type.upper()}"
            elif not hvac_eq_type and existing_eq_types:
                # HVAC rule applies to all, but building-center has specific types
                return True, "BUILDING_CENTER_HAS_ATTRIBUTE"

        # Check if target name conflicts (with equipment type consideration)
        if target_name != attribute and target_name in current_coverage[brand]:
            existing_eq_types = current_coverage[brand][target_name]
            if "" in existing_eq_types:
                return True, "TARGET_NAME_CONFLICT"
            elif hvac_eq_type and hvac_eq_type in existing_eq_types:
                return True, f"TARGET_NAME_CONFLICT_FOR_{hvac_eq_type.upper()}"
            elif not hvac_eq_type and existing_eq_types:
                return True, "TARGET_NAME_CONFLICT"

    # Check quality filter (only if enforce_quality is True)
    if enforce_quality and quality_filter is not None:
        if (brand, attribute, regex) not in quality_filter:
            return True, "QUALITY_FILTER"

    return False, "INTEGRATE"


def convert_jsonl_to_csv_row(
    rule: Dict,
    alignment: Dict[str, Dict]
) -> Dict:
    """
    Convert JSONL rule to CSV row format.

    Applies attribute renaming based on SDI alignment.
    Extracts equipment type from limitations if not already populated.
    """
    brand = normalize_brand(rule.get("brand", ""))
    attribute = rule.get("attribute_name", "").strip()

    # Apply attribute renaming
    if attribute in alignment:
        target_name = alignment[attribute].get("target_name", attribute)
    else:
        target_name = attribute

    # Get equipment types - prefer existing field, fallback to parsing limitations
    equipment_types = rule.get("equipment_types", [])
    if not equipment_types:
        # Extract from limitations field
        eq_type = extract_equipment_type_from_limitations(rule.get("limitations", ""))
        if eq_type:
            # Capitalize for consistency with building-center.org format
            equipment_types = [eq_type.title()]

    return {
        "rule_type": rule.get("rule_type", "decode"),
        "brand": brand,
        "model_regex": rule.get("model_regex", ""),
        "attribute_name": target_name,
        "value_extraction": json.dumps(rule.get("value_extraction", {})),
        "units": rule.get("units", ""),
        "examples": json.dumps(rule.get("examples", [])),
        "limitations": rule.get("limitations", ""),
        "guidance_action": rule.get("guidance_action", ""),
        "guidance_text": rule.get("guidance_text", ""),
        "evidence_excerpt": rule.get("evidence_excerpt", ""),
        "source_url": rule.get("source_url", ""),
        "retrieved_on": rule.get("retrieved_on", ""),
        "image_urls": json.dumps(rule.get("image_urls", [])),
        "equipment_types": json.dumps(equipment_types),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Merge HVAC export supplementary rules into AttributeDecodeRule.csv"
    )
    parser.add_argument(
        "--current-rules",
        required=True,
        type=Path,
        help="Path to current AttributeDecodeRule.csv (building-center.org rules)",
    )
    parser.add_argument(
        "--hvacexport-candidates",
        required=True,
        type=Path,
        help="Path to HVAC export candidates JSONL",
    )
    parser.add_argument(
        "--sdi-alignment",
        required=True,
        type=Path,
        help="Path to SDI column alignment CSV (from analyze_hvacexport_sdi_alignment.py)",
    )
    parser.add_argument(
        "--quality-report",
        type=Path,
        help="Path to regex quality report CSV (optional filter)",
    )
    parser.add_argument(
        "--min-quality",
        default="GOOD",
        choices=["GOOD", "WEAK", "POOR"],
        help="Minimum quality status to integrate (default: GOOD includes GOOD+WEAK)",
    )
    parser.add_argument(
        "--no-quality-filter",
        action="store_true",
        help="Disable quality filtering - integrate all non-conflicting rules (supplementary mode)",
    )
    parser.add_argument(
        "--allow-conflicts",
        action="store_true",
        help="Allow HVAC export rules even if building-center.org has the same attribute (bypass conflict checking)",
    )
    parser.add_argument(
        "--brand",
        help="Filter to specific brand (optional)",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output path for merged AttributeDecodeRule.csv",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("data/validation/hvacexport/integration_log.csv"),
        help="Output path for integration log",
    )

    args = parser.parse_args()

    print("Loading current building-center.org rules...")
    current_rules, current_coverage = load_current_rules(args.current_rules)
    print(f"Loaded {len(current_rules)} existing rules")
    print(f"Coverage: {len(current_coverage)} brands")

    print("\nLoading HVAC export candidates...")
    candidates = load_jsonl_candidates(args.hvacexport_candidates)
    print(f"Loaded {len(candidates)} candidate rules")

    print("\nLoading SDI alignment mapping...")
    alignment = load_alignment_mapping(args.sdi_alignment)
    print(f"Loaded alignment for {len(alignment)} attributes")

    # Load quality filter (optional, unless --no-quality-filter is set)
    quality_filter = None
    enforce_quality = not args.no_quality_filter
    allow_conflicts = args.allow_conflicts

    if enforce_quality and args.quality_report and args.quality_report.exists():
        print(f"\nLoading quality filter from {args.quality_report}...")
        quality_filter = load_quality_filter(args.quality_report, args.min_quality)
        print(f"Quality filter: {len(quality_filter)} rules pass threshold")
    elif args.no_quality_filter:
        print(f"\nQuality filtering DISABLED - integrating all non-conflicting rules (supplementary mode)")

    if allow_conflicts:
        print(f"\nBuilding-center.org conflict checking DISABLED - will add all HVAC export rules")

    # Process candidates
    print("\nProcessing HVAC export candidates...")
    integration_log = []
    added_rules = []
    stats = defaultdict(int)

    for i, rule in enumerate(candidates, 1):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(candidates)} rules...")

        brand = normalize_brand(rule.get("brand", ""))
        attribute = rule.get("attribute_name", "").strip()

        # Filter by brand if specified
        if args.brand and normalize_brand(args.brand) != brand:
            continue

        # Check if should skip
        should_skip, reason = should_skip_rule(
            rule, current_coverage, alignment, quality_filter, enforce_quality, allow_conflicts
        )

        # Log decision
        integration_log.append({
            "brand": brand,
            "attribute_name": attribute,
            "model_regex": rule.get("model_regex", ""),
            "action": "SKIPPED" if should_skip else "ADDED",
            "reason": reason,
        })

        stats[reason] += 1

        if not should_skip:
            # Convert to CSV row and add
            csv_row = convert_jsonl_to_csv_row(rule, alignment)
            added_rules.append(csv_row)

            # Update coverage tracking (so subsequent rules know we added this)
            target_name = csv_row["attribute_name"]
            # Extract equipment type from the rule we just added
            eq_types = normalize_equipment_types(csv_row.get("equipment_types", ""))
            current_coverage[brand][target_name].update(eq_types)
            if not eq_types:
                current_coverage[brand][target_name].add("")  # Empty = applies to all

    # Write merged rules
    print(f"\nWriting merged ruleset to {args.output}...")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", newline="", encoding="utf-8") as f:
        # Use same fieldnames as current rules
        if current_rules:
            fieldnames = list(current_rules[0].keys())
        else:
            fieldnames = [
                "rule_type", "brand", "model_regex", "attribute_name",
                "value_extraction", "units", "examples", "limitations",
                "guidance_action", "guidance_text", "evidence_excerpt",
                "source_url", "retrieved_on", "image_urls", "equipment_types"
            ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Write existing rules first
        writer.writerows(current_rules)

        # Write added HVAC export rules
        writer.writerows(added_rules)

    print(f"Wrote {len(current_rules) + len(added_rules)} total rules")

    # Write integration log
    print(f"\nWriting integration log to {args.log}...")
    args.log.parent.mkdir(parents=True, exist_ok=True)

    with args.log.open("w", newline="", encoding="utf-8") as f:
        if integration_log:
            writer = csv.DictWriter(f, fieldnames=integration_log[0].keys())
            writer.writeheader()
            writer.writerows(integration_log)

    # Print summary
    print("\n=== INTEGRATION SUMMARY ===")
    print(f"Existing rules (building-center.org): {len(current_rules)}")
    print(f"Added rules (hvacexport): {len(added_rules)}")
    print(f"Total merged rules: {len(current_rules) + len(added_rules)}")

    print(f"\n=== SKIP REASONS ===")
    total_processed = sum(stats.values())
    for reason, count in sorted(stats.items(), key=lambda x: -x[1]):
        pct = count / total_processed * 100 if total_processed > 0 else 0
        print(f"  {reason}: {count} ({pct:.1f}%)")

    print(f"\n✓ Integration complete!")
    print(f"  Merged ruleset: {args.output}")
    print(f"  Integration log: {args.log}")


if __name__ == "__main__":
    main()
