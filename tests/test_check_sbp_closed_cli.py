import subprocess
import sys
import unittest


class CheckSbpClosedCliTests(unittest.TestCase):
    def test_dry_run_lists_all_reproducibility_checks(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_sbp_closed.py", "--dry-run"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("python3 -m unittest discover -s tests -v", result.stdout)
        self.assertIn("517-sbp-closed.edge", result.stdout)
        self.assertIn("529-sbp-closed.edge", result.stdout)
        self.assertIn("553-sbp-closed.edge", result.stdout)
        self.assertIn("517-sbp-closed.cnf", result.stdout)
        self.assertIn("529-sbp-closed.cnf", result.stdout)
        self.assertIn("553-sbp-closed.cnf", result.stdout)


if __name__ == "__main__":
    unittest.main()
