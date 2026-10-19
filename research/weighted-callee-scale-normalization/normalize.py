"""Scale-normalization of the pinned failing weighted callee P_(2,1).

On G=(Z/3Z)^2 the proposed weighted reversal P_a with a=(2,1) satisfies
P^2 = 2 I != I, so Theorem 1 of weighted-wrapper-contract rejects every
two-call ordinary wrapper using F_a. Left-diagonal post-scales
T=diag(1,2) give P' = T P with (P')^2 = I; post-composing each F_a call
by those two coordinate multiplies realizes F_{P'} and admits the wrapper.

Bill (exact, algebraic address volume V = |G| = 9 per bank coordinate
sweep counted as V modular multiplies per scaled coordinate):

  scales_per_F = 2 V     (H'[1] *= 2 and D'[0] *= 2)
  scales_two_F = 4 V     (both wrapper calls)
  no input restore       (scales act on callee outputs only)

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from itertools import product

MODULUS = 3
DIMENSION = 2
WEIGHTS = (2, 1)  # proposed failing callee
SCALE_T = (1, 2)  # left diagonal T; P' = T P
SCALE_FACTOR = 2  # the only non-unit entry of T
V = MODULUS**DIMENSION  # 9
SCALES_PER_F = 2 * V  # 18
SCALES_TWO_F = 2 * SCALES_PER_F  # 36
RAW_AGREEMENTS = 9  # formula (5): M^n * prod gcd(M, a_i a_{n-1-i}-1)
RAW_FAILURES = V * V - RAW_AGREEMENTS  # 72
KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def vectors(modulus=MODULUS, dimension=DIMENSION):
    return tuple(product(range(modulus), repeat=dimension))


def apply_P(x, weights=WEIGHTS, modulus=MODULUS):
    """Weighted reversal (P x)_i = a_i x_{n-1-i}."""
    n = len(weights)
    need(len(x) == n, "dimension")
    return tuple(weights[i] * x[n - 1 - i] % modulus for i in range(n))


def apply_P_inv(y, weights=WEIGHTS, modulus=MODULUS):
    """Inverse weighted reversal: solve P x = y."""
    n = len(weights)
    x = [0] * n
    for i in range(n):
        # weights[i] * x[n-1-i] = y[i]  =>  x[n-1-i] = weights[i]^{-1} y[i]
        inv = pow(weights[i], -1, modulus)
        x[n - 1 - i] = inv * y[i] % modulus
    return tuple(x)


def apply_T(x, scale=SCALE_T, modulus=MODULUS):
    return tuple(scale[i] * x[i] % modulus for i in range(len(x)))


def apply_P_prime(x, modulus=MODULUS):
    """P' = T P."""
    return apply_T(apply_P(x, modulus=modulus), modulus=modulus)


def F_a(h, d, modulus=MODULUS):
    """Unnormalized callee: (P D, P^{-1} H)."""
    return apply_P(d, modulus=modulus), apply_P_inv(h, modulus=modulus)


def normalize_out(h, d, modulus=MODULUS):
    """Post-scales realizing F_{P'} from F_a output: H'[1]*=2, D'[0]*=2."""
    need(len(h) == DIMENSION and len(d) == DIMENSION, "banks")
    h2 = list(h)
    d2 = list(d)
    h2[1] = (h2[1] * SCALE_FACTOR) % modulus
    d2[0] = (d2[0] * SCALE_FACTOR) % modulus
    return tuple(h2), tuple(d2)


def F_normalized(h, d, modulus=MODULUS):
    """Norm o F_a = F_{P'}."""
    return normalize_out(*F_a(h, d, modulus=modulus), modulus=modulus)


def F_prime(h, d, modulus=MODULUS):
    """Direct F_{P'} with (P')^{-1} = P' since (P')^2 = I."""
    return apply_P_prime(d, modulus=modulus), apply_P_prime(h, modulus=modulus)


def wrapper_word(h, d, callee, modulus=MODULUS):
    """Literal D-=H; F; D+=H; F; D=-D; D+=H with a shared callee."""
    d = tuple((di - hi) % modulus for hi, di in zip(h, d))
    h, d = callee(h, d, modulus=modulus)
    d = tuple((di + hi) % modulus for hi, di in zip(h, d))
    h, d = callee(h, d, modulus=modulus)
    d = tuple((-di) % modulus for di in d)
    d = tuple((di + hi) % modulus for hi, di in zip(h, d))
    return h, d


def census(callee, modulus=MODULUS, dimension=DIMENSION):
    """Count agreements with interchange J(H,D)=(D,H)."""
    agrees = 0
    total = 0
    for h in vectors(modulus, dimension):
        for d in vectors(modulus, dimension):
            total += 1
            oh, od = wrapper_word(h, d, callee, modulus=modulus)
            if (oh, od) == (d, h):
                agrees += 1
    return agrees, total


def formula5_agreements(weights=WEIGHTS, modulus=MODULUS, dimension=DIMENSION):
    """Exact agreement count (5) for equal weighted calls Q=P=P_a."""
    from math import gcd, prod

    n = dimension
    return (modulus**n) * prod(
        gcd(modulus, (weights[i] * weights[n - 1 - i] - 1) % modulus)
        for i in range(n)
    )


def bill(volume=V):
    """Exact modular-multiply invoice for two normalized F calls."""
    scales_per_f = 2 * volume
    return {
        "volume_V": volume,
        "scales_per_F": scales_per_f,
        "scales_two_F": 2 * scales_per_f,
        "input_restores": 0,
        "weight_table_rewrites": 0,
        "note": "scales act on callee outputs only; proposed weights stay (2,1)",
    }
