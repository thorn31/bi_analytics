import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestHvacExportCandidatesAndAlignment(unittest.TestCase):
    def test_generate_candidates_and_align(self):
        repo_root = Path(__file__).resolve().parents[1]
        parse_script = repo_root / "scripts" / "hvacexport_parse.py"
        gen_script = repo_root / "scripts" / "hvacexport_generate_attribute_candidates.py"
        eval_script = repo_root / "scripts" / "hvacexport_attribute_alignment_eval.py"
        hvac_fixture = repo_root / "tests" / "fixtures" / "hvacexport_voltage_fixture.xml"
        sdi_fixture = repo_root / "tests" / "fixtures" / "sdi_small_normalized.csv"

        self.assertTrue(parse_script.exists())
        self.assertTrue(gen_script.exists())
        self.assertTrue(eval_script.exists())
        self.assertTrue(hvac_fixture.exists())
        self.assertTrue(sdi_fixture.exists())

        with tempfile.TemporaryDirectory() as td:
            hvac_root = Path(td) / "hvacexport"
            snapshot_id = "snap_voltage"

            # 1) Parse fixture into snapshot (support + mapping defaults are repo files; snapshot uses those).
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

            # 2) Generate candidates in that snapshot.
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
            self.assertTrue(cand_path.exists())
            cand_lines = [json.loads(l) for l in cand_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertTrue(any(o.get("attribute_name") == "VoltageVoltPhaseHz" for o in cand_lines))
            self.assertTrue(any(o.get("attribute_name") == "Refrigerant" for o in cand_lines))

            # 3) Run alignment against SDI fixture.
            p3 = subprocess.run(
                [
                    sys.executable,
                    str(eval_script),
                    "--snapshot-id",
                    snapshot_id,
                    "--hvacexport-root",
                    str(hvac_root),
                    "--input-sdi",
                    str(sdi_fixture),
                    "--min-brand-support",
                    "0",
                    "--run-id",
                    "eval1",
                ],
                cwd=str(repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(p3.returncode, 0, msg=f"eval stderr:\n{p3.stderr}")

            rows_path = hvac_root / snapshot_id / "derived" / "runs" / "eval1" / "alignment_rows.csv"
            self.assertTrue(rows_path.exists())
            with rows_path.open(newline="", encoding="utf-8") as f:
                r = csv.DictReader(f)
                out_rows = list(r)
            self.assertEqual(len(out_rows), 1)
            self.assertEqual(out_rows[0]["RefrigerantResult"], "match")
            self.assertEqual(out_rows[0]["VoltageResult"], "match")


if __name__ == "__main__":
    unittest.main()
