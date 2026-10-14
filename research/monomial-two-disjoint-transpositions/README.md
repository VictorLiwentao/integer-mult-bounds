# Two disjoint monomial transpositions share one CLEAR

**Recursive-interface exact finite floor; no new kappa.** In the absolute-label
COPY/CLEAR quotient of
[`research/complex-monomial-runs-seed25`](../complex-monomial-runs-seed25/README.md),
one transposition costs **4**. Composing two *closed* disjoint transpositions
therefore costs **8**. Treating them as a typed open/closed pair eliminates the
midpoint workspace CLEAR that the second call would otherwise reconstruct: the
joint map `(1 2)(3 4)` with workspace restored to zero has exact minimum **7**.

This answers the card's persistence question on a concrete two-type pilot. It
does not reopen the predecessor's single 2-cycle floor (**4**) or its disjoint
2+3-cycle floor (**8**). Those remain positive controls.

## Typed entry/exit contracts

Keep the predecessor monomial class: four data registers plus one workspace;
every intermediate row is a single absolute incoming label or zero; primitives
are unit-cost COPY and CLEAR (the signed ADD/SUB/NEGATE/DOUBLE/HALVE alphabet
projects onto this quotient). Endpoints restore the declared permutation and
clear the workspace. Dirty entry erases incoming workspace dirt; clean entry
starts with a zero workspace. Both cases are checked.

| Call type | Contract | Exact cost in this class |
|---|---|---:|
| Closed transposition `T` | entry work label unused/zeroed; exit work `0`; data swapped | 4 |
| Open transposition `O` | same data swap; exit leaves work holding the displaced label | 3 |
| Closing transposition `T'` from that open midpoint | consumes the open work slot; exits work `0` | 4 |

Separate closed composition `T` then `T'` costs **8**. The open composition
`O` then `T'` costs **7** and attains the joint floor. The eliminated
primitive is exactly the midpoint CLEAR.

## Exact evidence

Both the predecessor forward BFS (`finite.py`) and reverse enumeration
(`backward.py`) return minimum **7** for permutation `(2,1,4,3)`, on clean and
dirty-erase entry. An independent forward BFS in this package agrees on every
reachable-state count, primitive-edge count and distance histogram. Literal
matrix replay accepts the open witness, the closed separate witness and both
search witnesses, and rejects a one-shorter word, an omitted CLEAR and a wrong
second-cycle completion.

| Entry | Forward reachable states | Forward primitive edges | Joint minimum |
|---|---:|---:|---:|
| Clean | 360 | 2,400 | 7 |
| Dirty-erase | 361 | 2,405 | 7 |

No path of length ≤6 reaches the joint target. The shared-CLEAR upper bound of
seven (three COPYs per 2-cycle plus one final CLEAR) is therefore exact.

## Reproduce

Python 3.12 and the standard library; from the repository root:

```sh
python3.12 -I -B research/monomial-two-disjoint-transpositions/verify.py
python3.12 scripts/research_package.py --package research/monomial-two-disjoint-transpositions --check-only
python3.12 scripts/research_package.py --package research/monomial-two-disjoint-transpositions
```

Expected final verifier line:

```text
PASS_MONOMIAL_TWO_DISJOINT_TRANSPOSITIONS joint=7 separate_closed=8 eliminated_mid_clear=1 no_new_kappa
```

## Scope and limits

Task `persistent-boundary`, priority revision 3, OS-random assignment seed
`606c01aeeef18054c0e46f4ce68fe3e9`, scope key `026be4b6e61971d51838`. Scope
**refined** to this monomial two-disjoint-transposition pilot. Base commit
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Selected-record SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

This is a finite class certificate for the declared absolute-label quotient. It
is not an unrestricted arithmetic-circuit minimum, a restored-dirty-workspace
theorem (the sole workspace is erased, not restored), a supplier admission, a
paid recursive-profile change or a new kappa. Physical hosting, precision/tape
and all-size/compiler obligations remain.

Nearest local predecessor: `complex-monomial-runs-seed25` (floors 4 and 8 only).
Open connector-delivery and mutable-connector packages address different
alphabets. Restored-cycle and borrowed-donor packages restore dirt rather than
erase it. No open PR title/body matched this joint two-disjoint monomial floor
on the refreshed overlap snapshot.

## Open next questions

1. Does a selected physical caller expose two consecutive disjoint
   transposition boundaries that can keep this open midpoint type?
2. Can three disjoint 2-cycles share one CLEAR at cost 10 (exact), or does an
   extra obstruction appear?

## Credit

Predecessor absolute-label engines and floors: the authors of
`research/complex-monomial-runs-seed25` (PR credit retained in that package's
NOTICE). 

## Disposition (2026-10-14)

**Defer upstream publication.** Exact joint floor 7 on `(2,1,4,3)` verifies in this
COPY/CLEAR class, but predecessor
[`complex-monomial-runs-seed25`](../complex-monomial-runs-seed25/README.md)
already supplies the shared-final-CLEAR multi-cycle upper bound that yields 7 for
two 2-cycles, and already certifies floors 4 and 8. The typed open→closed
narrative is compositional accounting against a 4+4 baseline; most length-7
shortest words are interleaved shared-CLEAR schedules, not consecutive typed
calls. Not enough for a standalone #840-class recursive-interface claim.


Prepared by **Wentao Li** with substantial AI assistance under
Apache-2.0. No independent human or proof-assistant review is claimed.
