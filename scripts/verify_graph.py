#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hnp.coloring import find_coloring
from hnp.dimacs import coloring_cnf, graph_from_dimacs_edge_text, to_dimacs
from hnp.examples import moser_spindle
from hnp.graph import Graph


def load_json_graph(path: Path) -> Graph:
    with path.open("r", encoding="utf-8") as handle:
        payload: dict[str, Any] = json.load(handle)
    return Graph.from_json_dict(payload)


def load_edge_graph(path: Path) -> Graph:
    return graph_from_dimacs_edge_text(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify k-colorability for a finite graph.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--example", choices=("moser",), help="built-in example graph")
    source.add_argument("--graph", type=Path, help="path to a graph JSON file")
    source.add_argument("--edge", type=Path, help="path to a DIMACS edge graph file")
    parser.add_argument("--colors", type=int, required=True, help="number of colors to test")
    parser.add_argument(
        "--encoding",
        choices=("exact", "cover"),
        default="exact",
        help="CNF encoding for --dimacs: exact means exactly one color per vertex; cover omits at-most-one clauses",
    )
    parser.add_argument("--dimacs", type=Path, help="write k-colorability CNF to this DIMACS file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.example == "moser":
        graph = moser_spindle()
    elif args.graph is not None:
        graph = load_json_graph(args.graph)
    else:
        graph = load_edge_graph(args.edge)

    if args.dimacs is not None:
        cnf = coloring_cnf(graph, args.colors, require_exactly_one=args.encoding == "exact")
        args.dimacs.parent.mkdir(parents=True, exist_ok=True)
        args.dimacs.write_text(to_dimacs(cnf), encoding="utf-8")
        print(f"wrote DIMACS CNF: {args.dimacs}")
        print(f"variables: {cnf.variables}")
        print(f"clauses: {len(cnf.clauses)}")
        return 0

    result = find_coloring(graph, args.colors)

    print(f"vertices: {len(graph.vertices)}")
    print(f"edges: {len(graph.edges)}")
    print(f"colors: {args.colors}")
    print(f"search nodes: {result.nodes}")
    print(f"backtracks: {result.backtracks}")

    if result.coloring is None:
        print("result: NOT colorable")
        return 2

    print("result: colorable")
    print("coloring:")
    for vertex in graph.vertices:
        print(f"  {vertex}: {result.coloring[vertex]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
