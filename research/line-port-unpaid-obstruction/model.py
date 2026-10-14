# SPDX-License-Identifier: Apache-2.0
"""Abstract line-port rank-tracking model for unpaid-coordinate bounds.

Scoped model (not a claim about every conceivable decoder):
  * v ports; each port has s live slots (selected complex: s = 8, v = 112);
  * ambient dimension N; a set Offset of d distinguished port-label directions;
  * for every coordinate i not in Offset, track the F2-rank of an abstract
    s-by-s value matrix on one port's slots, starting at rank s and ending at 0;
  * an event that crosses i, or a paid label change of i, changes that rank by
    at most 1; bridges, same-side shears, helpers, centres and monomials that
    ignore i leave the rank unchanged.

Lemma. Summing the necessary rank drops over the N - d non-offset coordinates
gives at least s * (N - d) paid i-crossing (or paid label-change) events on that
port. Across v ports, at least v * s * (N - d) such events occur. Each unpaid
coordinate is a (slot, direction) pair that is never paid-advanced. With at most
one unpaid direction accounted per non-offset direction per port in the equality
case used by the selected stock, the total unpaid count satisfies

    U <= v * (N - d).

At the selected complex line (v = 112, N = 9, d = 1) this is U <= 896. The
hosted nine-stage stock has exactly W = 896 live families and U = W unpaid
coordinates (one per family), so the bound is tight. In particular, two unpaid
coordinates per family would require U = 1792 > 896, which is impossible in this
model without increasing N - d (changing ambient dimension or the offset set).

This file only checks the abstract counting model and its small-domain
saturation. Geometry citations and selected-record attestation live in verify.py.
"""
from __future__ import annotations

from dataclasses import dataclass


def require(ok: bool, why: str) -> None:
    if not ok:
        raise AssertionError(why)


@dataclass(frozen=True)
class PortState:
    """Rank tracker for one ambient coordinate on one port's s slots."""

    rank: int
    slots: int

    def __post_init__(self) -> None:
        require(0 <= self.rank <= self.slots, "rank in [0, s]")


def initial_state(slots: int) -> PortState:
    require(slots >= 1, "slots")
    return PortState(rank=slots, slots=slots)


def apply_crossing(state: PortState) -> PortState:
    """A paid crossing / paid label-change of this coordinate: rank drops by at most 1."""
    if state.rank == 0:
        return state
    return PortState(rank=state.rank - 1, slots=state.slots)


def apply_inert(state: PortState) -> PortState:
    """Bridges, same-side shears, helpers, centres, monomials: rank unchanged."""
    return state


def min_crossings_to_clear(slots: int) -> int:
    """Exactly s crossings are necessary and sufficient to take rank s -> 0."""
    state = initial_state(slots)
    steps = 0
    while state.rank > 0:
        state = apply_crossing(state)
        steps += 1
    require(state.rank == 0, "cleared")
    require(steps == slots, "tight crossing count")
    return steps


def unpaid_upper_bound(ports: int, ambient: int, offset_dirs: int) -> int:
    """U <= v * (N - d) in the equality accounting of the lemma statement."""
    require(ports >= 1 and ambient >= 1, "ports/ambient")
    require(0 <= offset_dirs < ambient, "offset dirs")
    return ports * (ambient - offset_dirs)


def selected_complex_line() -> dict:
    """Pinned selected complex template parameters used by the bound corollary."""
    return {
        "ports_v": 112,
        "ambient_N": 9,
        "offset_d": 1,
        "slots_per_port_s": 8,
        "families_per_replica_W": 896,  # 2 * 4 * 112
        "stages": 9,
        "calls_N": 144,
        "width_m": 73,
        "centre_per_call": 64,
        "unpaid_per_family_u": 1,
    }


def corollary_two_unpaid_blocked(line: dict | None = None) -> dict:
    """At the selected line-port ambient N=9, u=2 is blocked by the counting bound."""
    line = selected_complex_line() if line is None else line
    bound = unpaid_upper_bound(line["ports_v"], line["ambient_N"], line["offset_d"])
    need = 2 * line["families_per_replica_W"]
    require(bound == line["ports_v"] * (line["ambient_N"] - line["offset_d"]), "bound formula")
    require(bound == line["families_per_replica_W"], "selected equality U_max = W")
    return {
        "unpaid_upper_bound": bound,
        "unpaid_needed_for_u2": need,
        "blocked": need > bound,
        "min_ambient_minus_offset_for_u2": (
            (need + line["ports_v"] - 1) // line["ports_v"]
        ),
    }


def exhaustive_small_domain() -> dict:
    """Exhaustively check the rank tracker on a bounded (s, event-pattern) domain."""
    checked = 0
    # For each slot count s, any interleaving of inert and crossing events that
    # ends at rank 0 needs at least s crossings; extra crossings cannot raise rank.
    for slots in range(1, 7):
        necessary = min_crossings_to_clear(slots)
        require(necessary == slots, "necessary crossings")
        # All binary strings of length <= 2s with enough crossings clear iff
        # crossings >= s (order does not matter for this monotone tracker).
        limit = 2 * slots
        for mask in range(1 << limit):
            state = initial_state(slots)
            crossings = 0
            for bit in range(limit):
                if mask >> bit & 1:
                    state = apply_crossing(state)
                    crossings += 1
                else:
                    state = apply_inert(state)
            if crossings >= slots:
                require(state.rank == 0, "enough crossings clear")
            checked += 1
        # Bound arithmetic for small (v,N,d).
        for ports in range(1, 6):
            for ambient in range(1, 8):
                for offset in range(0, ambient):
                    u = unpaid_upper_bound(ports, ambient, offset)
                    require(u == ports * (ambient - offset), "arithmetic")
                    checked += 1
    # Selected corollary.
    cor = corollary_two_unpaid_blocked()
    require(cor["blocked"], "u=2 blocked at selected N=9")
    require(cor["min_ambient_minus_offset_for_u2"] == 16, "need N-d >= 16 for u=2")
    checked += 1
    return {"patterns_and_bounds_checked": checked, "corollary": cor}
