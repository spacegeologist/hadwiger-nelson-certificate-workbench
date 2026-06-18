#!/usr/bin/env python3
from __future__ import annotations

import argparse
import multiprocessing as mp
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hnp.sat import SatResult, solve_dimacs_cnf_text


def solve_worker(path: str, solver_name: str, queue: mp.Queue) -> None:
    try:
        text = Path(path).read_text(encoding="utf-8")
        result = solve_dimacs_cnf_text(text, solver_name=solver_name)
        queue.put(("ok", result))
    except Exception as error:  # pragma: no cover - surfaced through CLI stderr
        queue.put(("error", repr(error)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Solve a DIMACS CNF file with PySAT.")
    parser.add_argument("cnf", type=Path, help="path to DIMACS CNF file")
    parser.add_argument("--solver", default="cadical153", help="PySAT solver name")
    parser.add_argument("--timeout", type=float, default=30.0, help="seconds before terminating the solver")
    return parser.parse_args()


def print_result(result: SatResult) -> None:
    print(f"variables: {result.variables}")
    print(f"clauses: {result.clauses}")
    print(f"seconds: {result.seconds:.6f}")
    print(f"result: {'SAT' if result.satisfiable else 'UNSAT'}")


def main() -> int:
    args = parse_args()
    queue: mp.Queue = mp.Queue()
    process = mp.Process(target=solve_worker, args=(str(args.cnf), args.solver, queue))
    process.start()
    process.join(args.timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        print(f"result: TIMEOUT after {args.timeout:g}s")
        return 124

    if queue.empty():
        print("solver exited without returning a result", file=sys.stderr)
        return 1

    status, payload = queue.get()
    if status == "error":
        print(payload, file=sys.stderr)
        return 1

    print_result(payload)
    return 10 if payload.satisfiable else 20


if __name__ == "__main__":
    raise SystemExit(main())
