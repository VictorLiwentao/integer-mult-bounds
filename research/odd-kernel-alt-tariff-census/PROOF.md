# Alternate ADDRESS physical tariffs vs dyadic

## Claim

Let `address_word(k)` be the seven-event ADDRESS lowering of
`M(k)=I+(k/4)sr^T` used by PR840 / `#2687` / `#3702`. Define three **named
alternate** physical tariffs on its affine coefficients, each distinct from
the published `#3702` bit-sum
`ADDRESS_affine_coeff_num_den_bit_sum`:

```text
ADDRESS_affine_coeff_max_height
    T_word(k) = max_{c=p/q} ( bit_length(|p|) + bit_length(q) )

ADDRESS_affine_coeff_shared_den_packing
    L = lcm(denominators); T_word(k) = bit_length(L)
        + Σ bit_length(|num| · L / den)

ADDRESS_affine_coeff_odd_core_bit_sum
    for each c=p/q, strip factors of 2 from |p| and q;
    charge bit_length(odd_p) + bit_length(odd_q)
```

Program bills match `#3702`:

```text
T_fused(q,j)     = 2·T_word(q·2^j) + T_word(q·2^{j+1})
T_baseline(q,j)  = 4·T_word(q·2^j)
```

Then for every certified odd kernel `q ∈ {3,5,7,9,15}`, every
`j ∈ {0,…,32}`, and each of the three tariffs:

```text
T_fused(q,j)     ≥ T_fused(1,j)      (never a strict beat)
T_baseline(q,j)  ≥ T_baseline(1,j)   (never a strict beat)
```

In particular, fused is always a strict exceedance (`165` per tariff). Baseline
has a single tie under max-height at `(q=3,j=0)` with bill `22`
(`2·T_word(-3)+2·T_word(3) = 2·5+2·6`), and is a strict exceedance on the
other `164` pairs for that tariff and on all `165` pairs for packing and
odd-core. Max-height and packing are **sign-sensitive**
(`T_max(32)=7 ≠ T_max(-32)=8`; `T_pack(3) ≠ T_pack(-3)`); odd-core remains
sign-invariant. Fused/baseline therefore charge the actual signed power lists.

Selected kappa is unchanged.

## Distinctness from `#3702`

On every `|k|∈{1,…,64}`, each alternate `T_word` disagrees with the published
bit-sum `T_word`. Spot values:

| k | bit-sum (#3702) | max-height | packing | odd-core |
|---:|---:|---:|---:|---:|
| 1 | 45 | 6 | 48 | 35 |
| 2 | 38 | 4 | 32 | 33 |
| 3 | 49 | 6 | 69 | 39 |
| 4 | 32 | 3 | 17 | 31 |
| 5 | 55 | 7 | 84 | 45 |

## Grid evidence (fused `j=2`, signed powers)

| q | max-height | packing | odd-core |
|---:|---:|---:|---:|
| 1 | 9 | 70 | 95 |
| 3 | 16 | 143 | 115 |
| 5 | 20 | 191 | 134 |
| 7 | 22 | 205 | 134 |
| 9 | 26 | 251 | 153 |
| 15 | 28 | 265 | 153 |

## Relation to `#3702` OQ1

`#3702` closed the bit-sum obligation and left open whether max-height,
packing, or modulus-dependent encodings could reorder odd vs dyadic. This
package admits those three families as named tariffs and answers in the
negative on the certified kernel grid `j=0..32`.

## What this does not claim

- No fourth alternate tariff beyond the three named here.
- No BIT-supplier hosting bill (still `#2687` OQ1 / `#3702` OQ2).
- No reprint of the `#3702` bit-sum `165+165` exceedance claim as a new result.
- No new kappa and no production adoption.
