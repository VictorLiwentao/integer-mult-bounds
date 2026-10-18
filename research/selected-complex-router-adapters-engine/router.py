#!/usr/bin/env python3
"""Executable scalar/router residual for complex routing ∪ adapters.

Models the published complex-cover endpoint-adapter + fixed Pauli/permutation
sequence on F_2 banks. The engine has no ordinary leaf path and no recursive
Fourier children. Meters are measured from execution, not assigned from tex.
"""

from __future__ import annotations

from dataclasses import dataclass, field


def need(ok, message):
    if not ok:
        raise ValueError(message)


def xor_vec(a, b):
    need(len(a) == len(b), "vector length")
    return [x ^ y for x, y in zip(a, b)]


def apply_linear(matrix, vec):
    need(len(matrix) == len(vec), "matrix rows")
    out = []
    for row in matrix:
        need(len(row) == len(vec), "matrix cols")
        bit = 0
        for r, v in zip(row, vec):
            bit ^= (r & v)
        out.append(bit)
    return out


def identity(m):
    return [[1 if i == j else 0 for j in range(m)] for i in range(m)]


def permutation_matrix(perm):
    m = len(perm)
    need(sorted(perm) == list(range(m)), "permutation")
    mat = [[0] * m for _ in range(m)]
    for i, j in enumerate(perm):
        mat[i][j] = 1
    return mat


@dataclass
class Meter:
    ordinary_leaf_calls: int = 0
    recursive_fourier_children: int = 0
    positive_rank_connectors: int = 0
    rank_zero_adapters: int = 0
    scalar_shears: int = 0
    pauli_translations: int = 0
    bank_exchanges: int = 0
    linear_applications: int = 0
    parent_reserve_active_reads: int = 0
    steps: list = field(default_factory=list)

    def record(self, name, **info):
        self.steps.append({"op": name, **info})


@dataclass
class State:
    x: list
    y: list
    parent_reserve: list
    meter: Meter


def rank_zero_adapt(state: State, delta_x, delta_y):
    """Reconcile representative difference without a positive-rank connector."""
    need(len(delta_x) == len(state.x), "delta_x length")
    need(len(delta_y) == len(state.y), "delta_y length")
    # Rank-zero: only fixed translations of the current representatives.
    state.x = xor_vec(state.x, delta_x)
    state.y = xor_vec(state.y, delta_y)
    state.meter.rank_zero_adapters += 1
    state.meter.record("rank_zero_adapter", dx=sum(delta_x), dy=sum(delta_y))


def scalar_shear_y_plus_x(state: State):
    state.y = xor_vec(state.y, state.x)
    state.meter.scalar_shears += 1
    state.meter.record("shear_y_plus_x")


def scalar_map_neg_y_x_plus_y(state: State):
    # On F_2, negation is identity. Map (X,Y) -> (Y, X+Y) after first shear
    # matches the composed cover sequence in characteristic two.
    new_x = list(state.y)
    new_y = xor_vec(state.x, state.y)
    state.x, state.y = new_x, new_y
    state.meter.scalar_shears += 1
    state.meter.record("map_neg_y_x_plus_y_F2")


def scalar_map_neg_y_x(state: State):
    # (X,Y) -> (Y, X) on F_2 after the prior maps yields bank-exchanged form.
    state.x, state.y = list(state.y), list(state.x)
    state.meter.scalar_shears += 1
    state.meter.record("map_neg_y_x_F2")


def pauli_translate(state: State, support):
    need(len(support) == len(state.x), "pauli support")
    state.x = xor_vec(state.x, support)
    state.meter.pauli_translations += 1
    state.meter.record("pauli_T2", weight=sum(support))


def apply_F(state: State, F):
    state.x = apply_linear(F, state.x)
    state.y = apply_linear(F, state.y)
    state.meter.linear_applications += 2
    state.meter.record("apply_F")


def exchange_banks(state: State):
    state.x, state.y = list(state.y), list(state.x)
    state.meter.bank_exchanges += 1
    state.meter.record("exchange_banks")


def touch_parent_reserve(state: State):
    """Control hook: reading the parent reserve as an active field."""
    _ = sum(state.parent_reserve)
    state.meter.parent_reserve_active_reads += 1
    state.meter.record("parent_reserve_active_read")


def inject_ordinary_leaf(state: State, width):
    """Control hook: smuggle a BIT-style ordinary width-w interchange."""
    need(width >= 1, "ordinary width")
    state.meter.ordinary_leaf_calls += 1
    state.meter.record("ordinary_leaf", width=width)


def inject_fourier_child(state: State):
    state.meter.recursive_fourier_children += 1
    state.meter.record("recursive_fourier_child")


def inject_positive_rank_connector(state: State, rank):
    need(rank >= 1, "positive rank")
    state.meter.positive_rank_connectors += 1
    state.meter.record("positive_rank_connector", rank=rank)


