# Hadwiger-Nelson Research Workbench

This workspace is for a serious attack on the Hadwiger-Nelson problem through finite unit-distance graphs.

Current target:

1. Reproduce known finite graph/coloring baselines.
2. Build reliable verification tools.
3. Search for structured candidate graphs that may improve known bounds.

The long-shot breakthrough target is a finite unit-distance graph that is not 5-colorable, which would raise the lower bound for the chromatic number of the plane from 5 to 6.

## First Baseline

The first implemented baseline is the Moser spindle:

- 7 vertices
- 11 unit edges
- not 3-colorable
- 4-colorable

Run:

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 scripts/verify_graph.py --example moser --colors 3
python3 scripts/verify_graph.py --example moser --colors 4
```

## Proof Checker Setup

DRAT proof verification needs `drat-trim`. It is not vendored in this repository.
To reproduce the local path used below:

```bash
git clone https://github.com/marijnheule/drat-trim.git \
  data/hadwiger-nelson/external/drat-trim
make -C data/hadwiger-nelson/external/drat-trim
```

If you already have a `drat-trim` binary, substitute that path in the commands.

## One-Command Verification

After installing dependencies and building `drat-trim`, run:

```bash
python3 scripts/check_sbp_closed.py
```

This runs:

- the Python unit test suite,
- all three SBP-closed unit-distance embedding checks,
- all three SBP-closed DRAT certificate checks.

Preview the exact commands without running them:

```bash
python3 scripts/check_sbp_closed.py --dry-run
```

Key artifact checksums are in
`data/hadwiger-nelson/generated/sbp-closed/SHA256SUMS`.

## 553-Vertex Reproduction

The workspace now reproduces Marijn Heule's 553-vertex 5-chromatic unit-distance graph certificate from `marijnheule/CNP-SAT`.

Downloaded inputs:

- `data/hadwiger-nelson/external/marijnheule-CNP-SAT/edge/553.edge`
- `data/hadwiger-nelson/external/marijnheule-CNP-SAT/cnf/553-4-sbp.cnf`
- `data/hadwiger-nelson/external/marijnheule-CNP-SAT/proof/553-4-sbp.drat`

Rebuild the 4-color cover CNF from the edge file:

```bash
python3 scripts/verify_graph.py \
  --edge data/hadwiger-nelson/external/marijnheule-CNP-SAT/edge/553.edge \
  --colors 4 \
  --encoding cover \
  --dimacs data/hadwiger-nelson/generated/553-4-cover.cnf
```

Solve the symmetry-broken 553 CNF:

```bash
python3 scripts/solve_cnf.py \
  data/hadwiger-nelson/external/marijnheule-CNP-SAT/cnf/553-4-sbp.cnf \
  --solver cadical153 \
  --timeout 20
```

Expected: `result: UNSAT`.

Check the DRAT proof:

```bash
data/hadwiger-nelson/external/drat-trim/drat-trim \
  data/hadwiger-nelson/external/marijnheule-CNP-SAT/cnf/553-4-sbp.cnf \
  data/hadwiger-nelson/external/marijnheule-CNP-SAT/proof/553-4-sbp.drat
```

Expected: `s VERIFIED`.

## Criticality Probes

Probe vertex deletion on the 517-vertex graph:

```bash
python3 scripts/probe_deletions.py \
  --edge data/hadwiger-nelson/external/marijnheule-CNP-SAT/edge/517.edge \
  --colors 4 \
  --kind vertices \
  --limit 5 \
  --timeout 5
```

Probe edge deletion on the 517-vertex graph:

```bash
python3 scripts/probe_deletions.py \
  --edge data/hadwiger-nelson/external/marijnheule-CNP-SAT/edge/517.edge \
  --colors 4 \
  --kind edges \
  --limit 10 \
  --timeout 5
```

The current lesson: vertex deletions are SAT and fast enough to scan; edge deletions need proof-guided tooling.

## Proof-Core Reductions

The current strongest local artifacts are proof-core reductions of the CNP-SAT
517, 529, and 553 vertex graphs.  The reductions keep the symmetry-breaking
triangle on vertices `1,2,6`, so the SBP unit clauses `1 0`, `6 0`, and `23 0`
remain a valid color-symmetry normalization.

| graph | original edges | SBP-closed reduced edges | removed edges | DRAT check | embedding check |
| --- | ---: | ---: | ---: | --- | --- |
| 517 | 2579 | 2576 | 3 | VERIFIED | all unit |
| 529 | 2670 | 2662 | 8 | VERIFIED | all unit |
| 553 | 2722 | 2715 | 7 | VERIFIED | all unit |

Rebuild one reduced artifact:

```bash
python3 scripts/reduce_by_core.py \
  --edge data/hadwiger-nelson/external/marijnheule-CNP-SAT/edge/553.edge \
  --core data/hadwiger-nelson/generated/cores/553-core-r2.core \
  --cnf data/hadwiger-nelson/external/marijnheule-CNP-SAT/cnf/553-4-sbp.cnf \
  --colors 4 \
  --preserve-edge 1:2 \
  --preserve-edge 1:6 \
  --preserve-edge 2:6 \
  --output-edge data/hadwiger-nelson/generated/sbp-closed/553-sbp-closed.edge \
  --output-cnf data/hadwiger-nelson/generated/sbp-closed/553-sbp-closed.cnf
```

Verify the certificate:

```bash
data/hadwiger-nelson/external/drat-trim/drat-trim \
  data/hadwiger-nelson/generated/sbp-closed/553-sbp-closed.cnf \
  data/hadwiger-nelson/external/marijnheule-CNP-SAT/proof/553-4-sbp.drat
```

Verify the geometry:

```bash
python3 scripts/verify_embedding.py \
  --edge data/hadwiger-nelson/generated/sbp-closed/553-sbp-closed.edge \
  --vtx data/hadwiger-nelson/external/marijnheule-CNP-SAT/vtx/553.vtx
```
