from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from pysat.solvers import Solver

Clause = tuple[int, ...]


@dataclass(frozen=True)
class DimacsCnf:
    variables: int
    clauses: list[Clause]


@dataclass(frozen=True)
class SatResult:
    satisfiable: bool
    variables: int
    clauses: int
    seconds: float


def parse_dimacs_cnf_text(text: str) -> DimacsCnf:
    variables: int | None = None
    expected_clauses: int | None = None
    clauses: list[Clause] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("c"):
            continue

        parts = line.split()
        if parts[0] == "p":
            if len(parts) != 4 or parts[1] != "cnf":
                raise ValueError(f"line {line_number}: expected 'p cnf <variables> <clauses>'")
            variables = int(parts[2])
            expected_clauses = int(parts[3])
            continue

        literals = [int(part) for part in parts]
        if not literals or literals[-1] != 0:
            raise ValueError(f"line {line_number}: DIMACS clause must end with 0")
        clause = tuple(literal for literal in literals[:-1] if literal != 0)
        clauses.append(clause)

    if variables is None or expected_clauses is None:
        raise ValueError("missing DIMACS CNF header")
    if len(clauses) != expected_clauses:
        raise ValueError(f"clause count mismatch: header says {expected_clauses}, found {len(clauses)}")

    return DimacsCnf(variables=variables, clauses=clauses)


def solve_dimacs_cnf_text(text: str, solver_name: str = "glucose3") -> SatResult:
    formula = parse_dimacs_cnf_text(text)
    start = perf_counter()
    with Solver(name=solver_name, bootstrap_with=formula.clauses) as solver:
        satisfiable = solver.solve()
    elapsed = perf_counter() - start
    return SatResult(
        satisfiable=satisfiable,
        variables=formula.variables,
        clauses=len(formula.clauses),
        seconds=elapsed,
    )
