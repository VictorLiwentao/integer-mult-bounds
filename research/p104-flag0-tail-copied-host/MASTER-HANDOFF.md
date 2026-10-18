# Master handoff — `research/p104-flag0-tail-copied-host/`

## Candidate

- Branch: `cursor/flag0-tail-copied-host-60b9` (VictorLiwentao fork).
- Content tip: see `git rev-parse HEAD` after the scientific commit.
- Package: `research/p104-flag0-tail-copied-host/`
- Base: CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`
- Card: `p104-side-correction` (refined), priority revision 6
- κ: unchanged at `0.001672660197076918`
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`, with no
  `Co-authored-by: Victor Li` trailer (`git -c core.hooksPath=/dev/null commit`).
- **Do not open a CrocSwap PR** — master publishes.

## Claim

On present-head flag 0, the published promote/add/restore at 5758/5759/5807
admits **47** non-self co-chart host alternatives among window-named ADD
sources (exemplar `X5` → `S_cochart_X5`): each holds `FULL` at the ADD, remains
`FULL` after restore, has zero post-channel destinations, and shares
`dirty_helper_touches=0` / zero endpoint repayment. ADD-5759 uniqueness of
`X0` is retained. Broader all-X co-chart nonself count is **103**. Answers
#3683 OQ1. No new kappa.

## Why this is not a leave-alone reprint

Headline is a **window-named co-chart census** expanding beyond #3683's
ADD-5759 uniqueness. It does not reprint #3683 S0 as a new claim, does not
reprint #3669 drop/arrive chronology, and does not retarget the #3532/+2
head-span repair template. Semantic scope is interpretive co-chart hosting on
the published word (no vector-equality, no dirty-helper construction).

## Evidence commands

```sh
python3.12 -I -B research/p104-flag0-tail-copied-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-copied-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-copied-host/independent.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-copied-host/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag0-tail-copied-host
```

Expected markers:

```text
PASS_P104_FLAG0_TAIL_COPIED_HOST flag=0 nonself_cochart=47 all_x_cochart_nonself=103 dirty_helper_touches=0 endpoint_repay=0 exemplar=X5 unique_add5759_owner=1 no_new_kappa
PASS_P104_FLAG0_TAIL_COPIED_HOST_INDEPENDENT flag=0 nonself_cochart=47 all_x_cochart_nonself=103 dirty_helper_touches=0 endpoint_repay=0 exemplar=X5 unique_add5759_owner=1 no_new_kappa
PASS_P104_FLAG0_TAIL_COPIED_HOST_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag0-tail-copied-host outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.
Duplicate JSON keys are rejected. On-disk certificate / witness corruption is
rejected in temp copies.

## Soft overlap

- Soft vs #3683 (leave alone): answers OQ1; reuses the same cut and S0
  uniqueness as cited context; new checkable fact is the 47/103 co-chart census.
- Soft vs #3669 (chronology leave-alone): no drop/arrive reprint.
- Soft vs deferred `p104-flag0-head-span-schedule` / #3532: different cut
  (5758/5759/5807 vs 3369 co-host repair); not a FLAG_INDEX retarget.
- Side-correction and present-head chronology leave-alones untouched.

## Disposition

Fork branch for master publish decision. Do not open a CrocSwap PR from this
worker.
