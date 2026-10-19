# No two-target UT4 central word has n_b = 6

In the formal group-algebra model of
[CrocSwap/integer-mult-bounds#1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662),
every legal word realizing two central targets satisfies `n_b >= 6`. This note
proves the complementary statement:

> No legal word equal to `I+([z]+1)I_2`, of any finite length and on any finite
> restored dirty workspace, has exactly six paid `b` factors.

The case `n_b = 7` is left open. There is no new κ; the selected decimal
`0.001672660197076918` is unchanged.

## 1. Model and inherited rank bound

Let `G = UT4(F2)` with `a = I+E12`, `b = I+E23`, `c = I+E34`, `z = I+E14`, and
work in `R = F2[G]`. On `r >= 2` roles a paid factor is
`I + ([g]+1) x y^T` with `g in {a,b,c}` and `x y^T` a nonzero binary rank-one
coupling (idempotent or nilpotent). The target is `T = I + ([z]+1) P` with
`P = diag(I_2, 0_(r-2))`. Scalar `GL_r(F2)` mixing is free and normalized into
the couplings; every occurrence, including restoration, is counted.

Use the fixed 17-dimensional quotient

```
Q = F2<a,b,c>/(a^2,b^2,c^2,ac-ca, deg >= 4)
```

of #1662, with `z |-> 1+abc+acb+bac+cba`. Necessary conditions on a realizing
word include vanishing of all degree-1/2 and non-target degree-3 coefficients
in `Mat_r(Q)`, and coefficient `P` on `abc, acb, bac, cba`.

Write `B_j = x_j y_j^T` for the six middle couplings in product order, and set

```
X = [x_j] (r x 6),   Y = [y_j^T] (6 x r).
```

#1662 gives `XY = 0` and `n_b >= 2 + rank X + rank Y` from the factorization of
`UV` through `ker X / im Y`, together with `rank X, rank Y >= 2` from the `bac`
and `acb` coefficients. At `n_b = 6` this forces

```
rank X = rank Y = 2.
```

In particular every middle coupling is supported on a fixed 2-dimensional
active plane `H` (after a free `GL_r` change of basis that places `P` in the
leading block). Write `e_b^x = e_b^y = 0` for this vanishing middle excess.

## 2. Reduction to two active roles

With all six `b`-couplings in `H x H`, an interior dirty contraction
`v_i(u_{i+1})` in a degree-`<=3` product can involve only `a` and `c` calls:
any factor that is a `b` call has zero dirty row and column, so contractions
against `b` see only the active block. Same-label dirty contractions between
two `a` calls (resp. two `c` calls) vanish in `R` because `([a]+1)^2 = 0`
(resp. `([c]+1)^2 = 0`).

Consequently the monomials that use only `{a,b}` or only `{c,b}`, and the
cross monomials `abc` and `cba` (which never place `a` adjacent to `c`),
receive no interior dirty contribution. Their active `H x H` blocks are
exactly the two-role coefficients computed from:

- the six active middle couplings (a zero-sum sequence in the nine nonzero
  rank-one `2 x 2` matrices);
- the active prefix sums `P_j` of `a`-couplings before each middle call;
- the active suffix sums `Q_j` of `c`-couplings after each middle call.

Unrestricted outer length means every 6-tuple of `2 x 2` matrices arises as
such a profile for some finite `n_a` (resp. `n_c`): each gap increment has
rank at most two and is a sum of at most two rank-one couplings.

Therefore a realizing word with `n_b = 6` on any `r >= 2` yields a two-role
profile pair with

```
(ab, ba, aba, bab) = (0,0,0,0),
(cb, bc, cbc, bcb) = (0,0,0,0),
(abc, cba) = (I_2, I_2).
```

(The remaining target equations `acb = bac = I_2` are not needed for the
obstruction below.)

## 3. Finite census on two roles

Conjugation by `GL_2(F2)` fixes the two-role target `I_2` and acts on middle
sequences. There are 33,489 zero-sum length-6 sequences of nonzero rank-one
`2 x 2` matrices; they form 5,582 conjugation-minimal orbits (the same count
as in #1690 / #1816). Of these, 182 have `rank X < 2` or `rank Y < 2` and are
excluded by Section 1. The remaining **5,400** middles are searched.

For each middle, the side-zero profiles are collected by a 3+3 meet-in-the-middle
on the packed side table of #1690. Each side-zero profile determines a
transport key `(U_0,U_1,W_0,W_1)` whose bits record `(P_j x_j)` and
`(y_j^T P_j)`. The identity cross condition `abc = cba = I_2` is exactly
the key-pairing equation of #1690 with target packing `9 = I_2`.

**Result.** Across all 5,400 rank-adequate middles the set of side-zero keys
admits **zero** pairs with `abc = cba = I_2`. Certificate counts:

| Quantity | Count |
|---|---:|
| Canonical zero-sum middles | 5,582 |
| With `rank X,Y >= 2` | 5,400 |
| Sum of side-zero key cardinalities | 1,568,064 |
| Key pairs with `abc = cba = I_2` | **0** |

A low-rank control middle `(E_{11})^6` still produces many identity key pairs,
so the screen is not vacuous: the obstruction is the rank-2 constraint
together with the side-zero locus.

## 4. Conclusion

No two-role profile pair meets the necessary quotient conditions of Section 2.
By the dirty-contraction reduction, no word on any finite `r >= 2` with
`n_b = 6` reaches the degree-three quotient endpoint, hence none equals the
formal target. Combined with #1662's bound `n_b >= 6`, every legal two-target
word satisfies `n_b >= 7`.

The value `n_b = 7` is not decided here.

## Credit

Model and separate-label bound: #1662 (@ToikY). Unit-tariff exactness and the
weighted open question that motivates this package: #1816. Profile/key pipeline:
#1690 (Aaron Wang / @navinor), as used by #1816. Workspace compression context:
#1680. Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
