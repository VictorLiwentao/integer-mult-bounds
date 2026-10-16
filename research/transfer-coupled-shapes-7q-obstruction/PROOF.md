# All transfer-coupled shapes cannot undercut tariff 436 at Q=7

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898). It answers
open question 1 of [#2779](https://github.com/CrocSwap/integer-mult-bounds/pull/2779)
and the remaining-shapes OQ left by the freestanding `(5,1,1)`-only
transfer-coupled package.

No new kappa is claimed. Leave-alone packages through #2779 and the
`(5,1,1)`-only transfer-coupled directory are not edited.

## Setup

A **transfer-coupled dual** of total query count `Q = 7` is a shape `(p,a,b)`
with `p+a+b = 7` and `p,a,b ≥ 1`: shared prefix of length `p` (counted once),
divergent nonempty suffixes of lengths `a` and `b`, walks
`w0 = prefix∥suffix_a` and `w1 = prefix∥suffix_b` (distinct), priced transfer
`C ≥ 1`, and dual even-parity readout with independent dirt.

Fair shared-prefix XOR billing (transfer folded into `X`):

```text
X = (prefix edges once) + C + Σ_{tips} (prefix_end → suffix → 0).
```

Abstract tariff at `(b,a,x)=(38,2,2)`: `38·Q + 2·R + 2·X`.

## Census

Every covering divergent distinct-label schedule was enumerated. Dual cost is
the real `min_a` sum over masks, not a copied constant.

| Shape | Covering | Min R |
|---|---:|---:|
| `(1,1,5)` | 3916416 | 92 |
| `(1,2,4)` | 10416000 | 98 |
| `(1,3,3)` | 7082880 | 100 |
| `(2,1,4)` | 19165440 | 90 |
| `(2,2,3)` | 39997440 | 94 |
| `(3,1,3)` | 37497600 | 88 |
| `(3,2,2)` | 28748160 | 90 |
| `(4,1,2)` | 36664320 | 86 |
| `(5,1,1)` | 8749440 | **84** |

Hence every covering transfer-coupled dual has `R ≥ 84`. Equality only on
`(5,1,1)` (divergent tips; same-suffix walks excluded).

## Binding fair-X floor

On the `R=84` layer of `(5,1,1)`, min fair shared-prefix `X` (with `C=1`) is
`9`, attained e.g. at prefix `(0,1,3,6,12)` with tips `(8,16)`. Therefore

```text
38·7 + 2·84 + 2·9 = 452 > 436.
```

All other shapes have `R ≥ 86`, so even at `X = C = 1`

```text
38·7 + 2·86 + 2·1 = 440 > 436.
```

## Scope limits

- Fixes transfer-coupled duals at total `Q=7` with divergent walks and distinct
  nonzero labels within each walk relative to the shared prefix.
- Does not edit the `(5,1,1)`-only transfer-coupled package; extends it by
  completing the remaining-shape census on a distinct directory.
- Same-walk multi-connector / priced shadow remains #2761 (not edited).
- Partitioned independent walks remain #2779 (not edited).
- Host screens and shared-XOR soft-overlap with #2643 are deferred.
- No new kappa, physical supplier, or multiplication theorem.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| #2779 | Partitioned duals have `R=112` | transfer-coupled OQ |
| `(5,1,1)`-only TC package | Binding shape `R=84`, fair `X≥9`, tariff `452` | — |
| **This** | — | **All nine shapes: global min still `R=84` on `(5,1,1)`; every other shape has `R≥86`** |
