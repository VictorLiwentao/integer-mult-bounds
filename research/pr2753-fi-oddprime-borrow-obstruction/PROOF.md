# Proof sketch: odd-prime Incoming obstruction under borrowed wrapper schedule

## Arithmetic

Let `G = |GL_2(F_3)| = (9-1)(9-3) = 48`. Every positive power `3^k` is odd and,
modulo 16, lands in `{1,3,9,11}`. In particular `3^k` is never divisible by 16,
hence never by 48. Therefore no genuine high-field extent `R = 3^k` is a multiple
of the LowCodes GL order that the PR2753 Node requires of its **padded** row
count (`fresh_rows.quotient`).

## Borrowed fixture inside the volume bound

The outer-wrapper fixture bound is `volume ≤ 60000`. With `q=3`, `n=2`, `w=1`,
`a=9`, the choice `k=3` gives `R=27` and volume `27²·9² = 59049`. Stock `S=24`
yields

```text
R' = ceil(R/S)·S = 48 = G,
```

so the Node admits the padded call, with `added = 21` fabricated rows. This is
the unique `(k,S)` pair in the bounded domain with `R' = G` and `1 ≤ S ≤ R`.

## Model control

At this fixture the wrapper's literal `model_callee` (n atom swaps) completes
the two-call ordinary schedule and the full-chunk interchange on all 59049
Boolean columns. So the fixture itself is legal for the wrapper contract.

## Incoming census

Replace the callee by the source-bound PR2753 `Incoming` with LowCodes `(q,dim,requests)=(3,2,2)`
and identity weights `A=(1,1)`. For each completed F call on the padded layout
(`width = 104976`), compare origins to the mixed-radix unweighted destination
`destination(·, n=2, m=3, weights=(1,1), gap=R, suffix=1)`.

Exact support of mismatches:

| Row class | Rows | Mismatches per row | Total |
|---|---:|---:|---:|
| Genuine good | `{0,…,5}` | 0 | 0 |
| Genuine bad | `{6,…,26}` | 1944 | 40824 |
| Padded | `{27,…,47}` | 0 | 0 |

Identity `21 · 1944 = 40824` and `1944 = 2187 − 243` with `2187 = width/48`.
The wrapper therefore rejects the Incoming endpoint. The same Incoming equals
`F_I` on the **flat** gap-1 padding fixture (identity-weight pad package); the
obstruction is specific to the wrapper's chunked layout with `gap = R` between
atom bodies under borrowed width.

## Scope

This is an obstruction for this source-bound odd-prime program under the
wrapper two-call schedule. It does not admit GL64, change kappa, or claim every
odd-prime Incoming fails.
