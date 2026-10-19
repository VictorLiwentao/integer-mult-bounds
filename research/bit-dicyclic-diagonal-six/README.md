# Depth-six Dic_3 diagonal layer: no sharing for direct bill ≥ 7

**Scoped exact negative result; no new kappa.** In the same paid alphabet as
[`bit-dicyclic-diagonal-seed620ca`](../bit-dicyclic-diagonal-seed620ca/README.md),
every diagonal triple whose positive-generator direct bill is at least **7**
has **no** paid word of length at most **6**. This answers that package's open
next question. Preferred #2687 / #2888 paths were not grounded in this budget;
the card is a disjoint #840-style finite layer outside dirty-role / dihedral /
PR2298 / Norm leave-alones.

## Model (unchanged from predecessor)

Dicyclic group of order 12

\[
\mathrm{Dic}_3=\langle u,v\mid u^6=e,\ v^2=u^3,\ vuv^{-1}=u^{-1}\rangle
\]

in `F2[Dic_3]`. Paid operations are `D_N([g])=I+([g]+[e])N` on three registers
with `g∈{u,v}` and `N` one of the **28** rank-one idempotents (`56` paid types).
The direct bill of `diag([w0],[w1],[w2])` is the sum of shortest positive
`{u,v}` spellings of each `wi`.

## Result

| Layer | Direct bill | Word cap | Endpoints | Hits |
|---|---:|---:|---:|---:|
| Predecessor depth 4 | ≥5 | 4 | 1482 | 0 |
| Predecessor depth 5 | ≥6 | 5 | 1230 | 0 |
| **This package depth 6** | **≥7** | **6** | **890** | **0** |

Exact meet-in-the-middle over the **94,727** distinct products through depth
three (histogram `[1,56,2352,92318]`): every word of length ≤6 splits as a
prefix and suffix each of length ≤3. Coverage SHA-256 is recorded in
[CERTIFICATE.json](CERTIFICATE.json). No new kappa; selected
`κ = 0.001672660197076918` is unchanged.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/bit-dicyclic-diagonal-six/verify.py
python3.12 -I -O -Werror -B research/bit-dicyclic-diagonal-six/verify.py
python3.12 -I -B research/bit-dicyclic-diagonal-six/independent.py
python3.12 -I -B research/bit-dicyclic-diagonal-six/test_package.py
python3.12 -B scripts/research_package.py --package research/bit-dicyclic-diagonal-six
```

Expected:

```text
PASS_BIT_DICYCLIC_DIAGONAL_SIX group=Dic_3 registers=3 ops=56 products=94727 eligible=890 hits=0 misses=890 max_calls=6 min_direct=7 no_new_kappa
PASS_INDEPENDENT_BIT_DICYCLIC_DIAGONAL_SIX group=Dic_3 products=94727 eligible=890 hits=0 misses=890 no_new_kappa
PASS_BIT_DICYCLIC_DIAGONAL_SIX_PACKAGE_TESTS groups=5
PASS_REGISTERED_RESEARCH_PACKAGE research/bit-dicyclic-diagonal-six outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()`; `-O` also passes.

## Scope and overlap

Base commit `bb4bccbf42844d2801487450727c2f63e10d1d0f` (CrocSwap/main). Soft
overlap with the predecessor is intentional semantic succession (same alphabet;
new depth-6 / bill≥7 layer), not a template retarget of dirty-role / dihedral /
PR2298 / Norm cascades. Does not edit the predecessor package tree.

## Open next questions

1. Does any diagonal triple with direct bill at least 8 admit a word of length
   at most 7 in this same alphabet?
2. Is there an algebraic invariant proving no saving for all depths?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit Cinna Davis / the predecessor dicyclic diagonal package for
the alphabet, depth-4/5 layers, and the OQ answered here. No independent human
review is claimed. No new kappa.
