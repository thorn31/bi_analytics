#!/usr/bin/env python3
"""
Phase 1.2: SDI Column Alignment Analysis

Maps HVAC export attributes to SDI column names and validates format compatibility.
Determines which attributes can be integrated and how they should be renamed.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

# Add repository root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from msl.decoder.normalize import normalize_brand


# SDI column names (from sdi_equipment_normalized.csv)
SDI_COLUMNS = {
    "KnownCapacityTons": 12,           # Truth data for cooling capacity
    "Refrigerant": 37,                  # Refrigerant type
    "Voltage (Volt-Phase)": 38,        # Electrical specifications (text format)
    "Cooling Capacity (Unit)": 13,
    "Cooling Efficiency (Value)": 14,
    "Cooling Efficiency (Rating)": 15,
    "Heating Capacity (Input)": 16,
    "Heating Fuel": 20,
    "Fan (HP)": 22,
    "Fan Flow (CFM)": 23,
}


# HVAC Export attribute naming conventions
HVAC_EXPORT_ATTRIBUTES = {
    # Capacity-related (needs unit conversion detection)
    "HVACExport_CoolingCode": {
        "description": "Raw cooling capacity code (no mapping)",
        "needs_mapping": True,
        "potential_sdi_column": "KnownCapacityTons",
        "unit_ambiguous": True,  # Could be tons, MBH, BTUH
    },
    "HVACExport_CoolingTonCode": {
        "description": "Cooling capacity code (ton-based)",
        "needs_mapping": True,
        "potential_sdi_column": "KnownCapacityTons",
        "unit_ambiguous": True,  # Usually MBH÷12 or direct tons
    },
    "HVACExport_CoolingMinCode": {
        "description": "Minimum cooling capacity code",
        "needs_mapping": True,
        "potential_sdi_column": None,
        "unit_ambiguous": True,
    },
    "HVACExport_CoolingMaxCode": {
        "description": "Maximum cooling capacity code",
        "needs_mapping": True,
        "potential_sdi_column": None,
        "unit_ambiguous": True,
    },
    "HVACExport_HeatingCode": {
        "description": "Raw heating capacity code (no mapping)",
        "needs_mapping": True,
        "potential_sdi_column": "Heating Capacity (Input)",
        "unit_ambiguous": True,
    },
    # Attributes that may match directly
    "Refrigerant": {
        "description": "Refrigerant type (e.g., R-410A)",
        "needs_mapping": False,
        "potential_sdi_column": "Refrigerant",
        "unit_ambiguous": False,
    },
    "VoltageVoltPhaseHz": {
        "description": "Voltage specification (V-P-Hz)",
        "needs_mapping": False,
        "potential_sdi_column": "Voltage (Volt-Phase)",
        "unit_ambiguous": False,
        "needs_format_conversion": True,  # Numeric → text format
    },
}


def load_jsonl_candidates(path: Path) -> List[Dict]:
    """Load JSONL candidate rules."""
    candidates = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    return candidates


def load_current_attribute_rules(path: Path) -> Dict[str, Set[str]]:
    """
    Load existing building-center.org attribute rules.

    Returns:
        Dict[brand, Set[attribute_names]]
    """
    rules_by_brand = defaultdict(set)

    if not path.exists():
        return rules_by_brand

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            brand = normalize_brand(row.get("brand", ""))
            attribute = row.get("attribute_name", "").strip()
            if brand and attribute:
                rules_by_brand[brand].add(attribute)

    return rules_by_brand


def load_sdi_columns(path: Path) -> List[str]:
    """Load SDI column names from CSV header."""
    # Try multiple encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with path.open("r", encoding=encoding, errors='replace') as f:
                reader = csv.reader(f)
                return next(reader)
        except UnicodeDecodeError:
            if encoding == 'cp1252':
                raise  # Last attempt failed
    return []


def determine_rename_action(attribute_name: str) -> Dict:
    """
    Determine how to handle an HVAC export attribute.

    Returns:
        {
            "action": "RENAME" | "KEEP" | "MATCH" | "SKIP",
            "target_name": str (if RENAME),
            "sdi_column": str (if maps to SDI),
            "needs_mapping": bool,
            "needs_format_conversion": bool,
            "reason": str
        }
    """
    # Check if attribute is in known HVAC export conventions
    if attribute_name in HVAC_EXPORT_ATTRIBUTES:
        info = HVAC_EXPORT_ATTRIBUTES[attribute_name]
        sdi_col = info.get("potential_sdi_column")

        if not sdi_col:
            # No SDI column exists
            return {
                "action": "KEEP",
                "target_name": attribute_name,
                "sdi_column": None,
                "needs_mapping": info.get("needs_mapping", False),
                "needs_format_conversion": False,
                "reason": "No SDI column for this attribute (intermediate code)",
            }

        if info.get("needs_mapping"):
            # Needs code→value mapping AND SDI column exists
            return {
                "action": "RENAME",
                "target_name": "NominalCapacityTons" if "Capacity" in sdi_col else sdi_col.replace(" ", ""),
                "sdi_column": sdi_col,
                "needs_mapping": True,
                "needs_format_conversion": False,
                "unit_ambiguous": info.get("unit_ambiguous", False),
                "reason": "Rename after mapping code→value (use capacity_from_codes script)",
            }

        if info.get("needs_format_conversion"):
            # Direct attribute but needs format conversion
            return {
                "action": "RENAME",
                "target_name": sdi_col.replace(" ", "").replace("(", "").replace(")", ""),
                "sdi_column": sdi_col,
                "needs_mapping": False,
                "needs_format_conversion": True,
                "reason": "Format conversion required (numeric → SDI text format)",
            }

        # Direct match
        return {
            "action": "MATCH",
            "target_name": attribute_name,
            "sdi_column": sdi_col,
            "needs_mapping": False,
            "needs_format_conversion": False,
            "reason": "Direct match with SDI column",
        }

    # Unknown attribute - flag for research
    return {
        "action": "SKIP",
        "target_name": attribute_name,
        "sdi_column": None,
        "needs_mapping": False,
        "needs_format_conversion": False,
        "reason": "Unknown attribute (needs manual research)",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze HVAC export attribute alignment with SDI columns"
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
        "--current-rules",
        type=Path,
        help="Path to current AttributeDecodeRule.csv (building-center.org rules)",
    )
    parser.add_argument(
        "--brand",
        help="Filter to specific brand (optional)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/validation/hvacexport"),
        help="Output directory for alignment reports",
    )

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading HVAC export candidates...")
    candidates = load_jsonl_candidates(args.candidates_jsonl)
    print(f"Loaded {len(candidates)} candidate rules")

    print("\nLoading SDI columns...")
    sdi_columns = load_sdi_columns(args.sdi_csv)
    print(f"SDI has {len(sdi_columns)} columns")

    print("\nLoading current building-center.org rules...")
    current_rules_by_brand = {}
    if args.current_rules and args.current_rules.exists():
        current_rules_by_brand = load_current_attribute_rules(args.current_rules)
        print(f"Loaded rules for {len(current_rules_by_brand)} brands")
    else:
        print("No current rules provided")

    # Analyze each unique attribute
    print("\nAnalyzing attribute alignment...")
    attribute_alignment = {}
    conflicts = []

    for rule in candidates:
        brand = normalize_brand(rule.get("brand", ""))
        attribute = rule.get("attribute_name", "")

        # Filter by brand if specified
        if args.brand and normalize_brand(args.brand) != brand:
            continue

        # Determine rename action (only analyze once per attribute)
        if attribute not in attribute_alignment:
            attribute_alignment[attribute] = determine_rename_action(attribute)

        # Check for conflicts with building-center.org
        if brand in current_rules_by_brand:
            existing_attrs = current_rules_by_brand[brand]

            # Check if brand+attribute already exists
            if attribute in existing_attrs:
                conflicts.append({
                    "brand": brand,
                    "attribute": attribute,
                    "hvacexport_regex": rule.get("model_regex", ""),
                    "conflict_type": "EXACT_MATCH",
                    "resolution": "SKIP hvacexport (building-center.org priority)",
                })

            # Check if target name would conflict
            target_name = attribute_alignment[attribute].get("target_name")
            if target_name and target_name in existing_attrs and target_name != attribute:
                conflicts.append({
                    "brand": brand,
                    "attribute": attribute,
                    "target_name": target_name,
                    "hvacexport_regex": rule.get("model_regex", ""),
                    "conflict_type": "TARGET_NAME_CONFLICT",
                    "resolution": "SKIP hvacexport (target name already exists)",
                })

    # Write alignment report
    brand_safe = args.brand.lower().replace("/", "_").replace(" ", "_") if args.brand else None
    alignment_path = args.output_dir / (
        f"{brand_safe}_sdi_column_alignment.csv" if brand_safe
        else "sdi_column_alignment.csv"
    )

    with alignment_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "hvacexport_attribute",
            "action",
            "target_name",
            "sdi_column",
            "needs_mapping",
            "needs_format_conversion",
            "unit_ambiguous",
            "reason",
        ])
        writer.writeheader()

        for attr, info in sorted(attribute_alignment.items()):
            writer.writerow({
                "hvacexport_attribute": attr,
                "action": info["action"],
                "target_name": info.get("target_name", ""),
                "sdi_column": info.get("sdi_column", ""),
                "needs_mapping": info.get("needs_mapping", False),
                "needs_format_conversion": info.get("needs_format_conversion", False),
                "unit_ambiguous": info.get("unit_ambiguous", False),
                "reason": info.get("reason", ""),
            })

    print(f"\nWrote alignment report: {alignment_path}")

    # Write conflict report
    if conflicts:
        conflict_path = args.output_dir / (
            f"{brand_safe}_attribute_conflicts.csv" if brand_safe
            else "attribute_conflicts.csv"
        )

        with conflict_path.open("w", newline="", encoding="utf-8") as f:
            if conflicts:
                writer = csv.DictWriter(f, fieldnames=conflicts[0].keys())
                writer.writeheader()
                writer.writerows(conflicts)

        print(f"Wrote conflict report: {conflict_path}")
        print(f"  Found {len(conflicts)} conflicts with building-center.org rules")

    # Summary
    print("\n=== ATTRIBUTE ALIGNMENT SUMMARY ===")
    action_counts = defaultdict(int)
    for info in attribute_alignment.values():
        action_counts[info["action"]] += 1

    total = len(attribute_alignment)
    print(f"Total unique attributes: {total}")
    print(f"  RENAME: {action_counts['RENAME']} ({action_counts['RENAME']/total*100:.1f}%) - Will map to SDI columns")
    print(f"  KEEP: {action_counts['KEEP']} ({action_counts['KEEP']/total*100:.1f}%) - Keep as intermediate codes")
    print(f"  MATCH: {action_counts['MATCH']} ({action_counts['MATCH']/total*100:.1f}%) - Direct SDI match")
    print(f"  SKIP: {action_counts['SKIP']} ({action_counts['SKIP']/total*100:.1f}%) - Needs research")

    print(f"\n=== INTEGRATION RECOMMENDATIONS ===")
    can_integrate = action_counts['RENAME'] + action_counts['MATCH']
    print(f"Can integrate: {can_integrate} attributes")
    print(f"Needs mapping: {sum(1 for i in attribute_alignment.values() if i.get('needs_mapping'))}")
    print(f"Needs format conversion: {sum(1 for i in attribute_alignment.values() if i.get('needs_format_conversion'))}")
    print(f"Unit ambiguous (needs capacity_from_codes): {sum(1 for i in attribute_alignment.values() if i.get('unit_ambiguous'))}")


if __name__ == "__main__":
    main()
