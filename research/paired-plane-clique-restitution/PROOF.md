# Quotient-collision restitution

**Hypothesis (quotient-collision restitution).** Let S be a set of the 56 PR1825 matched planes whose joint F2 pairing has rank at most 2. One one-array total on S can then be charged strictly less than `2|S|`. The hypothesis says a signed sum of one-array totals realizes the strict identity on S for complete-plane copy mass strictly less than `4|S|`.

**Theorem.** The hypothesis is false over every field. Every finite one-total factorization of that induced strict identity has complete-plane copy mass at least `4|S|`.

## Setup

The 112 selected labels and the PR1825 matching determine 56 planes. Each plane has Gram matrix I2, so its own pairing rank is 2. Two planes are orthogonal when all four basis pairings vanish. A plane is not orthogonal to itself.

A matrix fits the strict mask when its diagonal is 1 and `K_ij = 0` whenever `i ≠ j` and the planes of `i` and `j` are not orthogonal. On a pairwise non-orthogonal set there are no free entries, so the principal submatrix is exactly the identity on the `2|S|` ports.

A one-total is a rank-1 update `c u v^T`. Its source planes are the planes on which `u` is nonzero, and its reader planes are those on which `v` is nonzero. Touching any port of a plane includes the whole plane. The complete-plane charge is the F2 rank of the dot product between those two spans. Adding further planes cannot lower that rank. The copy mass of a factorization is the sum of the charges.

## The collisions

A set collides when the pairing on the sum of its planes has rank at most 2. The verifier checks every pair, every triple, and every 4-plane set:

- 144 pairs have joint form rank 2. Each is a conflict clique.
- 8 triples have joint form rank 2. Each is a conflict clique. The first is `[5, 15, 30]`.
- No 4-plane set has joint form rank 2.

On each of those 152 sets, every nonempty choice of source planes and reader planes has pairing rank at least 2. That includes one-sided choices, where the source planes and the reader planes are disjoint. A single total on the whole set is charged 2, which is strictly less than `2|S|` once `|S| ≥ 2`.

There are also 879 non-orthogonal pairs whose cross-pairing rank is 1, including 173 pairs inside the checked 24-plane conflict clique. Those supports are outside the hypothesis: a one-sided total there can be charged 1, and this package does not price them at 4 per plane.

## Restitution

Fix a colliding set S. Its principal submatrix is `I_{2|S|}`, which has rank `2|S|`. Any sum of rank-1 matrices equaling that block uses at least `2|S|` summands whose restrictions to the block are nonzero. Each such summand has nonempty source and reader intersection with S. The charge of the summand is at least the pairing rank of those two intersections, hence at least 2. Summands that miss the block do not contribute to this count.

The copy mass is therefore at least

```text
(2|S|) * 2 = 4|S|.
```

A joint total charged 2, rather than `2|S|`, does not reduce the sum. The identity still demands `2|S|` nonzero contributions, and every legal support inside S pays at least 2. Cancellation cannot delete that term count: the rank of a sum is at most the number of rank-1 summands.

Every form-rank-2 pair therefore costs at least 8, and every form-rank-2 triple costs at least 12. The singleton schedule, one rank-2 total on each of the 112 ports, attains global copy mass 224 and realizes the strict identity with every cross entry zero. Its favorable moment is

```text
(71*896 + 9*224) / (73*896) = 293/292 > 1.
```

## What is not claimed

The same arithmetic does not apply to an arbitrary conflict clique. The checked 24-plane clique is pairwise non-orthogonal, but it contains cross-rank-1 pairs, so a one-sided total can be charged 1. This package does not conclude that the clique costs 96, and it does not conclude that every sharing of all 56 blocks pays 224.

Orthogonal-only totals are the complementary regime already priced by the one-plane bill: pairwise orthogonal planes are disjoint here and contribute form rank exactly 2 per plane. That bill is not restated as a new theorem.

No new κ is claimed. The selected decimal remains `0.001672660197076918`.
