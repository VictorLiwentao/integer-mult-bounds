# Faster historical inplace-side compile_side with identical gate lists

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, merged
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793)
sped up `verify_prefix` with a least-unused flag scan and left an open next
question: can the same scan replace `sorted(unused)` inside `compile_side`
without changing gate lists?

Each elimination column previously rebuilt `sorted(unused)` to locate the least
unused row with the pivot bit set, and tested bits with `>> col & 1`. The
production compiler now scans an unused flag array from index 0 and uses a
column mask for both the pivot search and the row-XOR updates. The lexicographic
rule, gate order, pivots, initial matching and every receipt field are unchanged.

The selected frontier, `upstream/` and the mathematical rejection in
[docs/research/inplace-side.md](../../docs/research/inplace-side.md) are not
reopened. Only the source pin for `scripts/experiments/inplace_side.py` changes
inside `certificates/inplace-side.json`.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/inplace-side-compile-scan/verify.py
python3.12 -I -O -B research/inplace-side-compile-scan/verify.py
python3.12 -I -B -m unittest tests.test_inplace_side tests.test_inplace_side_compile_scan -v
python3.12 -B scripts/research_package.py --package research/inplace-side-compile-scan --check-only
python3.12 -B scripts/research_package.py --package research/inplace-side-compile-scan
```

Expected verifier line:

```text
PASS_INPLACE_SIDE_COMPILE_SCAN identity_h=[6, 10, 14, 18, 22, 26, 30] ... no_new_kappa
```

Expected registered replay:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/inplace-side-compile-scan outcome=completed
```

Normal verification is read-only. To regenerate the certificate after editing the
production source:

```sh
python3.12 -I -B research/inplace-side-compile-scan/verify.py --write-certificate
```

Before/after wall times (descriptive; not a pass gate):

```sh
python3.12 -I -B research/inplace-side-compile-scan/benchmark.py --rounds 5
```

Expected: `PASS_IDENTICAL_INPLACE_COMPILE_RECEIPTS`. Samples are retained in
[RESULT.json](RESULT.json).

## Why the receipts stay identical

For each column `col`, the original code selected

```text
min{ i in unused : work[i] has bit col }
```

by materializing `sorted(unused)` and taking the first hit. Scanning
`i = 0, 1, …` over a boolean unused table and stopping at the first hit yields
the same index. Column tests `work[i] & (1 << col)` equal `work[i] >> col & 1`
on these nonnegative row masks. The subsequent row-XOR updates therefore run on
the same pivot sequence, append the same `(target, pivot)` ops in increasing
`i` order, and produce the same reversed gate list and initial matching.

[baseline.py](baseline.py) is a byte-identical copy of
`scripts/experiments/inplace_side.py` at base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (blob
`4f5e7b3f61697ac2095e18d5cd00e3cacd875d99`). The verifier compares full
`compile_side` dicts on `h in {6,10,14,18,22,26,30}`, rejects singular `h=8`,
rejects a greatest-unused mutant (different pivots/gates), rejects an on-disk
temp-copy corruption that flips the scan direction, checks package JSON for
duplicate keys, and requires the working certificate to differ from the base
certificate only in the single `inplace_side.py` source pin.

## Task card, overlap and limits

Expertise override to `replay-runtime` (verifier-engineering) after profiling
discarded weaker candidates: DisjointTensor `dag_sha256` hand-roll (~1.2× on
verify; production edit blocked by open #2117's four `disjoint_tensor.py` cert
pins) and MixedPoint `Circuit.add`/`total` micro-opts (~1.0×). Scope **refined**
to this fixed historical compiler inside `make verify-certificates`.

Closest priors (different objects or already-landed prefix path):

- [CrocSwap #1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793) —
  `verify_prefix` least-unused scan; this answers its compile_side open question.
- [CrocSwap #756](https://github.com/CrocSwap/integer-mult-bounds/pull/756) —
  packed-column balanced-Fano replay on a different checker.
- Local `find_overlap.py` for `compile_side` / `inplace side` reported no
  competing open PR on this object at refresh time.

Limits: timing is host-descriptive; OS caches were not flushed. Full
`make verify`, selected-supplier cold replay, Lean and multiplication-theorem
obligations were not rerun for this isolated historical-checker change.

## Open next questions

- Can the dominant O(n²) XOR update loop inside `compile_side` be accelerated
  further without changing gate order?
- Should CI grow a soft regression timer for `compile_side(h=30)`, or keep
  RESULT.json descriptive only?

## Credit

Douglas R. Colkitt authored the inplace-side rejection, witnesses and original
checker. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor), wentaol4@illinois.edu)
with substantial AI assistance, under Apache-2.0. No independent human
peer-review or formal proof-assistant claim.
