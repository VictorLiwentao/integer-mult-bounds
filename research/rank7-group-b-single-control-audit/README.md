# Group B joint lowering versus losing single-299 control

**Finite independent-moment audit; no new kappa or supplier admission.**

On both #2979 providers, group B's joint five-helper lowering to shared
\(W=\langle 256,128,64,34,17,11,4\rangle\) has guide margin **+42541**, while
the single-299 control on the same twenty-one partner frames loses at
**-58943**. Entrance-relative widths are **7/6/6/6/6**, and the shipped T74
fill places the five helpers **3330** times. Selected κ stays
`0.001672660197076918`.

## Existing coverage

- Marius-Paul Dumitrean / mdumitrean #2979 supplies the joint construction,
  words and `STAGE-PRICES.json`.
- Nick Petalas #2993 / `rank7-joint-frame-audit` recounts all-group frame
  invoices and every V45 endpoint subset; it does not register a group-B
  single-299 control package.
- `rank7-group-a-entrance-audit` binds group A's native widths and single-331
  comparison; group B is outside that package.
- `rank7-group-interactions` certifies disjoint register paths across the
  five groups.

This package closes the still-missing group-B single-change control against
the joint win, with an independent fill-placement join.

## Reproduction

```sh
python3 -I -B research/rank7-group-b-single-control-audit/verify.py
python3 -I -O -B research/rank7-group-b-single-control-audit/verify.py
python3 -I -B research/rank7-group-b-single-control-audit/independent.py
python3 -I -B research/rank7-group-b-single-control-audit/test_package.py
python3 -I -B scripts/research_package.py --package research/rank7-group-b-single-control-audit
```

## Open next questions

1. Do group B's emitted mixed-entrance wrappers and native residual recipes
   match the reconstructed 7/6/6/6/6 widths in both orientations?
2. Does the same single-control loss hold for groups C and D after their
   partner frames are fixed?

## Credit

Builds on #2979 (Dugongue / mdumitrean), Jeremy Kothe's rewrites, Mason Hale /
Jeremy Diviney paired-extraction lineage, Nick Petalas joint-frame and group-A
entrance audits, and Ross Richardson's packing/invoice audits. New check by
Wentao Li. Apache-2.0.
