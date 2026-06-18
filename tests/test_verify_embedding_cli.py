import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class VerifyEmbeddingCliTests(unittest.TestCase):
    def test_reports_unit_distance_edges(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            edge_path = root / "triangle.edge"
            vtx_path = root / "triangle.vtx"
            edge_path.write_text("p edge 3 3\ne 1 2\ne 1 3\ne 2 3\n", encoding="utf-8")
            vtx_path.write_text("{0, 0}\n{1, 0}\n{1/2, Sqrt[3]/2}\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/verify_embedding.py",
                    "--edge",
                    str(edge_path),
                    "--vtx",
                    str(vtx_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("result: all edges are unit distance", result.stdout)

    def test_reports_non_unit_edges(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            edge_path = root / "bad.edge"
            vtx_path = root / "bad.vtx"
            edge_path.write_text("p edge 2 1\ne 1 2\n", encoding="utf-8")
            vtx_path.write_text("{0, 0}\n{2, 0}\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/verify_embedding.py",
                    "--edge",
                    str(edge_path),
                    "--vtx",
                    str(vtx_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(2, result.returncode, result.stderr)
            self.assertIn("result: NON-UNIT EDGES FOUND", result.stdout)


if __name__ == "__main__":
    unittest.main()
