# Engineering notes

## Choices

- Reuse the authenticated C5 geometry loaders and 23-cycle census pattern with
  `HERE.parents[1]` as the repository root and `need()` for all proof gates so
  `-O` admission holds.
- Primary scanner uses packed bit pivots; the independent scanner uses dense
  GF(2) elimination and an iterative chordless-path C5 census, plus a reversed
  pair enumeration for the expansion lemma.
- The reduction certificate expands J and pairwise Grams into the `{D, OD}`
  basis and checks exact netting to the diagonal on four fixtures; it does not
  rerun #3643's 2.5M named-support domination census.
- Global minimality of tariff 224 is certified by a convex subgradient argument
  fed by the pair-expansion lemma `τ(P)+τ(OD_ij)+τ(OD_ji) ≥ 4`.

## Rejected alternatives

- Reprinting or rescaling #3643 floors `45` / `561/16` without a reduction:
  excluded by donor instruction (thin charging corollary).
- J-only expansion without P-elimination: not cost-preserving on the signed
  Gram extension (pre-cost 47257 rises under J-only rewrite before P expansion).
- Claiming a new unconditional decoder floor of 224: out of scope; 224 is the
  named-class optimum on `I`, not a general Cost_opt bound.

## Runtime

All three registered commands finish well under their VERIFY.json budgets on
CPython 3.12 with the standard library only.
