# Edge Proof-Reuse Scan

This directory records the 2026-06-19 bounded proof-reuse loop.

The scanner tries one-edge deletions from an SBP-closed graph, filters the CNF,
and checks whether the original upstream DRAT proof still verifies.

## Scan Coverage

| graph | candidates checked | statuses |
| --- | ---: | --- |
| 517 | 2573 / 2573 | 27 VERIFIED, 2546 NOT_VERIFIED |
| 529 | 2003 / 2659 | 26 VERIFIED, 1977 NOT_VERIFIED |
| 553 | 2712 / 2712 | 7 VERIFIED, 2705 NOT_VERIFIED |

## Final Greedy Artifacts

| graph | removed edges | final edges | final clauses | DRAT | embedding |
| --- | ---: | ---: | ---: | --- | --- |
| 517 | 20 | 2556 | 13843 | VERIFIED | all unit |
| 529 | 21 | 2641 | 11093 | VERIFIED | all unit |
| 553 | 7 | 2708 | 11388 | VERIFIED | all unit |

The final removed edge lists are:

- `517-proof-reuse-final.txt`
- `529-proof-reuse-final.txt`
- `553-proof-reuse-final.txt`

The scan CSV files are append-only logs and can be resumed by rerunning
`scripts/scan_edge_proof_reuse.py` with the same `--output` path.
