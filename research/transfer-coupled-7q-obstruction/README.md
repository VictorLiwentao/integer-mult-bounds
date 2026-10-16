# Transfer-coupled dual-walk obstruction at seven queries

**Scoped obstruction / priced alphabet; no new kappa.** Answers open question 1
of [#2779](https://github.com/CrocSwap/integer-mult-bounds/pull/2779)
(partitioned independent-walks) in the five-source common-B mutable-source
alphabet of [#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898):
can a **transfer-coupled** dual (shared prefix, priced transfer `C≥1`, divergent
suffixes) undercut tariff `436` after charging walks+transfers+dirt at total
`Q=7`?

| Shape `(p,a,b)` | Covering | Exact min R | Tariff at X=0,C=1 | Undercuts 436? |
|---|---:|---:|---:|---|
| `(1,1,5)` | 3916416 | 92 | 452 | no |
| `(1,2,4)` | 10416000 | 98 | 464 | no |
| `(1,3,3)` | 7082880 | 100 | 468 | no |
| `(2,1,4)` | 19165440 | 90 | 448 | no |
| `(2,2,3)` | 39997440 | 94 | 456 | no |
| `(3,1,3)` | 37497600 | 88 | 444 | no |
| `(3,2,2)` | 28748160 | 90 | 448 | no |
| `(4,1,2)` | 36664320 | 86 | 440 | no |
| `(5,1,1)` | **9166080** | **84** | **436** | **no (= endpoint)** |

Every covering transfer-coupled dual has `R≥84`. Binding minimum `84` on
maximal-share `(5,1,1)`. Abstract tariff `38·Q+2·R+2·X+2·C` at `X=0,C=1` is
already `436`; positive fair shared-prefix path-`X` only increases the bill.

## Reproduction

```sh
python3.12 -I -B research/transfer-coupled-7q-obstruction/verify.py
python3.12 -I -O -B research/transfer-coupled-7q-obstruction/verify.py --quick
python3.12 -I -B research/transfer-coupled-7q-obstruction/independent.py
python3.12 -I -B research/transfer-coupled-7q-obstruction/test_package.py
python3.12 -B scripts/research_package.py --package research/transfer-coupled-7q-obstruction
```

Expected:

```text
PASS_TRANSFER_COUPLED_7Q_OBSTRUCTION global_min_R=84 binding=(5, 1, 1) tariff_floor=436 ... answers_independent_walks_oq_transfer_coupled no_new_kappa
PASS_INDEPENDENT_TRANSFER_COUPLED_7Q covering_124=... global_min_R=84 tariff_floor=436 ... no_new_kappa
PASS_TRANSFER_COUPLED_7Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/transfer-coupled-7q-obstruction outcome=completed
```

Default verify live-censuses the binding batch; `--quick` is champions/tariff only.
Admission uses `need()`; `-O --quick` also passes. Independent censuses the
complement batch.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2643, #2686, #2715, #2761, #2779 (OQ1). Leave-alone through #2779
including #2593, #2643, #2677, #2686, #2687, #2715, #2761, #2764, #2779 is
respected; those packages are not edited. Deferred shared-XOR soft-overlap with
#2643 and host screens are not opened.

## Open next questions

1. Does the dirty-shadow sym-diff collapse of #2761 extend verbatim to eight
   queries (dirty-shadow-8q)?
   Why it matters: closes the remaining multi-connector OQ2.
   First step: reuse the snapshot lemma on length-8 slot lists.
   Blocked by: leave-alone of #2761 fixture; freestanding 8q package only.
2. Do non-distinct (repeat-label) layers inside a transfer-coupled walk improve
   on `R=84`?
   Why it matters: closes the one-repeat companion of the Hamilton layer.
   First step: allow one repeated nonzero label in a suffix of `(5,1,1)`.
   Blocked by: larger search; expected to worsen coverage/cost.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, **#2715**, **#2761**, open **#2779** (OQ1
answered here; not edited), **TennisBowling / PR1524**, **Ross Richardson /
PR943**, and the retained mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.
