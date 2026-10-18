# Flag 9's basis head can be co-hosted at its delivering target update for exactly two added rank units

**Finite repaired words with an exact bill, plus a zero-mass obstruction that
covers every relocation slot when the private register keeps its charts. No new
exponent.**

[#3443](https://github.com/CrocSwap/integer-mult-bounds/pull/3443) is the
published obstruction for present-head flag 9 (`X4` → `Y23`, basis head `196`).
Its open question asks whether a changed schedule can co-host `196` on `X4` and
`Y23` long enough to dirty-restore, and at what cost. This package answers it
with the method of [#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508)
(flag 43, zero cost) and open
[#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) (flag 1, +2).
Flag 9 follows flag 1: the floor is two rank units. Unlike flag 1, the floor is
closed over the whole relocation window in the class that keeps the private
register's events.

## Result

Event 3124, `Y23 += D28/4` in chart `[447, 127, 192]`, is the only `Y23` update
that carries `X4`. It brings `-1/2`, which is `Y23`'s final `X4` coefficient.
`D28`'s row is fixed from its write at 2520 until its restoration at 3635, and
`Y23` is never read, so this ADD commutes freely within that window. In span
terms `X4` hosts `196` at all nine `Y23` updates. The event-500 "drop" in
#3443 is generator-only, as its limits note anticipated.

Two repaired words make 3124's ADD co-host the head while `X4` sits in its
rank-9 full chart with five later reads. The published `check_native.validate()`
passes unchanged on both. It covers every native edge, all 208 endpoint adapters
and all 280 framed rows, including the restoration of the 72 dirty helpers.

- **R0 (order-preserving).** `D28` and `Y23` enter `[447, 127, 192, 196]`, the
  published 3124 chart plus the head, at their last transports before 3124
  (3122 and 3123). The ADD runs there. One inserted transport then drops `D28`
  back to `[447, 127, 192]` before `Y28` and `Y29` read it at 3126 and 3128.
  `Y23`'s terminal transport at 3489 starts from the rank-4 chart.
- **R1 (relocation).** `Y23`'s 3123 transport, the ADD and the 3489 transport
  move into `D28`'s full-chart window between 3634 and 3635. `Y23` lifts
  `[447, 127]` to the full chart, takes the ADD there, then drops to its final
  frame. No event is added or removed.

| Bill term | Published | R0 | R1 |
|---|---:|---:|---:|
| Events | 4,058 | 4,059 | 4,058 |
| Scalar ADDs | 2,624 | 2,624 | 2,624 |
| Transport occurrences | 1,410 | 1,411 | 1,410 |
| Rank mass | 2,368 | 2,370 | 2,370 |
| Distinct native edges | 740 | 742 | 741 |
| Where the +2 sits | — | `D28` | `Y23` |
| Paid profile delta | — | `-H1 + 2H2 + H4 - H5` | `H7 - H5` |

Under an affine per-rank price `H(r) = a + b·r`, R0 costs `a + 2b` and R1 costs
`2b`. R1's `H7 - H5` is nonnegative for any nondecreasing `H`. R0's sign is not
fixed: `+2` at `H(r) = r` and `-2` at `H(r) = r²`. Neither repair touches the
private register `C`.

## Obstruction: zero added mass is blocked

All 280 non-private registers sit at their rank floor. With no added
non-private rank mass, every non-private path is therefore monotone. Mass minus
floor is always even, so any nonzero surcharge is at least 2.

- **Head closure (the #3508 rule).** All nine `Y23` updates force the head into
  a register whose final frame excludes it. For 3124 there are five such
  registers (`Y28`, `Y29`, `Y22`, `Y31`, `Y103`, the later readers of `D28`).
- **Exact least-frame sweep, `C` relaxed (the #3532 model).** Infeasible for all
  nine order-preserving updates. Infeasible at 941 of the 1,114 relocation slots
  of the delivering ADD, namely every slot before `Y103`'s read of `D28` at
  3462. The 173 later slots are relaxed-feasible: there the relaxed least frame
  of `D28` is empty.
- **Exact least-frame sweep, `C` pinned (new).** Both repairs keep `C`'s events,
  so `D28 += C` at 2520 forces `D28` to equal `C`'s chart `[383]`, and each
  copy `C := Q_k` forces `Q_k` to equal its chart. With these constraints the
  sweep is infeasible for all nine order-preserving updates and for **all 1,114**
  relocation slots. In the late window the only blocker is `Y23` itself.
  `D28`'s least frame after 3462 has rank 6, and three of its reduced basis
  vectors (139, 75 and 32) lie outside `final(Y23)`.

So +2 is the floor for order-preserving repairs in both models, and for every
relocation of the delivering ADD that keeps `C`'s events. R0 and R1 reach it,
and both lie in those classes. With `C` relaxed, the 173 late slots stay open
(open question 1).

Selected κ stays `0.001672660197076918`. Proof details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag9-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag9-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag9-head-step-repair/independent.py
python3.12 -I -O -Werror -B research/p104-flag9-head-step-repair/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag9-head-step-repair
```

`verify.py` is read-only. It loads the pinned `check_native.py` by path and runs
its `validate()` on each repaired word built in memory. Admission goes through
`need()` and still fires under `-O`. The reusable machinery lives in
`headstep.py`: splicing, recipe assembly, the bill, head closure, and both
least-frame models. It is flag-agnostic, so a later flag package can load it by
path instead of copying it. `independent.py` imports neither `verify.py`,
`headstep.py` nor the native checker. `test_package.py` corrupts temporary
copies, and both scanners must reject all 22 corruptions. `build.py` is the
producer and is not part of the replay.

## Credit

Credit #3443 for flag 9's published present-head chronology. Credit #3508 for
the head-step repair method, the head-closure rule and the bill format. Credit
#3532 for the relaxed least-frame sweep, the relocation scan and the R0/R1
template reused here. Credit #3349 for the present-head census, and Nick
Petalas / #2981 for the flag matching. The witness, checker and compiler come
from the reviewed #1991 native channel (Chafik Boukhalfa). #3363's relay census
records final coefficients; only the single `X4` entry delivered at 3124 is
re-reported here. Prepared by Wentao Li with substantial AI assistance.

## Open next questions

1. If `C` may change its charts, is there a zero-added-mass relocation after
   3462? It would have to re-chart `C`'s 2520 chart `[383]` and pay `C`'s own
   mass, so the question is whether that can ever cost less than 2.
2. Does the `C`-pinned sweep also close flag 1's 247 late slots (#3532 open
   question 1)? Loading `headstep.py` with flag 1's constants answers this in a
   separate package.
3. Which +2 repair is cheaper under the repository's actual per-rank weights?

[TASK.json](TASK.json) gives first steps and blockers.
