# MASTER-HANDOFF — gate-operand-dest-absent-guard

## Candidate

- Branch: `cursor/gate-operand-dest-absent-guard-60b9` (VictorLiwentao fork).
- Package: `research/gate-operand-dest-absent-guard/`
- Predecessor: #3696 `research/gate-operand-export-parity/` @
  `0581402f978addb2eda5306fd124001486c76b08` (leave alone; present on branch).
- Base: CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`
- Card: `supplier-boundary-audit` (refined), priority revision 6
- κ: unchanged at `0.001672660197076918`
- Author and committer: Wentao Li `<wentaol4@illinois.edu>`, with no
  `Co-authored-by: Victor Li` trailer (`git -c core.hooksPath=/dev/null commit`).
- **Do not open a CrocSwap PR** — master publishes.

## Claim (one sentence)

On the #3696 gate-operand domain, destination-absent (`d ∉ srcs`) rejects all
3492 dest-in divergent patterns and zero agreeing dest-free lists, while
simple-support also rejects all divergent dest-in but additionally rejects 3450
agreeing dest-free lists — answering #3696 OQ1.

## Closest prior

- #3696 dest-free/dest-in Sym/Exp lemma (OQ1 left open; leave package alone)
- #3004 / #2977 scatter parity cascade (scatter-only; leave alone)

## New checkable fact

Guard accept/reject census and named controls (`dup_src` / `d=1,srcs=[0,0]`),
not a reprint of `dest_free_agree=4686` / `selected_gates=5472` / the two named
divergent witnesses as a new claim (those remain #3696 facts used only as pins).

## Evidence commands

```sh
python3.12 -I -B research/gate-operand-dest-absent-guard/verify.py
python3.12 -I -O -Werror -B research/gate-operand-dest-absent-guard/verify.py
python3.12 -I -B research/gate-operand-dest-absent-guard/independent.py
python3.12 -I -B research/gate-operand-dest-absent-guard/test_package.py
python3.12 -B scripts/research_package.py --package research/gate-operand-dest-absent-guard
```

## Soft-overlap vs leave-alones

- Vs #3696: semantic successor (guard sharpness after Sym/Exp lemma); expected
  soft-overlap ~0.1–0.3, not a template reprint (~0.9).
- Clear of stock-leaf / router / flag-0 / C5 / side-correction / present-head /
  groups B–D native / #3532 repair-template clusters.

## Attribution

Author Wentao Li `<wentaol4@illinois.edu>`. Neutral AI assistance disclosure.
No `Co-authored-by: Victor Li`. No CrocSwap PR from this worker (master publishes).

## Disposition

Ready for master independent review / publish decision. Kappa unchanged.
