# Odd-kernel alternate physical tariff census (answers #3702 OQ1)

**Card `connector-alphabet-change`, priority revision 6**, refined to open
question 1 of
[#3702](https://github.com/CrocSwap/integer-mult-bounds/pull/3702)
(`research/odd-kernel-coeff-bit-tariff`). No new kappa
(`0.001672660197076918`).

[#3702](https://github.com/CrocSwap/integer-mult-bounds/pull/3702) showed that
under the named bit-sum tariff
`ADDRESS_affine_coeff_num_den_bit_sum`, every certified odd kernel exceeds
dyadic on `j=0..32`, and asked whether any alternate physical tariff
(max-height / packing / modulus-dependent) can make an odd kernel beat dyadic
at some `j`. This package names three such tariffs on the same PR840
`address_word` coefficients and answers that obligation in the negative.

**Tariffs (all distinct from the #3702 bit-sum).** For affine coeffs of
`address_word(k)`:

```text
ADDRESS_affine_coeff_max_height
    T_word(k) = max_c (bit_length(|p|)+bit_length(q))

ADDRESS_affine_coeff_shared_den_packing
    L = lcm(dens); T_word(k) = bit_length(L) + Σ bit_length(num rewritten / L)

ADDRESS_affine_coeff_odd_core_bit_sum
    strip factors of 2 from num and den; sum odd-core bit lengths
```

Program bills are the same fused/baseline shapes as #3702:

```text
T_fused(q,j)    = 2·T_word(q·2^j) + T_word(q·2^{j+1})
T_baseline(q,j) = 4·T_word(q·2^j)
```

**Result.** On kernels `{1,3,5,7,9,15}` and every `j∈{0,…,32}`, under each of
the three tariffs, no odd kernel strictly beats dyadic fused or baseline
(`0` beats). Max-height baseline ties once at `(q=3,j=0)` (`22=22`); fused has
no ties. Max-height and packing are sign-sensitive, so bills use the signed
power lists. Each alternate disagrees with the #3702 bit-sum on every
`|k|∈1..64`.

```sh
python3.12 -I -B research/odd-kernel-alt-tariff-census/verify.py
```

Expected:

```text
PASS_ODD_KERNEL_ALT_TARIFF_CENSUS tariffs=3 kernels=[1, 3, 5, 7, 9, 15] j=0..32 odd_fused_beats_dyadic=0 odd_baseline_beats_dyadic=0 no_new_kappa
```

## Evidence

- Three named tariffs with locked spot `T_word` values and fused `j=2` rows.
- Distinctness control vs #3702 bit-sum (`64/64` disagreements on `1..64`).
- Grid: `3×165` fused comparisons with `0` beats; baseline `0` beats and one
  locked max-height tie.
- Inflated-dyadic adversarial control (creates a synthetic beat).
- Byte-pinned `#2687` `address_word` cross-check.

Default verify is read-only against `CERTIFICATE.json`. Admission uses
`need()` and stays enforced under `python -O`. Explicit `--write` regenerates
the certificate only.

## Reproduce

```sh
python3.12 -I -B research/odd-kernel-alt-tariff-census/verify.py
python3.12 -I -O -Werror -B research/odd-kernel-alt-tariff-census/verify.py
python3.12 -I -B research/odd-kernel-alt-tariff-census/independent.py
python3.12 -I -B research/odd-kernel-alt-tariff-census/test_package.py
python3.12 -B scripts/research_package.py --package research/odd-kernel-alt-tariff-census
```

## Open next questions

1. **Does any further alternate physical tariff outside {max-height,
   shared-den packing, odd-core} make a certified odd kernel beat dyadic at
   some `j`?** First step: name a fourth tariff with a physical encoding story
   and replay the grid. Blocked by: no fourth tariff admitted here.
2. **Can an admitted BIT supplier host a small odd-kernel shear with a favorable
   fully charged bill versus dyadic?** First step: one exact source-return
   boundary with routing, precision and dispatch. Blocked by: still
   `#2687` OQ1 / `#3702` OQ2; not constructed here.

## Credit

Credit `#3702` / `research/odd-kernel-coeff-bit-tariff` (OQ1 answered; leave
alone — this package does not reprint the bit-sum `165+165` claim),
`#2687` / `research/odd-kernel-query-pair`, PR840 /
`research/dyadic-query-pair`, and PR521/PR677 ADDRESS / DATA-shear lineage.
Predecessor notices are unchanged.

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. No independent human review is claimed. No new kappa.
