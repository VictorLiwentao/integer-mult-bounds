# Four roles force nine calls for three negative Q8 targets

Work in the formal group algebra `F2[Q8]`. Group elements are encoded
`1,z,i,zi,j,zj,k,zk` as digits `0..7`, with `i^2=j^2=z`, `z^2=1` and
`ji=z ij`. A paid factor is

```text
D = I + ([g]+1) u v^T,    g in {i,j},    v^T u = 1,
```

with binary vectors. Only scalar `GL_r(F2)` mixing is free. Every role
starts dirty. An identity-target role must return its input unchanged.

**Claim.** On exactly four roles, every diagonal endpoint with three
entries in `{zi,zj}` and one identity costs exactly nine positive `i/j`
calls. No new kappa is claimed. Five or more roles stay open.

## Upper bound

One factor with `u=v=e_a` and label `g` multiplies the coefficient of
role `a` by `g` and leaves every other role unchanged. Indeed

```text
D x = x + ([g]+1) x_a e_a,
```

so the `a`-component becomes `g x_a`. Since `i^3=zi` and `j^3=zj`, three
such factors on each negative-target role, and none on the identity
spectator, realize the endpoint in nine calls. Deleting any one call
changes that role's coefficient. The verifier checks all 32 ordered
targets and all 9 deletions of each word.

## Lower bound

Augmentation sends every paid factor and every diagonal group endpoint
to the identity, so a realizing word has odd length: each factor has
trace one and three negative targets have trace one. Length 8 is therefore
impossible. It remains to exclude lengths 1, 3, 5 and 7.

The three-role case is the published census in
`research/q8-multiple-negative-census`: no three-negative word through
length 7, and the direct word attains 9. This package recomputes that
exclusion (`333` has 0 hits) and the published two-negative attainment
(`332` has 6774 hits) as engine controls. It does not replace that proof.

For four roles the same meet-in-the-middle is run on two representatives.
A positive word of length at most 7 is a product `P Q` with `P` of length
at most 3 and `Q` of length at most 4. The inverse of a positive factor
is the same projector at `zi` or `zj`. The engine stores every state
reachable by at most three inverse factors (6,735,641 states, including
the identity), right-multiplies each by the target, and tests every
forward word of length at most 4 (the depth-3 forward ball, one extra
factor, 1,623,289,481 candidates). Both representatives return 0 hits.

## Symmetry

Two reductions cut the 32 ordered targets down to `3330` and `3350`.

1. Conjugation by a permutation matrix is free scalar mixing. It permutes
   diagonal entries and sends legal factors to legal factors, because
   `v^T u=1` is preserved. The identity spectator may therefore sit in
   the last coordinate.
2. The automorphism swapping `i` with `j` swaps `zi` with `zj` and
   preserves the paid alphabet. A target with more `zj` than `zi` reduces
   to one with at least as many `zi`.

After those moves, a single `zj` among the first three coordinates can be
placed last among them by another role permutation. The two remaining
shapes are all-`zi`, and two `zi` plus one `zj`.

## What is not proved

The scalar core in `research/q8-short-negative-gram` allows two essential
dirty blocks at seven calls, so a five-role word is not covered by a
four-role exclusion. This package does not decide arbitrary workspace,
does not re-prove the boundary-rank inequality `5n>=11t`, and supplies
no physical caller. The length-7 stream has one native implementation;
the independent replay checks the nine-call words, the 32-to-2 orbit
map and the depth-2 ball size 42,041, not a second copy of the full meet.
