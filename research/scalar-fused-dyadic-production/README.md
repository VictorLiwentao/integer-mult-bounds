# Production fused dyadic apply for the PR799 independent auditor

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`,
`research/gauge44-frames-x/independent/audit_local.py` still computed every
sparse-row update as `y + q*x` with two `Fraction` normalizations. Gareth
Davidson’s opt-in adapter `research/scalar-fused-dyadic/` (incorporated
[#849](https://github.com/CrocSwap/integer-mult-bounds/pull/849)) already
proved a single-normalization fused update with identical complete audit
receipts. This package wires that equivalent rewrite into the **production**
PR799 independent auditor used by gauge44-frames-x / X4 tooling.

SELECTED-SOURCE-bound sibling copies (`gauge44-slots`, `gauge44-leaver`,
`complex-sw4-frame8/independent`, `complex-t21-owners/...`) are intentionally
left pairwise so the selected inventory stays untouched aside from the live
frames-x working bytes (open question: coordinated digest refresh).

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/scalar-fused-dyadic-production/verify.py
python3.12 -I -O -B research/scalar-fused-dyadic-production/verify.py
python3.12 -B scripts/research_package.py --package research/scalar-fused-dyadic-production
taskset -c 0 python3.12 -I -B research/scalar-fused-dyadic-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_SCALAR_FUSED_DYADIC_PRODUCTION honest=1 fuzz=40 corruption=… certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/scalar-fused-dyadic-production outcome=completed
PASS_IDENTICAL_SCALAR_FUSED_DYADIC_PRODUCTION_RECEIPTS
```

Default verify is read-only. Temp-copy destination-drop foil rejects via audit
failure or receipt divergence. Package gates under `-O` still load checkers with
`compile(..., optimize=0)`. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating fresh-process
pairs over the pinned PR799 jx `FULL-WORD` (parent centre/port check enabled)
gave the median wall time recorded in [`RESULT.json`](RESULT.json). Timing is
host-descriptive and is not a correctness gate. Every honest and fuzz outcome
matches the pairwise baseline, and the honest receipt matches
`research/community-frontier799-audit/INDEPENDENT-LOCAL.json`.

## Why the fused update is equivalent

Let `q*x = N/D` before reduction and `y = A/B`. For dyadic inputs `D` and `B`
are positive powers of two, so one divides the other. With `L = max(D, B)`,

```text
y + q*x = (A*(L/B) + N*(L/D)) / L.
```

Both divisions are exact integer divisions. Constructing one `Fraction` from
this numerator/denominator gives exactly the same reduced result as the
original multiplication followed by addition. Non-dyadic existing denominators
fall back to the original general-rational operations. See
`research/scalar-fused-dyadic/`.

## Overlap and credit

Closest priors (different delivery):

- `research/scalar-fused-dyadic/` / [#849](https://github.com/CrocSwap/integer-mult-bounds/pull/849)
  — opt-in fused apply; this is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Leave-alone tooling through [#2412](https://github.com/CrocSwap/integer-mult-bounds/pull/2412)
  (HPE integer-row / frame-pair / emitted-local production rewrites) and pending
  `cursor/ck-dyadic-replay-production-60b9` were not reopened.

Credit icekylinx, Jeremy Kothe, and Gareth Davidson. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should the other SELECTED-SOURCE-bound byte-identical
   `audit_local.py` copies adopt the same fused apply with a coordinated
   `SELECTED-SOURCE.json` digest refresh?
   **Why it matters:** Selected inventory still pins pairwise-era digests for
   those paths.
   **First step:** Enumerate SELECTED-SOURCE paths with sha256 `03afcfc9…`.
   **Blocked by:** Maintainer inventory-refresh preference.

2. **Question:** Should `research/scalar-fused-dyadic` be marked superseded now
   that production frames-x ships the fused apply?
   **Why it matters:** One recommended path for the PR799 independent auditor.
   **First step:** Add a one-line pointer in that package README after merge.
   **Blocked by:** Documentation-only follow-up.
