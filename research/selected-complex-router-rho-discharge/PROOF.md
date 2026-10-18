# Routing/adapter discharge from external leaf-reserve rho (selected m=73 complex)

## Claim

Let the selected m=73 complex stopped producer be the producer that binds the
shared saving and the selected kappa. The retained coarse-depth inventory
names exactly four leaf-call classes:

```text
{peeled atoms, routing, adapters, high-part exchanges}.
```

On this producer, the **routing** and **adapters** classes are charged only
inside the finite scalar/router guard of the complex cover. Exact before/after
costs for those two classes:

| Quantity | Before (blocking card rho) | After |
|---|---|---|
| Ordinary external leaf calls | unrealized / treated as ordinary obligation | **0** |
| Recursive Fourier children | open | **0** |
| Contribution to shape `rho` | open | **0** |

Finite scalar/router stock is already inside the cited `A = 0`, `B_bits = 2642`
candidate. The remaining ordinary leaf classes that can still force `rho > 0`
are exactly `{peeled, high-part}`. Global `rho` stays open pending those two.
Selected kappa is unchanged at `0.001672660197076918`.

## Source binding

1. **Inventory.** `research/selected-coarse-depth-stock/PROOF.md` states that
   ordinary peeled atoms, routing, adapters and high-part exchanges are
   separate completed calls. This package takes that sentence as the card-level
   leaf-call inventory of size 4.
2. **Complex charge class.** `notes/three-stage-cover-complex.tex` states that
   fixed permutations and signs incur scalar/router charges without recursive
   Fourier children, and that all fixed address adapters, endpoint Paulis and
   invocation permutations are implemented inside the finite scalar/router
   guard of the assembly. Rank-zero adapters reconcile representative
   differences; there are no positive-rank data connectors.
3. **Stock already paid.** `#3421` / `research/selected-stock-shape-a-zero`
   proves `A = 0` with `B_bits = 2642` for the finite-stock-as-C candidate that
   retains those finite role counts. This package cites that shape and does not
   recompute `|Sp(72,2)|`.
4. **Ordinary contrast (BIT).** `notes/three-stage-cover-bit.tex` routes each
   fixed port through a constant number of old width-`O(w)` interchanges.
   `research/stock-routing-factor` records that the constant factor `c_R` is
   unnamed (`named_factor=false`). That ordinary BIT obligation is **not**
   imported into the complex discharge.
5. **Ordinary remainder.** `notes/three-stage-cover-rows.tex` still writes the
   high-part exchange as one inherited ordinary width-`k` interchange. Peeled
   atoms remain ordinary completed calls in the coarse-depth inventory. Both
   stay outside this discharge.

## Composition consequence

Under `#3421`'s `A = 0` and `B = 2642`,

```text
sigma <= (43/26) * (1 - s) * 2642 + rho.
```

Partition the inventory into routing∪adapters versus peeled∪high-part. The
external leaf-reserve shape constant charged by routing∪adapters is zero
because those classes make no ordinary external leaf call and place no
recursive Fourier children (scalar/router only). Write
`rho_peeled_highpart` for any remaining external leaf reserve required by
peeled∪high-part. Then

```text
sigma <= (43/26) * (1 - s) * 2642 + rho_peeled_highpart.
```

This is an inventory accounting identity under the four-class sentence, not a
new analytic decomposition of an unknown fifth class. It does **not** prove
`rho_peeled_highpart = 0` and does not elevate citation-only `S_leaf = 1` to
global `rho = 0`.

## What this package does not claim

- It does not recompute `A = 0` or `B_bits = 2642`.
- It does not realize peeled or high-part through the physical ordinary engine.
- It does not name a BIT routing factor `c_R`.
- It does not substitute historical `57604` or slack `252` for `rho`.
- It does not change selected kappa, suppliers, frontiers, or cutoffs.
