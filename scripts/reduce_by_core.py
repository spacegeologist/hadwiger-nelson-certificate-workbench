#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hnp.core_analysis import analyze_core_edge_usage, variable_to_vertex_color
from hnp.dimacs import graph_from_dimacs_edge_text
from hnp.graph import Edge, Graph, canonical_edge
from hnp.sat import DimacsCnf, parse_dimacs_cnf_text


def clause_edge(clause: tuple[int, ...], graph: Graph, colors: int) -> Edge | None:
    if len(clause) != 2 or clause[0] >= 0 or clause[1] >= 0:
        return None

    first_vertex, first_color = variable_to_vertex_color(abs(clause[0]), colors)
    second_vertex, second_color = variable_to_vertex_color(abs(clause[1]), colors)
    if first_vertex == second_vertex or first_color != second_color:
        return None

    edge = canonical_edge(first_vertex, second_vertex)
    return edge if edge in graph.edges else None


def render_dimacs_edge(graph: Graph) -> str:
    lines = [f"p edge {len(graph.vertices)} {len(graph.edges)}"]
    for a, b in sorted(graph.edges, key=lambda edge: (int(edge[0]), int(edge[1]))):
        lines.append(f"e {a} {b}")
    return "\n".join(lines) + "\n"


def render_cnf(variables: int, clauses: list[tuple[int, ...]]) -> str:
    lines = [f"p cnf {variables} {len(clauses)}"]
    for clause in clauses:
        lines.append(" ".join(str(literal) for literal in clause) + " 0")
    return "\n".join(lines) + "\n"


def filter_cnf_by_edges(graph: Graph, cnf: DimacsCnf, colors: int, used_edges: set[Edge]) -> list[tuple[int, ...]]:
    filtered: list[tuple[int, ...]] = []
    for clause in cnf.clauses:
        edge = clause_edge(clause, graph, colors)
        if edge is None or edge in used_edges:
            filtered.append(clause)
    return filtered


def parse_edge_spec(edge_spec: str) -> tuple[str, str]:
    if ":" in edge_spec:
        parts = edge_spec.split(":")
    elif "," in edge_spec:
        parts = edge_spec.split(",")
    else:
        raise argparse.ArgumentTypeError("preserved edges must be written as A:B or A,B")

    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise argparse.ArgumentTypeError("preserved edges must contain exactly two vertices")
    return parts[0], parts[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reduce a DIMACS edge graph using a DRAT unsat core.")
    parser.add_argument("--edge", type=Path, required=True, help="source DIMACS edge graph")
    parser.add_argument("--core", type=Path, required=True, help="DRAT-trim core CNF")
    parser.add_argument("--cnf", type=Path, required=True, help="base CNF to filter")
    parser.add_argument("--colors", type=int, required=True, help="color count used by the CNF")
    parser.add_argument(
        "--preserve-edge",
        action="append",
        type=parse_edge_spec,
        default=[],
        help="edge to keep even if absent from the core, written as A:B; repeatable",
    )
    parser.add_argument("--output-edge", type=Path, required=True, help="where to write the reduced edge graph")
    parser.add_argument("--output-cnf", type=Path, required=True, help="where to write the filtered CNF")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    graph = graph_from_dimacs_edge_text(args.edge.read_text(encoding="utf-8"))
    core = parse_dimacs_cnf_text(args.core.read_text(encoding="utf-8"))
    cnf = parse_dimacs_cnf_text(args.cnf.read_text(encoding="utf-8"))
    usage = analyze_core_edge_usage(graph, core, args.colors)
    preserved_edges = {canonical_edge(a, b) for a, b in args.preserve_edge}
    unknown_preserved_edges = preserved_edges.difference(graph.edges)
    if unknown_preserved_edges:
        raise ValueError(f"cannot preserve unknown edges: {sorted(unknown_preserved_edges)}")

    retained_edges = usage.used_edges.union(preserved_edges)
    reduced_graph = Graph.from_edges(graph.vertices, retained_edges)
    filtered_clauses = filter_cnf_by_edges(graph, cnf, args.colors, retained_edges)

    args.output_edge.parent.mkdir(parents=True, exist_ok=True)
    args.output_cnf.parent.mkdir(parents=True, exist_ok=True)
    args.output_edge.write_text(render_dimacs_edge(reduced_graph), encoding="utf-8")
    args.output_cnf.write_text(render_cnf(cnf.variables, filtered_clauses), encoding="utf-8")

    print(f"original_edges: {len(graph.edges)}")
    print(f"used_edges: {len(usage.used_edges)}")
    print(f"preserved_edges: {len(preserved_edges)}")
    print(f"removed_edges: {len(graph.edges.difference(retained_edges))}")
    print(f"original_clauses: {len(cnf.clauses)}")
    print(f"filtered_clauses: {len(filtered_clauses)}")
    print(f"wrote_edge: {args.output_edge}")
    print(f"wrote_cnf: {args.output_cnf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
