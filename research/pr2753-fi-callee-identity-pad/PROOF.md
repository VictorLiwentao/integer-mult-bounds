# Proof sketch: identity weights realise wrapper F_I under padding

## Endpoint

PR2753's address endpoint on each frozen prefix is

```text
head_i' = a_i · tail_(n-1-i),
tail_(n-1-i)' = a_i^{-1} · head_i.
```

The outer wrapper's completed unweighted callee requires

```text
F_I(H,D) = (C D, C H),
```

where `C` reverses the `n` atom coordinates. Setting every `a_i = 1` yields
exactly that map. On the GL2(F3) fixture (`n=2`, modulus `3`, `gap=suffix=1`)
the runtime `destination(·,(1,1))` therefore equals the closed-form F_I map
used in this package, and F_I is an involution on each body block.

The published padding integration uses `Incoming(..., (2,1))`. For that
weight vector, `destination(·,(2,1))` differs from F_I on 72 of 81 body
addresses, hence on `49·72 = 3528` genuine columns of the 49-row fixture.
A weighted involution is not a substitute for F_I (wrapper contract).

## Padding composition

`padding.complete` inserts `a = R' - R` zero rows per prefix with
`R' = ceil(R/S)·S`, invokes a row-pointwise completed callee on all `R'`
rows, checks added output bits are zero, and restricts to the original `R`
rows. Under the callee premise that genuine ordinals are preserved and
added rows stay zero, restriction returns the F_I endpoint on genuine
columns. The identity-weight Node satisfies that premise on the fixture
(certificate: 0 F_I mismatches at `R=49`, `S=48`).

## Fitted multiplicity `t > 1`

When `R = t·S` for integer `t ≥ 1`, `plan_rows` completes exactly `t` stock
groups and returns `added = 0`, so `R' = R`. The same identity-weight Node
at `t=2` (`R=96`, `S=48`) matches F_I on all genuine columns. During
`plan_rows`, the implementation closes the group `Counter` before opening
the next, so the live Counter peak is exactly 2 for every exact multiple
`t = 1..16` (instrumented census). This is physical control metadata for
fitted multiplicity, not a `log_q t` coefficient-room corollary.

## Limits

The fixture is one-family GL2(F3), not selected odd-prime GL64. Root
coupling, numerical arenas and fixed-tape placement remain open. No new
kappa.
