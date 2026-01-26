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


if __name__ == "__main__":
    unittest.main()

