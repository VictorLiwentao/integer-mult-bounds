# Shared shears cannot undercut the six-query endpoint on R=82 seven-query schedules

Retain the five-source common-B mutable-source alphabet and the PR1898 abstract
complete-call tariff `(b,a,x)=(38,2,2)`. Connector prefixes live in `F₂⁵`. A
**path-lowered** schedule chooses a closed walk of length `Q`, reads each
nonzero mask on a minimum even subset of the visited slots, and implements each
multi-bit edge by compute/uncompute into one target source.

The pending 789q invoice shows that every path-lowered even-subset word with
`Q=7` and minimum readout cost `R=82` has path-local XOR count `X≥6`, so its
abstract tariff is at least `38·7 + 2·82 + 2·6 = 442 > 436`. Its open question 1
asks whether a **non-path** schedule — elementary source XORs interleaved
arbitrarily with queries, sources restored at the end — can realize some `R=82`
increment sequence with `X≤2` (tariff `434`) and beat the six-query endpoint.

## Interleaved model

Represent the live source basis by a 5-tuple of columns in `F₂⁵`, starting at
the identity. An elementary shear `X_(s,t)` replaces column `t` by
`column_t ⊕ column_s`. Querying physical source `j` emits the current column
`j` as the connector increment. The schedule must finish at the identity.

This strictly contains path-local compute/uncompute: the latter is the special
case that builds and immediately tears down each multi-bit edge.

## Restored length-two words

Every elementary shear is an involution. Exhaustive enumeration finds exactly
**20** restored words of length two: for each ordered pair `(s,t)` with
`s≠t`, the word `(X_(s,t), X_(s,t))`. No mixed pair restores. Each mid-state
exposes **exactly one** weight-2 column. Consequently any `X≤2` restored
schedule can present at most one distinct multi-bit increment value between
the two shears.

## Path-local X=6 class

There are `97216` six-subsets of `F₂⁵\{0}` with even-subset readout cost
`R=82` on slots `(0)∪S`. Among full-rank closed walks on those sets, exactly
`40320` attain the path-local minimum `X=6`. Their multi-bit increment patterns
are:

| weight pattern | count | repeated multi-bit values |
|---|---:|---:|
| three distinct weight-2 | 30240 | 0 |
| one weight-2 and one weight-3 | 10080 | 0 |

No such walk repeats a multi-bit increment, and every walk exposes at least two
distinct multi-bit values. The length-two classification already obstructs
`X≤2` on this class; the stronger `X≤3` bound is settled by census.

## Exhaustive interleaved census

For each of the `40320` increment sequences, a Cayley-ball search decides
whether a restored elementary-XOR walk of length at most `2` or `3` realizes
that sequence. The ball of radius `2` has `281` matrices; radius `3` has
`2851`. Both censuses return **zero** realizable sequences.

The 789q champion path `[0,1,2,6,12,24,16,0]` lies in the class. The same search
shows it is unrealizable at budgets `2` and `3`, and realizable at budget `6`,
so its interleaved minimum equals the path-local count `6`.

## Tariff consequence

Under `(38,2,2)` with `Q=7` and `R=82`,

| X | tariff | vs endpoint 436 |
|---:|---:|---|
| 2 | 434 | would beat |
| 3 | 436 | would tie |
| ≥4 | ≥438 | already above |
| 6 (attained path-local / champion interleaved) | 442 | +6 |

Because no schedule in the path-local-`X=6` class admits interleaved `X≤3`,
shared shear preparation cannot beat or tie the six-query endpoint on that
entire competitive class. This answers the concrete first step of the 789q
open question for every minimum path-local seven-query `R=82` walk.

## Scope

The census is for connector-prefix increment sequences coming from full-rank
closed walks with path-local `X=6` on `R=82` slot sets. Words whose path-local
`X` already exceeds `6` bill at least `446` under path-local lowering and are
not claimed here under interleaved shears. Readouts outside even-subset
schedules, non-elementary source maps, and physical supplier tariffs remain
outside scope. No new kappa.
