# Data Sources

This repository combines local verification code with upstream certificate data.

## Upstream Data

The following files were downloaded from `marijnheule/CNP-SAT`:

- `data/hadwiger-nelson/external/marijnheule-CNP-SAT/edge/*.edge`
- `data/hadwiger-nelson/external/marijnheule-CNP-SAT/cnf/*.cnf`
- `data/hadwiger-nelson/external/marijnheule-CNP-SAT/proof/*.drat`
- `data/hadwiger-nelson/external/marijnheule-CNP-SAT/vtx/*.vtx`
- directory listing JSON files under `data/hadwiger-nelson/external/marijnheule-CNP-SAT/`

Source repository:

- https://github.com/marijnheule/CNP-SAT

The DRAT checker is not vendored. Reproduce the expected local path with:

```bash
git clone https://github.com/marijnheule/drat-trim.git \
  data/hadwiger-nelson/external/drat-trim
make -C data/hadwiger-nelson/external/drat-trim
```

## Generated Data

The following directories contain local generated artifacts:

- `data/hadwiger-nelson/generated/cores/`
- `data/hadwiger-nelson/generated/core-reduced/`
- `data/hadwiger-nelson/generated/sbp-closed/`

The primary reproducibility artifacts are the `sbp-closed` edge/CNF pairs. They
retain the symmetry-breaking support triangle on vertices `1`, `2`, and `6` and
verify against the upstream CNP-SAT DRAT proofs.

## Checksums

Key artifact checksums are recorded in:

- `data/hadwiger-nelson/generated/sbp-closed/SHA256SUMS`
