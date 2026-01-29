from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from msl.decoder.attributes import decode_attributes
from msl.decoder.io import load_attribute_rules_csv
from msl.decoder.validate import validate_attribute_rules


class TestDecoderAttributes(unittest.TestCase):
    def test_decode_attribute_with_mapping_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "AttributeDecodeRule.csv"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "rule_type",
                        "brand",
                        "model_regex",
                        "attribute_name",
                        "value_extraction",
                        "units",
                        "examples",
                        "limitations",
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
                        "model_regex": "",
                        "attribute_name": "NominalCapacityTons",
                        "value_extraction": json.dumps(
                            {
                                "data_type": "Number",
                                "pattern": {"regex": r"(024|030)", "group": 1},
                                "mapping": {"024": 2.0, "030": 2.5},
                            }
                        ),
                        "units": "Tons",
                        "examples": json.dumps(["GRH024AHC30CLBS"]),
                        "limitations": "",
                        "guidance_action": "",
                        "guidance_text": "",
                        "evidence_excerpt": "excerpt",
                        "source_url": "url",
                        "retrieved_on": "2026-01-25",
                        "image_urls": "[]",
                    }
                )

            rules = load_attribute_rules_csv(path)
            accepted, issues = validate_attribute_rules(rules)
            self.assertEqual(len(issues), 0)

            attrs = decode_attributes("TEST", "GRH024AHC30CLBS", accepted)
            self.assertEqual(len(attrs), 1)
            self.assertEqual(attrs[0].attribute_name, "NominalCapacityTons")
            self.assertEqual(attrs[0].value_raw, "024")
            self.assertEqual(attrs[0].value, 2.0)

    def test_equipment_type_prefers_typed_attribute_rules(self) -> None:
        from msl.decoder.io import AttributeRule

        rules = [
            AttributeRule(
                rule_type="decode",
                brand="TEST",
                model_regex="",
                attribute_name="NominalCapacityTons",
                equipment_types=[],
                value_extraction={"data_type": "Number", "pattern": {"regex": r"(024)", "group": 1}, "mapping": {"024": 2.5}},
                units="Tons",
                examples=["GRH024AHC30CLBS"],
                limitations="",
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="url",
                retrieved_on="",
                image_urls=[],
            ),
            AttributeRule(
                rule_type="decode",
                brand="TEST",
                model_regex="",
                attribute_name="NominalCapacityTons",
                equipment_types=["Cooling Condensing Unit"],
                value_extraction={"data_type": "Number", "pattern": {"regex": r"(024)", "group": 1}, "mapping": {"024": 2.0}},
                units="Tons",
                examples=["GRH024AHC30CLBS"],
                limitations="",
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            ),
        ]
        accepted, issues = validate_attribute_rules(rules)
        self.assertEqual(len(issues), 0)

        attrs_typed = decode_attributes("TEST", "GRH024AHC30CLBS", accepted, equipment_type="Cooling Condensing Unit")
        self.assertEqual(len(attrs_typed), 1)
        self.assertEqual(attrs_typed[0].value, 2.0)
        self.assertEqual(attrs_typed[0].rule_equipment_types, ["Cooling Condensing Unit"])

        attrs_missing = decode_attributes("TEST", "GRH024AHC30CLBS", accepted, equipment_type=None)
        self.assertEqual(len(attrs_missing), 1)
        self.assertTrue(attrs_missing[0].typed_rule_applied_without_type_context)


if __name__ == "__main__":
    unittest.main()

