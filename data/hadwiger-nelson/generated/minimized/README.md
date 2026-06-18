# Minimized artifacts

Deletion-minimized non-4-colorable unit-distance graphs produced by
`scripts/minimize_graph.py`.

## 510-min

- `510-min.edge` — 510 vertices, 2287 edges (217 redundant edges deleted from the
  CNP-SAT 510 graph), proved non-4-colorable.
- `510-min.report.json` — full run report, including an independent UNSAT
  re-check on a fresh CaDiCaL (no symmetry breaking) and exact-geometry result.
- `510-vertex-critical.txt` — exhaustive vertex-criticality check of the input
  510 graph (all 510 single-vertex deletions are 4-colorable).

Coordinates: the vertex set is unchanged from the original graph (0 vertices
pruned), so the exact coordinates in
`../../external/marijnheule-CNP-SAT/vtx/510.vtx` apply directly. Verify with:

```bash
python3 scripts/verify_embedding_exact.py \
  --edge data/hadwiger-nelson/generated/minimized/510-min.edge \
  --vtx  data/hadwiger-nelson/external/marijnheule-CNP-SAT/vtx/510.vtx
```

This is **not** a record graph: Parts (2020) has 509 vertices / 2442 edges. The
510 graph is vertex-critical, so deletion cannot beat 509 vertices. See
`docs/hadwiger-nelson/lab-notes/2026-06-18-phase-5.md`.
