# Line-port unpaid obstruction at ambient dimension 9

**Scoped obstruction and exact dirty toy for `coverage-law-change`. No new κ;
selected frontier untouched.**

Under the stated line-port rank-tracking model, unpaid coordinates per replica
satisfy `U ≤ v(N − d)`. On the selected complex line (`v = 112`, `N = 9`,
`d = 1`) this is `U ≤ 896`. The hosted stock has exactly `W = 896` live
families and one unpaid coordinate each, so the bound is tight. **Two unpaid
coordinates per family (`U = 1792`) cannot be reached by rearranging the
nine-stage template at ambient dimension 9.** Achieving `u = 2` under this
model needs `N − d ≥ 16`.

A separate exact dirty toy (`N = 4`, `d = 2`) shows that a two-unpaid-direction
endpoint contract is legal once ambient dimension permits it. Ideal packing
with `ceiling.ceiling(..., unpaid=2)` on the selected local word still gives
the known `×3.77` lever; that lever is blocked here for line ports at `N = 9`.

## Reproduce

Python 3.12, standard library only:

```sh
python3 -B research/line-port-unpaid-obstruction/verify.py
python3 -I -O -B research/line-port-unpaid-obstruction/verify.py
python3 -B scripts/research_package.py --package research/line-port-unpaid-obstruction
```

Expected:

```text
PASS_LINE_PORT_UNPAID_OBSTRUCTION U_bound=896 u2_blocked=True toy_cols=65536 controls=5 no_new_kappa
```

Read-only replay compares to [RESULT.json](RESULT.json). Pass `--write` only to
regenerate that receipt. Asserts are not admission predicates; `-O` also passes.
Failure controls reject a forged `u = 2` fit at `N = 9`, idle-rank-52 and
local-mass coverage violations, a toy paid-omission, and receipt corruption.

## Evidence map

| Claim | Where |
|---|---|
| Abstract rank lemma and small-domain census | [model.py](model.py), [PROOF.md](PROOF.md) |
| Selected coverage identity `mass = 72W + 64N` | `ASSEMBLY.json` via `verify.py` |
| Unpaid direction is port `q` (`terminal_Y == q` on 112 ports) | pinned `DATA-PHASES.json` member |
| Dirty two-unpaid toy + omission controls | [toy_two_unpaid.py](toy_two_unpaid.py) |
| Packing screens / ideal `unpaid=2` lever | `ceiling.ceiling` + predecessor `RESULT.json` |

## Open next questions

1. **Plane-port decoder cost.** Question: with 112 planes in `F₂⁹` and target
   caps `E_t^⊥`, is there an exact decoder whose copy charge per call is below
   `1472/9 ≈ 163.6`? Why it matters: plane ports leave two unpaid directions at
   fixed `N = 9`, escaping this line-port obstruction. First step: pairing-rank
   lower bound against the break-even (Discussion #1587). Blocked by: active
   plane-port decoder claim on that thread; do not duplicate it.
2. **Bit-side line-port bound.** Question: does the same `U ≤ v(N − d)` counting
   close `u = 2` for the PR589 bit ambient (`m = 64`, copy charge 63)? Why it
   matters: the bit side still caps κ. First step: pin the hosted bit template
   receipts and rerun the bound with `N = 8`, `d = 1`. Blocked by: hosted bit
   template not present as a first-class tree artifact in this checkout.

## Assignment and credit

Chooser nonce `a946c496b01c23f36f2c8de5246cce74`, track `recursive-interfaces`,
card `coverage-law-change`, catalogue scope key `f383d8fc405ee6982cdd`,
priority revision 3. Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Scope
**refined**: independent machine-checked line-port counting obstruction at the
selected ambient dimension, plus a dirty two-unpaid toy and packing screens
(see [TASK.json](TASK.json)).

Predecessor credit: complex local-word ceiling / PR #1240; coverage identity
lineage (#1012 / T37 notes); inherited complex geometry in
`split-centres-global`; Discussion #1587 (ctoth and independent reviewers) for
posing the unpaid-coordinate question and releasing the line-port diagnosis
this package independently formalizes and checks. Plane-port decoder work on
that thread is not consumed.

Prepared by **Wentao Li** ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial **Cursor/Composer**
assistance, under Apache-2.0. No independent human review, Lean formalization,
or selected cold replay is claimed.
