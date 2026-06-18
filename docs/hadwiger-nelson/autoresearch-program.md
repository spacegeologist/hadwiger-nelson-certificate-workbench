# Hadwiger-Nelson Autoresearch Program

## Purpose

This file adapts the `karpathy/autoresearch` style to finite unit-distance graph
research: keep the environment fixed, mutate only small experiment scripts or
candidate graph choices, measure against stable objectives, and preserve every
accepted and rejected result.

## Fixed Environment

- Source data: `marijnheule/CNP-SAT` edge, CNF, proof, and `.vtx` files.
- Solver path: `scripts/solve_cnf.py` with PySAT/CaDiCaL.
- Proof checker: `data/hadwiger-nelson/external/drat-trim/drat-trim`.
- Geometry checker: `scripts/verify_embedding.py`.
- Core reducer: `scripts/reduce_by_core.py`.

## Objective Ladder

1. Certificate validity
   - DRAT must return `s VERIFIED`.
   - Geometry checker must return `result: all edges are unit distance`.

2. Graph reduction
   - Primary metric: fewer edges while preserving non-4-colorability.
   - Secondary metric: fewer vertices, but only when vertex deletion remains UNSAT.

3. Search value
   - Prefer reductions that keep a simple SBP support explanation.
   - Prefer artifacts whose CNF can be solved in under 20 seconds locally.
   - Reject changes that require undocumented assumptions.

## Current Best Local Artifacts

| artifact | vertices | edges | clauses | SAT solver | DRAT | geometry |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `517-sbp-closed` | 517 | 2576 | 13923 | UNSAT, 2.388952s | VERIFIED, 2.147s | all unit |
| `529-sbp-closed` | 529 | 2662 | 11177 | UNSAT, 2.385371s | VERIFIED, 2.917s | all unit |
| `553-sbp-closed` | 553 | 2715 | 11416 | UNSAT, 1.770220s | VERIFIED, 0.964s | all unit |

## Acceptance Rule

An experiment is accepted into `generated/sbp-closed` only if all are true:

- The graph keeps edges `1:2`, `1:6`, and `2:6`.
- The filtered CNF keeps the SBP unit clauses for vertices `1`, `2`, and `6`.
- The matching DRAT proof verifies.
- The edge file passes `.vtx` unit-distance verification.
- The result removes at least one original edge or gives a clear diagnostic.

## Next Experiments

1. Vertex deletion with proof repair:
   - Try removing one vertex from `517-sbp-closed`.
   - Rebuild a cover/SBP CNF.
   - Use SAT first; if timeout, attempt proof/core reuse.

2. Edge-minimality scan:
   - For every non-SBP-support edge in `517-sbp-closed`, remove it.
   - Generate the filtered CNF and test whether the original proof still verifies.
   - If proof fails but SAT is UNSAT, attempt to produce a new proof.

3. Literature novelty check:
   - Compare against Jaan Parts' 509-vertex, 2442-edge graph.
   - Decide whether our contribution is a methods note, a dataset note, or only
     internal research infrastructure.
