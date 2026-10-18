# Proof: non-self co-chart hosts on the flag-0 tail cut

## Claim

On the published #2089 augmented witness, events 5758/5759/5807 form a
promote/add/restore triple for target `Y34` with source read `X0`. Among
registers named as ADD sources in that window, every register other than `X0`
holds host chart `FULL` at the ADD, remains `FULL` after restore, has no
destination event after the 4,058-event channel prefix, and shares the window's
zero dirty-helper touches and zero endpoint repayment toward initials. Those
**47** registers are non-self co-chart host alternatives to schedule S0 on the
published word. Among registers named by ADD 5759 alone, the unique source
owner remains `X0`. Broader census: all **103** non-`X0` X-registers are
likewise co-chart. No new κ.

## Inputs

Pinned at CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`:

- `research/p104-native-channel/inputs/LOWRANK-WITNESS.json` (#1991 channel)
- `research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz` (#2089)
- `research/p104-tail-side-correction-seed749717/CORRECTION-ROWS.json`
- `research/p104-tail-flag0-owner/RESULT.json` (prior: no owner field)
- `research/p104-channel-touch-restoration-audit/CERTIFICATE.json` (#3349)

Hashes are in [SOURCES.json](SOURCES.json). This package answers open
[#3683](https://github.com/CrocSwap/integer-mult-bounds/pull/3683) OQ1; it does
not vendor #3683's certificate (leave that package alone).

## Setup

Write `FULL = [1,2,4,8,16,32,64,128,256]` and
`RANK8 = [499,23,232,32,112,15,7,2]`. The channel leaves `X0` at `FULL` and
`Y34` at `RANK8`. Event 5758 is `transport Y34: RANK8 → FULL`. Event 5759 is
`add Y34 X0 -1/2 FULL`. Event 5807 is `transport Y34: FULL → RANK8`. The window
contains exactly 50 events: 2 transports and 48 `Y34` adds. No top-level field
in the window is a dirty helper name (`D*`/`G*`/`Q*`/`C`).

## Window ADD-source census

Scan adds in event order. The first-seen source registers are exactly the 48
names recorded in [CERTIFICATE.json](CERTIFICATE.json) as
`window_add_sources_first_seen`, beginning with `X0` and continuing through
`X100`. Removing `X0` leaves 47 non-self names.

## Co-chart and zero-repay for each non-self name

A forward frame walk (and independently, per-register transport reconstruction)
shows: for every non-self window ADD source `Xi`,

1. the live frame at event 5759 equals `FULL`;
2. the live frame after event 5807 equals `FULL`;
3. every destination event of `Xi` in `[0,5807]` has index `< 4058`;
4. `FULL` differs from `Xi`'s initial frame, so the post-restore frame is not a
   repayment toward the initial.

Together with the window's zero dirty-helper touches and the already-checked
`X0`/`Y34` non-repayment, each such `Xi` is a legal interpretive co-chart host
assignment `S_cochart_Xi` (`owner=Xi`, `host_chart=FULL`) with the same dirt and
endpoint-repay profile as S0 on the published word.

## Uniqueness on ADD 5759 alone

ADD 5759 names exactly `{Y34, X0}`. The write target cannot own the source
read, so among registers named by that single ADD the unique source owner is
still `X0`. Non-self alternatives require the larger window-named (or all-X)
search domain; they are not a second owner inside the ADD-5759 name set.

## Broader all-X census

The same frame walk on `{X0,…,X103}` shows every non-`X0` X-register holds
`FULL` at the ADD and after restore, with no post-channel destination and no
repayment to its initial. Count: 103.

## Semantic scope

These are **interpretive co-chart host** assignments on the published word.
They do not rewrite ADD 5759, do not claim `Xi` equals `X0` as a vector, and do
not construct a fresh dirty-helper copy path. Vector-equal copied-host words and
priced host-rank mass remain open.

## What this does not prove

- A dirty-helper copied-host construction or its rank-mass floor (#3683 TASK OQ)
- A constructed dirt-restore program inserted into 5758–5807 without enlargement
- A global 104×104 owner map or supplier admission
- Anything about #3669 OQ1 / deferred flag0 head-span schedule / open #3532

## Independence

`verify.py` walks frames in program order. `independent.py` rebuilds frames from
per-register transport indexes. Neither imports the other or the native
checker. Both compare against [CERTIFICATE.json](CERTIFICATE.json). Temp-copy
corruptions of that certificate and of the gzipped witness are rejected under
`-O`.
