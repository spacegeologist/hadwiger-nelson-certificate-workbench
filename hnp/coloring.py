from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from hnp.graph import Graph


@dataclass(frozen=True)
class ColoringSearchResult:
    colors: int
    coloring: dict[str, int] | None
    nodes: int
    backtracks: int

    @property
    def colorable(self) -> bool:
        return self.coloring is not None


def is_proper_coloring(graph: Graph, coloring: Mapping[str, int]) -> bool:
    if set(coloring) != set(graph.vertices):
        return False
    return all(coloring[a] != coloring[b] for a, b in graph.edges)


def find_coloring(graph: Graph, colors: int) -> ColoringSearchResult:
    """Find a proper k-coloring, or prove none exists by exhaustive search."""

    if colors < 1:
        raise ValueError("colors must be positive")

    adjacent = graph.adjacency()
    degrees = graph.degrees()
    coloring: dict[str, int] = {}
    nodes = 0
    backtracks = 0

    def available_colors(vertex: str) -> list[int]:
        forbidden = {coloring[neighbor] for neighbor in adjacent[vertex] if neighbor in coloring}
        available = [color for color in range(colors) if color not in forbidden]

        # Color names are symmetric. This canonical rule keeps the search complete
        # while avoiding equivalent permutations of already-seen colors.
        if coloring:
            highest_seen = max(coloring.values())
            available = [color for color in available if color <= min(colors - 1, highest_seen + 1)]
        else:
            available = [0] if 0 in available else []

        return available

    def choose_vertex() -> tuple[str, list[int]]:
        best_vertex = ""
        best_available: list[int] = []
        best_key: tuple[int, int, str] | None = None

        for vertex in graph.vertices:
            if vertex in coloring:
                continue
            options = available_colors(vertex)
            key = (len(options), -degrees[vertex], vertex)
            if best_key is None or key < best_key:
                best_key = key
                best_vertex = vertex
                best_available = options

        return best_vertex, best_available

    def search() -> bool:
        nonlocal nodes, backtracks
        nodes += 1

        if len(coloring) == len(graph.vertices):
            return True

        vertex, options = choose_vertex()
        if not options:
            backtracks += 1
            return False

        for color in options:
            coloring[vertex] = color
            if search():
                return True
            del coloring[vertex]

        backtracks += 1
        return False

    if search():
        final_coloring = dict(coloring)
        if not is_proper_coloring(graph, final_coloring):
            raise RuntimeError("internal error: search returned an invalid coloring")
        return ColoringSearchResult(colors=colors, coloring=final_coloring, nodes=nodes, backtracks=backtracks)

    return ColoringSearchResult(colors=colors, coloring=None, nodes=nodes, backtracks=backtracks)
