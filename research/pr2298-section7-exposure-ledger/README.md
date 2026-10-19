# Exact §7 nonadjacent exposure chunk-swap ledger (answers #4075 OQ2)

**Research construction / recursive interface; no new kappa.** Answers open
question 2 of open
[#4075](https://github.com/CrocSwap/integer-mult-bounds/pull/4075)
(`research/pr2298-section3-opcounts`): can section 7’s exposure exponent be
expanded from the §3 exchange counts into a fully numerical chunk-swap
ledger at fixed `(d,ell,tau)`?

**Yes** on the adjacent domain `d≤8`, widths `{3,4}` (`ell=4`), with pinned

```text
tau = 99830289/10^8,  epsilon = 1/40.
```

| Ledger item | Exact value |
|---|---|
| CRT forward + inverse exchanges | `2⌊d/2⌋` |
| Tensor expose/restore exchanges | `2(d−1)` |
| Composite multiplier `M(d)` | `2⌊d/2⌋ + 2(d−1)` |
| Linear majorant | `M(d) ≤ 3d−2` (sharp on even `d`; `M(8)=22`) |
| Unit charge per exchange | `≤ 1 + ell^tau` (`lem:chunk-swap`) |
| §7 saving | `(1−tau)(1−epsilon) = 6618729/4000000000` |

Every one of the `∑_{d=1}^{8} 2^d = 510` mixed patterns has
`pattern_charge ≤ M(d)·(1+ell^tau) ≤ (3d−2)·(1+ell^tau)`. This is the
composite CRT+exposure ledger behind the §7 row “Nonadjacent CRT and line
exposure”, not a reprint of the #4075 adjacent opcount census alone and not
the deferred gap-2 `{3,5}` retarget.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/pr2298-section7-exposure-ledger/verify.py
python3.12 -I -O -Werror -B research/pr2298-section7-exposure-ledger/verify.py
python3.12 -I -B research/pr2298-section7-exposure-ledger/independent.py
python3.12 -I -B research/pr2298-section7-exposure-ledger/test_package.py
python3.12 -B scripts/research_package.py --package research/pr2298-section7-exposure-ledger
```

Expected:

```text
PASS_PR2298_SECTION7_EXPOSURE_LEDGER patterns=510 max_d=8 M8=22 saving=6618729/4000000000 exponent=... even_d_sharp=true no_new_kappa
PASS_INDEPENDENT_PR2298_SECTION7_EXPOSURE_LEDGER M8=22 saving=6618729/4000000000 ... no_new_kappa
PASS_PR2298_SECTION7_EXPOSURE_LEDGER_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/pr2298-section7-exposure-ledger outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()`; `-O` also passes.

## Scope and overlap

Base commit `bb4bccbf42844d2801487450727c2f63e10d1d0f` (CrocSwap/main). Closest
priors: open [#4075](https://github.com/CrocSwap/integer-mult-bounds/pull/4075)
(§3 counts; OQ2 answered here); [#2413](https://github.com/CrocSwap/integer-mult-bounds/pull/2413);
PR2298 §3/§7; Colkitt nonadjacent audit. Soft-overlap with #4075 is moderate on
shared adjacent pair algebra; the composite `M(d)` ledger, per-d numerical
charges, and §7 saving/exponent expansion are the new checkable facts. Does
**not** reopen the deferred gap-2 package, precision-blind / odd-kernel /
PR2809 / route-cube / UT4 leave-alones, or #2687/#2888 preferred paths.

Preferred #2687 admitted BIT-supplier hosting and #2888 non-toy `F_I` Incoming
were not grounded in this budget without soft-overlap DEFER risk; this card is
the disjoint #840-style alternative.

## Open next questions

1. Does the same `M(d)·(1+ell^tau)` ledger extend to gap-`g≥2` once a
   non-thin general-`g` physical lemma exists?
2. Can the Decimal `ell^tau` rows be replaced by a fully rational interval
   certificate?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit Jose Manuel / PR2298, #2413, open #4075, Douglas Colkitt’s
nonadjacent audit, and the synthetic-layout physical oracle. No independent
human review is claimed. No new kappa.
