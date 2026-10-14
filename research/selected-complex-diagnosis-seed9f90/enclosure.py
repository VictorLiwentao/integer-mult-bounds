#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact rational enclosures for ln and exp, code-disjoint from complex-local-word-ceiling.

Method (distinct from the atanh-successor chains in research/complex-local-word-ceiling/ceiling.py):

* ln 2 from the alternating binary series with an explicit geometric remainder.
* For integer n >= 1 write n = 2^v * m with odd m (or m = 1), so
  ln n = v ln 2 + ln m.
* For odd m >= 3 reduce by the algebraic identity
  ln m = ln((m+1)/2) + ln(2m/(m+1)), each argument closer to 1, until the
  residual lies in (1, 2]; then set x = residual - 1 in (0, 1] and apply the
  Mercator series ln(1+x) = sum_{k>=1} (-1)^{k+1} x^k / k with a Lagrange-style
  alternating remainder bound.

* exp on [0, 1/2] by the Taylor series with a positive Lagrange remainder bound.

All arithmetic is exact Fraction outward rounding to 2^-PREC. Standard library
only. Independent of ceiling.py / levers.py.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from math import isqrt

PREC = 256
UNIT = Q(1, 1 << PREC)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def down(x: Q) -> Q:
    return Q((x.numerator << PREC) // x.denominator, 1 << PREC)


def up(x: Q) -> Q:
    return -down(-x)


@lru_cache(None)
def ln2() -> tuple[Q, Q]:
    """Enclosure of ln 2 = sum_{k>=1} 1/(k 2^k)."""
    s = Q(0)
    k = 0
    while True:
        k += 1
        term = Q(1, k * (1 << k))
        s += term
        # Tail sum_{j>k} 1/(j 2^j) < 1/((k+1) 2^{k+1}) * sum_{i>=0} 2^{-i}
        #            = 1/((k+1) 2^k).
        tail = Q(1, (k + 1) * (1 << k))
        if tail < UNIT / 16:
            return down(s), up(s + tail)


@lru_cache(None)
def ln1p(x: Q) -> tuple[Q, Q]:
    """Enclosure of ln(1+x) for 0 <= x <= 1 via Mercator with alternating remainder."""
    require(0 <= x <= 1, "ln1p domain")
    if x == 0:
        return Q(0), Q(0)
    s = Q(0)
    term = x
    k = 1
    while True:
        signed = term / k if k % 2 == 1 else -term / k
        s += signed
        term *= x
        k += 1
        # Next term magnitude is term/k; alternating remainder <= that magnitude.
        rem = abs(term / k)
        if rem < UNIT / 16:
            lo = s if k % 2 == 1 else s - rem  # next sign is + when k odd
            hi = s + rem if k % 2 == 1 else s
            # More carefully: after adding term k-1, remainder has sign of term k
            # and magnitude <= |term_k|.
            if (k % 2) == 1:
                # next contribution positive
                return down(s), up(s + rem)
            return down(s - rem), up(s)


@lru_cache(None)
def ln_odd(m: int) -> tuple[Q, Q]:
    """Enclosure of ln m for odd positive integer m."""
    require(isinstance(m, int) and m >= 1 and m % 2 == 1, "odd")
    if m == 1:
        return Q(0), Q(0)
    # Peel: ln m = ln((m+1)/2) + ln(2m/(m+1)).
    # (m+1)/2 is an integer (m odd); 2m/(m+1) = 1 + (m-1)/(m+1) with
    # 0 < (m-1)/(m+1) < 1.
    half = (m + 1) // 2
    a_lo, a_hi = ln_int(half)
    x = Q(m - 1, m + 1)
    b_lo, b_hi = ln1p(x)
    return down(a_lo + b_lo), up(a_hi + b_hi)


@lru_cache(None)
def ln_int(n: int) -> tuple[Q, Q]:
    """Enclosure of ln n for integer n >= 1."""
    require(isinstance(n, int) and n >= 1, "ln domain")
    if n == 1:
        return Q(0), Q(0)
    v = 0
    m = n
    while m % 2 == 0:
        m //= 2
        v += 1
    lo2, hi2 = ln2()
    lo_m, hi_m = ln_odd(m)
    return down(v * lo2 + lo_m), up(v * hi2 + hi_m)


def exp_unit(y: Q, upper: bool) -> Q:
    """One-sided enclosure of exp(y) for 0 <= y <= 1/2."""
    require(0 <= y <= Q(1, 2), "exp range")
    s = Q(1)
    t = Q(1)
    k = 0
    while True:
        k += 1
        t = t * y / k
        s += t
        # Remainder after degree k is < t * y / (k+1) * exp(y) / (1 - y/(k+2)) loosely;
        # for y <= 1/2 and k large, 2 t y /(k+1) dominates the Taylor remainder.
        if t * y < UNIT / 16:
            if upper:
                return up(s + 2 * t * y / (k + 1))
            return down(s)


def exp_encl(lo: Q, hi: Q) -> tuple[Q, Q]:
    """Enclosure of exp on 0 <= lo <= hi. Reduces by halves into [0, 1/2]."""
    require(0 <= lo <= hi, "exp interval order")
    if hi <= Q(1, 2):
        return exp_unit(lo, False), exp_unit(hi, True)
    # exp(y) = exp(y/2)^2
    a_lo, a_hi = exp_encl(lo / 2, hi / 2)
    return down(a_lo * a_lo), up(a_hi * a_hi)


def child_cost(r: int, m: int, a: Q) -> tuple[Q, Q]:
    """Enclosure of (r/m)^(1-a) = (r/m) exp(a ln(m/r))."""
    require(1 <= r < m and a >= 0, "child_cost domain")
    lm_lo, lm_hi = ln_int(m)
    lr_lo, lr_hi = ln_int(r)
    # ln(m/r) in [lm_lo - lr_hi, lm_hi - lr_lo]
    d_lo = lm_lo - lr_hi
    d_hi = lm_hi - lr_lo
    require(d_lo >= 0, "ln(m/r) negativity")
    e_lo, e_hi = exp_encl(max(Q(0), a * d_lo), a * d_hi)
    return down(Q(r, m) * e_lo), up(Q(r, m) * e_hi)


def max_idle_rank(m: int) -> int:
    R = isqrt((m * m - 1) // 2)
    while 2 * (R + 1) ** 2 < m * m:
        R += 1
    while 2 * R * R >= m * m:
        R -= 1
    return R


def model(local: dict, m: int, families: int, stages: int, centre: int, unpaid: int = 1, R: int | None = None):
    R = max_idle_rank(m) if R is None else R
    require(2 * R * R < m * m, "idle rank cap violates the halving guard")
    require(all(0 < r < m for r in local) and all(n >= 0 for n in local.values()), "local profile")
    require(1 <= unpaid < m, "unpaid")
    w = Q(families, stages)
    total = (m - unpaid) * w + centre
    local_mass = sum(r * Q(n) for r, n in local.items())
    idle = total - local_mass
    require(idle >= 0, "local word pays more mass than the coverage law allows")
    return {
        "R": R,
        "w": w,
        "total_mass": total,
        "local_mass": local_mass,
        "idle_mass": idle,
        "deficit": unpaid * w - centre,
    }


def relax(local, m, families, stages, centre, a, unpaid=1, R=None):
    q = model(local, m, families, stages, centre, unpaid=unpaid, R=R)
    lo = hi = Q(0)
    for r, n in local.items():
        c = child_cost(int(r), m, a)
        lo += Q(n) * c[0]
        hi += Q(n) * c[1]
    c = child_cost(q["R"], m, a)
    k = q["idle_mass"] / q["R"]
    lo += k * c[0]
    hi += k * c[1]
    return down(lo / q["w"]), up(hi / q["w"])


def ceiling(local, m, families, stages, centre, grid=Q(1, 10**12), unpaid=1, R=None):
    lo, hi = Q(0), Q(1, 20)
    require(relax(local, m, families, stages, centre, hi, unpaid=unpaid, R=R)[0] > 1, "search window too small")
    require(relax(local, m, families, stages, centre, lo, unpaid=unpaid, R=R)[1] < 1, "no positive saving")
    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        if mid <= lo:
            mid = lo + grid
        v = relax(local, m, families, stages, centre, mid, unpaid=unpaid, R=R)
        if v[1] < 1:
            lo = mid
        elif v[0] > 1:
            hi = mid
        else:
            raise ValueError("enclosure too wide to separate the grid point")
    return lo, hi
