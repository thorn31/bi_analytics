from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from msl.decoder.decode import decode_serial
from msl.decoder.io import load_serial_rules_csv
from msl.decoder.normalize import normalize_brand
from msl.decoder.validate import validate_serial_rules


class TestDecoderSerial(unittest.TestCase):
    def test_decode_extracts_positions(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "SerialDecodeRule.csv"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "rule_type",
                        "brand",
                        "style_name",
                        "serial_regex",
                        "date_fields",
                        "example_serials",
                        "decade_ambiguity",
                        "guidance_action",
                        "guidance_text",
                        "evidence_excerpt",
                        "source_url",
                        "retrieved_on",
                        "image_urls",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "rule_type": "decode",
                        "brand": "TEST",
                        "style_name": "Style 1",
                        "serial_regex": r"^\d{6}$",
                        "date_fields": json.dumps(
                            {"year": {"positions": {"start": 1, "end": 2}}, "week": {"positions": {"start": 3, "end": 4}}}
                        ),
                        "example_serials": json.dumps(["250712"]),
                        "decade_ambiguity": json.dumps({"is_ambiguous": True}),
                        "guidance_action": "",
                        "guidance_text": "",
                        "evidence_excerpt": "excerpt",
                        "source_url": "url",
                        "retrieved_on": "2026-01-25",
                        "image_urls": "[]",
                    }
                )

            rules = load_serial_rules_csv(path)
            accepted, issues = validate_serial_rules(rules)
            self.assertEqual(len(issues), 0)

            res = decode_serial("TEST", "25 07 12", accepted)
            self.assertEqual(res.matched_style_name, "Style 1")
            self.assertEqual(res.manufacture_year_raw, "25")
            self.assertEqual(res.manufacture_week_raw, "07")
            self.assertTrue(res.ambiguous_decade)

    def test_guidance_is_returned_as_notes_when_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "SerialDecodeRule.csv"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "rule_type",
                        "brand",
                        "style_name",
                        "serial_regex",
                        "date_fields",
                        "example_serials",
                        "decade_ambiguity",
                        "guidance_action",
                        "guidance_text",
                        "evidence_excerpt",
                        "source_url",
                        "retrieved_on",
                        "image_urls",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "rule_type": "guidance",
                        "brand": "TEST",
                        "style_name": "Notes",
                        "serial_regex": "",
                        "date_fields": json.dumps({}),
                        "example_serials": json.dumps([]),
                        "decade_ambiguity": json.dumps({"is_ambiguous": True}),
                        "guidance_action": "contact_manufacturer",
                        "guidance_text": "Contact manufacturer",
                        "evidence_excerpt": "excerpt",
                        "source_url": "url",
                        "retrieved_on": "2026-01-25",
                        "image_urls": "[]",
                    }
                )
            rules = load_serial_rules_csv(path)
            accepted, _issues = validate_serial_rules(rules)

            res = decode_serial("TEST", "NOPE", accepted)
            self.assertEqual(res.confidence, "None")
            self.assertIn("Contact manufacturer", res.notes)

    def test_year_add_base_with_constraints_selects_correct_rule(self) -> None:
        # Simulates two rules that both match, but only one is valid by year constraint.
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="TEST",
                priority=None,
                style_name="Style old",
                serial_regex=r"^(?=.*[A-Z])\d{4}[A-Z0-9]{3,30}$",
                equipment_types=[],
                date_fields={"year": {"positions": {"start": 1, "end": 2}, "transform": {"type": "year_add_base", "base": 2000, "max_year": 2009}}},
                example_serials=["0901ABCD"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="",
                retrieved_on="",
                image_urls=[],
            ),
            SerialRule(
                rule_type="decode",
                brand="TEST",
                priority=None,
                style_name="Style new",
                serial_regex=r"^(?=.*[A-Z])\d{4}[A-Z0-9]{3,30}$",
                equipment_types=[],
                date_fields={"year": {"positions": {"start": 1, "end": 2}, "transform": {"type": "year_add_base", "base": 2000, "min_year": 2010}}},
                example_serials=["1201ABCD"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="",
                retrieved_on="",
                image_urls=[],
            ),
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        res = decode_serial("TEST", "1201ABCD", accepted)
        self.assertEqual(res.matched_style_name, "Style new")
        self.assertEqual(res.manufacture_year, 2012)

    def test_equipment_type_gates_typed_serial_rule(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="TEST",
                priority=None,
                style_name="Typed style",
                serial_regex=r"^\d{4}[A-Z]{2}$",
                equipment_types=["Cooling Condensing Unit"],
                date_fields={"year": {"positions": {"start": 1, "end": 4}}},
                example_serials=["2020AB"],
                decade_ambiguity={"is_ambiguous": False},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            )
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        res_ok = decode_serial("TEST", "2020AB", accepted, equipment_type="Cooling Condensing Unit")
        self.assertEqual(res_ok.confidence, "Low")
        self.assertEqual(res_ok.manufacture_year, 2020)

        res_mismatch = decode_serial("TEST", "2020AB", accepted, equipment_type="Boiler")
        self.assertEqual(res_mismatch.confidence, "None")

        res_missing = decode_serial("TEST", "2020AB", accepted, equipment_type=None)
        self.assertEqual(res_missing.manufacture_year, 2020)
        self.assertTrue(res_missing.typed_rule_applied_without_type_context)
        self.assertIn("type_context_missing_for_typed_serial_rule", res_missing.notes)


if __name__ == "__main__":
    unittest.main()
