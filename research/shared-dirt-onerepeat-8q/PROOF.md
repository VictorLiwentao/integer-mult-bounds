# Shared-dirt one-repeat (2,6) cannot undercut tariff 436 at Q=8

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at unit
tariff `(b,a,x)=(38,2,2)`. It names one freestanding `#840`-style priced
readout alphabet at eight queries: the **mixed shared-dirt + one-repeat**
companion of the partitioned `(2,6)` dual. It answers open question 2 of
[`research/independent-walks-9q`](../independent-walks-9q/) (PR #2883): whether
combining shared-dirt (joint even live-read parity) with one-repeat excess
undercuts the shared-dirt distinct floor `R=82` or the six-query endpoint.

No new kappa is claimed. Leave-alone packages through #2883 / #2868 / #2867 /
#2861 / #2860 / #2858 / #2851 are not edited. Soft-overlap with deferred
shared-XOR remains closed: only the R-side dirt coefficient is coupled.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **restored walk** of length `n≥2` is an open slot list starting at
`0` whose closed completion has only nonzero edges.

A **shared-dirt one-repeat (2,6) dual** is a pair

- short walk `(0,σ)` with `σ∈{1,…,31}`,
- long walk `(0,ℓ_1,…,ℓ_5)` whose five nonzero slots contain **exactly one**
  repeated nonzero label (multiset shape `{d:2,o₁,o₂,o₃}`),

with **one shared dirt coefficient**. Legal dirty cancellation requires even
**total** live-read parity across both walks. With even/odd subset tables
`(e,o)` on the long walk, the dual cost is

```text
R = Σ_{m=1}^{31} min(
      e[m],  2 + e[m ⊕ σ],  1 + o[m],  1 + o[m ⊕ σ]
    ).
```

Independent dirt ([`research/independent-walks-onerepeat-8q`](../independent-walks-onerepeat-8q/))
admits only the even branch, so shared-dirt `R` is always ≤ independent `R`
whenever both cover. The abstract complete-call tariff at `(b,a,x)=(38,2,2)` is
`38·Q + 2·R + 2·X`.

## Structural lemmas

**Lemma (Σe = 40 on rank-4 one-repeat longs).** Every valid restored length-6
walk whose nonzero multiset has shape `{d:2,o₁,o₂,o₃}` and whose four distinct
nonzero labels span a rank-4 subspace has

```text
Σ_{v ∈ V \ {0}} e[v] = 40,
```

where `V` is the long span. Inherited from the independent one-repeat package;
rechecked here on all `3749760` such walks.

**Lemma (independent outside).** When the long span has rank `4` and `σ ∉ V`,
independent dirt gives `R = 2·40 + 32 = 112`.

**Lemma (shared outside).** On the same pairs, shared dirt gives **`R = 96`**
exactly (save `16` versus independent). Machine-checked on all
`3749760 · 16 = 59996160` covering pairs.

**Lemma (inside span / rank&lt;4 never cover).** If `σ ∈ V`, or if the four
distinct nonzero labels have rank `&lt;4`, shared-dirt dual cost returns `None`
for every such one-repeat long (machine-checked: `inside_cover=0`,
`covering_rank_lt4=0` on `781200` rank`&lt;4` walks).

## Census

Valid one-repeat length-6 walks: `4530960`, of which rank-4: `3749760`.
Outside-span short labels per rank-4 long: `31 − 15 = 16`. Covering pairs:

```text
3749760 · 16 = 59996160.
```

Attainable spectrum: `{96}` with histogram `{96: 59996160}`. Minimum `R=96`.

Champion path `((0,16),(0,4,1,8,2,1))` has shared `R=96`, independent `R=112`,
path `X=8`, tariff `512`. The `X=0` figure `496` is only the abstract lower
bound from `R=96`.

## Tariff consequence

Every covering shared-dirt one-repeat `(2,6)` dual has `R=96`. Even at `X=0`,

```text
38·8 + 2·96 + 2·0 = 496 > 436.
```

Positive path-`X` only increases the bill. Comparison:

| Alphabet | Covering min R | Tariff floor (X=0) | Undercuts 436? |
|---|---:|---:|---|
| Distinct partitioned (#2851) | 92 | 488 | no |
| Independent one-repeat (#2861) | 112 | 528 | no |
| Shared-dirt distinct (#2867) | 82 | 468 | no |
| **Shared-dirt one-repeat (this)** | **96** | **496** | **no** |

Shared dirt **improves** independent one-repeat (`112 → 96`) but does **not**
undercut the shared-dirt distinct floor `82`, and still cannot undercut the
six-query endpoint under the PR1898 abstract tariff.

## Scope limits

- Fixes the **shared-dirt one-repeat** partitioned dual interface at total
  `Q=8` on shape `(2,6)`. Same-walk, dirty-shadow, distinct partitioned,
  one-repeat independent, two-repeat, three-repeat, shared-dirt distinct, and
  Q=9 partitioned leave-alones are outside and not edited.
- Soft-overlap with deferred shared-XOR is avoided: R-side dirt coupling only.
- No new kappa and no multiplication theorem are claimed.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
