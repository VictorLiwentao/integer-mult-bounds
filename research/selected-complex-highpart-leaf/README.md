# Selected complex high-part exchange through the completed ordinary leaf

**Card `selected-stock-envelope`, scope refined** to the leaf-reserve term
`rho` left open by
[`research/selected-stock-envelope-m73`](../selected-stock-envelope-m73/) /
[#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113) and by
[`research/selected-stock-shape-a-zero`](../selected-stock-shape-a-zero/) /
[#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421) (A=0; rho
unbound). A citation-only `rho=0` via `S_leaf=1` and a peeled-atom residual
realization were deferred. This package realizes a **disjoint** PR185
leaf-call class: the high-part exchange of
`notes/three-stage-cover-rows.tex`.

## Claim

For the selected m=73 complex producer, the post-wrapper high-part exchange
(one ordinary width-`k` interchange of `H_hi` with `D_hi`, bodies and `Z` as
spectators) completes through the published
`research/physical-ordinary-interchange` engine with parent leaf reserve
extent 1. Exact before/after costs are recorded: naive full-chunk active
width `k+body` versus high-part active width `k`, call count exactly 1.
On this class `S_leaf = 1`. Global `rho` stays open. **No new kappa.**
Selected κ stays `0.001672660197076918`.

## Validation

```sh
python3.12 -I -B research/selected-complex-highpart-leaf/verify.py
python3.12 -I -O -B research/selected-complex-highpart-leaf/verify.py
python3.12 -I -B research/selected-complex-highpart-leaf/independent.py
python3.12 -I -B research/selected-complex-highpart-leaf/test_package.py
python3.12 -I -B research/selected-complex-highpart-leaf/verify.py --suite fitted
python3.12 -B scripts/research_package.py --package research/selected-complex-highpart-leaf
```

Expected:

```text
PASS_SELECTED_COMPLEX_HIGHPART_LEAF shapes=25 calls=1 active_width=k full_chunk_width=k+body width_ratios=2/1..6/1 physical_cases=12 controls=4 S_leaf=1_realized_on_highpart_exchange no_new_kappa
PASS_SELECTED_COMPLEX_HIGHPART_LEAF_INDEPENDENT shapes=25 calls=1 physical_cases=12 engine_payloads_match
PASS_SELECTED_COMPLEX_HIGHPART_LEAF_TESTS groups=6
PASS_SELECTED_COMPLEX_HIGHPART_LEAF_FITTED cases=2 padded_ratio=3/2 own_rows=8 reserve_extents=1,2 parent_reserve_restored_through_C0
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-complex-highpart-leaf outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under
`-O`. The fitted suite is included in the registered package check.

## Soft-overlap note

Closest priors: [#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421)
(A=0; rho open), [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113),
[#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105),
`research/physical-ordinary-interchange`, and the deferred packages
`research/selected-stock-rho-zero/` (citation-only) and
`research/selected-complex-peeled-leaf/` (peeled residual class). This package
does **not** reprint the peeled residual, does not recompute A=0 or B=2642,
and does not clone the P104 side-correction series. Soft-overlap risk remains
on the shared engine and the fitted `(1,1,1)`-style fixture machinery; the
checkable novelty is the high-part call class, exact `(k+body)/k` width costs,
and dual scanners on that class.

## Open next questions

1. **Fixed cover routing.** Can the complex producer's fixed-port routing be
   realized the same way, so that together with the deferred peeled residual
   and this high-part class every PR185 leaf-call use has `S_leaf = 1`?
   Relevance: global `rho` needs every class. First step: extract from
   `notes/three-stage-cover-bit.tex` the constant number of width-`O(w)`
   interchanges per fixed port and write one port's signatures against the
   same engine. Blocked by: the complex cover note does not write routing as
   ordinary interchanges.
2. **Production-width high-part.** Does a production call at
   `k = ceil(log_q S)` keep the parent reserve out of its fresh rows, not
   only on the reduced fitted fixture? Blocked by: uniform `C(w)` for the
   complex producer is not established; production fitted domain is huge.

## Credit

Credit Aaron Wang / #3113, Sricharan Vagvala / #2105, Adam Gall / #2084,
Jose Manuel / physical-ordinary-interchange, and #3421. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance,
under Apache-2.0.
