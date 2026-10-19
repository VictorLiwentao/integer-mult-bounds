# Shared-dirt one-repeat partitioned-walk obstruction at eight queries

**Scoped obstruction / priced alphabet; no new kappa.** Freestanding
`#840`-style priced obstruction under
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at
`(b,a,x)=(38,2,2)`. Names one new dirt-legal readout alphabet at `Q=8`:
**mixed shared-dirt + one-repeat** (joint even live-read parity on a one-repeat
partitioned `(2,6)` dual). Answers open question 2 of
[#2883](https://github.com/CrocSwap/integer-mult-bounds/pull/2883) /
`research/independent-walks-9q`. Soft-overlap-safe vs deferred shared-XOR
(R-side dirt coupling only).

| Dual schedule | Covering pairs | Exact min R | Tariff floor (X≥0) | Undercuts 436? | vs priors |
|---|---:|---:|---:|---|---|
| Distinct partitioned (#2851) | — | 92 | ≥488 | no | — |
| Independent one-repeat (#2861) | 59996160 | 112 | ≥528 | no | — |
| Shared-dirt distinct (#2867) | — | 82 | ≥468 | no | — |
| **Shared-dirt one-repeat (this)** | **59996160** | **96** | **≥496** | **no** | beats ind. 112; does not beat shared 82 |

Global covering minimum is `R=96` (spectrum `{96}` only). Abstract tariff
`38·8 + 2·96 + 2·0 = 496 > 436`. Selected κ stays `0.001672660197076918`.

## Reproduction

```sh
python3.12 -I -B research/shared-dirt-onerepeat-8q/verify.py
python3.12 -I -O -Werror -B research/shared-dirt-onerepeat-8q/verify.py
python3.12 -I -B research/shared-dirt-onerepeat-8q/independent.py
python3.12 -I -B research/shared-dirt-onerepeat-8q/test_package.py
python3.12 -B scripts/research_package.py --package research/shared-dirt-onerepeat-8q
```

Expected:

```text
PASS_SHARED_DIRT_ONEREPEAT_8Q_OBSTRUCTION shared_dirt_onerepeat_min_R=96 covering=59996160 tariff_floor=496 independent_one_repeat_min_R=112 shared_dirt_distinct_min_R=82 answers_independent_walks_9q_oq2_mixed_shared_dirt_excess no_undercut_436 no_new_kappa
PASS_SHARED_DIRT_ONEREPEAT_8Q shared_dirt_onerepeat_min_R=96 covering=59996160 tariff_floor=496 independent_one_repeat_min_R=112 answers_independent_walks_9q_oq2_mixed_shared_dirt_excess no_undercut_436 no_new_kappa
PASS_SHARED_DIRT_ONEREPEAT_8Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/shared-dirt-onerepeat-8q outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.
`independent.py` does not import `verify.py` or `model.py`.

## Overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Direct predecessors:
PR1898, #2867 (shared-dirt distinct), #2861 (independent one-repeat), #2883
(Q=9; OQ2 answered here), #2851 (distinct partitioned). Leave-alone through
#2883 including #2868 / #2867 / #2861 / #2860 / #2858 / #2851 is respected;
those packages are not edited. Just-published #3953 (length-≤2 reject census),
selected-stock-envelope finite-C(w)/A=0/rho/STAGE-PRICES, route-cube, UT4,
odd-kernel, and other named leave-alones are outside this package.

## Open next questions

1. Does a mixed shared-dirt + two-repeat (or three-repeat) partitioned schedule
   at `Q=8` undercut shared-dirt distinct `R=82`?
   Why it matters: next mixed excess after one-repeat on the shared-dirt axis.
   First step: fix shared-dirt cost on two-repeat `(2,6)` multisets and census
   covering `R`. Blocked by: two-repeat independent covering is already empty.
2. Does any further priced readout alphabet under PR1898 `(b,a,x)=(38,2,2)`
   beyond the closed Q=8/#9q cluster undercut `436`?
   Why it matters: remaining unequal-price handoff.
   First step: name one new alphabet outside leave-alones and census dirt-legal R.
   Blocked by: leave-alones through #2883; deferred soft-overlaps.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2779**, **#2851**, **#2861** (independent one-repeat), **#2867**
(shared-dirt), **#2868** / **#2860** / **#2858** (leave-alone), **#2883**
(OQ2 answered here; not edited), **TennisBowling / PR1524**, **Ross Richardson
/ PR943**, and the retained mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
No independent human review or multiplication theorem is claimed.
