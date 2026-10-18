# Master handoff — `research/selected-complex-router-adapters-engine/`

## Candidate

- Branch: `cursor/complex-router-adapters-engine-60b9` (VictorLiwentao fork).
- Tip: `420b3a95a2634b7bbf29019b705c54cb2aa8c593` (scientific `23b168e97862c15faf17e8a3226157b8a5329a29`; SOURCES head pin `93542bce3a4610c8b20ef4336dd25e014fead0f1`).
- Package: `research/selected-complex-router-adapters-engine/`
- Base: CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`
- Card: `selected-stock-envelope` (refined), priority revision 6
- κ: unchanged at `0.001672660197076918`
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`, with no
  `Co-authored-by: Victor Li` trailer (`git -c core.hooksPath=/dev/null commit`).
- **Do not open a CrocSwap PR** — master publishes.

## Claim

On the selected m=73 complex producer, an executable F₂ scalar/router residual
engine for the routing∪adapters operation class measures ordinary external
leaf calls **0**, recursive Fourier children **0**, positive-rank connectors
**0**, parent-reserve active reads **0**, hence `rho_contrib=0` for those two
inventory classes (exhaustive m=3 domain 64; reserve extents 1≡3). Cites A=0 /
B_bits=2642; peeled+highpart remain. No new kappa.

## Why this is not a leave-alone reprint / deferred citation

Distinct from deferred `selected-complex-router-rho-discharge` (tex
phrase-match assigned zeros): costs are metered from `router.py` execution
with mutant controls that measure nonzero. Does not recompute A=0/B=2642, does
not reprint deferred peeled/highpart cores, does not claim global `rho=0`.

## Evidence commands

```sh
python3.12 -I -Werror -B research/selected-complex-router-adapters-engine/verify.py
python3.12 -I -O -Werror -B research/selected-complex-router-adapters-engine/verify.py
python3.12 -I -O -Werror -B research/selected-complex-router-adapters-engine/independent.py
python3.12 -I -O -Werror -B research/selected-complex-router-adapters-engine/test_package.py
python3.12 -Werror -B scripts/research_package.py --package research/selected-complex-router-adapters-engine
```

Expected markers:

```text
PASS_SELECTED_COMPLEX_ROUTER_ADAPTERS_ENGINE inventory=4 routing_adapters_ordinary_calls=0 rho_contrib=0 fourier_children=0 positive_rank=0 exhaust=64 reserve_indep=1 remaining=peeled+highpart A=0_cited B=2642_cited engine_measured no_new_kappa
PASS_SELECTED_COMPLEX_ROUTER_ADAPTERS_ENGINE_INDEPENDENT ordinary_calls=0 rho_contrib=0 fourier_children=0 exhaust=64 reserve_indep=1 remaining=peeled+highpart
PASS_SELECTED_COMPLEX_ROUTER_ADAPTERS_ENGINE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-complex-router-adapters-engine outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.
Duplicate JSON keys are rejected. On-disk certificate corruption is rejected
in temp copies.

## Soft overlap

- Soft vs deferred router-rho citation: same inventory partition; novelty is
  engine measurement.
- Soft vs #3421: cites A=0/B only.
- Soft vs deferred peeled/highpart / peeled-highpart-rho: does not reprint
  those cores or assign `rho_*=0` without measuring routing∪adapters.
- Leave-alones (flag-0, C5, side-correction, groups B–D, #3532) untouched.

## Disposition

Fork branch for master publish decision. Do not open a CrocSwap PR from this
worker.
