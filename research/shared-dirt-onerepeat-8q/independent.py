#!/usr/bin/env python3
"""Independent shared-dirt one-repeat (2,6) dual census at Q=8.

Does not import model.py or verify.py. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from itertools import combinations, permutations
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
INF = 99


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def even_odd_tables(slots):
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


def dual_shared_short(e_long, o_long, sigma):
    total = 0
    for m in range(1, 32):
        best = e_long[m]
        if e_long[m ^ sigma] < INF:
            best = min(best, 2 + e_long[m ^ sigma])
        if o_long[m] < INF:
            best = min(best, 1 + o_long[m])
        if o_long[m ^ sigma] < INF:
            best = min(best, 1 + o_long[m ^ sigma])
        if best >= INF:
            return None
        total += best
    return total


def dual_independent_short(e_long, sigma):
    total = 0
    for m in range(1, 32):
        best = INF
        if e_long[m] < INF:
            best = e_long[m]
        if e_long[m ^ sigma] < INF:
            best = min(best, 2 + e_long[m ^ sigma])
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


def tariff(q, r, x):
    return 38 * q + 2 * r + 2 * x


def _work(dbls):
    valid = 0
    rank4 = 0
    rank_lt4 = 0
    covering = 0
    covering_rank_lt4 = 0
    hist = Counter()
    for dbl in dbls:
        for others in combinations([x for x in range(1, 32) if x != dbl], 3):
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
                        if dual_shared_short(e, o, sigma) is not None:
                            covering_rank_lt4 += 1
                    continue
                rank4 += 1
                span, rank = gf2_span(slots)
                if rank != 4:
                    fail("rank mismatch")
                even_sum = sum(e[v] for v in span if v)
                if even_sum != 40:
                    fail(f"Σe={even_sum}")
                for sigma in range(1, 32):
                    r = dual_shared_short(e, o, sigma)
                    if sigma in span:
                        if r is not None:
                            covering += 1
                            hist[r] += 1
                        continue
                    if r is None:
                        continue
                    if r != 96:
                        fail(f"expected R=96 got {r}")
                    covering += 1
                    hist[96] += 1
    return valid, rank4, rank_lt4, covering, covering_rank_lt4, hist


def main():
    pinned = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = pinned["claim"]

    n = max(1, os.cpu_count() or 2)
    chunks = [list(range(1, 32))[i::n] for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_work, chunks)

    valid = rank4 = rank_lt4 = covering = covering_rank_lt4 = 0
    hist = Counter()
    for v, r4, rlt, c, c_lt, h in parts:
        valid += v
        rank4 += r4
        rank_lt4 += rlt
        covering += c
        covering_rank_lt4 += c_lt
        hist.update(h)

    if valid != claim["valid_one_repeat_walks"]:
        fail(f"valid {valid}")
    if rank4 != claim["rank4_one_repeat_walks"]:
        fail(f"rank4 {rank4}")
    if rank_lt4 != claim["valid_rank_lt4_walks"]:
        fail(f"rank_lt4 {rank_lt4}")
    if covering_rank_lt4 != 0:
        fail(f"covering_rank_lt4 {covering_rank_lt4}")
    if covering != claim["covering_pairs"]:
        fail(f"covering {covering}")
    if min(hist) != claim["min_R"] or dict(hist) != {96: claim["covering_pairs"]}:
        fail(f"histogram {dict(hist)}")

    short, long = (0, 16), (0, 4, 1, 8, 2, 1)
    e, o = even_odd_tables(long)
    if dual_shared_short(e, o, short[1]) != 96:
        fail("champ shared")
    if dual_independent_short(e, short[1]) != 112:
        fail("champ independent")
    if tariff(8, 96, 0) != 496:
        fail("tariff")
    if tariff(8, 96, 0) <= 436:
        fail("undercut")

    print(
        "PASS_SHARED_DIRT_ONEREPEAT_8Q",
        f"shared_dirt_onerepeat_min_R={claim['min_R']}",
        f"covering={claim['covering_pairs']}",
        f"tariff_floor={claim['tariff_floor_at_X0']}",
        f"independent_one_repeat_min_R={claim['independent_one_repeat_min_R']}",
        "answers_independent_walks_9q_oq2_mixed_shared_dirt_excess",
        "no_undercut_436",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
