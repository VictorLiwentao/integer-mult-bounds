# Shared shears cannot undercut tariff 436 on R=82 seven-query schedules

**Priced obstruction under the PR1898 abstract complete-call tariff; no new κ.**
Answers open question 1 of the pending
`research/mutable-source-789q-invoice/` package (fork tip `bc957a78`): whether a
non-path / interleaved elementary source-XOR schedule at seven queries can reach
`X≤2` with readout cost `R=82` and beat the sharp six-query endpoint tariff
**436**.

Under **restored interleaved elementary source XORs** (a strict enlargement of
path-local compute/uncompute), every full-rank connector walk that already has
path-local `X=6` on an `R=82` seven-query slot set remains unrealizable with
interleaved `X≤3`. The 789q champion path has interleaved minimum **exactly 6**.

| Schedule class | X bound | Abstract tariff `(38,2,2)` | vs 436 |
|---|---|---:|---|
| Q=6 endpoint (PR1898/PR2455) | exact 8 | **436** | — |
| Q=7, R=82, path-local (789q) | ≥6 | ≥442 | +≥6 |
| **Q=7, R=82, path-local X=6, interleaved (this)** | **≥4 (census: no ≤3)** | **≥438** | **+≥2** |
| Q=7 champion interleaved minimum | **exact 6** | **442** | +6 |

The restored length-2 classification alone blocks `X≤2`: only twenty restored
words exist, each exposing a single weight-2 column mid-state. The `X≤3`
strengthening is an exhaustive Cayley-ball census over all **40,320** full-rank
path-local-`X=6` increment sequences on the **97,216** `R=82` covering sets.

This does **not** price arbitrary non-elementary source maps, readout rules
outside even-subset schedules, or physical supplier tariffs. No new kappa.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/mutable-source-7q-shared-xor/verify.py
python3.12 -I -O -B research/mutable-source-7q-shared-xor/verify.py
python3.12 -I -B research/mutable-source-7q-shared-xor/independent.py
python3.12 -I -B research/mutable-source-7q-shared-xor/test_package.py
python3.12 scripts/research_package.py --package research/mutable-source-7q-shared-xor
```

Expected:

```text
PASS_MUTABLE_SOURCE_7Q_SHARED_XOR paths6=40320 Xle2=0 Xle3=0 champion_min_X=6 tariffs=434,436,442 ... no_new_kappa
PASS_INDEPENDENT_7Q_SHARED_XOR restored2=20 mid_sets=10 champion_min_X=6 ... no_new_kappa
PASS_MUTABLE_SOURCE_7Q_SHARED_XOR_PACKAGE_TESTS groups=5
PASS_REGISTERED_RESEARCH_PACKAGE research/mutable-source-7q-shared-xor outcome=completed
```

Default verify is read-only and compares the fresh census to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes. The principal
census takes on the order of a few minutes.

## Evidence map

| Claim | Where |
|---|---|
| 20 restored length-2 words; one multi-bit mid-column | `model.restored_length_two_words` |
| 97216 R=82 covers; 40320 path-local X=6 full-rank walks | `verify.py` census |
| Multi-bit patterns (222)/(23), no repeats | `model.multi_bit_pattern` |
| Zero walks with interleaved X≤2 or X≤3 | Cayley-ball search in `verify.py` |
| Champion interleaved min X=6 | budget 2/3 fail, budget 6 succeeds |
| Tariffs 434/436/438/442 | `(38,2,2)` fixture |

## Scope limits

No new kappa, frontier, native/hosted admission, or compiler/tape claim. The
schedule class is connector-prefix increment sequences of full-rank closed
walks with path-local `X=6` on `R=82` seven-query slot sets. Walks whose
path-local `X` already exceeds 6 bill at least 446 under path-local lowering
and are not re-censused here for interleaved shears. Global unequal-price
optimality over all XOR interleavings and all readout rules remains open.

## Open next questions

1. **Can an interleaved schedule with path-local X≥8 on an R=82 set still reach
   interleaved X≤3 via repeated multi-bit increments?**
   Why it matters: only then could shared shears reopen a tie/beat of 436
   outside the minimum path-local class. First step: filter full-rank R=82
   walks with repeated multi-bit increments and rerun the budget-3 ball search.
   Blocked by: no such competitive witness is known; path-local they already
   bill ≥446.

2. **Does any non-elementary restored source map (beyond single-target XORs)
   realize an R=82 seven-query covering with X≤3 under a declared complete
   price?**
   Why it matters: the present obstruction is for elementary shears. First
   step: name one additional paid source operation and rerun the champion
   census. Blocked by: no cheaper operation is admitted in the mutable-source
   alphabet used here.

## Credit

Credit **Arham Tahir / PR1898** (minimum-query endpoint, abstract tariff,
unequal-price handoff), the pending **789q invoice** package (exact Q=7 path-
local minimum and OQ1 answered here), **ywz65 / PR2455** (sharp eight XORs at
six queries), **PR1370** (four-X path), **TennisBowling / PR1524** (equal-price
theorem / unequal handoff), **Ross Richardson / PR943** (prefix framework), and
the retained mutable-source lineage. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.
