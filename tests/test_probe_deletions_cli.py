import subprocess
import sys
import unittest


class ProbeDeletionsCliTests(unittest.TestCase):
    def test_probe_vertex_deletion_on_moser(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/probe_deletions.py",
                "--example",
                "moser",
                "--colors",
                "3",
                "--kind",
                "vertices",
                "--limit",
                "1",
                "--timeout",
                "5",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("kind,candidate,vertices,edges,variables,clauses,status,seconds", result.stdout)
        self.assertIn("vertex,x,6,7,18,45,SAT", result.stdout)

    def test_probe_can_start_after_initial_candidates(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/probe_deletions.py",
                "--example",
                "moser",
                "--colors",
                "3",
                "--kind",
                "vertices",
                "--start",
                "1",
                "--limit",
                "1",
                "--timeout",
                "5",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("vertex,a,6,8,18,48,SAT", result.stdout)
        self.assertNotIn("vertex,x,", result.stdout)


if __name__ == "__main__":
    unittest.main()
