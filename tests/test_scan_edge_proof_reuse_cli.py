import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class ScanEdgeProofReuseCliTests(unittest.TestCase):
    def test_dry_run_lists_candidates_after_preserved_edges(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            edge_path = root / "graph.edge"
            cnf_path = root / "graph.cnf"
            proof_path = root / "graph.drat"
            edge_path.write_text("p edge 3 2\ne 1 2\ne 2 3\n", encoding="utf-8")
            cnf_path.write_text("p cnf 6 2\n-1 -3 0\n-3 -5 0\n", encoding="utf-8")
            proof_path.write_text("", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/scan_edge_proof_reuse.py",
                    "--edge",
                    str(edge_path),
                    "--cnf",
                    str(cnf_path),
                    "--proof",
                    str(proof_path),
                    "--colors",
                    "2",
                    "--preserve-edge",
                    "1:2",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("candidates: 1", result.stdout)
            self.assertIn("2:3", result.stdout)
            self.assertNotIn("1:2", result.stdout)

    def test_writes_verified_rows_from_checker_output(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            edge_path = root / "graph.edge"
            cnf_path = root / "graph.cnf"
            proof_path = root / "graph.drat"
            checker_path = root / "fake-drat-trim.py"
            output_path = root / "scan.csv"

            edge_path.write_text("p edge 3 2\ne 1 2\ne 2 3\n", encoding="utf-8")
            cnf_path.write_text(
                "p cnf 6 4\n"
                "1 2 0\n"
                "3 4 0\n"
                "-1 -3 0\n"
                "-3 -5 0\n",
                encoding="utf-8",
            )
            proof_path.write_text("fake proof\n", encoding="utf-8")
            checker_path.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                "text = open(sys.argv[1], encoding='utf-8').read()\n"
                "print('s VERIFIED' if '-3 -5 0' not in text else 's NOT VERIFIED')\n",
                encoding="utf-8",
            )
            checker_path.chmod(0o755)

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/scan_edge_proof_reuse.py",
                    "--edge",
                    str(edge_path),
                    "--cnf",
                    str(cnf_path),
                    "--proof",
                    str(proof_path),
                    "--colors",
                    "2",
                    "--drat-trim",
                    str(checker_path),
                    "--preserve-edge",
                    "1:2",
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("2:3,VERIFIED", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
