# Scale-normalize the failing weighted callee P_(2,1)

**Research construction / recursive interface; no new kappa.** Answers open
question 1 of
[`weighted-wrapper-contract`](../weighted-wrapper-contract/README.md): can a
proposed weighted callee be normalized at an affordable complete cost?

On `G=(Z/3Z)^2` the pinned failing weights `a=(2,1)` give `P^2=2I≠I`, so the
ordinary two-call wrapper rejects (exact raw agreements **9/81** by formula
(5)). Left-diagonal post-scales `T=diag(1,2)` produce involutory
`P'=TP` with `(P')^2=I`. Composing each `F_a` call by those two output
multiplies realizes `F_{P'}` and the wrapper attains interchange `J` on
**81/81** pairs.

| Item | Raw `F_(2,1)` twice | Normalized `Norm∘F_(2,1)` twice |
|---|---:|---:|
| Agreements with `J` | 9 / 81 | 81 / 81 |
| Modular multiplies (scales) | 0 | **36 = 4V** |
| Input restores | 0 | 0 |
| Weight-table rewrites | — | 0 (weights stay `(2,1)`) |

No new kappa. Selected κ stays `0.001672660197076918`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/weighted-callee-scale-normalization/verify.py
python3.12 -I -O -Werror -B research/weighted-callee-scale-normalization/verify.py
python3.12 -I -B research/weighted-callee-scale-normalization/independent.py
python3.12 -I -B research/weighted-callee-scale-normalization/test_package.py
python3.12 -B scripts/research_package.py --package research/weighted-callee-scale-normalization
```

Expected:

```text
PASS_WEIGHTED_CALLEE_SCALE_NORMALIZATION M=3 n=2 a=(2,1) raw_agreements=9/81 normalized_agreements=81/81 scales_two_F=36 no_new_kappa
PASS_INDEPENDENT_WEIGHTED_CALLEE_SCALE_NORMALIZATION raw=9/81 normalized=81/81 scales_two_F=36 no_new_kappa
PASS_WEIGHTED_CALLEE_SCALE_NORMALIZATION_PACKAGE_TESTS groups=5
PASS_REGISTERED_RESEARCH_PACKAGE research/weighted-callee-scale-normalization outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()`; `-O` also passes.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap/main). Closest
prior: `weighted-wrapper-contract` (Theorem 1 / formula (5); OQ1 answered here).
Freestanding normalization invoice; does not edit that package.

Clear of leave-alones: not a GL2(F3)/wrapper-toy `F_I` census, not odd-kernel
BIT-supplier/tariff/run retarget, not PR2809/priced-park, not route-cube, not
UT4 unfinished, not stock-envelope/finite-C/rho, not gate-operand dest-absent.

Soft-overlap vs `weighted-wrapper-contract` is intentional semantic successor
(answers its OQ1), not a ~0.9 scaffold retarget of an already-closed claim.

## Open next questions

1. Does the same left-diagonal post-scale pattern normalize the precision-blind
   family `a=(1+p^{w-1},1)` on `(Z/p^wZ)^2` with bill still `4V`, or does the
   `p`-power force a wider scale support? First expand `P'=TP` at `p=3,w=2`.
   Blocked by a missing all-`w` scale lemma.
2. Can the `4V` algebraic bill be lowered onto a literal Boolean payload meter
   in the unchanged PR2808 harness without rewriting weights? First attach
   scale meters to one modulo-3 fixture. Blocked by harness instrumentation.

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit Jerry Chen (@CubeJerry) for `weighted-wrapper-contract`
Theorem 1 / formula (5); Nick Petalas for PR2808's ordinary wrapper. No
independent human review is claimed. No new kappa.
