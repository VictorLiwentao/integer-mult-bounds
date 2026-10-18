# Proof sketch — gate-operand dest-absent vs simple-support (#3696 OQ1)

## Setup

Reuse the #3696 operators on bit-register valuations:

- **Sym** (checker / accumulate-XOR): `acc = XOR_{s in srcs} val[s]`; then `out[d] = val[d] XOR acc`.
- **Exp** (exporter sequential ADD): for each `s` in `srcs` in order, `out[d] ^= out[s]`.

Predecessor tip `0581402f978addb2eda5306fd124001486c76b08` (`research/gate-operand-export-parity/`)
proves: if `d ∉ srcs` then Sym = Exp for every length; if `d ∈ srcs` then disagreement
is possible (`self_even`, `dest_with_src`).

Domain for the guard census (same as #3696 small domain): `n = 6` registers,
source lists of length `0..4`.

## Guards

- **Simple-support:** `len(set([d] + srcs)) == len([d] + srcs)` (every listed register distinct).
- **Destination-absent:** `d ∉ srcs`.

Observation: simple-support implies destination-absent.

## Soundness

By the #3696 dest-free lemma, destination-absent acceptance implies Sym = Exp.
Hence neither guard can accept a disagreeing pattern: every dest-in divergent
case fails destination-absent (and therefore also fails simple-support).

Exact census on the domain:

| quantity | count |
|---|---|
| dest-free agree | 4686 |
| dest-in disagree | 3492 |
| dest-in agree | 1152 |
| simple-support accept | 1236 |
| simple-support reject among dest-free agree | 3450 |
| dest-absent reject among dest-free agree | 0 |
| either guard miss among dest-in disagree | 0 |

## Sharpness for #3696 OQ1

OQ1 asks for a guard that (i) rejects all dest-in divergent cases and (ii) does
not reject agreeing dest-free lists.

- **Simple-support:** (i) yes (3492/3492); (ii) **no** — rejects 3450 agreeing
  dest-free lists. Smallest witness: `d = 1`, `srcs = [0, 0]` (duplicate source,
  destination absent; Sym = Exp, but not simple).
- **Destination-absent:** (i) yes (3492/3492); (ii) **yes** — rejects 0 agreeing
  dest-free lists. Accepted set equals the dest-free (hence agreeing) set on this
  domain.

Named controls: both guards reject `#3696` witnesses `self_even` / `dest_with_src`;
`dup_src` agrees and is dest-absent-accepted but simple-rejected; `self_once` agrees
as dest-in and is rejected by both (outside OQ1's dest-free preservation clause).

## Selected-word positive control

All 5472 selected D/A/B/C gates already satisfy both guards (distinct operands).
That is a positive control, not a new selected-word defect and not a reprint of
the #3696 export-without-check claim.

## Kappa

Selected κ unchanged: `0.001672660197076918`.
