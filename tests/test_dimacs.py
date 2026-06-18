import unittest

from hnp.dimacs import color_var, coloring_cnf, graph_from_dimacs_edge_text, to_dimacs
from hnp.graph import Graph


class DimacsTests(unittest.TestCase):
    def test_color_var_numbers_vertices_by_input_order_then_color(self):
        graph = Graph.from_edges(("u", "v"), (("u", "v"),))
        vertex_index = {vertex: index for index, vertex in enumerate(graph.vertices)}

        self.assertEqual(1, color_var(vertex_index, "u", 0, 3))
        self.assertEqual(3, color_var(vertex_index, "u", 2, 3))
        self.assertEqual(4, color_var(vertex_index, "v", 0, 3))
        self.assertEqual(6, color_var(vertex_index, "v", 2, 3))

    def test_coloring_cnf_for_single_edge_with_two_colors(self):
        graph = Graph.from_edges(("u", "v"), (("u", "v"),))

        cnf = coloring_cnf(graph, 2)

        self.assertEqual(4, cnf.variables)
        self.assertEqual(
            [
                (1, 2),
                (-1, -2),
                (3, 4),
                (-3, -4),
                (-1, -3),
                (-2, -4),
            ],
            cnf.clauses,
        )

    def test_coloring_cnf_can_skip_at_most_one_color_clauses(self):
        graph = Graph.from_edges(("u", "v"), (("u", "v"),))

        cnf = coloring_cnf(graph, 2, require_exactly_one=False)

        self.assertEqual(
            [
                (1, 2),
                (3, 4),
                (-1, -3),
                (-2, -4),
            ],
            cnf.clauses,
        )

    def test_to_dimacs_renders_header_comments_and_clauses(self):
        graph = Graph.from_edges(("u", "v"), (("u", "v"),))
        cnf = coloring_cnf(graph, 2)

        dimacs = to_dimacs(cnf)

        self.assertIn("c vertex u color 0 var 1", dimacs)
        self.assertIn("c vertex v color 1 var 4", dimacs)
        self.assertIn("p cnf 4 6", dimacs)
        self.assertTrue(dimacs.endswith("0\n"))

    def test_graph_from_dimacs_edge_text(self):
        graph = graph_from_dimacs_edge_text(
            """
            c small graph
            p edge 3 2
            e 1 2
            e 2 3
            """
        )

        self.assertEqual(("1", "2", "3"), graph.vertices)
        self.assertEqual(frozenset({("1", "2"), ("2", "3")}), graph.edges)


if __name__ == "__main__":
    unittest.main()
