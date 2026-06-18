#!/usr/bin/env python3
"""Empirically test whether a non-4-colorable graph is vertex-critical.

A graph G is k-vertex-critical when deleting *any* single vertex makes it
k-colorable.  We test this with the incremental selector model: deleting a vertex
is the same as deleting all its incident edges, so for each vertex we assume its
incident edge selectors are on and check that the result is satisfiable.

This backs the deletion lower bound in
docs/hadwiger-nelson/lab-notes/2026-06-18-phase-5.md: a vertex-critical graph
cannot be reduced below its vertex count by any edge/vertex deletion.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hnp.dimacs import graph_from_dimacs_edge_text
from hnp.graph import canonical_edge
from hnp.minimize import build_model


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edge", type=Path, required=True)
    parser.add_argument("--colors", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0, help="check only the first N vertices (0 = all)")
    args = parser.parse_args()

    graph = graph_from_dimacs_edge_text(args.edge.read_text(encoding="utf-8"))
    adjacency = graph.adjacency()
    model = build_model(graph, colors=args.colors)

    # Sanity: the whole graph must be non-k-colorable to begin with.
    assert model.is_unsat_without(set()) is True, "input graph is k-colorable; not a certificate"

    vertices = list(graph.vertices)
    if args.limit:
        vertices = vertices[: args.limit]

    start = time.perf_counter()
    non_critical = []
    for index, vertex in enumerate(vertices, start=1):
        incident = {canonical_edge(vertex, n) for n in adjacency[vertex]}
        colorable = model.is_unsat_without(incident) is False
        if not colorable:
            non_critical.append(vertex)
        if index % 100 == 0:
            print(f"  checked {index}/{len(vertices)} ({time.perf_counter()-start:.1f}s)", flush=True)
    model.close()

    print(f"vertices_checked: {len(vertices)}")
    print(f"seconds: {time.perf_counter()-start:.1f}")
    if non_critical:
        print(f"result: NOT vertex-critical; {len(non_critical)} removable vertices keep it non-{args.colors}-colorable")
        print(f"  examples: {non_critical[:10]}")
        return 1
    print(f"result: vertex-critical (every single-vertex deletion is {args.colors}-colorable)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
