# Production zero-row skip for the cyclic-inverse verifier

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`research/prime-power-cyclic-inverse/verify.py` still performed exact Field
updates on every non-pivot row, including rows whose coefficient was
`k.zero`. thakrarsagar’s opt-in adapter
`research/cyclic-zero-elimination/` (incorporated
[#736](https://github.com/CrocSwap/integer-mult-bounds/pull/736)) already
proved that skipping those updates preserves the complete eight-case receipt.
This package wires that equivalent guard into the **production** verifier.

No other VERIFY package live-pinned the production `verify.py` bytes. The
historical opt-in adapter now vendors the pairwise baseline in
`research/cyclic-zero-elimination/baseline.py`.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/cyclic-zero-production/verify.py
python3.12 -I -O -B research/cyclic-zero-production/verify.py
python3.12 -B scripts/research_package.py --package research/cyclic-zero-production
taskset -c 0 python3.12 -I -B research/cyclic-zero-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_CYCLIC_ZERO_PRODUCTION keys=… corruption=… certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/cyclic-zero-production outcome=completed
PASS_IDENTICAL_CYCLIC_ZERO_PRODUCTION_RECEIPTS
```

Default verify is read-only. Temp-copy inverted zero-skip foil rejects via
subprocess failure or receipt divergence. Package gates under `-O` still launch
asserting verifier children (`python -B` with `PYTHONOPTIMIZE` cleared). Full
`make verify`, selected cold replay, Lean, and multiplication-theorem
obligations were not rerun for this isolated historical-checker change.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating fresh-process
pairs gave median complete eight-case wall time recorded in
[`RESULT.json`](RESULT.json). Timing is host-descriptive and is not a
correctness gate. Every receipt matches digest
`2c4ab855129670053f4f39ee14269cc9b5bda015eab71d5a226dd0d395740ebd`
(byte-identical to `EXPECTED.json`).

## Why the zero-row skip is equivalent

For exact Field arithmetic, `k.sub(x, k.mul(k.zero, y)) = x` and
`k.sub(b, k.mul(k.zero, c)) = b`. Omitting those updates leaves every matrix
entry and every right-hand side unchanged. Pivot selection, reciprocal scaling,
determinants and Bezout solves are untouched. See
`research/cyclic-zero-elimination/README.md` and the focused matrix controls in
that package’s `verify.py`.

## Overlap and credit

Closest priors (different delivery):

- `research/cyclic-zero-elimination/` / [#736](https://github.com/CrocSwap/integer-mult-bounds/pull/736)
  — opt-in zero-row skip; this is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2039/#2054
  shared-point, #2100 ternary, #2117 DisjointTensor, #2150 mixed-point,
  #2194/#2210/#2231/#2239/#2257/#2263/#2276/#2320/#2329/#2348/#2357 production
  rewrites; #1076 quadratic-affine) was not reopened. Fresh overlap refresh
  over open PRs found no competing production rewrite of
  `prime-power-cyclic-inverse/verify.py:eliminate`.

Credit Ali Romman and thakrarsagar. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should `research/cyclic-zero-elimination/README.md` permanently
   describe production as shipping the same zero-row skip?
   **Why it matters:** That package historically described itself as in-memory
   only so the predecessor source stayed byte-pinned.
   **First step:** Keep the one-line status note; expand only if maintainers want
   deeper cross-links.
   **Blocked by:** Maintainer preference on touching incorporated historical
   packaging prose.

2. **Question:** Do other Field.eliminate call sites in descendant cyclic
   packages share this exact zero-row loop?
   **Why it matters:** A coordinated refresh could remove duplicated pairwise
   eliminate copies without changing receipts.
   **First step:** Search for the unguarded coefficient update pattern outside
   this verifier.
   **Blocked by:** One-object stop rule.
