# Flag-0 tail cut admits 47 non-self co-chart hosts with zero dirt and zero endpoint repayment

**Finite co-chart host census on the published #2089 word. No new exponent.**

Open [#3683](https://github.com/CrocSwap/integer-mult-bounds/pull/3683) asks
whether any non-self / copied-host alternative among event-named registers also
achieves zero dirty-helper touches and zero endpoint repayment on the
promote/add/restore at 5758/5759/5807. This package answers yes for that local
cut.

## Result

Among the 48 ADD sources named in the window, every register other than `X0`
holds host chart `FULL` at the ADD, remains `FULL` after restore, has no
destination after the channel prefix, and shares the window's dirt/repay
profile:

| Fact | Value |
|---|---|
| Promote / add / restore | 5758 / 5759 / 5807 |
| Window ADD sources (first-seen) | 48, beginning `X0` |
| Non-self co-chart hosts | **47** (exemplar `X5` → schedule `S_cochart_X5`) |
| All-X co-chart nonself | **103** |
| Dirty-helper touches in the window | **0** |
| Endpoint repay of `X0`/`Y34` / any nonself co-chart host toward initials | **false** |
| Unique source owner among registers named by ADD 5759 alone | still `X0` |

Semantic scope: interpretive co-chart hosts on the published word. Does not
claim vector equality with `X0`, does not rewrite the ADD, and does not build a
dirty-helper copy path.

Selected κ stays `0.001672660197076918`. Leave [#3683](https://github.com/CrocSwap/integer-mult-bounds/pull/3683)
S0, [#3669](https://github.com/CrocSwap/integer-mult-bounds/pull/3669) chronology,
and open [#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) alone.

Details are in [PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag0-tail-copied-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-copied-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-copied-host/independent.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-copied-host/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag0-tail-copied-host
```

`verify.py` is read-only. Admission goes through `need()` and still fires under
`-O`. `independent.py` imports neither `verify.py` nor the native checker.

## Credit

Credit #3683 OQ1 and S0 uniqueness scope, #3669 for the flag-0 chronology that
posed the owner/host question, Cinna Davis / #2089 for the tail word, jwr404's
`p104-tail-flag0-*` readings, #3349 for the unrestored-endpoint census, and the
reviewed #1991 channel. Prepared by Wentao Li with substantial AI assistance.

## Open next questions

1. What is the minimum added host rank mass for a dirty-helper copied-host word
   that routes the 5759 operand through a fresh helper while leaving endpoints
   at channel finals?
2. Can a constructed dirt-restore program under S0 fit inside 5758–5807 without
   enlarging or replacing a published event?

[TASK.json](TASK.json) gives first steps and blockers.
