from __future__ import annotations

from math import hypot
from typing import Mapping

from hnp.graph import Graph

Point = tuple[float, float]


def squared_distance(a: Point, b: Point) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def unit_edge_errors(
    graph: Graph,
    coordinates: Mapping[str, Point],
    tolerance: float = 1e-9,
) -> list[tuple[str, str, float]]:
    missing = [vertex for vertex in graph.vertices if vertex not in coordinates]
    if missing:
        raise ValueError(f"missing coordinates for vertices: {missing}")

    errors: list[tuple[str, str, float]] = []
    for a, b in sorted(graph.edges):
        distance = hypot(coordinates[a][0] - coordinates[b][0], coordinates[a][1] - coordinates[b][1])
        if abs(distance - 1.0) > tolerance:
            errors.append((a, b, distance))
    return errors
