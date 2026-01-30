#!/usr/bin/env python3
"""
Test that v16-priority-test loads without errors.

Validates that adding priority column doesn't break rule loading.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from msl.decoder.io import load_serial_rules_csv


def test_loading():
    """Test loading v16-priority-test rules."""

    base_dir = Path(__file__).parent.parent

    print("=" * 80)
    print("TEST: Loading v16-priority-test")
    print("=" * 80)
    print()

    # Test v14 (baseline)
    v14_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v14' / 'SerialDecodeRule.csv'
    print(f"Loading v14 (baseline): {v14_path}")

    try:
        v14_rules = load_serial_rules_csv(v14_path)
        print(f"  ✓ Loaded {len(v14_rules)} rules")
        v14_count = len(v14_rules)
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        sys.exit(1)

    print()

    # Test v16-priority-test
    v16_path = base_dir / 'data' / 'rules_normalized' / '2026-01-29-sdi-master-v16-priority-test' / 'SerialDecodeRule.csv'
    print(f"Loading v16-priority-test: {v16_path}")

    if not v16_path.exists():
        print(f"  ✗ FAILED: File not found")
        print(f"  Run: python3 scripts/add_priority_column_test.py")
        sys.exit(1)

    try:
        v16_rules = load_serial_rules_csv(v16_path)
        print(f"  ✓ Loaded {len(v16_rules)} rules")
        v16_count = len(v16_rules)
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()
    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print()

    # Compare counts
    if v14_count == v16_count:
        print(f"✓ Rule count matches: {v14_count} rules")
    else:
        print(f"✗ Rule count mismatch!")
        print(f"  v14: {v14_count}")
        print(f"  v16: {v16_count}")
        sys.exit(1)

    # Check rule structure
    print()
    print("Checking rule structure...")

    for i, (v14_rule, v16_rule) in enumerate(zip(v14_rules[:5], v16_rules[:5])):
        if v14_rule.brand != v16_rule.brand or v14_rule.style_name != v16_rule.style_name:
            print(f"✗ Rule {i} mismatch!")
            print(f"  v14: {v14_rule.brand} - {v14_rule.style_name}")
            print(f"  v16: {v16_rule.brand} - {v16_rule.style_name}")
            sys.exit(1)

    print(f"✓ First 5 rules match")

    # Check if priority field exists in v16 rules
    print()
    print("Checking priority field...")

    # Check if SerialRule has priority attribute
    if hasattr(v16_rules[0], 'priority'):
        print(f"✓ SerialRule has 'priority' attribute")

        # Count explicit priorities
        explicit_priorities = sum(1 for r in v16_rules if hasattr(r, 'priority') and r.priority is not None)
        print(f"✓ {explicit_priorities} rules have explicit priority")

        # Show McQuay priorities
        mcquay_rules = [r for r in v16_rules if r.brand.upper() == 'MCQUAY']
        if mcquay_rules:
            print()
            print(f"McQuay rules ({len(mcquay_rules)} total):")
            for rule in mcquay_rules[:5]:
                priority = getattr(rule, 'priority', None)
                print(f"  Priority {priority}: {rule.style_name[:50]}")
    else:
        print(f"⚠️  SerialRule doesn't have 'priority' attribute")
        print(f"   This is OK - the column exists in CSV but class doesn't use it yet")
        print(f"   Next step: Update msl/decoder/io.py to read priority field")

    print()
    print("=" * 80)
    print("✓ LOADING TEST PASSED")
    print("=" * 80)
    print()
    print("Next: Run decode comparison test")
    print("  python3 scripts/test_priority_decode_comparison.py")


if __name__ == '__main__':
    test_loading()
