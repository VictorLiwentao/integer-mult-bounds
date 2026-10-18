# Handoff: selected stock shape rho = 0 (m=73 complex)

## Result

Under the completed ordinary-leaf interface already named by
`research/selected-coarse-depth-stock/PROOF.md`, the selected m=73 complex
producer may take `S_leaf = 1`, so `log_q S_leaf = 0` and the shape bound
`log_q S_leaf(e,w) <= rho*w*(1+log2 e)` holds with **rho = 0**. Ledger term
252 is not `S_leaf`. Citing (not reprinting) A=0 and B_bits=2642, the
composition collapses to `sigma <= (43/26)*(1-s)*2642`. Selected κ is
unchanged at `0.001672660197076918`.

Pinned main: `6f100d4bb5083f8c35d96fd95a539811c62f245c`.
Branch: `cursor/selected-stock-rho-zero-60b9`.
Package: `research/selected-stock-rho-zero`.
Tip SHA: fill after commit (`git rev-parse HEAD`).

## Switch

Did not switch cards. Preferred obligation 1 after A=0 (bind rho or prove
rho=0) was still open. Avoided reprinting A=0 / B=2642. Did not take P104
coefficient work (soft overlap with open #3363/#3365/#3371/#3372) or group
C/D native widths (available as fallback).

## Exact commands (expected PASS)

```sh
python3.12 -I -B research/selected-stock-rho-zero/verify.py
# PASS_SELECTED_STOCK_SHAPE_RHO_ZERO rho=0 S_leaf=1 B_bits=2642_cited A=0_cited completed_ordinary_leaf no_new_kappa

python3.12 -I -O -B research/selected-stock-rho-zero/verify.py
# same marker

python3.12 -I -B research/selected-stock-rho-zero/independent.py
# PASS_SELECTED_STOCK_SHAPE_RHO_ZERO ..._INDEPENDENT

python3.12 -I -B research/selected-stock-rho-zero/test_package.py
# PASS_SELECTED_STOCK_SHAPE_RHO_ZERO_TESTS groups=6

python3.12 -B scripts/research_package.py --package research/selected-stock-rho-zero
# PASS_REGISTERED_RESEARCH_PACKAGE research/selected-stock-rho-zero outcome=completed
```

## Closest priors

- In-flight `research/selected-stock-shape-a-zero` @ `eb215c641` — A=0; left rho unbound.
- [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113)
  `research/selected-stock-envelope-m73` — bound B_bits=2642, left A,B,rho unbound.
- [#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105)
  `research/selected-coarse-depth-stock` — 43/26 depth, S_leaf=1 permission.
- [#2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084)
  `research/selected-bit-parent-reserve` — completed ordinary-leaf hypothesis 4.

## Soft-overlap risks

- Do not read this as recomputing #3113's B_bits or the in-flight A=0 proof.
- Do not read rho=0 as realizing the completed ordinary-leaf interface.
- Do not treat 252 as a selected leaf reserve or as rho.
- Ordinary BIT packages that bind parent envelopes are interface contrast only.

## What remains open

Realize the completed ordinary-leaf interface on one complex residual;
adopt finite stock as uniform `C(w)` so the closed envelope is admitted.

## Credit

Aaron Wang (#3113), Sricharan Vagvala (#2105), Adam Gall (#2084), in-flight
A=0 tip. Notices untouched.

Prepared by Wentao Li with substantial AI assistance.
