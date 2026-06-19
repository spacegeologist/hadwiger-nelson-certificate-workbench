#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hnp.dimacs import graph_from_dimacs_edge_text
from hnp.graph import Edge, canonical_edge
from hnp.sat import parse_dimacs_cnf_text
from reduce_by_core import filter_cnf_by_edges, parse_edge_spec, render_cnf

CSV_FIELDS = ("edge", "status", "seconds", "clauses", "returncode")


def edge_label(edge: Edge) -> str:
    return f"{edge[0]}:{edge[1]}"


def edge_sort_key(edge: Edge) -> tuple[int, int] | tuple[str, str]:
    try:
        return int(edge[0]), int(edge[1])
    except ValueError:
        return edge


def read_done_edges(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()

    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["edge"] for row in csv.DictReader(handle) if row.get("edge")}


def classify_checker_output(returncode: int, output: str) -> str:
    if "s VERIFIED" in output:
        return "VERIFIED"
    if "s NOT VERIFIED" in output:
        return "NOT_VERIFIED"
    if returncode != 0:
        return "ERROR"
    return "UNKNOWN"


def append_row(path: Path | None, row: dict[str, object]) -> None:
    if path is None:
        print(",".join(str(row[field]) for field in CSV_FIELDS), flush=True)
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Try one-edge deletions and check whether the existing DRAT proof still verifies."
    )
    parser.add_argument("--edge", type=Path, required=True, help="source DIMACS edge graph")
    parser.add_argument("--cnf", type=Path, required=True, help="source CNF")
    parser.add_argument("--proof", type=Path, required=True, help="DRAT proof to reuse")
    parser.add_argument("--colors", type=int, required=True, help="color count used by the CNF")
    parser.add_argument(
        "--drat-trim",
        type=Path,
        default=Path("data/hadwiger-nelson/external/drat-trim/drat-trim"),
        help="path to the drat-trim binary",
    )
    parser.add_argument(
        "--preserve-edge",
        action="append",
        type=parse_edge_spec,
        default=[],
        help="edge to skip, written as A:B; repeatable",
    )
    parser.add_argument("--output", type=Path, help="append CSV scan results to this file")
    parser.add_argument("--limit", type=int, help="maximum number of new candidate edges to check")
    parser.add_argument("--per-check-timeout", type=float, default=30.0, help="seconds per DRAT check")
    parser.add_argument("--stop-after-seconds", type=float, help="total wall-clock time budget")
    parser.add_argument("--dry-run", action="store_true", help="print candidate edges without checking them")
    parser.add_argument("--overwrite", action="store_true", help="ignore existing output rows")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    graph = graph_from_dimacs_edge_text(args.edge.read_text(encoding="utf-8"))
    cnf = parse_dimacs_cnf_text(args.cnf.read_text(encoding="utf-8"))

    preserved_edges = {canonical_edge(a, b) for a, b in args.preserve_edge}
    unknown_preserved_edges = preserved_edges.difference(graph.edges)
    if unknown_preserved_edges:
        raise ValueError(f"cannot preserve unknown edges: {sorted(unknown_preserved_edges)}")

    done_edges = set() if args.overwrite else read_done_edges(args.output)
    candidates = [
        edge
        for edge in sorted(graph.edges.difference(preserved_edges), key=edge_sort_key)
        if edge_label(edge) not in done_edges
    ]

    if args.dry_run:
        print(f"candidates: {len(candidates)}")
        for edge in candidates:
            print(edge_label(edge))
        return 0

    if not args.drat_trim.exists():
        print(f"missing drat-trim binary: {args.drat_trim}", file=sys.stderr)
        return 1

    started_at = time.monotonic()
    checked = 0
    with tempfile.TemporaryDirectory(prefix="edge-proof-reuse-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        for edge in candidates:
            if args.limit is not None and checked >= args.limit:
                break
            if args.stop_after_seconds is not None and time.monotonic() - started_at >= args.stop_after_seconds:
                break

            retained_edges = set(graph.edges)
            retained_edges.remove(edge)
            filtered_clauses = filter_cnf_by_edges(graph, cnf, args.colors, retained_edges)
            temporary_cnf = temporary_root / f"without-{edge[0]}-{edge[1]}.cnf"
            temporary_cnf.write_text(render_cnf(cnf.variables, filtered_clauses), encoding="utf-8")

            check_started_at = time.monotonic()
            try:
                result = subprocess.run(
                    [str(args.drat_trim), str(temporary_cnf), str(args.proof)],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=args.per_check_timeout,
                )
                seconds = time.monotonic() - check_started_at
                combined_output = result.stdout + result.stderr
                status = classify_checker_output(result.returncode, combined_output)
                returncode: int | str = result.returncode
            except subprocess.TimeoutExpired:
                seconds = time.monotonic() - check_started_at
                status = "TIMEOUT"
                returncode = "timeout"

            row = {
                "edge": edge_label(edge),
                "status": status,
                "seconds": f"{seconds:.6f}",
                "clauses": len(filtered_clauses),
                "returncode": returncode,
            }
            append_row(args.output, row)
            checked += 1

    print(f"checked: {checked}")
    print(f"remaining: {max(0, len(candidates) - checked)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
