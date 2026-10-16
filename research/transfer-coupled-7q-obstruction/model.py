"""Transfer-coupled dual walks at seven queries (shared prefix, priced transfer).

Answers open question 1 of #2779 (independent-walks-7q): can a transfer-coupled
dual (shared prefix, priced transfer C>=1, divergent suffixes) undercut tariff
436 after charging walks+transfers+dirt at total Q=7?

Shapes (p,a,b) with p+a+b=7, p,a,b>=1, walks of lengths (p+a,p+b), dual
even-parity readout, fair shared-prefix XOR billing, transfer C>=1.

Self-contained relative to PR1898 / #2643 / #2686 / #2715 / #2761 / #2779.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from multiprocessing import Pool, cpu_count


def need(ok, message):
    if not ok:
        raise ValueError(message)


INF = 99

# Exact census results (machine-checked). Keys are "p_a_b".
EXPECTED = {
    "global_min_R": 84,
    "binding_shape": (5, 1, 1),
    "endpoint_tariff_Q6": 436,
    "tariff_floor_R84_X0_C1": 436,
    "transfer_C_min": 1,
    "F2_5_even_sum": 96,
    "shapes": {
        "1_1_5": {
            "covering": 3916416,
            "min_R": 92,
            "histogram": {"92": 1416576, "96": 1249920, "104": 1249920},
            "champion": {"prefix": [0], "suffix_a": [1], "suffix_b": [2, 4, 7, 8, 16]},
        },
        "1_2_4": {
            "covering": 10416000,
            "min_R": 98,
            "histogram": {"98": 3124800, "104": 7291200},
            "champion": {"prefix": [0], "suffix_a": [1, 2], "suffix_b": [4, 8, 13, 16]},
        },
        "1_3_3": {
            "covering": 7082880,
            "min_R": 100,
            "histogram": {"100": 1805440, "104": 4999680, "112": 277760},
            "champion": {"prefix": [0], "suffix_a": [1, 2, 4], "suffix_b": [7, 8, 16]},
        },
        "2_1_4": {
            "covering": 19165440,
            "min_R": 90,
            "histogram": {
                "90": 4583040,
                "92": 4999680,
                "96": 7082880,
                "100": 2499840,
            },
            "champion": {
                "prefix": [0, 7],
                "suffix_a": [1],
                "suffix_b": [2, 8, 11, 16],
            },
        },
        "2_2_3": {
            "covering": 39997440,
            "min_R": 94,
            "histogram": {
                "94": 7499520,
                "96": 17498880,
                "100": 14165760,
                "104": 833280,
            },
            "champion": {
                "prefix": [0, 7],
                "suffix_a": [1, 2],
                "suffix_b": [8, 12, 16],
            },
        },
        "3_1_3": {
            "covering": 37497600,
            "min_R": 88,
            "histogram": {
                "88": 6666240,
                "90": 7499520,
                "92": 7499520,
                "94": 9999360,
                "96": 5832960,
            },
            "champion": {
                "prefix": [0, 1, 8],
                "suffix_a": [2],
                "suffix_b": [4, 15, 16],
            },
        },
        "3_2_2": {
            "covering": 28748160,
            "min_R": 90,
            "histogram": {
                "90": 4374720,
                "92": 8124480,
                "94": 7499520,
                "96": 6249600,
                "98": 2499840,
            },
            "champion": {
                "prefix": [0, 1, 8],
                "suffix_a": [2, 4],
                "suffix_b": [15, 16],
            },
        },
        "4_1_2": {
            "covering": 36664320,
            "min_R": 86,
            "histogram": {
                "86": 5832960,
                "88": 3333120,
                "90": 9999360,
                "92": 15832320,
                "96": 1666560,
            },
            "champion": {
                "prefix": [0, 1, 2, 4],
                "suffix_a": [8],
                "suffix_b": [15, 16],
            },
        },
        "5_1_1": {
            "covering": 9166080,
            "min_R": 84,
            "histogram": {
                "84": 1458240,
                "88": 2083200,
                "90": 5208000,
                "96": 416640,
            },
            "champion": {
                "prefix": [0, 1, 2, 4, 8],
                "suffix_a": [15],
                "suffix_b": [16],
            },
        },
    },
}

# VERIFY live-computes these; independent.py live-computes the complement.
VERIFY_SHAPES = ((5, 1, 1), (4, 1, 2), (3, 1, 3), (2, 1, 4), (1, 1, 5))
INDEPENDENT_SHAPES = ((1, 2, 4), (1, 3, 3), (3, 2, 2), (2, 2, 3))

_CUR = None


def shape_key(p, a, b):
    return f"{p}_{a}_{b}"


def tariff_qrx(q, r, x, extra=0):
    """Abstract complete-call tariff at (b,a,x)=(38,2,2), plus optional extras."""
    leaves = 28 * q + r
    nodes = 9 * q
    dispatch = q + r + x
    return leaves + nodes + x + dispatch + extra


def tariff_with_transfer(q, r, x, c=1):
    """Charge transfer C like source-XOR units (contributes 2*C)."""
    need(c >= 1, "transfer C must be at least 1")
    return tariff_qrx(q, r, x, extra=2 * c)


def even_table(slots):
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
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


def support_of(even):
    costs = []
    masks = []
    for a, c in enumerate(even):
        if c < INF:
            costs.append(c)
            masks.append(a)
    return costs, masks


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


def dual_independent_R(e0, e1):
    costs, masks = support_of(e0)
    return dual_from_support(e1, costs, masks)


def dual_R_short_long(e_long, sigma):
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


def path_edges(seq):
    total = 0
    for a, b in zip(seq, seq[1:]):
        delta = a ^ b
        if delta == 0:
            return None
        total += 2 * (delta.bit_count() - 1)
    return total


def path_X(slots):
    return path_edges(slots + (0,))


def fair_shared_prefix_X(prefix, suffix_a, suffix_b):
    """Charge shared prefix edges once, then both divergent closed forks."""
    w0 = prefix + suffix_a
    w1 = prefix + suffix_b
    x0 = path_X(w0)
    x1 = path_X(w1)
    if x0 is None or x1 is None:
        return None
    if len(prefix) >= 2:
        xp = path_edges(prefix)
        if xp is None:
            return None
    else:
        xp = 0
    return x0 + x1 - xp


def walk_slots(prefix, suffix):
    return prefix + suffix


def valid_restored_walk(slots):
    if type(slots) is not tuple or not slots or slots[0] != 0:
        return False
    if len(slots) < 2:
        return False
    return path_X(slots) is not None


def even_sum_F2_5():
    """Σ_{v≠0} least_even_geq(wt(v)) over F2^5 = 96."""
    total = 0
    for v in range(1, 32):
        wt = v.bit_count()
        total += wt + (wt % 2)
    return total


def _handle_prefix(pref_nz):
    mode, p, a, b = _CUR
    if mode == "511":
        prefix = (0,) + pref_nz
        used = set(prefix)
        avail = [x for x in range(1, 32) if x not in used]
        tabs = []
        supports = []
        for s in avail:
            e = even_table(prefix + (s,))
            tabs.append(e)
            supports.append(support_of(e))
        hist = Counter()
        covering = 0
        min_r = 999
        wit = None
        n = len(avail)
        for i in range(n):
            e = tabs[i]
            if all(e[m] < INF for m in range(1, 32)):
                r = sum(e[1:])
                covering += 1
                hist[r] += 1
                if r < min_r:
                    min_r = r
                    wit = (list(prefix), [avail[i]], [avail[i]])
            sc, sm = supports[i]
            for j in range(i + 1, n):
                r = dual_from_support(tabs[j], sc, sm)
                if r is None:
                    continue
                covering += 1
                hist[r] += 1
                if r < min_r:
                    min_r = r
                    wit = (list(prefix), [avail[i]], [avail[j]])
        return covering, min_r, dict(hist), wit

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
    wit = None
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
                wit = (list(prefix), list(A), list(B))
    return covering, min_r, dict(hist), wit


def enumerate_shape(p, a, b, workers=None):
    """Census one transfer-coupled shape (p,a,b) with p+a+b=7."""
    need(p >= 1 and a >= 1 and b >= 1 and p + a + b == 7, "shape must partition 7")
    need(p + a >= 2 and p + b >= 2, "restored walks need length >= 2")
    global _CUR
    if p == 1 and a == 1:
        return _enumerate_115()
    if p == 1 and a == 2 and b == 4:
        return _enumerate_124()
    if p == 1 and a == 3 and b == 3:
        return _enumerate_133()

    mode = "511" if (p, a, b) == (5, 1, 1) else "g"
    _CUR = (mode, p, a, b)
    prefs = list(combinations(range(1, 32), p - 1))
    workers = workers or min(4, cpu_count() or 1)
    hist = Counter()
    covering = 0
    min_r = 999
    wit = None
    with Pool(processes=workers) as pool:
        for cov, mn, h, w in pool.imap_unordered(
            _handle_prefix, prefs, chunksize=max(1, len(prefs) // 32 or 1)
        ):
            covering += cov
            hist.update(h)
            if mn < min_r:
                min_r = mn
                wit = w
    return _pack_result(p, a, b, covering, hist, wit)


def _pack_result(p, a, b, covering, hist, wit):
    need(covering > 0, "expected covering schedules")
    return {
        "shape": [p, a, b],
        "Q": 7,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "champion": {
            "prefix": wit[0],
            "suffix_a": wit[1],
            "suffix_b": wit[2],
        }
        if wit
        else None,
    }


def _enumerate_115():
    """Shape (1,1,5): short (0,σ) vs long length-6; short dual formula."""
    hist = Counter()
    covering = 0
    wit = None
    tables = {
        nz: even_table((0,) + nz) for nz in combinations(range(1, 32), 5)
    }
    min_r = 999
    for sigma in range(1, 32):
        for nz, e_long in tables.items():
            r = dual_R_short_long(e_long, sigma)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
            if r < min_r:
                min_r = r
                wit = ([0], [sigma], list(nz))
    return _pack_result(1, 1, 5, covering, hist, wit)


def _enumerate_124():
    """Shape (1,2,4): short length-3 vs long length-5."""
    hist = Counter()
    covering = 0
    wit = None
    min_r = 999
    long_tabs = {
        nz: even_table((0,) + nz) for nz in combinations(range(1, 32), 4)
    }
    for short_nz in combinations(range(1, 32), 2):
        short = (0,) + short_nz
        costs, masks = support_of(even_table(short))
        for long_nz, e in long_tabs.items():
            r = dual_from_support(e, costs, masks)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
            if r < min_r:
                min_r = r
                wit = ([0], list(short_nz), list(long_nz))
    return _pack_result(1, 2, 4, covering, hist, wit)


def _enumerate_133():
    """Shape (1,3,3): two length-4 walks; unordered pairs."""
    hist = Counter()
    covering = 0
    wit = None
    min_r = 999
    tabs = {}
    for nz in combinations(range(1, 32), 3):
        e = even_table((0,) + nz)
        tabs[nz] = (e, support_of(e))
    keys = list(tabs.keys())
    for i, nz0 in enumerate(keys):
        e0, (sc, sm) = tabs[nz0]
        for nz1 in keys[i:]:
            e1, _ = tabs[nz1]
            r = dual_from_support(e1, sc, sm)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
            if r < min_r:
                min_r = r
                wit = ([0], list(nz0), list(nz1))
    return _pack_result(1, 3, 3, covering, hist, wit)


def champion_recompute(p, a, b):
    """Recompute dual R and fair X on the pinned champion (set order)."""
    rec = EXPECTED["shapes"][shape_key(p, a, b)]
    prefix = tuple(rec["champion"]["prefix"])
    suf_a = tuple(rec["champion"]["suffix_a"])
    suf_b = tuple(rec["champion"]["suffix_b"])
    need(len(prefix) == p and len(suf_a) == a and len(suf_b) == b, "champ shape")
    w0 = walk_slots(prefix, suf_a)
    w1 = walk_slots(prefix, suf_b)
    need(valid_restored_walk(w0) and valid_restored_walk(w1), "champ restored")
    r = dual_independent_R(even_table(w0), even_table(w1))
    need(r == rec["min_R"], f"champion R {r} != {rec['min_R']}")
    fx = fair_shared_prefix_X(prefix, suf_a, suf_b)
    need(fx is not None and fx >= 0, "fair X")
    tariff_floor = tariff_with_transfer(7, r, 0, c=1)
    tariff_live = tariff_with_transfer(7, r, fx, c=1)
    need(tariff_floor >= EXPECTED["endpoint_tariff_Q6"], "no undercut at X0")
    need(tariff_live >= tariff_floor, "live tariff")
    return {
        "shape": [p, a, b],
        "R": r,
        "fair_X": fx,
        "tariff_X0_C1": tariff_floor,
        "tariff_fair_X_C1": tariff_live,
        "walks": [list(w0), list(w1)],
    }


def check_result_against_expected(result):
    p, a, b = result["shape"]
    exp = EXPECTED["shapes"][shape_key(p, a, b)]
    need(result["covering_pairs"] == exp["covering"], "covering mismatch")
    need(result["min_R"] == exp["min_R"], "min_R mismatch")
    need(result["histogram"] == exp["histogram"], "histogram mismatch")
    need(result["min_R"] >= EXPECTED["global_min_R"], "below global floor")


def enumerate_shapes(shapes, workers=None):
    out = {}
    for p, a, b in shapes:
        result = enumerate_shape(p, a, b, workers=workers)
        check_result_against_expected(result)
        out[shape_key(p, a, b)] = result
    return out
