# SPDX-License-Identifier: Apache-2.0
"""Small exact dirty-input instance with two unpaid coordinates per family.

Scoped replacement identity outside the selected N=9 line-port stock.
Ambient dimension N=4 with d=2 unpaid directions on a two-slot port group.
Paid advances clear the two non-offset coordinates; unpaid directions are never
paid-advanced and remain at their dirty initial values (legal unpaid pair).

No claim is made that this toy lifts to a favorable P112 decoder. It only shows
that a two-unpaid endpoint contract can be exact on dirty inputs once ambient
dimension permits a second unpaid direction.
"""
from __future__ import annotations

from itertools import product


def require(ok: bool, why: str) -> None:
    if not ok:
        raise AssertionError(why)


N = 4
OFFSET = (0, 1)  # unpaid directions
PAID = (2, 3)
SLOTS = 2


def advance_paid(state: list[list[int]], slot: int, coord: int) -> None:
    """Paid self-clear of one (slot, paid-coord) line (one crossing)."""
    require(coord in PAID, "only paid coordinates may be advanced")
    row = state[slot * N + coord]
    for i in range(len(row)):
        row[i] = 0


def endpoint_ok(initial: list[list[int]], final: list[list[int]]) -> bool:
    for slot in range(SLOTS):
        for coord in OFFSET:
            if final[slot * N + coord] != initial[slot * N + coord]:
                return False
        for coord in PAID:
            if any(final[slot * N + coord]):
                return False
    return True


def run_program(initial: list[list[int]]) -> list[list[int]]:
    state = [row[:] for row in initial]
    for slot in range(SLOTS):
        for coord in PAID:
            advance_paid(state, slot, coord)
        # Unpaid coordinates are intentionally never advanced.
    return state


def all_dirty_columns(width: int = 2) -> dict:
    """Exhaustive dirty F2 columns on a small width, plus omission controls."""
    rows = SLOTS * N
    total = 0
    for bits in product([0, 1], repeat=rows * width):
        initial = [list(bits[i * width : (i + 1) * width]) for i in range(rows)]
        final = run_program(initial)
        require(endpoint_ok(initial, final), "endpoint on dirty input")
        # Unpaid rows never change bit-for-bit.
        for slot in range(SLOTS):
            for coord in OFFSET:
                require(
                    final[slot * N + coord] == initial[slot * N + coord],
                    "unpaid frozen",
                )
        total += 1
    # Negative control: clearing an unpaid coordinate breaks preservation.
    initial = [[1] * width for _ in range(rows)]
    state = [row[:] for row in initial]
    for slot in range(SLOTS):
        for coord in PAID:
            advance_paid(state, slot, coord)
        state[slot * N + OFFSET[0]] = [0] * width
    require(not endpoint_ok(initial, state), "clearing unpaid must fail preservation")
    # Negative control: omit one paid clear.
    state = [row[:] for row in initial]
    for slot in range(SLOTS):
        for coord in PAID:
            if slot == 0 and coord == PAID[0]:
                continue
            advance_paid(state, slot, coord)
    require(not endpoint_ok(initial, state), "omission must fail clear")
    return {
        "ambient_N": N,
        "offset_d": len(OFFSET),
        "slots": SLOTS,
        "width": width,
        "exhaustive_columns": total,
        "omission_controls_rejected": 2,
        "unpaid_directions_per_slot": len(OFFSET),
        "lemma_U_upper_bound_v1": 1 * (N - len(OFFSET)),  # v=1
        "status": "PASS_EXACT_TWO_UNPAID_DIRTY_TOY",
    }
