# Shape constant rho = 0 for the selected m=73 complex leaf reserve

## Claim

Let S_leaf(e,w) be the inherited leaf-reserve factor in the selected m=73
complex parent formula already written in
`research/selected-coarse-depth-stock/PROOF.md`:

```text
S_parent(e,w) = C(w)^D(n) * S_leaf(e,w).
```

Under the **completed ordinary-leaf interface** already named there (and
instantiated for ordinary BIT by PR #2084 / `selected-bit-parent-reserve`
hypothesis 4), one may take S_leaf = 1. Consequently

```text
log_q S_leaf(e,w) = log_q 1 = 0
```

for every eligible base q > 1, and the shape bound

```text
log_q S_leaf(e,w) <= rho * w * (1 + log2 e)
```

holds for every atom width w >= 1 and every stage width e >= 1 with
**rho = 0**.

The finite-stock constants A and B_bits are **not** recomputed here. Predecessor
#3113 bound B_bits = 2642; the in-flight tip
`research/selected-stock-shape-a-zero` (fork branch
`cursor/selected-stock-a-zero-60b9` @ `eb215c641`) answers A = 0 under the
finite-stock-as-C admission. Substituting those cited values with rho = 0
collapses the retained composition to

```text
sigma <= (43/26) * (1 - s) * 2642.
```

Selected kappa is unchanged. This is not a full outer-proof adoption: the
completed ordinary-leaf interface remains a retained hypothesis, and adopting
finite stock as uniform C(w) remains the physical/compiler admission named by
the coarse-depth proof.

## Why S_leaf = 1 is available for the complex parent

1. **Complex coarse leaves are ordinary completed calls.** The coarse-depth
   proof states that ordinary peeled atoms, routing, adapters and high-part
   exchanges are separate completed calls, and that completed inner ordinary
   calls borrow internally from their supplied chunks, preserve outer
   spectators and restore their row. Their internal stock stays in their
   completed contract; their execution counts do not multiply the parent's
   external stock.
2. **Named permission for S_leaf = 1.** The same proof states: if the full
   completed ordinary-leaf contract is available without an external reserve,
   one may take S_leaf = 1. A nontrivial S_leaf is an explicitly retained extra
   reserve, not a claim that completed leaves require one.
3. **Ordinary completed-leaf contract.** PR #2084 hypothesis 4 (PR185/PR387
   nested row restoration): the previous ordinary algorithm handles all
   required widths and complete spectators, borrows its own high digits
   internally and restores its row coordinate. It needs no additional
   externally supplied row factor. At a leaf there is no external factor.
4. **252 is not S_leaf.** The coarse-depth ledger keeps charging 252 as
   inherited external slack rather than an ordinary-leaf reserve estimate.
   Historical 57,604 and 252 must not be substituted for rho.

## Zero shape constant

With S_leaf = 1 the left-hand side of the shape inequality is identically zero.
For any rho = 0, w >= 1 and e >= 1 the right-hand side
`rho * w * (1 + log2 e)` is also zero when e >= 1 is read with
`log2 e` for e >= 1 (so 1 + log2 1 = 1), hence the inequality holds with
equality at every probed pair. No atom-width or stage-width factor appears in
S_leaf under the completed interface, so the discrete coefficient of
`w*(1+log2 e)` is zero.

## Failure control

If a leaf instead needs an external factor B > 1, the base case becomes
S_leaf = B and log_q B > 0. Then rho = 0 fails the shape inequality at every
(e, w). That is exactly the control named by PR #2084: the zero-external
conclusion is a genuine hypothesis, not something finite examples can infer.

## What this package does not claim

- It does not recompute A = 0 or B_bits = 2642.
- It does not implement or realize the completed ordinary-leaf interface for
  the complex producer.
- It does not treat 252 or 57604 as a selected leaf reserve.
- It does not change selected kappa, suppliers, frontiers, or cutoffs.
- It does not identify the ordinary BIT m=64 producer with the complex m=73
  producer; the ordinary package is cited only for the completed-leaf
  interface that complex coarse leaves invoke.
