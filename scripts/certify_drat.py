#!/usr/bin/env python3
"""Generate and check a DRAT non-4-colorability certificate for an edge graph.

Builds the exactly-one coloring CNF, pins a triangle to three distinct colors
(color-symmetry breaking, keeping the instance cleanly UNSAT and the proof
small), solves with CaDiCaL emitting a DRAT proof, writes both the CNF and the
proof, and runs drat-trim to check the proof.

This adds a second, independent verification method on top of the plain CaDiCaL
UNSAT result: the SAT proof itself is mechanically checked.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hnp.dimacs import color_var, coloring_cnf, graph_from_dimacs_edge_text
from hnp.minimize import find_triangle
from pysat.solvers import Glucose4

DEFAULT_DRAT_TRIM = PROJECT_ROOT / "data/hadwiger-nelson/external/drat-trim/drat-trim"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edge", type=Path, required=True)
    parser.add_argument("--colors", type=int, default=4)
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--drat", type=Path, required=True)
    parser.add_argument("--drat-trim", type=Path, default=DEFAULT_DRAT_TRIM)
    args = parser.parse_args()

    graph = graph_from_dimacs_edge_text(args.edge.read_text(encoding="utf-8"))
    cnf = coloring_cnf(graph, args.colors)

    triangle = find_triangle(graph)
    if triangle is None:
        raise SystemExit("graph has no triangle for symmetry breaking")
    t0, t1, t2 = triangle
    pins = [
        (color_var(cnf.vertex_index, t0, 0, args.colors),),
        (color_var(cnf.vertex_index, t1, 1, args.colors),),
        (color_var(cnf.vertex_index, t2, 2, args.colors),),
    ]
    clauses = list(cnf.clauses) + pins

    # Glucose's DRUP proof logging (no inprocessing) is reliably drat-trim-checkable;
    # CaDiCaL via pysat sometimes returns an incomplete proof under preprocessing.
    solver = Glucose4(bootstrap_with=clauses, with_proof=True)
    satisfiable = solver.solve()
    proof = solver.get_proof()
    solver.delete()
    if satisfiable:
        raise SystemExit("graph is colorable; no UNSAT certificate to emit")

    header = [
        f"c {args.colors}-coloring of {args.edge.name}: "
        f"{len(graph.vertices)} vertices, {len(graph.edges)} edges",
        f"c symmetry-breaking pins: {t0}->0, {t1}->1, {t2}->2",
        f"p cnf {cnf.variables} {len(clauses)}",
    ]
    body = [" ".join(map(str, clause)) + " 0" for clause in clauses]
    args.cnf.write_text("\n".join(header + body) + "\n", encoding="utf-8")
    args.drat.write_text("\n".join(proof) + "\n", encoding="utf-8")

    print(f"vertices: {len(graph.vertices)}")
    print(f"edges: {len(graph.edges)}")
    print(f"clauses: {len(clauses)}")
    print(f"proof_lines: {len(proof)}")

    completed = subprocess.run(
        [str(args.drat_trim), str(args.cnf), str(args.drat)],
        capture_output=True, text=True, check=False,
    )
    verified = "s VERIFIED" in completed.stdout
    print(f"drat-trim: {'VERIFIED' if verified else 'NOT VERIFIED'}")
    if not verified:
        sys.stdout.write(completed.stdout[-1500:])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
