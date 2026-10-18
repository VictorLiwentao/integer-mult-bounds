# Handoff: cost-preserving J/P elimination unlocks universal floor 45

## Result

Every exact named-class fit of `I_112` in `{diagonal, J, off-diagonal, pairwise
Gram}` expands into the coordinate `{D, OD}` basis and nets to the diagonal
tariff **224**. Pair-expansion lemma `τ(P)+τ(OD_ij)+τ(OD_ji) ≥ 4` (min slack 4
on 6216 pairs; 436 equalities) puts zero in `∂C` at the diagonal, so 224 is the
global named-class minimum and the rewrite is cost-preserving. Citing #3643's
J-free floor **45** (not recomputed), that floor applies universally inside the
named alphabet. Dual scanners agree. Selected κ unchanged at
`0.001672660197076918`.

Pinned CrocSwap main tip (branch base): `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Scientific geometry base (SOURCES): `463113d675af7410ac91d53a4fed51ec6494eb9a`.
Branch: `cursor/c5-j-free-universal-reduction-60b9`.
Scientific package tip: `aa9ff691f9be20da580a51745758d2a1c718878c` (Wentao-only; no `Co-authored-by: Victor Li`).
Branch tip: this commit on `cursor/c5-j-free-universal-reduction-60b9` (`git rev-parse HEAD`).
Package: `research/c5-j-free-universal-reduction/`.

## Switch

Took #3643's open cost-preserving J-elimination OQ (preferred next). Did not
reprint #3643 named-support domination, floors `45`/`561/16` derivation, or
termwise `180/7`. Left #3639 residual `460>224` alone. Avoided P104
side-correction leave-alones and stock-leaf class-only `S_leaf=1` DEFERs.

## Exact commands (expected PASS)

```sh
python3.12 -I -W error -B research/c5-j-free-universal-reduction/verify.py
# PASS_C5_J_FREE_UNIVERSAL_REDUCTION cycles=23 named_class_opt=224 pair_slack_min=4 j_free_floor=45 universal=true

python3.12 -I -O -W error -B research/c5-j-free-universal-reduction/verify.py
# same marker

python3.12 -I -W error -B research/c5-j-free-universal-reduction/independent.py
# PASS_C5_J_FREE_UNIVERSAL_REDUCTION_INDEPENDENT cycles=23 named_class_opt=224 pair_slack_min=4 j_free_floor=45 universal=true

python3.12 -I -O -W error -B research/c5-j-free-universal-reduction/test_verify.py
# 9 tests OK

python3.12 -W error -B scripts/research_package.py --package research/c5-j-free-universal-reduction
# PASS_REGISTERED_RESEARCH_PACKAGE research/c5-j-free-universal-reduction outcome=completed
```

## Closest priors

- `research/c5-fit-level-cancellation-charge` / #3643 — floors 45 / 561/16;
  leaves this J-elimination OQ (leave-alone; cited only).
- `research/c5-fit-level-residual-charge` / #3639 — residual/local-opt fails
  (leave-alone).
- `research/c5-global-charging-obstruction` / `c5-global-charging-ceiling` —
  termwise `180/7` (leave-alone).

## Soft-overlap risks

- Do not read this as reprinting #3643's domination census or as a thin
  rescaling of `561/16`.
- Named-class optimum 224 on `I` is not a new unconditional decoder floor.
- Reduction proved for exact fits of `I_112`; general strict-fit targets open.
- Leave #3643, #3639, and C5 termwise priors alone.

## What remains open

Does expand-and-net stay cost-preserving for every completed strict fit beyond
`I_112` (free orthogonal off-diagonals)?

## Credit

Nick Petalas, Krzysztof Wójt, #3639, #3643, Tekalign/PR2782, Cinna Davis/PR1825,
Adam Gall/PR1889, thakrarsagar/PR3256, retained matching lineage.

Prepared by Wentao Li `<wentaol4@illinois.edu>` with substantial AI assistance.
No CrocSwap PR opened (donor instruction).
