import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class ReduceByCoreCliTests(unittest.TestCase):
    def test_reduces_edge_graph_and_filters_cnf(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            edge_path = root / "graph.edge"
            core_path = root / "core.cnf"
            cnf_path = root / "base.cnf"
            output_edge = root / "reduced.edge"
            output_cnf = root / "reduced.cnf"

            edge_path.write_text("p edge 3 2\ne 1 2\ne 2 3\n", encoding="utf-8")
            core_path.write_text("p cnf 6 1\n-1 -3 0\n", encoding="utf-8")
            cnf_path.write_text(
                "p cnf 6 4\n"
                "1 2 0\n"
                "3 4 0\n"
                "-1 -3 0\n"
                "-3 -5 0\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/reduce_by_core.py",
                    "--edge",
                    str(edge_path),
                    "--core",
                    str(core_path),
                    "--cnf",
                    str(cnf_path),
                    "--colors",
                    "2",
                    "--output-edge",
                    str(output_edge),
                    "--output-cnf",
                    str(output_cnf),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("removed_edges: 1", result.stdout)
            self.assertEqual("p edge 3 1\ne 1 2\n", output_edge.read_text(encoding="utf-8"))
            self.assertEqual("p cnf 6 3\n1 2 0\n3 4 0\n-1 -3 0\n", output_cnf.read_text(encoding="utf-8"))

    def test_can_preserve_edges_needed_for_symmetry_breaking(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            edge_path = root / "graph.edge"
            core_path = root / "core.cnf"
            cnf_path = root / "base.cnf"
            output_edge = root / "reduced.edge"
            output_cnf = root / "reduced.cnf"

            edge_path.write_text("p edge 3 2\ne 1 2\ne 2 3\n", encoding="utf-8")
            core_path.write_text("p cnf 6 1\n-1 -3 0\n", encoding="utf-8")
            cnf_path.write_text(
                "p cnf 6 4\n"
                "1 2 0\n"
                "3 4 0\n"
                "-1 -3 0\n"
                "-3 -5 0\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/reduce_by_core.py",
                    "--edge",
                    str(edge_path),
                    "--core",
                    str(core_path),
                    "--cnf",
                    str(cnf_path),
                    "--colors",
                    "2",
                    "--preserve-edge",
                    "2:3",
                    "--output-edge",
                    str(output_edge),
                    "--output-cnf",
                    str(output_cnf),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("preserved_edges: 1", result.stdout)
            self.assertEqual("p edge 3 2\ne 1 2\ne 2 3\n", output_edge.read_text(encoding="utf-8"))
            self.assertEqual(
                "p cnf 6 4\n1 2 0\n3 4 0\n-1 -3 0\n-3 -5 0\n",
                output_cnf.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
