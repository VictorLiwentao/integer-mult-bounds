#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Four-role A5 conjugate 5-cycle target; need()-based admission."""
from __future__ import annotations

import hashlib
import itertools

ROLES = 4
GROUP_ORDER = 60
EXPECTED_IDEM = 120
EXPECTED_CALLS = 240
NCELL = ROLES * ROLES
KAPPA = "0.001672660197076918"
DIRECT_LEN = 4
SHORT_DEPTH = 3
LAYER_SIZES = (1, 240, 37285, 5150035)
SEEN_AT_DEPTH3 = 5187561

# Generators matching research/a5-conjugate-5cycle-seedd316f8
X_PERM = (1, 0, 3, 2, 4)  # (1 2)(3 4)
Y_PERM = (2, 1, 4, 3, 0)  # (1 3 5)
E_PERM = (0, 1, 2, 3, 4)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL_A5_FOUR_ROLE_CONJUGATE: {message}")


def compose(a, b):
    """Permutation product a∘b, applying b first."""
    return tuple(a[b[i]] for i in range(5))


def even_permutation(p) -> bool:
    inversions = sum(p[i] > p[j] for i in range(5) for j in range(i + 1, 5))
    return inversions % 2 == 0


def build_group_generated():
    """Build A5 by closing {e} under right multiplication by X,Y."""
    seen = {E_PERM}
    frontier = [E_PERM]
    while frontier:
        current = frontier.pop()
        for generator in (X_PERM, Y_PERM):
            successor = compose(current, generator)
            if successor not in seen:
                seen.add(successor)
                frontier.append(successor)
    need(len(seen) == GROUP_ORDER, "generated <X,Y> must be all of A5")
    elements = tuple(sorted(seen))
    index = {g: i for i, g in enumerate(elements)}
    table = tuple(tuple(index[compose(a, b)] for b in elements) for a in elements)
    return elements, index, table


ELEMENTS, GROUP_INDEX, GROUP_MUL = build_group_generated()
E = GROUP_INDEX[E_PERM]
X = GROUP_INDEX[X_PERM]
Y = GROUP_INDEX[Y_PERM]
XY = GROUP_MUL[X][Y]
YX = GROUP_MUL[Y][X]
GENERATOR_IDS = (X, Y)
GENERATOR_NAMES = {X: "x", Y: "y"}


def order_of(element: int) -> int:
    value = E
    for power in range(1, GROUP_ORDER + 1):
        value = GROUP_MUL[value][element]
        if value == E:
            return power
    raise SystemExit("FAIL_A5_FOUR_ROLE_CONJUGATE: element order failed")


need(order_of(X) == 2, "x must have order 2")
need(order_of(Y) == 3, "y must have order 3")
need(order_of(XY) == 5, "xy must have order 5")
need(order_of(YX) == 5, "yx must have order 5")


def rank_one_idempotents():
    """Rank-one idempotents N=u v^T in M4(F2) with v^T u = 1."""
    return tuple(
        (u, v)
        for u in range(1, 1 << ROLES)
        for v in range(1, 1 << ROLES)
        if ((u & v).bit_count() & 1)
    )


IDEMPOTENTS = rank_one_idempotents()
need(len(IDEMPOTENTS) == EXPECTED_IDEM, "expected 120 rank-one idempotents")
CALLS = tuple((g, u, v) for g in GENERATOR_IDS for u, v in IDEMPOTENTS)
need(len(CALLS) == EXPECTED_CALLS, "expected 240 paid factors")
CALL_INDEX = {call: i for i, call in enumerate(CALLS)}


def right_permute_mask(mask: int, g: int) -> int:
    out = 0
    remaining = mask
    while remaining:
        bit = remaining & -remaining
        a = bit.bit_length() - 1
        out ^= 1 << GROUP_MUL[a][g]
        remaining ^= bit
    return out


def identity_state():
    cells = [0] * NCELL
    one = 1 << E
    for i in range(ROLES):
        cells[i * ROLES + i] = one
    return tuple(cells)


