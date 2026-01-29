import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestHvacExportAttributeCatalog(unittest.TestCase):
    def test_catalog_runs_on_fixture_snapshot(self):
        repo_root = Path(__file__).resolve().parents[1]
        parse_script = repo_root / "scripts" / "hvacexport_parse.py"
        catalog_script = repo_root / "scripts" / "hvacexport_attribute_catalog.py"
        fixture = repo_root / "tests" / "fixtures" / "hvacexport_small.xml"

        self.assertTrue(parse_script.exists())
        self.assertTrue(catalog_script.exists())
        self.assertTrue(fixture.exists())

        with tempfile.TemporaryDirectory() as td:
            out_root = Path(td) / "hvacexport"
            snapshot_id = "test_snapshot_catalog"
            # 1) Parse fixture into a snapshot
            p1 = subprocess.run(
                [
                    sys.executable,
                    str(parse_script),
                    "--input",
                    str(fixture),
                    "--snapshot-id",
                    snapshot_id,
                    "--out-root",
                    str(out_root),
                ],
                cwd=str(repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(p1.returncode, 0, msg=f"parse stderr:\n{p1.stderr}")

            # 2) Build catalog within that snapshot
            p2 = subprocess.run(
                [
                    sys.executable,
                    str(catalog_script),
                    "--snapshot-id",
                    snapshot_id,
                    "--hvacexport-root",
                    str(out_root),
                    "--run-id",
                    "test_catalog",
                ],
                cwd=str(repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(p2.returncode, 0, msg=f"catalog stderr:\n{p2.stderr}")

            run_dir = out_root / snapshot_id / "derived" / "runs" / "test_catalog"
            self.assertTrue((run_dir / "attribute_catalog.csv").exists())
            self.assertTrue((run_dir / "attribute_catalog_summary.json").exists())
            summary = json.loads((run_dir / "attribute_catalog_summary.json").read_text(encoding="utf-8"))
            self.assertIn("counts", summary)


if __name__ == "__main__":
    unittest.main()
