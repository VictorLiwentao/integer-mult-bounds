# Identity-weight PR2753 Node is the wrapper F_I under padding

**Research construction / recursive interface; no new kappa.** Answers the
first step of open question 1 in
[`selected-lcm-stock-wrapper-fit`](../selected-lcm-stock-wrapper-fit/README.md)
(#2888): pin one PR2753 incoming program and compare its endpoint, row
restoration and borrowed heads with the merged outer wrapper's unweighted
`F_I` contract.

The published
[`selected-compatible-row-padding`](../selected-compatible-row-padding/)
integration uses weights `A=(2,1)` on the one-family GL2(F3) fixture. That
endpoint is an involutive weighted reverse, **not** the wrapper's unweighted

```text
F_I(H,D) = (C D, C H)
```

(with `C` reversing atom coordinates). This package specialises the same
authenticated PR2753 Node + `padding.complete` harness to identity weights
`A=(1,1)` and checks:

| Check | Result |
|---|---|
| Identity `A=(1,1)` Node under padding vs F_I on 49×81 genuine columns | 0 mismatches |
| Published `A=(2,1)` destination vs F_I (oracle) | 3528 mismatches (=49×72) |
| Fitted multiplicity `t=2` (`R=96`, `S=48`, `added=0`) vs F_I | 0 mismatches |
| `plan_rows` Counter live peak on exact multiples `t=1..16` | peak **2**, independent of `t` |

Root coupling, numerical arenas, physical tape placement and selected odd-prime
GL64 admission remain open. The q=2 outer-wrapper toy is not used.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/pr2753-fi-callee-identity-pad/verify.py
python3.12 -I -O -B research/pr2753-fi-callee-identity-pad/verify.py
python3.12 -I -B research/pr2753-fi-callee-identity-pad/independent.py
python3.12 -I -B research/pr2753-fi-callee-identity-pad/test_package.py
python3.12 -B scripts/research_package.py --package research/pr2753-fi-callee-identity-pad
```

Expected:

```text
PASS_PR2753_FI_CALLEE_IDENTITY_PAD identity=F_I fi_bad=0 weighted_oracle_fi_bad=3528 t2_added=0 counter_peak=2 no_new_kappa
PASS_INDEPENDENT_PR2753_FI_CALLEE_IDENTITY_PAD body_diffs=72 oracle=3528 counter_peak=2 no_new_kappa
PASS_PR2753_FI_CALLEE_IDENTITY_PAD_PACKAGE_TESTS groups=4
PASS_REGISTERED_RESEARCH_PACKAGE research/pr2753-fi-callee-identity-pad outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()`; `-O` also passes.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap/main). Closest
priors: #2888 lcm stock fit (callee open); outer borrowing wrapper F_I contract;
compatible-row padding with published weighted `(2,1)` integration. Soft-overlap
reuses the padding harness but changes the load-bearing weight specialisation
and adds fitted-multiplicity metadata; it is not a numerical padding or
`log_q t` unit-fit corollary (those were DEFER'd separately).

Does not reopen leave-alone PR2809 annotation cascades, outer-wrapper
multiplicity padding, route-cube fibre/key scaffolds, or odd-kernel BIT-supplier
screens.

## Open next questions

1. Does the same identity-weight equality hold for a source-bound odd-prime
   GL64 unweighted incoming program with fitted `k` and constructed `S`?
   First pin one PR2753 odd-prime program and compare padded-row restoration
   under the wrapper's two-call schedule. Blocked by root coupling, numerical
   arenas and physical placement.
2. Can the `plan_rows` Counter/Count streams (peak 2 on exact multiples) be
   placed in the physical caller's fixed tape inventory for fitted `t>1`?
   First serialize locations, heads and blank-return with the Frame/bank
   investigation. Blocked by the pending fixed-physical-tape caller.

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit David Arias (PR2753), Nick Petalas (padding / outer wrapper),
jwr404 (#2888). No independent human review is claimed. No new kappa.
