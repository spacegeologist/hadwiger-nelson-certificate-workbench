import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class VerifyGraphCliTests(unittest.TestCase):
    def test_script_runs_from_project_root(self):
        result = subprocess.run(
            [sys.executable, "scripts/verify_graph.py", "--example", "moser", "--colors", "4"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("result: colorable", result.stdout)

    def test_script_writes_dimacs_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "moser-4.cnf"

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/verify_graph.py",
                    "--example",
                    "moser",
                    "--colors",
                    "4",
                    "--dimacs",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("wrote DIMACS CNF", result.stdout)
            dimacs = output_path.read_text(encoding="utf-8")
            self.assertIn("p cnf 28 93", dimacs)
            self.assertIn("c vertex x color 0 var 1", dimacs)

    def test_script_writes_dimacs_from_edge_file_with_cover_encoding(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            edge_path = Path(temporary_directory) / "path.edge"
            edge_path.write_text("p edge 3 2\ne 1 2\ne 2 3\n", encoding="utf-8")
            output_path = Path(temporary_directory) / "path-2.cnf"

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/verify_graph.py",
                    "--edge",
                    str(edge_path),
                    "--colors",
                    "2",
                    "--encoding",
                    "cover",
                    "--dimacs",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            dimacs = output_path.read_text(encoding="utf-8")
            self.assertIn("p cnf 6 7", dimacs)


if __name__ == "__main__":
    unittest.main()
