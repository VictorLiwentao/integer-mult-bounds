# MASTER-HANDOFF — odd-kernel-alt-tariff-census

## Claim (one sentence)

Under three named alternate ADDRESS physical tariffs (max-height, shared-den
packing, odd-core), every certified odd kernel `q∈{3,5,7,9,15}` fails to
strictly beat the dyadic fused and baseline bills on `j=0..32` (`0` beats;
one max-height baseline tie at `(3,0)` bill `22`), answering #3702 OQ1 without
reprinting the published bit-sum census.

## Closest prior

- #3702 / `research/odd-kernel-coeff-bit-tariff` — bit-sum tariff; OQ1 left open
- #2687 / `research/odd-kernel-query-pair` — exclusion pattern; ADDRESS pin
- PR840 / `research/dyadic-query-pair` — dyadic fusion and ADDRESS shape

## New checkable fact

Three named alternate tariffs, each disagreeing with #3702 bit-sum on all
`|k|∈1..64`; `3×165` fused comparisons with `0` beats; baseline `0` beats and
one locked max-height tie `(q=3,j=0,bill=22)`; max-height/packing
sign-sensitivity documented.

## Evidence commands

```sh
python3.12 -I -B research/odd-kernel-alt-tariff-census/verify.py
python3.12 -I -O -Werror -B research/odd-kernel-alt-tariff-census/verify.py
python3.12 -I -B research/odd-kernel-alt-tariff-census/independent.py
python3.12 -I -B research/odd-kernel-alt-tariff-census/test_package.py
python3.12 -B scripts/research_package.py --package research/odd-kernel-alt-tariff-census
```

## Soft-overlap vs leave-alones

Clear of flag-0 / stock / gate-operand / C5 / side-correction / present-head /
groups B–D. Soft-overlap with #3702/#2687/#2593/PR840 is intentional predecessor
citation (same `address_word` pin; new tariff names and beat/tie census). Does
**not** reprint the bit-sum `165+165` exceedance claim as a new result.

## Attribution

Author Wentao Li `<wentaol4@illinois.edu>`. Neutral AI assistance disclosure.
No `Co-authored-by: Victor Li`. No CrocSwap PR from this worker (master publishes).

## Disposition

Ready for master independent review / publish decision. Kappa unchanged
(`0.001672660197076918`).
