# Charged k=2 centre-path sharing: copy amortization fails the ≥10% gate

**Planning obstruction / exact packing screen; no new κ.** Selected frontier untouched.

Problem: the `centre-path-sharing` card asks whether sharing the selected centre
path across **k=2** calls can clear a ≥10% packing-ceiling gate after
restoration/hosting overhead is charged. The lever table’s ideal share-by-2
figure (centre charge 32, four rank-8 copies, **zero** overhead) is about ×1.90.
This package answers the charged question on the fixed selected local word
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` under the incumbent coverage law,
using `research/complex-local-word-ceiling/ceiling.py`.

## Result (certified interval gate)

Gate certification against baseline bracket `(a_lo, a_hi)`:

- **PASS** only if `a_lo(new) ≥ (11/10)·a_hi(base)`
- **FAIL** only if `a_hi(new) < (11/10)·a_lo(base)`
- otherwise **INCONCLUSIVE**

| Profile | Centre | Rank-8 copies | Overhead | Gate (certified) |
|---|---:|---:|---|---|
| Selected baseline | 64 | 8 | none | — |
| Ideal share-by-2 | 32 | 4 | none | **PASS** (×≈1.90 on `a_hi/a_hi`) |
| Copy-only amortization | 64 | 4 | none | **FAIL** |
| No rank-8 copies | 64 | 0 | none | **FAIL** |
| Share-by-2 + entire idle mass as rank-1 | 32 | 4 | +1646 | **PASS** |
| Share-by-2, centre 60 | 60 | 4 | none | **PASS** |
| Share-by-2, centre 61 | 61 | 4 | none | **FAIL** |

**Precise new fact.** With copies fixed at 4, an independent fine-grid window scan
shows a single cut: centres ≤60 are certified **PASS** and centres ≥61 are
certified **FAIL**. Copy-only amortization at centre charge 64 is a certified
**FAIL**. Ideal share-by-2 remains a certified **PASS** even after consuming the
entire idle mass as adversarial rank-1 overhead. So the binding obligation for
this route is **reducing the coverage-law centre charge** (or replacing the
coverage model), not merely amortizing the eight rank-8 COPY/ERASE children.

This is not a physical sharing construction, cut-rank transport theorem, or κ
claim. Complementary to #1656 and #1684.

## Reproduce

Python 3.12+, standard library only. Default verify is **read-only** (leaves the
checkout unchanged, compares to committed `RESULT.json`, rejects receipt
corruption). Use `--write` only to regenerate the receipt.

```sh
python3 -B research/centre-share-overhead-screen/verify.py
```

Expected:

```text
PASS_CENTRE_SHARE_OVERHEAD_SCREEN ideal_gate=PASS copy_only_gate=FAIL max_centre_for_10pct=60 rank1_overhead_clears_all_idle=True controls=8 no_new_kappa
```

Also: `python3 -I -O -B research/centre-share-overhead-screen/verify.py` and
`python3 -B scripts/research_package.py --package research/centre-share-overhead-screen`.

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Pins in `SOURCES.json`.
Chooser nonce `1707ecf836f0e426690c9e33d5d902df`. Not run: `make frontier1094-verify`.

## Scope and limits

- Inherited model: PR1012 coverage identity, nine-stage template, idle rank cap
  51, fractional idle packing.
- No two-call circuit, dirty-temp contract, restoration lemma, hosting
  realization, or precision/tape charge.
- Selected κ `836330098538459/500000000000000000` unchanged.

## Open next questions

1. Which explicit two-call dirty-temp contract can legally drop centre charge
   below 60? First step: entry/exit obligations and priced restores. Blocked by
   a restoration/hosting lemma, not another packing sweep.
2. Does #1684’s transport floor of 64 survive shared-temporary accounting across
   two calls?



## Disposition (2026-10-14)

**Defer upstream publication.** Bounded probes against live main `0b1cccf8`:

| Prior | What it already proves (code/proof read) |
|---|---|
| [CrocSwap/integer-mult-bounds#1348](https://github.com/CrocSwap/integer-mult-bounds/pull/1348) (`74768ab4`) | Code-disjoint exact unpaid/centre/families/word-scaling thresholds for T1/T2, pair points, D/E margins, monotonicity/failure controls |
| [CrocSwap/integer-mult-bounds#1708](https://github.com/CrocSwap/integer-mult-bounds/pull/1708) (`4d163c04`) | Shared-source forward fanout construction; complete local invoice 416→384; profile rank-8 8→4 |
| [CrocSwap/integer-mult-bounds#1714](https://github.com/CrocSwap/integer-mult-bounds/pull/1714) (`333acd5b`) | Scoped all-batch floor 64·rank(C) in the P112 root-code model |
| [CrocSwap/integer-mult-bounds#1748](https://github.com/CrocSwap/integer-mult-bounds/pull/1748) (`ea14f191`) | Shared reverse phase + precision/overhead inequality |

This package’s certified 10% card-gate cut (copies=4 ⇒ centre ≤60 PASS / ≥61 FAIL) and copy-only FAIL at centre 64 are packing-parameter screens. The #1708 fused rank-8 profile matches the copy-only row; adding centre-monotonicity alone does not establish a new construction or restoration lemma. Fork PR kept for record; not submitted to CrocSwap.


## Credit

Packing ceiling / levers: `research/complex-local-word-ceiling/` (Douglas
Colkitt; Claude assistance). Coverage identity: PR1012 lineage. Selected
construction: community batch #1099 / frontier #1094. Nearby: #1656, #1684,
#1664. Prepared by Wentao Li (@VictorLiwentao; wentaol4@illinois.edu;
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0.
