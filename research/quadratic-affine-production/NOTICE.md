# Attribution and license

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor), wentaol4@illinois.edu) with substantial
AI assistance for orientation, overlap search, profiling, production wiring,
packaging, benchmarking and writing. Not independent human peer review.
Apache-2.0; see the repository root `LICENSE`.

The exact base-256 packed-lane algorithm and its no-carry / compaction argument
were introduced by **Curtis Dransfield (@Curtis-D)** in the opt-in adapter
`research/quadratic-affine-packed/` (incorporated
[CrocSwap/integer-mult-bounds#752](https://github.com/CrocSwap/integer-mult-bounds/pull/752);
see that package's README and NOTICE). This package wires an equivalent check
into the production `scripts/experiments/quadratic_affine.py:rank_witness` path
used by `make verify-certificates`.

The original quadratic-phase families, witnesses, binary elimination and twelve
central-matrix rejections are by **Douglas R. Colkitt**. Upstream material
retains its own source notices and license.

Open [CrocSwap/integer-mult-bounds#1076](https://github.com/CrocSwap/integer-mult-bounds/pull/1076)
targets the same production hotspot with a different bit-sliced engine and is
credited as overlapping unfinished work; this delivery uses the incorporated
#752 packed algorithm rather than that second implementation.
