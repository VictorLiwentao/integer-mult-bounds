# Transfer-coupled duals cannot undercut tariff 436 at Q=7

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898). It answers
open question 1 of [#2779](https://github.com/CrocSwap/integer-mult-bounds/pull/2779):
can a **transfer-coupled** dual (shared prefix, priced transfer `C≥1`, divergent
suffixes) undercut the six-query endpoint tariff `436` at total `Q=7`?

No new kappa is claimed. Leave-alone packages through #2779 are not edited.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **restored walk** of length `n` is an open slot list
`(s_0,…,s_{n-1})` with `s_0 = 0` whose closed completion has only nonzero edges.

A **transfer-coupled dual** of total query count `Q = 7` is a shape `(p,a,b)`
with `p+a+b = 7` and `p,a,b ≥ 1`:

- shared prefix of length `p` (counted once in `Q`);
- divergent suffixes of lengths `a` and `b`;
- walks `w0 = prefix∥suffix_a` and `w1 = prefix∥suffix_b` of lengths `p+a` and
  `p+b` (both ≥ 2);
- priced transfer `C ≥ 1` for the fork after the prefix;
- dual even-parity readout with independent dirt on each walk.

Fair shared-prefix XOR billing charges internal prefix edges once:

```text
X_fair = path_X(w0) + path_X(w1) − path_edges(prefix).
```

The abstract complete-call tariff at `(b,a,x)=(38,2,2)` with transfer is

```text
38·Q + 2·R + 2·X + 2·C.
```

Up to swapping suffixes `a ≤ b`, the shapes are
`(1,1,5),(1,2,4),(1,3,3),(2,1,4),(2,2,3),(3,1,3),(3,2,2),(4,1,2),(5,1,1)`.

## Census results

Every covering distinct-label schedule (nonzero labels within each walk
disjoint from the shared prefix; suffixes may share labels with each other) was
enumerated. Dual cost is the real `min_a` sum

```text
R = Σ_{m=1}^{31} min_a (e0[a] + e1[a ⊕ m]),
```

not a copied constant.

| Shape | Covering | Min R |
|---|---:|---:|
| `(1,1,5)` | 3916416 | 92 |
| `(1,2,4)` | 10416000 | 98 |
| `(1,3,3)` | 7082880 | 100 |
| `(2,1,4)` | 19165440 | 90 |
| `(2,2,3)` | 39997440 | 94 |
| `(3,1,3)` | 37497600 | 88 |
| `(3,2,2)` | 28748160 | 90 |
| `(4,1,2)` | 36664320 | 86 |
| `(5,1,1)` | 9166080 | **84** |

Hence every covering transfer-coupled dual has `R ≥ 84`, with equality on
maximal-share `(5,1,1)`.

## Binding shape `(5,1,1)`

Prefix length 5, two singleton suffixes `σ,τ`. Walks have length 6. Same-suffix
schedules (`σ=τ`) that cover are exactly the rank-5 bases; their even-subset
cost equals the `F₂⁵` even-sum identity

```text
Σ_{v≠0} least_even_≥(wt(v)) = 96,
```

so same-suffix dual cost is `96`. Distinct suffixes improve to `R ∈ {84,88,90}`;
covering count `9166080` with histogram
`{84:1458240, 88:2083200, 90:5208000, 96:416640}`.

Champion: prefix `(0,1,2,4,8)`, suffixes `(15,)` and `(16,)`, `R=84`, fair
path-`X = 18`, tariff `472` at `C=1`.

## Tariff consequence

At the global minimum `R=84`, even with `X=0` and minimal transfer `C=1`,

```text
38·7 + 2·84 + 2·0 + 2·1 = 436,
```

matching but **not undercutting** the six-query endpoint. Positive fair path-`X`
strictly increases the bill. All other shapes have `R ≥ 86` and therefore tariff
`≥ 440` already at `X=0,C=1`.

By comparison:

- partitioned independent walks (#2779) have exact `R=112` (tariff floor `490`);
- same-walk even-subset / multi-connector (#2686 / #2761) reach `R=82` at `X=6`
  (tariff `442`) but are leave-alone same-walk fixtures, not transfer-coupled.

Sharing a prefix improves on partitioned duals (84 < 112) but the mandatory
transfer charge and remaining readout invoice still cannot beat `436`.

## Scope limits

- Fixes transfer-coupled duals at total `Q=7` with distinct nonzero labels
  within each walk relative to the shared prefix. Repeat-label layers are
  outside.
- Same-walk multi-connector / priced shadow remains #2761 (not edited).
- Partitioned independent walks remain #2779 (not edited).
- Shared non-path XOR schedules remain deferred (soft-overlap with #2643).
- Host screens are deferred.
- Leave-alone through #2779 is not edited.
- No new kappa, physical supplier, or multiplication theorem.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q=6`, endpoint tariff 436 | — |
| #2643 | `X≥6` at single-walk `Q=7` | — |
| #2686 | Even-subset `R≥82` on one walk | — |
| #2715 | All-subset collapses under dirty-parity | — |
| #2761 | Same-walk dual / dirty shadow stay at `R≥82` | — |
| #2779 | Partitioned dual walks at `Q=7` have `R=112` | transfer-coupled OQ |
| **This** | — | **Transfer-coupled duals at `Q=7` have `R≥84`; tariff floor `436` at `C=1` (no undercut)** |
