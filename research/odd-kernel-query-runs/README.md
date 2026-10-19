# Odd-kernel run batching for completed native DATA shears

**Research construction / recursive interface; no new kappa.** Combines the
dyadic-run schedule of
[PR953](https://github.com/CrocSwap/integer-mult-bounds/pull/953)
(`research/dyadic-query-runs`) with the odd-kernel admission pattern of
[#2687](https://github.com/CrocSwap/integer-mult-bounds/pull/2687)
(`research/odd-kernel-query-pair` / PR840 lineage).

For every positive odd kernel `q` and every finite nonempty index set `J` with
`r=|J|` indices in `c` maximal consecutive runs, the signed q-dyadic run walk
attains the typed invoice below on every **odd modulus coprime to `q`**. Even
moduli and odd moduli sharing a prime with `q` are excluded. Typed costs match
the dyadic formula and do **not** improve for larger `q`.

| Complete cost item | Separate #2687 pairs | Odd-kernel run batch |
|---|---:|---:|
| Ordinary recursive children | `3r` | `2r+c` |
| Ordered affine events | `18r` | `6(2r+c)` |
| Aligned XOR scans | `2r` | `2r` |
| Extra full private rows | 0 | 0 |

Seed-55 witness `J={0,1,2,4,5}` (`r=5`, `c=2`): children `15→12`, affine
`90→72`, XOR `10`. Certificate kernels `{1,3,5,7,9,15}`; all 63 nonempty
subsets of `{0,…,5}` per kernel. Restricted alphabet: query powers in
`{±q·2^k}`. The written `2r+c` lower bound carries over from the dyadic-run
graph argument with q-dyadic edges.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/odd-kernel-query-runs/verify.py
python3.12 -I -O -B research/odd-kernel-query-runs/verify.py
python3.12 -I -B research/odd-kernel-query-runs/independent.py
python3.12 -I -B research/odd-kernel-query-runs/test_package.py
python3.12 -B scripts/research_package.py --package research/odd-kernel-query-runs
```

Expected:

```text
PASS_ODD_KERNEL_QUERY_RUNS kernels=[1, 3, 5, 7, 9, 15] subsets_per_kernel=63 seed55_children=15->12 affine=90->72 xor=10 no_typed_gain_over_dyadic ... no_new_kappa
PASS_INDEPENDENT_ODD_KERNEL_QUERY_RUNS kernels=[1, 3, 5, 7, 9, 15] ... no_new_kappa
PASS_ODD_KERNEL_QUERY_RUNS_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/odd-kernel-query-runs outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes. Corrupted
temporary certificates and duplicate JSON keys are rejected.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Direct predecessors:
PR953 / `research/dyadic-query-runs` (dyadic alphabet only) and #2687 /
`research/odd-kernel-query-pair` (single-pair odd kernels). This package does
not edit those trees. It does **not** answer #2687 OQ1 (admitted BIT-supplier
hosting / fully charged source-return bill) and does **not** retarget the
#3702 coefficient-bit tariff. Clear of UT4 weighted cascade, route-cube
fibre/key scaffold, and forbidden leave-alones listed on the worker card.

Selected κ stays `0.001672660197076918`.

## Open next questions

1. Can an admitted BIT supplier host a small odd-kernel run batch (or single
   shear) with a favorable fully charged bill versus the dyadic path? First
   write one exact source-return boundary and charge routing, precision and
   dispatch non-cancellably. Still #2687 OQ1 / #3702 leave-alone.
2. Does allowing a mixed alphabet of several odd kernels on one target ever
   beat separate single-kernel batches under the same typed invoice model?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit #2687 / #3702 leave-alone context, PR953 / dyadic-query-runs,
PR840 / dyadic-query-pair, and PR521/PR677 ADDRESS / DATA-shear lineage. No
independent human review is claimed. No new kappa.
