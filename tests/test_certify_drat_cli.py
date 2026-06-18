import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRAT_TRIM = PROJECT_ROOT / "data/hadwiger-nelson/external/drat-trim/drat-trim"

MOSER_EDGES = """p edge 7 11
e 1 2
e 1 3
e 2 3
e 2 4
e 3 4
e 1 5
e 1 6
e 5 6
e 5 7
e 6 7
e 4 7
"""


@unittest.skipUnless(DRAT_TRIM.exists(), "drat-trim binary not built")
class CertifyDratCliTests(unittest.TestCase):
    def test_moser_spindle_three_color_certificate_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edge = root / "moser.edge"
            edge.write_text(MOSER_EDGES, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "scripts/certify_drat.py", "--edge", str(edge),
                 "--colors", "3", "--cnf", str(root / "m.cnf"), "--drat", str(root / "m.drat")],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("drat-trim: VERIFIED", result.stdout)


if __name__ == "__main__":
    unittest.main()
