# Transfer-coupled all-shapes obstruction at seven queries

**Scoped obstruction / priced alphabet; no new kappa.** Answers open question 1
of [#2779](https://github.com/CrocSwap/integer-mult-bounds/pull/2779) and the
**remaining-shapes** open question left by the `(5,1,1)`-only transfer-coupled
package, in the five-source common-B mutable-source alphabet of
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898): across every
shape `(p,a,b)` with `p+a+b=7`, can a transfer-coupled dual undercut tariff
`436` after fair shared-prefix XOR billing with priced transfer `C≥1`?

| Shape `(p,a,b)` | Covering | Exact min R | Undercuts 436? |
|---|---:|---:|---|
| `(1,1,5)` | 3916416 | 92 | no (≥440 at X=C=1) |
| `(1,2,4)` | 10416000 | 98 | no |
| `(1,3,3)` | 7082880 | 100 | no |
| `(2,1,4)` | 19165440 | 90 | no |
| `(2,2,3)` | 39997440 | 94 | no |
| `(3,1,3)` | 37497600 | 88 | no |
| `(3,2,2)` | 28748160 | 90 | no |
| `(4,1,2)` | 36664320 | 86 | no |
| `(5,1,1)` | **8749440** | **84** | **no** (min fair X=9 ⇒ tariff **452**) |

Global minimum `R=84` only on maximal-share `(5,1,1)`; on that layer min fair
shared-prefix `X=9` (transfer `C=1` folded in) gives tariff `452>436`. Every
other shape has `R≥86`, already `≥440` at `X=C=1`.

## Reproduction

```sh
python3.12 -I -B research/transfer-coupled-shapes-7q-obstruction/verify.py
python3.12 -I -O -B research/transfer-coupled-shapes-7q-obstruction/verify.py --quick
python3.12 -I -B research/transfer-coupled-shapes-7q-obstruction/independent.py
python3.12 -I -B research/transfer-coupled-shapes-7q-obstruction/test_package.py
python3.12 -B scripts/research_package.py --package research/transfer-coupled-shapes-7q-obstruction
```

Expected:

```text
PASS_TRANSFER_COUPLED_SHAPES_7Q_OBSTRUCTION global_min_R=84 binding=(5, 1, 1) min_fair_X=9 tariff_floor=452 ... answers_remaining_transfer_coupled_shapes no_new_kappa
PASS_INDEPENDENT_TRANSFER_COUPLED_SHAPES_7Q covering_124=... global_min_R=84 tariff_floor=452 ... no_new_kappa
PASS_TRANSFER_COUPLED_SHAPES_7Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/transfer-coupled-shapes-7q-obstruction outcome=completed
```

Default verify live-censuses the binding batch; `--quick` is champions/tariff
only. Admission uses `need()`; `-O --quick` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2643, #2686, #2715, #2761, #2779, and the freestanding `(5,1,1)`-only
transfer-coupled package (not edited; this package answers its remaining-shapes
OQ on a distinct directory). Leave-alone through #2779 is respected. Deferred
shared-XOR soft-overlap with #2643 and host screens are not opened.

## Open next questions

1. Does the dirty-shadow sym-diff collapse of #2761 extend verbatim to eight
   queries (dirty-shadow-8q)?
   Why it matters: closes the remaining multi-connector OQ2.
   First step: reuse the snapshot lemma on length-8 slot lists.
   Blocked by: leave-alone of #2761 fixture; freestanding 8q package only.
2. Do non-distinct (repeat-label) layers inside a transfer-coupled walk improve
   on `R=84` / fair `X=9`?
   Why it matters: closes the one-repeat companion of the Hamilton layer.
   First step: allow one repeated nonzero label in a suffix of `(5,1,1)`.
   Blocked by: larger search; expected to worsen coverage/cost.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, **#2715**, **#2761**, open **#2779**, the
`(5,1,1)`-only transfer-coupled prior (not edited), **TennisBowling / PR1524**,
**Ross Richardson / PR943**, and the retained mutable-source lineage. Live input
pin: `research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao
Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.
