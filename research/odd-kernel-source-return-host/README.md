# Source-return host bill: odd-kernel shear vs dyadic

**Research construction / recursive interface; no new kappa.** Answers open
question 1 of
[#2687](https://github.com/CrocSwap/integer-mult-bounds/pull/2687)
(`research/odd-kernel-query-pair`) at its stated first step: name one exact
immutable-source / exclusive-target **source-return host bill** that charges
routing, precision and dispatch, then compare certified odd kernels to dyadic.

```text
H_fused(q,j;I) = 3C + 2X + 18D + R_SR + T_fused(q,j) + I·A(q)
```

with `C=100`, `X=40`, `D=5`, `R_SR=30`, `T_fused` the ADDRESS coefficient-bit
prep of the fused three-query power list, `SCREEN` = odd moduli in `[3,99]`
(`|SCREEN|=49`), and `A(q)=|{m∈SCREEN: gcd(m,q)=1}|`.

| Instantiate tariff `I` | Odd fused beats of dyadic on `j=0..32` |
|---:|---|
| `0` (coeff-only; recovers `#3702` subsystem) | **0** |
| `1` (unit admitted-screen routing) | **1** — exactly `(q=3,j=0)` at `674<677` |
| `2` | **33** — all `j` at `q=3` |

Critical threshold: `I*=14/17` at `(3,0)`. Fusion always beats baseline on the
grid (`save = 210 + 2 T(a) - T(2a) > 0`).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/odd-kernel-source-return-host/verify.py
python3.12 -I -O -Werror -B research/odd-kernel-source-return-host/verify.py
python3.12 -I -B research/odd-kernel-source-return-host/independent.py
python3.12 -I -B research/odd-kernel-source-return-host/test_package.py
python3.12 -B scripts/research_package.py --package research/odd-kernel-source-return-host
```

Expected:

```text
PASS_ODD_KERNEL_SOURCE_RETURN_HOST kernels=[1, 3, 5, 7, 9, 15] j=0..32 I0_beats=0 I1_beats=1 critical_I=14/17 first_beat=(3,0) no_new_kappa
PASS_ODD_KERNEL_SOURCE_RETURN_HOST_INDEPENDENT I0_beats=0 I1_beats=1 critical_I=14/17 first_beat=(3,0) no_new_kappa
PASS_ODD_KERNEL_SOURCE_RETURN_HOST_PACKAGE_TESTS groups=4
PASS_REGISTERED_RESEARCH_PACKAGE research/odd-kernel-source-return-host outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Direct predecessor:
[#2687](https://github.com/CrocSwap/integer-mult-bounds/pull/2687) OQ1.
Complementary open [#3702](https://github.com/CrocSwap/integer-mult-bounds/pull/3702)
is the `I=0` coefficient-bit subsystem (leave alone; intentionally reused as
prep, not retargeted). Clear of deferred
`research/odd-kernel-alt-tariff-census/` (alternate `T_word` shortlist), flag-0 /
stock / gate-operand / C5 / side-correction leave-alones. Does not edit
`#2687` / `#2593` / PR840 package trees.

## Open next questions

1. Does a supported production BIT supplier expose a common admitted-modulus
   screen whose instantiate/routing tariff matches `I·A(q)` closely enough that
   the `(q=3,j=0)` undercut survives after frames, precision envelopes and owner
   schedules?
2. For which alternate screens (prime-only, prime-power widths, or larger odd
   ranges) does the first critical `I*` move above or below `1`?

Structured blockers are in [TASK.json](TASK.json).

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit #2687 OQ1, PR840 / `dyadic-query-pair`, #2593, and the
ADDRESS / DATA-shear lineage (PR521/PR677). No independent human review is
claimed. No new kappa.
