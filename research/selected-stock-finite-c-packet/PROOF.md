# Finite Sp(72,2)×14826 stock as the uniform C(w) packet candidate

## Claim

Let C be the selected m=73 complex assembler's charged per-level stock unit

```text
C = |Sp(72,2)| * P,    P = 14826 = 14336 + 480 + 8 + 2.
```

Under the selected full-cover reading already named by
`research/selected-coarse-depth-stock/PROOF.md` (one fresh complete physical-role
packet per active coarse level; sequential residuals reuse restored stock),
the packet cardinality equals C at every atom width w ≥ 1. Equivalently, the
uniform per-level divisor candidate may be taken as

```text
C(w) := C    for all w >= 1,
```

with bit length `log_2 C = 2642` already bound by #3113 and shape A = 0 already
bound by #3421 under that reading. Leaf reserve rho remains unbound. Selected
kappa is unchanged. Outer-proof adoption of the ledger replacement
`16469 -> 15555` is not claimed.

## Assembler identity

The pinned selected assembler
`research/gauge44-slots-t16/code/assemble.py` builds

```text
group = 2^(36^2) * prod_{j=1..36} (2^(2j) - 1)   # |Sp(72,2)|
stock = group * invoice['physical']
```

and charges

```text
physical_row_coefficient = 2 * bit_length(stock) + 9909 + 252 + 1024.
```

The physical inventory is asserted as
`14336 + R + 8 + 2` with `R` the helper count, summing to `invoice['physical']`.
The stock block contains no atom-width parameter w and no local-ring digit
tower. Recomputing `|Sp(72,2)| * 14826` recovers bit length 2642, matching the
already-bound B_bits.

## Why this is uniform in w

1. **Finite binary cover.** `notes/three-stage-cover-complex.tex` retains full
   finite role counts, specifies group elements by binary matrices, and has no
   `W(w)` or `q^{m^2(w-1)}` lift. Sp→O parameters are `u ∈ U`, `c ∈ F_2`.
2. **Fixed family count.** The selected invoice split
   `14336 + 480 + 8 + 2 = 14826` is an integer partition independent of w.
3. **Zero slope.** For every probed pair of atom widths w1 < w2 the charged
   packet bit length is the constant 2642, so the discrete slope of log_2 C is
   zero. Hence C(w) := C satisfies the uniform-divisor reading at every probed w.

## Coarse residual restore (semantic fixture)

Under the fresh-role splitting and row-restoration contract of the coarse-depth
proof, a coarse node exposes one packet role, passes the unused quotient to a
child, and restores the role before a sequential sibling reuses the same
quotient. The finite fixture executes that contract on a positive w-free
divisor D with two sequential residuals at every row of D^depth, and rejects an
omit-restore mutant. The fixture does not enumerate the full Sp×P domain; the
real packet cardinality C is bound separately by the assembler identity above
and is independently shown w-free.

Ordinary peeled atoms, routing, adapters and high-part exchanges remain
separate completed calls in the coarse-depth proof. This package does not
realize those leaf classes or bind rho.

## Ordinary contrast

The selected BIT producer (#2084) charges a local-ring packet
`W_q(w) = P * |GL_m(F_q)| * q^{m^2(w-1)}` with positive atom-width slope. That
tower is absent from the complex cover and from the selected complex stock
block. The present C(w) := C identification is complex-only.

## What this package does not claim

- It does not recompute A = 0 or B_bits = 2642 as a new contribution.
- It does not bind rho or prove a numerical closed sigma.
- It does not adopt the conditional ledger replacement into the selected receipt.
- It does not change selected kappa, suppliers, frontiers, or cutoffs.
- It does not identify the ordinary BIT m=64 producer with the complex m=73 producer.
