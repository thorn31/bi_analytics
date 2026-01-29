import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestHvacExportParse(unittest.TestCase):
    def test_parse_fixture_to_snapshot(self):
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "hvacexport_parse.py"
        fixture = repo_root / "tests" / "fixtures" / "hvacexport_small.xml"
        self.assertTrue(script.exists())
        self.assertTrue(fixture.exists())

        with tempfile.TemporaryDirectory() as td:
            out_root = Path(td) / "external_sources" / "hvacexport"
            snapshot_id = "test_snapshot_v1"
            cmd = [
                sys.executable,
                str(script),
                "--input",
                str(fixture),
                "--snapshot-id",
                snapshot_id,
                "--out-root",
                str(out_root),
            ]
            p = subprocess.run(cmd, cwd=str(repo_root), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(p.returncode, 0, msg=f"stderr:\n{p.stderr}")

            snapshot_dir = out_root / snapshot_id
            for name in ["records.csv", "segments.csv", "options.csv", "metadata.json", "summary.md"]:
                self.assertTrue((snapshot_dir / name).exists(), msg=f"missing: {name}")

            meta = json.loads((snapshot_dir / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["snapshot_id"], snapshot_id)
            self.assertEqual(meta["counts"]["records_n"], 2)
            self.assertEqual(meta["counts"]["segments_n"], 3)
            self.assertEqual(meta["counts"]["options_n"], 5)
            # Ensure segcount mismatch warning is present
            self.assertTrue(any(w.get("type") == "segcount_mismatch" for w in meta.get("warnings", [])))

            # Ensure ExtraFieldsJson captures unknown record/segment tags
            records_text = (snapshot_dir / "records.csv").read_text(encoding="utf-8")
            self.assertIn("UnknownRecordTag", records_text)
            segments_text = (snapshot_dir / "segments.csv").read_text(encoding="utf-8")
            self.assertIn("UnknownSegmentTag", segments_text)

            # Segment start/end positions should be present when SL sums to record length.
            # Fixture record 1: SL=3 then SL=8 for length=11 -> positions 1-3 and 4-11.
            self.assertIn(",1,3,", segments_text)
            self.assertIn(",4,11,", segments_text)

            # Category map audit columns should exist and be populated for mapped categories.
            # Fixture Category "Condenser" is mapped (even if low confidence), so it should have meta fields.
            self.assertIn("CategoryMapConfidence", records_text)


if __name__ == "__main__":
    unittest.main()
