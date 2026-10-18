# Cost-preserving J/P elimination unlocks the universal J-free floor 45

## Premises

Fix the 56 physical nondegenerate binary planes and the 23 induced C5s retained
by PR2782/PR1825. Complete-plane binary pairing tariffs are as in the C5
charging line. Local cost-20 theorems and the named-class cancellation charge of
`research/c5-fit-level-cancellation-charge` / [#3643](https://github.com/CrocSwap/integer-mult-bounds/pull/3643)
are **cited, not replayed**: after identical-support netting that package gives
fit-level floors **45** (J-free) and **561/16** (one net J). This note answers
its open OQ: whether a cost-preserving reduction eliminates every net
full-support term so that 45 applies universally inside the named term alphabet
`{diagonal, J, off-diagonal, pairwise Gram}`.

A **named-class exact fit of** `I_112` is a finite integer combination of those
four term classes equaling the identity. Cost is the sum of complete-plane
pairing tariffs of the terms (absolute coefficients).

## Reduction

**Coordinate expand-and-net.** Replace each remaining net `±J` by

```
±J  =  ±(sum_i e_i e_i^T + sum_{i != j} e_i e_j^T)
```

and each remaining net `±P_{ij}` by

```
±(e_i+e_j)(e_i+e_j)^T
  =  ±(e_i e_i^T + e_j e_j^T + e_i e_j^T + e_j e_i^T),
```

then cancel identical-support opposite signs. The `{D, OD}` outer products form
a free basis of all matrices, so every exact fit of `I` reduces uniquely to the
diagonal

```
I = sum_i e_i e_i^T
```

of tariff exactly **224**. The reduced fit is J-free (and P-free).

## Cost non-increase

Write `C(γ, δ)` for the named-class cost of the exact-I parameterisation with
net J-coefficient `γ` and pairwise-Gram coefficients `δ_{ij}` (off-diagonal and
diagonal coefficients then fixed by exactness). Then `C` is a convex piecewise
linear function of `(γ, δ)`, and `C(0, 0) = 224`.

**Pair-expansion lemma.** For every unordered port pair `{i, j}`,

```
τ(P_{ij}) + τ(OD_{ij}) + τ(OD_{ji})  ≥  4,
```

with equality on 436 of the 6216 pairs (dual scanners agree). Consequently the
zero covector lies in the subdifferential `∂C(0, 0)`: the `γ`-slice range
`[-224 − Σ τ(OD) − 9, −224 + Σ τ(OD) + 9]` contains 0, and every `δ_{ij}`-slice
admits signs making the directional derivative vanish precisely because the
displayed slack is at least 4. Convexity therefore makes the diagonal a **global
minimizer**, so

```
C(γ, δ)  ≥  224
```

for every exact named-class fit of `I`. In particular the expand-and-net
reduction is cost-preserving: `224 = Cost(R(F)) ≤ Cost(F)`.

## Universal J-free floor

[#3643](https://github.com/CrocSwap/integer-mult-bounds/pull/3643) already gives
`Cost(F) ≥ 45` whenever `F` is J-free after netting. Every named-class exact fit
`F` of `I` admits a J-free rewrite `R(F)` of no greater tariff, so

```
Cost(F)  ≥  Cost(R(F))  ≥  45.
```

Thus the J-free floor applies universally inside `{D, J, OD, P}` for exact fits
of `I`; one need not stop at the one-J bound `561/16`. The same argument shows
the sharp named-class optimum on `I` is exactly 224 (attained by the diagonal,
and also by some J-free Gram-supported equality-pair rewrites of cost 224).

## Discriminating fixtures

| Fixture | Net J | Pre-cost | Post-cost |
|---|---:|---:|---:|
| Diagonal | 0 | 224 | 224 |
| J-identity extension | 1 | 16097 | 224 |
| Signed Gram extension | 1 | 47257 | 224 |
| Padded `+J − J` | 0 after netting | 242 | 224 |

## Limits

No new global decoder floor outside named classes, no supplier, no native
program, no dirty restoration, no selected-frontier update and no new kappa.
Selected κ stays `0.001672660197076918`. The #3643 domination census and the
`561/16` one-J arithmetic are cited, not recomputed. Local cost-20 theorems are
granted, not replayed. The reduction is proved for exact fits of `I_112`; a
general strict-fit target with free orthogonal off-diagonals is left open.
