# Master handoff — `research/p104-flag0-tail-vector-equal-host/`

## Candidate

- Branch: `cursor/flag0-vector-equal-host-60b9` (VictorLiwentao fork).
- Package: `research/p104-flag0-tail-vector-equal-host/`
- Base: CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`
- Card: `p104-side-correction` (changed), priority revision 6
- κ: unchanged at `0.001672660197076918`
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`, with no
  `Co-authored-by: Victor Li` trailer (`git -c core.hooksPath=/dev/null commit`).
- **Do not open a CrocSwap PR** — master publishes.

## Claim

On present-head flag 0, a five-event splice around the published
promote/add/restore window yields dirty-helper host schedule **S_D0**
(`owner=D0`, chart `FULL`): `D0` is vector-equal to `X0` at the ADD; displaced
`D0` dirt is saved into scratch `C` and restored after the window; window length
stays **50** with **zero** in-window dirty-helper touches; `X0`/`Y34` endpoint
repayment toward initials stays false. Exact added cost **+5 events**. Answers
#3683 OQ1 (strong / vector-equal) and the dirt-restore half of #3683 OQ2. No new
kappa.

## Why this is not a leave-alone reprint

- Not interpretive co-chart census (deferred `p104-flag0-tail-copied-host`).
- Not #3683 self-owned S0 on the unspliced word.
- Not #3669 drop/arrive chronology; not #3532 / flag-0 head-span repair template.
- Not stock-envelope / gate-operand / C5 / side-correction leave-alones.

## Evidence commands

```sh
python3.12 -I -B research/p104-flag0-tail-vector-equal-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-vector-equal-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-vector-equal-host/independent.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-vector-equal-host/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag0-tail-vector-equal-host
```

Expected markers:

```text
PASS_P104_FLAG0_TAIL_VECTOR_EQUAL_HOST flag=0 host=D0 added_events=5 window_len=50 dirty_helper_touches=0 vector_equal=1 dirt_restored=1 endpoint_repay=0 no_new_kappa
PASS_P104_FLAG0_TAIL_VECTOR_EQUAL_HOST_INDEPENDENT flag=0 host=D0 added_events=5 window_len=50 dirty_helper_touches=0 vector_equal=1 dirt_restored=1 endpoint_repay=0 no_new_kappa
PASS_P104_FLAG0_TAIL_VECTOR_EQUAL_HOST_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flag0-tail-vector-equal-host outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.
Duplicate JSON keys are rejected. On-disk certificate / witness corruption is
rejected in temp copies.

## Soft overlap

- Soft vs #3683 (leave alone): answers its OQ1-strong / OQ2; reuses the same cut
  as context; new checkable fact is the +5-event vector-equal dirty-helper splice.
- Soft vs deferred `p104-flag0-tail-copied-host`: that package counted co-chart X
  peers without vector equality or dirt construction; this builds the missing
  construction.
- Soft vs #3669 / #3532 / deferred head-span: different cut; not a FLAG_INDEX
  retarget.
- Clear of stock-envelope / finite-C / gate-operand / C5 leave-alones.

## Disposition

Fork branch for master publish decision. Do not open a CrocSwap PR from this
worker.