def target_state():
    """diag([xy], [yx], [e], [e])."""
    cells = list(identity_state())
    cells[0] = 1 << XY
    cells[ROLES + 1] = 1 << YX
    return tuple(cells)


def step(state, call):
    """Right-multiply a 4x4 F2[A5] matrix by one paid factor D_N(g)."""
    g, u, v = call
    cells = list(state)
    for row in range(ROLES):
        value = 0
        for middle in range(ROLES):
            if (u >> middle) & 1:
                value ^= cells[ROLES * row + middle]
        delta = value ^ right_permute_mask(value, g)
        for col in range(ROLES):
            if (v >> col) & 1:
                cells[ROLES * row + col] ^= delta
    return tuple(cells)


def word_state(word):
    state = identity_state()
    for call in word:
        state = step(state, call)
    return state


def e_ii(i: int):
    u = 1 << i
    v = 1 << i
    return u, v


def make_direct_word():
    """D_E11(x) D_E11(y) D_E22(y) D_E22(x)."""
    e11 = e_ii(0)
    e22 = e_ii(1)
    return (
        (X, e11[0], e11[1]),
        (Y, e11[0], e11[1]),
        (Y, e22[0], e22[1]),
        (X, e22[0], e22[1]),
    )


def convolve(left: int, right: int) -> int:
    out = 0
    a_rem = left
    while a_rem:
        a_bit = a_rem & -a_rem
        a = a_bit.bit_length() - 1
        b_rem = right
        while b_rem:
            b_bit = b_rem & -b_rem
            b = b_bit.bit_length() - 1
            out ^= 1 << GROUP_MUL[a][b]
            b_rem ^= b_bit
        a_rem ^= a_bit
    return out


def formal_matrix_product(word):
    """Literal 4x4 matrix product with 60-bit group-algebra coefficients."""
    out = list(identity_state())
    one = 1 << E
    for g, u, v in word:
        factor = [0] * NCELL
        for row in range(ROLES):
            for col in range(ROLES):
                cell = one if row == col else 0
                if ((u >> row) & 1) and ((v >> col) & 1):
                    cell ^= one ^ (1 << g)
                factor[ROLES * row + col] = cell
        nxt = [0] * NCELL
        for row in range(ROLES):
            for col in range(ROLES):
                value = 0
                for middle in range(ROLES):
                    value ^= convolve(
                        out[ROLES * row + middle], factor[ROLES * middle + col]
                    )
                nxt[ROLES * row + col] = value
        out = nxt
    return tuple(out)


def group_elements_digest() -> str:
    """Match predecessor a5-conjugate-5cycle-seedd316f8 group digest."""
    lines = ["".join(map(str, element)) for element in ELEMENTS]
    return hashlib.sha256("\n".join(lines).encode("ascii")).hexdigest()


def state_digest(state) -> str:
    payload = ",".join(f"{cell:015x}" for cell in state)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def bfs_short_layers(target):
    """Forward BFS from identity through SHORT_DEPTH; return layer sizes and hits."""
    identity = identity_state()
    frontier = {identity}
    seen = {identity}
    layer_sizes = [1]
    hits = []
    for _depth in range(1, SHORT_DEPTH + 1):
        nxt = set()
        hit = 0
        for st in frontier:
            for call in CALLS:
                ns = step(st, call)
                if ns not in seen:
                    seen.add(ns)
                    nxt.add(ns)
                if ns == target:
                    hit += 1
        frontier = nxt
        layer_sizes.append(len(nxt))
        hits.append(hit)
    return {
        "layer_sizes": tuple(layer_sizes),
        "seen_total": len(seen),
        "hits_by_depth": tuple(hits),
        "short_witness": None if sum(hits) == 0 else "found",
    }


def all_even_permutations_group():
    """Independent A5 construction: every even permutation of {0..4}."""
    elements = tuple(
        sorted(p for p in itertools.permutations(range(5)) if even_permutation(p))
    )
    need(len(elements) == GROUP_ORDER, "even-permutation A5 must have order 60")
    index = {g: i for i, g in enumerate(elements)}
    table = tuple(tuple(index[compose(a, b)] for b in elements) for a in elements)
    return elements, index, table
