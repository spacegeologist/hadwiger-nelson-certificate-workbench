#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hnp.dimacs import graph_from_dimacs_edge_text
from hnp.embedding import unit_edge_errors
from hnp.vtx import parse_vtx_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify that DIMACS edge graph edges are unit distances in a .vtx embedding.")
    parser.add_argument("--edge", type=Path, required=True, help="path to a DIMACS edge graph file")
    parser.add_argument("--vtx", type=Path, required=True, help="path to a CNP-SAT Mathematica-style .vtx coordinate file")
    parser.add_argument("--tolerance", type=float, default=1e-9, help="absolute distance tolerance")
    parser.add_argument("--max-errors", type=int, default=10, help="maximum number of non-unit edges to print")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    graph = graph_from_dimacs_edge_text(args.edge.read_text(encoding="utf-8"))
    coordinates = parse_vtx_text(args.vtx.read_text(encoding="utf-8"))
    errors = unit_edge_errors(graph, coordinates, tolerance=args.tolerance)

    print(f"vertices: {len(graph.vertices)}")
    print(f"edges: {len(graph.edges)}")
    print(f"coordinates: {len(coordinates)}")
    print(f"tolerance: {args.tolerance}")

    if errors:
        print("result: NON-UNIT EDGES FOUND")
        for a, b, distance in errors[: args.max_errors]:
            print(f"  {a} {b}: {distance:.17g}")
        if len(errors) > args.max_errors:
            print(f"  ... {len(errors) - args.max_errors} more")
        return 2

    print("result: all edges are unit distance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
