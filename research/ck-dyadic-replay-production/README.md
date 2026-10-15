# Production CK dyadic replay via proved fast row kernels

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, production
`research/complex-ck-two-sided/independent.py` still used the pairwise
`_normal_row` / `_sum_rows` kernels. Sricharan Vagvala’s opt-in adapter
`research/ck-dyadic-replay-fast/` already proved early-exit normalization and
COPY-safe zero-free addition with identical PR917 receipts. This package wires
those equivalent kernels into the **production** PR917 independent checker.

Leave-alone objects (emitted-local `#2357`, frame-pair `#2375`, HPE audit
`#2409`, pending HPE-transport sibling) are not reopened.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/ck-dyadic-replay-production/verify.py
python3.12 -I -O -B research/ck-dyadic-replay-production/verify.py
python3.12 -B scripts/research_package.py --package research/ck-dyadic-replay-production
taskset -c 0 python3.12 -I -B research/ck-dyadic-replay-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_CK_DYADIC_REPLAY_PRODUCTION … streams=4 primitives=374606 … no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/ck-dyadic-replay-production outcome=completed
PASS_IDENTICAL_CK_DYADIC_REPLAY_PRODUCTION_RECEIPTS …
```

Default verify is read-only. Temp-copy kernel foil rejects via receipt
divergence or runtime failure. Package gates under `-O` still load checkers
with `compile(..., optimize=0)`. Full `make verify`, selected cold replay,
Lean, and multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating fresh-process
pairs timing the four complete integer-dyadic streams gave median wall time
**1.722 → 1.445 s (1.19×)**.
Details are in [`RESULT.json`](RESULT.json). Timing is host-descriptive and is
not a correctness gate. Every four-stream receipt matches the pairwise baseline
fieldwise. The prior opt-in package reported about 1.45–1.50× on other hosts;
this Linux sample is lower and is the figure claimed here.

## Why the kernels are equivalent

A row `(terms, e)` denotes `sum terms[j]*input[j] / 2**e`. Normalization
divides by `2**min(e, min_j v2(terms[j]))`. Encountering one odd nonzero
numerator proves the common valuation is zero, so the scan can stop exactly.
Addition aligns denominators by exact integer shifts, copies the left map
(never mutating a COPY-shared dictionary), adds each signed right numerator,
and deletes cancellations immediately. See
`research/ck-dyadic-replay-fast/README.md`.

## Overlap and credit

Closest priors (different delivery):

- `research/ck-dyadic-replay-fast/` — opt-in kernels; this is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- `#2357` / `#2409` — integer-row production promotions on other auditors.

Credit Ross Richardson / PR917 and Sricharan Vagvala / @theon199. Prepared by
Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should `u8-two-sided-biforest-seed35/independent.py` adopt the
   same early-exit dyadic kernels?
   **Why it matters:** It carries a near-copy of the pairwise PR917 row kernels.
   **First step:** Diff its `_normal_row` / `_sum_rows` against this transform.
   **Blocked by:** One-object stop rule.

2. **Question:** Should the registered `ck-dyadic-replay-fast` adapter document
   that production already ships its kernels?
   **Why it matters:** Operators may still expect an in-memory monkey-patch.
   **First step:** Update the opt-in README after review.
   **Blocked by:** Maintainer doc preference.
