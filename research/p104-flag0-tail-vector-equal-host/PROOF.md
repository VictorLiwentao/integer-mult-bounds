# Proof: vector-equal dirty-helper host with outside-window dirt restore

## Claim

Start from the published #2089 augmented witness. Form a spliced word W' by
inserting five events around the flag-0 promote/add/restore window
(5758/5759/5807):

```text
# immediately after the 4,058-event channel prefix
zero  C   FULL
copy  C  ← D0   FULL     # save restored dirt
copy  D0 ← X0   FULL     # vector-equal host

# unchanged published window (indices shifted by +3)
transport Y34: RANK8 → FULL      # promote
add       Y34 ← (-1/2)·X0 FULL   # ADD (still reads X0)
… 47 further Y34 adds …
transport Y34: FULL → RANK8      # restore

# immediately after the window
copy  D0 ← C   FULL     # restore D0 dirt
erase C   FULL
```

On W', schedule **S_D0** assigns `owner = D0` on host chart `FULL` at the ADD.
Then:

1. At the ADD, `D0` is vector-equal to `X0` (copy semantics + destination freeze).
2. The promote/add/restore window still has length 50 and zero dirty-helper touches.
3. Displaced `D0` dirt is restored after the window; other dirty helpers are
   untouched by the splice.
4. `X0`/`Y34` remain at their unrestored channel finals after the window
   (zero endpoint repayment toward initials).

Exact added cost: **+5 events**. No new κ.

## Inputs

Pinned at CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (hashes in
[SOURCES.json](SOURCES.json)):

- `research/p104-native-channel/inputs/LOWRANK-WITNESS.json`
- `research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz`
- `research/p104-tail-side-correction-seed749717/CORRECTION-ROWS.json`
- `research/p104-tail-flag0-owner/RESULT.json`
- `research/p104-channel-touch-restoration-audit/CERTIFICATE.json`

## Setup

Write `FULL = [1,2,4,8,16,32,64,128,256]` and
`RANK8 = [499,23,232,32,112,15,7,2]`. The channel leaves `X0` and every `D*`
helper (including `D0`) at `FULL`, and `Y34` at `RANK8`. The published tail
has **zero** dirty-helper mentions after the channel prefix and **zero**
`copy · ← X0` events. Scratch `C` is absent from channel finals (last used as
a mid-channel private-copy temporary and erased).

## Vector equality at the ADD

Let `e_eq` be the spliced event `copy D0 ← X0 FULL`. After `e_eq`, the live
value of `D0` equals the live value of `X0` by the copy rule. In W' the next
destination event of `X0` after `e_eq` does not exist before the ADD (published
last write remains event 1486). The next destination event of `D0` after `e_eq`
and at or before the ADD is empty. Therefore at the ADD both registers still
carry the post-copy value, so they are vector-equal. Both frames are `FULL`,
matching the ADD's chart annotation and `Y34`'s promoted frame.

Independently, a value-id walk (fresh id on overwrite; share id on copy) reaches
the same conclusion: after `e_eq` and through the ADD, `id(D0) = id(X0)` while
`id(C) ≠ id(X0)` (the saved dirt).

## Window length and dirt non-touch

The published window occupies indices 5758…5807 (50 events: 2 transports, 48
adds). The prefix splice has length 3 and sits entirely before the window; the
suffix splice has length 2 and sits entirely after. The shifted window is
5761…5810, still length 50, and still equals the published window byte-for-byte.
No top-level field in that window is a dirty-helper name, so
`dirty_helper_touches_in_window = 0`.

## Dirt save and restore

Before overwriting `D0`, the splice writes `copy C ← D0`. Between that save and
the post-window `copy D0 ← C`, scratch `C` is never a destination, so the saved
dirt is intact. The restore copy returns `D0` to its pre-overwrite value. The
five splice events mention only dirty names `D0` and `C`; every other dirty
helper is untouched by the splice. This is a constructed dirt-restore of the
single displaced helper, placed entirely outside the promote/add/restore window,
so the window is not enlarged.

## Endpoint non-repayment

After the (shifted) restore transport, a frame walk gives `X0 = FULL` and
`Y34 = RANK8`, equal to the channel finals and different from the initials
`[232]` and `[]`. No transport in the construction returns either endpoint to
its initial frame.

## Relation to priors

- [#3683](https://github.com/CrocSwap/integer-mult-bounds/pull/3683) certifies
  interpretive self-owned schedule S0 on the **published** word with
  `dirty_helper_touches = 0`. It does not construct a vector-equal host or a
  dirt save/restore program.
- Deferred `p104-flag0-tail-copied-host` counts interpretive co-chart X-register
  peers on the published word (no vector equality, no dirty-helper construction).
- This package answers the strong reading of #3683 OQ1 (vector-equal dirty-helper
  copy) and the dirt-restore half of #3683 OQ2, with exact +5 event cost and
  unchanged window length.

## What this does not prove

- A global owner/host map for all 4,992 source reads
- That every co-chart X-register admits a zero-cost vector-equal host on the
  published word without splicing
- Integration with the #1940 chronological schedule or a new κ
- Anything about the deferred #3532 / flag-0 head-span repair template

## Independence

`verify.py` uses destination-freeze after the equality copy plus frame walks.
`independent.py` uses value-id equality and does not import `verify.py`. Both
compare against [CERTIFICATE.json](CERTIFICATE.json). Temp-copy corruptions of
that certificate and of the gzipped witness are rejected under `-O`.
