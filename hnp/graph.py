from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

Edge = tuple[str, str]


def canonical_edge(a: str, b: str) -> Edge:
    if a == b:
        raise ValueError(f"self-loop is not allowed: {a!r}")
    return (a, b) if a < b else (b, a)


@dataclass(frozen=True)
class Graph:
    """A small immutable undirected graph model."""

    vertices: tuple[str, ...]
    edges: frozenset[Edge]

    @classmethod
    def from_edges(cls, vertices: Iterable[str], edges: Iterable[tuple[str, str]]) -> "Graph":
        vertex_tuple = tuple(vertices)
        vertex_set = set(vertex_tuple)
        if len(vertex_tuple) != len(vertex_set):
            raise ValueError("vertices must be unique")

        canonical_edges: set[Edge] = set()
        for a, b in edges:
            if a not in vertex_set or b not in vertex_set:
                raise ValueError(f"edge references missing vertex: {(a, b)!r}")
            canonical_edges.add(canonical_edge(a, b))

        return cls(vertices=vertex_tuple, edges=frozenset(canonical_edges))

    @classmethod
    def from_json_dict(cls, payload: Mapping[str, object]) -> "Graph":
        raw_vertices = payload.get("vertices")
        raw_edges = payload.get("edges")
        if not isinstance(raw_vertices, list) or not all(isinstance(v, str) for v in raw_vertices):
            raise ValueError("JSON graph must contain a string list named 'vertices'")
        if not isinstance(raw_edges, list):
            raise ValueError("JSON graph must contain a list named 'edges'")

        edges: list[tuple[str, str]] = []
        for raw_edge in raw_edges:
            if (
                not isinstance(raw_edge, list)
                or len(raw_edge) != 2
                or not isinstance(raw_edge[0], str)
                or not isinstance(raw_edge[1], str)
            ):
                raise ValueError(f"invalid edge entry: {raw_edge!r}")
            edges.append((raw_edge[0], raw_edge[1]))

        return cls.from_edges(raw_vertices, edges)

    def adjacency(self) -> dict[str, set[str]]:
        adjacent = {vertex: set() for vertex in self.vertices}
        for a, b in self.edges:
            adjacent[a].add(b)
            adjacent[b].add(a)
        return adjacent

    def degrees(self) -> dict[str, int]:
        return {vertex: len(neighbors) for vertex, neighbors in self.adjacency().items()}

    def without_vertices(self, vertices_to_remove: Iterable[str]) -> "Graph":
        removed = set(vertices_to_remove)
        unknown = removed.difference(self.vertices)
        if unknown:
            raise ValueError(f"cannot remove unknown vertices: {sorted(unknown)}")

        vertices = tuple(vertex for vertex in self.vertices if vertex not in removed)
        edges = tuple((a, b) for a, b in self.edges if a not in removed and b not in removed)
        return Graph.from_edges(vertices, edges)

    def without_edges(self, edges_to_remove: Iterable[tuple[str, str]]) -> "Graph":
        removed = {canonical_edge(a, b) for a, b in edges_to_remove}
        unknown = removed.difference(self.edges)
        if unknown:
            raise ValueError(f"cannot remove unknown edges: {sorted(unknown)}")

        edges = tuple(edge for edge in self.edges if edge not in removed)
        return Graph.from_edges(self.vertices, edges)
