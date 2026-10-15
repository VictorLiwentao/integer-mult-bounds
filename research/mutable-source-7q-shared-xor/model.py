"""Interleaved source-XOR schedules for seven-query R=82 invoices. Wentao Li + AI, Apache-2.0.

Enlarges the path-local compute/uncompute shear model of the PR1898/789q invoice
lineage: elementary source XORs may be interleaved arbitrarily with queries, as
long as sources restore to the identity at the end. Connector increments are the
queried source-matrix columns in the original basis.
"""
from __future__ import annotations

import itertools
from collections import deque


TARIFF_B = 38
TARIFF_A = 2
TARIFF_X = 2
ENDPOINT_Q6 = 436
CHAMPION_PATH = (0, 1, 2, 6, 12, 24, 16, 0)
CHAMPION_INCREMENTS = tuple(
    CHAMPION_PATH[i] ^ CHAMPION_PATH[i + 1] for i in range(len(CHAMPION_PATH) - 1)
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def tariff(q, r, x):
    return TARIFF_B * q + TARIFF_A * r + TARIFF_X * x


def min_even_subset_R(slots):
    """Minimum total even-subset readout count on connector prefix slots."""
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
    n = len(slots)
    best = [99] * 32
    for bits in range(1 << n):
        if bits.bit_count() % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        size = bits.bit_count()
        if size < best[value]:
            best[value] = size
    if any(best[mask] >= 99 for mask in range(1, 32)):
        return None
    return sum(best[1:])


def path_X(closed):
    """Path-local compute/uncompute XOR count on a closed connector walk."""
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        need(delta != 0, "zero query edge")
        total += 2 * (delta.bit_count() - 1)
    return total


def rank_increments(closed):
    rows = [closed[i] ^ closed[i + 1] for i in range(len(closed) - 1)]
    rank = 0
    for bit in range(5):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] >> bit & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] >> bit & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def mat_id():
    return tuple(1 << i for i in range(5))


def apply_x(cols, s, t):
    cols = list(cols)
    cols[t] ^= cols[s]
    return tuple(cols)


def elementary_neighbors(cols):
    return [
        apply_x(cols, s, t)
        for s, t in itertools.product(range(5), repeat=2)
        if s != t
    ]


def ball_adjacency(radius):
    """Cayley ball of elementary source shears about the identity, with adjacency."""
    dist = {mat_id(): 0}
    queue = deque([mat_id()])
    while queue:
        cols = queue.popleft()
        depth = dist[cols]
        if depth >= radius:
            continue
        for nxt in elementary_neighbors(cols):
            if nxt not in dist:
                dist[nxt] = depth + 1
                queue.append(nxt)
    adj = {
        cols: [nxt for nxt in elementary_neighbors(cols) if nxt in dist] for cols in dist
    }
    return dist, adj


def increments_realizable(incs, budget, adj):
    """True iff a restored elementary-XOR walk of length <= budget realizes incs."""
    current = {mat_id(): 0}
    for need_inc in incs:
        seen = dict(current)
        queue = deque(current.items())
        while queue:
            cols, cost = queue.popleft()
            if cost >= budget:
                continue
            for nxt in adj[cols]:
                if nxt not in seen or cost + 1 < seen[nxt]:
                    seen[nxt] = cost + 1
                    queue.append((nxt, cost + 1))
        current = {
            cols: cost
            for cols, cost in seen.items()
            if any(cols[j] == need_inc for j in range(5))
        }
        if not current:
            return False
    seen = dict(current)
    queue = deque(current.items())
    while queue:
        cols, cost = queue.popleft()
        if cols == mat_id():
            return True
        if cost >= budget:
            continue
        for nxt in adj[cols]:
            if nxt not in seen or cost + 1 < seen[nxt]:
                seen[nxt] = cost + 1
                queue.append((nxt, cost + 1))
    return False


def restored_length_two_words():
    """All restored elementary-XOR words of length exactly two from the identity."""
    identity = mat_id()
    words = []
    for s, t in itertools.product(range(5), repeat=2):
        if s == t:
            continue
        mid = apply_x(identity, s, t)
        for s2, t2 in itertools.product(range(5), repeat=2):
            if s2 == t2:
                continue
            if apply_x(mid, s2, t2) == identity:
                multi = frozenset(c for c in mid if c.bit_count() >= 2)
                words.append(
                    {
                        "first": [s, t],
                        "second": [s2, t2],
                        "mid_multi_bit_columns": sorted(multi),
                    }
                )
    return words


def r82_covering_sets():
    """All 6-subsets S of F2^5\\{0} with even-subset readout cost R=82 on (0,)+S."""
    out = []
    for subset in itertools.combinations(range(1, 32), 6):
        if min_even_subset_R((0,) + subset) == 82:
            out.append(subset)
    return out


def path_x6_fullrank_increments(cover=None):
    """Increment tuples of full-rank closed walks with path-local X=6 on R=82 sets."""
    if cover is None:
        cover = r82_covering_sets()
    paths = []
    for subset in cover:
        for order in itertools.permutations(subset):
            closed = (0,) + order + (0,)
            if path_X(closed) != 6:
                continue
            if rank_increments(closed) < 5:
                continue
            paths.append(tuple(closed[i] ^ closed[i + 1] for i in range(7)))
    return paths


def multi_bit_pattern(incs):
    multi = [d for d in incs if d.bit_count() >= 2]
    weights = tuple(sorted(d.bit_count() for d in multi))
    return {
        "multi_bit": multi,
        "distinct_multi": len(set(multi)),
        "has_repeat": len(multi) != len(set(multi)),
        "weight_pattern": weights,
    }
