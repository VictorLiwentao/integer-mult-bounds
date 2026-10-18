# Handoff: complex routing/adapters discharged from external leaf-reserve rho

## Result

For the selected m=73 complex producer, the coarse-depth leaf-call inventory
has four classes `{peeled, routing, adapters, high-part}`. Routing and
adapters are charged only inside the finite scalar/router guard of
`notes/three-stage-cover-complex.tex`: ordinary external leaf calls **0**,
recursive Fourier children **0**, contribution to shape `rho` **0**. Finite
scalar/router stock is already inside cited `A=0`, `B_bits=2642`. BIT ordinary
width-`O(w)` routing (unnamed `c_R`) is not imported. Remaining ordinary leaf
classes: peeled + high-part. Global `rho` stays open pending those two.
Selected κ unchanged at `0.001672660197076918`.

Pinned CrocSwap main: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Branch: `cursor/complex-router-rho-discharge-60b9`.
Package: `research/selected-complex-router-rho-discharge`.
Content tip: `a62ef2d6cbc7c4b3b23512c5c9a1e5d0504a4039` (full package except this
handoff tip-pin commit).
Packaging tip: `6b8ec515a735885e7388f5d4fa0eb3450e072c96`.

## Switch

No card switch. Preferred next after deferred class-only peeled/highpart and
citation-only `rho=0`: bind card/global rho via routing/adapters. Does not
recompute `A=0` or `B_bits=2642`, does not extend C5 charging or P104
present-head side-correction, does not open a CrocSwap PR.

## Exact commands (expected PASS)

```sh
python3.12 -I -W error -B research/selected-complex-router-rho-discharge/verify.py
# PASS_SELECTED_COMPLEX_ROUTER_RHO_DISCHARGE inventory=4 routing_adapters_ordinary_calls=0 rho_contrib=0 remaining=peeled+highpart A=0_cited B=2642_cited no_new_kappa

python3.12 -I -O -W error -B research/selected-complex-router-rho-discharge/verify.py

python3.12 -I -W error -B research/selected-complex-router-rho-discharge/independent.py
# PASS_SELECTED_COMPLEX_ROUTER_RHO_DISCHARGE_INDEPENDENT inventory=4 ordinary_calls=0 rho_contrib=0 remaining=peeled+highpart

python3.12 -I -W error -B research/selected-complex-router-rho-discharge/test_package.py
# PASS_SELECTED_COMPLEX_ROUTER_RHO_DISCHARGE_TESTS groups=6

python3.12 -W error -B scripts/research_package.py --package research/selected-complex-router-rho-discharge
# PASS_REGISTERED_RESEARCH_PACKAGE research/selected-complex-router-rho-discharge outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.
Duplicate JSON keys and on-disk certificate corruption are rejected (temp copies).

## Soft-overlap risks

- Shares stock-envelope scaffolding with #3421/#3113/#2105 — novelty is the
  inventory partition with exact ordinary-call/rho costs for routing+adapters.
- Contrasts `research/stock-routing-factor` (BIT `c_R` unnamed) without
  reprinting that screen.
- Does not reprint deferred peeled/highpart class-only `S_leaf=1` or
  citation-only `rho=0`.
- Leave-alones untouched: #3643/#3639 C5 chain, P104 present-head
  side-correction series, #3421 A=0 numbers, groups B–D native widths.

## Open questions

1. Peeled + high-part card-level closure for global `rho=0`.
2. Hidden fifth external leaf-reserve class beyond the four-class inventory.

## Attribution

Author/committer: Wentao Li `<wentaol4@illinois.edu>`. No `Co-authored-by: Victor Li`.
`ai_assistance`: neutral substantial-AI disclosure only (no product/model names).
