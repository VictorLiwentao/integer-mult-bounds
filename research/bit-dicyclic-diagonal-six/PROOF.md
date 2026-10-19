# Proof sketch — depth-six Dic_3 diagonal obstruction

## Claim

In the formal model of `research/bit-dicyclic-diagonal-seed620ca` (group
`Dic_3`, paid letters `{u,v}`, three registers, 28 rank-one idempotents), let
`T = diag([w0],[w1],[w2])` with each `wi ∈ Dic_3`. Let `direct(T)` be the sum of
shortest positive `{u,v}` word lengths of the three coordinates. Then every `T`
with `direct(T) ≥ 7` has no product of at most six paid factors equal to `T` in
`M3(F2[Dic_3])`.

## Argument

1. **Alphabet and distances.** The positive Cayley graph on `{u,v}` reaches all
   twelve group elements; the distance table is identical to the predecessor
   `EXPECTED.json` receipt (cross-checked in `verify.py`).
2. **Product table.** Breadth-first enumeration of distinct products of paid
   factors yields exactly `1 + 56 + 2352 + 92318 = 94727` matrices through depth
   three, matching the predecessor histogram.
3. **Meet-in-the-middle.** Any word of length `≤ 6` factors as a prefix of
   length `≤ 3` and a suffix of length `≤ 3`. For each eligible target `T` and
   each depth-`≤3` prefix product `P`, test whether `P^{-1} T` lies in the
   depth-`≤3` product table (right-monomial shift of the inverse prefix by the
   diagonal target, as in the predecessor). Exact product replay rejects false
   positives.
4. **Census.** There are exactly `890` triples with `direct ≥ 7`. The search
   returns zero hits; the coverage digest over all eligible endpoints is stored
   in `CERTIFICATE.json`.
5. **Independent engine.** `independent.py` repeats the census with frozenset
   coefficient vectors instead of bit masks and matches the coverage digest.

## Limits

This is a finite exhaustive obstruction at word length six for the stated
direct-bill layer. It does not prove a uniform all-depth lower bound, admit a
BIT supplier, or change kappa.
