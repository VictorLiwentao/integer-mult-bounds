# Proof: flag-0 head-span schedule at +2 rank mass

## Setup

Pin CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`, the #2981
208-flag matching (`research/p104-joint-unit-flags/CERTIFICATE.json`), and the
reviewed #1991 channel witness
(`research/p104-native-channel/inputs/LOWRANK-WITNESS.json`, 4,058 events).

Open #3669 records that on the published word, present-head flag 0
(`X0` → `Y34`, basis head `232`) never updates `Y34` while both endpoints host
the head in span: the head enters `Y34` only at the terminal transport after-frame
(event 3500), after all fifteen `Y34` adds (last at 3369). Its first open
question asks for a changed schedule that places `232` in `Y34`'s span before
3369 while `X0` is still live, together with the channel bill ahead of the
published `I−G/2` tail add at 5759. This note answers that question. It does not
reprint #3669's chronology.

Labels are vectors in the nine-dimensional binary space. Frames are binary
subspaces; transports are nested; ADDs run in a common chart
(`research/p104-native-channel/PROOF.md` §2). The published native checker
`check_native.validate()` is the acceptance gate for each repaired word.

## Settling update

Exact rational row replay of the published word shows three nonzero `X0` carries
into `Y34`:

| Event | Partner | Carry | Running `X0` coeff |
|---:|---|---:|---:|
| 2815 | `D17` | `+1/2` | `1/2` |
| 2998 | `D13` | `-1/2` | `0` |
| 3369 | `D23` | `+1/2` | `1/2` |

Event 3369 settles the final coefficient. Its published chart is
`[95, 502, 16, 32, 2]` (rank 5), which excludes `232`. `D23` is written at 2511
and restored at 3625; `Y34` is never read. So 3369 commutes inside that window.

## Repair R0 (order-preserving)

Keep every published event in order with the same ADD registers and coefficients.
Change only four sites:

1. Event 3367: `D23` transports `[95, 502, 32, 2] → [95, 502, 16, 32, 2, 232]`
   (rank 2; published rank 1 to the head-free chart).
2. Event 3368: `Y34` transports `[95, 502, 16, 32] → [95, 502, 16, 32, 2, 232]`
   (rank 2; published rank 1).
3. Event 3369: ADD chart becomes `[95, 502, 16, 32, 2, 232]`. Immediately after,
   insert `D23: [95, 502, 16, 32, 2, 232] → [95, 502, 16, 32, 2]` (rank 1), so
   later `D23` readers (starting with `Y33` at 3438) see the published chart.
4. Event 3500: `Y34` terminal starts from the rank-6 chart (rank 2 to the final;
   published rank 3 from the head-free chart).

At 3369, `X0` already sits on the coordinate basis (rank 9) and has four later
reads (3643, 3799, 3851, 3955 after the insert). Both endpoints therefore host
the head at the settling update.

Bill versus published: +1 event, +0 ADDs, +1 transport occurrence, +2 rank mass
(the surcharge sits entirely on `D23`), profile delta `-H1 + 3H2 - H3`, 741
native edges (4 new, 3 dropped). The private register `C` is untouched.

## Repair R1 (relocation)

Delete the published 3368–3369 pair and the 3500 terminal. After `D23`'s lift to
the full chart at 3624, insert:

1. `Y34: [95, 502, 16, 32] → FULL` (rank 5),
2. `Y34 += D23/4` in `FULL`,
3. `Y34: FULL → final(Y34)` (rank 1),

then the published restoration at 3625. No event is added or removed. The
settling ADD lands at index 3623; `X0` still has four later reads and hosts the
head.

Bill versus published: +0 events, +0 ADDs, +0 transport occurrences, +2 rank
mass (the surcharge sits entirely on `Y34`), profile delta `-H3 + H5`, 740
native edges (2 new, 2 dropped). `C` untouched.

## Native validation

For each repair, the package assembles the published recipe set plus the six
committed new-edge recipes in `REPAIR-RECIPES.json` (lowered by the pinned
`compile.py` / `clifford_exact.py`) and runs `check_native.validate()`
unchanged. Both repairs pass: every used edge has a recipe, all 208 endpoint
adapters hold, all 280 framed rows (including 72 dirty-helper restorations)
match, and the independent reduced-basis / exact-rational scanner reports
280/280 final rows equal to the published rows.

## Zero-mass obstruction

All 280 non-private registers sit at their rank floor on the published word, so
any zero-mass non-private path is monotone and any nonzero surcharge is at least
2 by parity.

**Head closure.** Propagate the common-chart obligation forward from each of the
fifteen `Y34` adds, forcing every touched register that does not already span
the head to change. Every update hits at least one register whose final frame
excludes the head. At 3369 the forced set is `{D23, Y34, Y33}` and the single
hard obstruction is `Y33` at 3438.

**Least-frame sweep.** With `C` fully relaxed, force the head into the common
chart of one ADD and take the least monotone frames consistent with every other
ADD. The published word is feasible. Forcing any of the fifteen order-preserving
`Y34` updates is infeasible. Relocating 3369 to any of the 1,113 slots in
`(2511, 3625)` is infeasible at 926 slots (every slot before 3438) and
relaxed-feasible at the remaining 187. R0 therefore meets the parity floor in
the order-preserving class. The package does not claim that every relocation in
the 187-slot window needs +2; R1 is one concrete repair there that still pays +2
on `Y34`.

## Soft overlap

Open #3669 is the published flag-0 chronology; this package answers its schedule
OQ and does not re-audit drop/arrive/head-free counts. #3532 (flag 1) and #3508
(flag 43) supply the repair method; flag 0 shares source `X0`/head `232` with
flag 1 but targets `Y34`/`D23` and has fifteen updates rather than six. Side-
correction bills #3601/#3610/#3614/#3618/#3621, flags 1/9/43 chronologies, #3575
Q-relay, and the tail owner schedule (#3669 OQ2) are untouched.

## Limits

This is a scoped channel-prefix bill for one matched flag. It does not construct
an `I−G/2` side correction, assign an owner to event 5759, price the published
tail add, or claim a new κ. A zero-mass relocation after 3438 remains open. Per-
rank prices `H_r` are left symbolic.
