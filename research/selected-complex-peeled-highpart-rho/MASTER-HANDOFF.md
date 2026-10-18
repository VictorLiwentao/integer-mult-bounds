# Handoff: joint engine-measured rho_peeled_highpart = 0

## Result

For the selected m=73 complex producer, the remaining ordinary leaf-call
classes peeled∪highpart both complete through
`research/physical-ordinary-interchange` (Binary + fitted adapters) with
parent reserve extent 1. Binary.run / Ordinary.run take no stock / S_leaf /
reserve argument (AST + live calls). Exact joint costs: peeled ≤72 calls /
highpart 1 call; reserve_active=0 on both; S_leaf=1 on both. Therefore
**rho_peeled_highpart = 0** is engine-measured. Routing∪adapters remain under
the complex cover's finite scalar/router guard (named, not phrase-assigned).
Selected κ unchanged at `0.001672660197076918`.

Pinned CrocSwap main: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Branch: `cursor/peeled-highpart-rho-60b9`.
Content tip (gates PASS): `789e40be39978ec84f5e9ab546552c13658e31ad`.
Packaging tip: `git rev-parse HEAD` on this branch after this file.
Package: `research/selected-complex-peeled-highpart-rho`.

## Switch

No card switch. Preferred obligation: engine-measured card/global rho binding
for peeled+highpart with adapters that close the ordinary leaf path. Avoided
class-only S_leaf=1 reprints and citation-only router inventory partitions
(both DEFER'd). Did not touch #3683 flag-0 tail, #3669 chronology, C5, or
near-literal #3532 retargets.

## Exact commands (expected PASS)

```sh
python3.12 -I -W error -B research/selected-complex-peeled-highpart-rho/verify.py
# PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO ... rho_peeled_highpart=0 ... no_new_kappa

python3.12 -I -O -W error -B research/selected-complex-peeled-highpart-rho/verify.py

python3.12 -I -W error -B research/selected-complex-peeled-highpart-rho/independent.py
# PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO_INDEPENDENT ... rho_peeled_highpart=0 ...

python3.12 -I -W error -B research/selected-complex-peeled-highpart-rho/test_package.py
# PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO_TESTS groups=6

python3.12 -I -W error -B research/selected-complex-peeled-highpart-rho/verify.py --suite fitted
# PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO_FITTED ...

python3.12 -W error -B scripts/research_package.py --package research/selected-complex-peeled-highpart-rho
# PASS_REGISTERED_RESEARCH_PACKAGE research/selected-complex-peeled-highpart-rho outcome=completed
```

## Closest priors

- [#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421) A=0; rho open
- [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113) B_bits=2642; rho unbound
- [#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105) conditional S_leaf=1
- Deferred class-only peeled / highpart packages; deferred citation-only router-rho

## Soft-overlap risks

- Shares physical-ordinary engine and fitted fixture with deferred class-only
  packages; novelty is the joint certificate, adapter stock-free measurement,
  and composed rho_peeled_highpart=0.
- Does not claim unconditional global rho=0 (routing∪adapters not leaf-engine
  measured).
- Leave-alones untouched: #3683, #3669, #3532, #3643/#3639, groups B–D, #3421
  A=0 recomputation.

## Attribution

Author/committer: Wentao Li `<wentaol4@illinois.edu>`.
No `Co-authored-by: Victor Li`.
`ai_assistance`: neutral substantial-AI disclosure only (no product/model names).

## Disposition

Push VictorLiwentao fork only. Do **not** open a CrocSwap PR from this worker
(master decides publish after skeptical review).
