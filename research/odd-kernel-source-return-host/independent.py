#!/usr/bin/env python3
"""Independent replay of the source-return host-bill lemma (no verify import).

Rebuilds H_fused from closed-form T_word and admitted-screen counts; checks
I=0 zero beats, critical I*=14/17, and the unique I=1 beat at (q=3,j=0).
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = (
    "PASS_ODD_KERNEL_SOURCE_RETURN_HOST_INDEPENDENT "
    "I0_beats=0 I1_beats=1 critical_I=14/17 first_beat=(3,0) no_new_kappa"
)
ODD = (3, 5, 7, 9, 15)
J_MAX = 32
SCREEN = tuple(m for m in range(3, 100) if m % 2 == 1)
C, X, D, R_SR = 100, 40, 5, 30
FUSED_FIXED = 3 * C + 2 * X + 18 * D + R_SR


def need(ok, message):
    if not ok:
        raise ValueError(message)


def bits(value):
    value = Fraction(value)
    return abs(value.numerator).bit_length() + value.denominator.bit_length()


def T_word(k):
    a = Fraction(k, 4)
    variable = (a, 1 + a, -a, -a, -1 / a, 1 / a - 1)
    return 20 + sum(bits(c) for c in variable)


def T_fused(j, q):
    a = q * (1 << j)
    return 2 * T_word(a) + T_word(2 * a)


def A(q):
    return sum(1 for m in SCREEN if gcd(m, q) == 1)


def H_fused(j, q, I):
    return FUSED_FIXED + T_fused(j, q) + I * A(q)


def main():
    need(FUSED_FIXED == 500, "fused fixed")
    need(len(SCREEN) == 49 and A(1) == 49 and A(3) == 32, "screen admissions")
    need(T_word(4) == 32 and T_word(2) == 38 and T_word(1) == 45, "T_word spots")

    beats0 = 0
    for j in range(0, J_MAX + 1):
        dy = H_fused(j, 1, 0)
        for q in ODD:
            need(H_fused(j, q, 0) > dy, f"I=0 q={q} j={j}")
            beats0 += 0
    need(beats0 == 0, "I=0 zero beats")

    dT = T_fused(0, 3) - T_fused(0, 1)
    dA = A(1) - A(3)
    need(dT == 14 and dA == 17, "critical ingredients")
    need(Fraction(dT, dA) == Fraction(14, 17), "critical I*")

    beats1 = []
    for j in range(0, J_MAX + 1):
        dy = H_fused(j, 1, 1)
        for q in ODD:
            bill = H_fused(j, q, 1)
            if bill < dy:
                beats1.append((q, j, bill, dy))
    need(beats1 == [(3, 0, 674, 677)], "unique I=1 beat")

    import runpy
    bill = runpy.run_path(str(HERE / "host_bill.py"))
    for j in (0, 2, 8, 16, 32):
        for q in (1, 3, 15):
            need(H_fused(j, q, 1) == bill["H_fused"](j, q, 1), "match host_bill")
            need(H_fused(j, q, 0) == bill["H_fused"](j, q, 0), "match I=0")

    print(MARKER)


if __name__ == "__main__":
    main()
