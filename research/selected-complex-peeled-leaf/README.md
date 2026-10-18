# Selected complex peeled residual through the completed ordinary leaf

**Card `selected-stock-envelope`, scope refined** to the leaf-reserve term
`rho` left open by
[`research/selected-stock-envelope-m73`](../selected-stock-envelope-m73/)
(PR [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113), open
question 2) and by the open A=0 package
(PR [#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421)).
PR [#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105) allows
`S_leaf = 1` *if* the completed ordinary-leaf contract is available on the
complex side. This package does not cite that permission as a result. It
realizes the contract on one complex residual class and checks the outcome.

**Result.** Take the selected m=73 complex stopped producer. Its peeled-atom
remainder at every coarse node (`n = 73f + delta`) and its bounded stopped
leaf (`n < 73`) are exactly `delta` (resp. `n`) sequential calls, at most 72,
of the completed ordinary width-`w` interchange in
[`research/physical-ordinary-interchange`](../physical-ordinary-interchange/).
Each call has the signature

```text
(w; P_i, G_i, S_i) = (w;  Pre * S_ext * q^(w i),  q^(w(n-1-i)) * Z * q^(w(n-1-i)),  q^(w i) * Post)
```

The parent's leaf reserve `S_ext` enters only as a factor of the prefix
`P_i`. The engine takes no stock argument, and its fitted branch draws its
fresh rows from its own high field. So the parent can supply `S_ext = 1`.
On this residual class `log_q S_leaf = 0`, giving `rho = 0` for the class.
That is realized and checked here, not assumed. Global `rho` stays open:
routing, high-part exchange and adapter calls are not realized. No new kappa
(selected decimal `0.001672660197076918`).

```sh
python3.12 -I -B research/selected-complex-peeled-leaf/verify.py
```

Expected:

```text
PASS_SELECTED_COMPLEX_PEELED_LEAF m=73 nodes=1533 deltas=73/73 max_calls=72 reserve_active_calls=0 physical_cases=12 controls=4 S_leaf=1_realized_on_peeled_residual no_new_kappa
```

Python 3.12, standard library only, about 5 seconds. Default verify is
read-only. It re-hashes 25 pinned inputs before importing the engine,
including every importable `.py` file and both source archives of
`physical-ordinary-interchange`. It then compares the full typed result with
`CERTIFICATE.json`. Admission uses `need()`, so it is still enforced under
`python -O`.

## What is checked

1. **Plan, every n < 1533 (all 73 residues).** The plan follows the
   source rule in `notes/stopped-product-interface.tex` at the selected
   `m = 73`, which is bound by the
   `research/selected-coarse-depth-stock/PROOF.md` citation. The peeled pairs
   `(H_i, D_{n-1-i})`, `i < delta`, are disjoint and avoid both whole
   `73f`-atom intervals. Composed with the coarse middle reversal they give
   exactly `F_n(H,D) = (C_n D, C_n H)`, where `C_n` reverses atom order. Each
   node needs at most 72 calls, and the reserve is an active field in 0 of
   55,188 calls. PROOF.md gives the all-n argument.
2. **Physical execution, elementary branch.** There are 12 residual runs
   through the unchanged `Binary` adapter over completed elementary native
   backends at `q = 2, 3, 5`. They cover `delta = 1..3` with collapsed coarse
   intervals, plus complete `n = 3` stopped leaves. Each call gets a fresh
   borrowed payload with an explicit parent-reserve field of extent 1 or 3.
   Per-column provenance checks that every output cell comes from the
   expected column, and that the parent-reserve coordinate is restored at
   every call return. The checks also cover input preservation, workspace
   erasure and the composed endpoint (for `n < 73`, the full `F_n`). Pool
   peaks and active extents match between reserve extents 1 and 3.
3. **Physical execution, fitted branch** (`--suite fitted`, about 2 minutes).
   One peeled pair of width 5 runs through the published fitted fixture,
   which borrows 3 high digits of its own field (8 rows, stock 6, padded to
   12). An observer at the C0 boundary checks that C0 returns every genuine
   column with its parent-reserve coordinate. The padded fresh-row ratio is
   `3/2` at reserve extents 1 and 2, so the reserve never feeds the fresh
   rows. The extent-1 shape repeats the predecessor's own `(1,1,1)` fixture
   case. The new parts are the extent-2 run and the C0-level reserve check.
4. **Controls (all rejected).** These are forward pairing
   `H_i <-> D_{n-delta+i}` (fails `F_n`), the ordinary `m = 64` histogram in
   place of 73, a call that makes the reserve an active field (fails the
   reserve-coordinate check), and an omitted residual call (fails the
   endpoint).

`independent.py` does not import the engine or `verify.py`. It rebuilds the
plan by list simulation, recomputes every call signature by slicing, and
recomputes every engine payload hash by a direct digit exchange.

## Why this is not the deferred citation

The deferred `research/selected-stock-rho-zero` tip (`f18dc91d5`) turned
#2105's sentence into `rho = 0` with no complex-side object. This package
names the complex residual, proves its call plan for every `n`, and binds
each call to the published completed interface signature. It runs those calls
with the parent reserve present and absent, and observes reserve-independence
of both the result and the internal resources. Its scope is the one residual
class it executes. It does not cover all leaf calls.

## Reproduce

```sh
python3.12 -I -B research/selected-complex-peeled-leaf/verify.py
python3.12 -I -O -B research/selected-complex-peeled-leaf/verify.py
python3.12 -I -B research/selected-complex-peeled-leaf/independent.py
python3.12 -I -B research/selected-complex-peeled-leaf/test_package.py
python3.12 -I -B research/selected-complex-peeled-leaf/verify.py --suite fitted
python3.12 -B scripts/research_package.py --package research/selected-complex-peeled-leaf
```

`test_package.py` rejects duplicate JSON keys and a temp-corrupted
certificate (normal and `-O`). It also rejects a corrupted physical payload
hash under `-O`, an altered engine pin, an unpinned engine module and a
missing citation. It reruns the controls and checks that replay leaves the
package files unchanged. `--write` regenerates one certificate section.

## Limits

- The physical evidence is finite: small widths, `q = 2, 3, 5` elementary
  backends and the published `q = 2` dimension-2 fitted fixture. It does not
  run at stage-1 widths or at the production large-prime fitted domain.
  The all-size statement comes from PROOF.md together with the
  predecessor's written arguments for the completed interface (C0 endpoint,
  borrowing, cost). Those arguments are inherited, not re-proved.
- In the physical layouts the two `73f`-atom intervals are collapsed to one
  spectator field each. They sit inside the call gap `G`, and the interface
  accepts any `G >= 1`. The finite construction on those intervals (the
  `C(w)^D` part) is not executed.
- Routing, high-part exchange, residual digits and adapters are not realized.
  `A = 0`, `B_bits = 2642` and the finite-stock-as-C admission are untouched.
  The 252 and 57,604 allowances are not substituted.

## Open next questions

1. **Realize the remaining leaf-call classes.** Fixed cover routing and the
   high-part exchange / residual digits are the PR185 uses not covered here.
   Relevance: global `rho = 0` needs all of them. First step: write the
   high-part exchange in `notes/three-stage-cover-rows.tex` as one call
   `(k; P, G, S)` of the same engine and check that the parent reserve lies
   in `P`. Blocked by: the complex cover note does not write its routing as
   ordinary interchanges, and `k` depends on the unadmitted uniform `C(w)`.
2. **Fitted branch at production widths.** Record the C0 `old_count` and
   `fresh_rows` for one peeled pair under the production profile. Blocked
   by: the fitted production domain starts at `e >= 311311` digits, which is
   infeasible to replay on the tape model.

## Credit

Jose Manuel (`jmbarrancoml`) built the completed ordinary engine, together
with Nick Petalas (PR2808), David Arias (PR2753) and the PR2809 lineage it
retains. Aaron Wang (#3113) recorded the missing `rho`. Sricharan Vagvala
(#2105) supplied the parent formula and the conditional `S_leaf = 1`
permission. The PR185 reviewed proof states the completed leaf contract and
its four uses. The stopped-product and cover-rows notes are retained project
sources. Their notices are unchanged.

Prepared by Wentao Li with substantial AI assistance.
