#!/usr/bin/env python3
import json
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


class TestSpecsMineSnapshot(unittest.TestCase):
    def test_mine_snapshot_writes_candidates(self):
        snapshot_id = "2026-01-30-specs-batch1"
        snapshot_dir = BASE_DIR / "data/external_sources/specs_snapshots" / snapshot_id
        if not (snapshot_dir / "manifest.json").exists():
            self.skipTest("specs snapshot not present in workspace")

        out_dir = BASE_DIR / "data/rules_discovered/spec_sheets" / snapshot_id / "candidates"
        out_path = out_dir / "AttributeDecodeRule.candidates.jsonl"
        if not out_path.exists():
            self.skipTest("candidates not generated yet (run specs.mine_snapshot once)")

        rows = [json.loads(l) for l in out_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertGreaterEqual(len(rows), 1)
        attrs = {r.get("attribute_name") for r in rows}
        # Expect at least one of the known miners to have fired for this snapshot.
        self.assertTrue({"SupplyFanHP", "NominalCapacityTons"} & attrs)


if __name__ == "__main__":
    unittest.main(verbosity=2)

