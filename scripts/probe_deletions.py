#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hnp.dimacs import coloring_cnf, graph_from_dimacs_edge_text, to_dimacs
from hnp.examples import moser_spindle
from hnp.graph import Graph
from hnp.sat import solve_dimacs_cnf_text


def load_json_graph(path: Path) -> Graph:
    with path.open("r", encoding="utf-8") as handle:
        payload: dict[str, Any] = json.load(handle)
    return Graph.from_json_dict(payload)


def load_graph(args: argparse.Namespace) -> Graph:
    if args.example == "moser":
        return moser_spindle()
    if args.graph is not None:
        return load_json_graph(args.graph)
    return graph_from_dimacs_edge_text(args.edge.read_text(encoding="utf-8"))


def solve_worker(dimacs: str, solver_name: str, queue: mp.Queue) -> None:
    try:
        result = solve_dimacs_cnf_text(dimacs, solver_name=solver_name)
        queue.put(("ok", result.satisfiable, result.seconds))
    except Exception as error:  # pragma: no cover - surfaced through CLI output
        queue.put(("error", repr(error), 0.0))


def solve_with_timeout(dimacs: str, solver_name: str, timeout: float) -> tuple[str, float]:
    queue: mp.Queue = mp.Queue()
    process = mp.Process(target=solve_worker, args=(dimacs, solver_name, queue))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        return ("TIMEOUT", timeout)

    if queue.empty():
        return ("ERROR", 0.0)

    status, payload, seconds = queue.get()
    if status == "error":
        return (f"ERROR:{payload}", seconds)
    return ("SAT" if payload else "UNSAT", seconds)


def candidate_graphs(graph: Graph, kind: str, start: int, limit: int) -> list[tuple[str, str, Graph]]:
    if kind == "vertices":
        return [
            ("vertex", vertex, graph.without_vertices({vertex}))
            for vertex in graph.vertices[start : start + limit]
        ]

    return [
        ("edge", f"{a}-{b}", graph.without_edges({(a, b)}))
        for a, b in sorted(graph.edges)[start : start + limit]
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe whether vertex/edge deletions preserve non-colorability.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--example", choices=("moser",), help="built-in example graph")
    source.add_argument("--graph", type=Path, help="path to a graph JSON file")
    source.add_argument("--edge", type=Path, help="path to a DIMACS edge graph file")
    parser.add_argument("--colors", type=int, required=True, help="number of colors to test")
    parser.add_argument("--kind", choices=("vertices", "edges"), default="vertices", help="deletion candidates")
    parser.add_argument("--start", type=int, default=0, help="zero-based candidate offset before applying --limit")
    parser.add_argument("--limit", type=int, default=10, help="maximum number of candidates to test")
    parser.add_argument(
        "--encoding",
        choices=("exact", "cover"),
        default="exact",
        help="CNF encoding: exact means exactly one color per vertex; cover omits at-most-one clauses",
    )
    parser.add_argument("--solver", default="cadical153", help="PySAT solver name")
    parser.add_argument("--timeout", type=float, default=5.0, help="seconds per candidate")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    graph = load_graph(args)
    require_exactly_one = args.encoding == "exact"

    print("kind,candidate,vertices,edges,variables,clauses,status,seconds")
    for kind, candidate, reduced in candidate_graphs(graph, args.kind, args.start, args.limit):
        cnf = coloring_cnf(reduced, args.colors, require_exactly_one=require_exactly_one)
        dimacs = to_dimacs(cnf)
        start = perf_counter()
        status, seconds = solve_with_timeout(dimacs, args.solver, args.timeout)
        elapsed = seconds if status != "TIMEOUT" else perf_counter() - start
        print(
            f"{kind},{candidate},{len(reduced.vertices)},{len(reduced.edges)},"
            f"{cnf.variables},{len(cnf.clauses)},{status},{elapsed:.6f}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
