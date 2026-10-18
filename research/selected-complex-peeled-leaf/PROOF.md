# The selected complex peeled residual needs no external leaf reserve

## Setting and inherited statements

`m = 73` is the selected complex coarse size: a node is internal exactly when
`n >= 73` (`research/selected-coarse-depth-stock/PROOF.md`). The same proof
lists ordinary peeled atoms, routing, adapters and high-part exchanges as
separate completed calls. It gives

```text
S_parent(e,w) = C(w)^D(n) * S_leaf(e,w),
```

with `S_leaf = 1` allowed *if* the full completed ordinary-leaf contract is
available without an external reserve.

The stopped-product note (`notes/stopped-product-interface.tex`) fixes the
residual. For `n = m f + delta`, `0 <= delta < m`, pair the first `delta`
head atoms with the last `delta` tail atoms in reverse order, one retained
ordinary width-`w` interchange per pair. The two remaining contiguous
`m f`-atom intervals get the finite construction. When `n < m`, at most `m`
such calls complete `F_n`. Here `F_n(H,D) = (C_n D, C_n H)` and `C_n`
reverses the `n` atom positions (`research/physical-ordinary-interchange/PROOF.md`).

The completed ordinary interface used is the published one in
`research/physical-ordinary-interchange`. On a complete stream
`[P][q^e][G][q^e][S]` with `e >= 1` and `P, G, S >= 1`, it returns the
interchange of the two `q^e` fields, keeps the borrowed input unchanged,
restores every spectator pointwise and leaves owned work empty. It requires
no external fresh-row factor. The binary adapter extends this to binary
fields, and the fitted branch passes the caller prefix to C0 only as
`old_count=P`, with fresh rows from the padded own high field. These are
inherited statements with their written all-size arguments. This package does
not re-prove them.

## Lemma 1 (exact plan, every n)

Let `delta = n mod 73` for `n >= 73`, and `delta = n` for `n < 73`. The pairs
`(H_i, D_{n-1-i})`, `0 <= i < delta`, are pairwise disjoint. They avoid the
intervals `H_delta..H_{n-1}` and `D_0..D_{n-1-delta}`, and each of those
intervals has `n - delta = 73 f` atoms. Exchanging each pair and applying
`F_{73f}` to the two intervals gives `F_n`.

*Proof.* The head indices `i < delta` and tail indices `n-1-i >= n-delta` are
distinct across pairs, and they fall outside the two intervals by the index
ranges. After exchange, the new `H_i` is the old `D_{n-1-i}` and the new
`D_{n-1-i}` is the old `H_i`. On the intervals, `F_{73f}` sends position
`H_{delta+k}` to `D_{n-1-delta-k}` and back. Both agree with `C_n`, which
sends `H_j` to `D_{n-1-j}`. For `n < 73` there is no interval, and the `n`
pairs give `F_n` directly. The number of calls is `delta <= 72`. `verify.py`
checks this position by position for every `n < 1533`, which covers all 73
residues with `f` from 1 to 20. `independent.py` repeats the check by list
simulation.

## Lemma 2 (call signature)

Write the node stream with arbitrary complete outer spectators and an
explicit parent leaf-reserve field of extent `S_ext >= 1`:

```text
[Pre][S_ext][H_0..H_{n-1}][Z][D_0..D_{n-1}][Post].
```

The call for pair `i` exchanges the fields `H_i` and `D_{n-1-i}`. Its
parameters are therefore

```text
P_i = Pre * S_ext * q^(w i),   G_i = q^(w (n-1-i)) * Z * q^(w (n-1-i)),   S_i = q^(w i) * Post,
```

and `P_i q^w G_i q^w S_i` equals the node volume. In this layout the reserve
always precedes the first active field, so it is a factor of `P_i` and never
an active field. Lemma 2 does not depend on that placement: any layout in
which the reserve is a complete spectator field, in prefix, gap or suffix,
gives the same conclusion below. Since `S_ext` divides `P_i`, the volume
identity holds for every `S_ext >= 1`, and in particular for `S_ext = 1`.

## Theorem (S_leaf = 1 on the peeled residual and stopped leaves)

Take the selected m=73 complex producer. Assume the completed interface
statement inherited above, which is the PR185 contract in the published
engine's form. Then the peeled-atom residual of every coarse node and every
bounded stopped leaf completes with parent leaf reserve `S_ext = 1`. Each of
its calls returns with every prefix coordinate restored, including any
reserve the parent does supply, and with owned work empty. Hence on this
residual class the leaf factor in `S_parent = C(w)^D(n) * S_leaf` is `1`, and

```text
log_q S_leaf(e,w) = 0 <= rho * w * (1 + log2 e)   with rho = 0 for this class.
```

*Proof.* By Lemma 2 each call is an admitted instance `[P_i][q^w][G_i][q^w][S_i]`
with `P_i, G_i, S_i >= 1` whatever `S_ext >= 1` is. The interface has no
stock parameter and requires no external fresh-row factor. So each call
completes at `S_ext = 1` and restores all spectators, the parent reserve
among them. Because owned work is empty at each return, the next call starts
from the same fixed inventory. As `notes/three-stage-cover-rows.tex` says,
successive residuals reuse one reserve and do not multiply reserves. By
Lemma 1 the `delta <= 72` calls realize the residual part of `F_n`.

Radix-`q` padding inside the binary adapter is owned scratch of volume below
`q^2` times the call volume. It is erased before return and is not a row
field supplied by the parent.

## Finite evidence (what the executions add)

The theorem is conditional on the inherited interface. The executions check
that the complex residual's calls really are instances of that interface and
that the reserve-independence holds on the published code:

- Elementary branch: 12 runs at `q = 2, 3, 5`. Each checks the per-column
  endpoint, the per-column parent-reserve coordinate at every call return,
  input preservation and workspace erasure. Pool peaks are identical at
  reserve extents 1 and 3, and only the prefix multiplicity changes.
- Fitted branch: at the C0 boundary, every genuine column returns with its
  parent-reserve coordinate. The padded fresh-row ratio is `12/8 = 3/2` at
  reserve extents 1 and 2, so fresh rows come only from the call's own three
  borrowed high digits.

Both mutations that put the reserve into play are rejected. Making the
reserve an active field fails the reserve-coordinate check. Using the
ordinary `m = 64` histogram changes the residual plan.

## Not claimed

- Global `rho = 0`. Routing, high-part exchange, residual digits and adapters
  are other leaf-call classes, and none is realized here.
- Stage-1 or production-width execution, a new proof of the C0 or borrowing
  arguments, or the finite construction on the `73f` intervals.
- Any change to `A = 0`, `B_bits = 2642`, the finite-stock-as-C admission,
  the 252 or 57,604 allowances, suppliers, frontier or kappa.
