#!/usr/bin/env python3
"""Independent replay of the alternate-tariff census (no verify import).

Rebuilds the three named T_word functions from closed forms on a=k/4 and checks
that every odd kernel on j=0..32 fails to strictly beat the dyadic fused bill.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from fractions import Fraction
from math import lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = (
    "PASS_ODD_KERNEL_ALT_TARIFF_CENSUS_INDEPENDENT "
    "tariffs=3 j=0..32 odd_fused_beats_dyadic=0 no_new_kappa"
)
ODD = (3, 5, 7, 9, 15)
J_MAX = 32


def need(ok, message):
    if not ok:
        raise ValueError(message)


def bits(value):
    value = Fraction(value)
    return abs(value.numerator).bit_length() + value.denominator.bit_length()


def variable_and_units(k):
    a = Fraction(k, 4)
    variable = (a, 1 + a, -a, -a, -1 / a, 1 / a - 1)
    # Ten unit ±1 coefficients accompany the six variable ones in address_word.
    units = (Fraction(1), Fraction(-1)) * 5
    return variable + units


def T_max_height(k):
    return max(bits(c) for c in variable_and_units(k))


def T_packing(k):
    coeffs = variable_and_units(k)
    dens = [c.denominator for c in coeffs]
    L = dens[0]
    for d in dens[1:]:
        L = lcm(L, d)
    charge = L.bit_length()
    for c in coeffs:
        charge += (abs(c.numerator) * (L // c.denominator)).bit_length()
    return charge


def T_odd_core(k):
    s = 0
    for c in variable_and_units(k):
        p = abs(c.numerator)
        q = c.denominator
        while p % 2 == 0 and p > 0:
            p //= 2
        while q % 2 == 0:
            q //= 2
        s += (0 if p == 0 else p.bit_length()) + q.bit_length()
    return s


def T_fused(Tw, j, q):
    a = q * (1 << j)
    # Signed fused powers (-a, 2a, -a); max-height is sign-sensitive.
    return 2 * Tw(-a) + Tw(2 * a)


def main():
    tariffs = (
        ("max_height", T_max_height),
        ("packing", T_packing),
        ("odd_core", T_odd_core),
    )
    need(T_max_height(1) == 6 and T_max_height(-1) == 5, "mh ±1")
    need(T_max_height(4) == 3 and T_max_height(32) != T_max_height(-32),
         "mh sign-sensitive")
    need(T_packing(1) == 48 and T_packing(4) == 17, "pk spots")
    need(T_odd_core(1) == 35 and T_odd_core(4) == 31, "oc spots")

    beats = 0
    exceeds = 0
    for _, Tw in tariffs:
        for j in range(0, J_MAX + 1):
            dy = T_fused(Tw, j, 1)
            for q in ODD:
                bill = T_fused(Tw, j, q)
                if bill < dy:
                    beats += 1
                elif bill == dy:
                    need(False, f"unexpected fused tie q={q} j={j}")
                else:
                    exceeds += 1
    need(beats == 0, "zero fused beats")
    need(exceeds == 3 * 165, "3*165 fused exceeds")

    import runpy

    tariff = runpy.run_path(str(HERE / "tariff.py"))
    mapping = {
        "max_height": "ADDRESS_affine_coeff_max_height",
        "packing": "ADDRESS_affine_coeff_shared_den_packing",
        "odd_core": "ADDRESS_affine_coeff_odd_core_bit_sum",
    }
    for local_name, Tw in tariffs:
        remote = tariff["T_WORD"][mapping[local_name]]
        for j in (0, 2, 8, 16, 32):
            for q in (1, 3, 15):
                need(T_fused(Tw, j, q) == tariff["T_fused"](remote, j, q),
                     "match tariff module")
    print(MARKER)


if __name__ == "__main__":
    main()
