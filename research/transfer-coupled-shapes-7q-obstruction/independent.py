#!/usr/bin/env python3
"""Independent transfer-coupled census (complement of verify live shapes).

Does not import model.py census helpers beyond constants/dual primitives used
inline. Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from multiprocessing import Pool, cpu_count
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
INF = 99
_CUR = None

# Complement of verify live shapes.
SHAPES = ((1, 2, 4), (1, 3, 3), (3, 2, 2), (2, 2, 3))


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def even_table(slots):
    n = len(slots)
    even = [INF] * 32
    even[0] = 0
    sl = slots
    for bits in range(1, 1 << n):
        size = bits.bit_count()
        if size & 1:
            continue
        value = 0
        b = bits
        i = 0
        while b:
            if b & 1:
                value ^= sl[i]
            b >>= 1
            i += 1
        if size < even[value]:
            even[value] = size
    return even


def dual_from_support(e1, costs, masks):
    total = 0
    for m in range(1, 32):
        best = INF
        for i in range(len(masks)):
            c = e1[m ^ masks[i]]
            if c < INF:
                s = costs[i] + c
                if s < best:
                    best = s
        if best >= INF:
            return None
        total += best
    return total


def support_of(e):
    costs, masks = [], []
    for a, c in enumerate(e):
        if c < INF:
            costs.append(c)
            masks.append(a)
    return costs, masks


def dual_full(e0, e1):
    return dual_from_support(e1, *support_of(e0))


def tariff(q, r, x):
    return 38 * q + 2 * r + 2 * x


def census_124():
    hist = Counter()
    covering = 0
    long_tabs = {
        nz: even_table((0,) + nz) for nz in combinations(range(1, 32), 4)
    }
    for short_nz in combinations(range(1, 32), 2):
        costs, masks = support_of(even_table((0,) + short_nz))
        for e in long_tabs.values():
            r = dual_from_support(e, costs, masks)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
    return covering, hist


def census_133():
    hist = Counter()
    covering = 0
    tabs = {
        nz: (even_table((0,) + nz), support_of(even_table((0,) + nz)))
        for nz in combinations(range(1, 32), 3)
    }
    # recompute support once
    tabs = {}
    for nz in combinations(range(1, 32), 3):
        e = even_table((0,) + nz)
        tabs[nz] = (e, support_of(e))
    keys = list(tabs.keys())
    for i, nz0 in enumerate(keys):
        _e0, (sc, sm) = tabs[nz0]
        for nz1 in keys[i:]:
            e1, _ = tabs[nz1]
            r = dual_from_support(e1, sc, sm)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
    return covering, hist


def _handle_prefix(pref_nz):
    p, a, b = _CUR
    prefix = (0,) + tuple(pref_nz)
    used = set(prefix)
    avail = [x for x in range(1, 32) if x not in used]
    a_sets = list(combinations(avail, a))
    b_sets = list(combinations(avail, b))
    a_data = []
    for A in a_sets:
        e = even_table(prefix + A)
        a_data.append((A,) + support_of(e))
    b_tabs = {B: even_table(prefix + B) for B in b_sets}
    hist = Counter()
    covering = 0
    min_r = 999
    for A, sc, sm in a_data:
        for B in b_sets:
            if a == b and B < A:
                continue
            r = dual_from_support(b_tabs[B], sc, sm)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
            if r < min_r:
                min_r = r
    return covering, min_r, dict(hist)


def census_pooled(p, a, b):
    global _CUR
    _CUR = (p, a, b)
    prefs = list(combinations(range(1, 32), p - 1))
    hist = Counter()
    covering = 0
    min_r = 999
    with Pool(processes=min(4, cpu_count() or 1)) as pool:
        for cov, mn, h in pool.imap_unordered(
            _handle_prefix, prefs, chunksize=max(1, len(prefs) // 32 or 1)
        ):
            covering += cov
            hist.update(h)
            if mn < min_r:
                min_r = mn
    return covering, hist


def check_shape(key, covering, hist, claim_shapes):
    pinned = claim_shapes[key]
    if covering != pinned["covering_pairs"]:
        fail(f"{key} covering {covering} != {pinned['covering_pairs']}")
    if min(hist) != pinned["min_R"] or set(hist) != set(map(int, pinned["histogram"])):
        fail(f"{key} hist {dict(hist)} vs {pinned['histogram']}")
    for r, c in hist.items():
        if pinned["histogram"].get(str(r)) != c:
            fail(f"{key} hist count {r}")
    if pinned["min_R"] < 84:
        fail(f"{key} below global floor")


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = cert["claim"]
    shapes = cert["shapes"]

    if claim["global_min_R"] != 84:
        fail(f"global min {claim['global_min_R']}")
    if claim["tariff_floor_at_R84_fairX9"] != 452:
        fail("tariff floor")
    if claim["binding_min_fair_X_at_R84"] != 9:
        fail("fair X floor")
    if tariff(7, 84, 9) != 452 or tariff(7, 84, 9) <= 436:
        fail("tariff arithmetic")
    if claim["undercuts_436_after_complete_bill"]:
        fail("undercut flag")

    # Binding champion recomputed without model.py
    w0 = (0, 1, 3, 6, 12, 8)
    w1 = (0, 1, 3, 6, 12, 16)
    r_bind = dual_full(even_table(w0), even_table(w1))
    if r_bind != 84:
        fail(f"binding champion R {r_bind}")

    c124, h124 = census_124()
    check_shape("1_2_4", c124, h124, shapes)
    c133, h133 = census_133()
    check_shape("1_3_3", c133, h133, shapes)
    c322, h322 = census_pooled(3, 2, 2)
    check_shape("3_2_2", c322, h322, shapes)
    c223, h223 = census_pooled(2, 2, 3)
    check_shape("2_2_3", c223, h223, shapes)

    # All certificate shape mins are >= 84 and include binding 84.
    mins = [shapes[k]["min_R"] for k in shapes]
    if min(mins) != 84 or 84 not in mins:
        fail(f"mins {mins}")

    print(
        "PASS_INDEPENDENT_TRANSFER_COUPLED_SHAPES_7Q",
        f"covering_124={c124}",
        f"covering_133={c133}",
        f"covering_322={c322}",
        f"covering_223={c223}",
        "global_min_R=84",
        "tariff_floor=452",
        "endpoint=436",
        "answers_remaining_transfer_coupled_shapes",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
