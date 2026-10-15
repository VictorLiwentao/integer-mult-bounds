# Production packed quadratic-affine rank witness

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`scripts/experiments/quadratic_affine.py:rank_witness` still built each binary
row with the historical pairwise `inner` loop over all sample columns. Curtis
Dransfield's opt-in adapter `research/quadratic-affine-packed/` (incorporated
[#752](https://github.com/CrocSwap/integer-mult-bounds/pull/752)) already proved
an exact base-256 packed-lane algorithm with identical receipts. This package
wires that equivalent check into the **production** source used by
`scripts/audit_quadratic_affine.py` / `make verify-certificates`.

Only the source pin for `scripts/experiments/quadratic_affine.py` changes inside
`certificates/quadratic-affine-vectors.json`. Every orthogonality entry is still
materialised; GF(2) elimination, row digests, rational span controls and the
retained historical `2^-31` language are unchanged. Selected frontier untouched.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/quadratic-affine-production/verify.py
python3.12 -I -O -B research/quadratic-affine-production/verify.py
python3.12 -B scripts/research_package.py --package research/quadratic-affine-production
python3.12 -I -B research/quadratic-affine-production/benchmark.py --rounds 5
```

Expected:

```text
PASS_QUADRATIC_AFFINE_PRODUCTION cases=12 ... no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/quadratic-affine-production outcome=completed
PASS_IDENTICAL_QUADRATIC_AFFINE_PRODUCTION_RECEIPTS
```

Default verify is read-only. Use `--write-certificate` only after editing the
production source. Timing is host-descriptive and is not a correctness gate.

On Linux / CPython 3.12.3, five alternating fresh-process pairs gave median
**witness-only** and **complete audit** ratios recorded in
[`RESULT.json`](RESULT.json) after `benchmark.py`.

## Why the packed check is equivalent

Write each sampled vector coordinate as a Gaussian unit or zero. For `N`
columns and `D <= 32`, pack each ambient coordinate into signed base-256 lanes
and evaluate `conj(v) · w[j]` as a polynomial identity with digits in
`[0, 2D] ⊂ [0, 64]`. Zero-lane detection and power-of-two compaction recover
exactly the support of the historical orthogonality relation; OR-ing bit `i`
recovers **I plus the full orthogonality relation**. The original ordered GF(2)
elimination and independence rejection are unchanged. This is the same argument
as `research/quadratic-affine-packed/README.md`.

## Overlap and credit

Closest priors:

- [Curtis Dransfield / quadratic-affine-packed](../quadratic-affine-packed/) /
  [#752](https://github.com/CrocSwap/integer-mult-bounds/pull/752) — opt-in
  packed adapter; this package is the production wiring of that algorithm.
- Open [#1076](https://github.com/CrocSwap/integer-mult-bounds/pull/1076) —
  different bit-sliced production engine for the same hotspot; credited, not
  imported.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Production-promotion pattern of central-factor / leech-minor packages; those
  leave-alone objects were not reopened.

Douglas R. Colkitt authored the quadratic-affine families and original checker.
Curtis Dransfield authored the packed algorithm. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** If open #1076's distinct bit-sliced engine later lands, does it
   supersede or coexist with the packed production path?
   **Why it matters:** Two production algorithms for the same hotspot would need
   an explicit maintainer choice.
   **First step:** Diff #1076 head against this packed `rank_witness`.
   **Blocked by:** #1076 remains open / partially reviewed.

2. **Question:** Should `verify-certificates` adopt a microbenchmark regression
   gate for the twelve-case `rank_witness` workload?
   **Why it matters:** A future edit could restore the pairwise loop without
   failing equivalence tests.
   **First step:** Decide whether `RESULT.json` medians belong in CI or remain
   descriptive.
   **Blocked by:** Maintainer CI-budget preference.
