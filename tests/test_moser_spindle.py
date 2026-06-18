import json
import unittest
from pathlib import Path

from hnp.coloring import find_coloring, is_proper_coloring
from hnp.embedding import unit_edge_errors
from hnp.examples import moser_spindle, moser_spindle_coordinates
from hnp.graph import Graph


class MoserSpindleTests(unittest.TestCase):
    def test_moser_spindle_is_not_three_colorable(self):
        graph = moser_spindle()

        result = find_coloring(graph, 3)

        self.assertIsNone(result.coloring)
        self.assertGreater(result.nodes, 0)

    def test_moser_spindle_is_four_colorable(self):
        graph = moser_spindle()

        result = find_coloring(graph, 4)

        self.assertIsNotNone(result.coloring)
        self.assertTrue(is_proper_coloring(graph, result.coloring or {}))

    def test_moser_spindle_edges_are_unit_distance(self):
        graph = moser_spindle()
        coordinates = moser_spindle_coordinates()

        errors = unit_edge_errors(graph, coordinates)

        self.assertEqual([], errors)

    def test_json_data_matches_builtin_graph(self):
        path = Path("data/hadwiger-nelson/moser_spindle.json")
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        graph = Graph.from_json_dict(payload)

        self.assertEqual(moser_spindle(), graph)


if __name__ == "__main__":
    unittest.main()
