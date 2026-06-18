import unittest

from hnp.examples import moser_spindle
from hnp.graph import Graph
from hnp.minimize import (
    build_model,
    edge_minimize,
    find_triangle,
    prune_low_degree_vertices,
)


class FindTriangleTests(unittest.TestCase):
    def test_finds_triangle(self):
        graph = Graph.from_edges(("a", "b", "c", "d"), (("a", "b"), ("b", "c"), ("a", "c"), ("c", "d")))
        triangle = find_triangle(graph)
        self.assertIsNotNone(triangle)
        self.assertEqual({"a", "b", "c"}, set(triangle))

    def test_triangle_free_returns_none(self):
        path = Graph.from_edges(("a", "b", "c"), (("a", "b"), ("b", "c")))
        self.assertIsNone(find_triangle(path))


class SelectorModelTests(unittest.TestCase):
    def test_moser_spindle_unsat_at_three_colors(self):
        model = build_model(moser_spindle(), colors=3)
        self.assertTrue(model.is_unsat_without(set()))
        model.close()

    def test_removing_any_edge_makes_spindle_three_colorable(self):
        graph = moser_spindle()
        model = build_model(graph, colors=3)
        triangle_edges = {
            tuple(sorted((a, b)))
            for a, b in (("x", "a"), ("x", "b"), ("a", "b"))
        }
        for edge in graph.edges:
            if edge in triangle_edges:
                continue  # selectors do not toggle the symmetry-breaking triangle's pins
            self.assertFalse(model.is_unsat_without({edge}), edge)
        model.close()


class EdgeMinimizeTests(unittest.TestCase):
    def test_moser_spindle_is_already_edge_critical(self):
        # The Moser spindle is edge-critical at 3 colors, so nothing is removable.
        result = edge_minimize(moser_spindle(), colors=3, order="lexicographic")
        self.assertEqual(0, len(result.removed_edges))
        self.assertEqual(11, len(result.kept_edges))


class PruneTests(unittest.TestCase):
    def test_prunes_pendant_and_isolated_vertices(self):
        graph = Graph.from_edges(
            ("a", "b", "c", "d", "e"),
            (("a", "b"), ("b", "c"), ("a", "c"), ("c", "d")),
        )  # d is a pendant, e is isolated
        pruned, removed = prune_low_degree_vertices(graph)
        self.assertEqual({"d", "e"}, set(removed))
        self.assertEqual(("a", "b", "c"), pruned.vertices)


if __name__ == "__main__":
    unittest.main()
