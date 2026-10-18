# Complex routing/adapters discharge from external leaf-reserve rho

**Card `selected-stock-envelope`, scope refined** to the routing/adapter share
of the leaf-reserve constant `rho` left open by
[`research/selected-stock-envelope-m73`](../selected-stock-envelope-m73/) /
[#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113) and
[`research/selected-stock-shape-a-zero`](../selected-stock-shape-a-zero/) /
[#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421) (`A=0`;
rho unbound). Class-only `S_leaf=1` realizations of peeled and high-part were
deferred for weak maintainer need. This package answers the preferred next:
bind the **routing/adapter** share of card-level `rho` for the selected m=73
complex producer.

## Claim

The coarse-depth inventory has four leaf-call classes: peeled, routing,
adapters, high-part. On the selected complex producer, routing and adapters
are charged only inside the finite scalar/router guard
(`notes/three-stage-cover-complex.tex`). Exact costs for those two classes:

- ordinary external leaf calls: **0**
- recursive Fourier children: **0**
- contribution to shape `rho`: **0**

Finite scalar/router stock is already inside cited `A=0`, `B_bits=2642`. The
BIT cover's ordinary width-`O(w)` routing (unnamed `c_R`) is not imported.
Remaining ordinary leaf classes: **peeled + high-part**. Global `rho` stays
open pending those two. **No new kappa.** Selected κ stays
`0.001672660197076918`.

## Validation

```sh
python3.12 -I -W error -B research/selected-complex-router-rho-discharge/verify.py
python3.12 -I -O -W error -B research/selected-complex-router-rho-discharge/verify.py
python3.12 -I -W error -B research/selected-complex-router-rho-discharge/independent.py
python3.12 -I -W error -B research/selected-complex-router-rho-discharge/test_package.py
python3.12 -W error -B scripts/research_package.py --package research/selected-complex-router-rho-discharge
```

Expected:

```text
PASS_SELECTED_COMPLEX_ROUTER_RHO_DISCHARGE inventory=4 routing_adapters_ordinary_calls=0 rho_contrib=0 remaining=peeled+highpart A=0_cited B=2642_cited no_new_kappa
PASS_SELECTED_COMPLEX_ROUTER_RHO_DISCHARGE_INDEPENDENT inventory=4 ordinary_calls=0 rho_contrib=0 remaining=peeled+highpart
PASS_SELECTED_COMPLEX_ROUTER_RHO_DISCHARGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-complex-router-rho-discharge outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under
`-O`. Dual scanners agree. Duplicate JSON keys and temp certificate corruption
are rejected.

## Soft-overlap note

Closest priors: [#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421)
(A=0; rho open), [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113),
[#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105),
`research/stock-routing-factor` (BIT `c_R` unnamed), and deferred class-only
peeled/highpart / citation-only `rho=0` packages. This package does **not**
reprint A=0 or B=2642, does not realize class-only `S_leaf=1`, does not extend
C5 charging or the P104 present-head side-correction series, and does not claim
global `rho=0`. Soft-overlap risk is shared stock-envelope scaffolding; the
checkable novelty is the inventory partition with exact ordinary-call / rho
costs for routing+adapters.

## Open next questions

1. **Peeled + high-part closure.** With routing/adapters discharged, can those
   two ordinary classes each bind `S_leaf=1` so card-level `rho=0` follows?
   Relevance: composition collapses to
   `(43/26)*(1-s)*2642 + rho_peeled_highpart`. First step: a joint inventory
   closure, not another class-only harness. Blocked by: deferred peeled/highpart
   weak-need under class-only scope.
2. **Hidden fifth class.** Does the selected assembler charge any external
   leaf reserve outside the four-class inventory and inherited 252 slack?
   Blocked by: assembler call inventory not re-enumerated here; 252 may not be
   substituted for `rho`.

## Credit

Credit Aaron Wang / #3113, #3421 (A=0), Sricharan Vagvala / #2105, Adam Gall /
#2084, Josie Elliston / stock-routing-factor, and the retained cover notes.
Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance,
under Apache-2.0.
