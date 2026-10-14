# Selected complex revision-3 diagnosis (independent enclosure)

**Independent verification only. No new κ; the selected frontier is unchanged.**

This package binds the revision-3 portfolio diagnosis in
[autoresearch.md](../../autoresearch.md) and
[bottleneck-brief.md](../../docs/research/bottleneck-brief.md) to the selected
`ASSEMBLY.json` complex ledger with a **code-disjoint** exact enclosure. It does
**not** import `research/complex-local-word-ceiling/` (atanh-successor chains).
Logarithms use a binary `ln 2` series plus odd reduction to Mercator `ln(1+x)`;
exponentials use Taylor series with range reduction.

## Result

From `research/community-frontier1094-audit/ASSEMBLY.json`:

| Quantity | Exact / certified value |
|---|---|
| Rank mass / live width | 1,041,408 / 14,336 |
| Deficit `D = 73·W − mass` | 5,120 |
| Coverage identity | `mass = 72W + 64N` (N = 144) |
| Live families per call | `896/9 ≈ 99.556` |
| Unpaid after centre per call | `320/9 ≈ 35.556` |
| Effective child rank `m exp(−E/mass)` | ≈ 3.9159 ∈ [3.9, 4] |
| `a* < D/E` | yes; enclosure intersects PR1293's |
| Packing ceiling (same model as #1240) | contains `0.001690054109089` |
| Ideal lever multipliers | ×2.80, ×1.90, ×2.31, ×1.62, ×3.77, ×6.51 |
| `κ` vs `a/(1+a)` | 18-decimal truncation of the binding complex transfer |

Semantic controls reject an idle-rank-52 halving violation, a local mass beyond the
coverage law, a raised ceiling after one extra rank-1 child, a bogus ×3
centre-free multiplier, and a one-ulp kappa forgery. The local×144 + idle
histogram rebuilds the ASSEMBLY complex profile exactly.

## Reproduce

Default verify is **read-only**: recomputes evidence, requires exact equality
with committed [RESULT.json](RESULT.json), rejects forged D/status, and does not
rewrite the receipt. Use `--write` only to regenerate.

```sh
python3 -I -B research/selected-complex-diagnosis-seed9f90/verify.py
```

Expected on stderr: `PASS_SELECTED_COMPLEX_DIAGNOSIS`

Also: `python3 -B scripts/research_package.py --package research/selected-complex-diagnosis-seed9f90`.

## Scope and limitations

- Favorable lever relaxations omit realization cost; they are not constructions.
- Does not rebuild the rank ledger from gate operations (see #1262 / #1421).
- Does not re-prove the no-q-adic-selector compiler premise (PR552 / PR559).
- Does not run `make frontier1094-verify`.
## Open next questions

1. **Can the no-q-adic-selector premise (b) of the surcharge-free complex
   recurrence be checked from the pinned emit/controller rules rather than the
   PR552/PR559 review prose?** It matters because the selected κ uses the
   native (no complex surcharge) moment. First step: a code-disjoint static
   vocabulary check on the bound `emit_local` / hosted schedule. Blocker: none
   beyond careful reading of the pinned capsule.
2. **Do the same diagnosis identities hold for each open complex claim whose
   local word leaves the #1240 packing model?** It matters for portfolio
   triage of claims above the selected κ. First step: extract one claim's
   per-call local profile and rerun this checker. Blocked by each claim's
   idle histogram extraction.

## Credit

- Douglas Colkitt: revision-3 diagnosis, packing-ceiling model (#1240).
- Sagar Thakrar: emitted complex ledger (#1262) and bit-side levers (#1334).
- Navinor: independent D/E diagnostic (#1293).
- commdata2338: bit projector ledger (#1421).
- Rohan Arun / Jeremy Kothe and the frontier1094 packing lineage.



## Disposition (2026-10-14)

**Defer upstream publication.** Bounded probes against live main `0b1cccf8`:

| Prior | What it already proves |
|---|---|
| [CrocSwap/integer-mult-bounds#1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240) | Packing ceiling model and diagnosis figures |
| [CrocSwap/integer-mult-bounds#1262](https://github.com/CrocSwap/integer-mult-bounds/pull/1262) | Emitted complex ledger rebuild |
| [CrocSwap/integer-mult-bounds#1293](https://github.com/CrocSwap/integer-mult-bounds/pull/1293) | `a* < D/E` diagnostic |
| [CrocSwap/integer-mult-bounds#1334](https://github.com/CrocSwap/integer-mult-bounds/pull/1334) | Bit-side lever budgets |
| [CrocSwap/integer-mult-bounds#1421](https://github.com/CrocSwap/integer-mult-bounds/pull/1421) | Bit projector ledger |

**Independence (precise):** `enclosure.py` is code-disjoint from `research/complex-local-word-ceiling/ceiling.py` (binary `ln 2` + odd reduction + Mercator `ln(1+x)` + Taylor `exp`, not atanh-successor chains). It still shares classical Mercator/Taylor range logic with earlier vendored moment engines (e.g. PR559 `engines/moment.py`). Diagnosis quantities reprint the known portfolio.

**no-q-adic:** A useful check must inspect the transitive `emit_local`/controller path and inject a meaningful selector counterexample. Keyword absence / vocabulary counting is not a compiler theorem; PR559 already argues the premise in review prose. Not completed in this bounded budget.

Fork PR kept for record; not submitted to CrocSwap.


Prepared by Wentao Li (@VictorLiwentao; wentaol4@illinois.edu;
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
New work Apache-2.0; retain source notices.
