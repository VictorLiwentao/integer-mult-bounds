# Handoff: completed ordinary leaf realized on the selected m=73 complex peeled residual

## Result

The selected m=73 complex producer's peeled-atom remainder (`n = 73f + delta`)
and its bounded stopped leaf (`n < 73`) are at most 72 sequential calls of the
published completed ordinary interchange
(`research/physical-ordinary-interchange`). In each call the parent's leaf
reserve is only a factor of the prefix, `P_i = Pre * S_ext * q^(w i)`. These
calls run through the unchanged engine, on both the elementary and fitted
branches, with the reserve at extent 1 and extent > 1. In every run each
column keeps its parent-reserve coordinate and the internal resources are
the same. So `S_leaf = 1` (`rho = 0`) holds **on this residual class**,
realized rather than cited. Global `rho` stays open. Selected κ is unchanged
at `0.001672660197076918`.

Pinned CrocSwap main: `6f100d4bb5083f8c35d96fd95a539811c62f245c`.
Branch: `cursor/selected-stock-leaf-realization-b2fc` (environment-required
suffix in place of `-60b9`).
Content tip: `0c5f2b51b363c130654ad55d2dee4be20efc88b7`. It holds the full
package except this file. Injected co-author trailers were stripped with
`commit-tree`.
Packaging tip: the commit that adds this file (`git rev-parse HEAD` on the
branch). It changes only `MASTER-HANDOFF.md`.
Package: `research/selected-complex-peeled-leaf`.

## Switch

No card switch. This follows the preferred claim: realize completed
ordinary-leaf on one complex residual, the step named by the deferred
`research/selected-stock-rho-zero` (`f18dc91d5`). That citation is not
reprinted, and `A = 0` and `B_bits = 2642` are not recomputed.

## Exact commands (expected PASS)

```sh
python3.12 -I -B research/selected-complex-peeled-leaf/verify.py
# PASS_SELECTED_COMPLEX_PEELED_LEAF m=73 nodes=1533 deltas=73/73 max_calls=72 reserve_active_calls=0 physical_cases=12 controls=4 S_leaf=1_realized_on_peeled_residual no_new_kappa

python3.12 -I -O -B research/selected-complex-peeled-leaf/verify.py
# same marker

python3.12 -I -B research/selected-complex-peeled-leaf/independent.py
# PASS_SELECTED_COMPLEX_PEELED_LEAF_INDEPENDENT nodes=1533 deltas=73/73 max_calls=72 physical_cases=12 engine_payloads_match

python3.12 -I -B research/selected-complex-peeled-leaf/test_package.py
# PASS_SELECTED_COMPLEX_PEELED_LEAF_TESTS groups=6

python3.12 -I -B research/selected-complex-peeled-leaf/verify.py --suite fitted
# PASS_SELECTED_COMPLEX_PEELED_LEAF_FITTED cases=2 padded_ratio=3/2 own_rows=8 reserve_extents=1,2 parent_reserve_restored_through_C0

python3.12 -B scripts/research_package.py --package research/selected-complex-peeled-leaf
# PASS_REGISTERED_RESEARCH_PACKAGE research/selected-complex-peeled-leaf outcome=completed
```

Runtimes: default verify about 5 s, tests about 25 s, fitted suite about
2 min 10 s, full registered replay about 2 min 50 s (Python 3.12.3, Linux).

## Closest priors

- [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113)
  `research/selected-stock-envelope-m73` bound `B_bits = 2642` and recorded
  `rho` as unbound (OQ2).
- [#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421) (open)
  `research/selected-stock-shape-a-zero` proved `A = 0` and left `rho` open.
- [#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105)
  `research/selected-coarse-depth-stock` gives the parent formula and the
  conditional `S_leaf = 1` permission.
- `research/physical-ordinary-interchange` (Jose Manuel, PR2808/PR2809
  lineage) is the completed ordinary engine executed here, unchanged. Its own
  OQ says the complex supplier remains separate.
- Deferred `research/selected-stock-rho-zero` (`f18dc91d5`) is the
  citation-only `rho = 0`. This package is the realization that deferral
  asked for.

## Soft-overlap risks

- Reviewers may read this as the deferred citation. The difference is the
  exact all-n residual plan, the per-call interface signature, and the
  physical runs with reserve present and absent. The scope is one residual
  class, not all leaf calls.
- The fitted extent-1 run has the same shape as the predecessor's own
  `(1,1,1)` fixture case. The new parts are the extent-2 run and the C0-level
  reserve-coordinate observer.
- The BIT-side node packages (`selected-bit-node`,
  `selected-node-stock-refinement`, `residual-call-refinement`) handle m=64
  peel/NODE boundaries. This package is complex m=73 only and does not touch
  them.
- No overlap with the P104 present-head series, group B/C/D native widths,
  F17 bills, or the #3363 cascade.

## Open next questions

1. Realize the remaining leaf-call classes (fixed cover routing, high-part
   exchange / residual digits) so that global `rho = 0` is bound.
2. Record the C0 `old_count` / `fresh_rows` arguments of the fitted branch
   under the production profile.

## Credit

Jose Manuel, Nick Petalas, David Arias and the PR2809 lineage built the
engine. Aaron Wang (#3113), Sricharan Vagvala (#2105), the PR185 reviewed
proof, and the stopped-product and cover-rows notes are the other sources.
Their notices are untouched.

Prepared by Wentao Li with substantial AI assistance.
