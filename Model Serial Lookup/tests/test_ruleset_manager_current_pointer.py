from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from msl.pipeline.ruleset_manager import read_current_ruleset, update_current_pointer


class TestRulesetManagerCurrentPointer(unittest.TestCase):
    def test_current_pointer_folder_name_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "data" / "rules_normalized"
            base.mkdir(parents=True, exist_ok=True)

            ruleset_dir = base / "2026-01-27-trane-fix-v3"
            ruleset_dir.mkdir(parents=True, exist_ok=True)
            (ruleset_dir / "SerialDecodeRule.csv").write_text("rule_type,brand\n", encoding="utf-8")

            (base / "CURRENT.txt").write_text("2026-01-27-trane-fix-v3\n", encoding="utf-8")
            resolved = read_current_ruleset(base)
            self.assertEqual(resolved, ruleset_dir)

    def test_current_pointer_legacy_path_is_tolerated(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "data" / "rules_normalized"
            base.mkdir(parents=True, exist_ok=True)

            ruleset_dir = base / "2026-01-27-trane-fix-v3"
            ruleset_dir.mkdir(parents=True, exist_ok=True)
            (ruleset_dir / "SerialDecodeRule.csv").write_text("rule_type,brand\n", encoding="utf-8")

            (base / "CURRENT.txt").write_text(str(ruleset_dir) + "\n", encoding="utf-8")
            resolved = read_current_ruleset(base)
            self.assertEqual(resolved, ruleset_dir)

    def test_update_current_pointer_writes_folder_name_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "data" / "rules_normalized"
            base.mkdir(parents=True, exist_ok=True)

            ruleset_dir = base / "some-ruleset"
            ruleset_dir.mkdir(parents=True, exist_ok=True)

            update_current_pointer(ruleset_dir, base_dir=base)
            content = (base / "CURRENT.txt").read_text(encoding="utf-8").strip()
            self.assertEqual(content, "some-ruleset")


if __name__ == "__main__":
    unittest.main()

