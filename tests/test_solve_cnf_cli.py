import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class SolveCnfCliTests(unittest.TestCase):
    def test_script_reports_sat(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sat.cnf"
            path.write_text("p cnf 1 1\n1 0\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/solve_cnf.py", str(path), "--solver", "minisat22", "--timeout", "5"],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(10, result.returncode, result.stderr)
            self.assertIn("result: SAT", result.stdout)

    def test_script_reports_unsat(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "unsat.cnf"
            path.write_text("p cnf 1 2\n1 0\n-1 0\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/solve_cnf.py", str(path), "--solver", "minisat22", "--timeout", "5"],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(20, result.returncode, result.stderr)
            self.assertIn("result: UNSAT", result.stdout)


if __name__ == "__main__":
    unittest.main()
