"""Alternate ADDRESS physical tariffs for odd-kernel vs dyadic census.

Three named tariffs on the same address_word(k) affine coefficients, distinct
from the published #3702 bit-sum tariff ADDRESS_affine_coeff_num_den_bit_sum:

  ADDRESS_affine_coeff_max_height
      max over coeffs of bit_length(|p|)+bit_length(q)  [sign-sensitive]

  ADDRESS_affine_coeff_shared_den_packing
      rewrite all coeffs over L = lcm(dens); charge L.bit_length() plus
      rewritten-numerator bit lengths  [sign-sensitive]

  ADDRESS_affine_coeff_odd_core_bit_sum
      strip factors of 2 from num and den; charge odd-core bit lengths
      (modulus-dependent / 2-adic-normalized)  [sign-invariant]

Fused/baseline always sum T_word over the signed power lists
(-a,2a,-a) / (-a,a,a,-a).

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from fractions import Fraction
from math import lcm


def need(ok, message):
    if not ok:
        raise ValueError(message)


def odd_kernel_power(j, sign=1, kernel=1):
    need(type(j) is int and j >= 0, "nonnegative dyadic index")
    need(type(sign) is int and sign in (-1, 1), "integer sign")
    need(type(kernel) is int and kernel > 0 and kernel % 2 == 1, "positive odd kernel")
    return sign * kernel * (1 << j)


def address_word(k):
    """Seven events for M(k)=I+(k/4) s r^T; identical shape to odd-kernel-query-pair."""
    need(type(k) is int and k != 0, "nonzero integer query power")
    a = Fraction(k, 4)
    return (
        ("affine", 2, Fraction(1), ((0, Fraction(-1)),)),
        ("affine", 3, Fraction(1), ((0, Fraction(1)),)),
        ("affine", 5, a, ((0, 1 + a), (2, -a), (3, -a))),
        ("child", 0, 5),
        ("affine", 2, Fraction(1), ((0, Fraction(1)),)),
        ("affine", 3, Fraction(1), ((0, Fraction(-1)),)),
        ("affine", 5, -1 / a, ((0, 1 / a - 1), (2, Fraction(1)),
                              (3, Fraction(1)))),
    )


def word_coefficients(k):
    """All affine diagonal and control coefficients of address_word(k)."""
    out = []
    for event in address_word(k):
        if event[0] != "affine":
            continue
        out.append(Fraction(event[2]))
        for _, c in event[3]:
            out.append(Fraction(c))
    return tuple(out)


def coeff_bit_length(value):
    value = Fraction(value)
    return abs(value.numerator).bit_length() + value.denominator.bit_length()


def odd_core_bit_length(value):
    """Bits of the odd parts of numerator and denominator."""
    value = Fraction(value)
    p = abs(value.numerator)
    q = value.denominator
    while p % 2 == 0 and p > 0:
        p //= 2
    while q % 2 == 0:
        q //= 2
    return (0 if p == 0 else p.bit_length()) + q.bit_length()


TARIFF_NAMES = (
    "ADDRESS_affine_coeff_max_height",
    "ADDRESS_affine_coeff_shared_den_packing",
    "ADDRESS_affine_coeff_odd_core_bit_sum",
)


def T_word_max_height(k):
    """Named max-height tariff."""
    return max(coeff_bit_length(c) for c in word_coefficients(k))


def T_word_shared_den_packing(k):
    """Named shared-denominator packing tariff."""
    coeffs = word_coefficients(k)
    dens = [c.denominator for c in coeffs]
    L = dens[0]
    for d in dens[1:]:
        L = lcm(L, d)
    charge = L.bit_length()
    for c in coeffs:
        rewritten = abs(c.numerator) * (L // c.denominator)
        charge += rewritten.bit_length()
    return charge


def T_word_odd_core(k):
    """Named modulus-dependent odd-core bit-sum tariff."""
    return sum(odd_core_bit_length(c) for c in word_coefficients(k))


T_WORD = {
    "ADDRESS_affine_coeff_max_height": T_word_max_height,
    "ADDRESS_affine_coeff_shared_den_packing": T_word_shared_den_packing,
    "ADDRESS_affine_coeff_odd_core_bit_sum": T_word_odd_core,
}


def fused_powers(j, kernel=1, sign=1):
    a = odd_kernel_power(j, sign, kernel)
    return (-a, 2 * a, -a)


def baseline_powers(j, kernel=1, sign=1):
    a = odd_kernel_power(j, sign, kernel)
    return (-a, a, a, -a)


def T_program(T_word, powers):
    return sum(T_word(k) for k in powers)


def T_fused(T_word, j, kernel=1):
    return T_program(T_word, fused_powers(j, kernel))


def T_baseline(T_word, j, kernel=1):
    return T_program(T_word, baseline_powers(j, kernel))


def reference_bit_sum_T_word(k):
    """Published #3702 bit-sum (reference only; not one of the alternate claims)."""
    return sum(coeff_bit_length(c) for c in word_coefficients(k))
