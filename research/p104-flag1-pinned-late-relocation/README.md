# Flag 1's late relocation slots are closed when the private register keeps its charts

**A thin delta to open [#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532):
its 247 open slots are zero-mass-impossible in the `C`-pinned class, and exactly four
private charts carry the obstruction. No repaired word, no new exponent.**

#3532 prices co-hosting flag 1's head (`X0` → `Y7`, head `232`) at +2 rank units,
with two repairs R0 and R1, neither of which touches the private register `C`. Its
relaxed least-frame sweep blocks a zero-mass relocation of the delivering ADD 2797
(`Y7 += D17/4`) at 868 of 1,115 slots. It leaves the 247 slots after `Y103`'s read
of `D17` at 3366 open (its open question 1). This package runs the `C`-pinned
least-frame model from the deferred flag-9 harness (`headstep.py`, loaded
unchanged) on that window. #3532's constructions and bill are cited, not
recomputed.

## Result

| Least-frame scan of 2797's 1,115 slots | Obstructed | Late slots (after 3366) obstructed |
|---|---:|---:|
| `C` relaxed, head forced (#3532's model) | 868 | 0 / 247 |
| `C` pinned, head forced | **1,115** | **247 / 247**, by `final(Y7)` alone |
| `C` relaxed, head-free (ADD only moved) | 0 | 0 / 247 |
| `C` pinned, head-free | 458 | 247 / 247 (all 429 slots after 3183), by `final(Y7)` alone |

- **Floor over the whole window.** Every relocation of the delivering ADD that
  keeps `C`'s published events needs at least +2 non-private rank mass, by the
  parity argument #3532 uses. #3532's R0 and R1 keep `C`, so +2 is tight over all
  1,115 slots in this class, not only over the 868 before 3366.
- **The head is not needed.** `final(Y7)` is the hyperplane
  `{x : popcount(x & 61) even}`. `D17`'s pinned least frame is `[486]` at 2797 and
  `[441, 95]` after 3183, both inside it. The read `Y31 += D17` at 3184 pushes it
  outside. After 3366 it is `[395, 75, 32, 18, 6]`, and 32, 18 and 6 are odd. So
  in the pinned class the delivering ADD cannot even be moved past 3183 at zero
  mass, with or without the head.
- **Four private charts carry it.** Of the 40 private ADD/copy events
  (2462–2523), keeping only one of these four at its published chart already
  closes all 247 late slots. Keeping the other 36 leaves all 247 open.

  | Event | Chart | Path to `D17` |
  |---|---|---|
  | 2480 `D8 += C` | `[447]` | `Y14 += D8` 2552, `Y14 += D5` 2735, `Y31 += D5` 3007, `Y31 += D17` 3184 |
  | 2482 `D10 += C` | `[447]` | `Y31 += D10` 2832, `Y31 += D17` 3184 |
  | 2504 `D20 += C` | `[127]` | `Y31 += D20` 2646, `Y31 += D17` 3184 |
  | 2511 `D23 += C` | `[500]` | `Y59 += D23` 2698, `Y59 += D17` 3364 |

  Each chart is odd against 61. The model is monotone in the set of pinned
  events, so a set of kept private charts closes every late slot **exactly when it
  contains one of the four**. `D17`'s own private chart `[486]` at 2497 is even and
  carries nothing.

What stays open: with `C` free to re-chart, the 247 slots remain relaxed-feasible.
Any zero-mass repair there must change `C`'s common chart at all four events
above. Selected κ stays `0.001672660197076918`. Details are in [PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag1-pinned-late-relocation/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-pinned-late-relocation/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-pinned-late-relocation/independent.py
python3.12 -I -O -Werror -B research/p104-flag1-pinned-late-relocation/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag1-pinned-late-relocation
```

`verify.py` is read-only. It refuses to load `headstep.py` unless its SHA-256
matches the flag-9 harness. It checks the committed headline through `need()`,
which still fires under `-O`, then recomputes everything and requires equality
with `CERTIFICATE.json`. The flag-1 code is about 200 lines: constants, a
subset-pinned model, the late-window tally and the chain backtrack.
`independent.py` imports neither `verify.py` nor `headstep.py`. It reads the
pinned inputs itself, finds the delivering update with its own rational replay,
and replays every slot from scratch with lowest-bit echelon frames. It then
rechecks every verdict and every committed chain link. `test_package.py` corrupts
temporary copies; all 18 corruptions must be rejected. `build.py` is the producer
and is not part of the replay.

## Credit

Credit #3532 for flag 1's delivering update, window, relaxed sweep, R0/R1 and the
+2 parity floor, all cited here. Credit the deferred flag-9 head-step package
(fork commit `a919d1303`, not upstream) for `headstep.py` and the `C`-pinned
least-frame model, reused byte-for-byte. Credit #3508 for the head-step method,
#3451 for flag 1's chronology, #3349 for the present-head census, Nick Petalas /
#2981 for the flag matching, and the reviewed #1991 native channel (Chafik
Boukhalfa) for the witness. Prepared by Wentao Li with substantial AI assistance.

## Open next questions

1. With `C` free to re-chart, is there a zero-mass co-hosting relocation after
   3366? It must change `C`'s chart at 2480, 2482, 2504 and 2511. The first step
   is to ask whether the native framed induction admits charts for those ADDs
   that exclude 447, 447, 127 and 500, and what `C` then pays.
2. Does flag 9's 173 relaxed-open window (after 3462) have the same kind of
   small private core? Run the single-event and released-core tests on its
   constants.
3. Under the repository's per-rank weights, which of #3532's +2 repairs is cheaper?

[TASK.json](TASK.json) gives first steps and blockers.
