# Hadwiger-Nelson Research Plan

## Problem

The Hadwiger-Nelson problem asks for the chromatic number of the Euclidean plane unit-distance graph: the fewest colors needed so that any two points at distance 1 receive different colors.

As of the current research scan on 2026-06-18, the answer is still known to be one of 5, 6, or 7. The lower bound was raised from 4 to 5 by Aubrey de Grey in 2018 using a finite unit-distance graph that is not 4-colorable.

Primary starting sources:

- Aubrey D. N. J. de Grey, "The chromatic number of the plane is at least 5", arXiv:1804.02385.
- Polymath16 follow-up work on smaller non-4-colorable unit-distance graphs.
- Vsevolod Voronov, Anna Neopryatnaya, Eugene Dergachev, "Constructing 5-chromatic unit distance graphs embedded in the Euclidean plane and two-dimensional spheres", arXiv:2106.11824.

## Research Thesis

The most realistic path to a world-class breakthrough is not a direct analytic proof at first. It is a verified finite certificate:

- A finite unit-distance graph that is not 5-colorable would prove the plane needs at least 6 colors.
- A finite unit-distance graph that improves known 5-chromatic examples may still be publishable if it is smaller, cleaner, structurally novel, or easier to verify.

## Milestones

1. Baseline verification
   - Reproduce the Moser spindle as a 4-chromatic unit-distance graph.
   - Reproduce at least one known 5-chromatic construction from published data.
   - Store graph data and verification commands in a repeatable format.

2. Search infrastructure
   - Add DIMACS export for SAT solvers.
   - Add graph minimization by vertex deletion while preserving non-k-colorability.
   - Add candidate construction families based on spindle gluing, ring constraints, and symmetric motifs.

3. Breakthrough search
   - Search for smaller non-4-colorable graphs as a calibration task.
   - Search for graphs with unusually high fractional chromatic lower bounds.
   - Run non-5-colorability searches only after the verification pipeline is independently cross-checkable.

## Reproduced Reference Result

On 2026-06-18, this workbench reproduced the Heule 553-vertex non-4-colorability certificate from `marijnheule/CNP-SAT`:

- `553.edge`: 553 vertices and 2722 edges.
- cover CNF generated locally: 2212 variables and 11441 clauses.
- `553-4-sbp.cnf`: 2212 variables and 11444 clauses, adding 3 symmetry-breaking unit clauses.
- PySAT/CaDiCaL result on `553-4-sbp.cnf`: UNSAT in about 1.98 seconds.
- `drat-trim` result on `553-4-sbp.cnf` plus `553-4-sbp.drat`: VERIFIED in about 0.90 seconds.

## Verification Rules

- Every graph must have both an abstract edge list and a unit-distance embedding claim.
- Every negative coloring claim must be verified by at least two independent methods before being treated as serious.
- Any candidate breakthrough must produce:
  - graph data,
  - coordinates or an exact construction recipe,
  - non-colorability certificate,
  - independent reproducibility notes.

## Current State

Implemented and verified:

- Moser spindle graph.
- k-colorability backtracking verifier.
- DIMACS edge/CNF import and export.
- PySAT/CaDiCaL CNF solving.
- DRAT-trim proof verification.
- CNP-SAT `.vtx` coordinate parsing and unit-distance embedding checks.
- Proof-core reductions of the CNP-SAT 517, 529, and 553 vertex graphs.
- Exact (symbolic) unit-distance verification in `Q(sqrt 3, sqrt 5, sqrt 11)`
  for all four CNP-SAT graphs (`hnp/exact_embedding.py`).
- Incremental SAT criticality reducer with edge selectors + symmetry breaking
  (`hnp/minimize.py`).
- unit tests and CLI smoke checks.

Current publishable-unit candidate (Phase 5, honest framing):

- An open verification + deletion-minimization toolkit for the CNP-SAT family,
  with two genuine contributions over the prior art:
  - **Exact** (proof-grade, non-floating-point) unit-distance certificates for
    the 510/517/529/553 graphs.
  - A clean **deletion lower bound**: the 510 graph is vertex-critical, so no
    sequence of edge/vertex deletions can drop below 510 vertices; Parts'
    509-vertex record is therefore unreachable by deletion (proof in
    `lab-notes/2026-06-18-phase-5.md`).
- Best-effort edge-critical reductions of the 510 graph (510 vertices, fewer
  edges), independently re-verified UNSAT and exactly unit-distance.

Boundary:

- This does not improve the known plane lower bound from 5 to 6.
- This is not a record-size graph; 509 vertices is provably out of reach by
  deletion. Beating the record needs a new vertex set (construction/search),
  which deletion-based tooling cannot supply.
- Honest positioning: a reproducibility + exact-verification computational note,
  not a breakthrough.
