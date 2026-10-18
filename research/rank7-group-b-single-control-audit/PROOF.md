# Proof note: group B joint win versus single-299 loss

## Claim

On both literal #2979 providers (`base` and `extra`), reconstruct only the
group-B stage-one frame edits from the pinned `STAGE1-FRAME-EDITS.json`:

- shared endpoint \(W=\langle 256,128,64,34,17,11,4\rangle\);
- helpers \(\{299,448,449,484,485\}\);
- twenty-one gate-frame edits whose new frames lie in \(W\).

Then:

1. The joint lowering of all five endpoints to \(W\) has paid-profile delta
   \(\Delta=(-1)H_1+20H_2-14H_3+2H_4-2H_5\), surrogate price delta
   \(-10499041\), five freed entrance-relative width units, and guide margin
   \(+42541\).
2. The single-299 control keeps the same twenty-one partner gate frames but
   lowers only helper 299. Its paid-profile delta is
   \(\Delta=3H_1+20H_2-14H_3+2H_4-2H_5\), surrogate price delta \(-2032357\),
   one freed width unit, and guide margin \(-58943\).
3. Entrance-relative widths on the joint word are
   \(299:7\), \(448:6\), \(449:6\), \(484:6\), \(485:6\). Helpers
   \(448,449,484,485\) enter at `[51]`; helper 299 enters at zero.
4. The shipped T74 fill places each of the five helpers once per call
   (\(666\) placements each, \(3330\) total).

Guide margins use the pinned search-time coefficients
\(c_r=\lfloor 2^{40}T_r(b)\rfloor\) and break-even \(2091300\) from
`STAGE-PRICES.json`. They are not a certified physical idle tariff and do not
admit a supplier or change κ.

## Argument

Parent words are authenticated byte-for-byte. Group ownership of each of the
139 stage-one gate edits is the unique rank-seven group space containing the
new frame; exactly twenty-one edits belong to \(W\). Applying those edits and
the chosen endpoint subset changes only `helper_final` and gate trailing
frames; scalars, operators and cleanup are unchanged.

Paid ranks are the chronological climb ranks of the finite frame contract on
`A`, centre copies, `B` warps/gates, `restore` and terminal ends. The two
scanners recompute that ledger independently: one by explicit XOR closure of
generators, one by annihilator masks in \(\mathbb F_2^9\). Both return the
same profiles, widths and margins on both providers.

The margin identity is
\(\mathrm{margin}=-\Delta_{\mathrm{price}}-\mathrm{break\_even}\cdot\mathrm{freed}\).
Substituting the recomputed values reproduces the pinned group-B
`joint_margin` and `singles_margin[299]` exactly. The joint word’s
`helper_final` entries for the five helpers equal the shipped `WORD-*.json.gz`
endpoints.

## Limits

This package does not replay native residual recipes, private cleanup
semantics, physical movement/storage, precision, bit-supplier coupling or
outer release. The selected κ remains `0.001672660197076918`.
