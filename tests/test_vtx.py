import math
import unittest

from hnp.graph import Graph
from hnp.embedding import unit_edge_errors
from hnp.vtx import parse_mathematica_number, parse_vtx_text


class VtxParserTests(unittest.TestCase):
    def test_parses_mathematica_square_roots_and_rationals(self):
        value = parse_mathematica_number("(-1 + Sqrt[33])/12")

        self.assertAlmostEqual((-1 + math.sqrt(33)) / 12, value)

    def test_parses_nested_square_root_fraction(self):
        value = parse_mathematica_number("-1/(2*Sqrt[3])")

        self.assertAlmostEqual(-1 / (2 * math.sqrt(3)), value)

    def test_vtx_lines_are_one_based_vertex_coordinates(self):
        coordinates = parse_vtx_text(
            "\n".join(
                [
                    "{0, 0}",
                    "{1, 0}",
                    "{1/2, Sqrt[3]/2}",
                ]
            )
        )

        self.assertEqual({"1", "2", "3"}, set(coordinates))
        graph = Graph.from_edges(("1", "2", "3"), (("1", "2"), ("1", "3"), ("2", "3")))
        self.assertEqual([], unit_edge_errors(graph, coordinates))

    def test_rejects_unsupported_calls(self):
        with self.assertRaises(ValueError):
            parse_mathematica_number("__import__('os').system('echo bad')")


if __name__ == "__main__":
    unittest.main()
