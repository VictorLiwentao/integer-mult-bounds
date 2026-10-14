# Q8 inverse labels do not compress central-pair bills

**Scoped negative result / recursive bit alphabet; no new kappa.** In formal
`F2[Q8]` with paid labels `x=i`, `x^{-1}=-i`, `y=j`, `y^{-1}=-j` and every
binary rank-one idempotent on two dirty scalar registers, the exact minimum for
each of

- `diag([z],[z])` with `z=xyxy=x^2=y^2=-1`, and
- `diag([xy],[yx])`,

remains **four** paid calls. Adding the two inverse labels enlarges the
generator set from 12 to 24 relative to
[CrocSwap/integer-mult-bounds#1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822)
but does not beat the direct bill.

## Changed hypothesis and complete bill

Keep the quaternion address group and scalar-idempotent call form of #1822:

\[
D_N(g)=I+([g]+1)N,\qquad N=uv^T,\ v^Tu=1,
\]

over formal matrices in `M_2(F2[Q8])`. Free scalar `GL_2(F2)` mixing is
normalized by augmentation (inherited argument; finite conjugation closure is
rechecked). Every register input is arbitrary dirty; every paid call is charged;
no COPY, ERASE, clean ancilla or free address map is provided.

**Changed premise:** paid labels are `{x,x^{-1},y,y^{-1}}` rather than `{x,y}`.
That is the first open alphabet variant named in #1822's open-next list. The
direct attaining words still cost four calls (two squares per active role, or
the ordered `x,y` / `y,x` pair). An inverse-square word
`D(x^{-1})^2` on each idempotent also attains `diag([z],[z])` in four calls.

Acceptance is equality of every coefficient in the full eight-element group
algebra, not equality at one finite address representation.

## Exact evidence

Complete BFS layer expansion with the 24 generators yields

| depth | new states |
| ---: | ---: |
| 0 | 1 |
| 1 | 24 |
| 2 | 358 |
| 3 | 4104 |
| 4 | 29889 |

The depth-3 ball misses both pair targets, so no word of length at most three
exists. Both targets appear at BFS distance exactly four, matching the direct
bill. Layer SHA-256 digests and generator tables are in `CERTIFICATE.json`.

Controls include: exhaustive Q8 laws plus agreement of two independent
multiplications; inverse identities `x x^{-1}=e`, `(x^{-1})^2=z`; the
positive-only 12-generator alphabet as a proper subset; `D_N(g)^2=D_N(g^2)` for
all 24 generators; `GL_2(F2)` (order 6) conjugation closure; known distances
`I` at 0, `diag([x],[e])` and `diag([x^{-1}],[e])` at 1, `diag([z],[e])` at 2;
independent engine-B replay of every witness and direct word; every single-call
omission of each witness; and a mutated-target failure control.

## Reproduce

```sh
python3 -I -O -B research/q8-inverse-labels/verify.py
python3.12 scripts/research_package.py --package research/q8-inverse-labels --check-only
python3.12 scripts/research_package.py --package research/q8-inverse-labels
```

Expected:

```text
PASS_Q8_INVERSE_LABELS diag_z_z_r2:4 diag_xy_yx_r2:4 layers=[1, 24, 358, 4104, 29889] gens=24 no_new_kappa
PASS_PACKAGE_METADATA_AND_PINS research/q8-inverse-labels
PASS_REGISTERED_RESEARCH_PACKAGE research/q8-inverse-labels outcome=negative-result
```

Chooser OS nonce `293ce5a2f3b3bc035f2fbc75e4c8cbfb` selected track `bit-mechanisms`
and card `bit-new-register-model` (scope key `7084092dd726e7ba1f2f`, method:
target-specific relaxation bound). The H2-helper card from the same draw is
deliberately not pursued. Exact base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`.

## Scope and what is not claimed

No kappa, supplier, moment or frontier change. The result is exact only for
this enlarged label set, these two endpoints and `r=2`. Failed search below
length 4 is a statement about the searched domain. Not a proof-assistant
verification. Physical invoices, hosting, precision and analytic transfer are
not invoked. Concurrent UT3/D8, S4/GL3 and positive-label Q8 work is treated as
context, not superseded.

## Open next questions

1. **Three active `z` roles at `r=3` with the inverse-label alphabet.** Direct
   bill 6; ask whether the minimum stays 4. First step: meet-in-the-middle over
   depth-3 balls with the 112 generators; memory cap and layer digests. Blocker:
   state-space growth.
2. **Still larger paid label sets inside `Q8`.** Adding `{+-k,-1}` yields a
   36-generator alphabet at `r=2`. First step: the same depth-3 miss / depth-4
   hit receipts against the two pair targets. Blocker: none technical.

Structured copies live in [TASK.json](TASK.json).

## Credit



## Disposition (2026-10-14)

**Defer upstream publication as a freestanding claim.** Exact inverse-label BFS
is real (`PASS_Q8_INVERSE_LABELS`), and #1822 left this alphabet variant open,
but the minima remain 4 on the same endpoints with the same method. That is an
incremental alphabet census on an open predecessor, not a new useful obstruction
under the donation negative-result bar. Prefer folding into reviewed #1822 or a
harder distinct endpoint (e.g. inverse-label `r=3`).


Prepared by **Wentao Li** with substantial AI assistance; no independent human
review. Apache-2.0. Model and presentation follow
[CrocSwap/integer-mult-bounds#1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822)
and woklerx's
[CrocSwap/integer-mult-bounds#1443](https://github.com/CrocSwap/integer-mult-bounds/pull/1443).
See [NOTICE.md](NOTICE.md) for the full predecessor list. Frozen sources and
`upstream/` are unchanged.
