# MASTER-HANDOFF — selected-complex-highpart-leaf

## Tips

| Ref | SHA |
|---|---|
| CrocSwap `main` base | `20ecf2891d80b5acf18d980b2164fb44ea7faa90` |
| VictorLiwentao branch | `cursor/selected-complex-ordinary-leaf-eb60` |
| Package tip | `cd9c9b89f23437f7ac251e621e8bb4e42366e0a3` |
| Content tip (VERIFY/PROOF) | `91e00c51cfdde9b53e58580d64bb72081d64effa` |
| Selected κ (unchanged) | `0.001672660197076918` (priority revision 6) |

## One-sentence claim

On the selected m=73 complex producer, the PR185 high-part-exchange leaf-call class (one ordinary width-`k` interchange of `H_hi`/`D_hi` after the body wrapper, bodies and `Z` as spectators) completes through the published physical-ordinary engine with parent reserve extent 1, exact before/after widths `(k+body)/k`, and observed `S_leaf=1` on that class; global `rho` stays open; no new kappa.

## PASS lines

```text
PASS_SELECTED_COMPLEX_HIGHPART_LEAF shapes=25 calls=1 active_width=k full_chunk_width=k+body width_ratios=2/1..6/1 physical_cases=12 controls=4 S_leaf=1_realized_on_highpart_exchange no_new_kappa
PASS_SELECTED_COMPLEX_HIGHPART_LEAF_INDEPENDENT shapes=25 calls=1 physical_cases=12 engine_payloads_match
PASS_SELECTED_COMPLEX_HIGHPART_LEAF_TESTS groups=6
PASS_SELECTED_COMPLEX_HIGHPART_LEAF_FITTED cases=2 padded_ratio=3/2 own_rows=8 reserve_extents=1,2 parent_reserve_restored_through_C0
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-complex-highpart-leaf outcome=completed
```

## Commands

```sh
python3.12 -I -B research/selected-complex-highpart-leaf/verify.py
python3.12 -I -O -B research/selected-complex-highpart-leaf/verify.py
python3.12 -I -B research/selected-complex-highpart-leaf/independent.py
python3.12 -I -B research/selected-complex-highpart-leaf/test_package.py
python3.12 -I -B research/selected-complex-highpart-leaf/verify.py --suite fitted
python3.12 -B scripts/research_package.py --package research/selected-complex-highpart-leaf
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.
Duplicate JSON keys and on-disk certificate corruption are rejected (temp copies).

## Soft-overlap risks

- Shares `research/physical-ordinary-interchange` with deferred
  `research/selected-complex-peeled-leaf/` — different call class (high-part
  vs peeled residual), different layout, exact `(k+body)/k` width costs.
- Fitted suite reuses the published reduced fixture machinery (same soft-overlap
  surface that deferred peeled-leaf); novelty is the high-part signature
  (highs active; bodies/Z spectators), not a new fitted engine.
- Does not reprint citation-only `research/selected-stock-rho-zero/`.
- Does not recompute A=0 / B=2642 from #3421.
- Leave-alones untouched: #3621/#3618/#3614/#3610/#3601/#3532/#3508/#3421 and
  P104 side-correction template series.

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
