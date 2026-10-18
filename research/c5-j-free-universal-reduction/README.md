# Cost-preserving J/P elimination unlocks universal named-class floor 45

Every exact `{diagonal, J, off-diagonal, pairwise Gram}` decomposition of
`I_112` expands into the coordinate `{D, OD}` basis and nets to the diagonal
tariff **224**. The named-class cost is convex; a geometric pair-expansion lemma
`τ(P)+τ(OD_ij)+τ(OD_ji) ≥ 4` (min slack 4 on all 6216 pairs) puts zero in the
subdifferential at the diagonal, so 224 is the global named-class minimum and
the expand-and-net rewrite is cost-preserving. Combined with the J-free floor
**45** of [#3643](https://github.com/CrocSwap/integer-mult-bounds/pull/3643),
that floor applies universally inside the named alphabet — not only when
`σ_J = 0` after netting. Dual scanners agree. Selected κ is unchanged at
`0.001672660197076918`.

This answers the cost-preserving J-elimination OQ left open by
`research/c5-fit-level-cancellation-charge` / #3643. It does not reprint the
named-support domination census, the floors `45` / `561/16` derivation, or the
termwise `180/7` bill.

[PROOF.md](PROOF.md) states the reduction and subgradient corollary. RESULT.json
records the pair-slack histogram, fixture reductions and the cited floor 45.

## Evidence and reproduction

From the repository root, using standard-library CPython 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/c5-j-free-universal-reduction
```

Direct commands:

```sh
python3.12 -Werror -I -B research/c5-j-free-universal-reduction/verify.py
python3.12 -Werror -I -B research/c5-j-free-universal-reduction/independent.py
python3.12 -Werror -I -O -B research/c5-j-free-universal-reduction/test_verify.py
```

Expected markers:

```text
PASS_C5_J_FREE_UNIVERSAL_REDUCTION cycles=23 named_class_opt=224 pair_slack_min=4 j_free_floor=45 universal=true
PASS_C5_J_FREE_UNIVERSAL_REDUCTION_INDEPENDENT cycles=23 named_class_opt=224 pair_slack_min=4 j_free_floor=45 universal=true
```

Default verify is read-only and compares the committed RESULT.json. Admission
uses `need()` and still fires under `-O`.

## Open next questions

1. Does the same expand-and-net reduction stay cost-preserving for every
   completed strict fit (not only `I_112`), including free orthogonal
   off-diagonal fillings?

## Credit

Nick Petalas (termwise charging), Krzysztof Wójt (four-residual floors),
#3639 residual/local-opt audit, #3643 named-class cancellation charge,
Tekalign/PR2782, Cinna Davis/PR1825, Adam Gall/PR1889, thakrarsagar/PR3256,
and the retained matching lineage. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