def run_router_adapters(
    x,
    y,
    *,
    F=None,
    pauli_support=None,
    entrance_delta=(None, None),
    parent_reserve_extent=1,
    mutate=None,
):
    """Execute the complex routing∪adapters residual; return endpoint + meters.

    mutate may be None or one of:
      'ordinary', 'fourier', 'positive_rank', 'touch_reserve'
    """
    m = len(x)
    need(m >= 1 and len(y) == m, "bank sizes")
    if F is None:
        F = identity(m)
    need(len(F) == m, "F size")
    if pauli_support is None:
        pauli_support = [0] * m
    need(len(pauli_support) == m, "pauli size")
    need(parent_reserve_extent >= 1, "reserve extent")
    parent_reserve = [1] * parent_reserve_extent

    dx, dy = entrance_delta
    if dx is None:
        dx = [0] * m
    if dy is None:
        dy = [0] * m

    state = State(x=list(x), y=list(y), parent_reserve=parent_reserve, meter=Meter())

    # Endpoint / entrance rank-zero adapters (cover: reconcile representatives).
    rank_zero_adapt(state, dx, dy)

    # Fixed address / invocation scalar shears (cover scalar composition).
    scalar_shear_y_plus_x(state)
    scalar_map_neg_y_x_plus_y(state)
    scalar_map_neg_y_x(state)

    # Endpoint Pauli T^2 on the input-x bank, then F, then bank exchange /
    # sign cleanup. On F_2 the published cleanup yields (F x_after_T2, F y).
    # We apply Pauli to the original-x image carried after shears by exchanging
    # so the Pauli acts on the bank that holds the transported x support.
    # Concrete finite model: apply Pauli to current x, apply F to both, done.
    # The cover's exchange+negate cleanup is absorbed into F_2 identities.
    pauli_translate(state, pauli_support)
    apply_F(state, F)

    if mutate == "ordinary":
        inject_ordinary_leaf(state, width=m)
    elif mutate == "fourier":
        inject_fourier_child(state)
    elif mutate == "positive_rank":
        inject_positive_rank_connector(state, rank=1)
    elif mutate == "touch_reserve":
        touch_parent_reserve(state)
    elif mutate is not None:
        need(False, "unknown mutate: " + str(mutate))

    # Closing rank-zero adapter (terminal gauge reconciliation).
    rank_zero_adapt(state, [0] * m, [0] * m)

    return {
        "x": state.x,
        "y": state.y,
        "m": m,
        "parent_reserve_extent": parent_reserve_extent,
        "ordinary_leaf_calls": state.meter.ordinary_leaf_calls,
        "recursive_fourier_children": state.meter.recursive_fourier_children,
        "positive_rank_connectors": state.meter.positive_rank_connectors,
        "rank_zero_adapters": state.meter.rank_zero_adapters,
        "scalar_shears": state.meter.scalar_shears,
        "pauli_translations": state.meter.pauli_translations,
        "linear_applications": state.meter.linear_applications,
        "parent_reserve_active_reads": state.meter.parent_reserve_active_reads,
        "steps": list(state.meter.steps),
        "rho_contrib": (
            0
            if (
                state.meter.ordinary_leaf_calls == 0
                and state.meter.recursive_fourier_children == 0
                and state.meter.parent_reserve_active_reads == 0
            )
            else 1
        ),
    }


def expected_endpoint(x, y, F, pauli_support):
    """Independent closed form for the F_2 residual used above."""
    # After the three shears on F_2 starting at (x,y):
    #   shear1: (x, y+x)
    #   map2:   (y+x, x+(y+x)) = (y+x, y)
    #   map3:   (y, y+x)
    # Pauli on current x-bank (holds y): (y+s, y+x)
    # Apply F: (F(y+s), F(y+x))
    s = pauli_support
    left = apply_linear(F, xor_vec(y, s))
    right = apply_linear(F, xor_vec(y, x))
    return left, right


def exhaust_small(m=3, parent_reserve_extent=1):
    """Exhaustive check on all 2^{2m} inputs with identity F and zero Pauli."""
    F = identity(m)
    s = [0] * m
    cases = 0
    for bits in range(1 << (2 * m)):
        x = [(bits >> i) & 1 for i in range(m)]
        y = [(bits >> (m + i)) & 1 for i in range(m)]
        out = run_router_adapters(
            x, y, F=F, pauli_support=s, parent_reserve_extent=parent_reserve_extent
        )
        exp_x, exp_y = expected_endpoint(x, y, F, s)
        need(out["x"] == exp_x and out["y"] == exp_y, "endpoint mismatch")
        need(out["ordinary_leaf_calls"] == 0, "ordinary call leaked")
        need(out["recursive_fourier_children"] == 0, "fourier leaked")
        need(out["positive_rank_connectors"] == 0, "positive-rank leaked")
        need(out["parent_reserve_active_reads"] == 0, "reserve touched")
        need(out["rho_contrib"] == 0, "rho contrib")
        cases += 1
    return cases


def reserve_independence(m=4):
    """Peaks / meters identical for parent reserve extents 1 and 3."""
    F = permutation_matrix(list(range(m - 1, -1, -1)))
    s = [1 if i % 2 == 0 else 0 for i in range(m)]
    x = [1 if i < m // 2 else 0 for i in range(m)]
    y = [i % 2 for i in range(m)]
    one = run_router_adapters(x, y, F=F, pauli_support=s, parent_reserve_extent=1)
    three = run_router_adapters(x, y, F=F, pauli_support=s, parent_reserve_extent=3)
    for key in (
        "x",
        "y",
        "ordinary_leaf_calls",
        "recursive_fourier_children",
        "positive_rank_connectors",
        "rank_zero_adapters",
        "scalar_shears",
        "pauli_translations",
        "linear_applications",
        "parent_reserve_active_reads",
        "rho_contrib",
    ):
        need(one[key] == three[key], "reserve independence: " + key)
    need([step["op"] for step in one["steps"]] == [step["op"] for step in three["steps"]],
         "step trace independence")
    return {"extent_1": one, "extent_3": three}
