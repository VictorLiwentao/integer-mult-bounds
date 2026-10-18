# Finite Sp(72,2)×14826 stock as the uniform C(w) packet candidate

**Card `selected-stock-envelope`, scope refined** to #3421 open question 2:
adopt the finite stock as uniform per-level divisor `C(w)` by tracing a coarse
residual that consumes a fresh complete physical-role packet whose cardinality
equals that stock at every atom width w. Predecessor
[`research/selected-stock-shape-a-zero`](../selected-stock-shape-a-zero/)
(PR [#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421)) already
bound **A = 0** with **B = 2642** under the finite-stock-as-C reading; this
package does not recompute those. Leaf reserve `rho` stays unbound. No new
kappa (selected decimal `0.001672660197076918`).

```sh
python3.12 -I -B research/selected-stock-finite-c-packet/verify.py
```

Expected:

```text
PASS_SELECTED_STOCK_FINITE_C_PACKET C=Sp72x14826 bits=2642 w_free coarse_residual_restore rho=unbound no_new_kappa
```

Python 3.12, standard library only. Default verify is read-only: it re-hashes
eight pinned inputs, admits against `CERTIFICATE.json`, and rejects mutation
controls. Admission uses `need()` and stays enforced under `python -O`.

## What is newly bound

1. **Assembler stock unit.** The selected assembler
   `research/gauge44-slots-t16/code/assemble.py` charges
   `stock = |Sp(72,2)| * invoice['physical']` with physical inventory
   `14336 + 480 + 8 + 2 = 14826`, then
   `row = 2*bit_length(stock) + 9909 + 252 + 1024`. The stock block has no
   atom-width parameter w.
2. **Uniform packet cardinality.** Recomputing `|Sp(72,2)| * 14826` recovers
   bit length 2642. At every probed w ∈ {1,2,4,8,16,32,64} the charged packet
   bit length is that same constant (zero discrete slope).
3. **Coarse residual restore fixture.** A finite w-free divisor fixture shows
   two sequential residuals draw a fresh role, restore it, and reuse the same
   stock; an omit-restore mutant diverges. Leaf classes (peeled / routing /
   adapters / high-part) remain separate completed calls and are not realized
   here.

## Composition status after this package

```text
sigma <= (43/26) * (1 - s) * 2642 + rho
```

still has `rho` unbound. Identifying `C(w) := |Sp(72,2)| * 14826` supplies the
source-bound packet reading #3421 OQ2 asked for; it does not by itself adopt
the conditional ledger `15555` into the selected receipt.

## Reproduce

```sh
python3.12 -I -B research/selected-stock-finite-c-packet/verify.py
python3.12 -I -O -Werror -B research/selected-stock-finite-c-packet/verify.py
python3.12 -I -O -Werror -B research/selected-stock-finite-c-packet/independent.py
python3.12 -I -O -Werror -B research/selected-stock-finite-c-packet/test_package.py
python3.12 -B scripts/research_package.py --package research/selected-stock-finite-c-packet
```

## Open next questions

1. **Bind `rho`.** Still open after #3421. Requires a complex completed-leaf
   realization that can fail without injected meters — not a citation of
   `S_leaf=1`, and not another class-only leaf soft-overlapping deferred
   peeled/highpart/router packages.
2. **Outer ledger adoption.** Whether the other row-ledger terms permit
   replacing `2*2642` by `ceil(43*2642/26)` remains a maintainer/compiler
   admission outside this package.

## Credit

Aaron Wang / #3113 bound `B_bits = 2642`. Wentao Li / #3421 bound A = 0 and
recorded OQ2. Sricharan Vagvala / #2105 supplied the coarse `43/26` depth and
finite-stock-as-C admission language. Adam Gall / #2084 supplies the ordinary
packet interface contrast. The selected gauge44-slots-t16 assembler and cover
notes are retained predecessors. Their notices are unchanged.

Prepared by Wentao Li with substantial AI assistance.
