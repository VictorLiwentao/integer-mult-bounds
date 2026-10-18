# Proof: flag 1's relocation window under the `C`-pinned least-frame model

## Setup and cited facts

Pin CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`. Inputs are the
hash-pinned #1991 witness and the #2981 flag matching (flag 1: source 0,
target 7, basis head 232). The frame semantics are those of
`research/p104-native-channel/PROOF.md` §2–§3. Transports are nested and pay
`|Δ dim|`, and an ADD or copy needs both registers in one chart.

The following are #3532's facts. They are rechecked here, not re-derived as new
results.

- 2797 (`Y7 += D17/4`, chart `[95, 486]`) is the only `Y7` update carrying `X0`.
- `D17`'s row is written only at 2497 and 3613, and `Y7` is never read. So the ADD
  commutes over 1,115 slots, labelled by the published event it follows
  (2497–2796 and 2798–3612).
- All 280 non-private registers sit at their rank floor. By parity, any repair
  adds either zero non-private rank mass, with every non-private frame path
  monotone, or at least 2.
- #3532's R0 and R1 add exactly 2 and leave `C`'s events unchanged.

## The model (from the flag-9 harness, unchanged)

Fix a slot for the moved ADD. Walk the word with `L(r) = init(r)`.

- At each ADD or copy between non-private `a` and `b`, set
  `L(a) = L(b) = L(a) + L(b)`. At the moved ADD, also add the head 232
  (head-forced) or nothing (head-free).
- **Relaxed.** Skip every event involving `C`.
- **Pinned on a set S of private events.** At each event of S, with partner `r`
  and published chart `c`, the placement is infeasible if `L(r) ⊄ c`; otherwise
  set `L(r) = c`. Events outside S are skipped. Full pinning is S = all 40
  private ADD/copy events, 2462–2523.

A placement is *obstructed* if some `L(r) ⊄ final(r)` at the end, or if a chart
check fails. In any zero-surcharge word of the class (private events in S kept
with their charts, monotone non-private paths), each frame contains `L` at
every event, by induction. An obstructed placement therefore has no zero-mass
completion. This is the flag-9 harness's lemma. `headstep.py` is loaded
byte-for-byte, and `verify.py` checks its SHA-256 first.

**Monotonicity in S.** If `S ⊆ S'`, then `L_S ≤ L_S'` pointwise at every event,
by induction: joins are monotone, and an event in `S' \ S` only enlarges
`L_S'`. Final violations and chart violations are therefore inherited from S to
S'. So an obstruction under S is an obstruction under S', and an open slot
under S' is open under S.

## Results

1. **Scans** (all 1,115 slots, in `CERTIFICATE.json` → `scans`). With the head
   forced, the relaxed model obstructs 868 slots and the 247 after 3366 are open
   (#3532's numbers). The pinned model obstructs all 1,115. On every late slot,
   its only violated constraint is `final(Y7)`. Head-free, the relaxed model
   obstructs nothing. That matches the free row commutation. The pinned model
   obstructs 458 slots: 29 directly after 2497–2525, and every slot after 3184
   through 3612 (429), the latter by `final(Y7)` alone.

2. **Why.** `final(Y7) = span(256, 128, 64, 33, 17, 9, 5, 2)` has rank 8. Its
   unique annihilator is `w = 61`, so `final(Y7) = {x : popcount(x & 61) even}`.
   Under full pinning, `L(D17)` (published word without 2797) is `[486]` after
   2797 and `[441, 95]` after 3183, both even. After the read `Y31 += D17` at 3184
   it is rank 4 and not inside. After 3366 it is `[395, 75, 32, 18, 6]`, and 32,
   18 and 6 are odd. At any late slot, the moved ADD makes
   `L(Y7) ⊇ L(D17) ⊄ final(Y7)`. Nothing later shrinks `L`, so the placement is
   obstructed whether or not the head is forced.

3. **Core.** Let K = {2480 `D8 += C` `[447]`, 2482 `D10 += C` `[447]`,
   2504 `D20 += C` `[127]`, 2511 `D23 += C` `[500]`}. All four charts are odd.
   - For each `p` in K, pinning `S = {p}` obstructs all 247 late slots, by
     `final(Y7)` alone.
   - Pinning `S` = the 36 private events outside K leaves all 247 late slots
     open.

   By monotonicity, for every subset S of the 40 private events and every late
   slot, the slot is obstructed under S if and only if S meets K. In particular,
   releasing any single private event leaves all 247 closed, and `D17`'s own
   chart `[486]` at 2497 is not load-bearing.

   Each `p` in K reaches `D17` along the committed chain of first exits from
   `final(Y7)`:
   - 2480 → 2552 `Y14 += D8` → 2735 `Y14 += D5` → 3007 `Y31 += D5` → 3184
     `Y31 += D17`;
   - 2482 → 2832 `Y31 += D10` → 3184;
   - 2504 → 2646 `Y31 += D20` → 3184;
   - 2511 → 2698 `Y59 += D23` → 3364 `Y59 += D17`.

   `independent.py` checks every link. Each link is the published event, links
   share a register, and at each link one register was inside `final(Y7)` before
   and both are outside after.

## Consequences

- **Pinned class.** No relocation of the delivering ADD that keeps `C`'s
  published events co-hosts the head at zero added mass, at any of the 1,115
  slots. With #3532's parity floor and its R0/R1, which keep `C`, +2 is the
  exact floor over the full relocation window in that class. Here this package
  strengthens #3532, which closes only the 868 early slots.
- **Relaxed class.** Nothing new is claimed about existence. The obstruction
  analysis does say where a zero-mass late repair would have to differ from the
  published word: it must change `C`'s common chart at all four events of K.

## Limits

- No repaired word is built or natively validated. All feasibility verdicts are
  least-frame verdicts, and they are sound only as obstructions.
- The class keeps every non-moved event and its partner pair. Only charts and
  transports may change, as in #3532 and the flag-9 package. Repairs that add,
  drop or reorder other events are outside it.
- "Re-chart" in the open question means the chart of `D_k += C` no longer
  contains the published odd vector. Which charts the native framed induction
  admits for those ADDs is not examined.
- Flags 0, 9 and 43 are not recomputed. #3532's R0/R1 bill is cited, not
  recomputed.
