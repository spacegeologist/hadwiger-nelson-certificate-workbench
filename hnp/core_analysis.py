from __future__ import annotations

from dataclasses import dataclass

from hnp.graph import Edge, Graph, canonical_edge
from hnp.sat import DimacsCnf


@dataclass(frozen=True)
class CoreEdgeUsage:
    used_edges: set[Edge]
    unused_edges: set[Edge]
    edge_clause_counts: dict[Edge, int]


def variable_to_vertex_color(variable: int, colors: int) -> tuple[str, int]:
    if variable < 1:
        raise ValueError("DIMACS variables are 1-based")
    zero_based = variable - 1
    vertex = str(zero_based // colors + 1)
    color = zero_based % colors
    return vertex, color


def analyze_core_edge_usage(graph: Graph, core: DimacsCnf, colors: int) -> CoreEdgeUsage:
    graph_edges = set(graph.edges)
    edge_clause_counts: dict[Edge, int] = {}

    for clause in core.clauses:
        if len(clause) != 2 or clause[0] >= 0 or clause[1] >= 0:
            continue

        first_vertex, first_color = variable_to_vertex_color(abs(clause[0]), colors)
        second_vertex, second_color = variable_to_vertex_color(abs(clause[1]), colors)
        if first_vertex == second_vertex or first_color != second_color:
            continue

        edge = canonical_edge(first_vertex, second_vertex)
        if edge not in graph_edges:
            continue

        edge_clause_counts[edge] = edge_clause_counts.get(edge, 0) + 1

    used_edges = set(edge_clause_counts)
    return CoreEdgeUsage(
        used_edges=used_edges,
        unused_edges=graph_edges.difference(used_edges),
        edge_clause_counts=edge_clause_counts,
    )
