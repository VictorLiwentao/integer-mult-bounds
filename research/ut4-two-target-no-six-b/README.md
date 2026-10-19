# No two-target UT4 central word has n_b = 6

**Result.** In the explicit `F2[UT4(F2)]` central-target alphabet of
[CrocSwap/integer-mult-bounds#1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662),
no legal word realizing two central targets — of any finite length, on any
finite restored dirty workspace — has exactly six paid `b` calls. Every such
word therefore has `n_b >= 7`. The case `n_b = 7` is left open.

No new κ. Selected decimal stays `0.001672660197076918`.

This answers the `n_b = 6` half of open next question 2 in
[CrocSwap/integer-mult-bounds#1816](https://github.com/CrocSwap/integer-mult-bounds/pull/1816)
(`research/ut4-two-target-fifteen/`).

## Why it matters

#1662 prices labels separately: `n_a, n_c >= 4` and `n_b >= 6`, while the direct
word `(abcb)^2` per target uses `n_b = 8`. A realizing word with `n_b = 6` and
only modestly larger outer counts would beat the direct word whenever `β` is
large relative to `α+γ`. Ruling out `n_b = 6` at every length is the first
weighted-tariff step; `n_b = 7` remains the next gate.

## Method

[PROOF.md](PROOF.md) records the argument. At `n_b = 6` the middle quotient of
#1662 forces `rank X = rank Y = 2`, so every `b` coupling lies in the active
2-plane. Interior dirty contractions then cannot touch the `{a,b}` / `{c,b}`
side coefficients or the cross coefficients `abc` and `cba`. Those necessary
equations reduce to a two-role profile problem with unrestricted outer length
(every `2 x 2` profile is realizable with enough `a`/`c` calls).

The census (self-contained in `core.py`, formulas matching #1690) enumerates
all 5,582 GL2-minimal zero-sum length-6 middle sequences, keeps the 5,400 with
both middle ranks at least two, builds every side-zero transport key via a 3+3
meet-in-the-middle, and pairs keys for `abc = cba = I_2`. **Zero pairs survive.**
A low-rank control middle still produces pairs, so the screen is not empty by
accident.

| Stage | Count |
|---|---:|
| Canonical zero-sum middles | 5,582 |
| `rank X,Y >= 2` | 5,400 |
| Sum of side-zero key-set sizes | 1,568,064 |
| Key pairs with `abc = cba = I_2` | **0** |

## Evidence

- `verify.py` (read-only, `need()` gates survive `python -O`): source pins;
  corrupted temporary certificate and duplicate JSON key rejection; low-rank
  positive control; full census against `CERTIFICATE.json`.
- `independent.py` does **not** import `verify.py`; it re-runs the census with
  a separate base-16 half-profile MITM and matches the certificate.
- `test_package.py`: isolated `-O` read-only replay, independent import guard,
  certificate pair corruption, duplicate keys, SOURCES sha drift.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/ut4-two-target-no-six-b
# Direct:
python3 -I -B research/ut4-two-target-no-six-b/verify.py
python3 -I -O -B research/ut4-two-target-no-six-b/independent.py
python3 -I -B research/ut4-two-target-no-six-b/test_package.py
```

## Open next questions

1. **Does any two-target word have `n_b = 7`?** Why it matters: finishes the
   first step of #1816 open question 2. First step: run the unrestricted-profile
   key census for length-7 middles on rank patterns `(2,2)`, `(2,3)`, `(3,2)`,
   or find an algebraic obstruction. Blocked by: `16^7` profiles, middle excess
   when a middle rank is 3, and dirty-role structure beyond the `e_b = 0`
   reduction used here.

## Limits

- Decides `n_b = 6` only; `n_b = 7` is explicitly open.
- Does not restate the unit-tariff minimum 16 from #1816; does not reopen
  three-target lengths 21/22.
- Quotient-level obstruction (sufficient for the formal endpoint). No
  proof-assistant or independent human review. No supplier or κ change.

## Credit

#1662 (@ToikY) for the model and `n_b >= 6` bound. #1816 for unit-tariff
exactness and the weighted open question. #1690 (Aaron Wang / @navinor) for
the profile/key pipeline, as used by #1816. #1680 for workspace context.
Prepared by Wentao Li `<wentaol4@illinois.edu>` with substantial AI assistance.
Apache-2.0.
