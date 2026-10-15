# Host-magnitude screen: leave-alone-safe proved adapters (defer)

**Deferred tooling screen; no new kappa; no production file edited.**

Answers open question 2 of the prior ledger-Deferred package
`research/lec-parallel-host-screen/`: after leave-alone tooling through
[#2433](https://github.com/CrocSwap/integer-mult-bounds/pull/2433) and ledger
Deferred dyadic/Clifford/U8/LEC screens, is there another proved opt-in whose
production target is byte-disjoint from those leave-alone packages and whose
complete-host samples stably exceed ~1.5× on Linux?

**Disposition: DEFER_TOOLING_INVENTORY_EXHAUSTED.** No such leave-alone-safe
complete-host win was found on this refresh. Strong hosts remain soft-overlap
blocked. Do not open a CrocSwap PR as a production wiring.

## Leading leave-alone-safe sample (this session)

The proved opt-in `research/gram-prefix-performance/` (#707 lineage) reuses
leading principal Bareiss determinants for the R420 positive Gram checker.
Its production target
`research/e8-bit-carrier-skeleton/code/pricing/prime_witnesses.py:det` is
byte-disjoint from leave-alone [#2263](https://github.com/CrocSwap/integer-mult-bounds/pull/2263)/[#2276](https://github.com/CrocSwap/integer-mult-bounds/pull/2276)
(`e8-bit-r420` MANIFEST/`xcheck`/`mutants`) and from tooling through #2433.

On Linux / CPython 3.12.3, five alternating production-style in-process pairs
(PrefixDeterminant replacing `pw.det` with no adapter import/hash overhead;
identical 672-frame positive Gram receipts) gave:

| Workload | Ratio of medians | Per-round range |
|---|---:|---:|
| Complete positive Gram checker | **1.077×** | **1.065–1.120** |
| Determinant-request batch only | 1.509× | 1.454–1.588 |

**DEFER_MAGNITUDE.** The complete-host sample is below the clearly-above-~1.5×
bar. The batch figure is micro-only and is not a complete-host claim.

## Cyclic-zero corroboration

Independent Linux remeasure of `research/cyclic-zero-elimination/` (#736)
(seven pairs, identical eight-case receipt
`2c4ab855129670053f4f39ee14269cc9b5bda015eab71d5a226dd0d395740ebd`):

| Metric | Value |
|---|---:|
| Ratio of medians | **1.279×** |
| Per-round range | **1.168–1.307** |

Leave-alone-safe; still below bar. Corroborates the prior lec-parallel
inventory (~1.285×, 1.25–1.30).

## Inventory (this session)

| Candidate | Host / note | Disposition |
|---|---|---|
| gram-prefix production-style | full **1.077×** (1.065–1.120); batch 1.509× micro | DEFER_MAGNITUDE |
| cyclic-zero remeasure | **1.279×** (1.168–1.307) | DEFER_MAGNITUDE |
| LEC / phase / selected-replay parallel | strong claimed hosts | DEFER_SOFT_OVERLAP vs #2409/#2412/#2329 |
| owner-footprint / exact-frame / joint-frame-modular / t37 / p111-rup / stage-pair / exact-exp / rational-containment | complete hosts ~1.0–1.23× or micro-only | DEFER_MAGNITUDE |
| Ledger Deferred dyadic/Clifford/U8/LEC/quadratic screens | — | Leave alone |
| Tooling through #2433 | — | Leave alone |

## Reproduce

```sh
python3.12 -I -B research/leave-alone-safe-host-screen/verify.py
python3.12 -I -O -B research/leave-alone-safe-host-screen/verify.py
python3.12 -B scripts/research_package.py --package research/leave-alone-safe-host-screen
```

Expected: `PASS_LEAVE_ALONE_SAFE_HOST_SCREEN deferred=true no_production_edit`.
Default verify is read-only and checks committed receipt schema/pins; it does
not rerun the host pairs. Package gates under `-O` still use `require()`.

Optional cyclic remeasure (descriptive only; ~1 minute):

```sh
python3.12 -I -B research/cyclic-zero-elimination/verify.py \
  --output /tmp/cyclic-zero-remeasure.json
```

## Open next questions

1. **Question:** After leave-alone #2409/#2412 (and preferably #2329) merge,
   can production wiring of `controls_parallel.py` into a default LEC call site
   keep identical receipts with retargeted HPE digests?
   **Why it matters:** Prior Linux remeasure shows a stable ~2.45× host that
   already clears the #756 magnitude bar; leave-alone-safe adapters remain thin.
   **First step:** Retarget `PINS.json` audit digest to the merged integer-row
   production tip; remeasure one call site.
   **Blocked by:** #2409 / #2412 leave-alone resolution.

2. **Question:** Is there a scoped #840-style construction (exact before/after
   costs, independent replay) outside exhausted tooling spaces and open
   leave-independent soft-overlaps?
   **Why it matters:** This inventory refresh finds no leave-alone-safe proved
   opt-in clearing the complete-host #756 bar.
   **First step:** Pick one open next question from a recently incorporated
   recursive-interface or bit-mechanism package whose object is byte-disjoint
   from leave-alone PRs.
   **Blocked by:** Construction search / claim coordination on Discussions #1166.

## Credit

Closest priors (different delivery): `research/gram-prefix-performance/`
(opt-in Bareiss prefix reuse; this is a Linux production-style host remeasure +
magnitude defer, not a production wire), Sagar Thakrar’s
`research/cyclic-zero-elimination/` / [#736](https://github.com/CrocSwap/integer-mult-bounds/pull/736),
prior Victor inventories
`research/lec-parallel-host-screen/` / `research/u8-dyadic-host-screen/` /
`research/clifford-reuse-host-screen/` (ledger Deferred; open Q2 answered here),
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
(tooling bar). Leave-alone tooling through
[#2433](https://github.com/CrocSwap/integer-mult-bounds/pull/2433) was not
reopened.

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0.
