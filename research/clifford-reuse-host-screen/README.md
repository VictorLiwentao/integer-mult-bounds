# Host-magnitude screen for remaining production-wiring candidates

**Deferred tooling screen; no new kappa; no production file edited.**

After leave-alone tooling through
[#2433](https://github.com/CrocSwap/integer-mult-bounds/pull/2433) and ledger
Deferred packages (`ck-dyadic-replay-production`,
`scalar-fused-dyadic-production`, `quadratic-affine-production`, …), this
session screened the next proved opt-in adapters for production wiring under
the [#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756) host bar:
identical receipts, no new kappa, and host samples **clearly above ~1.5×** with
**stable** per-round ratios (not ratio-of-medians cherry-picks).

## Leading candidate remeasure

`research/clifford-state-reuse/` (#1092, incorporated opt-in) replaces one
redundant `op.zero_state()` call in `monomial()` with the already-computed
`(vec,den)`. On this Linux / CPython 3.12.3 host, three alternating complete U8
phase pairs (2,949 edges, 224 adapters, identical recipe bytes) gave:

| Metric | Value |
|---|---:|
| Baseline seconds | 133.762, 122.685, 125.378 |
| Candidate seconds | 88.129, 84.401, 80.927 |
| Per-round ratios | **1.518, 1.454, 1.549** |
| Ratio of medians | **1.486×** |
| Median of ratios | 1.518× |
| Ranges disjoint | yes |
| Identical recipes | yes |

**Disposition: DEFER_MAGNITUDE.** Ratio-of-medians 1.486× and a per-round sample
at 1.454× are not clearly above ~1.5×. Soft file overlap with leave-alone open
[#2329](https://github.com/CrocSwap/integer-mult-bounds/pull/2329) (gate-table
`zero_state` on the multicold `clifford_exact.py` copy) is an additional reason
not to open a competing production PR on that path until magnitude clears.

Probe-only 16-operator timings on the same host were ~1.50–1.52× and are not
the publish bar.

## Other remaining adapters (same host)

| Opt-in | Host ratio (this session) | Notes |
|---|---:|---|
| `cyclic-zero-elimination` | **1.244×** (1.157–1.383) | Production `eliminate()` still lacks the zero skip |
| `owner-footprint-bitsets` | **1.198×** | Production owner checker still uses sets |
| `t37-slice-bitmaps` | **1.205×** | Thin |
| `gram-prefix-performance` | **1.027×** process | Kernel historically ~1.8–2.0×; E2E thin here |
| Ledger Deferred dyadic/quadratic packages | — | Leave alone |

Already-production or already-published leave-alones were not reopened.

## Reproduce

```sh
python3 -I -B research/clifford-reuse-host-screen/verify.py
```

Expected: `PASS_CLIFFORD_REUSE_HOST_SCREEN deferred=true no_production_edit`.
The verifier only checks committed RESULT schema and pins; it does not rerun
the multi-minute phase pairs. Raw receipts live beside this README.

Optional remeasure (long):

```sh
python3 -I -B research/clifford-state-reuse/verify.py \
  --work /tmp/csr-fresh --rounds 3 --hard-seconds 3600
```

## Open next questions

1. **Question:** After [#2329](https://github.com/CrocSwap/integer-mult-bounds/pull/2329)
   merges gate-table `zero_state`, does monomial reuse still clear ~1.5× on the
   composed evaluator, or does the relative saving shrink further?
   **Why it matters:** Reuse and gate tables compose on different loci of
   `clifford_exact.py`, but the host bar is absolute.
   **First step:** Remeasure three alternating phase pairs on the merged tip.
   **Blocked by:** #2329 merge and a free Linux host slot.

2. **Question:** Is there another proved opt-in with stable host samples
   clearly above ~1.5× that does not touch leave-alone production objects?
   **Why it matters:** The remaining unwired adapters measured here are thin.
   **First step:** Refresh open/#756-bar tooling after the next leave-alone
   batch merges.
   **Blocked by:** Inventory refresh.

## Credit

Clifford reuse opt-in: incorporated #1092 lineage / Charles Bethin gate-table
predecessor #662. Cyclic-zero: Sagar Thakrar #736. Other screened packages keep
their notices. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No new kappa.
