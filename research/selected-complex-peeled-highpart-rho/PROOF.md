# Joint ordinary-leaf rho binding for peeled ∪ high-part (selected m=73)

## Claim

Let the selected m=73 complex stopped producer be the producer that binds the
shared saving and the selected kappa. The retained coarse-depth inventory names
four leaf-call classes:

```text
{peeled atoms, routing, adapters, high-part exchanges}.
```

On this producer, the **peeled** and **high-part** classes are ordinary
completed calls of the published interface in
`research/physical-ordinary-interchange`. This package realizes both classes
through that engine (Binary elementary branch and fitted branch) with parent
leaf reserve extent 1, measures that the Binary/Ordinary adapters take no
external stock argument, and concludes

```text
rho_peeled_highpart = 0.
```

Routing∪adapters remain charged inside the finite scalar/router guard of
`notes/three-stage-cover-complex.tex`; this package names that charge class and
does not phrase-assign measured zeros for it. Selected kappa is unchanged at
`0.001672660197076918`. Cited shape constants `A = 0`, `B_bits = 2642` are not
recomputed.

## Inherited statements

1. **Inventory.** `research/selected-coarse-depth-stock/PROOF.md` states that
   ordinary peeled atoms, routing, adapters and high-part exchanges are
   separate completed calls, and that `S_leaf = 1` is allowed if the completed
   ordinary-leaf contract is available without an external reserve.
2. **Peeled plan.** `notes/stopped-product-interface.tex` pairs the first
   `delta` head atoms with the last `delta` tail atoms in reverse order; each
   pair is one ordinary width-`w` interchange. For `n < 73` the same pairing
   completes `F_n`.
3. **High-part plan.** `notes/three-stage-cover-rows.tex` leaves one ordinary
   width-`k` interchange of the two high parts after the body wrapper, with
   bodies and `Z` as spectators.
4. **Completed interface.** The published engine requires no external
   fresh-row factor; `old_count=P`, depth 0, empty directory. Parent reserve
   may sit in the caller prefix.
5. **Shape.** `#3421` proves `A = 0` with `B = 2642` under finite-stock-as-C.

## Lemma 1 (peeled: S_leaf = 1)

For every `n < 1533` the reverse pairing plan realizes `F_n` with at most 72
calls. In the stream layout with parent reserve preceding every head atom, the
reserve is never an active field. Physical Binary runs at `q ∈ {2,3,5}` with
reserve extents 1 and 3 restore the parent-reserve coordinate on every column
and keep internal pool peaks independent of the reserve extent. Hence the
peeled residual and `n < 73` stopped leaves complete at `S_ext = 1`.

## Lemma 2 (high-part: S_leaf = 1)

On the post-wrapper layout, one high-part swap of `H_hi` with `D_hi` yields the
full-chunk order. Exact before/after widths are `k+body` versus `k`. Physical
Binary runs with reserve extents 1 and 3 restore the parent-reserve coordinate
and keep peaks independent of the reserve. Hence the high-part class completes
at `S_ext = 1`.

## Lemma 3 (adapters close the ordinary leaf path)

AST inspection of the pinned `Binary.run` and `Ordinary.run` methods shows
parameters
`(payload, width|original, prefixes, gap, suffix)` only — no `stock`,
`S_leaf`, or `reserve` argument. Live Binary calls for one peeled pair and one
high-part exchange pass the parent reserve only as a factor of `prefixes`.
Therefore the adapters that execute both classes add no external leaf-reserve
factor.

## Theorem (rho_peeled_highpart = 0)

Under Lemmas 1–3, both remaining ordinary leaf-call classes of the selected
m=73 producer realize `S_leaf = 1` through the published completed ordinary
engine and its stock-free adapters. The external leaf-reserve shape constant
charged by peeled∪highpart is therefore zero:

```text
log_q S_leaf^{peeled∪highpart}(e,w) = 0 = rho_peeled_highpart · w · (1 + log2 e)
with rho_peeled_highpart = 0.
```

Under `#3421`'s `A = 0` and `B = 2642`,

```text
sigma <= (43/26) * (1 - s) * 2642 + rho_routing_adapters,
```

where `rho_routing_adapters` is whatever external leaf reserve (if any) remains
after the finite scalar/router reading of routing∪adapters. This package does
not measure that remainder from a leaf engine.

## What this package does not claim

- It does not recompute `A = 0` or `B_bits = 2642`.
- It does not phrase-assign measured zeros for routing∪adapters.
- It does not substitute historical `57604` or slack `252` for `rho`.
- It does not change selected kappa, suppliers, frontiers, or cutoffs.
