import unittest

from hnp.exact_embedding import exact_non_unit_edges, parse_mathematica_exact, parse_vtx_exact
from hnp.graph import Graph


class ExactEmbeddingTests(unittest.TestCase):
    def test_parses_exact_radicals(self):
        value = parse_mathematica_exact("(-Sqrt[3] + Sqrt[11])/6")
        # Squaring should stay exact: ((-r3 + r11)/6)^2 = (3 + 11 - 2*sqrt(33))/36
        import sympy

        self.assertEqual(sympy.expand(value ** 2), sympy.Rational(14, 36) - sympy.sqrt(33) / 18)

    def test_unit_triangle_is_exactly_unit(self):
        graph = Graph.from_edges(("1", "2", "3"), (("1", "2"), ("1", "3"), ("2", "3")))
        coords = parse_vtx_exact("{0, 0}\n{1, 0}\n{1/2, Sqrt[3]/2}\n")
        self.assertEqual([], exact_non_unit_edges(graph, coords))

    def test_detects_non_unit_edge_exactly(self):
        graph = Graph.from_edges(("1", "2"), (("1", "2"),))
        coords = parse_vtx_exact("{0, 0}\n{2, 0}\n")
        self.assertEqual([("1", "2")], exact_non_unit_edges(graph, coords))

    def test_near_miss_is_rejected_exactly(self):
        # A point at exact distance sqrt(1 + 1/10^9) is ~unit but not exactly unit.
        graph = Graph.from_edges(("1", "2"), (("1", "2"),))
        coords = parse_vtx_exact("{0, 0}\n{Sqrt[1 + 1/1000000000], 0}\n")
        self.assertEqual([("1", "2")], exact_non_unit_edges(graph, coords))


if __name__ == "__main__":
    unittest.main()
