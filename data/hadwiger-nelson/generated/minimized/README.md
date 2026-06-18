# Minimized artifacts

Deletion-minimized non-4-colorable unit-distance graphs produced by
`scripts/minimize_graph.py` (lexicographic edge order, per-solve conflict budget
8000). Edges are removed only when removal is *proved* to keep the graph
non-4-colorable, so every output is still non-4-colorable by construction.

## Results (all triple-verified)

| graph | input | reduced | edges removed | indep. UNSAT | DRAT | exact geometry |
| --- | --- | --- | ---: | --- | --- | --- |
| 510-min | 510 v / 2504 e | 510 v / **2287 e** | 217 | UNSAT | VERIFIED | all unit |
| 517-min | 517 v / 2579 e | 517 v / **2335 e** | 244 | UNSAT | VERIFIED | all unit |
| 529-min | 529 v / 2670 e | 529 v / **2388 e** | 282 | UNSAT | VERIFIED | all unit |
| 553-min | 553 v / 2722 e | 553 v / **2484 e** | 238 | UNSAT | VERIFIED | all unit |

Three independent verifications per graph:
- **indep. UNSAT** — a fresh CaDiCaL solve of the plain CNF (no symmetry
  breaking, no selectors), recorded in `<graph>-min.report.json`.
- **DRAT** — `scripts/certify_drat.py` proof checked by drat-trim; summary in
  `drat/<graph>-min.cert.json` (the proof file itself is git-ignored and
  regenerable).
- **exact geometry** — `scripts/verify_embedding_exact.py` proves every surviving
  edge has squared length identically 1.

`510-vertex-critical.txt` records the exhaustive vertex-criticality check of the
input 510 graph (all 510 single-vertex deletions are 4-colorable).

Vertices are unchanged (0 pruned in every case — the inputs are vertex-critical),
so the original `../../external/marijnheule-CNP-SAT/vtx/<n>.vtx` coordinates apply
directly:

```bash
python3 scripts/verify_embedding_exact.py \
  --edge data/hadwiger-nelson/generated/minimized/510-min.edge \
  --vtx  data/hadwiger-nelson/external/marijnheule-CNP-SAT/vtx/510.vtx
```

## Scope (honest)

These are **not** record graphs. The smallest known 5-chromatic unit-distance
graph in the plane is Parts (2020): 509 vertices / 2442 edges. Each CNP-SAT graph
here is vertex-critical, so deletion cannot drop below its vertex count and
cannot reach 509 vertices (proof in
`docs/hadwiger-nelson/lab-notes/2026-06-18-phase-5.md`). The edge counts are
honest upper bounds for these specific vertex sets, not minima — the
`budget-exceeded` edges in each report could be removed with more solver effort.
