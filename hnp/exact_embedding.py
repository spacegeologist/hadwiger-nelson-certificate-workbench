"""Exact (symbolic) unit-distance verification for CNP-SAT .vtx embeddings.

The floating-point checker in :mod:`hnp.embedding` accepts an edge as unit length
when ``|dist - 1| < tol``.  That is a numerical sanity check, not a proof.  Here
we parse each coordinate as an exact element of an algebraic number field
``Q(sqrt(3), sqrt(5), sqrt(11), ...)`` using sympy and verify that the squared
edge length equals exactly ``1`` by symbolic simplification.  An edge passes only
when ``(dx**2 + dy**2 - 1)`` reduces identically to zero.
"""

from __future__ import annotations

import sympy

from hnp.graph import Graph


def parse_mathematica_exact(expression: str) -> sympy.Expr:
    """Parse a CNP-SAT Mathematica-style coordinate expression to an exact sympy value."""

    python_expr = expression.strip().replace("Sqrt[", "sqrt(").replace("]", ")").replace("^", "**")
    # sympify with rational=True keeps 1/2 etc. exact, and maps sqrt -> sympy.sqrt.
    return sympy.sympify(python_expr, locals={"sqrt": sympy.sqrt}, rational=True)


def parse_vtx_exact(text: str) -> dict[str, tuple[sympy.Expr, sympy.Expr]]:
    coordinates: dict[str, tuple[sympy.Expr, sympy.Expr]] = {}
    index = 1
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if not (line.startswith("{") and line.endswith("}")):
            raise ValueError(f"vertex {index}: expected '{{x, y}}', got {line!r}")
        body = line[1:-1]
        depth = 0
        split_at = None
        for i, ch in enumerate(body):
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
            elif ch == "," and depth == 0:
                split_at = i
                break
        if split_at is None:
            raise ValueError(f"vertex {index}: could not split coordinate pair")
        x = parse_mathematica_exact(body[:split_at])
        y = parse_mathematica_exact(body[split_at + 1 :])
        coordinates[str(index)] = (x, y)
        index += 1
    return coordinates


def exact_non_unit_edges(
    graph: Graph,
    coordinates: dict[str, tuple[sympy.Expr, sympy.Expr]],
) -> list[tuple[str, str]]:
    """Return edges whose exact squared length is not identically 1."""

    missing = [v for v in graph.vertices if v not in coordinates]
    if missing:
        raise ValueError(f"missing coordinates for vertices: {missing[:5]}")

    bad: list[tuple[str, str]] = []
    for a, b in sorted(graph.edges):
        ax, ay = coordinates[a]
        bx, by = coordinates[b]
        residual = sympy.expand((ax - bx) ** 2 + (ay - by) ** 2 - 1)
        if residual != 0:
            # expand collapses sqrt(p)*sqrt(p) -> p and sqrt(p)*sqrt(q) -> sqrt(pq);
            # fall back to a stronger simplification before declaring failure.
            if sympy.simplify(residual) != 0:
                bad.append((a, b))
    return bad
