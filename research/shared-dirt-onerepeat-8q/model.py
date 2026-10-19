"""Shared-dirt one-repeat partitioned dual at eight queries.

Freestanding priced alphabet under PR1898 (b,a,x)=(38,2,2): one-repeat
length-6 longs paired with short (0,σ) under **shared dirt** (joint even
live-read parity). Answers independent-walks-9q OQ2 (mixed shared-dirt +
excess) without editing leave-alones through #2883 / #2868 / #2867 / #2861 /
#2860 / #2858 / #2851.

Self-contained relative to the shared-dirt / one-repeat / iw lineage.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, permutations
from multiprocessing import Pool
import os


def need(ok, message):
    if not ok:
        raise ValueError(message)


INF = 99

EXPECTED = {
    "Q": 8,
    "partition": (2, 6),
    "independent_one_repeat_min_R": 112,
    "shared_dirt_distinct_min_R": 82,
    "valid_one_repeat_walks": 4530960,
    "rank4_one_repeat_walks": 3749760,
    "valid_rank_lt4_walks": 781200,
    "covering_pairs": 59996160,
    "min_R": 96,
    "histogram": {"96": 59996160},
    "sum_even_rank4": 40,
    "sigmas_outside_rank4": 16,
    "save_vs_independent": 16,
    "champion_walks": ((0, 16), (0, 4, 1, 8, 2, 1)),
    "champion_path_X": 8,
    "champion_rank": 4,
    "champion_independent_R": 112,
    "champion_shared_R": 96,
    "tariff_floor_at_X0": 496,
    "endpoint_tariff_Q6": 436,
}


def tariff_qrx(q, r, x, extra=0):
    """Abstract complete-call tariff at (b,a,x)=(38,2,2), plus optional extras."""
    leaves = 28 * q + r
    nodes = 9 * q
    dispatch = q + r + x
    return leaves + nodes + x + dispatch + extra


def even_odd_tables(slots):
    """Even- and odd-subset per-mask minima on a slot list (INF if unreachable)."""
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
    n = len(slots)
    even = [INF] * 32
    odd = [INF] * 32
    even[0] = 0
    for bits in range(1, 1 << n):
        size = bits.bit_count()
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        table = even if size % 2 == 0 else odd
        if size < table[value]:
            table[value] = size
    return even, odd


def even_table(slots):
    even, _odd = even_odd_tables(slots)
    return even


def dual_independent_short_long(e_long, sigma):
    """Independent-dirt dual when the short walk is (0, sigma)."""
    total = 0
    for m in range(1, 32):
        best = INF
        if e_long[m] < INF:
            best = e_long[m]
        flipped = e_long[m ^ sigma]
        if flipped < INF:
            best = min(best, 2 + flipped)
        if best >= INF:
            return None
        total += best
    return total


def dual_shared_short_long(e_long, o_long, sigma):
    """Shared-dirt dual when the short walk is (0, sigma).

    Short tables: e[0]=0, e[sigma]=2, o[0]=1, o[sigma]=1.
    Per mask: min(e_long[m], 2+e_long[m⊕σ], 1+o_long[m], 1+o_long[m⊕σ]).
    """
    total = 0
    for m in range(1, 32):
        best = e_long[m]
        flipped = e_long[m ^ sigma]
        if flipped < INF:
            best = min(best, 2 + flipped)
        odd_m = o_long[m]
        if odd_m < INF:
            best = min(best, 1 + odd_m)
        odd_flipped = o_long[m ^ sigma]
        if odd_flipped < INF:
            best = min(best, 1 + odd_flipped)
        if best >= INF:
            return None
        total += best
    return total


def path_X(slots):
    closed = slots + (0,)
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        if delta == 0:
            return None
        total += 2 * (delta.bit_count() - 1)
    return total


def valid_restored_walk(slots):
    if type(slots) is not tuple or not slots or slots[0] != 0:
        return False
    if len(slots) < 2:
        return False
    return path_X(slots) is not None


def gf2_span(vals):
    basis = []
    for v in vals:
        x = v
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    span = {0}
    for b in basis:
        span |= {s ^ b for s in span}
    return frozenset(span), len(basis)


def gf2_rank(vals):
    return gf2_span(vals)[1]


def is_one_repeat_long(slots):
    """Length-6 walk whose five nonzero slots have exactly one repeated label."""
    need(type(slots) is tuple and len(slots) == 6 and slots[0] == 0, "long form")
    counts = sorted(Counter(slots[1:]).values())
    return counts == [1, 1, 1, 2]


def structural_shared_rank4_outside(sigma, long_slots):
    """When long span has rank 4 and sigma is outside, shared-dirt R = 96."""
    e_long, o_long = even_odd_tables(long_slots)
    span, rank = gf2_span(long_slots)
    r = dual_shared_short_long(e_long, o_long, sigma)
    r_ind = dual_independent_short_long(e_long, sigma)
    if r is None or rank != 4 or sigma in span:
        return {
            "applies": False,
            "rank": rank,
            "sigma_in_span": sigma in span,
            "R_shared": r,
            "R_independent": r_ind,
            "sum_even": None,
        }
    even_sum = sum(e_long[v] for v in span if v != 0)
    need(even_sum == EXPECTED["sum_even_rank4"], f"Σe={even_sum}")
    need(r_ind == 112, f"independent outside must be 112, got {r_ind}")
    need(r == 96, f"shared outside must be 96, got {r}")
    need(r_ind - r == EXPECTED["save_vs_independent"], "save 16")
    return {
        "applies": True,
        "rank": 4,
        "sigma_in_span": False,
        "R_shared": r,
        "R_independent": r_ind,
        "sum_even": even_sum,
        "save": r_ind - r,
    }


def _pool_count():
    return max(1, os.cpu_count() or 2)


def _work_dbls(dbls):
    """Census shared-dirt one-repeat (2,6) duals for a chunk of doubled labels."""
    valid = 0
    rank4 = 0
    rank_lt4 = 0
    covering = 0
    covering_rank_lt4 = 0
    hist = Counter()
    sum_e_bad = 0
    inside_cover = 0
    non96 = 0
    champ = None
    for dbl in dbls:
        others_pool = [x for x in range(1, 32) if x != dbl]
        for others in combinations(others_pool, 3):
            labels = (dbl,) + others
            rank_labels = gf2_rank(labels)
            for perm in set(permutations((dbl, dbl) + others)):
                slots = (0,) + perm
                if path_X(slots) is None:
                    continue
                valid += 1
                e, o = even_odd_tables(slots)
                if rank_labels != 4:
                    rank_lt4 += 1
                    for sigma in range(1, 32):
                        if dual_shared_short_long(e, o, sigma) is not None:
                            covering_rank_lt4 += 1
                    continue
                rank4 += 1
                span, rank = gf2_span(slots)
                need(rank == 4, "label rank 4 implies walk span rank 4")
                even_sum = sum(e[v] for v in span if v != 0)
                if even_sum != EXPECTED["sum_even_rank4"]:
                    sum_e_bad += 1
                for sigma in range(1, 32):
                    r = dual_shared_short_long(e, o, sigma)
                    if sigma in span:
                        if r is not None:
                            inside_cover += 1
                            hist[r] += 1
                            covering += 1
                        continue
                    if r is None:
                        continue
                    need(r == 96, f"outside rank-4 shared must be R=96, got {r}")
                    covering += 1
                    hist[96] += 1
                    if champ is None:
                        champ = ((0, sigma), slots)
    return (
        valid,
        rank4,
        rank_lt4,
        covering,
        covering_rank_lt4,
        hist,
        sum_e_bad,
        inside_cover,
        non96,
        champ,
    )


def census_shared_dirt_onerepeat_26(workers=None):
    """All valid one-repeat length-6 longs × short (0,σ); shared-dirt spectrum {96}."""
    n = workers or _pool_count()
    chunks = [list(range(1, 32))[i::n] for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_work_dbls, chunks)
    valid = rank4 = rank_lt4 = covering = covering_rank_lt4 = 0
    sum_e_bad = inside_cover = 0
    hist = Counter()
    champ = None
    for v, r4, rlt, c, c_lt, h, bad, inside, _non96, ch in parts:
        valid += v
        rank4 += r4
        rank_lt4 += rlt
        covering += c
        covering_rank_lt4 += c_lt
        sum_e_bad += bad
        inside_cover += inside
        hist.update(h)
        if champ is None and ch is not None:
            champ = ch
    need(valid == EXPECTED["valid_one_repeat_walks"], "valid walk count")
    need(rank4 == EXPECTED["rank4_one_repeat_walks"], "rank4 walk count")
    need(rank_lt4 == EXPECTED["valid_rank_lt4_walks"], "rank<4 walk count")
    need(valid == rank4 + rank_lt4, "valid partition rank4+rank<4")
    need(covering_rank_lt4 == 0, "rank<4 never covers")
    need(covering == EXPECTED["covering_pairs"], "covering count")
    need(sum_e_bad == 0, "every rank-4 one-repeat has Σe=40")
    need(inside_cover == 0, "sigma in span never covers")
    need(min(hist) == EXPECTED["min_R"], "min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["histogram"],
        "histogram",
    )
    need(rank4 * EXPECTED["sigmas_outside_rank4"] == covering, "16 outside σ")
    need(champ is not None, "champion exists")
    return {
        "kind": "shared_dirt_one_repeat_partition_2_plus_6",
        "Q": 8,
        "valid_one_repeat_walks": valid,
        "rank4_one_repeat_walks": rank4,
        "valid_rank_lt4_walks": rank_lt4,
        "covering_rank_lt4": covering_rank_lt4,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "sum_even_rank4": EXPECTED["sum_even_rank4"],
        "sigmas_outside_rank4": EXPECTED["sigmas_outside_rank4"],
        "first_witness": {
            "96": [list(champ[0]), list(champ[1])],
        },
    }


def champion_analysis():
    short, long = EXPECTED["champion_walks"]
    need(is_one_repeat_long(long), "champion one-repeat")
    e, o = even_odd_tables(long)
    sigma = short[1]
    r_shared = dual_shared_short_long(e, o, sigma)
    r_ind = dual_independent_short_long(e, sigma)
    need(r_shared == EXPECTED["champion_shared_R"], "champ shared R")
    need(r_ind == EXPECTED["champion_independent_R"], "champ independent R")
    struct = structural_shared_rank4_outside(sigma, long)
    need(struct["applies"] is True, "struct applies")
    need(path_X(long) == EXPECTED["champion_path_X"], "champ path X")
    floor = tariff_qrx(8, EXPECTED["min_R"], 0)
    need(floor == EXPECTED["tariff_floor_at_X0"], "floor")
    need(floor > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(
        EXPECTED["min_R"] > EXPECTED["shared_dirt_distinct_min_R"],
        "does not beat shared-dirt distinct floor",
    )
    need(
        EXPECTED["min_R"] < EXPECTED["independent_one_repeat_min_R"],
        "beats independent one-repeat",
    )
    return {
        "champion": {
            "short": list(short),
            "long": list(long),
            "shared_R": r_shared,
            "independent_R": r_ind,
            "path_X": path_X(long),
            "structural": struct,
        },
        "shared_dirt_onerepeat_min_R": EXPECTED["min_R"],
        "independent_one_repeat_min_R": EXPECTED["independent_one_repeat_min_R"],
        "shared_dirt_distinct_min_R": EXPECTED["shared_dirt_distinct_min_R"],
        "tariff_floor_at_X0": floor,
        "endpoint_tariff_Q6": EXPECTED["endpoint_tariff_Q6"],
        "undercuts_436_after_complete_bill": False,
        "beats_independent_one_repeat": True,
        "beats_shared_dirt_distinct_82": False,
    }
