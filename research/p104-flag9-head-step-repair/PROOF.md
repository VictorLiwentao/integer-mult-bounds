# Proof: flag-9 head-step repairs, their bill, and the zero-mass floor

## Setup

Pin CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`. Inputs:

- The #2981 flag matching (`research/p104-joint-unit-flags/CERTIFICATE.json`).
  Flag 9 has source 4, target 23 and basis `[196, 8, 3, 4, 16, 96, 256, 1, 32]`.
- The reviewed #1991 witness, recipes and checker in `research/p104-native-channel/`.

All of these are hash-pinned. The channel semantics are those of
`research/p104-native-channel/PROOF.md` §2–§3, as in #3508 and #3532:

- Each register carries a binary frame.
- A transport is nested (up or down) and pays rank `|dim B - dim A|`.
- An ADD or copy needs both registers in the same frame. An ADD changes only
  the destination's row.

A register *hosts* `196` when `196` lies in the GF(2) span of its frame.

#3443 records the published literal frames of `X4` and `Y23`. That chronology is
cited, not re-derived. This package rechecks only two span-level facts it
needs. First, no published `Y23` update hosts the head. Second, `X4` hosts it
at every `Y23` update. The second fact holds because `X4`'s event-500 frame
`[8, 64, 132, 260]` spans `196 = 132 ^ 64`, so the literal drop is
generator-only.

## 1. The delivering update and its commutation window

The rational replay finds that among the nine `Y23` updates (74, 75, 76, 2070,
2160, 2296, 2640, 2826, 3124), only 3124 (`Y23 += D28/4`, chart
`[447, 127, 192]`) carries any `X4` entry. It carries `-1/2`, which is `Y23`'s
final `X4` coefficient. `D28` is the destination of exactly two events: 2520
(`D28 += C`) and 3635 (`D28 += -Q7`). No event reads `Y23`.

So placing the ADD anywhere after 2520 and before 3635 gives the same final rows.
This window has 1,114 slots, counting the published one.

## 2. The repairs

Write `A2 = [447, 127, 192]`, `A3 = A2 + [196]` and `FULL` for the rank-9 chart.
`span(A3)` lies in `final(Y23) = [467, 27, 196, 12, 124, 3, 7, 1]`.

**R0** replaces these published events (later indices shift by one):

| Event | Published | R0 |
|---|---|---|
| 3122 | `D28: [447,192] -> A2`, rank 1 | `D28: [447,192] -> A3`, rank 2 |
| 3123 | `Y23: [447,127] -> A2`, rank 1 | `Y23: [447,127] -> A3`, rank 2 |
| 3124 | `Y23 += D28/4` in `A2` | same ADD in `A3`, then inserted `D28: A3 -> A2`, rank 1 |
| 3489 | `Y23: A2 -> final`, rank 5 | `Y23: A3 -> final`, rank 4 |

`Y23` stays monotone and its mass is unchanged (`1 + 5 = 2 + 4`). `D28` goes up
and back down once, which adds exactly 2. The drop must come before `Y28` reads
`D28` at 3126, because `final(Y28)` excludes the head.

**R1** deletes published 3123, 3124 and 3489. After 3634 (`D28: V6 -> FULL`) it
inserts three events: `Y23: [447,127] -> FULL` (rank 7), `Y23 += D28/4` in
`FULL`, and `Y23: FULL -> final` (rank 1, downward). `Y23`'s last two transports
go from `1 + 5` to `7 + 1`, adding 2. No other register changes, and the event
count is unchanged.

**Native validation.** `verify.py` builds each word in memory. It assembles a
recipe set from two parts: the published recipes for every edge still in use,
and the committed `REPAIR-RECIPES.json` for each of the six new edges (four in
R0, two in R1). It then calls the published `check_native.validate()`
unchanged. That function:

- checks every edge's full Clifford operator, phase included;
- binds every transport to its recipe and rank;
- checks all 208 endpoint adapters;
- runs the framed scalar induction over all 280 inputs.

The induction includes the common-chart rule, the restoration of every source
and dirty helper, and each target's final row and frame. Both words pass.
`independent.py` replays both words with exact rational rows and finds all 280
final rows equal to the published ones.

**Co-hosting.**

- In R0, the ADD at 3124 runs in `A3`, which spans `196`.
- In R1, it runs in `FULL` (new index 3633).
- In both, `X4` is in its rank-9 frame and has five later events. All five are
  reads (`Q_k += ±2·X4` in `FULL`).
- In both, this is the only co-hosted `Y23` update, and it delivers `X4`'s
  `-1/2`.

## 3. The bill

All counts come from the validated words.

| | Events | ADDs | Transports | Rank mass | Edges | Profile delta |
|---|---:|---:|---:|---:|---:|---|
| R0 | +1 | 0 | +1 | +2 | 742 | `-H1 + 2H2 + H4 - H5` |
| R1 | 0 | 0 | 0 | +2 | 741 | `-H5 + H7` |

For affine `H(r) = a + b·r` the deltas are `a + 2b` and `2b`. For nondecreasing
`H`, `H7 - H5 >= 0`. R0's delta equals `H2 + (H2 - H1) - (H5 - H4)`. It is at
most `H2` for convex `H`, and its sign is not fixed: `+2` at `H = r` and `-2` at
`H = r²`. The private register `C` has identical events in all three words.

## 4. The zero-mass obstruction

**Classes.** All classes keep:

- every ADD (same registers and coefficients);
- every endpoint frame.

Transports of non-private registers may be inserted, retargeted or removed
freely.

- **Z₀** keeps the published relative order of all ADDs and copies.
- **Z₁** is Z₀, except that the delivering ADD may sit at any slot of its
  commutation window (§1).
- **Relaxed:** `C`'s events are unconstrained (the #3532 model).
- **Pinned:** `C`'s events are the published ones, frames included. R0 is in
  pinned Z₀ and R1 is in pinned Z₁.

**Parity lemma.** Take a non-private register's nested path from `init` to
`final`. Its mass is `sum |Δ_i|`. This is at least `|sum Δ_i| = rank(final) -
rank(init)` and has the same parity. Equality holds iff the frames grow by
inclusion. All 280 non-private registers meet this floor on the published word
(checked). So a repair that adds no non-private mass has monotone non-private
paths. Any other repair adds an even amount, at least 2. In the pinned class
`C`'s mass is fixed, so total and non-private surcharges agree.

**Least-frame sweep.** Fix a placement and a forced ADD `u`. Walk the events in
order with `L(r) = init(r)`.

- At each ADD between non-private registers `a` and `b`, set both `L(a)` and
  `L(b)` to `L(a) + L(b)`, and at `u` add `196` as well.
- *Relaxed:* skip every ADD or copy involving `C`.
- *Pinned:* at `D_k += C` in chart `c` and at `C := Q_k` in chart `c`, the
  partner must equal `c`. If `L(partner)` is not inside `c`, the placement is
  infeasible. Otherwise set `L(partner) = c`.

By induction, in any monotone solution of the class, each register's frame at
each event contains its `L`. So the final frame must contain the end value of
`L`. If some `L(r)` is not inside `final(r)`, or a pinned chart check fails, no
zero-surcharge repair of that placement co-hosts at `u`. With nothing forced,
the published word passes both models.

**Results** (exact lists are in `CERTIFICATE.json`):

| Placement | Relaxed infeasible | Pinned infeasible |
|---|---|---|
| Z₀, updates 74 / 75 / 76 | 56 each | 91 each |
| Z₀, update 2070 / 2160 / 2296 | 56 / 53 / 43 | 73 / 65 / 46 |
| Z₀, update 2640 / 2826 / 3124 | 23 / 14 / 5 | 23 / 14 / 5 |
| Z₁, slots after 2520–3461 (941) | 27 down to 1, last blocker `Y103` | 39 down to 2 |
| Z₁, slots after 3462–3634 (173) | 0 | 1 (`Y23`) |

#3508's head-closure rule gives the same verdict for all nine Z₀ updates. It
finds 56, 56, 56, 56, 56, 56, 23, 14 and 5 registers whose final frame excludes
the head. For 3124 those are `Y28` (3126), `Y29` (3128), `Y22` (3278), `Y31`
(3387) and `Y103` (3462), `D28`'s later readers.

**Why the pinned late window fails.** After 3462, `D28` has no further reads
before its full lift, and its relaxed least frame is empty. Under pinning,
`D28 += C` at 2520 fixes `D28 ⊇ [383]`. The pinned charts of the other `D_k`
reach `Y22`, `Y31` and `Y103` through their earlier reads, and those frames
flow back into `D28` at 3278, 3387 and 3462. The result is the rank-6 least
frame `(256, 139, 75, 32, 18, 6)`. Its basis vectors 139, 75 and 32 are outside
`final(Y23)`, so `Y23` cannot share `D28`'s frame at any late slot without
leaving its final frame.

**Consequences.**

1. No Z₀ repair with zero added non-private mass co-hosts at any `Y23` update,
   in either model. By parity every co-hosting Z₀ repair adds at least 2, and R0
   adds exactly 2.
2. No pinned Z₁ placement does either, at any of the 1,114 slots. R1 lies in
   pinned Z₁ and adds exactly 2. So +2 is the exact floor over relocations that
   keep `C`'s events.
3. With `C` relaxed, the 941 slots before 3462 are blocked, and no bound is
   claimed for the 173 later slots.

`independent.py` recomputes the closure and both sweeps with separate code. It
replays each relocation slot from the window start.

## Controls

`test_package.py` copies the package and the six pinned inputs into a temporary
tree and runs both scanners there under `-O`. The clean tree must pass and stay
byte-identical. Both scanners must reject all 22 mutations:

- thirteen certificate fields (bill, profile, register mass, co-hosting,
  delivery, source liveness, closure, both sweeps, scan window, scan count, the
  pinned late window, the late partner frame), plus κ;
- a duplicate JSON key, a witness byte flip, and a phase flip in a new recipe;
- R0 without the inserted drop, R0 with only `Y23` lifted, and R1 placed before
  `D28`'s full lift. All three must fail at the common-chart rule.
- an undercharged 3122 transport;
- R1 placed after `D28`'s restoration at 3635, which breaks `Y23`'s final row.

## Limits

This is a statement about finite repaired words for one flag.

- It does not build or price the `I - G/2` side correction or a supplier.
- It does not perform global hosting or precision analysis.
- It does not change κ.

"Co-hosting" means span membership in annotated frames. `H_r` is left symbolic.
The obstruction does not cover:

- reorders of other events;
- changed ADDs or endpoint frames;
- relocations after 3462 that re-chart `C`.

Two separate relaxations are in play. A repair with zero non-private surcharge
that changes `C` is outside the pinned class, and it pays `C`'s own mass.
Whether that mass can be less than 2 is open.
