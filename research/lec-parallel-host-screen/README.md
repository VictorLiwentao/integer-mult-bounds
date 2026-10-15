# Host-magnitude screen: LEC parallel (defer soft-overlap)

**Deferred tooling screen; no new kappa; no production file edited.**

After leave-alone tooling through
[#2433](https://github.com/CrocSwap/integer-mult-bounds/pull/2433), ledger
Deferred packages (`ck-dyadic-replay-production`,
`scalar-fused-dyadic-production`, `clifford-reuse-host-screen`,
`u8-dyadic-host-screen`, …), and the prior U8 dyadic host inventory (which
flagged parallel LEC/phase adapters as soft-overlap **without** a Linux
remeasure), this session measured the strongest remaining claimed host under
the [#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756) bar:
identical receipts, no new kappa, and host samples **clearly above ~1.5×** with
**stable** per-round ratios.

## Leading candidate

Sagar Thakrar’s proved opt-in `research/layer-end-controls-parallel/`
(incorporated #1059/#1151 lineage) parallelizes the 96 independent PR635 HPE
audits inside PR870’s `layers_p6n/layer_end_controls.py` without editing that
script. Prior author measurements on macOS arm64 reported ~2.6–3.0×. Prior
Victor host inventories deferred it for soft-overlap with leave-alone HPE
production PRs and did not remeasure on Linux.

On Linux / CPython 3.12.3 with 4 CPUs and `--jobs 4`, five `verify.py --serial`
pairs (byte-identical `COLD-END-CONTROLS.json`, C1 corruption control) gave:

| Metric | Value |
|---|---:|
| Serial median seconds | 89.1 |
| Parallel median seconds | 36.4 |
| Per-round ratios | **2.426–2.617** |
| Ratio of medians | **2.448×** |
| Identical cold-end receipts | yes |

**Disposition: DEFER_SOFT_OVERLAP.** Magnitude clears the clearly-above-~1.5×
bar with a tight per-round range, but production wiring would soft-overlap
leave-alone [#2409](https://github.com/CrocSwap/integer-mult-bounds/pull/2409)
/ [#2412](https://github.com/CrocSwap/integer-mult-bounds/pull/2412): the
parallel runner digest-authenticates production
`hpe_audit_and_transport.py`, which those PRs rewrite. Soft MANIFEST overlap
is acceptable for complementary merges only after those leave-alone heads
settle; competing production edits while they are open are deferred.

## Other inventory (this session)

| Candidate | Host / note | Disposition |
|---|---|---|
| `cyclic-zero-elimination` remeasure | **1.285×** (1.247–1.297) | DEFER_MAGNITUDE (leave-alone-safe; thin) |
| `phase-recipes-parallel` / `frontier1042-lec-parallel` / `selected-replay-fastpath` | Strong claimed hosts | DEFER_SOFT_OVERLAP vs #2329 / #2409 / #2412 |
| gram-prefix / owner-footprint / exact-frame / joint-frame-modular / p111-rup | Complete hosts ~1.0–1.23× or micro-only | DEFER_MAGNITUDE |
| p112-single-lift + modulo-521 | Envelope fits; Bareiss already beats modular on this host | no win |
| Ledger Deferred dyadic/Clifford/quadratic screens | — | Leave alone |
| Tooling through #2433 | — | Leave alone |

## Reproduce

```sh
python3 -I -B research/lec-parallel-host-screen/verify.py
python3 -I -O -B research/lec-parallel-host-screen/verify.py
python3.12 -B scripts/research_package.py --package research/lec-parallel-host-screen
```

Expected: `PASS_LEC_PARALLEL_HOST_SCREEN deferred=true no_production_edit`.
Default verify is read-only and checks committed receipt schema/pins; it does
not rerun the multi-minute host pairs.

Optional remeasure (descriptive only; ~12 minutes for five pairs):

```sh
work=$(mktemp -d /tmp/lec-remeasure.XXXXXX)
python3.12 -I -B research/layer-end-controls-parallel/verify.py \
  --work "$work/r0" --jobs 4 --serial
python3.12 -I -B research/cyclic-zero-elimination/verify.py \
  --output /tmp/cyclic-zero-remeasure.json
```

## Open next questions

1. **Question:** After leave-alone #2409/#2412 merge, can production wiring of
   `controls_parallel.py` into a single default LEC call site (PR870
   `reproduce_barch.py` or frontier1042 leaver chain) keep identical receipts
   with retargeted HPE digests?
   **Why it matters:** This Linux remeasure shows a stable ~2.45× host that
   already clears the #756 magnitude bar.
   **First step:** Retarget `PINS.json` audit digest to the merged integer-row
   production tip; remeasure one call site.
   **Blocked by:** #2409 / #2412 leave-alone resolution.

2. **Question:** Is there another proved opt-in whose production target is
   byte-disjoint from leave-alone and ledger-Deferred packages and whose
   complete-host samples stably exceed ~1.5× on Linux?
   **Why it matters:** Leave-alone-safe adapters screened here remain thin.
   **First step:** Refresh the open/#756-bar inventory after the next merge batch.
   **Blocked by:** Inventory refresh.

## Credit

Closest priors (different delivery): Sagar Thakrar’s
`research/layer-end-controls-parallel/` (opt-in parallel LEC; this is a Linux
host remeasure + soft-overlap defer, not a production wire),
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
(tooling bar), prior Victor inventories
`research/u8-dyadic-host-screen/` / `research/clifford-reuse-host-screen/`
(flagged LEC soft-overlap without this Linux remeasure). Leave-alone tooling
through [#2433](https://github.com/CrocSwap/integer-mult-bounds/pull/2433)
was not reopened.

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0.
