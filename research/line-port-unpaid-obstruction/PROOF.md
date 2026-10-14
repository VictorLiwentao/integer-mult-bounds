# Line-port unpaid-coordinate obstruction

**Scoped counting lemma and exact dirty toy. No new κ.**

## Setup

Fix a line-port local contract with ambient dimension `N`, a distinguished
offset set `Offset` of size `d`, and `v` ports. Each port has `s` live slots.
An ambient coordinate `i ∉ Offset` carries an abstract value matrix on those
`s` slots. Under the model in `model.py`, that matrix starts at rank `s` and
must end at rank `0`. A paid crossing of `i`, or a paid label change of `i`,
changes the rank by at most one. Inert events (bridges, same-side shears,
helpers, centres, monomials that ignore `i`) leave it unchanged.

## Lemma

For each port and each `i ∉ Offset`, at least `s` paid crossings (or paid
label changes) of `i` are required. Summing over ports and non-offset
coordinates produces at least `v · s · (N − d)` such events. In the equality
accounting used by the selected complex stock—one unpaid unit per non-offset
direction per port—the total unpaid count satisfies

\[
U \le v(N-d).
\]

`model.py` checks the rank tracker on every interleaving of length at most
`2s` for `s ≤ 6`, and the bound arithmetic on a bounded `(v,N,d)` domain.

## Selected corollary

On the selected complex line (`v = 112`, `N = 9`, `d = 1`, `s = 8`,
`W = 896` families per replica) the bound is `U ≤ 896`. The coverage identity
`mass = 72W + 64N` (attested on `ASSEMBLY.json`) gives exactly one unpaid
coordinate per live family, so `U = W = 896`: the bound is tight.

Two unpaid coordinates per family would require `U = 1792 > 896`. Therefore
**no rearrangement of the nine-stage template at ambient dimension 9 can
realize `u = 2` under this line-port model**. Achieving `u = 2` needs
`N − d ≥ 16` (for example `N = 18`, `d = 2`).

Independent attestation that the unpaid direction is the port label `q`:
every one of the 112 pinned `DATA-PHASES.json` recipes satisfies
`terminal_Y_translation == q`, matching the inherited geometry
(`C_q` bookkeeping and terminal `X_q` repair in
`INHERITED-COMPLEX-GEOMETRY.txt`).

## Exact dirty toy (`u = 2` directions)

`toy_two_unpaid.py` realizes ambient `N = 4`, unpaid directions `{0,1}`, paid
`{2,3}`, on two slots. The program clears every paid coordinate and never
advances an unpaid coordinate. Exhaustive dirty F2 columns of width 2
(`2^{16}` inputs) meet the endpoint; omitting a paid clear or clearing an
unpaid direction fails. This is a legal replacement identity outside the
selected `N = 9` stock, not a P112 decoder.

## Packing screens

Using `ceiling.ceiling` on the selected local word
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`:

- baseline `unpaid=1` reproduces the predecessor packing ceiling
  `a < 0.001690054109089`;
- ideal `unpaid=2` at the same `m = 73` gives the known lever multiplier
  about `×3.77`;
- an optimistic transplant of that word to `m = 145` (minimum ambient
  `N = 18` under `m = 1 + 8N`) with `unpaid=2` remains favorable as a
  packing relaxation. It is **not** a construction and does not price a
  real larger-ambient decoder.

## Limits

- The counting model is the stated line-port rank tracker, not a theorem
  about every nonlinear or plane-port architecture.
- Plane-port contracts (two unpaid directions at fixed `N = 9`) lie outside
  this obstruction; their decoder cost is a separate open question
  (Discussion #1587).
- Finite toy replay is not a multiplication theorem. The selected frontier
  and cold replay are untouched.
