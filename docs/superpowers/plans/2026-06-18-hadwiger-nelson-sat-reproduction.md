# Hadwiger-Nelson SAT Reproduction Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add SAT-export infrastructure and begin importing known 5-chromatic graph sources for reproduction.

**Architecture:** Keep the internal verifier as a pure-Python sanity check, and add a separate DIMACS CNF encoder for standard SAT tooling. Treat literature/data discovery as research evidence and record source status in lab notes rather than baking unverified data into the code.

**Tech Stack:** Python standard library, JSON graph data, DIMACS CNF, unittest.

---

### Task 1: DIMACS Encoder

**Files:**
- Create: `hnp/dimacs.py`
- Modify: `hnp/__init__.py`
- Test: `tests/test_dimacs.py`

- [ ] Add tests for variable numbering, clause count, and DIMACS rendering on a single-edge graph.
- [ ] Implement `color_var`, `coloring_cnf`, and `to_dimacs`.
- [ ] Export the DIMACS helpers from the package.
- [ ] Run the DIMACS test file.

### Task 2: CLI Export

**Files:**
- Modify: `scripts/verify_graph.py`
- Modify: `tests/test_verify_graph_cli.py`

- [ ] Add a CLI test for writing a DIMACS file from the Moser spindle.
- [ ] Add `--dimacs PATH` support to the existing script.
- [ ] Preserve existing colorability behavior when `--dimacs` is absent.
- [ ] Run CLI tests and full test suite.

### Task 3: Known Graph Source Investigation

**Files:**
- Modify: `docs/hadwiger-nelson/research-plan.md`
- Create: `docs/hadwiger-nelson/lab-notes/2026-06-18-phase-2.md`

- [ ] Check primary sources for de Grey/Polymath16 graph data.
- [ ] Record confirmed source links and whether graph data is directly downloadable.
- [ ] Avoid importing any dataset until provenance and format are clear.
