"""Exact PR2298 §3 exchange schedules for mixed gap-g (non-adjacent) axis widths.

Research construction / recursive interface; no new kappa.
Prepared by Wentao Li with substantial AI assistance.

Extends the adjacent (|Δw|≤1) elementary schedule of PR2298 §3 / #4075 to
arbitrary gap g = |w_i − w_j| ≥ 0 by the multi-bit normal form:

  equal:            1 interchange
  long-first (g>0): 1 interchange + g bit_moves
  long-last  (g>0): g bit_moves + 1 interchange

Physical (swap|move) streams are checked against physical.move_address.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable


def need(ok, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


@dataclass(frozen=True)
class Op:
    """One completed equal-width interchange or one elementary bit move."""

    kind: str  # "interchange" or "bit_move"
    i: int
    j: int
    width_i: int
    width_j: int

    def as_list(self):
        return [self.kind, self.i, self.j, self.width_i, self.width_j]


def gap(wi: int, wj: int) -> int:
    return abs(wi - wj)


def _plan_pair(wi: int, wj: int) -> list[str]:
    """Primitive sequence for exchanging axes of bit-widths wi, wj (any gap).

    Matches PR2298 PROOF §3 / #4075 when |wi−wj|≤1, and extends by repeating
    the elementary bit-move for each excess bit when |wi−wj|≥2.
    """
    need(wi > 0 and wj > 0, f"positive widths required: {wi},{wj}")
    g = gap(wi, wj)
    if g == 0:
        return ["interchange"]
    if wi > wj:
        # long field first: interchange common width, then g excess bit moves
        return ["interchange"] + ["bit_move"] * g
    # long field last: g bit moves, then interchange
    return ["bit_move"] * g + ["interchange"]


def pair_invoice(wi: int, wj: int) -> dict:
    """Closed-form primitive invoice for one exchange of widths wi, wj."""
    kinds = _plan_pair(wi, wj)
    g = gap(wi, wj)
    inter = sum(1 for k in kinds if k == "interchange")
    bits = sum(1 for k in kinds if k == "bit_move")
    need(inter == 1, "exactly one interchange per exchange")
    need(bits == g, f"exactly g={g} bit_moves per exchange")
    return {
        "wi": wi,
        "wj": wj,
        "gap": g,
        "interchanges": inter,
        "bit_moves": bits,
        "kinds": kinds,
    }


def exchange_ops(widths: list[int], i: int, j: int) -> list[Op]:
    """Emit the primitive ops that exchange positions i and j."""
    need(0 <= i < j < len(widths), f"bad exchange indices {i},{j}")
    wi, wj = widths[i], widths[j]
    kinds = _plan_pair(wi, wj)
    return [Op(kind, i, j, wi, wj) for kind in kinds]


def apply_exchange(widths: list[int], i: int, j: int) -> list[Op]:
    ops = exchange_ops(widths, i, j)
    widths[i], widths[j] = widths[j], widths[i]
    return ops


def reversal_schedule(widths: list[int]) -> dict:
    """Reverse axis order by nonadjacent endpoint exchanges."""
    d = len(widths)
    live = list(widths)
    ops: list[Op] = []
    exchanges = 0
    for k in range(d // 2):
        ops.extend(apply_exchange(live, k, d - 1 - k))
        exchanges += 1
    need(live == list(reversed(widths)), "reversal must invert axis order")
    return {
        "kind": "reversal",
        "d": d,
        "widths_in": list(widths),
        "widths_out": live,
        "exchanges": exchanges,
        "bound_exchanges": d // 2,
        "interchanges": sum(1 for op in ops if op.kind == "interchange"),
        "bit_moves": sum(1 for op in ops if op.kind == "bit_move"),
        "ops": [op.as_list() for op in ops],
    }


def tensor_map_schedule(widths: list[int]) -> dict:
    """Expose each non-innermost axis, then restore: exactly 2(d−1) exchanges."""
    d = len(widths)
    live = list(widths)
    ops: list[Op] = []
    exchanges = 0
    for i in range(d - 1):
        ops.extend(apply_exchange(live, i, d - 1))
        exchanges += 1
        ops.extend(apply_exchange(live, i, d - 1))
        exchanges += 1
    need(live == list(widths), "tensor map must restore widths")
    return {
        "kind": "tensor_map",
        "d": d,
        "widths_in": list(widths),
        "widths_out": live,
        "exchanges": exchanges,
        "bound_exchanges": 2 * max(d - 1, 0),
        "interchanges": sum(1 for op in ops if op.kind == "interchange"),
        "bit_moves": sum(1 for op in ops if op.kind == "bit_move"),
        "ops": [op.as_list() for op in ops],
    }


def _check_pair_invoice(ops: list) -> None:
    """Group ops into per-exchange invoices of 1 + g primitives."""
    i = 0
    while i < len(ops):
        kind, a, b, wi, wj = ops[i]
        g = gap(wi, wj)
        need(i + g < len(ops) or g == 0, "gap invoice truncated")
        block = ops[i : i + 1 + g]
        need(len(block) == 1 + g, "invoice length")
        for op in block:
            need(op[1:5] == [a, b, wi, wj], "paired primitives share endpoints")
        kinds = [op[0] for op in block]
        need(kinds.count("interchange") == 1, "one interchange")
        need(kinds.count("bit_move") == g, "g bit_moves")
        if wi > wj:
            need(kinds == ["interchange"] + ["bit_move"] * g, "long-first order")
        elif wi < wj:
            need(kinds == ["bit_move"] * g + ["interchange"], "long-last order")
        else:
            need(kinds == ["interchange"], "equal order")
        i += 1 + g


def gap_unit_cases(short: int = 3, long: int = 5) -> list[dict]:
    """Unit checks of equal / gap-g pair invoices at a single pair."""
    need(long > short, "long must exceed short")
    g = long - short
    cases = []
    for wi, wj, label in (
        (long, short, "long_first"),
        (short, long, "long_last"),
        (short, short, "equal_short"),
        (long, long, "equal_long"),
    ):
        inv = pair_invoice(wi, wj)
        cases.append(
            {
                "label": label,
                "widths": [wi, wj],
                "gap": inv["gap"],
                "ops": [[k, 0, 1, wi, wj] for k in inv["kinds"]],
                "interchanges": inv["interchanges"],
                "bit_moves": inv["bit_moves"],
            }
        )
    need(cases[0]["bit_moves"] == g and cases[1]["bit_moves"] == g, "gap unit")
    need(cases[2]["bit_moves"] == 0 and cases[3]["bit_moves"] == 0, "equal unit")
    return cases


def mixed_width_patterns(d: int, short: int, long: int) -> Iterable[tuple[int, ...]]:
    """All 2^d patterns of bit-widths {short, long} for axis count d."""
    need(long > short, "need a positive width gap")
    for bits in product((short, long), repeat=d):
        yield bits


def census(max_d: int = 6, short: int = 3, long: int = 5) -> dict:
    """Exact schedule census for every mixed gap-(long-short) pattern at d=1..max_d."""
    g0 = long - short
    need(g0 >= 2, "this package targets non-adjacent gaps (|Δw|≥2)")
    rows = []
    max_rev_ex = 0
    max_tensor_ex = 0
    for d in range(1, max_d + 1):
        for widths in mixed_width_patterns(d, short, long):
            rev = reversal_schedule(list(widths))
            ten = tensor_map_schedule(list(widths))
            need(rev["exchanges"] == rev["bound_exchanges"], "reversal exchange exact")
            need(ten["exchanges"] == ten["bound_exchanges"], "tensor exchange exact")
            _check_pair_invoice(rev["ops"])
            _check_pair_invoice(ten["ops"])
            # Bit-move total equals sum of per-exchange gaps.
            rev_gap_sum = sum(
                gap(widths[k], widths[d - 1 - k]) for k in range(d // 2)
            )
            need(rev["bit_moves"] == rev_gap_sum, "reversal bit_moves = gap sum")
            need(rev["interchanges"] == rev["exchanges"], "one interchange / exchange")
            need(ten["interchanges"] == ten["exchanges"], "tensor interchange count")
            max_rev_ex = max(max_rev_ex, rev["exchanges"])
            max_tensor_ex = max(max_tensor_ex, ten["exchanges"])
            rows.append(
                {
                    "d": d,
                    "widths": list(widths),
                    "reversal_exchanges": rev["exchanges"],
                    "reversal_bound": rev["bound_exchanges"],
                    "reversal_interchanges": rev["interchanges"],
                    "reversal_bit_moves": rev["bit_moves"],
                    "tensor_exchanges": ten["exchanges"],
                    "tensor_bound": ten["bound_exchanges"],
                    "tensor_interchanges": ten["interchanges"],
                    "tensor_bit_moves": ten["bit_moves"],
                    "reversal_ops": rev["ops"],
                    "tensor_ops": ten["ops"],
                }
            )
    unit = gap_unit_cases(short, long)
    pattern_count = sum(2**d for d in range(1, max_d + 1))
    need(len(rows) == pattern_count, "pattern census size")
    return {
        "max_d": max_d,
        "short_width": short,
        "long_width": long,
        "gap": g0,
        "pattern_count": len(rows),
        "max_reversal_exchanges": max_rev_ex,
        "max_tensor_exchanges": max_tensor_ex,
        "unit_gap_pairs": unit,
        "rows": rows,
        "bounds": {
            "reversal_exchanges": "floor(d/2)",
            "tensor_exchanges": "2(d-1)",
            "gap_g_pair": "1 interchange + g bit_moves",
            "equal_pair": "1 interchange",
        },
        "all_reversals_exact": all(
            r["reversal_exchanges"] == r["reversal_bound"] for r in rows
        ),
        "all_tensors_exact": all(
            r["tensor_exchanges"] == r["tensor_bound"] for r in rows
        ),
    }


def low_level_exchange_ops(
    live: list[int], i: int, j: int
) -> list[tuple[str, int, int, int]]:
    """Emit absolute (swap|move) ops for exchanging fields i < j in live widths.

    Positions are MSB-origin bit indices matching physical.move_address.
    """
    need(0 <= i < j < len(live), "bad indices")
    wi, wj = live[i], live[j]
    left = sum(live[:i])
    right = sum(live[:j])
    g = gap(wi, wj)
    if g == 0:
        return [("swap", left, right, wi)]
    if wi > wj:
        # long first: swap common then move excess bits toward the short slot
        ops: list[tuple[str, int, int, int]] = [
            ("swap", left + g, right, wj)
        ]
        for t in range(g):
            ops.append(("move", left + (g - 1 - t), right - 1 - t, 1))
        return ops
    # long last: inverse of long-first on the swapped width pair (absolute MSB indices)
    ops = []
    for k in range(g):
        ops.append(("move", right + k, left + k, 1))
    ops.append(("swap", right + g, left + g, wi))
    return ops


def physical_reversal_ok(widths: list[int], move_address) -> bool:
    """Apply the gap-g reversal schedule via move_address; check field reversal."""
    d = len(widths)
    total = sum(widths)
    live = list(widths)
    low_ops: list[tuple[str, int, int, int]] = []
    for k in range(d // 2):
        i, j = k, d - 1 - k
        low_ops.extend(low_level_exchange_ops(live, i, j))
        live[i], live[j] = live[j], live[i]
    need(live == list(reversed(widths)), "width track for physical reversal")

    def apply_all(index: int) -> int:
        for op in low_ops:
            index = move_address(index, total, op)
        return index

    def decode(index: int, ws: list[int]) -> list[int]:
        coords = []
        shift = total
        for w in ws:
            shift -= w
            coords.append((index >> shift) & ((1 << w) - 1))
        return coords

    def encode(coords: list[int], ws: list[int]) -> int:
        index = 0
        for c, w in zip(coords, ws):
            index = (index << w) | c
        return index

    if total <= 14:
        space = list(range(1 << total))
    else:
        import random

        rng = random.Random(2298 + d + sum(widths) + 2)  # distinct from adjacent seed
        space = [rng.randrange(1 << total) for _ in range(64)]
        space += [0, (1 << total) - 1]

    for addr in space:
        coords = decode(addr, list(widths))
        expect = encode(list(reversed(coords)), list(reversed(widths)))
        got = apply_all(addr)
        if got != expect:
            return False
    return True
