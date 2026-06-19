#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ArtifactSet:
    label: str
    edge: str
    vtx: str
    cnf: str
    proof: str


ARTIFACTS = (
    ArtifactSet(
        label="517",
        edge="data/hadwiger-nelson/generated/sbp-closed/517-sbp-closed.edge",
        vtx="data/hadwiger-nelson/external/marijnheule-CNP-SAT/vtx/517.vtx",
        cnf="data/hadwiger-nelson/generated/sbp-closed/517-sbp-closed.cnf",
        proof="data/hadwiger-nelson/external/marijnheule-CNP-SAT/proof/517-4-sbp.drat",
    ),
    ArtifactSet(
        label="529",
        edge="data/hadwiger-nelson/generated/sbp-closed/529-sbp-closed.edge",
        vtx="data/hadwiger-nelson/external/marijnheule-CNP-SAT/vtx/529.vtx",
        cnf="data/hadwiger-nelson/generated/sbp-closed/529-sbp-closed.cnf",
        proof="data/hadwiger-nelson/external/marijnheule-CNP-SAT/proof/529-4-sbp.drat",
    ),
    ArtifactSet(
        label="553",
        edge="data/hadwiger-nelson/generated/sbp-closed/553-sbp-closed.edge",
        vtx="data/hadwiger-nelson/external/marijnheule-CNP-SAT/vtx/553.vtx",
        cnf="data/hadwiger-nelson/generated/sbp-closed/553-sbp-closed.cnf",
        proof="data/hadwiger-nelson/external/marijnheule-CNP-SAT/proof/553-4-sbp.drat",
    ),
)


def build_commands(args: argparse.Namespace) -> list[tuple[str, list[str]]]:
    commands: list[tuple[str, list[str]]] = []
    if not args.skip_unit_tests:
        commands.append(("unit tests", ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"]))

    if not args.skip_embedding:
        for artifact in ARTIFACTS:
            commands.append(
                (
                    f"{artifact.label} embedding",
                    [
                        "python3",
                        "scripts/verify_embedding.py",
                        "--edge",
                        artifact.edge,
                        "--vtx",
                        artifact.vtx,
                    ],
                )
            )

    if not args.skip_drat:
        for artifact in ARTIFACTS:
            commands.append(
                (
                    f"{artifact.label} DRAT",
                    [
                        str(args.drat_trim),
                        artifact.cnf,
                        artifact.proof,
                    ],
                )
            )

    return commands


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SBP-closed certificate reproducibility checks.")
    parser.add_argument(
        "--drat-trim",
        type=Path,
        default=Path("data/hadwiger-nelson/external/drat-trim/drat-trim"),
        help="path to the drat-trim binary",
    )
    parser.add_argument("--dry-run", action="store_true", help="print commands without running them")
    parser.add_argument("--skip-unit-tests", action="store_true", help="do not run the Python unit tests")
    parser.add_argument("--skip-embedding", action="store_true", help="do not run unit-distance embedding checks")
    parser.add_argument("--skip-drat", action="store_true", help="do not run DRAT proof checks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    commands = build_commands(args)

    if args.dry_run:
        for label, command in commands:
            print(f"{label}: {shlex.join(command)}")
        return 0

    if not args.skip_drat and not args.drat_trim.exists():
        print(f"missing drat-trim binary: {args.drat_trim}", file=sys.stderr)
        return 1

    for label, command in commands:
        print(f"==> {label}", flush=True)
        print(shlex.join(command), flush=True)
        result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
        if result.returncode != 0:
            print(f"check failed: {label}", file=sys.stderr)
            return result.returncode

    print("all SBP-closed checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
