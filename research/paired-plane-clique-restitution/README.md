# Quotient-collision restitution for the paired-plane blocks

**Scoped obstruction. No new κ.** The selected decimal stays
`0.001672660197076918`.

[PR2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203) implements the
56 rank-two matched-plane blocks of the rank-49 paired-plane identity on the
one-array native interface. The direct profile is `{7:224, 2:112}`, copy mass
224, and the favorable two-unpaid moment is `293/292`. That package does not
exclude shared fractional decoders or cross-plane mixing. This package prices
the sharings in which the joint pairing actually collapses.

**Hypothesis (quotient-collision restitution).** If S is a set of these planes
whose joint F2 pairing has rank at most 2, one one-array total on S can be
charged less than `2|S|`. The hypothesis says signed sums of such totals
realize the strict identity on S for copy mass strictly below `4|S|`.

**Theorem.** The hypothesis is false over every field. The induced block is
`I_{2|S|}`. At least `2|S|` totals meet it, and every nonempty complete-plane
support inside S pays pairing rank at least 2, so the copy mass is at least
`4|S|`.

The census is 144 form-rank-2 pairs and 8 form-rank-2 triples, and no 4-plane
set of form rank 2. The sample triple is `[5, 15, 30]`: one total there is
charged 2, and the identity still costs 12. The singleton schedule attains
global copy mass 224 and moment `293/292`.

A reprint of the one-plane bill is not this statement. The one-plane bill
refuses to add floors across planes. Here the planes share a total, the pairing
rank may fall to 2, and the identity rank puts the floor back at 4 per plane.

## Credit

Cinna Davis / PR1825 and PR2126 supply the matching and the identity blocks.
Adam Gall / PR1889 supplies the strict mask. ywz65 / PR2471 and Sagar Thakrar /
PR2484 supply the fitting-rank model and the exact rank 49. The 24-plane
witness uses the same non-orthogonality notion as PR2484's `ω(G)=24`; it is
recorded only to show that this clique contains 173 cross-rank-1 pairs, which
are outside the theorem. Jeremy Diviney / PR2203 supplies the one-array payload
bill `{7:224, 2:112}` and the moment `293/292`, and leaves sharing open.
Philippe Van Velzen's one-total pairing-rank tariff and ctoth's naive 224
baseline are the charge and the attainment this restitution meets on singletons.
PR2541 is the block-rank companion of the scalar rank 49. PR3335 is a different
matching. PR2585 separates the 224 payload bill from the rank-49 channel count.
PR3625 bounds lost-free port sets and does not price this sharing.

## Replay

```sh
python3 -B research/paired-plane-clique-restitution/verify.py
python3 -B research/paired-plane-clique-restitution/independent.py
python3 -B scripts/research_package.py --package research/paired-plane-clique-restitution
```

`verify.py` is read-only on the package tree. It uses `need`, so the gates
survive `python -O`. It rejects a corrupted temporary copy of the certificate
and rejects duplicate JSON keys. `independent.py` does not import it.

## Open next questions

Can a support that is not a form-rank-2 collision, including a cross-rank-1
pair or a total that mixes an orthogonal pair with a non-orthogonal pair, bring
the global complete-plane copy mass below 224? This package does not claim that
the checked 24-plane conflict clique costs 96. The structured question and
blocker are in `TASK.json`.

Prepared by Wentao Li `<wentaol4@illinois.edu>` with substantial AI assistance.
Apache-2.0.
