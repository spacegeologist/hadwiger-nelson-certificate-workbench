# Hadwiger-Nelson Critical Probe Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand known-certificate reproduction to smaller CNP-SAT graphs and add first local deletion-probe tooling.

**Architecture:** Keep certificate reproduction data-driven: external graph/CNF/proof files live under `data/hadwiger-nelson/external`, while scripts and Python helpers provide repeatable local checks. Deletion probes should operate on abstract DIMACS edge graphs and produce CSV-like text outputs that can be inspected before any search automation grows.

**Tech Stack:** Python standard library, PySAT, DRAT-trim, DIMACS edge/CNF/DRAT files, unittest.

---

### Task 1: Reproduce 529/517 Certificates

**Files:**
- Download: `data/hadwiger-nelson/external/marijnheule-CNP-SAT/edge/529.edge`
- Download: `data/hadwiger-nelson/external/marijnheule-CNP-SAT/edge/517.edge`
- Download: `data/hadwiger-nelson/external/marijnheule-CNP-SAT/cnf/529-4.cnf`
- Download: `data/hadwiger-nelson/external/marijnheule-CNP-SAT/cnf/517-4.cnf`
- Download: `data/hadwiger-nelson/external/marijnheule-CNP-SAT/cnf/517-4-sbp.cnf`
- Download: `data/hadwiger-nelson/external/marijnheule-CNP-SAT/proof/529-4-sbp.drat`
- Download: `data/hadwiger-nelson/external/marijnheule-CNP-SAT/proof/517-4-sbp.drat`

- [ ] Confirm available edge/CNF/proof file names through GitHub API directory listings.
- [ ] Download the smallest known available graph certificates.
- [ ] Run PySAT on SBP CNFs where available.
- [ ] Run `drat-trim` proof checks where matching CNF/proof pairs exist.

### Task 2: Graph Deletion Utilities

**Files:**
- Modify: `hnp/graph.py`
- Test: `tests/test_graph.py`

- [ ] Add failing tests for removing one vertex and one edge.
- [ ] Implement `without_vertices` and `without_edges`.
- [ ] Preserve original vertex ordering and canonical edge validation.

### Task 3: Probe Script

**Files:**
- Create: `scripts/probe_deletions.py`
- Test: `tests/test_probe_deletions_cli.py`

- [ ] Add a CLI test that probes vertex deletion on the Moser spindle.
- [ ] Implement bounded vertex/edge deletion probes.
- [ ] Output one line per deletion candidate with SAT/UNSAT/TIMEOUT status.

### Task 4: Research Log

**Files:**
- Create: `docs/hadwiger-nelson/lab-notes/2026-06-18-phase-3.md`
- Modify: `README.md`

- [ ] Record reproduction results.
- [ ] Record first deletion probe observations.
- [ ] Add concise commands to README.
