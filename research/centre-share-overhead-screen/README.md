# Charged k=2 centre-path sharing screen (no new κ)

**Scoped planning screen for the `centre-path-sharing` card. Selected frontier untouched.**

The packing-ceiling lever table reports an ideal ×1.90 when the selected centre
path is shared across two calls with **zero** restoration/hosting overhead
(`centre` charge 32, four rank-8 copies). The card's acceptance gate requires
those costs to be charged. This package screens that charged question on the
fixed selected local word
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` under the incumbent coverage law,
using `research/complex-local-word-ceiling/ceiling.py`.

## Result

| Profile | Centre charge | Rank-8 copies | Overhead | Ceiling × vs selected word | ≥10% gate |
|---|---:|---:|---|---:|---|
| Selected baseline | 64 | 8 | none | 1.00 | — |
| Ideal share-by-2 (`levers.py`) | 32 | 4 | none | **1.90** | pass |
| Copy-only amortization | 64 | 4 | none | **1.0028** | **fail** |
| No rank-8 copies | 64 | 0 | none | 1.0057 | fail |
| Share-by-2 + 4 rank-1 units | 32 | 4 | +4 | 1.90 | pass |
| Share-by-2 + entire idle mass as rank-1 | 32 | 4 | +1646 | **1.45** | pass |
| Share-by-2, centre charge 60 | 60 | 4 | none | 1.115 | pass |
| Share-by-2, centre charge 61 | 61 | 4 | none | 1.092 | fail |

**Findings.**

1. Ideal k=2 sharing clears the card's ≥10% stop rule; the route is not killed by
   the zero-overhead lever alone.
2. Halving only the eight private COPY/ERASE children while leaving the
   coverage-law centre charge at 64 yields about **+0.28%** and **fails** the
   ≥10% gate. Deleting those copies entirely still fails.
3. With copies fixed at 4, the coverage-law centre charge must be **≤ 60** to
   clear ≥10%; charge 61 fails.
4. Once the centre charge is reduced to 32, even consuming the entire idle mass
   as adversarial rank-1 overhead still clears ≥10%.

So the binding obligation for this route is **reducing the coverage-law centre
charge** (or stating a replacement coverage model with its own fully charged
bound), not merely amortizing the eight rank-8 COPY/ERASE children across two
calls.

This is a packing-relaxation screen, not a physical sharing construction, not a
cut-rank transport theorem, and not a kappa claim. It is complementary to
#1656 (within-call pair-total replacements on the delivery cut) and #1684
(selected centre-phase cut-rank transport floor 64 under an explicit scalar
model).

## Reproduce

Standard library only, Python 3.12:

```sh
python3 -B research/centre-share-overhead-screen/verify.py
python3 -I -O -B research/centre-share-overhead-screen/verify.py
python3 -B scripts/research_package.py --package research/centre-share-overhead-screen
```

Expected final line:

```text
PASS_CENTRE_SHARE_OVERHEAD_SCREEN ideal_x=1.9011 copy_only_x=1.0028 max_centre_for_10pct=60 rank1_overhead_clears_all_idle=True controls=7 no_new_kappa
```

The verifier pins predecessor sources, reproduces the selected-word packing
ceiling against `RESULT.json`, screens the rows above, confirms the centre-charge
threshold on the fine grid, and rejects an impossible overhead that violates the
coverage law. Asserts are not admission predicates; `-O` also passes.

## Scope and limits

- Inherited model: PR1012 coverage identity, nine-stage template, idle rank cap
  51, fractional idle packing. Outside those hypotheses the numbers do not apply.
- No two-call circuit, dirty temporary contract, restoration lemma, hosting
  realization, or precision/tape charge is constructed.
- Selected κ `836330098538459/500000000000000000` and cold replay
  `make frontier1094-verify` are **not** re-run; the selected record is unchanged.
- Chooser nonce `1707ecf836f0e426690c9e33d5d902df`; catalogue scope key
  `a55534776f5479f1686c`; scope **refined** to charged k=2 overhead vs the
  coverage centre charge (see `TASK.json`).

## Open next questions

1. **Which explicit two-call contract can reduce the coverage-law centre charge
   below 60 while remaining legal on dirty private temporaries?**
   Why it matters: the screen shows copy amortization alone cannot meet the
   card's ≥10% gate. First step: write entry/exit obligations for one shared
   temporary across two consecutive selected-centre phases and price every
   restore. Blocked by: a concrete restoration/hosting lemma, not another
   packing sweep.
2. **Does #1684's cut-rank transport floor of 64 per emitted centre phase survive
   a shared-temporary accounting that credits work across two calls?**
   Why it matters: a shared-temp model might change the measured interval or
   Q-entry rank. First step: restate #1664/#1684 with an explicit two-call
   history span. Blocked by: agreement on the shared-temp observation model.

## Credit

Packing ceiling and lever table:
[`research/complex-local-word-ceiling/`](../complex-local-word-ceiling/README.md)
(Douglas Colkitt; Claude assistance). Coverage identity: PR1012 lineage.
Selected construction: community batch #1099 / frontier #1094 review.
Nearby distinct centre work: #1656, #1684, #1664. Task selection via
`scripts/choose_research_task.py` on base `0b1cccf8`. Prepared by Victor
Liwentao with substantial Cursor / Composer AI assistance. Apache-2.0.
