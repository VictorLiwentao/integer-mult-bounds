# Handoff: finite Sp(72,2)×14826 stock as uniform C(w) packet

## Result

The selected m=73 complex assembler's charged per-level stock unit is
`C = |Sp(72,2)| * 14826` with bit length 2642 and no atom-width factor in the
stock block. At every probed atom width the packet bit length is that same
constant. A coarse residual restore fixture shows sequential residuals draw and
restore a fresh role on a w-free divisor. This answers #3421 OQ2's first step
(finite stock as uniform C(w) candidate via packet cardinality). Leaf reserve
`rho` remains unbound. Outer ledger adoption is not claimed. Selected κ is
unchanged at `0.001672660197076918`.

Pinned main: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Branch: `cursor/stock-finite-c-packet-60b9`.
Package: `research/selected-stock-finite-c-packet`.

## Switch

Did not switch cards. Preferred obligation after #3421 was OQ2 (finite stock as
uniform C(w)), not another A=0/B=2642 reprint and not citation-only rho=0 or
class-only S_leaf leaf/router work (those clusters are deferred / leave-alone).

## Exact commands (expected PASS)

```sh
python3.12 -I -B research/selected-stock-finite-c-packet/verify.py
# PASS_SELECTED_STOCK_FINITE_C_PACKET C=Sp72x14826 bits=2642 w_free coarse_residual_restore rho=unbound no_new_kappa

python3.12 -I -O -Werror -B research/selected-stock-finite-c-packet/verify.py
# same marker

python3.12 -I -O -Werror -B research/selected-stock-finite-c-packet/independent.py
# ..._INDEPENDENT

python3.12 -I -O -Werror -B research/selected-stock-finite-c-packet/test_package.py
# PASS_SELECTED_STOCK_FINITE_C_PACKET_TESTS groups=7

python3.12 -B scripts/research_package.py --package research/selected-stock-finite-c-packet
# PASS_REGISTERED_RESEARCH_PACKAGE research/selected-stock-finite-c-packet outcome=completed
```

## Closest priors

- [#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421)
  `research/selected-stock-shape-a-zero` — A=0, left OQ2 open.
- [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113)
  `research/selected-stock-envelope-m73` — B_bits=2642.
- [#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105)
  `research/selected-coarse-depth-stock` — 43/26 depth; finite-stock-as-C admission.
- [#2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084)
  `research/selected-bit-parent-reserve` — ordinary packet interface contrast.

## Soft-overlap risks

- Do not read this as recomputing #3421's A=0 or #3113's B_bits as a contribution.
- Do not read this as citation-only rho=0 or as a peeled/highpart/router leaf
  realization (those packages are deferred; leaf classes stay separate here).
- Do not read `C(w):=C` as outer adoption of the 15555 ledger replacement.
- Leave alone: #3696 gate-operand, deferred dest-absent, stock-leaf DEFERs,
  flag-0 cascade, C5, side-correction, present-head chronologies, groups B–D.

## What remains open

Bind `rho` with a failing-capable completed-leaf realization; maintainer
adoption of the conditional ledger refinement.

## Credit

Aaron Wang (#3113), Wentao Li (#3421), Sricharan Vagvala (#2105), Adam Gall
(#2084), retained assembler and cover notes. Notices untouched.

Prepared by Wentao Li with substantial AI assistance.
