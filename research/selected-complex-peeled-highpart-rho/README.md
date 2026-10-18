# Joint engine-measured rho for peeled + high-part (selected m=73 complex)

**Card `selected-stock-envelope`, scope refined** to the leaf-reserve term
`rho` left open by
[`research/selected-stock-envelope-m73`](../selected-stock-envelope-m73/) /
[#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113) and by
[`research/selected-stock-shape-a-zero`](../selected-stock-shape-a-zero/) /
[#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421) (`A=0`;
rho unbound). Class-only `S_leaf=1` packages for peeled or high-part alone, and
citation-only routing/adapter inventory partitions, were deferred. This package
answers the preferred next: **engine-measured joint binding of peeled∪highpart
through the physical ordinary Binary/fitted adapters**, composing
`rho_peeled_highpart = 0`.

## Claim

For the selected m=73 complex producer, the two remaining ordinary leaf-call
classes of the PR185 / coarse-depth inventory — peeled atoms (and `n<73`
stopped leaves) and the high-part exchange — each complete through
`research/physical-ordinary-interchange` with parent reserve extent 1.
Exact joint costs:

| Class | Calls | Active width | Reserve active | `S_leaf` |
|---|---:|---|---:|---:|
| Peeled / stopped leaf | ≤72 | `w` | 0 | **1** |
| High-part exchange | 1 | `k` (vs naive `k+body`) | 0 | **1** |

Binary.run / Ordinary.run take **no** stock / `S_leaf` / reserve argument
(AST + live Binary calls). Parent reserve enters only as a factor of the
caller prefix count. Therefore

```text
rho_peeled_highpart = 0
```

is engine-measured on the card, not cited. Routing∪adapters remain under the
complex cover's finite scalar/router guard (named, not phrase-assigned as a
measured discharge). **No new kappa.** Selected κ stays
`0.001672660197076918`.

## Validation

```sh
python3.12 -I -W error -B research/selected-complex-peeled-highpart-rho/verify.py
python3.12 -I -O -W error -B research/selected-complex-peeled-highpart-rho/verify.py
python3.12 -I -W error -B research/selected-complex-peeled-highpart-rho/independent.py
python3.12 -I -W error -B research/selected-complex-peeled-highpart-rho/test_package.py
python3.12 -I -W error -B research/selected-complex-peeled-highpart-rho/verify.py --suite fitted
python3.12 -W error -B scripts/research_package.py --package research/selected-complex-peeled-highpart-rho
```

Expected:

```text
PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO peeled_nodes=1533 peeled_deltas=73/73 peeled_max_calls=72 highpart_shapes=25 peeled_physical=12 highpart_physical=12 controls=4+4 adapters_stock_args=0 rho_peeled_highpart=0 S_leaf=1_both_classes adapters_close_ordinary_leaf_path no_new_kappa
PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO_INDEPENDENT ...
PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO_TESTS groups=6
PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO_FITTED ...
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-complex-peeled-highpart-rho outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under
`-O`. Engine tempdir is cleaned so `-Werror` stays clean.

## Soft-overlap note

Closest priors: [#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421)
(A=0; rho open), [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113),
[#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105),
`research/physical-ordinary-interchange`, deferred class-only peeled/highpart
packages, and deferred citation-only router-rho discharge. This package does
**not** recompute A=0 or B=2642, does not reopen P104 / C5 / flag-0-tail leave-
alones, and does not phrase-assign routing/adapter zeros. Soft-overlap risk
remains on the shared engine and fitted fixture; the checkable novelty is the
**joint** certificate, adapter stock-free measurement, and composed
`rho_peeled_highpart=0`.

## Open next questions

1. **Engine-measure routing∪adapters** so global `rho=0` is unconditional.
2. **Production-width fitted** reserve independence for both classes.

## Credit

Credit Aaron Wang / #3113, #3421 (A=0), Sricharan Vagvala / #2105, Adam Gall /
#2084, Jose Manuel / physical-ordinary-interchange, and the retained cover
notes. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance,
under Apache-2.0.
