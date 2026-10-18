# Gate-operand guards after #3696: destination-absent answers OQ1; simple-support does not

## Change and mathematical scope

Bounded follow-up under priority revision 6 answering
[#3696](https://github.com/CrocSwap/integer-mult-bounds/pull/3696) open question 1
at the selected PR589 checker/exporter gate-operand boundary.

Predecessor tip `0581402f978addb2eda5306fd124001486c76b08`
(`research/gate-operand-export-parity/`) proved that destination-free gate source
lists always make accumulate-XOR and sequential ADD agree, while
destination-in-sources lists can diverge. OQ1 asks whether a simple-support (or
other) guard rejects all dest-in divergent cases without rejecting agreeing
dest-free lists.

On the same `n=6`, `len(srcs)≤4` domain:

- Both **simple-support** (`d` and all sources distinct) and **destination-absent**
  (`d ∉ srcs`) reject all **3492** dest-in divergent patterns.
- Destination-absent rejects **0** of the **4686** agreeing dest-free lists.
- Simple-support additionally rejects **3450** agreeing dest-free lists
  (witness `d=1`, `srcs=[0,0]`).

So the answer to OQ1 is: simple-support alone is not sharp; destination-absent
is. This is a semantic successor to #3696 (guard sharpness), not a reprint of
its dest-free census or selected-word export gap as a new claim.

**No new kappa.** Selected κ stays `0.001672660197076918`. No production/schema
adoption. The #3696 package tree is left untouched.

## Task and overlap

- Package: `research/gate-operand-dest-absent-guard/`
- Predecessor: #3696 @ `0581402f978addb2eda5306fd124001486c76b08`
- Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`
- Scope: **refined** — answers #3696 OQ1 guard comparison

Closest prior: #3696 (leave alone; OQ1 answered here). Soft-overlap vs #3696
should be semantic successor (~0.1–0.3): shared domain/operators, new claim is
guard accept/reject counts. Clear of stock-leaf / router / flag-0 / C5 /
side-correction leave-alones and of #3004/#2977 scatter-only reprints.

## Validation

```sh
python3.12 -I -B research/gate-operand-dest-absent-guard/verify.py
python3.12 -I -O -Werror -B research/gate-operand-dest-absent-guard/verify.py
python3.12 -I -B research/gate-operand-dest-absent-guard/independent.py
python3.12 -I -B research/gate-operand-dest-absent-guard/test_package.py
python3.12 -B scripts/research_package.py --package research/gate-operand-dest-absent-guard
```

Expected:

```text
PASS_GATE_OPERAND_DEST_ABSENT_GUARD dest_absent_rejects_divergent=3492 dest_absent_rejects_dest_free_agree=0 simple_rejects_divergent=3492 simple_rejects_dest_free_agree=3450 no_new_kappa
PASS_GATE_OPERAND_DEST_ABSENT_INDEPENDENT dest_absent_rejects_divergent=3492 dest_absent_rejects_dest_free_agree=0 simple_rejects_dest_free_agree=3450
PASS_GATE_OPERAND_DEST_ABSENT_PACKAGE_TESTS
PASS_REGISTERED_RESEARCH_PACKAGE research/gate-operand-dest-absent-guard outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.

## Credit

Credit #3696, #3004, #2977, and the retained PR589 checker/exporter lineage.
Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. Should a successor opt-in exporter boundary adopt destination-absent (rather
   than full simple-support) for gate operand lists?
2. Are the four selected-word checker rejects exhaustive for dest-in-sources
   divergence on the pinned word (#3696 OQ2)?
