# 2026-06-19 Proof-Reuse Loop

## Goal

Run a bounded autonomous loop over SBP-closed graphs to test whether additional
single-edge deletions can reuse the same upstream DRAT proofs.

## Tooling Added

- `scripts/scan_edge_proof_reuse.py`
- `tests/test_scan_edge_proof_reuse_cli.py`

The scanner:

1. removes one candidate edge,
2. filters edge-color conflict clauses from the CNF,
3. runs `drat-trim` against the original proof,
4. appends a CSV row with `VERIFIED`, `NOT_VERIFIED`, `TIMEOUT`, or `ERROR`.

It supports resume through an existing output CSV.

## Scan Results

| graph | checked | verified single deletions | not verified |
| --- | ---: | ---: | ---: |
| 517 | 2573 / 2573 | 27 | 2546 |
| 529 | 2003 / 2659 | 26 | 1977 |
| 553 | 2712 / 2712 | 7 | 2705 |

The 529 scan stopped on the time budget with 656 candidates remaining.

## Final Greedy Candidates

The final artifacts use a greedy combination pass over verified single-edge
deletions. A single-edge deletion can verify while a combination fails, so the
greedy pass keeps only deletions that preserve DRAT verification for the whole
current set.

| graph | previous SBP-closed edges | final edges | removed edges | CNF clauses | DRAT | embedding |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| 517 | 2576 | 2556 | 20 | 13843 | VERIFIED | all unit |
| 529 | 2662 | 2641 | 21 | 11093 | VERIFIED | all unit |
| 553 | 2715 | 2708 | 7 | 11388 | VERIFIED | all unit |

## Interpretation

This improves the local certificate package, but it is still not a new
Hadwiger-Nelson lower bound. The contribution remains computational: smaller
SBP-closed certificate variants plus reproducible deletion-scan logs.
