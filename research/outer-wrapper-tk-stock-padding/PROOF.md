# Outer-wrapper stock padding for every multiplicity `t < q`

Fix a prime `q > 2^80` and integers `e,w >= 1`. Write

```text
N = |GL_64(F_q)|,
H = q^(4096(w-1)),
K = 269241600 N H,
D(e) = 0                         if e < 64,
D(e) = 1 + D(42 floor(e/64))      otherwise.
```

David Arias's PR2753 supplies the compatible fresh-row stock

```text
S(t) = t K^{D(e)}
```

for every positive integer multiplicity `t >= 1`. Nick Petalas's merged outer
borrowing wrapper (PR2808) accepts a caller-supplied modulus `S` only under
`1 <= S <= R` with `R = q^k`, and pads to `R' = ceil(R/S)*S`, requiring the
factor to be strictly below two. jwr's
[`selected-lcm-stock-wrapper-fit`](../selected-lcm-stock-wrapper-fit/README.md)
binds the unit-multiplicity case `S(1) = K^{D(e)}` to sigma `6748`, ell `16`
and all fourteen selected fit guards. The
[caller/storage map](../../docs/research/selected-bit-caller-storage-map.md)
still names the `t K^{D(e)}` obligation explicitly.

This note discharges that multiplicity gap. For every integer `t` with
`1 <= t < q`,

```text
log_q S(t) < 6748 w (1 + log2 e).
```

Setting `k = ceil(log_q S(t))` and `R = q^k` then gives the wrapper
precondition `1 <= S(t) <= R` and the below-two padding identity
`R <= R' < 2R`. Every recorded native and conservative selected cutoff still
meets Josie Elliston's repair-(b) numeric hypotheses at `ell = 16`, under the
same atom-width and coarse-width reading as the unit-multiplicity prior. No
new kappa, supplier, GL64 endpoint or physical tape is claimed.

## Source boundary

The PR2753 recursive-caller proof states the stock `R = t K^{D(n)}` and the
capacity estimate that stops short of implementing the outer
padding/borrowing wrapper. The outer-wrapper README states the modulus
precondition and the padding shape `R' = ceil(R/S)*S` with `R <= R' < 2R`,
and explicitly leaves the choice of `S`, `k` and `k < e/2` to its caller.
The unit-multiplicity fit package proves the `t = 1` case and does not
mention multiplicity `t`. All three texts, the storage map and the selected
assembly are live inputs. No predecessor executable is imported.

## 1. Packet and depth bounds

Counting independent columns gives `N < q^{4096}`. The selected prime domain
has `q > 2^{80} > 269241600`, so

```text
K < q · q^{4096} · q^{4096(w-1)} = q^{4096 w + 1},
```

hence `log_q K < 4096 w + 1`. The integer certificate

```text
2^{17} · 42^{28} < 64^{28}
```

gives `42/64 < 2^{-17/28}`. Strong induction on the floor recurrence yields

```text
D(e) <= (28/17) log2(max(1, e))
```

for every integer `e >= 1`, with the inductive step strict for internal
widths.

## 2. Multiplicity absorption

Assume `1 <= t < q`. Then `log_q t < 1`. For `D(e) = 0` one has
`S(t) = t`, so `log_q S(t) < 1`. For every admitted `w,e >= 1` the target
`6748 w (1 + log2 e)` is at least `6748`, and the inequality is strict.

For `D(e) >= 1` and `e >= 2`,

```text
log_q S(t) = log_q t + D(e) log_q K
           < 1 + D(e) (4096 w + 1)
           <= 1 + (28/17)(4096 w + 1) log2(e).
```

The coefficient comparison `(28/17)(4096 w + 1) <= 6748 w` is exactly
`4096 w + 1 <= 4097 w`, i.e. `1 <= w`, which holds for every admitted atom
width. Consequently

```text
log_q S(t) < 1 + 6748 w log2(e) <= 6748 w (1 + log2 e),
```

using `1 <= 6748 w`. At `w = 1` the middle step is equality before the strict
packet and multiplicity steps; the outer inequality remains strict.

The identity `(28/17) · 4097 = 6748` is the same one used for unit
multiplicity. The weak depth estimate `D(e) <= 2 log2 e` does not give this
coefficient: at `w = 1` it produces the larger product `8194`.

## 3. Wrapper precondition and below-two padding

Set `k = ceil(log_q S(t))` and `R = q^k`. Then `1 <= S(t) <= R` by
construction of the ceiling. The wrapper padding length is
`R' = ceil(R / S(t)) · S(t)`. It equals `R` when `S(t) = R` and is at most
`R + S(t) - 1 <= 2R - 2` when `S(t) < R`. In every case
`R <= R' < 2R`, so the padding factor is strictly below two. This is exactly
the interface the wrapper states and does not discharge. At recorded selected
cutoffs one has `e >= 64`, hence `D(e) >= 1`.

## 4. Fourteen fit guards

Write `sigma = 6748` and `ell = ceil(log2(8 · 6748)) = 16`. Every one of the
fourteen recorded native and conservative cutoffs in the selected assembly
meets the numeric hypotheses of Josie Elliston's repair-(b) fit lemma at this
`ell`, by the same recomputation as the unit-multiplicity prior: each
reproduced `L` satisfies `L · gap >= 2(4 + 16)` and `L · gap^2 >= 36`. Those
hypotheses, together with the stock bound of Section 2 and the stage atom
width `w = ceil(e^s)`, give `k < e/2` under the lemma's reading. The fit
conclusion is not a statement for independently chosen arbitrary `w` and `e`.
The separate uniform cutoff `311311` for atom exponent `17/10000` is a
different theorem and is not identified with these stages.

## 5. Limits

The result concerns the prescribed PR2753 stock shape and the outer wrapper's
numerical interface. It does not prove that PR2753's unweighted program is
the wrapper's `F_I` callee, does not implement metadata restoration on fixed
physical tapes, does not bind the complex `m = 73` per-level divisor, and
does not change the selected frontier. Multiplicities `t >= q` lie outside
the stated domain: then `log_q t >= 1` and the one-unit absorption above need
not apply.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
