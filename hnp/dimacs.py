from __future__ import annotations

from dataclasses import dataclass

from hnp.graph import Graph

Clause = tuple[int, ...]


@dataclass(frozen=True)
class ColoringCnf:
    colors: int
    variables: int
    clauses: list[Clause]
    vertex_index: dict[str, int]


def color_var(vertex_index: dict[str, int], vertex: str, color: int, colors: int) -> int:
    if colors < 1:
        raise ValueError("colors must be positive")
    if color < 0 or color >= colors:
        raise ValueError(f"color {color} is outside range 0..{colors - 1}")
    return vertex_index[vertex] * colors + color + 1


def coloring_cnf(graph: Graph, colors: int, require_exactly_one: bool = True) -> ColoringCnf:
    if colors < 1:
        raise ValueError("colors must be positive")

    vertex_index = {vertex: index for index, vertex in enumerate(graph.vertices)}
    clauses: list[Clause] = []

    for vertex in graph.vertices:
        clauses.append(tuple(color_var(vertex_index, vertex, color, colors) for color in range(colors)))
        if require_exactly_one:
            for first in range(colors):
                for second in range(first + 1, colors):
                    clauses.append(
                        (
                            -color_var(vertex_index, vertex, first, colors),
                            -color_var(vertex_index, vertex, second, colors),
                        )
                    )

    for a, b in sorted(graph.edges):
        for color in range(colors):
            clauses.append(
                (
                    -color_var(vertex_index, a, color, colors),
                    -color_var(vertex_index, b, color, colors),
                )
            )

    return ColoringCnf(
        colors=colors,
        variables=len(graph.vertices) * colors,
        clauses=clauses,
        vertex_index=vertex_index,
    )


def to_dimacs(cnf: ColoringCnf) -> str:
    lines: list[str] = []
    vertices_by_index = sorted(cnf.vertex_index, key=cnf.vertex_index.__getitem__)
    for vertex in vertices_by_index:
        for color in range(cnf.colors):
            variable = color_var(cnf.vertex_index, vertex, color, cnf.colors)
            lines.append(f"c vertex {vertex} color {color} var {variable}")

    lines.append(f"p cnf {cnf.variables} {len(cnf.clauses)}")
    for clause in cnf.clauses:
        lines.append(" ".join(str(literal) for literal in clause) + " 0")
    return "\n".join(lines) + "\n"


def graph_from_dimacs_edge_text(text: str) -> Graph:
    vertex_count: int | None = None
    expected_edges: int | None = None
    edges: list[tuple[str, str]] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("c"):
            continue

        parts = line.split()
        if parts[0] == "p":
            if len(parts) != 4 or parts[1] != "edge":
                raise ValueError(f"line {line_number}: expected 'p edge <vertices> <edges>'")
            vertex_count = int(parts[2])
            expected_edges = int(parts[3])
            continue

        if parts[0] == "e":
            if len(parts) != 3:
                raise ValueError(f"line {line_number}: expected 'e <u> <v>'")
            edges.append((parts[1], parts[2]))
            continue

        raise ValueError(f"line {line_number}: unsupported DIMACS edge record {parts[0]!r}")

    if vertex_count is None or expected_edges is None:
        raise ValueError("missing DIMACS edge header")
    if len(edges) != expected_edges:
        raise ValueError(f"edge count mismatch: header says {expected_edges}, found {len(edges)}")

    vertices = tuple(str(index) for index in range(1, vertex_count + 1))
    return Graph.from_edges(vertices, edges)
