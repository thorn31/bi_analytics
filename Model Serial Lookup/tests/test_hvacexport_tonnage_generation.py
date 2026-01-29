import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestHvacExportTonnageGeneration(unittest.TestCase):
    def test_tonnage_options_parse_as_number(self):
        repo_root = Path(__file__).resolve().parents[1]
        parse_script = repo_root / "scripts" / "hvacexport_parse.py"
        gen_script = repo_root / "scripts" / "hvacexport_generate_attribute_candidates.py"
        hvac_fixture = repo_root / "tests" / "fixtures" / "hvacexport_tonnage_fixture.xml"

        self.assertTrue(parse_script.exists())
        self.assertTrue(gen_script.exists())
        self.assertTrue(hvac_fixture.exists())

        with tempfile.TemporaryDirectory() as td:
            hvac_root = Path(td) / "hvacexport"
            snapshot_id = "snap_tonnage"

            p1 = subprocess.run(
                [
                    sys.executable,
                    str(parse_script),
                    "--input",
                    str(hvac_fixture),
                    "--snapshot-id",
                    snapshot_id,
                    "--out-root",
                    str(hvac_root),
                ],
                cwd=str(repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(p1.returncode, 0, msg=f"parse stderr:\n{p1.stderr}")

            p2 = subprocess.run(
                [
                    sys.executable,
                    str(gen_script),
                    "--snapshot-id",
                    snapshot_id,
                    "--hvacexport-root",
                    str(hvac_root),
                    "--run-id",
                    "gen1",
                ],
                cwd=str(repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(p2.returncode, 0, msg=f"gen stderr:\n{p2.stderr}")

            cand_path = hvac_root / snapshot_id / "derived" / "runs" / "gen1" / "AttributeDecodeRule.hvacexport.candidates.jsonl"
            objs = [json.loads(l) for l in cand_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            tons = [o for o in objs if o.get("attribute_name") == "NominalCapacityTons"]
            self.assertTrue(tons)
            m = tons[0]["value_extraction"]["mapping"]
            # Values should be numeric (float/int), not strings.
            self.assertIsInstance(m["31"], (int, float))
            self.assertEqual(float(m["31"]), 30.0)


if __name__ == "__main__":
    unittest.main()

