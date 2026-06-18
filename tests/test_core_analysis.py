import unittest

from hnp.core_analysis import analyze_core_edge_usage, variable_to_vertex_color
from hnp.graph import Graph
from hnp.sat import parse_dimacs_cnf_text


class CoreAnalysisTests(unittest.TestCase):
    def test_variable_to_vertex_color(self):
        self.assertEqual(("1", 0), variable_to_vertex_color(1, 4))
        self.assertEqual(("1", 3), variable_to_vertex_color(4, 4))
        self.assertEqual(("2", 0), variable_to_vertex_color(5, 4))

    def test_analyze_core_edge_usage_marks_unused_edges(self):
        graph = Graph.from_edges(("1", "2", "3"), (("1", "2"), ("2", "3")))
        core = parse_dimacs_cnf_text(
            """
            p cnf 6 3
            1 2 0
            3 4 0
            -1 -3 0
            """
        )

        usage = analyze_core_edge_usage(graph, core, colors=2)

        self.assertEqual({("1", "2")}, usage.used_edges)
        self.assertEqual({("2", "3")}, usage.unused_edges)
        self.assertEqual({("1", "2"): 1}, usage.edge_clause_counts)


if __name__ == "__main__":
    unittest.main()
