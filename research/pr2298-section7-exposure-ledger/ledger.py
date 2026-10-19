"""Exact §7 nonadjacent CRT + line-exposure chunk-swap ledger.

Research construction / recursive interface; no new kappa.
Prepared by Wentao Li with substantial AI assistance.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
from itertools import product
from typing import Iterable


# Pinned PR2298 / checks.py parameters (selected-conservative-outer).
TAU = Fraction(99830289, 10**8)
EPSILON = Fraction(1, 40)
PUBLISHED_SAVING = Fraction(6618729, 4 * 10**9)
SELECTED_KAPPA = "0.001672660197076918"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def exchange_bound_crt_forward(d: int) -> int:
    """Axis-order reversal: exactly floor(d/2) endpoint exchanges."""
    need(type(d) is int and d >= 1, "d >= 1")
    return d // 2


def exchange_bound_crt_inverse(d: int) -> int:
    """Inverse reversal uses the same floor(d/2) exchanges."""
    return exchange_bound_crt_forward(d)


def exchange_bound_tensor_map(d: int) -> int:
    """Expose/restore each non-innermost axis: exactly 2(d-1)."""
    need(type(d) is int and d >= 1, "d >= 1")
    return 2 * max(d - 1, 0)


def composite_exchange_multiplier(d: int) -> int:
    """M(d) = CRT forward + CRT inverse + one tensor map."""
    return (
        exchange_bound_crt_forward(d)
        + exchange_bound_crt_inverse(d)
        + exchange_bound_tensor_map(d)
    )


def m_upper_linear(d: int) -> int:
    """Uniform linear majorant: M(d) <= 3d - 2 for every d >= 1."""
    return 3 * d - 2


def section7_exponent() -> Fraction:
    """Published nonadjacent-exposure exponent tau + epsilon*(1-tau)."""
    return TAU + EPSILON * (1 - TAU)


def section7_saving() -> Fraction:
    """1 - exponent = (1-tau)*(1-epsilon)."""
    return (1 - TAU) * (1 - EPSILON)


def pair_primitives(wi: int, wj: int, ell: int) -> tuple[str, ...]:
    """Elementary unequal/equal pair schedule from PR2298 §3 / Colkitt audit."""
    need(abs(wi - wj) <= 1, f"adjacent widths only: {wi},{wj}")
    need(max(wi, wj) <= ell, "widths bounded by ell")
    if wi == wj:
        return ("interchange",)
    if wi == wj + 1:
        return ("interchange", "bit_move")
    return ("bit_move", "interchange")


def apply_exchange(widths: list[int], i: int, j: int, ell: int) -> list[tuple]:
    need(0 <= i < j < len(widths), "exchange indices")
    kinds = pair_primitives(widths[i], widths[j], ell)
    ops = [(kind, i, j, widths[i], widths[j]) for kind in kinds]
    widths[i], widths[j] = widths[j], widths[i]
    return ops


def reversal_ops(widths: list[int], ell: int) -> list[tuple]:
    live = list(widths)
    ops: list[tuple] = []
    d = len(live)
    for k in range(d // 2):
        ops.extend(apply_exchange(live, k, d - 1 - k, ell))
    need(live == list(reversed(widths)), "reversal restores reversed widths")
    return ops


def tensor_ops(widths: list[int], ell: int) -> list[tuple]:
    live = list(widths)
    ops: list[tuple] = []
    d = len(live)
    for i in range(d - 1):
        ops.extend(apply_exchange(live, i, d - 1, ell))
        ops.extend(apply_exchange(live, i, d - 1, ell))
    need(live == list(widths), "tensor map restores widths")
    return ops


def composite_ops(widths: list[int], ell: int) -> dict:
    """CRT forward reversal + inverse reversal + one tensor map."""
    d = len(widths)
    forward = reversal_ops(widths, ell)
    # Inverse reversal on the reversed list equals reversing again.
    inverse = reversal_ops(list(reversed(widths)), ell)
    tensor = tensor_ops(widths, ell)
    ops = forward + inverse + tensor
    exchanges = d // 2 + d // 2 + 2 * max(d - 1, 0)
    interchanges = sum(1 for op in ops if op[0] == "interchange")
    bit_moves = sum(1 for op in ops if op[0] == "bit_move")
    need(exchanges == composite_exchange_multiplier(d), "exchange multiplier")
    need(interchanges + bit_moves == len(ops), "op partition")
    # Each exchange emits 1 interchange; unequal adds exactly one bit_move.
    need(interchanges == exchanges, "one interchange per exchange")
    return {
        "d": d,
        "widths": list(widths),
        "ell": ell,
        "exchanges": exchanges,
        "interchanges": interchanges,
        "bit_moves": bit_moves,
        "bound_M": composite_exchange_multiplier(d),
        "forward_ops": len(forward),
        "inverse_ops": len(inverse),
        "tensor_ops": len(tensor),
        "ops": [list(op) for op in ops],
    }


def mixed_patterns(d: int, short: int, long: int) -> Iterable[tuple[int, ...]]:
    need(long == short + 1, "adjacent r/2 and r")
    for bits in product((short, long), repeat=d):
        yield bits


def unit_cost_bound(ell: int, tau: Fraction = TAU) -> tuple[Decimal, Decimal]:
    """Return (1, ell^tau) as high-precision Decimals for numerical ledger rows."""
    getcontext().prec = 80
    one = Decimal(1)
    # ell^tau = exp(tau * ln(ell)) with Decimal transcendental evaluation.
    ell_tau = (
        Decimal(ell).ln() * Decimal(tau.numerator) / Decimal(tau.denominator)
    ).exp()
    return one, ell_tau


def pattern_unit_charge(row: dict, ell: int, tau: Fraction = TAU) -> Decimal:
    """Charge each interchange <= ell^tau and each bit_move = 1 (lem:chunk-swap)."""
    _one, ell_tau = unit_cost_bound(ell, tau)
    # Interchanges on width w <= ell cost at most ell^tau; bit moves cost 1.
    return Decimal(row["interchanges"]) * ell_tau + Decimal(row["bit_moves"])


def coarse_unit_charge(d: int, ell: int, tau: Fraction = TAU) -> Decimal:
    """M(d) * (1 + ell^tau) coarse majorant used by the §7 O-notation."""
    _one, ell_tau = unit_cost_bound(ell, tau)
    return Decimal(composite_exchange_multiplier(d)) * (Decimal(1) + ell_tau)


def linear_unit_charge(d: int, ell: int, tau: Fraction = TAU) -> Decimal:
    """(3d-2) * (1 + ell^tau) published O(V d (1+ell^tau)) explicit constant."""
    _one, ell_tau = unit_cost_bound(ell, tau)
    return Decimal(m_upper_linear(d)) * (Decimal(1) + ell_tau)


def census(max_d: int = 8, short: int = 3, long: int = 4) -> dict:
    """Finite mixed-width ledger census; ell := long."""
    ell = long
    rows = []
    for d in range(1, max_d + 1):
        for widths in mixed_patterns(d, short, long):
            row = composite_ops(list(widths), ell)
            charge = pattern_unit_charge(row, ell)
            coarse = coarse_unit_charge(d, ell)
            linear = linear_unit_charge(d, ell)
            need(charge <= coarse, f"pattern exceeds coarse bound: {widths}")
            need(coarse <= linear, f"coarse exceeds linear: d={d}")
            need(row["exchanges"] <= m_upper_linear(d), "M(d) <= 3d-2")
            rows.append(
                {
                    **{k: row[k] for k in (
                        "d", "widths", "ell", "exchanges", "interchanges",
                        "bit_moves", "bound_M", "forward_ops", "inverse_ops",
                        "tensor_ops",
                    )},
                    "pattern_charge": str(charge),
                    "coarse_charge": str(coarse),
                    "linear_charge": str(linear),
                }
            )
    pattern_count = sum(2**d for d in range(1, max_d + 1))
    need(len(rows) == pattern_count, "census size")
    # Closed forms on every d.
    multipliers = {
        str(d): {
            "crt_forward": exchange_bound_crt_forward(d),
            "crt_inverse": exchange_bound_crt_inverse(d),
            "tensor": exchange_bound_tensor_map(d),
            "M": composite_exchange_multiplier(d),
            "linear_majorant": m_upper_linear(d),
        }
        for d in range(1, max_d + 1)
    }
    need(all(
        multipliers[str(d)]["M"] <= multipliers[str(d)]["linear_majorant"]
        for d in range(1, max_d + 1)
    ), "linear majorant")
    # Even d attains M = 3d-2.
    need(all(
        composite_exchange_multiplier(d) == m_upper_linear(d)
        for d in range(2, max_d + 1, 2)
    ), "even-d sharpness")
    # Per-d numerical ledger: worst pattern charge vs coarse/linear majorants.
    per_d = {}
    for d in range(1, max_d + 1):
        d_rows = [r for r in rows if r["d"] == d]
        worst = max(d_rows, key=lambda r: (Fraction(r["pattern_charge"]), r["bit_moves"]))
        per_d[str(d)] = {
            "M": multipliers[str(d)]["M"],
            "linear_majorant": multipliers[str(d)]["linear_majorant"],
            "worst_widths": worst["widths"],
            "worst_bit_moves": worst["bit_moves"],
            "worst_pattern_charge": worst["pattern_charge"],
            "coarse_charge": worst["coarse_charge"],
            "linear_charge": worst["linear_charge"],
        }
    return {
        "max_d": max_d,
        "short_width": short,
        "long_width": long,
        "ell": ell,
        "pattern_count": len(rows),
        "multipliers": multipliers,
        "per_d_ledger": per_d,
        "tau": str(TAU),
        "epsilon": str(EPSILON),
        "section7_exponent": str(section7_exponent()),
        "section7_saving": str(section7_saving()),
        "published_saving": str(PUBLISHED_SAVING),
        "saving_matches_published": section7_saving() == PUBLISHED_SAVING,
        "rows": rows,
    }


def asymptotic_constant() -> dict:
    """Explicit constant replacing the O(d) factor in O(V d (1+ell^tau)).

    With M(d) <= 3d-2 <= 3d and ell <= p/(3d) (PR2298 §3 domain),
        M(d)(1+ell^tau) <= 3d + 3d*(p/(3d))^tau
                        = 3d + 3^{1-tau} d^{1-tau} p^tau.
    Under d <= p^epsilon the second term is <= 3^{1-tau} p^{tau+epsilon(1-tau)}.
    """
    getcontext().prec = 80
    three = Decimal(3)
    const = three ** (Decimal(1) - Decimal(TAU.numerator) / Decimal(TAU.denominator))
    return {
        "linear_factor": 3,
        "ell_tau_prefactor": str(const),
        "domain": "ell <= p/(3d), d <= p^epsilon (PR2298 §3 / checks.py)",
        "target_exponent": str(section7_exponent()),
    }
