"""Source-return host bill for PR840 / odd-kernel fused DATA shears.

Named admitted-screen bill answering #2687 OQ1's first step: charge routing,
precision and dispatch on an immutable-source / exclusive-target boundary,
then compare certified odd kernels to dyadic.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd


def need(ok, message):
    if not ok:
        raise ValueError(message)


# Named unit costs (positive integers). Absolute scale is conventional;
# comparisons use the same units for every kernel.
C = 100  # ordinary ADDRESS child interchange
X = 40  # aligned XOR scan of one DATA row
D = 5  # dispatch per ordered affine event
R_SR = 30  # immutable-source certificate + exclusive-target return (once)

# Odd-modulus specialization screen: every odd integer in [3, 99].
SCREEN = tuple(m for m in range(3, 100) if m % 2 == 1)

KERNELS = (1, 3, 5, 7, 9, 15)
ODD_KERNELS = (3, 5, 7, 9, 15)
J_MAX = 32


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


def coeff_bit_length(value):
    value = Fraction(value)
    return abs(value.numerator).bit_length() + value.denominator.bit_length()


def word_coefficients(k):
    out = []
    for event in address_word(k):
        if event[0] != "affine":
            continue
        out.append(Fraction(event[2]))
        for _, c in event[3]:
            out.append(Fraction(c))
    return tuple(out)


def T_word(k):
    """Coefficient-bit prep (same named tariff as #3702 / ADDRESS_affine_coeff_num_den_bit_sum)."""
    return sum(coeff_bit_length(c) for c in word_coefficients(k))


def closed_form_T_word(k):
    need(type(k) is int and k != 0, "nonzero k")
    a = Fraction(k, 4)
    variable = (a, 1 + a, -a, -a, -1 / a, 1 / a - 1)
    return 20 + sum(coeff_bit_length(c) for c in variable)


def fused_powers(j, kernel=1, sign=1):
    a = odd_kernel_power(j, sign, kernel)
    return (-a, 2 * a, -a)


def baseline_powers(j, kernel=1, sign=1):
    a = odd_kernel_power(j, sign, kernel)
    return (-a, a, a, -a)


def T_program(powers):
    return sum(T_word(k) for k in powers)


def T_fused(j, kernel=1):
    return T_program(fused_powers(j, kernel))


def T_baseline(j, kernel=1):
    return T_program(baseline_powers(j, kernel))


def admitted_count(kernel, screen=SCREEN):
    """Number of screen moduli coprime to the odd kernel (and odd)."""
    need(type(kernel) is int and kernel > 0 and kernel % 2 == 1, "odd kernel")
    return sum(1 for m in screen if m % 2 == 1 and gcd(m, kernel) == 1)


def fused_fixed():
    """Kernel-independent fused charges: 3 children, 2 XOR, 18 affine dispatches, R_SR."""
    return 3 * C + 2 * X + 18 * D + R_SR


def baseline_fixed():
    """Kernel-independent baseline charges: 4 children, 4 XOR, 24 affine dispatches, R_SR."""
    return 4 * C + 4 * X + 24 * D + R_SR


def H_fused(j, kernel=1, I=1):
    """Fully charged fused source-return host bill at instantiate tariff I."""
    need(type(I) is int and I >= 0, "nonnegative instantiate tariff")
    return fused_fixed() + T_fused(j, kernel) + I * admitted_count(kernel)


def H_baseline(j, kernel=1, I=1):
    need(type(I) is int and I >= 0, "nonnegative instantiate tariff")
    return baseline_fixed() + T_baseline(j, kernel) + I * admitted_count(kernel)


def critical_I(j, kernel):
    """Least rational I where odd fused undercuts dyadic fused (positive when A drops)."""
    need(kernel in ODD_KERNELS, "odd certified kernel")
    dT = T_fused(j, kernel) - T_fused(j, 1)
    dA = admitted_count(1) - admitted_count(kernel)
    need(dT > 0, "odd coefficient prep exceeds dyadic")
    need(dA > 0, "odd kernel must exclude some screen moduli")
    return Fraction(dT, dA)


def odd_fused_beats(I):
    """List of (kernel, j, H_odd, H_dyadic) where odd fused strictly undercuts dyadic."""
    need(type(I) is int and I >= 0, "nonnegative I")
    beats = []
    for j in range(0, J_MAX + 1):
        dy = H_fused(j, 1, I)
        for q in ODD_KERNELS:
            bill = H_fused(j, q, I)
            if bill < dy:
                beats.append((q, j, bill, dy))
    return beats
