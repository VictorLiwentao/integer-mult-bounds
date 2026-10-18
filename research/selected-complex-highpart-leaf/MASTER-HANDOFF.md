# Handoff: completed ordinary leaf realized on the selected complex high-part exchange

## Result

The selected m=73 complex producer's high-part-exchange leaf-call class
(`notes/three-stage-cover-rows.tex` after the body wrapper: one ordinary
width-`k` interchange of `H_hi` with `D_hi`, bodies and `Z` as spectators)
completes through the published completed ordinary interchange
(`research/physical-ordinary-interchange`). Exact before/after costs are
recorded: naive full-chunk active width `k+body` versus high-part active
width `k`, call count exactly 1, width ratios `2/1..6/1` on the `5x5` plan
grid. Elementary and fitted branches restore the parent-reserve coordinate
at reserve extents 1 and >1 with unchanged internal resources. So
`S_leaf = 1` holds **on this leaf-call class**, realized rather than cited.
Global `rho` stays open. Selected κ is unchanged at `0.001672660197076918`.

Pinned CrocSwap main: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Branch: `cursor/selected-complex-ordinary-leaf-eb60`.
Content tip: `91e00c51cfdde9b53e58580d64bb72081d64effa` (full package except this
handoff's tip-pin commits; VERIFY budget, Open next questions, and registered
PASS). Injected `Co-authored-by: Victor Li` trailers were stripped with
`git commit-tree`.
Packaging tip: the tip of this branch after this file (`git rev-parse HEAD`).
Package: `research/selected-complex-highpart-leaf`.

## Switch

No card switch. This follows the preferred next46 claim: realize completed
ordinary-leaf on one complex residual, **disjoint** from deferred
`research/selected-complex-peeled-leaf/` (peeled residual) and
`research/selected-stock-rho-zero/` (citation-only). Does not recompute
`A = 0` or `B_bits = 2642` from #3421. Does not continue the P104
side-correction template series.

## Exact commands (expected PASS)

```sh
python3.12 -I -B research/selected-complex-highpart-leaf/verify.py
# PASS_SELECTED_COMPLEX_HIGHPART_LEAF shapes=25 calls=1 active_width=k full_chunk_width=k+body width_ratios=2/1..6/1 physical_cases=12 controls=4 S_leaf=1_realized_on_highpart_exchange no_new_kappa

python3.12 -I -O -B research/selected-complex-highpart-leaf/verify.py

python3.12 -I -B research/selected-complex-highpart-leaf/independent.py
# PASS_SELECTED_COMPLEX_HIGHPART_LEAF_INDEPENDENT shapes=25 calls=1 physical_cases=12 engine_payloads_match

python3.12 -I -B research/selected-complex-highpart-leaf/test_package.py
# PASS_SELECTED_COMPLEX_HIGHPART_LEAF_TESTS groups=6

python3.12 -I -B research/selected-complex-highpart-leaf/verify.py --suite fitted
# PASS_SELECTED_COMPLEX_HIGHPART_LEAF_FITTED cases=2 padded_ratio=3/2 own_rows=8 reserve_extents=1,2 parent_reserve_restored_through_C0

python3.12 -B scripts/research_package.py --package research/selected-complex-highpart-leaf
# PASS_REGISTERED_RESEARCH_PACKAGE research/selected-complex-highpart-leaf outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.
Duplicate JSON keys and on-disk certificate corruption are rejected (temp copies).

## Soft-overlap risks

- Shares `research/physical-ordinary-interchange` with deferred peeled-leaf —
  different call class (high-part vs peeled residual), different layout,
  exact `(k+body)/k` width costs.
- Fitted suite reuses the published reduced fixture machinery (same
  soft-overlap surface that deferred peeled-leaf); novelty is the high-part
  signature (highs active; bodies/Z spectators), not a new fitted engine.
- Does not reprint citation-only `research/selected-stock-rho-zero/`.
- Leave-alones untouched: #3621/#3618/#3614/#3610/#3601/#3532/#3508/#3421.

## Open questions

1. Fixed cover routing still unrealized (complex cover note does not write
   routing as ordinary interchanges).
2. Production-width high-part at `k = ceil(log_q S)` blocked on unadmitted
   uniform `C(w)`.

## Attribution

Author/committer: Wentao Li `<wentaol4@illinois.edu>`. No `Co-authored-by: Victor Li`.
`ai_assistance`: neutral substantial-AI disclosure only (no product/model names).

## Disposition

Push VictorLiwentao fork only. Do **not** open a CrocSwap PR from this worker
(master decides publish after skeptical review).
