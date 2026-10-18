# Master handoff — `research/p104-flag9-head-step-repair/`

## Candidate

- Branch: `cursor/p104-flag9-head-step-repair-9fb3` (VictorLiwentao fork). The
  `-9fb3` suffix is this worker's environment-required branch suffix, not
  `-60b9`.
- Content tip: `76523605c52bf1a70c322b2dfb9bc9f34bc527aa`. This is the
  scientific package commit. Its parent is the pinned base.
- Packaging tip: the child commit that adds only this handoff file. Read its SHA
  with `git rev-parse origin/cursor/p104-flag9-head-step-repair-9fb3`.
- Package: `research/p104-flag9-head-step-repair/`
- Base: CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`. #3443 and
  #3508 merged after this pin (in `a27b870`), and #3532 is open on the same
  pin. All three are cited by PR number. No file of theirs is an input.
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged at `0.001672660197076918`
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`, with no co-author
  trailer (both commits were built with `git commit-tree`).

## Claim

On present-head flag 9 (`X4` → `Y23`, head `196`), event 3124 (`Y23 += D28/4`)
is the only `Y23` update that carries `X4`. It brings `-1/2`, the final
coefficient. `X4` spans `196` at every `Y23` update; #3443's event-500 drop is
generator-only.

Two changed schedules make that ADD co-host the head while `X4` sits in its
rank-9 chart with five later reads. The published `check_native.validate()`
passes unchanged on both. That covers all native edges (six newly lowered), 208
adapters, 280 framed rows and 72 dirty-helper restorations.

