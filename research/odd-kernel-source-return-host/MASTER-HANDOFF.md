# MASTER-HANDOFF — odd-kernel-source-return-host

## Claim (one sentence)

Under the named immutable-source / exclusive-target admitted-screen host bill,
`I=0` recovers zero odd fused beats of dyadic on `j=0..32`, while unit routing
`I=1` yields exactly one beat at `(q=3,j=0)` (`674<677`) with critical
`I*=14/17` (answers #2687 OQ1 first step).

## Closest prior

- #2687 / `research/odd-kernel-query-pair` — exclusion pattern; OQ1 left open
- #3702 / `research/odd-kernel-coeff-bit-tariff` — coeff-bit `I=0` subsystem (open; leave alone)
- Deferred `research/odd-kernel-alt-tariff-census/` — alternate `T_word` shortlist (leave alone)
- PR840 / `research/dyadic-query-pair` — fusion + source-return contracts in eq. (6)

## New checkable fact

Named host bill `H_fused` / `H_baseline` with units `C,X,D,R_SR` and admitted-screen
term `I·A(q)` on `SCREEN=odd moduli [3,99]`; `I=0` zero beats; `I*=14/17`; unique
`I=1` beat `(3,0)`; `I=2` has 33 `q=3` beats; fusion save `210+2T(a)-T(2a)>0`.

## Evidence commands

```sh
python3.12 -I -B research/odd-kernel-source-return-host/verify.py
python3.12 -I -O -Werror -B research/odd-kernel-source-return-host/verify.py
python3.12 -I -B research/odd-kernel-source-return-host/independent.py
python3.12 -I -B research/odd-kernel-source-return-host/test_package.py
python3.12 -B scripts/research_package.py --package research/odd-kernel-source-return-host
```

## Soft-overlap vs leave-alones

Clear of flag-0 / stock / gate-operand / C5 / side-correction / present-head /
groups B–D / deferred alt-tariff census. Touches the #840/#2687 cascade at the
unanswered OQ1 hosting bill. Soft-overlap with #3702 is intentional `T_word`
reuse as the `I=0` prep subsystem; the new fact is admitted-screen routing that
**can reverse** odd-vs-dyadic (not another alternate-`T_word` shortlist).

## Attribution

Author Wentao Li `<wentaol4@illinois.edu>`. Neutral AI assistance disclosure.
No `Co-authored-by: Victor Li`. No CrocSwap PR from this worker (master publishes).

## Disposition

Ready for master independent review / publish decision. Kappa unchanged
(`0.001672660197076918`).
