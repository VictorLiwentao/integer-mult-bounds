# Engine-measured routing∪adapters discharge from external leaf-reserve rho

**Card `selected-stock-envelope`, scope refined** to the routing/adapter share
of the leaf-reserve constant `rho` left open by
[`research/selected-stock-envelope-m73`](../selected-stock-envelope-m73/) /
[#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113) and
[`research/selected-stock-shape-a-zero`](../selected-stock-shape-a-zero/) /
[#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421) (`A=0`;
rho unbound). A prior citation-only router discharge
(`research/selected-complex-router-rho-discharge/`) was deferred for
tex phrase-matching. This package answers the preferred next with an
**executable** scalar/router residual engine.

## Claim

The coarse-depth inventory has four leaf-call classes: peeled, routing,
adapters, high-part. On the selected complex producer, routing and adapters
are the cover's rank-zero endpoint adapters, fixed scalar shears, endpoint
Paulis and fixed linear maps inside the finite scalar/router guard
(`notes/three-stage-cover-complex.tex`). An executable F₂ residual engine
(`router.py`) runs that operation class and **measures**:

| Meter | Value |
|---|---:|
| ordinary external leaf calls | **0** |
| recursive Fourier children | **0** |
| positive-rank data connectors | **0** |
| parent-reserve active reads | **0** |
| contribution to shape `rho` | **0** |

Finite scalar/router stock sits inside cited `A=0`, `B_bits=2642` (not
recomputed). BIT ordinary width-`O(w)` routing (unnamed `c_R`) is contrasted,
not imported. Remaining ordinary leaf classes: peeled + high-part. Global
`rho` stays open pending those two. **No new kappa.** Selected κ stays
`0.001672660197076918`.

```sh
python3.12 -I -Werror -B research/selected-complex-router-adapters-engine/verify.py
```

Expected:

```text
PASS_SELECTED_COMPLEX_ROUTER_ADAPTERS_ENGINE inventory=4 routing_adapters_ordinary_calls=0 rho_contrib=0 fourier_children=0 positive_rank=0 exhaust=64 reserve_indep=1 remaining=peeled+highpart A=0_cited B=2642_cited engine_measured no_new_kappa
```

## Why this is not the deferred citation

The deferred package scanned cover tex for “scalar/router guard” / “without
recursive Fourier children” and **assigned** `ordinary_calls=0` /
`rho_contrib=0`. This package:

1. Implements a residual engine whose only paths are rank-zero adapters,
   scalar shears, Pauli translation and fixed linear `F`.
2. Exhausts all `2^{6}=64` inputs at `m=3` and checks the closed form.
3. Shows parent reserve extents 1 and 3 leave every meter and step trace
   unchanged.
4. Injects ordinary-leaf / Fourier / positive-rank / reserve-touch mutants and
   **measures** nonzero meters that charge `rho_contrib=1`.

Phrase citations still bind the operation class to the cover note; the costs
come from execution.

## Scope honesty

This is a finite engine for the published **operation class**, not a
byte-identical production replay of the selected m=73 assembler word. It does
not adopt uniform `C(w)`, does not realize peeled or high-part, and does not
close global `rho`.

## Reproduce

```sh
python3.12 -I -Werror -B research/selected-complex-router-adapters-engine/verify.py
python3.12 -I -O -Werror -B research/selected-complex-router-adapters-engine/verify.py
python3.12 -I -O -Werror -B research/selected-complex-router-adapters-engine/independent.py
python3.12 -I -O -Werror -B research/selected-complex-router-adapters-engine/test_package.py
python3.12 -Werror -B scripts/research_package.py --package research/selected-complex-router-adapters-engine
```

Default verify is read-only. Admission uses `need()` and stays enforced under
`python -O`. Duplicate JSON keys and temp certificate corruption are rejected.

## Soft overlap

- Soft vs deferred `selected-complex-router-rho-discharge`: same inventory
  partition and cited A=0/B; novelty is engine measurement vs phrase-assigned
  zeros.
- Soft vs #3421: cites A=0/B=2642; does not recompute.
- Does not reprint deferred peeled/highpart cores or claim `rho_*=0` by
  composition-without-measurement.
- Leave C5 #3643/#3639 and P104 present-head / flag-0 cascades alone.

## Open next questions

1. **Peeled + high-part card-level closure.** With routing∪adapters
   engine-discharged, can those two ordinary classes jointly bind card-level
   `rho` without another class-only harness?
2. **Hidden fifth class.** Does the selected assembler charge any external
   leaf reserve outside the four-class inventory and inherited 252 slack?

## Credit

Credit #3421, #3113, #2105, `stock-routing-factor`, the deferred
router-rho attempt (as negative prior: phrase-match insufficient), and the
retained selected-stock / cover-note lineage. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance,
under Apache-2.0.
