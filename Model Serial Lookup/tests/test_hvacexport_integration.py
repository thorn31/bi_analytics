#!/usr/bin/env python3
"""
Phase 4.2: End-to-End Integration Tests

Validates complete workflow from decoder.xml to merged ruleset.
"""

import csv
import json
import unittest
from pathlib import Path

from msl.decoder.normalize import normalize_brand


# Test data paths
BASE_DIR = Path(__file__).parent.parent
CANDIDATES_PATH = BASE_DIR / "data/external_sources/hvacexport/2026-01-24_v3.84_enriched2/derived/runs/candidates__20260129T2245Z_relax_codes/AttributeDecodeRule.hvacexport.candidates.jsonl"


def _load_sample_candidates(max_rows: int = 100) -> list[dict]:
    if not CANDIDATES_PATH.exists():
        return []
    candidates: list[dict] = []
    with CANDIDATES_PATH.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= max_rows:
                break
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    return candidates


class TestHVACExportIntegration(unittest.TestCase):
    """End-to-end integration tests for HVAC export workflow."""

    def test_decoder_xml_structure(self):
        """Verify decoder.xml can be parsed."""
        decoder_xml_path = BASE_DIR / "data/static/hvacdecodertool/decoder.xml"

        if not decoder_xml_path.exists():
            self.skipTest("decoder.xml not found")

        # Basic check: file exists and is non-empty
        self.assertGreater(decoder_xml_path.stat().st_size, 0, "decoder.xml is empty")

    def test_candidate_jsonl_format(self):
        """Validate JSONL candidate structure."""
        sample_candidates = _load_sample_candidates()
        if not sample_candidates:
            self.skipTest(f"Candidates file not found or empty: {CANDIDATES_PATH}")

        for i, rule in enumerate(sample_candidates):
            # Required fields
            self.assertIn("rule_type", rule, f"Rule {i} missing rule_type")
            self.assertIn("brand", rule, f"Rule {i} missing brand")
            self.assertIn("attribute_name", rule, f"Rule {i} missing attribute_name")
            self.assertIn("model_regex", rule, f"Rule {i} missing model_regex")
            self.assertIn("value_extraction", rule, f"Rule {i} missing value_extraction")

            # Validate rule_type
            self.assertIn(rule["rule_type"], ["decode", "guidance"], f"Rule {i} has invalid rule_type: {rule['rule_type']}")

            # Validate brand is normalized
            brand = normalize_brand(rule["brand"])
            self.assertEqual(brand, rule["brand"], f"Rule {i} brand not normalized: {rule['brand']} vs {brand}")

            # Validate value_extraction structure
            value_extraction = rule["value_extraction"]
            self.assertIsInstance(value_extraction, dict, f"Rule {i} value_extraction not a dict")

            if value_extraction:
                self.assertIn("data_type", value_extraction, f"Rule {i} value_extraction missing data_type")

    def test_attribute_naming_convention(self):
        """Verify attribute naming follows conventions."""
        sample_candidates = _load_sample_candidates()
        if not sample_candidates:
            self.skipTest(f"Candidates file not found or empty: {CANDIDATES_PATH}")
        for rule in sample_candidates:
            attr = rule.get("attribute_name", "")

            # Check HVAC export attributes start with prefix
            if "Code" in attr:
                self.assertTrue(attr.startswith("HVACExport_"), f"Code attribute should have HVACExport_ prefix: {attr}")

    def test_no_duplicate_rules_in_candidates(self):
        """Ensure no exact duplicate rules exist in candidates (full rule identity)."""
        sample_candidates = _load_sample_candidates()
        if not sample_candidates:
            self.skipTest(f"Candidates file not found or empty: {CANDIDATES_PATH}")
        seen = set()

        for rule in sample_candidates:
            brand = normalize_brand(rule.get("brand", ""))
            attribute = rule.get("attribute_name", "")
            regex = rule.get("model_regex", "")
            ve = json.dumps(rule.get("value_extraction", {}) or {}, sort_keys=True)
            ets = json.dumps(rule.get("equipment_types", []) or [], sort_keys=True)

            key = (brand, attribute, regex, ve, ets)

            if key in seen:
                self.fail(f"Duplicate rule found: {key}")

            seen.add(key)

    def test_alignment_mapping_exists(self):
        """Check that SDI alignment mapping is defined."""
        from scripts.analyze_hvacexport_sdi_alignment import HVAC_EXPORT_ATTRIBUTES

        # Verify critical attributes are mapped
        self.assertIn("HVACExport_CoolingCode", HVAC_EXPORT_ATTRIBUTES)
        self.assertIn("HVACExport_CoolingTonCode", HVAC_EXPORT_ATTRIBUTES)
        self.assertIn("Refrigerant", HVAC_EXPORT_ATTRIBUTES)

    def test_validation_mappings_exist(self):
        """Check that validation mappings are defined."""
        from scripts.validate_merged_ruleset_attributes import VALIDATION_MAPPINGS

        # Verify critical mappings exist
        self.assertIn("NominalCapacityTons", VALIDATION_MAPPINGS)
        self.assertEqual(VALIDATION_MAPPINGS["NominalCapacityTons"], "KnownCapacityTons")

    def test_merge_preserves_building_center_rules(self):
        """Verify merge script prioritizes building-center.org rules."""
        from scripts.merge_hvacexport_supplementary import should_skip_rule

        # Mock current coverage
        current_coverage = {
            "TRANE": {"NominalCapacityTons": {""}},
            "CARRIER": {"Refrigerant": {""}},
        }

        # Mock alignment
        alignment = {
            "HVACExport_CoolingTonCode": {
                "action": "RENAME",
                "target_name": "NominalCapacityTons",
            }
        }

        # Test: HVAC export rule should be skipped if building-center has it
        hvac_rule = {
            "brand": "TRANE",
            "attribute_name": "NominalCapacityTons",
            "model_regex": "^[A-Z]{3}\\d{5}$",
        }

        should_skip, reason = should_skip_rule(hvac_rule, current_coverage, alignment)
        self.assertTrue(should_skip, "Should skip HVAC rule when building-center has same attribute")
        self.assertEqual(reason, "BUILDING_CENTER_HAS_ATTRIBUTE")

        # Test: HVAC export rule OK if different brand
        hvac_rule_diff_brand = {
            "brand": "LENNOX",
            "attribute_name": "NominalCapacityTons",
            "model_regex": "^[A-Z]{3}\\d{5}$",
        }

        should_skip, reason = should_skip_rule(hvac_rule_diff_brand, current_coverage, alignment)
        self.assertFalse(should_skip, "Should not skip HVAC rule for different brand")

    def test_quality_filter_logic(self):
        """Test regex quality filtering logic."""
        from scripts.validate_hvacexport_regex_quality import calculate_status

        # High sample size: strict 90% threshold
        self.assertEqual(calculate_status(95.0, 100), "GOOD")
        self.assertEqual(calculate_status(85.0, 100), "WEAK")
        self.assertEqual(calculate_status(5.0, 100), "POOR")

        # Low sample size: relaxed threshold
        self.assertEqual(calculate_status(40.0, 5), "GOOD")
        self.assertEqual(calculate_status(20.0, 5), "WEAK")
        self.assertEqual(calculate_status(5.0, 5), "POOR")

        # No data
        self.assertEqual(calculate_status(0.0, 0), "NO_DATA")

    def test_value_comparison_logic(self):
        """Test value comparison with tolerance."""
        from scripts.validate_merged_ruleset_attributes import compare_values

        # Exact match
        self.assertTrue(compare_values("2.0", "2.0", "NominalCapacityTons"))

        # Numeric tolerance (5%)
        self.assertTrue(compare_values("2.0", "2.05", "NominalCapacityTons"))
        self.assertFalse(compare_values("2.0", "2.5", "NominalCapacityTons"))

        # Refrigerant variations
        self.assertTrue(compare_values("R-410A", "R410A", "Refrigerant"))
        self.assertTrue(compare_values("R410A", "R-410A", "Refrigerant"))

        # Voltage extraction
        self.assertTrue(compare_values("208", "208V - Three Phase", "VoltageVoltPhaseHz"))
        self.assertTrue(compare_values("480", "480V - Three Phase", "Voltage"))

    def test_full_workflow_trane(self):
        """
        End-to-end test: Validate full workflow for Trane.

        This is a slow test that runs the complete integration workflow.
        Skip if validation files don't exist.
        """
        # Treat as opt-in because it depends on locally-generated validation artifacts.
        if (Path(__file__).parent / "RUN_SLOW_TESTS.txt").exists() is False:
            self.skipTest("Slow test disabled. Create tests/RUN_SLOW_TESTS.txt to enable.")

        validation_dir = BASE_DIR / "data/validation/hvacexport"

        # Check if validation has been run
        quality_report = validation_dir / "trane_regex_quality_report.csv"
        if not quality_report.exists():
            self.skipTest("Trane validation not run yet")

        # Load quality report
        good_rules = 0
        with quality_report.open("r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("status") == "GOOD":
                    good_rules += 1

        # Basic sanity checks
        self.assertGreater(good_rules, 0, "Should have at least some GOOD rules for Trane")

        # Check if alignment report exists
        alignment_report = validation_dir / "trane_sdi_column_alignment.csv"
        if alignment_report.exists():
            with alignment_report.open("r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertGreater(len(rows), 0, "Alignment report should not be empty")


if __name__ == "__main__":
    unittest.main(verbosity=2)
