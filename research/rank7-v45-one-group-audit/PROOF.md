# Proof note: V45 does not set either selected supplier endpoint

## Predecessors

Marius-Paul Dumitrean, #2979 at `be191346391661f4d35fc0d1508d0a6029572576`, reported five shared rank-7 groups. For V45 the stated joint margin is +22,972 and each single lowering is -53,141, using surrogate prices `c1 = 2116671`, `c2 = 4228346`, `c3 = 6338140`, `c4 = 8446713` and an idle guide of 2,091,300. Nick Petalas, `research/rank7-joint-frame-audit`, independently recounted all five groups and all 16 V45 endpoint subsets and left the idle guide uncertified. `research/rank7-group-a-entrance-audit` does the same for group A and states that the recounted histogram does not certify either supplier cap. This note does not edit those packages.

## Reconstruction

Let the parent be either PR2942 word shipped in #2979. Write frames as subspaces of `F2^9`. The declared V45 subspace is

```text
W = <256, 128, 64, 35, 16, 11, 5>, dim W = 7.
```

Helpers 249, 251, 265 and 267 each have an 8-dimensional parent end, and W is a hyperplane of each. The 61 declared gate edits whose new frame lies only in W, among the five declared groups, are exactly the V45 edits: 20 in B and 41 in restore, with strictly increasing indexes inside each section. Applying those gate edits and replacing any nonempty subset of the four ends by W changes no scalar body and no cleanup list.

A Gaussian-elimination replay and a separate power-set replay both reproduce the parent's stored local profile and width inventory. Against that parent they give

```text
four ends lowered: paid delta -2 H1 + 10 H2 + 6 H3 - 10 H4,
                   widths 8 → 7 on four helpers
one end lowered:   paid delta +1 H1 + 10 H2 + 6 H3 - 10 H4,
                   widths 8 → 7 on that helper
```

The two providers agree. The same surrogate arithmetic as #2979 returns prices -8,388,172 and -2,038,159 and margins +22,972 and -53,141. Those margins are guide comparisons. They are not the selected endpoints below.

The final words still end the four helpers on W. Cleanup grows from 86 private buffers to 91 only by helpers 226, 228, 230, 363 and 395.

## Supplier endpoints

The reviewed selected assembly at this base records

```text
κ = 836330098538459/500000000000000000 = 0.001672660197076918
complex lower = 67018507072324140917/40000000000000000000000
bit lower     = 1733427039589844234749/1000000000000000000000000
binding       = complex
```

with `complex lower < bit lower` and `κ < complex lower`. The bit word is PR589's `v = 111` record and contains none of 249, 251, 265, 267. The selected complex profile is not the parent profile and not the V45-edited profile. The V45-only width multiset is not the five-group stage-one inventory, so that stage's fixed-capacity cap is not a V45 cap.

## Obstruction

The V45 joint-versus-single invoice is an exact local frame, width, cleanup and chronology identity on both providers. It does not determine the selected bit endpoint or the selected complex endpoint. No new selected κ is claimed. Full physical admission of #2979 remains open and is not settled by this group.

## Controls

A frame that does not drop dimension, a cleanup mutation, an omitted V45 gate, and a subspace other than W are rejected. Acceptance uses `need`, so Python `-O` does not disable it.
