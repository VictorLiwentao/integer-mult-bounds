# Vector-equal dirty-helper host for flag 0 with outside-window dirt restore

**Finite construction certificate. No new exponent.**

Open [#3683](https://github.com/CrocSwap/integer-mult-bounds/pull/3683) leaves
as OQ1/OQ2 whether a non-self host can be vector-equal (not merely co-chart) and
whether arbitrary dirt can be restored under S0 without enlarging the
promote/add/restore window. This package constructs such a host.

## Result

Splice five events around the published flag-0 window on the #2089 tail:

| Step | Placement | Event | Role |
|---|---|---|---|
| 1–2 | after channel | `zero C FULL`; `copy C ← D0 FULL` | save `D0` dirt |
| 3 | after channel | `copy D0 ← X0 FULL` | vector-equal host |
| — | window (+3) | published 5758/5759/5807 content | length **50**, dirt touches **0** |
| 4–5 | after window | `copy D0 ← C FULL`; `erase C FULL` | restore dirt; discard scratch |

Schedule **S_D0** (`owner=D0`, host chart `FULL`) is then a dirty-helper
vector-equal copied host for the `X0` read at the ADD. Exact added cost
**+5 events**. Window length unchanged. `X0`/`Y34` endpoint repayment toward
initials remains false. Other dirty helpers are untouched by the splice.

Selected κ stays `0.001672660197076918`. Distinct from deferred interpretive
co-chart census `p104-flag0-tail-copied-host` and from #3683's self-owned S0
on the unspliced word.

Details are in [PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag0-tail-vector-equal-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-vector-equal-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-vector-equal-host/independent.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-vector-equal-host/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag0-tail-vector-equal-host
```

`verify.py` is read-only. Admission goes through `need()` and still fires under
`-O`. `independent.py` imports neither `verify.py` nor the native checker.

## Credit

Credit #3683 for OQ1/OQ2, #3669 for the present-head flag-0 chronology,
Cinna Davis / #2089 for the tail word, jwr404's `p104-tail-flag0-*` readings,
#3349 for unrestored endpoints, and the reviewed #1991 channel. Prepared by
Wentao Li with substantial AI assistance.

## Open next questions

1. Can the same +5-event dirty-helper splice be shared across several target
   windows, or must each vector-equal host pay a fresh save/restore?
2. Is there a zero-added-event vector-equal host already present on the
   published word (live-value collision), or is +5 sharp for dirty-helper hosts?

[TASK.json](TASK.json) gives first steps and blockers.
