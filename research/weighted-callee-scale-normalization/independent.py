#!/usr/bin/env python3
"""Independent closed-form replay of the scale-normalization invoice.

Does not import normalize.py. Re-derives P', census counts, and 4V bill.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from itertools import product
from math import gcd, prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = (
    "PASS_INDEPENDENT_WEIGHTED_CALLEE_SCALE_NORMALIZATION "
    "raw=9/81 normalized=81/81 scales_two_F=36 no_new_kappa"
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    M, n = 3, 2
    a = (2, 1)
    V = M**n
    vecs = tuple(product(range(M), repeat=n))

    def P(x):
        return tuple(a[i] * x[n - 1 - i] % M for i in range(n))

    def Pinv(y):
        x = [0] * n
        for i in range(n):
            x[n - 1 - i] = pow(a[i], -1, M) * y[i] % M
        return tuple(x)

    def Tp(x):
        # T=diag(1,2); P'=T P
        px = P(x)
        return (px[0] % M, (2 * px[1]) % M)

    # (P')^2 = I
    for v in vecs:
        need(Tp(Tp(v)) == v, "independent (P')^2")

    def Fa(h, d):
        return P(d), Pinv(h)

    def Fn(h, d):
        hh, dd = Fa(h, d)
        return (hh[0], (2 * hh[1]) % M), ((2 * dd[0]) % M, dd[1])

    def word(h, d, callee):
        d = tuple((di - hi) % M for hi, di in zip(h, d))
        h, d = callee(h, d)
        d = tuple((di + hi) % M for hi, di in zip(h, d))
        h, d = callee(h, d)
        d = tuple((-di) % M for di in d)
        d = tuple((di + hi) % M for hi, di in zip(h, d))
        return h, d

    def census(callee):
        ok = sum(
            1
            for h in vecs
            for d in vecs
            if word(h, d, callee) == (d, h)
        )
        return ok, V * V

    raw_ok, raw_total = census(Fa)
    formula = (M**n) * prod(
        gcd(M, (a[i] * a[n - 1 - i] - 1) % M) for i in range(n)
    )
    need(raw_ok == formula == 9, "independent raw")
    need(raw_total == 81, "independent total")

    norm_ok, norm_total = census(Fn)
    need(norm_ok == norm_total == 81, "independent normalized")

    scales_two_F = 4 * V
    need(scales_two_F == 36, "independent bill")

    # Match committed certificate counts without importing normalize.
    import json

    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    need(cert["counts"]["raw_agreements"] == 9, "cert raw")
    need(cert["counts"]["normalized_agreements"] == 81, "cert norm")
    need(cert["counts"]["scales_two_F"] == 36, "cert bill")
    need(cert["kappa"]["changed"] is False, "no new kappa")

    print(MARKER)


if __name__ == "__main__":
    main()
