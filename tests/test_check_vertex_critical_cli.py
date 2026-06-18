import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Moser spindle with numeric labels (1..7); 4-chromatic and 3-vertex-critical.
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


class CheckVertexCriticalCliTests(unittest.TestCase):
    def test_moser_spindle_is_vertex_critical_at_three_colors(self):
        with tempfile.TemporaryDirectory() as tmp:
            edge_path = Path(tmp) / "moser.edge"
            edge_path.write_text(MOSER_EDGES, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "scripts/check_vertex_critical.py",
                 "--edge", str(edge_path), "--colors", "3"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("result: vertex-critical", result.stdout)


if __name__ == "__main__":
    unittest.main()
