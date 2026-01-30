#!/usr/bin/env python3
"""
Apply manual fixes to SerialDecodeRule.csv after promotion.

This script should be run after phase3-promote to ensure critical manual
fixes persist across ruleset updates. It modifies rules in-place based on
a registry of known fixes.

Usage:
    python3 scripts/apply_manual_serial_fixes.py --ruleset-dir <path>

Or use CURRENT:
    python3 scripts/apply_manual_serial_fixes.py
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Any


# Registry of manual fixes
# Each entry specifies how to identify and fix a rule
MANUAL_FIXES = [
    {
        "name": "Trane Style 1 (2002-2009) - Length Constraint",
        "match": {
            "brand": "TRANE",
            "style_name": "Style 1 (2002-2009)",
            # Match any of these patterns (old broken versions)
            "serial_regex_any": [
                r"^(?=.*[A-Z])\d{3}[A-Z0-9]{3,30}$",  # Original broken pattern
                r"^(?=.*[A-Z])\d{3,}[A-Z0-9]{2,30}$",  # v2 attempt
                r"^(?=.*[A-Z])\d{3}(?!\d)[A-Z0-9]{2,30}$",  # v1 attempt
            ]
        },
        "fix": {
            "serial_regex": r"^(?=.{7,9}$)(?=.*[A-Z])\d{3,}[A-Z0-9]{2,30}$",
            "example_serials": ["91531S41F", "315S41F", "2212WHP4F"],
            "date_fields": {
                "year": {
                    "positions": {"start": 1, "end": 1},
                    "transform": {
                        "type": "year_add_base",
                        "base": 2000,
                        "min_year": 2002,
                        "max_year": 2009
                    }
                },
                "week": {"positions": {"start": 2, "end": 3}}
            },
            "decade_ambiguity": {
                "is_ambiguous": True,
                "notes": "Year code is single digit. Matches serials with total length 7-9 characters. This length constraint prevents conflict with 2010+ format which uses 10+ character serials."
            },
            "evidence_excerpt": "From 2002 to 2009: Year determined by position 1 (single digit), week by positions 2-3. Analysis of real data shows these serials are 7-9 characters total length. The regex uses (?=.{7,9}$) lookahead to ensure this length constraint.",
            "retrieved_on": "2026-01-27"
        },
        "reason": "Original pattern allowed 3+ digits without length constraint, causing modern 10-char serials to incorrectly match and decode as 2002 instead of 2022. Fix adds (?=.{7,9}$) lookahead to restrict to 7-9 character serials only.",
        "issue_url": "https://github.com/your-org/project/issues/123"  # Add if tracked
    },
    {
        "name": "Trane Style 1 (2010+) - Length Constraint",
        "match": {
            "brand": "TRANE",
            "style_name": "Style 1 (2010+)",
            "serial_regex_any": [
                r"^(?=.*[A-Z])\d{4}[A-Z0-9]{3,30}$",  # Original pattern (exactly 4 digits)
                r"^(?=.*[A-Z])\d{4,}[A-Z0-9]{2,30}$",  # v2 attempt (without length constraint)
            ]
        },
        "fix": {
            "serial_regex": r"^(?=.{10,}$)(?=.*[A-Z])\d{4,}[A-Z0-9]{2,30}$",
            "example_serials": ["10161KEDAA", "130313596L", "22226NUP4F", "214410805D", "23033078JA"],
            "date_fields": {
                "year": {
                    "positions": {"start": 1, "end": 2},
                    "transform": {
                        "type": "year_add_base",
                        "base": 2000,
                        "min_year": 2010
                    }
                },
                "week": {"positions": {"start": 3, "end": 4}}
            },
            "decade_ambiguity": {
                "is_ambiguous": True,
                "notes": "Year code is 2 digits. Matches serials with total length 10+ characters. This length constraint prevents conflict with 2002-2009 format which uses 7-9 character serials."
            },
            "evidence_excerpt": "Starting in 2010: Year determined by positions 1-2 (two digits), week by positions 3-4. Analysis of real data shows these serials are 10+ characters total length. The regex uses (?=.{10,}$) lookahead to ensure this length constraint.",
            "retrieved_on": "2026-01-27"
        },
        "reason": "Original pattern required exactly 4 leading digits, missing modern 5-9 digit prefixes. Also lacked length constraint causing overlap with 2002-2009 era. Fix adds (?=.{10,}$) lookahead to restrict to 10+ character serials only.",
        "issue_url": "https://github.com/your-org/project/issues/123"
    }
    ,
    {
        "name": "York Style 2 - SDI-validated year-letter mapping + parenthesis-safe extraction",
        "match": {
            "brand": "YORK",
            "style_name": "Manual: Style 2 (Plant + MonthLetter + YearLetter + Letter + seq)",
            "serial_regex_any": [
                r"^(?:\([A-Z]\))?[A-Z][A-HK-N][A-HJ-NP-W][A-Z]\d{6,}$",
                r"^(?:\([A-Z]\))?[A-Z][A-HK-N][A-NP-W][A-Z]\d{6,}$",
            ],
        },
        "fix": {
            # Restrict to only the year letters we have validated from SDI truth so far.
            "serial_regex": r"^(?:\([A-Z]\))?[A-Z][A-HK-N][BCDEH][A-Z]\d{6,}$",
            "priority": "-2000",
            "example_serials": ["NCHM034439", "EFDM218213", "NFBS015990", "(S)EBHM062202"],
            "date_fields": {
                "month": {
                    "pattern": {"regex": r"^(?:\([A-Z]\))?[A-Z]([A-HK-N])", "group": 1},
                    "mapping": {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "K": 9, "L": 10, "M": 11, "N": 12},
                },
                "year": {
                    "pattern": {"regex": r"^(?:\([A-Z]\))?[A-Z][A-HK-N]([BCDEH])", "group": 1},
                    "mapping": {"B": 1994, "C": 1994, "H": 2002, "D": 2003, "E": 2003},
                },
            },
            "decade_ambiguity": {"is_ambiguous": False, "notes": "Year letter mapped to 4-digit year (SDI-validated subset)."},
            "evidence_excerpt": "From SDI export (2026-01-25): York Style 2 serials match ^(?:\\([A-Z]\\))?[A-Z][A-HK-N][BCDEH][A-Z]\\d{6,}$. Validated year-letter mapping on observed samples: B/C->1994, H->2002, D/E->2003. Pattern-based extraction keeps positions stable even when a leading parenthetical letter like (S) is present.",
            # Force a lexicographically newer timestamp so duplicate-removal keeps this fixed row.
            "retrieved_on": "2026-01-30T23:59:59Z",
        },
        "reason": "Earlier manual York Style 2 mapping (A-H then J-N) did not match SDI truth for York assets; also absolute positions break when a leading parenthetical letter exists. This fix uses pattern capture groups and a conservative mapping limited to SDI-validated letters.",
    },
    {
        "name": "AERCO G-YY-#### - Keep 2000+ bounds",
        "match": {
            "brand": "AERCO",
            "style_name": "Manual: G-YY-#### (2000+)",
            "serial_regex_any": [r"^G-?\d{2}-?\d{4}$"],
        },
        "fix": {
            "style_name": "Manual: G-YY-#### (2000+)",
            "serial_regex": r"^G-?\d{2}-?\d{4}$",
            "example_serials": ["G-10-0919", "G-10-0924", "G-12-0785"],
            "date_fields": {
                "year": {
                    "pattern": {"regex": r"^G-?(\d{2})", "group": 1},
                    "transform": {"type": "year_add_base", "base": 2000, "min_year": 2000, "max_year": 2035},
                }
            },
            "decade_ambiguity": {"is_ambiguous": False},
            "evidence_excerpt": "User-provided AERCO: serials like G-10-0919 / G-12-0785 decode year from the two digits after 'G-' (10=>2010, 12=>2012).",
            "retrieved_on": "2026-01-30T23:59:59Z",
        },
        "reason": "Keeps the AERCO G-YY-#### rule stable across promotions; earlier-year discrepancies vs SDI truth need separate investigation before constraining the year range.",
    },
    {
        "name": "AERCO G-YY-#### - Remove duplicate 2010+ variant",
        "match": {
            "brand": "AERCO",
            "style_name": "Manual: G-YY-#### (2010+ only)",
            "serial_regex_any": [r"^G-?\d{2}-?\d{4}$"],
        },
        "fix": {
            "style_name": "Manual: G-YY-#### (2000+)",
            "serial_regex": r"^G-?\d{2}-?\d{4}$",
            "example_serials": ["G-10-0919", "G-10-0924", "G-12-0785"],
            "date_fields": {
                "year": {
                    "pattern": {"regex": r"^G-?(\d{2})", "group": 1},
                    "transform": {"type": "year_add_base", "base": 2000, "min_year": 2000, "max_year": 2035},
                }
            },
            "decade_ambiguity": {"is_ambiguous": False},
            "evidence_excerpt": "User-provided AERCO: serials like G-10-0919 / G-12-0785 decode year from the two digits after 'G-' (10=>2010, 12=>2012).",
            "retrieved_on": "2026-01-30T23:59:59Z",
        },
        "reason": "Collapses the short-lived 2010+ constrained variant back into the canonical 2000+ rule to avoid duplicate rows in SerialDecodeRule.csv.",
    },
]


def load_rules(csv_path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    """Load rules from CSV."""
    with csv_path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    return fieldnames, rows


def save_rules(csv_path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    """Save rules to CSV."""
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def rule_matches(row: dict[str, Any], match_spec: dict[str, Any]) -> bool:
    """Check if a rule matches the match specification."""
    for key, value in match_spec.items():
        if key == "serial_regex_any":
            # Match if serial_regex is any of the listed patterns
            if row.get("serial_regex", "") not in value:
                return False
        else:
            if row.get(key, "") != value:
                return False
    return True


def apply_fix(row: dict[str, Any], fix_spec: dict[str, Any]) -> dict[str, Any]:
    """Apply fix specification to a rule row."""
    for key, value in fix_spec.items():
        if key in ["date_fields", "decade_ambiguity", "example_serials"]:
            # JSON fields
            row[key] = json.dumps(value, ensure_ascii=False)
        else:
            row[key] = value
    return row


def remove_duplicates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove duplicate rules, keeping the most recent version.

    Duplicates are identified by (brand, style_name) - we keep the one with
    the most recent retrieved_on date or the last one if dates are equal/missing.
    """
    from collections import defaultdict

    grouped: dict[tuple[str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)

    for idx, row in enumerate(rows):
        key = (row.get("brand", ""), row.get("style_name", ""))
        grouped[key].append((idx, row))

    keep_indices = set()
    for key, group in grouped.items():
        if len(group) == 1:
            keep_indices.add(group[0][0])
        else:
            # Multiple rules with same (brand, style_name) - keep most recent.
            # If retrieved_on is equal/blank, prefer later rows (candidates appended later should win).
            sorted_group = sorted(group, key=lambda x: (x[1].get("retrieved_on", ""), x[0]), reverse=True)
            keep_indices.add(sorted_group[0][0])

    return [rows[i] for i in sorted(keep_indices)]


def apply_manual_fixes(ruleset_dir: Path, dry_run: bool = False) -> int:
    """Apply all manual fixes to the ruleset."""
    csv_path = ruleset_dir / "SerialDecodeRule.csv"

    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        return 1

    # Backup
    if not dry_run:
        backup_path = csv_path.with_suffix(".csv.before_manual_fixes")
        shutil.copy2(csv_path, backup_path)
        print(f"Backed up to: {backup_path}")

    fieldnames, rows = load_rules(csv_path)
    original_count = len(rows)
    fixes_applied = 0

    print(f"\nLoaded {len(rows)} rules from {csv_path}")
    print(f"Checking {len(MANUAL_FIXES)} manual fixes...\n")

    for fix_def in MANUAL_FIXES:
        print(f"Applying: {fix_def['name']}")
        print(f"  Reason: {fix_def['reason']}")

        matched = False
        for row in rows:
            if rule_matches(row, fix_def["match"]):
                matched = True
                old_regex = row.get("serial_regex", "")
                apply_fix(row, fix_def["fix"])
                new_regex = row.get("serial_regex", "")

                print(f"  ✓ Fixed rule:")
                print(f"    Brand: {row.get('brand')}")
                print(f"    Style: {row.get('style_name')}")
                print(f"    Old regex: {old_regex[:50]}...")
                print(f"    New regex: {new_regex[:50]}...")
                fixes_applied += 1

        if not matched:
            print(f"  ℹ No matching rule found (may already be fixed)")
        print()

    # Remove duplicates
    print("Removing duplicate rules...")
    rows = remove_duplicates(rows)
    duplicates_removed = original_count + fixes_applied - len(rows)
    if duplicates_removed > 0:
        print(f"  Removed {duplicates_removed} duplicate(s)")

    print(f"\nSummary:")
    print(f"  Original rules: {original_count}")
    print(f"  Fixes applied: {fixes_applied}")
    print(f"  Duplicates removed: {duplicates_removed}")
    print(f"  Final rules: {len(rows)}")

    if not dry_run:
        save_rules(csv_path, fieldnames, rows)
        print(f"\n✓ Saved fixed rules to: {csv_path}")
    else:
        print(f"\n⚠ DRY RUN - No changes written")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply manual serial decode rule fixes")
    parser.add_argument(
        "--ruleset-dir",
        type=Path,
        help="Path to ruleset directory (default: use CURRENT.txt)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    if args.ruleset_dir:
        ruleset_dir = args.ruleset_dir
    else:
        # Use CURRENT.txt
        current_file = Path("data/rules_normalized/CURRENT.txt")
        if not current_file.exists():
            print(f"ERROR: {current_file} not found")
            return 1
        ruleset_dir = Path(current_file.read_text().strip())

    if not ruleset_dir.exists():
        print(f"ERROR: Ruleset directory not found: {ruleset_dir}")
        return 1

    print(f"Applying manual fixes to: {ruleset_dir}")
    return apply_manual_fixes(ruleset_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    exit(main())
