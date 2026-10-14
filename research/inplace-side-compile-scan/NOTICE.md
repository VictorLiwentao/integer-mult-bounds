# Notice

This package accelerates the historical inplace-side `compile_side` pivot search
in `scripts/experiments/inplace_side.py` while preserving lexicographic gate
lists, pivots, initial matching and certificate small-scalar controls.

Predecessor credit:

- Douglas R. Colkitt — inplace-side rejection, witnesses and original checker.
- CrocSwap/integer-mult-bounds#1793 (`research/inplace-side-performance/`) —
  least-unused flag scan for `verify_prefix`; this package answers that PR's
  open next question on `compile_side` (code-disjoint from the prefix path).
- Closest tooling priors on different objects: #756 (balanced-Fano packed
  replay), #1861 (parity-side basis/contains), #1984 (mixed-point scalar
  digests).

Prepared by Wentao Li with substantial AI assistance, under Apache-2.0.
No independent human peer-review or formal proof-assistant claim.
