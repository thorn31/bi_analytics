from __future__ import annotations

import unittest

from msl.pipeline.ruleset_cleanup import prune_superseded_attribute_guidance, prune_superseded_serial_guidance


class TestRulesetCleanup(unittest.TestCase):
    def test_prune_superseded_serial_guidance_by_style_number(self) -> None:
        rows = [
            {
                "rule_type": "guidance",
                "brand": "YORK",
                "style_name": "Style 2:",
                "serial_regex": "",
                "date_fields": {},
                "guidance_action": "chart_required",
                "guidance_text": "See chart",
            },
            {
                "rule_type": "decode",
                "brand": "YORK",
                "style_name": "Style 2: Example",
                "serial_regex": "^[A-Z]+$",
                "date_fields": {"year": {"pattern": {"regex": "X", "group": 0}, "mapping": {"A": 2000}}},
            },
            # Non-style guidance should remain.
            {
                "rule_type": "guidance",
                "brand": "YORK",
                "style_name": "Contact manufacturer",
                "serial_regex": "",
                "date_fields": {},
                "guidance_action": "contact_manufacturer",
                "guidance_text": "Call York",
            },
        ]
        out = prune_superseded_serial_guidance(rows)
        self.assertEqual(len(out), 2)
        self.assertTrue(any(r.get("style_name") == "Contact manufacturer" for r in out))
        self.assertTrue(any((r.get("rule_type") == "decode") for r in out))

    def test_prune_superseded_attribute_guidance_chart_required_brandwide(self) -> None:
        rows = [
            {
                "rule_type": "guidance",
                "brand": "RHEEM",
                "attribute_name": "NominalCapacityTons",
                "model_regex": "",
                "value_extraction": {},
                "guidance_action": "chart_required",
                "guidance_text": "See chart",
            },
            {
                "rule_type": "decode",
                "brand": "RHEEM",
                "attribute_name": "NominalCapacityTons",
                "model_regex": "^RKPN",
                "value_extraction": {"pattern": {"regex": "^RKPN-(\\d{3})", "group": 1}},
            },
            # Guidance with model_regex should remain.
            {
                "rule_type": "guidance",
                "brand": "RHEEM",
                "attribute_name": "NominalCapacityTons",
                "model_regex": "^SOMETHING",
                "value_extraction": {},
                "guidance_action": "chart_required",
                "guidance_text": "See chart for this family",
            },
        ]
        out = prune_superseded_attribute_guidance(rows)
        self.assertEqual(len(out), 2)
        self.assertTrue(any(r.get("model_regex") == "^SOMETHING" for r in out))
        self.assertTrue(any((r.get("rule_type") == "decode") for r in out))


if __name__ == "__main__":
    unittest.main()

