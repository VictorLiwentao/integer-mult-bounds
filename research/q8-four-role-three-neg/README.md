# Four-role three-negative Q8 targets cost nine calls

**Scoped exact cost; no new kappa.** On exactly four roles, every diagonal
endpoint with three entries in `{zi,zj}` and one restored identity needs
**exactly nine** positive `i/j` calls. The direct construction attains
nine. Parity rules out eight. An exhaustive meet-in-the-middle finds no
word of length at most seven.

This is the four-role case left open by
[`research/q8-multiple-negative-census`](../q8-multiple-negative-census/README.md):
three roles are already nine, and that package's validation states that
four-role three-negative targets are unclaimed. It does not decide the
arbitrary-workspace question left by
[`research/q8-short-negative-gram`](../q8-short-negative-gram/README.md),
which still allows a seven-call word on five roles.

```sh
python3.12 -I -B research/q8-four-role-three-neg/verify.py
```

Expected:

```text
PASS_Q8_FOUR_ROLE_THREE_NEG r4_hits=0+0 minimum=9 r3_333_hits=0 r3_332_hits=6774 no_new_kappa
```

The meet stores 6,735,641 inverse states and tests 1,623,289,481 candidates
on each of the representatives `3330` and `3350`. Wall time is a few
minutes. Python 3.12 and a C++20 compiler are required. Standard-library
Python only.

## Costs

| Endpoint class | Calls | Status |
|---|---:|---|
| Four roles, three negative targets, one identity | 9 | exact minimum, this package |
| Three roles, three negative targets | 9 | cited census, recomputed as a 0-hit control |
| Three roles, two negative targets (`332`) | 7 | cited census, recomputed as a 6774-hit control |

The nine-call word multiplies each negative role by `i` or `j` three
times and never touches the spectator. All 32 ordered targets reduce to
`3330` or `3350` by role permutation and the `i↔j` automorphism. Both
reductions preserve the paid alphabet. [PROOF.md](PROOF.md) records the
argument.

Selected κ stays `0.001672660197076918`.

## Reproduce

```sh
python3.12 -I -B research/q8-four-role-three-neg/verify.py
python3.12 -I -O -Werror -B research/q8-four-role-three-neg/verify.py
python3.12 -I -B research/q8-four-role-three-neg/independent.py
python3.12 -I -B research/q8-four-role-three-neg/test_package.py
python3.12 -B scripts/research_package.py --package research/q8-four-role-three-neg
```

`verify.py` is read-only: it compiles into a private temporary directory
and deletes the binary. Admission uses `need()` and still fires under
`-O`. The independent replay checks the 32 nine-call words, the orbit
map and the depth-2 ball size 42,041 with a quaternion multiplication
table. It does not repeat the length-7 meet.

## Open next questions

1. Does the nine-call minimum survive at five roles, and therefore for
   arbitrary finite restored dirty workspace? A seven-call word there
   would still be compatible with the scalar core's two dirty blocks.
   First step: the same 3+4 meet on one five-role representative, or a
   sign-sensitive invariant. Blocked by the size of the five-role
   depth-3 ball.
2. Can a physical caller use the nine-call word at a favorable complete
   invoice? First step: bind one eight-block layout and its restoration.
   Blocked by the absence of any caller in this package.

## Credit

Nick Petalas's multiple-negative census supplies the three-role nine-call
minimum and the meet-in-the-middle pattern used here. The short-negative
Gram note supplies the seven-versus-nine gap at arbitrary width; this
package decides only four roles. Aaron Wang, Cinna Davis, ywz65 and the
register-model lineage remain the predecessors of that census.

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance,
under Apache-2.0.
