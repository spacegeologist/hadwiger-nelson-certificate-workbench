import unittest

from hnp.graph import Graph


class GraphTests(unittest.TestCase):
    def test_without_vertices_removes_incident_edges_and_preserves_order(self):
        graph = Graph.from_edges(("a", "b", "c", "d"), (("a", "b"), ("b", "c"), ("c", "d")))

        reduced = graph.without_vertices({"b"})

        self.assertEqual(("a", "c", "d"), reduced.vertices)
        self.assertEqual(frozenset({("c", "d")}), reduced.edges)

    def test_without_edges_removes_canonical_edges(self):
        graph = Graph.from_edges(("a", "b", "c"), (("a", "b"), ("b", "c")))

        reduced = graph.without_edges({("b", "a")})

        self.assertEqual(graph.vertices, reduced.vertices)
        self.assertEqual(frozenset({("b", "c")}), reduced.edges)


if __name__ == "__main__":
    unittest.main()
