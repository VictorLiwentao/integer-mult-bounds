# Proof: PR2298 §3 operation counts on mixed gap-g (non-adjacent) widths

**Scoped exact schedule invoice; no new kappa.**

## Setup

Fix an axis count `d ≥ 1` and bit-widths `{s, s+g}` with gap `g ≥ 2`
(the non-adjacent extension of the mixed `r/2` / `r` domain). An
**exchange** of two axis fields is realized by the multi-bit normal form:

| Widths | Primitives |
|---|---|
| equal `w=w` | one completed interchange |
| long-first `w_i = w_j + g` | one completed interchange, then `g` elementary bit moves |
| long-last `w_j = w_i + g` | `g` elementary bit moves, then one completed interchange |

When `g = 1` this recovers the adjacent one-extra-bit identities of
PR2298 PROOF §3 / #4075. For `g ≥ 2` the same identities iterate once
per excess bit. Absolute `(swap|move)` streams realizing these
primitives are checked against the pinned `physical.move_address`
oracle.

## Reversal

Exchange positions `(k, d−1−k)` for `k = 0, …, ⌊d/2⌋−1`. These pairs are
disjoint, so each uses the multi-bit schedule on the original widths. The
number of exchanges is exactly `⌊d/2⌋`. After these exchanges the width
list is reversed. The total number of bit moves equals the sum of the
per-exchange gaps.

## Tensor map

For each axis `i ∈ {0,…,d−2}`, exchange `i` with the innermost index
`d−1` (expose), then exchange the same pair again (restore). That is
`2` exchanges per non-innermost axis, hence exactly `2(d−1)` exchanges.
Widths return to the input list.

## Gap-g pair invoice

Every exchanged pair with `|w_i − w_j| = g` contributes exactly one
interchange and exactly `g` bit moves. Equal-width pairs contribute one
interchange and zero bit moves.

## Finite census

Every one of the `∑_{d=1}^{6} 2^d = 126` patterns with widths in `{3,5}`
(gap `2`) is emitted and checked. The exchange bounds are attained: at
`d=6` the all-long pattern uses `3` reversal exchanges and `10`
tensor-map exchanges. Physical spot-checks apply the same low-level
`(swap|move)` stream through the pinned oracle and recover the reversed
field coordinates.

## Limitations

This package does not re-derive chunk-swap time coefficients or the
section-7 exposure exponent. It does not reprint the adjacent `{3,4}`
510-row ledger of #4075. No BIT supplier or new kappa is claimed.
