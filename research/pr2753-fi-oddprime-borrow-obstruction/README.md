# Odd-prime borrowed Incoming is not wrapper F_I

**Research construction / recursive interface; no new kappa.** Answers open
question 1 of
[`selected-lcm-stock-wrapper-fit`](../selected-lcm-stock-wrapper-fit/README.md)
(#2888) for the natural source-bound odd-prime program: under the merged outer
borrowing wrapper's **two-call** schedule at prime `q=3` with borrowed width
`(R,S,R')=(27,24,48)`, PR2753 LowCodes `GL_2(F_3)` unweighted `Incoming` does
**not** realize the wrapper's unweighted

```text
F_I(H,D) = (C D, C H).
```

| Check | Result |
|---|---|
| `\|GL_2(F_3)\|=48`; `3^k` never divisible by 48 | arithmetic PASS |
| Same fixture with wrapper `model_callee` | full interchange PASS |
| Incoming per-call F_I mismatches | **40824 / 104976** |
| Mismatch support | genuine rows `{6..26}` only (21×1944); padded `{27..47}` and `{0..5}` match |
| Wrapper endpoint | rejects Incoming |

This is not the deferred GL2(F3) identity-weight single-call pad (definitional
`A=(1,1)⇒F_I` on the flat gap-1 fixture). The load-bearing fact is the
**wrapper two-call / borrowed-width** census against `model_callee`.

Root coupling, numerical arenas, physical placement and selected GL64 admission
remain open. No new kappa.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/pr2753-fi-oddprime-borrow-obstruction/verify.py
python3.12 -I -O -Werror -B research/pr2753-fi-oddprime-borrow-obstruction/verify.py
python3.12 -I -B research/pr2753-fi-oddprime-borrow-obstruction/independent.py
python3.12 -I -B research/pr2753-fi-oddprime-borrow-obstruction/test_package.py
python3.12 -B scripts/research_package.py --package research/pr2753-fi-oddprime-borrow-obstruction
```

Expected:

```text
PASS_PR2753_FI_ODDPRIME_BORROW_OBSTRUCTION bad=40824/104976 bad_rows=6..26 model_callee=PASS three_pow_never_div_48 no_new_kappa
PASS_INDEPENDENT_PR2753_FI_ODDPRIME_BORROW_OBSTRUCTION gl=48 three_pow_never_div_48 bad_identity=21*1944 … no_new_kappa
PASS_PR2753_FI_ODDPRIME_BORROW_OBSTRUCTION_PACKAGE_TESTS groups=5
PASS_REGISTERED_RESEARCH_PACKAGE research/pr2753-fi-oddprime-borrow-obstruction outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()`; `-O` also passes.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap/main). Closest
priors: #2888 OQ1 (callee open); outer borrowing wrapper F_I contract and q=2
Incoming integration; compatible-row padding; deferred
`pr2753-fi-callee-identity-pad` (flat identity pad — leave alone). Soft-overlap
with that deferred package is complementary (flat equality vs wrapper
borrowed-width inequality), not a weight-specialization retarget.

Does not reopen leave-alone PR2809 cascades, outer-wrapper multiplicity
padding, route-cube scaffolds, or odd-kernel BIT-supplier screens.

## Open next questions

1. Is there a source-bound odd-prime Incoming (different low vocabulary or
   fitted `k` with `R` aligned to the callee's row factor) that matches wrapper
   `F_I` under the two-call schedule with `R'>R`? First pin such a program and
   rerun the padded-column census. Blocked by root coupling / GL64 admission.
2. Can the mismatch support `{6..26}` be derived from the LowCodes ranking
   without enumerating all 104976 columns? First relate the cut at row 6 to the
   low-matrix unranking. Blocked by a missing structural lemma in the Node
   addressing / gap=`R` interaction.

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit David Arias (PR2753), Nick Petalas (padding / outer wrapper),
jwr404 (#2888). No independent human review is claimed. No new kappa.
