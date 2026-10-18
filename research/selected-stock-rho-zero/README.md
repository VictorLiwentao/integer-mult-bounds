# Selected stock shape: rho = 0 at the m=73 complex producer

**Card `selected-stock-envelope`, scope refined** to the missing leaf-reserve
constant `rho` left open by
[`research/selected-stock-envelope-m73`](../selected-stock-envelope-m73/)
(PR [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113)) and by
the in-flight A=0 tip
[`research/selected-stock-shape-a-zero`](../selected-stock-shape-a-zero/)
(`eb215c641`). This package does **not** reprint A=0 or B_bits=2642. It proves
that under the completed ordinary-leaf interface already named for the complex
parent formula,

```text
S_parent(e,w) = C(w)^D(n) * S_leaf(e,w),
```

one may take `S_leaf = 1`, so `log_q S_leaf = 0` and

```text
log_q S_leaf(e,w) <= rho * w * (1 + log2 e)
```

holds with **rho = 0**. Citing A=0 and B_bits=2642, the composition collapses
to

```text
sigma <= (43/26) * (1 - s) * 2642.
```

No new kappa (selected decimal `0.001672660197076918`).

```sh
python3.12 -I -B research/selected-stock-rho-zero/verify.py
```

Expected:

```text
PASS_SELECTED_STOCK_SHAPE_RHO_ZERO rho=0 S_leaf=1 B_bits=2642_cited A=0_cited completed_ordinary_leaf no_new_kappa
```

Python 3.12, standard library only. Default verify is read-only: it re-hashes
five pinned inputs, admits against `CERTIFICATE.json`, and rejects mutation
controls. Admission uses `need()` and stays enforced under `python -O`.

## Why rho is zero here

| Interface | External leaf factor | Shape rho |
|---|---|---:|
| Completed ordinary leaf (PR185/PR387 / #2084 hyp. 4) | `S_leaf = 1` | **0** |
| Partial leaf needing external `B > 1` | `S_leaf = B` | must be `> 0` |

The coarse-depth proof already states that complex peeled atoms, routing,
adapters and high-part exchanges are separate completed ordinary calls, and
that under a completed ordinary-leaf contract one may take `S_leaf = 1`.
Ledger term 252 stays inherited external slack, not an ordinary-leaf reserve
estimate, and is not substituted for `rho`.

## Reproduce

```sh
python3.12 -I -B research/selected-stock-rho-zero/verify.py
python3.12 -I -O -B research/selected-stock-rho-zero/verify.py
python3.12 -I -B research/selected-stock-rho-zero/independent.py
python3.12 -I -B research/selected-stock-rho-zero/test_package.py
python3.12 -B scripts/research_package.py --package research/selected-stock-rho-zero
```

`test_package.py` rejects duplicate JSON keys, a temp-corrupted certificate
(`shape_rho` flipped to 1), hash failures, and the `B>1` / `252-as-S_leaf`
controls, and checks that package files are unchanged after replay.

## Open next questions

1. **Realize the completed ordinary-leaf interface on the complex side.** The
   binding here is conditional on that retained hypothesis. First step: exhibit
   one complex residual that returns its row under the PR185 nested-restoration
   contract at stage-1 widths.
2. **Adopt finite stock as uniform `C(w)`.** With A=0 (cited) and rho=0 the
   numerical envelope coefficient is ready once that admission is accepted.
   First step: exhibit one selected residual that consumes a fresh complete
   physical-role packet whose cardinality equals the finite stock at every w.

## Credit

Aaron Wang / #3113 bound `B_bits = 2642` and recorded the missing shape lemma.
Sricharan Vagvala / #2105 supplied the coarse `43/26` depth, parent formula and
`S_leaf=1` permission. Adam Gall / #2084 bound the ordinary completed-leaf
interface. The in-flight A=0 tip left `rho` unbound. Their notices are
unchanged.

Prepared by Wentao Li with substantial AI assistance.
