"""Deletion-based minimization of non-k-colorable unit-distance graphs.

The core idea is criticality reduction: starting from a graph that is *not*
k-colorable, greedily delete edges (and then low-degree vertices) as long as the
graph stays non-k-colorable.  Non-k-colorability is decided with an incremental
SAT solver.

Two ingredients make this fast enough to run on ~500-vertex graphs:

1. Color-symmetry breaking.  A fixed triangle has its three vertices pinned to
   three distinct colors via unit clauses.  This removes the ``k!`` color
   permutations and turns multi-second UNSAT proofs into sub-second ones.

2. Edge selector variables.  Every edge constraint carries a selector literal so
   a single incremental solver can test "is the graph still UNSAT if this set of
   edges is deleted?" purely through assumptions, reusing learned clauses across
   thousands of queries.

Geometry is preserved for free: every subgraph of a unit-distance graph is still
a unit-distance graph under the same coordinates, so only non-k-colorability has
to be re-checked.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter

from pysat.solvers import Solver

from hnp.graph import Edge, Graph, canonical_edge


def find_triangle(graph: Graph) -> tuple[str, str, str] | None:
    """Return three mutually adjacent vertices, or None if the graph is triangle-free."""

    adjacency = graph.adjacency()
    for a, b in sorted(graph.edges):
        common = adjacency[a] & adjacency[b]
        if common:
            c = min(common)
            return (a, b, c)
    return None


@dataclass
class ColorSelectorModel:
    """An incremental 4-coloring CNF with per-edge selector literals.

    Assumptions control which edges are "present".  For an active edge we assume
    its selector is False (the color-clash clauses are enforced); to delete an
    edge we assume its selector is True (the clauses become trivially satisfied).
    """

    graph: Graph
    colors: int
    vertex_index: dict[str, int]
    edge_selector: dict[Edge, int]
    sbp_triangle: tuple[str, str, str]
    solver_name: str = "cadical153"
    conflict_budget: int = 0  # 0 disables the budget (solve to completion)
    _solver: Solver = field(init=False, repr=False)
    solve_calls: int = field(default=0, init=False)
    solve_seconds: float = field(default=0.0, init=False)
    budget_exceeded: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self._solver = Solver(name=self.solver_name, bootstrap_with=self._clauses(), use_timer=True)

    # -- CNF construction -------------------------------------------------

    def _color_var(self, vertex: str, color: int) -> int:
        return self.vertex_index[vertex] * self.colors + color + 1

    def _clauses(self) -> list[tuple[int, ...]]:
        clauses: list[tuple[int, ...]] = []
        for vertex in self.graph.vertices:
            clauses.append(tuple(self._color_var(vertex, c) for c in range(self.colors)))
            for first in range(self.colors):
                for second in range(first + 1, self.colors):
                    clauses.append((-self._color_var(vertex, first), -self._color_var(vertex, second)))

        for edge in sorted(self.graph.edges):
            a, b = edge
            selector = self.edge_selector[edge]
            for color in range(self.colors):
                clauses.append((-self._color_var(a, color), -self._color_var(b, color), selector))

        # Symmetry breaking: pin the triangle to three distinct colors.
        t0, t1, t2 = self.sbp_triangle
        clauses.append((self._color_var(t0, 0),))
        clauses.append((self._color_var(t1, 1),))
        clauses.append((self._color_var(t2, 2),))
        return clauses

    # -- queries ----------------------------------------------------------

    def is_unsat_without(self, deleted: set[Edge]) -> bool | None:
        """Tri-state non-k-colorability test for the graph minus ``deleted``.

        Returns True if provably non-k-colorable (UNSAT), False if k-colorable
        (SAT), or None if the conflict budget was exhausted before either was
        proved.  None is treated conservatively by callers (do not delete).
        """

        assumptions = []
        for edge, selector in self.edge_selector.items():
            assumptions.append(selector if edge in deleted else -selector)
        start = perf_counter()
        if self.conflict_budget > 0:
            self._solver.conf_budget(self.conflict_budget)
            satisfiable = self._solver.solve_limited(assumptions=assumptions, expect_interrupt=False)
        else:
            satisfiable = self._solver.solve(assumptions=assumptions)
        self.solve_seconds += perf_counter() - start
        self.solve_calls += 1
        if satisfiable is None:
            self.budget_exceeded += 1
            return None
        return not satisfiable

    def delete_permanently(self, edge: Edge) -> None:
        """Commit an edge deletion as a unit clause so later solves need not assume it."""

        self._solver.add_clause((self.edge_selector[edge],))

    def close(self) -> None:
        self._solver.delete()


def build_model(
    graph: Graph,
    colors: int = 4,
    solver_name: str = "cadical153",
    conflict_budget: int = 0,
) -> ColorSelectorModel:
    triangle = find_triangle(graph)
    if triangle is None:
        raise ValueError("graph has no triangle; symmetry breaking needs one")
    vertex_index = {vertex: index for index, vertex in enumerate(graph.vertices)}
    base_vars = len(graph.vertices) * colors
    edge_selector: dict[Edge, int] = {}
    next_var = base_vars + 1
    for edge in sorted(graph.edges):
        edge_selector[edge] = next_var
        next_var += 1
    return ColorSelectorModel(
        graph=graph,
        colors=colors,
        vertex_index=vertex_index,
        edge_selector=edge_selector,
        sbp_triangle=triangle,
        solver_name=solver_name,
        conflict_budget=conflict_budget,
    )


@dataclass
class MinimizeResult:
    removed_edges: list[Edge]
    kept_edges: frozenset[Edge]
    order: str
    solve_calls: int
    solve_seconds: float
    budget_exceeded: int = 0


def edge_minimize(
    graph: Graph,
    colors: int = 4,
    order: str = "high-degree-first",
    protect: set[Edge] | None = None,
    conflict_budget: int = 0,
    progress=None,
) -> MinimizeResult:
    """Greedily delete edges while the graph stays non-k-colorable.

    An edge is removed only when its removal is *proved* to keep the graph
    non-k-colorable within the conflict budget.  Edges whose test is SAT
    (essential) or budget-exhausted (unknown) are kept, so the returned subgraph
    is always still non-k-colorable.
    """

    protect = set(protect or set())
    model = build_model(graph, colors=colors, conflict_budget=conflict_budget)
    # The symmetry-breaking triangle edges must stay so the pinning clauses remain valid.
    t0, t1, t2 = model.sbp_triangle
    for a, b in ((t0, t1), (t0, t2), (t1, t2)):
        protect.add(canonical_edge(a, b))

    degrees = graph.degrees()

    def edge_key(edge: Edge) -> tuple:
        a, b = edge
        if order == "high-degree-first":
            return (-(degrees[a] + degrees[b]), a, b)
        if order == "low-degree-first":
            return (degrees[a] + degrees[b], a, b)
        return (a, b)

    candidates = sorted((e for e in graph.edges if e not in protect), key=edge_key)

    deleted: set[Edge] = set()
    removed_order: list[Edge] = []
    for index, edge in enumerate(candidates):
        if model.is_unsat_without(deleted | {edge}) is True:
            deleted.add(edge)
            removed_order.append(edge)
            model.delete_permanently(edge)
        if progress is not None:
            progress(index + 1, len(candidates), len(deleted), model)

    kept = frozenset(e for e in graph.edges if e not in deleted)
    result = MinimizeResult(
        removed_edges=removed_order,
        kept_edges=kept,
        order=order,
        solve_calls=model.solve_calls,
        solve_seconds=model.solve_seconds,
        budget_exceeded=model.budget_exceeded,
    )
    model.close()
    return result


def prune_low_degree_vertices(graph: Graph) -> tuple[Graph, list[str]]:
    """Iteratively drop vertices of degree <= 1.

    For k >= 2 colors, a vertex of degree <= 1 can always be colored last, so its
    removal preserves non-k-colorability.  Returns the pruned graph and the list
    of removed vertices.
    """

    current = graph
    removed: list[str] = []
    while True:
        degrees = current.degrees()
        low = [v for v, d in degrees.items() if d <= 1]
        if not low:
            break
        removed.extend(low)
        current = current.without_vertices(low)
    return current, removed
