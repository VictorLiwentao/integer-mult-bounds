# The selected complex high-part exchange needs no external leaf reserve

## Setting and inherited statements

`m = 73` is the selected complex coarse size. The selected-stock proof
(`research/selected-coarse-depth-stock/PROOF.md`) lists ordinary peeled atoms,
routing, adapters and high-part exchanges as separate completed calls, and
gives

```text
S_parent(e,w) = C(w)^D(n) * S_leaf(e,w),
```

with `S_leaf = 1` allowed *if* the full completed ordinary-leaf contract is
available without an external reserve. [#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421)
bound `A = 0` and left `rho` open. A prior citation-only elevation of the
`S_leaf = 1` permission to `rho = 0`, and a later peeled-atom residual
realization on that class alone, were both deferred for weak maintainer need /
soft overlap with the published ordinary fitted fixture.

PR185 names four retained uses of the completed ordinary supplier. This
package realizes a **different** use from the peeled residual:

> High-part exchange and residual digits: ordinary calls with complete bodies
> as spectators (`notes/three-stage-cover-rows.tex`).

The rows note, after the ordinary body wrapper, leaves the stream in order

```text
H_hi, D_body, Z, D_hi, H_body.
```

One inherited ordinary width-`k` interchange of the two high parts, with the
bodies and `Z` as spectators, yields

```text
D_hi, D_body, Z, H_hi, H_body,
```

which is the original full-chunk interchange. The completed ordinary interface
used is the published one in `research/physical-ordinary-interchange`. On a
complete stream `[P][q^e][G][q^e][S]` with `e >= 1` and `P, G, S >= 1`, it
returns the interchange of the two `q^e` fields, keeps the borrowed input
unchanged, restores every spectator pointwise and leaves owned work empty. It
requires no external fresh-row factor. These are inherited statements. This
package does not re-prove them.

## Lemma 1 (exact plan and before/after widths)

Fix high-part width `k >= 1` and body width `b >= 1`. Materialize the
post-wrapper stream with an explicit parent leaf-reserve field of extent
`S_ext >= 1`:

```text
[Pre][S_ext][H_hi][D_body][Z][D_hi][H_body][Post],
```

with `|H_hi| = |D_hi| = 2^k` and `|D_body| = |H_body| = 2^b`. The single call
exchanges `H_hi` with `D_hi`. Its parameters are

```text
P = Pre * S_ext,   G = 2^b * Z,   S = 2^b * Post,
```

and `P * 2^k * G * 2^k * S` equals the node volume. The reserve always
precedes the first active field, so it is a factor of `P` and never an active
field. The endpoint of that one call is the full-chunk order
`D_hi, D_body, Z, H_hi, H_body`.

**Exact costs.** Before (naive full-chunk ordinary on concatenated chunks of
width `k+b`): one ordinary call of active width `k+b`. After (high-part route
on the post-wrapper stream): one ordinary call of active width `k`, with both
bodies complete spectators. The width ratio is exactly `(k+b)/k`. Call count
is exactly `1` for every admissible `(k,b)`. `verify.py` checks the plan on
the `5 x 5` grid `k,b in {1..5}` and records the ratios `2/1 .. 6/1`.

## Theorem (S_leaf = 1 on the high-part exchange class)

Take the selected m=73 complex producer. Assume the completed interface
statement inherited above. Then the high-part exchange of every post-wrapper
stream completes with parent leaf reserve `S_ext = 1`. The call returns with
every prefix coordinate restored, including any reserve the parent does
supply, and with owned work empty. Hence on this leaf-call class the leaf
factor in `S_parent = C(w)^D(n) * S_leaf` is `1`, and

```text
log_q S_leaf(e,w) = 0 <= rho * w * (1 + log2 e)   with rho = 0 for this class.
```

*Proof.* By Lemma 1 the call is an admitted instance `[P][q^k][G][q^k][S]` with
`P, G, S >= 1` whatever `S_ext >= 1` is. The interface has no stock parameter
and requires no external fresh-row factor. So the call completes at
`S_ext = 1` and restores all spectators, the parent reserve among them.
Owned work is empty at return. As `notes/three-stage-cover-rows.tex` says,
successive residuals reuse one reserve and do not multiply reserves.

## Finite evidence

- Elementary branch: 12 runs at `q = 2, 3, 5` with `(k,body)` in
  `{(1,1),(1,2),(2,1)}` and reserve extents 1 and 3. Each checks the
  per-column endpoint, the per-column parent-reserve coordinate, input
  preservation and workspace erasure. Pool peaks are identical at reserve
  extents 1 and 3; only the prefix multiplicity changes. Exact before/after
  widths `k+body` / `k` are recorded on every case.
- Fitted branch: at the C0 boundary, every genuine column returns with its
  parent-reserve coordinate. The padded fresh-row ratio is `12/8 = 3/2` at
  reserve extents 1 and 2, so fresh rows come only from the call's own three
  borrowed high digits. The fitted layout is the high-part exchange signature
  (highs active; bodies and Z spectators), not a peeled pair.

Controls reject a body-swap in place of the high-part swap, unequal high
extents, a reserve-consuming active field, and omitting the high-part call.

## Not claimed

- Global `rho = 0`. Peeled residuals, fixed cover routing, residual digits and
  adapters are other leaf-call classes; peeled was realized separately and
  deferred; routing is not realized here.
- That the selected bootstrap's particular ordinary level `A_(j-1)` is this
  engine.
- A binding of the uniform stock divisor `C(w)` that would fix a numerical
  production `k = ceil(log_q S)`. The class statement holds for every
  admissible `k`, so the missing uniform `C(w)` does not block the
  reserve-independence claim.
- Any change to `A = 0`, `B_bits = 2642`, suppliers, frontier or kappa.
