# MASTER-HANDOFF — q8-four-role-three-neg

| Field | Content |
|---|---|
| Branch | `cursor/q8-four-role-three-neg-60b9` |
| Package | `research/q8-four-role-three-neg/` |
| Claim | At four roles, every diagonal Q8 endpoint with three entries in {zi, zj} and one restored identity costs exactly nine positive i/j calls (0 meet hits through length 7 on representatives 3330 and 3350; parity excludes 8; direct word attains 9). |
| Closest prior | `research/q8-multiple-negative-census` (three-role minimum 9; four-role three-negative explicitly unclaimed); `research/q8-short-negative-gram` (seven-versus-nine still open for arbitrary workspace) |
| New checkable fact | Four-role exact minimum 9; inverse ball 6735641; 1623289481 candidates per representative; 32 targets reduce to two orbits |
| Kappa | unchanged `0.001672660197076918` |
| Soft-overlap | Not odd-kernel / #3702 / #2687, not flag-0, not stock, not C5, not gate-operand, not groups B–D. Does not claim five-role or arbitrary-workspace exclusion. |
| Attribution | Wentao Li `<wentaol4@illinois.edu>`; substantial AI assistance; no `Co-authored-by: Victor Li` |
| CrocSwap PR | **Not opened** (master publishes) |

## PASS markers

```
PASS_Q8_FOUR_ROLE_THREE_NEG r4_hits=0+0 minimum=9 r3_333_hits=0 r3_332_hits=6774 no_new_kappa
PASS_Q8_FOUR_ROLE_THREE_NEG_INDEPENDENT witnesses=32 orbits=3330,3350 depth2=42041 no_new_kappa
PASS_Q8_FOUR_ROLE_THREE_NEG_PACKAGE_TESTS groups=3
PASS_REGISTERED_RESEARCH_PACKAGE research/q8-four-role-three-neg outcome=completed
PASS_PACKAGE_METADATA_AND_PINS
PASS_DUP_JSON
```

## Evidence commands

```sh
python3.12 -I -B research/q8-four-role-three-neg/verify.py
python3.12 -I -O -Werror -B research/q8-four-role-three-neg/verify.py
python3.12 -I -B research/q8-four-role-three-neg/independent.py
python3.12 -I -B research/q8-four-role-three-neg/test_package.py
python3.12 -B scripts/research_package.py --package research/q8-four-role-three-neg
```
