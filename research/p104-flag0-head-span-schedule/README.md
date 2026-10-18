# Flag 0's basis head can be co-hosted at its settling target update for exactly two added rank units

**Finite repaired words with an exact bill, plus a zero-mass obstruction. No new exponent.**

Open [#3669](https://github.com/CrocSwap/integer-mult-bounds/pull/3669) is the
published obstruction for present-head flag 0 (`X0` → `Y34`, basis head `232`).
Its first open question asks whether a changed schedule can put `232` into
`Y34`'s span before the add at event 3369 while `X0` is still live, and what
that adds to the channel bill ahead of event 5759. This package answers that
question with two natively validated repaired words and an exact bill. It cites
#3669's chronology without re-deriving it, and it follows the method of
[#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) (flag-1
repair) / [#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508)
(flag-43 repair). The answer matches flag 1: flag 0 has no zero-cost repair in
the order-preserving class.

## Result

Event 3369, `Y34 += D23/4`, is the settling `Y34` update that carries `X0`. It
brings `+1/2` after the earlier `+1/2` at 2815 is cancelled at 2998, and settles
`Y34`'s final `X0` coefficient. `D23`'s row is fixed from its write at 2511
until its restoration at 3625, and `Y34` is never read. So this ADD commutes
freely within that window.

Two repaired words make 3369's ADD (or its relocated copy) co-host the head
while `X0` sits in its rank-9 full chart with four later reads. The published
`check_native.validate()` passes unchanged on both. It covers every native edge,
all 208 endpoint adapters and all 280 framed rows, including the restoration of
the 72 dirty helpers.

- **R0 (order-preserving).** `D23` and `Y34` enter `[95, 502, 16, 32, 2, 232]`,
  the published 3369 chart plus the head, at their last transports before 3369.
  The ADD runs there. One inserted transport then drops `D23` back to
  `[95, 502, 16, 32, 2]` for its remaining reads, and `Y34`'s terminal transport
  starts from the rank-6 chart.
- **R1 (relocation).** `Y34`'s 3368 transport, the ADD and the 3500 transport
  move into `D23`'s full-chart window between 3624 and 3625. `Y34` lifts
  `[95, 502, 16, 32]` to the full chart, takes the ADD there, then drops to its
  final frame. No event is added or removed.

| Bill term | Published | R0 | R1 |
|---|---:|---:|---:|
| Events | 4,058 | 4,059 | 4,058 |
| Scalar ADDs | 2,624 | 2,624 | 2,624 |
| Transport occurrences | 1,410 | 1,411 | 1,410 |
| Rank mass | 2,368 | 2,370 | 2,370 |
| Distinct native edges | 740 | 741 | 740 |
| Where the +2 sits | — | `D23` | `Y34` |
| Paid profile delta | — | `-H1 + 3H2 - H3` | `-H3 + H5` |

Under an affine per-rank price `H(r) = a + b·r`, R0 costs `a + 2b` (one transport
plus two rank units) and R1 costs `2b`. The extra cost is positive for any
positive affine price. Neither repair touches the private register `C`. Neither
repair reads or prices the published `I−G/2` tail add at event 5759; the bill
above is the channel-prefix surcharge ahead of that cut.

## Obstruction: zero added mass is blocked

All 280 non-private registers sit at their rank floor. With no added
non-private rank mass, every non-private path is therefore monotone. Over a
register's path, mass minus floor is always even. So any nonzero surcharge is at
least 2.

Two independent tests show that zero is impossible in the classes below.

- **Head closure (the #3508 rule).** All fifteen `Y34` updates force the head
  into a register whose final frame excludes it. For 3369 the single obstruction
  is `Y33` at 3438, `D23`'s next read. Flag 43 had one admissible update; flag 0
  has none.
- **Exact least-frame sweep.** For each class, a forward pass computes the
  least monotone frames forced by the common-chart rule plus the head. The
  private register `C` is fully relaxed, so every infeasible verdict is sound.
  - Order-preserving class: infeasible for all fifteen updates.
  - Relocation class (the settling ADD moved to any of its 1,113 legal slots
    between 2511 and 3625): infeasible at 926 slots. That is every slot before
    `Y33`'s read of `D23` at 3438; `Y33` is the last blocker.

Hence R0 is mass-optimal among order-preserving repairs: +2 is the parity floor
and R0 reaches it. In the 187 slots after 3438 the relaxed sweep is feasible, so
this package does **not** exclude a zero-mass relocation there. R1 sits in that
window but still pays +2 on `Y34`.

Selected κ stays `0.001672660197076918`. Proof details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag0-head-span-schedule/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-head-span-schedule/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-head-span-schedule/independent.py
python3.12 -I -O -Werror -B research/p104-flag0-head-span-schedule/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag0-head-span-schedule
```

`verify.py` is read-only. It loads the pinned `check_native.py` by path and runs
its `validate()` on each repaired word built in memory. Admission goes through
`need()` and still fires under `-O`. `independent.py` imports neither `verify.py`
nor the native checker. It uses reduced-basis frames, its own rational replay,
its own head closure and a from-scratch least-frame replay per slot.
`test_package.py` corrupts temporary copies and checks that both scanners reject
all 17 corruptions. Two truncated R0 cascades must fail at the common-chart rule.
Two further controls cover an undercharged transport and R1 moved past `D23`'s
restoration. `build.py` is the producer and is not part of the replay.

## Credit

Credit #3669 for flag 0's published chronology and OQ1, which this package
answers. Credit #3532 and #3508 for the flag-1 / flag-43 repair method and bill
format. Credit #3451/#3443/#3456 for the other present-head chronologies (left
alone), Nick Petalas / #2981 for the flag matching, and the reviewed #1991 native
channel (Chafik Boukhalfa) for the witness, checker and compiler. Prepared by
Wentao Li with substantial AI assistance.

## Open next questions

1. Is there a zero-added-mass co-hosting repair with flag 0's settling ADD
   relocated after 3438?
2. Which +2 repair is cheaper under the repository's actual per-rank weights?
3. Does the published promote/add/restore at 5758/5759/5807 admit an owner/host
   schedule for the `X0` read that restores arbitrary dirt without repaying the
   unrestored channel endpoints? ( #3669 OQ2; not touched here.)

[TASK.json](TASK.json) gives first steps and blockers for each.
