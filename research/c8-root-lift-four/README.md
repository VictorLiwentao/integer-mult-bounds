# C8 root lifting still needs four calls on four involutions

**Scoped exact minimum; no new kappa.** In \(\mathbb F_2[C_8]\) on four registers, with paid factors
\(D_N([g^s])=I+([g^s]+[e])N\) for \(s\in\{1,\ldots,7\}\) and rank-one idempotent \(N\), the diagonal target
\(\operatorname{diag}([g^4],[g^4],[g^4],[g^4])\) has exact minimum **4**. The length-three root-lift
suggested by the rank screen does not exist. The diagonal word of four pure involution calls attains the bound.

The screen that stays open is concrete. Multiplication by \(\varepsilon=[g]+[e]\) has rank 7 and multiplication by \(\varepsilon^4\) has rank 4, so three order-eight calls offer rank budget 21 against four involution blocks of rank 16. [PROOF.md](PROOF.md) closes that gap by the degree-1 and degree-2 augmentations, then a complete reduction of the 399 short label patterns. The degree-4 coefficient that survives is a sum of at most three rank-one matrices.

This answers the higher 2-power half of the question left by `research/bit-c4-root-lift-seedca46bc`. The group order, the target degree, and the valuation-1 layer are different from that \(C_4\) argument. The \(C_4\) package is not edited.

## Cost

| Word | Calls | Status |
|---|---:|---|
| Any product of length at most 3 | ≤3 | excluded, all 399 label patterns |
| \(\prod_{i=1}^4(I+\varepsilon^4 E_{ii})\) | 4 | attains the target |

There is no uncounted register operation in this alphabet. The result does not change κ (`0.001672660197076918` is untouched), and it does not supply a supplier, a frame, or a hosting bill.

## Replay

From the repository root, CPython 3.12:

```sh
python3.12 -I -O -Werror -B research/c8-root-lift-four/verify.py
python3.12 -I -O -Werror -B research/c8-root-lift-four/independent.py
python3.12 -I -O -Werror -B research/c8-root-lift-four/test_controls.py
python3.12 -B scripts/research_package.py --package research/c8-root-lift-four
```

`verify.py` prints `PASS_C8_ROOT_LIFT_FOUR minimum=4 below_four=0 no_new_kappa`. It recomputes the case split and compares [RESULT.json](RESULT.json). It does not write unless `--write` is passed. `independent.py` multiplies all 840 factors, stores the 552,756 length-two products, and checks that none of the 840 left cosets of the target is among them. The two programs do not import each other. Checks are ordinary conditionals, so `-O` does not drop them.

## Sources and credit

Canonical base `bb4bccbf42844d2801487450727c2f63e10d1d0f`, priority revision 6. [SOURCES.json](SOURCES.json) pins the task catalogue, the selected-result record, and the C4 root-lift note as provenance. Nothing in this package reads those files at replay time.

The C4 coefficient obstruction and its four-call diagonal word are the predecessor. This note keeps that alphabet shape and changes the cyclic order. Credit the earlier root-lift argument and the rank-one idempotent alphabet it fixed.

Prepared by Wentao Li with substantial AI assistance.

## Open next questions

Whether \(C_{16}\), or a specified noncommutative extension of this alphabet, admits a three-call word for the same four involution outputs. The valuation gap used here puts pairwise products of valuation-1 labels on degree 4; at target degree 8 those products no longer account for every cross term. No such word is searched here.
