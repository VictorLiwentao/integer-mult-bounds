# Exact PR2298 §3 operation counts on mixed gap-2 (non-adjacent) widths

**Research construction / recursive interface; no new kappa.** Answers open
question 1 of open
[#4075](https://github.com/CrocSwap/integer-mult-bounds/pull/4075)
(`research/pr2298-section3-opcounts`): do the same closed-form exchange
counts hold for non-adjacent width gaps larger than one bit?

**Yes**, under the multi-bit normal form below, on every mixed gap-2
bit-width pattern at `d≤6` with widths in `{3,5}` (**126** patterns):

| Invoice | Exact count |
|---|---|
| Axis-order reversal | `⌊d/2⌋` exchanges |
| Tensor expose/restore map | `2(d−1)` exchanges |
| Gap-`g` pair (`g=|Δw|`) | 1 interchange + `g` bit moves |
| Equal-width pair | 1 interchange |

When `g=1` this recovers the adjacent one-extra-bit invoice of PR2298 §3 /
#4075. For `g=2` the elementary bit-move iterates once per excess bit.
Sharp at `d=6`: reversal `3`, tensor `10`. Physical spot-checks replay the
low-level `(swap|move)` stream through the pinned `physical.move_address`
oracle.

This is a new multi-bit pair algebra, not a reprint of the adjacent 510-row
ledger.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/pr2298-section3-gap2-opcounts/verify.py
python3.12 -I -O -Werror -B research/pr2298-section3-gap2-opcounts/verify.py
python3.12 -I -B research/pr2298-section3-gap2-opcounts/independent.py
python3.12 -I -B research/pr2298-section3-gap2-opcounts/test_package.py
python3.12 -B scripts/research_package.py --package research/pr2298-section3-gap2-opcounts
```

Expected:

```text
PASS_PR2298_SECTION3_GAP2_OPCOUNTS patterns=126 max_d=6 gap=2 widths={3,5} rev_bound=floor(d/2) tensor_bound=2(d-1) pair_invoice=1+g sharp_d6_rev=3 sharp_d6_tensor=10 no_new_kappa
PASS_INDEPENDENT_PR2298_SECTION3_GAP2_OPCOUNTS patterns=126 max_d=6 gap=2 rev_bound=floor(d/2) tensor_bound=2(d-1) pair_invoice=1+g no_new_kappa
PASS_PR2298_SECTION3_GAP2_OPCOUNTS_PACKAGE_TESTS groups=5
PASS_REGISTERED_RESEARCH_PACKAGE research/pr2298-section3-gap2-opcounts outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()`; `-O` also passes.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap/main). Closest
priors: PR2298 §3; #2413; open #4075 (adjacent `{3,4}` census; OQ1 answered
here). Soft-overlap with #4075 is moderate on shared reversal/tensor
topology; the gap-`g` pair invoice, physical long-last invert stream, and
`{3,5}` census are new. Does not reopen leave-alone precision-blind /
odd-kernel / PR2809 / route-cube / UT4 clusters, and does not reprint the
510-row adjacent ledger.

## Open next questions

1. Does the same multi-bit normal form remain physical for every gap
   `g≥3` on mixed `{s,s+g}` at modest `d`, or do intervening-field carries
   force a different stream?
2. Can section 7's exposure exponent be expanded from these exact counts
   (including the `g·(exchanges)` bit-move term) into a fully numerical
   chunk-swap ledger at fixed `(d,ell,tau,g)`?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit Jose Manuel / PR2298, #2413, open #4075, Douglas Colkitt's
nonadjacent audit, and the synthetic-layout physical oracle. No independent
human review is claimed. No new kappa.
