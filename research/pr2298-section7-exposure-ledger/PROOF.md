# Proof: §7 nonadjacent exposure chunk-swap ledger

**Scoped exact ledger; no new kappa.**

## Setup

Fix the pinned PR2298 parameters

```text
tau = 99830289 / 10^8,   epsilon = 1/40,
```

and an axis count `d ≥ 1` with adjacent bit-widths in `{ell-1, ell}` (the
mixed `r/2` and `r` domain). By Colkitt's `lem:chunk-swap` / nonadjacent
audit, every completed equal-width interchange of width `w ≤ ell` costs at
most `O(V ell^tau)`, and every one-extra-bit exchange costs at most
`O(V(1+ell^tau))`. We work in units of `V` and charge each exchange at most
the numerical majorant `1 + ell^tau`.

## Composite schedule

The §7 row “Nonadjacent CRT and line exposure” pays:

1. **CRT forward reversal:** `⌊d/2⌋` endpoint exchanges;
2. **CRT inverse reversal:** another `⌊d/2⌋` exchanges;
3. **One Gaussian tensor expose/restore map:** `2(d−1)` exchanges.

Define

```text
M(d) := 2⌊d/2⌋ + 2(d−1).
```

Then the composite schedule uses exactly `M(d)` exchanges. Elementary
arithmetic gives `M(d) ≤ 3d − 2` for every `d ≥ 1`, with equality on every
even `d`.

## Numerical charge

On every mixed pattern of widths in `{3,4}` (so `ell = 4`) at `d ≤ 8`, emit
the composite schedule, count interchanges and bit-moves, and charge

```text
pattern_charge ≤ (#interchanges)·ell^tau + (#bit_moves)·1
               ≤ M(d)·(1 + ell^tau).
```

The second inequality holds because each exchange contributes one
interchange and at most one bit-move. The coarse bound
`M(d)·(1+ell^tau)` is at most the linear majorant `(3d−2)·(1+ell^tau)`.

## Section-7 saving identity

```text
1 − (tau + epsilon·(1−tau)) = (1−tau)·(1−epsilon) = 6618729 / 4000000000,
```

matching the published nonadjacent-exposure saving in
`research/selected-conservative-outer/checks.py` / PROOF §7.

## Asymptotic constant

Under the PR2298 domain `ell ≤ p/(3d)` and `d ≤ p^epsilon`,

```text
M(d)·ell^tau ≤ 3d · (p/(3d))^tau = 3^{1−tau} d^{1−tau} p^tau
             ≤ 3^{1−tau} p^{tau + epsilon·(1−tau)},
```

so the explicit factor `3` (from `M(d) ≤ 3d−2 ≤ 3d`) replaces the
`O(d)` in the manuscript’s `O(V d(1+ell^tau))` while preserving the
published exponent `tau + epsilon·(1−tau)`.

## Limits

Non-adjacent width gaps `|Δw| ≥ 2` are outside this ledger (deferred
gap-`g` work). Decimal evaluation of `ell^tau` is a numerical witness for
the finite `(d,ell)` table, not a rational enclosure. No BIT supplier or
new kappa is claimed.
