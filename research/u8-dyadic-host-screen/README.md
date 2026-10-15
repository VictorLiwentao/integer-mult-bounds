# Host-magnitude screen: U8 dyadic kernel transfer (defer)

**Deferred tooling screen; no new kappa; no production file edited.**

After leave-alone tooling through
[#2433](https://github.com/CrocSwap/integer-mult-bounds/pull/2433), ledger
Deferred packages (`ck-dyadic-replay-production`,
`scalar-fused-dyadic-production`, `clifford-reuse-host-screen`, …), and the
prior `research/clifford-reuse-host-screen/` inventory (defer branch
`cursor/clifford-reuse-host-defer-60b9`), this session tested the next
leave-alone-safe production-wiring idea under the
[#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756) host bar:
identical receipts, no new kappa, and host samples **clearly above ~1.5×** with
**stable** per-round ratios.

## Leading candidate

Sricharan Vagvala’s proved opt-in `research/ck-dyadic-replay-fast/` (#849-era
tooling; early-exit `_normal_row` / COPY-safe `_sum_rows`) already targets
PR917 `complex-ck-two-sided`. That production wiring was deferred at ~1.19×
complete-host magnitude. The same kernels are algebraically equivalent on the
pairwise `_normal_row` / `_sum_rows` in
`research/u8-two-sided-biforest-seed35/independent.py` (kernel differential
plus byte-identical four-stream integer receipts).

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating in-process
pairs of the four complete integer-dyadic streams (333,064 primitives) gave:

| Metric | Value |
|---|---:|
| Baseline median seconds | 1.274 |
| Accelerated median seconds | 0.944 |
| Per-round ratios | **1.302–1.388** |
| Ratio of medians | **1.350×** |
| Identical integer receipts | yes |

**Disposition: DEFER_MAGNITUDE.** Stable ~1.35× is below the clearly-above-~1.5×
bar. A same-session Fraction+integer host of those four streams was only
~1.09× (integer saving diluted by the Fraction oracle), so a complete
production verifier would be thinner still.

## Other inventory (this session)

| Candidate | Host / note | Disposition |
|---|---|---|
| `cyclic-zero-elimination` remeasure | **1.343×** (1.203–1.430) | DEFER_MAGNITUDE (confirms prior thin screen) |
| `phase-recipes-parallel` / `frontier1042-lec-parallel` / `layer-end-controls-parallel` | Strong claimed hosts | DEFER_SOFT_OVERLAP vs leave-alone #2329 / #2409 / #2412 |
| scalar-fused sibling `audit_local.py` copies | Byte-identical to deferred frames-x | DEFER_SAME_BYTES |
| Ledger Deferred dyadic/quadratic/clifford-reuse | — | Leave alone |
| Tooling through #2433 | — | Leave alone |

## Reproduce

```sh
python3 -I -B research/u8-dyadic-host-screen/verify.py
python3 -I -O -B research/u8-dyadic-host-screen/verify.py
python3.12 -B scripts/research_package.py --package research/u8-dyadic-host-screen
```

Expected: `PASS_U8_DYADIC_HOST_SCREEN deferred=true no_production_edit`.
Default verify is read-only and checks committed receipt schema/pins; it does
not rerun the multi-second host pairs.

Optional remeasure (descriptive only):

```sh
# See U8-DYADIC-LINUX.json method: apply ck-dyadic-replay-fast/fast_rows.py
# in-memory to u8-two-sided-biforest-seed35/independent.py on the four streams.
python3.12 -I -B research/cyclic-zero-elimination/verify.py --output /tmp/cyclic-zero-remeasure.json
```

## Open next questions

1. **Question:** After leave-alone HPE/Clifford production PRs merge, does an
   opt-in parallel LEC or phase runner clear a stable >~1.5× host on a
   leave-alone-safe default path without competing digests?
   **Why it matters:** Those adapters have the strongest remaining claimed
   hosts, but soft-overlap the leave-alone object space today.
   **First step:** Remeasure on the merged tips with reference engines only.
   **Blocked by:** #2329 / #2409 / #2412 leave-alone resolution.

2. **Question:** Is there another proved opt-in whose production target is
   byte-disjoint from leave-alone and ledger-Deferred packages and whose
   complete-host samples stably exceed ~1.5× on Linux?
   **Why it matters:** Remaining screened adapters are thin or soft-overlapping.
   **First step:** Refresh the open/#756-bar inventory after the next merge batch.
   **Blocked by:** Inventory refresh.

## Credit

CK dyadic fast kernels: Sricharan Vagvala / `ck-dyadic-replay-fast`. U8
two-sided biforest: Stephan Arrington / `u8-two-sided-biforest-seed35`.
Cyclic-zero: Sagar Thakrar #736. Prior host inventory:
`research/clifford-reuse-host-screen/` on `cursor/clifford-reuse-host-defer-60b9`.
Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No new kappa.
