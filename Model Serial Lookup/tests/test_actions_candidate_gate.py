from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


class TestActionsCandidateGate(unittest.TestCase):
    def test_serial_candidates_missing_examples_blocks_promotion(self) -> None:
        # Import from script module (wrapper-level policy).
        from scripts.actions import _validate_candidates_hard_fail

        with tempfile.TemporaryDirectory() as td:
            cand_dir = Path(td)
            path = cand_dir / "SerialDecodeRule.candidates.jsonl"
            path.write_text(
                json.dumps(
                    {
                        "rule_type": "decode",
                        "brand": "TEST",
                        "style_name": "bad",
                        "serial_regex": r"^\\d{6}$",
                        "date_fields": {"year": {"positions": {"start": 1, "end": 2}}},
                        # missing example_serials
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit):
                _validate_candidates_hard_fail(cand_dir)


if __name__ == "__main__":
    unittest.main()

