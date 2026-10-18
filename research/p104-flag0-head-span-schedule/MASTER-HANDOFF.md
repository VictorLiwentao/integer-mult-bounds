# Master handoff — `research/p104-flag0-head-span-schedule/`

## Candidate

- Branch: `cursor/flag0-head-span-schedule-60b9` (VictorLiwentao fork).
- Content tip: `c1ea52be05e21bb8efad20e7474fe417323e0e3e`. This is the
  scientific package commit. Its parent is the pinned base.
- Packaging tip: `ec6509890dda563bda82088f14f2d24586d89388` (adds only this handoff + test/VERIFY alignment).
- Package: `research/p104-flag0-head-span-schedule/`
- Base: CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged at `0.001672660197076918`
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`, with no
  `Co-authored-by: Victor Li` trailer (`git -c core.hooksPath=/dev/null commit`).
- **Do not open a CrocSwap PR** — master publishes.

## Claim

On present-head flag 0 (`X0` → `Y34`, head `232`), event 3369 (`Y34 += D23/4`)
settles `Y34`'s final `X0` coefficient (`+1/2` after the 2815/2998 cancel). Two
changed schedules make that ADD co-host the head while `X0` sits in its rank-9
chart and still has four later reads. The published `check_native.validate()`
passes unchanged on both. That covers all native edges (six newly lowered), 208
adapters, 280 framed rows and 72 dirty-helper restorations.

| | Events | ADDs | Transports | Rank mass | Profile delta | Surcharge on |
|---|---:|---:|---:|---:|---|---|
| R0 (order-preserving) | +1 | 0 | +1 | +2 | `-H1 + 3H2 - H3` | `D23` |
| R1 (relocated into `D23`'s full window) | 0 | 0 | 0 | +2 | `-H3 + H5` | `Y34` |

Under an affine price the extra cost is `a + 2b` for R0 and `2b` for R1, so it is
positive. Neither repair prices the published `I−G/2` tail add at event 5759;
the bill is the channel-prefix surcharge ahead of that cut.

**Obstruction.** All 280 non-private registers are at their rank floor, and the
excess over the floor is always even.

- The #3508 head closure blocks all fifteen `Y34` updates. For 3369 the first
  obstruction is `Y33` at 3438.
- The exact least-frame sweep (with the private register `C` relaxed, so the
  verdicts are sound) says zero added non-private mass is infeasible for all
  fifteen order-preserving updates.
- It is also infeasible for 926 of 1,113 relocation slots of the settling ADD,
  namely every slot before `Y33`'s read at 3438.

So +2 is the floor there, and R0 is mass-optimal among order-preserving
repairs. The 187 later slots are relaxed-feasible and left open.

## Why this is not a chronology reprint

The headline is two constructed repaired words, their native validation, their
exact bill and a zero-mass obstruction. #3669's drop/arrive/head-free chronology
is cited, not re-derived. The only published fact rechecked is "no `Y34` update
hosts the head", which the before/after comparison needs. This answers #3669
OQ1.

## Evidence commands

```sh
python3.12 -I -B research/p104-flag0-head-span-schedule/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-head-span-schedule/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-head-span-schedule/independent.py
python3.12 -I -O -Werror -B research/p104-flag0-head-span-schedule/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag0-head-span-schedule
```

Expected markers:

```text
PASS_P104_FLAG0_HEAD_SPAN_SCHEDULE flag=0 head=232 delivering_update=3369 R0=order_preserving added_events=1 added_adds=0 added_transports=1 added_rank_mass=2 profile_delta=-H1+3H2-H3 R1=relocated added_events=0 added_transports=0 added_rank_mass=2 profile_delta=-H3+H5 native_validate=PASS zero_mass_order_preserving=0/15 zero_mass_relocation_obstructed=926/1113 no_new_kappa
PASS_P104_FLAG0_HEAD_SPAN_SCHEDULE_INDEPENDENT flag=0 head=232 delivering_update=3369 R0 added_events=1 added_transports=1 added_rank_mass=2 R1 added_events=0 added_transports=0 added_rank_mass=2 rows_equal=280/280 zero_mass_order_preserving=0/15 zero_mass_relocation_obstructed=926/1113 no_new_kappa
PASS_P104_FLAG0_HEAD_SPAN_SCHEDULE_TESTS cases=17 clean_read_only=1 scanners=2
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag0-head-span-schedule outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.
Duplicate JSON keys are rejected. On-disk certificate / witness corruption is
rejected in temp copies.

## Soft overlap

| Prior | Relation |
|---|---|
| [#3669](https://github.com/CrocSwap/integer-mult-bounds/pull/3669) flag-0 chronology | **Leave alone.** This answers its OQ1; does not reprint arrive@3500 / 15/15 head-free. Soft method kinship with the flag-1 repair template only. |
| [#3575](https://github.com/CrocSwap/integer-mult-bounds/pull/3575) Q-relay | **Leave alone.** Not recomputed. |
| [#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) flag-1 repair | Method credit; different target (`Y7`/`D17`, 6 updates). Shared source `X0`/head `232`. |
| [#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508) flag-43 repair | Method credit; flag 43 admitted zero-mass; flag 0 does not. |
| Flags 1/9/43 chronologies #3451/#3443/#3456 | Leave alone. |
| Side-correction #3601/#3610/#3614/#3618/#3621 | Leave alone. |
| C5 #3643/#3639; #3421 A=0; groups B–D native | Leave alone. |

## Open questions for master

1. Zero-mass relocation after 3438 (relaxed-feasible window).
2. Which +2 repair wins under actual `H_r`.
3. #3669 OQ2 (tail owner/host at 5758/5759/5807) — not touched.

## Attribution check

```text
git log -1 --format='%an <%ae>%n%B'   # each tip: Wentao Li <wentaol4@illinois.edu>
# no Co-authored-by: Victor Li
# TASK.json ai_assistance: Substantial AI assistance for derivation, implementation, checking and writing.
# README/NOTICE: Prepared by Wentao Li with substantial AI assistance.
```
