# Master handoff — `research/p104-flag1-pinned-late-relocation/`

## Candidate

- Branch: `cursor/flag1-pinned-late-relocation-44d0` (VictorLiwentao fork). The
  `-44d0` suffix is this worker's environment-required branch suffix.
- Content tip: `4c4a853f5fd178e6d650efd9bde0a8219461abaa`. This is the scientific
  package commit, and its parent is the pinned base.
- Packaging tip: the child commit that adds only this handoff file. Read its SHA
  with `git rev-parse origin/cursor/flag1-pinned-late-relocation-44d0`.
- Package: `research/p104-flag1-pinned-late-relocation/`
- Base: CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`. This is the
  same pin as open #3532 and the deferred flag-9 package. #3508 and #3443 merged
  after this pin, and both are cited by number only.
- Card: `p104-side-correction` (refined), priority revision 6.
- κ: unchanged at `0.001672660197076918`.
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`, with no co-author
  trailer. Both commits were built with `git commit-tree`.

## Claim (answers #3532 open question 1 in the `C`-pinned class)

Take the relocations of flag 1's delivering ADD 2797 (`Y7 += D17/4`) that keep
the private register `C`'s published events. #3532's R0 and R1 are both in this
class. Every one of the 1,115 slots is zero-mass-obstructed, including **all 247
slots after 3366** that #3532 leaves relaxed-feasible. So the +2 rank-mass floor
holds over the full relocation window in that class.

| Scan of 1,115 slots | Obstructed | Late slots (after 3366) |
|---|---:|---:|
| `C` relaxed, head forced (#3532's model) | 868 | 0 / 247 |
| `C` pinned, head forced | 1,115 | 247 / 247, blocked only by `final(Y7)` |
| `C` relaxed, head-free | 0 | 0 / 247 |
| `C` pinned, head-free | 458 | 247 / 247; all 429 slots after 3183 |

New checkable facts beyond the count:

- `final(Y7) = ker(61)`. `D17`'s pinned least frame leaves it at the read
  `Y31 += D17` at 3184. After 3366 it is `[395, 75, 32, 18, 6]`, and 32, 18 and 6
  are odd. The late obstruction does not involve the head.
- There is an exact private core K = {2480 `D8 += C` [447], 2482 `D10 += C`
  [447], 2504 `D20 += C` [127], 2511 `D23 += C` [500]}. Pinning any one of the
  four closes all 247 late slots, and pinning the other 36 opens all 247. By
  monotonicity, a set of kept private charts closes the late window if and only
  if it meets K. Each core event has a committed propagation chain to `D17`.

## Why this is not a third flag clone

It builds no repaired word and recomputes no bill, R0/R1 or chronology. The
deliverable is the pinned verdict on #3532's open window, plus the core
characterization, which neither #3532 nor the flag-9 package has. The flag-9
harness is loaded byte-for-byte, with its SHA-256 pinned, rather than copied
with edits. The flag-1 code is constants, a subset-pinned model, a late-window
tally and a chain backtrack.

## Evidence commands

```sh
python3.12 -I -B research/p104-flag1-pinned-late-relocation/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-pinned-late-relocation/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-pinned-late-relocation/independent.py
python3.12 -I -O -Werror -B research/p104-flag1-pinned-late-relocation/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag1-pinned-late-relocation
```

Expected markers:

```text
PASS_P104_FLAG1_PINNED_LATE_RELOCATION flag=1 head=232 delivering_update=2797 partner=D17 window=2497..3613 relaxed_obstructed=868/1115 late_open_in_3532=247 pinned_obstructed=1115/1115 late_pinned_obstructed=247/247 late_blocker=final(Y7) head_free_pinned_obstructed_after_3183=429/429 target_final=ker(61) core=2480,2482,2504,2511 single_core_pin_blocks_late=4/4 release_core_only_opens_late=247/247 rank_mass_floor=2_over_window_for_C_keeping_relocations no_new_kappa
PASS_P104_FLAG1_PINNED_LATE_RELOCATION_INDEPENDENT flag=1 head=232 delivering_update=2797 relaxed_obstructed=868/1115 pinned_obstructed=1115/1115 late_pinned_obstructed=247/247 late_blocker=final(Y7) head_free_pinned_obstructed=458/1115 target_final=ker(61) single_core_pin_blocks_late=4/4 release_core_only_opens_late=247/247 chains=4 no_new_kappa
PASS_P104_FLAG1_PINNED_LATE_RELOCATION_TESTS cases=18 clean_read_only=1 scanners=2
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag1-pinned-late-relocation outcome=completed
```

The worker ran all five commands in a fresh detached worktree of the content
tip, together with `research_package.py --changed-since <base> --check-only`.
The package tree stayed byte-identical. Every package JSON file parses with
duplicate-key rejection. The test suite also checks the read-only property in
its temp tree. Runtimes are about 36 s for `verify.py`, 28 s for
`independent.py` and a few minutes for the test suite.

## Closest priors

- #3532 `p104-flag1-head-step-repair` (open): the same flag, delivering update,
  window and relaxed sweep, plus R0/R1 and the parity floor. All are cited and
  left alone. This package answers its open question 1 in the pinned class only.
- Deferred flag-9 package (fork `a919d1303`): the source of `headstep.py` and
  the pinned model. Its open question 2 is exactly this run. It is not
  re-upstreamed, and no flag-9 fact is restated.
- #3508 (flag 43): the method only, cited.
- #3451 (flag 1 chronology), #3349 and #2981: cited only.

## Soft-overlap risks

- **Vendored harness.** `headstep.py` is a 100% verbatim copy of the deferred
  flag-9 file (349 non-blank lines), and that file is 58% verbatim against
  #3532. This copy is unavoidable while flag 9 is off-base. If master publishes
  a shared harness later, this package should load it from there. Its
  splice/assemble/validate functions are unused here.
- **Package-owned code.** Measured as verbatim stripped non-blank lines in the
  four non-vendored `.py` files (533 lines): 31% against #3532's `.py` union and
  32% against flag 9's. By file, against #3532: `verify.py` 24%,
  `independent.py` 22%, `test_package.py` 57% (test-harness boilerplate),
  `build.py` 50%. Counting the vendored file, the totals are 42% against #3532
  and 59% against flag 9.
- **#3532 turf.** The headline uses #3532's delivering update, window and
  868/247 split, all recomputed only as the frame for the verdict. The +2
  tightness relies on #3532's statement that R0/R1 keep `C`, which is cited and
  not re-validated.
- **Pinned-class wording.** "247/247 obstructed" holds only if `C`'s events are
  kept, and the README, PROOF and marker say so. With `C` relaxed nothing new is
  claimed except the necessary condition (all four of K re-charted).
- **Flag-9 parallel.** The deferred package has the same "late window blocked
  only by the target's final frame" pattern for flag 9. The core
  characterization was not run on flag 9 (open question 2).

## Open questions

1. With `C` re-charting allowed, is there a zero-mass late relocation? It must
   change `C`'s chart at all four of 2480, 2482, 2504 and 2511.
2. Does flag 9's relaxed-open late window have a similar small private core?
3. Which of #3532's +2 repairs is cheaper under the repo's per-rank weights?

## Disposition note for master

This worker produces a fork branch and package only. Do **not** open a CrocSwap
PR from this worker. Master decides whether to publish or defer after an
independent skeptical review. If #3532 is still open at that point, the natural
venue is a comment or follow-up citing it, not a separate flag package.
