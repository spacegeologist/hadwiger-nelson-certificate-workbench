#!/usr/bin/env python3
"""Deletion-minimize a non-4-colorable unit-distance graph and verify the result.

Pipeline:
  1. edge_minimize: greedily delete edges while the graph stays non-4-colorable,
     producing an edge-critical subgraph.
  2. prune_low_degree_vertices: drop vertices that become degree <= 1.
  3. Re-verify non-4-colorability with a fresh solver (independent of the
     incremental search) and re-verify unit-distance geometry against the .vtx.
  4. Emit a reduced .edge file, a matching .vtx subset, and a JSON report.

Every accepted/rejected edge decision is summarized in the report so the run is
reproducible in the karpathy/autoresearch sense: fixed environment, logged
outcomes.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hnp.dimacs import coloring_cnf, graph_from_dimacs_edge_text
from hnp.embedding import unit_edge_errors
from hnp.graph import Graph
from hnp.minimize import edge_minimize, prune_low_degree_vertices
from hnp.vtx import parse_vtx_text
from pysat.solvers import Cadical153


def write_edge_file(path: Path, graph: Graph) -> None:
    # Keep numeric vertex labels in sorted numeric order for stable output.
    def key(v: str) -> tuple:
        return (0, int(v)) if v.isdigit() else (1, v)

    edges = sorted(graph.edges, key=lambda e: (key(e[0]), key(e[1])))
    lines = [f"p edge {len(graph.vertices)} {len(graph.edges)}"]
    lines.extend(f"e {a} {b}" for a, b in edges)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def independent_unsat_check(graph: Graph, colors: int, timeout: float) -> tuple[str, float]:
    """Solve a plain (no-selector) CNF with a fresh solver as an independent check."""
    cnf = coloring_cnf(graph, colors)
    solver = Cadical153(bootstrap_with=cnf.clauses, use_timer=True)
    start = time.perf_counter()
    sat = solver.solve()
    elapsed = time.perf_counter() - start
    solver.delete()
    return ("SAT" if sat else "UNSAT", elapsed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edge", type=Path, required=True)
    parser.add_argument("--vtx", type=Path, default=None)
    parser.add_argument("--colors", type=int, default=4)
    parser.add_argument("--order", default="high-degree-first",
                        choices=["high-degree-first", "low-degree-first", "lexicographic"])
    parser.add_argument("--conflict-budget", type=int, default=0,
                        help="per-solve conflict budget; 0 solves to completion")
    parser.add_argument("--out-edge", type=Path, required=True)
    parser.add_argument("--out-vtx", type=Path, default=None)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--log", type=Path, default=None)
    args = parser.parse_args()

    graph = graph_from_dimacs_edge_text(args.edge.read_text(encoding="utf-8"))
    coords = parse_vtx_text(args.vtx.read_text(encoding="utf-8")) if args.vtx else None

    log_handle = open(args.log, "w", encoding="utf-8") if args.log else None
    start_wall = time.time()

    def progress(done: int, total: int, removed: int, model) -> None:
        if done % 100 == 0 or done == total:
            msg = (f"[{time.time()-start_wall:7.1f}s] edges {done}/{total} "
                   f"removed={removed} solves={model.solve_calls} "
                   f"solve_s={model.solve_seconds:.1f}")
            if log_handle:
                log_handle.write(msg + "\n")
                log_handle.flush()

    result = edge_minimize(graph, colors=args.colors, order=args.order,
                           conflict_budget=args.conflict_budget, progress=progress)
    edge_reduced = graph.without_edges(result.removed_edges)
    pruned, removed_vertices = prune_low_degree_vertices(edge_reduced)

    # Independent re-verification on a fresh solver (no selectors, no SBP pins).
    status, verify_s = independent_unsat_check(pruned, args.colors, timeout=0)

    geometry = None
    if coords is not None:
        sub_coords = {v: coords[v] for v in pruned.vertices}
        errors = unit_edge_errors(pruned, sub_coords, tolerance=1e-9)
        geometry = {"non_unit_edges": len(errors)}

    write_edge_file(args.out_edge, pruned)
    if args.out_vtx and coords is not None:
        def key(v: str) -> tuple:
            return (0, int(v)) if v.isdigit() else (1, v)
        ordered = sorted(pruned.vertices, key=key)
        # Note: vertex labels are not renumbered, so the .vtx is keyed by label.
        lines = [f"{v}: {{{coords[v][0]!r}, {coords[v][1]!r}}}" for v in ordered]
        args.out_vtx.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = {
        "input": {
            "edge_file": str(args.edge),
            "vertices": len(graph.vertices),
            "edges": len(graph.edges),
        },
        "order": args.order,
        "edge_minimization": {
            "removed_edges": len(result.removed_edges),
            "kept_edges": len(result.kept_edges),
            "solve_calls": result.solve_calls,
            "solve_seconds": round(result.solve_seconds, 2),
            "budget_exceeded": result.budget_exceeded,
            "conflict_budget": args.conflict_budget,
        },
        "vertex_pruning": {
            "removed_vertices": len(removed_vertices),
            "removed_vertex_labels": sorted(removed_vertices, key=lambda v: (int(v) if v.isdigit() else 1 << 30)),
        },
        "result": {
            "vertices": len(pruned.vertices),
            "edges": len(pruned.edges),
            "independent_check": status,
            "independent_check_seconds": round(verify_s, 3),
            "geometry": geometry,
        },
        "wall_seconds": round(time.time() - start_wall, 1),
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if log_handle:
        log_handle.write("DONE " + json.dumps(report["result"]) + "\n")
        log_handle.close()

    print(json.dumps(report, indent=2))
    return 0 if status == "UNSAT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
