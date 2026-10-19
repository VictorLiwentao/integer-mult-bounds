# Two dirty A5 spectators do not lower the conjugate 5-cycle minimum

**Research construction / finite exact minimum; no new kappa.** Extends the
two- and three-role theorem of
[`research/a5-conjugate-5cycle-seedd316f8`](../a5-conjugate-5cycle-seedd316f8/README.md)
to four roles: does a second arbitrary restored dirty spectator permit a
shared-call saving below the four-call bill for the conjugate 5-cycle pair?

**No.** In `M₄(F₂[A₅])` with target

```text
diag([xy], [yx], [e], [e]),
```

the exact paid-call minimum remains **four**:

- Paid labels `{x,y}` generating `A5` and all **120** rank-one idempotents of
  `M₄(F₂)` give **240** factors.
- Exact forward BFS covers every word of length `0..3`; layer sizes are
  `[1, 240, 37285, 5150035]` with **zero** target hits.
- The direct four-call word on roles `0..1` attains the target and restores
  both spectators to `[e]`.
- No length-`≤3` witness exists, so the minimum is exactly four.

This is a finite formal-algebra theorem, not a physical supplier invoice.
**No new kappa.** Selected κ stays `0.001672660197076918`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/a5-four-role-conjugate-5cycle/verify.py
python3.12 -I -O -Werror -B research/a5-four-role-conjugate-5cycle/verify.py
python3.12 -I -B research/a5-four-role-conjugate-5cycle/independent.py
python3.12 -I -B research/a5-four-role-conjugate-5cycle/test_package.py
python3.12 -B scripts/research_package.py --package research/a5-four-role-conjugate-5cycle
```

Expected:

```text
PASS_A5_FOUR_ROLE_CONJUGATE roles=4 calls=240 idempotents=120 target_minimum=4 ... dirty_lowers=false short_witness=none no_new_kappa
PASS_INDEPENDENT_A5_FOUR_ROLE_CONJUGATE roles=4 calls=240 target_minimum=4 ... hits=[0, 0, 0] dirty_lowers=false no_new_kappa
PASS_A5_FOUR_ROLE_CONJUGATE_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/a5-four-role-conjugate-5cycle outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes.

## Scope and overlap

Base commit `bb4bccbf42844d2801487450727c2f63e10d1d0f` (CrocSwap/main). Direct
predecessor: `a5-conjugate-5cycle-seedd316f8` (two-/three-role minimum 4;
spectator-role OQ answered here at width 4). Soft overlap ≈0.35–0.55 vs that
package (shared A5 alphabet and conjugate target; new four-role projectors,
second spectator, and 240-factor BFS). Clear of leave-alone #4084 S3
dirty-role, #4083 SL2(F3), #4078 dihedral nine-prime, odd-kernel / #2687 thin
tariff retargets, #2888 F_I GL2(F3) toys, precision-blind Norm, PR2298 §3,
UT4 unfinished, and PR2809 cascades.

Preferred #2687 admitted BIT-supplier and #2888 non-toy fitted-`k`/GL64
Incoming were not grounded within budget without repeating deferred thin
obstructions; this package takes the disjoint #840-style construction branch.

## Open next questions

1. Does an algebraic invariant give the same four-call floor for every finite
   number of arbitrary dirty spectator registers in this fixed `A5` alphabet?
2. Is there a priced native address-operation realization of this alphabet
   inside an admitted BIT supplier?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit the predecessor `a5-conjugate-5cycle-seedd316f8` for the
two-/three-role theorem and spectator OQ; PR840 construction pattern. No
independent human review is claimed. No new kappa.
