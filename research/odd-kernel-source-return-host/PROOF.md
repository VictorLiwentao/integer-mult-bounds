# Source-return host bill for odd-kernel DATA shears

## Claim

Let `address_word(k)` be the seven-event ADDRESS lowering of
`M(k)=I+(k/4)sr^T` used by PR840 / `#2687`. Let `T_word(k)` be the named
coefficient-bit prep tariff

```text
T_word(k) = Σ_{c=p/q} (bit_length(|p|)+bit_length(q))
```

and write `T_fused(q,j)=2·T_word(q·2^j)+T_word(q·2^{j+1})` for the three-query
fused power list. Fix the odd-modulus screen

```text
SCREEN = { m ∈ ℤ : 3 ≤ m ≤ 99, m odd }     (|SCREEN|=49)
A(q)   = |{ m ∈ SCREEN : gcd(m,q)=1 }|
```

and the named positive integer units

```text
C=100, X=40, D=5, R_SR=30.
```

Define the **source-return admitted-screen host bill**

```text
H_fused(q,j;I)     = 3C + 2X + 18D + R_SR + T_fused(q,j) + I·A(q)
H_baseline(q,j;I)  = 4C + 4X + 24D + R_SR + T_baseline(q,j) + I·A(q)
```

with `T_baseline(q,j)=4·T_word(q·2^j)`. Here `R_SR` charges one immutable-source
certificate (source `y` is never written) plus exclusive-target return after
the completed shear; `I·A(q)` charges per-admitted-modulus specialization /
routing on `SCREEN`.

Then for every certified kernel `q∈{1,3,5,7,9,15}` and every `j∈{0,…,32}`:

1. **I=0 recovers coefficient-only obstruction.**  
   `H_fused(q,j;0) > H_fused(1,j;0)` for every odd `q` (165 comparisons).  
   This is the `#3702` / `#2687` OQ2 subsystem embedded as `I=0`.

2. **Critical instantiate threshold.**  
   `H_fused(q,j;I) < H_fused(1,j;I)` iff  
   `I > (T_fused(q,j)-T_fused(1,j))/(A(1)-A(q))` whenever `A(q)<A(1)`.  
   The least such critical value on the certified grid is  
   `I* = 14/17` at `(q,j)=(3,0)`.

3. **Unit routing favors one small odd shear.**  
   At integer `I=1`, there is **exactly one** odd fused beat of dyadic:  
   `(q,j)=(3,0)` with `H_fused(3,0;1)=674 < 677=H_fused(1,0;1)`.  
   At `I=2`, there are exactly `33` beats, all at `q=3` for every `j∈0..32`.

4. **Fusion still beats baseline.**  
   `H_baseline(q,j;I)-H_fused(q,j;I) = 210 + 2·T_word(a) - T_word(2a)` with
   `a=q·2^j`, independent of `I` and `A(q)`, and is strictly positive on the
   whole grid.

Selected kappa is unchanged.

## Source-return boundary

The boundary matches PR840 equation (6)'s contracts:

- Source `y` is never modified (immutable-source certificate in `R_SR`).
- Target `x` requires exclusive access until the completed endpoint.
- Each query pays one ordinary ADDRESS child (`C`), six ordered affine events
  with dispatch (`D`) and coefficient prep (`T_word`), and each XOR pays `X`.
- Fused programs use three queries / two XOR scans; baseline uses four / four.

This is a named fully charged host bill for the recursive-interface shear, not
a production BIT-supplier admission.

## Why this is not a `#3702` retarget

`#3702` fixes `I=0` (coefficient bits only) and proves zero odd fused beats.
The new checkable fact is the admitted-screen routing term `I·A(q)`, which
**can reverse** the odd-vs-dyadic order because odd kernels exclude screen
moduli (`A(3)=32 < A(1)=49`). At `I=1` the reverse occurs exactly once on the
certified grid. Soft-overlap with `#3702` is intentional reuse of `T_word` as
the prep subsystem, not a reprint of its zero-beat claim.

## What this does not claim

- No production BIT-supplier hosting or kappa change.
- No alternate screen beyond `ODD_MODULI_3_99`.
- No claim that every physical instantiate tariff equals the conventional unit
  `I=1`; the lemma records the exact critical threshold `14/17` and the `I=0/1/2`
  census so a later supplier measurement can be compared.
