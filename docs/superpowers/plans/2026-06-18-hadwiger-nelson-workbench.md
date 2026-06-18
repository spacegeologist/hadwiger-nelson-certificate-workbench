# Hadwiger-Nelson Research Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first local verification workbench for finite unit-distance graph coloring experiments.

**Architecture:** Use a small pure-Python core for abstract graph representation, exact search for k-colorability, and approximate coordinate checks for known geometric embeddings. Keep research notes, graph data, scripts, and tests separate so the workspace can grow into literature reproduction and candidate search.

**Tech Stack:** Python standard library, JSON graph data, unittest.

---

### Task 1: Research Skeleton

**Files:**
- Create: `README.md`
- Create: `docs/hadwiger-nelson/research-plan.md`
- Create: `docs/superpowers/plans/2026-06-18-hadwiger-nelson-workbench.md`

- [x] Create a concise top-level README with the problem target and baseline commands.
- [x] Create a research plan documenting sources, milestones, and first search directions.
- [x] Record this implementation plan in the superpowers plan directory.

### Task 2: Graph and Coloring Core

**Files:**
- Create: `hnp/__init__.py`
- Create: `hnp/graph.py`
- Create: `hnp/coloring.py`

- [x] Add a minimal immutable graph model with vertex and edge validation.
- [x] Add a backtracking k-colorability search with color-symmetry pruning.
- [x] Add a helper for checking that a returned coloring is proper.

### Task 3: Geometry and Baseline Example

**Files:**
- Create: `hnp/embedding.py`
- Create: `hnp/examples.py`
- Create: `data/hadwiger-nelson/moser_spindle.json`

- [x] Add coordinate checks for claimed unit-distance embeddings.
- [x] Encode the Moser spindle as an abstract graph.
- [x] Store a JSON copy of the Moser spindle with approximate coordinates.

### Task 4: Verification Entry Points

**Files:**
- Create: `scripts/verify_graph.py`
- Create: `tests/test_moser_spindle.py`

- [x] Add a command line script for checking k-colorability of an example or JSON graph.
- [x] Add tests proving the Moser spindle baseline is not 3-colorable and is 4-colorable.
- [x] Run the test suite and CLI smoke checks.