| | Events | ADDs | Transports | Rank mass | Profile delta | Surcharge on |
|---|---:|---:|---:|---:|---|---|
| R0 (order-preserving) | +1 | 0 | +1 | +2 | `-H1 + 2H2 + H4 - H5` | `D28` |
| R1 (relocated into `D28`'s full window) | 0 | 0 | 0 | +2 | `H7 - H5` | `Y23` |

**Rank-mass floor: +2**, like #3532 and unlike #3508's 0.

- The #3508 head closure blocks all nine `Y23` updates. At 3124 it blocks
  five, namely `D28`'s later readers `Y28`, `Y29`, `Y22`, `Y31` and `Y103`.
- With `C` relaxed (the #3532 model), the least-frame sweep is infeasible for
  9/9 order-preserving updates and for 941 of the 1,114 relocation slots. The
  173 slots after `Y103`'s read at 3462 stay relaxed-feasible.
- With `C` pinned to its published events (new), the sweep is infeasible for
  9/9 and for **1,114/1,114** slots. In the late window, `D28 += C` at 2520 and
  the pinned charts force `D28`'s least frame to rank 6 outside `final(Y23)`.

R0 lies in pinned Z₀ and R1 in pinned Z₁, so +2 is tight in both classes.

## Why this is not a chronology reprint

The headline is two constructed repaired words, their native validation, the
exact bill and a zero-mass floor closed over the whole relocation window in the
pinned class. #3443's drop/arrive events are not restated as a result. The
only published facts rechecked are span-level: no `Y23` update hosts `196`,
while `X4` does at every update. The before/after comparison needs both, and
the second refines #3443's literal drop.

## Evidence commands

```sh
python3.12 -I -B research/p104-flag9-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag9-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag9-head-step-repair/independent.py
python3.12 -I -O -Werror -B research/p104-flag9-head-step-repair/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag9-head-step-repair
```

Expected markers:

```text
PASS_P104_FLAG9_HEAD_STEP_REPAIR flag=9 head=196 delivering_update=3124 R0=order_preserving added_events=1 added_adds=0 added_transports=1 added_rank_mass=2 profile_delta=-H1+2H2+H4-H5 R1=relocated added_events=0 added_transports=0 added_rank_mass=2 profile_delta=-H5+H7 native_validate=PASS zero_mass_order_preserving=0/9 zero_mass_relocation_obstructed_relaxed=941/1114 zero_mass_relocation_obstructed_pinned=1114/1114 rank_mass_floor=2 no_new_kappa
PASS_P104_FLAG9_HEAD_STEP_REPAIR_INDEPENDENT flag=9 head=196 delivering_update=3124 R0 added_events=1 added_transports=1 added_rank_mass=2 R1 added_events=0 added_transports=0 added_rank_mass=2 rows_equal=280/280 zero_mass_order_preserving=0/9 zero_mass_relocation_obstructed_relaxed=941/1114 zero_mass_relocation_obstructed_pinned=1114/1114 no_new_kappa
PASS_P104_FLAG9_HEAD_STEP_REPAIR_TESTS cases=22 clean_read_only=1 scanners=2
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag9-head-step-repair outcome=completed
```

The worker ran all five commands in the working tree, and the tree stayed
byte-identical. It ran them again in a fresh detached worktree of the content
tip, together with `research_package.py --changed-since <base> --check-only`.
Every package JSON file parses with duplicate-key rejection. The test suite
checks the read-only property inside its temp tree.

## Closest priors

- #3532 `p104-flag1-head-step-repair` (open): the closest method prior, giving
  the R0/R1 template, relaxed least-frame sweep and relocation scan. Flag 9
  reproduces its +2 pattern. The pinned model additionally closes the window
  #3532 left open (for flag 9 only). #3532 is left alone.
- #3508 `p104-flag43-head-step-repair`: the splice/assemble/validate harness,
  head-closure rule and bill format. Flag 43 had a zero-cost repair; flag 9
  does not. Left alone.
- #3443 `p104-present-head-flag9-audit`: the chronology prior, cited only. Its
  open question is answered here.
- #3349 (census) and #2981 (matching): cited only.
- #3363: relay census. Only the single `X4` entry delivered into `Y23` at 3124
  is re-reported.

## Soft-overlap risks

- **Code reuse.** Measured as verbatim stripped non-blank lines against the
  union of each prior's `.py` files:
  - against #3532: 647 of 1,104 lines (59%). Per file: `headstep.py` 58%,
    `independent.py` 60%, `verify.py` 38%, `build.py` 72%, `test_package.py`
    71%;
  - against #3508: 48%.

  The shared machinery is factored into a flag-agnostic `headstep.py`, which
  future flag packages can load by path instead of copying. #3532 itself
  could not import it, because it is not on the pin and is a leave-alone.
  `independent.py` deliberately stays a separate copy for scanner
  independence.
- **#3532 turf.** The `C`-pinned sweep is a method that also applies to #3532's
  247 open slots. This package does not run it on flag 1. The application is
  listed as an open question for a separate package.
- **#3443.** The package restates the `Y23` update list and "no published
  `Y23` update hosts the head". It also states the span-level refinement that
  `X4` keeps `196` after event 500, which #3443's limits note anticipated.
- **#3363.** The single coefficient fact (`-1/2` at 3124 via `D28`) is on #3363's
  turf. It is load-bearing for "3124 is the delivering update".
- **Pinned-class wording.** "1,114/1,114 obstructed" holds only when `C`'s
  events are kept. With `C` relaxed, 173 slots stay open. The README and PROOF
  say so, and open question 1 carries it.
- **Flags 0/1/43.** None of them is recomputed. `D28` also appears in #3508's
  flag-43 R0, which retargets `D28`'s 3460 and 3634 transports. R1 here keeps
  published 3634 verbatim, and R0 here touches only 3122 and the drop after
  3124. Composition with #3508's repair is not checked.
- `H_r` is left symbolic.

## Open questions

1. With `C` allowed to re-chart, is there a zero-surcharge relocation after
   3462? Any such repair pays `C`'s own mass.
2. Does the `C`-pinned sweep close flag 1's 247 late slots?
3. Which +2 repair, R0 or R1, is cheaper under the repo's actual per-rank
   weights?

## Disposition note for master

This worker produces a fork branch and package only. Do **not** open a CrocSwap
PR from this worker. Master decides whether to publish or defer after an
independent skeptical review.
