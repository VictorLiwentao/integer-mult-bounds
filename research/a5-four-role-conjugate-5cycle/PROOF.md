# Proof sketch: four-role A5 conjugate 5-cycle minimum remains four

**Model.** Let `x=(1 2)(3 4)` and `y=(1 3 5)` in `A5`, so
`x^2=y^3=(xy)^5=e`. Work in the full formal group algebra `F2[A5]`. Paid
factors are

```text
D_N(g) = I + ([g] + [e]) N,   g ∈ {x,y},
```

where `N=u v^T` ranges over all 120 rank-one idempotents of `M4(F2)`. The
target is

```text
diag([xy], [yx], [e], [e]).
```

All four registers have arbitrary dirty inputs; equality of every group-algebra
coefficient certifies the formal endpoint for every input. There are no free
scalar maps between factors in this model (equivalently, free `GL4(F2)` mixes
only conjugate projectors already included).

**Upper bound.** The direct word

```text
D_E11(x) D_E11(y) D_E22(y) D_E22(x)
```

equals the target and restores both spectator diagonals to `[e]`. Hence the
minimum is at most four.

**Lower bound.** The forward breadth-first search from the identity through
paid depth three, over all 240 factors, produces layer sizes

```text
[1, 240, 37285, 5150035]
```

and **zero** hits on the target. Therefore no word of length `≤3` realizes the
endpoint, so the minimum is exactly four.

**Independence.** An independent engine rebuilds `A5` as the set of all even
permutations of `{0,1,2,3,4}`, rebuilds projectors as `u v^T` with
`v^T u=1`, and repeats the same BFS. Layer sizes, hit counts, and the direct
word agree. The group-element SHA-256 digest matches the predecessor package
`research/a5-conjugate-5cycle-seedd316f8`.

**Limits.** This is a finite formal-algebra theorem for four roles only. It
does not supply an all-roles invariant, a native BIT-supplier map, or a new
kappa. Selected κ remains `0.001672660197076918`.
