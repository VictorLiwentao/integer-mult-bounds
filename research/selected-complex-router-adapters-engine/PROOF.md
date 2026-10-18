# Proof note: engine-measured routing∪adapters rho share

## Setup

Fix the selected m=73 complex stopped producer. The coarse-depth stock proof
names four leaf-call classes:

> Ordinary peeled atoms, routing, adapters and high-part exchanges are
> separate completed calls.

[#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421) binds
`A = 0`, `B_bits = 2642` for the finite-stock-as-`C` candidate and leaves
`rho` unbound. Composition:

```text
sigma <= (43/26)*(1-s)*2642 + rho
```

Write `rho = rho_routing + rho_adapters + rho_peeled + rho_highpart`
along the inventory (nonnegative summands). This note bounds
`rho_routing + rho_adapters`.

## Operation class

`notes/three-stage-cover-complex.tex` places fixed address adapters, endpoint
Paulis and invocation permutations inside the finite scalar/router guard,
reconciles representative differences by rank-zero adapters (no positive-rank
data connectors), and states that fixed permutations and signs incur
scalar/router charges without recursive Fourier children. The BIT cover, by
contrast, routes fixed ports through a constant number of ordinary
width-`O(w)` interchanges (`notes/three-stage-cover-bit.tex`;
`stock-routing-factor` records the unnamed `c_R`). High-part exchange remains
an ordinary width-`k` interchange (`notes/three-stage-cover-rows.tex`).

## Finite residual engine

`router.py` executes a characteristic-two residual whose only operations are:

1. rank-zero adapter translations,
2. three fixed scalar shears matching the cover's `(X,Y)` composition on
   `\mathbb F_2`,
3. an endpoint Pauli translation,
4. a fixed invertible linear map `F`.

The engine exposes no ordinary leaf path and no recursive Fourier child path.
Parent reserve is a spectator list; the residual never reads it as an active
field.

## Measured costs

On every input of the exhaustive `m=3` domain (`2^{6}=64` cases) and on the
`m=4` reserve-independence pair (extents 1 and 3):

```text
ordinary_leaf_calls = 0
recursive_fourier_children = 0
positive_rank_connectors = 0
parent_reserve_active_reads = 0
```

Define `rho_contrib = 0` exactly when those four meters are zero, else `1`.
Hence `rho_contrib = 0` on the clean residual, so

```text
rho_routing + rho_adapters = 0
```

for this operation class under the engine's metering contract. Mutants that
inject an ordinary leaf call, a Fourier child, or a parent-reserve active read
measure `rho_contrib = 1`, so the meter is not vacuously stuck at zero.

## What is not claimed

- Global `rho = 0` (peeled and high-part remain).
- Byte-identical production assembler replay.
- Recomputation of `A` or `B_bits`.
- Substitution of inherited slack `252` for `rho`.
- New kappa.

## Independent check

`independent.py` re-pins sources, rebuilds exhaustive and independence meters
without importing `verify.evaluate`, and checks a mixed Pauli/permutation
closed form against `expected_endpoint`.
