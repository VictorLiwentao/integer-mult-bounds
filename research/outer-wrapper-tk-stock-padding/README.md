# Outer-wrapper stock padding for every multiplicity `t < q`

**Scoped interface lemma; no new kappa.** David Arias's PR2753 supplies the
compatible fresh-row stock `S(t) = t K^{D(e)}` for every positive multiplicity
`t`. jwr's [`selected-lcm-stock-wrapper-fit`](../selected-lcm-stock-wrapper-fit/)
binds only the unit case `t = 1` to sigma `6748`, the outer wrapper's
`1 <= S <= q^k` precondition and the below-two padding factor. The
[caller/storage map](../../docs/research/selected-bit-caller-storage-map.md)
still names the `tK^D(e)` obligation. This package closes that multiplicity
gap.

For every prime `q > 2^{80}`, integers `e,w >= 1` and integer `t` with
`1 <= t < q`,

```text
K = 269241600 |GL_64(F_q)| q^(4096(w-1)),
D(e) = 0 if e < 64 else 1 + D(42 floor(e/64)),
S(t) = t K^{D(e)},
log_q S(t) < 6748 w (1 + log2 e).
```

With `k = ceil(log_q S(t))` and `R = q^k`, the wrapper precondition
`1 <= S(t) <= R` holds and the padding length `R' = ceil(R/S(t)) · S(t)`
satisfies `R <= R' < 2R`. All fourteen recorded selected cutoffs still meet
the `ell = 16` numeric hypotheses of Josie Elliston's repair-(b) fit lemma
under the same stage reading as the unit-multiplicity prior. Selected decimal
stays `0.001672660197076918`.

The written [proof](PROOF.md) absorbs `log_q t < 1` into the strict packet
bound `log_q K < 4096 w + 1` and the depth certificate
`2^{17} · 42^{28} < 64^{28}`. Multiplicities `t >= q` are outside the stated
domain. No GL64 callee, physical metadata restoration, supplier or frontier
change is claimed.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -I -B research/outer-wrapper-tk-stock-padding/verify.py
python3.12 -I -O -Werror -B research/outer-wrapper-tk-stock-padding/verify.py
python3.12 -I -B research/outer-wrapper-tk-stock-padding/independent.py
python3.12 -I -B research/outer-wrapper-tk-stock-padding/test_package.py
python3.12 -B scripts/research_package.py --package research/outer-wrapper-tk-stock-padding
```

Expected markers include

```text
PASS_OUTER_WRAPPER_TK_STOCK_PADDING sigma=6748 ell=16 multiplicity=1..q-1 below_two fourteen_fit_guards no_new_kappa
PASS_OUTER_WRAPPER_TK_STOCK_PADDING_TESTS groups=7
PASS_REGISTERED_RESEARCH_PACKAGE research/outer-wrapper-tk-stock-padding outcome=completed
```

Default `verify.py` is read-only. Admission uses `need()` and still fires
under `-O`. Corrupted temporary certificates and duplicate JSON keys are
rejected. `independent.py` does not import `verify.py`.

## Open next questions

1. Is PR2753's actual unweighted program the wrapper's `F_I` callee at one odd
   prime and one borrowed width, including pointwise restoration of padded
   `t K^D` rows?
2. Can padding/count streams and complete metadata restoration share the
   physical caller's fixed tape inventory for a fitted `t > 1` plan?

## Credit

Closest priors: David Arias / PR2753 for the `t K^D` stock; Nick Petalas /
PR2808 for the outer borrowing wrapper interface; jwr /
`selected-lcm-stock-wrapper-fit` for the unit-multiplicity sigma `6748` fit;
Josie Elliston for the repair-(b) fit lemma; Nick Petalas / PR2120 for the
depth certificate; Adam Gall / PR2084 for the parent-reserve shape; the
selected-bit caller/storage map for naming the `tK^D` padding obligation.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
