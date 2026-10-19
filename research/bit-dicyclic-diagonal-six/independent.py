#!/usr/bin/env python3
"""Independent depth-six Dic_3 diagonal census (suffix-first bit-mask MITM).

Reimplements the group algebra and search without importing search.py.
Joins by iterating suffixes first; search.py iterates prefixes first.
Admission uses need() so -O still enforces gates.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import deque
from hashlib import sha256
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = (
    "PASS_INDEPENDENT_BIT_DICYCLIC_DIAGONAL_SIX "
    "group=Dic_3 products=94727 eligible=890 hits=0 misses=890 no_new_kappa"
)
N_GROUP = 12
RING_ONE = 1
GENERATORS = (1, 6)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def group_mul(x, y):
    i, j = x % 6, x // 6
    k, ell = y % 6, y // 6
    out_i = (i + (-1 if j else 1) * k + (3 if j and ell else 0)) % 6
    return out_i + 6 * ((j + ell) % 2)


GROUP_TABLE = tuple(tuple(group_mul(x, y) for y in range(N_GROUP)) for x in range(N_GROUP))
GROUP_INVERSE = tuple(
    next(y for y in range(N_GROUP) if GROUP_TABLE[x][y] == 0 and GROUP_TABLE[y][x] == 0)
    for x in range(N_GROUP)
)


def ring_mul(x, y):
    out = 0
    while x:
        xb = x & -x
        i = xb.bit_length() - 1
        x ^= xb
        yy = y
        while yy:
            yb = yy & -yy
            j = yb.bit_length() - 1
            yy ^= yb
            out ^= 1 << GROUP_TABLE[i][j]
    return out


IDENTITY = (RING_ONE, 0, 0, 0, RING_ONE, 0, 0, 0, RING_ONE)


def mat_mul(a, b):
    return tuple(
        ring_mul(a[3 * i + 0], b[0 + j])
        ^ ring_mul(a[3 * i + 1], b[3 + j])
        ^ ring_mul(a[3 * i + 2], b[6 + j])
        for i in range(3)
        for j in range(3)
    )


def projector_rows():
    result = []
    for x in range(1, 8):
        for y in range(1, 8):
            if (x & y).bit_count() & 1:
                result.append(
                    tuple(((x >> i) & 1) * ((y >> j) & 1) for i in range(3) for j in range(3))
                )
    need(len(result) == 28 and len(set(result)) == 28, "28 idempotents")
    return result


def paid_matrix(g, n):
    delta = (1 << g) ^ RING_ONE
    return tuple(IDENTITY[k] ^ (delta if n[k] else 0) for k in range(9))


PROJECTORS = projector_rows()
OP_MATS = []
OP_INVS = []
for g in GENERATORS:
    for n in PROJECTORS:
        OP_MATS.append(paid_matrix(g, n))
        OP_INVS.append(paid_matrix(GROUP_INVERSE[g], n))
need(len(OP_MATS) == 56, "56 ops")


def word_product(word):
    out = IDENTITY
    for i in word:
        out = mat_mul(out, OP_MATS[i])
    return out


def inverse_word_product(word):
    out = IDENTITY
    for i in reversed(word):
        out = mat_mul(out, OP_INVS[i])
    return out


def word_distances():
    dist = {0: 0}
    queue = deque([0])
    while queue:
        x = queue.popleft()
        for g in GENERATORS:
            y = GROUP_TABLE[x][g]
            if y not in dist:
                dist[y] = dist[x] + 1
                queue.append(y)
    need(len(dist) == N_GROUP, "reach Dic_3")
    return dist


DIST = word_distances()


def target_matrix(w):
    out = [0] * 9
    for i, g in enumerate(w):
        out[3 * i + i] = 1 << g
    return tuple(out)


def left_monomial_shift(mask, g):
    """Left multiply a coefficient mask by group element g: [g] * sum a_i [i]."""
    out = 0
    while mask:
        b = mask & -mask
        i = b.bit_length() - 1
        mask ^= b
        out ^= 1 << GROUP_TABLE[g][i]
    return out


# LEFT_SHIFT[mask][g] = left_monomial_shift(mask, g)
LEFT_SHIFT = tuple(
    tuple(left_monomial_shift(mask, g) for g in range(N_GROUP))
    for mask in range(1 << N_GROUP)
)


def all_products(max_depth):
    result = {IDENTITY: ()}
    frontier = {IDENTITY: ()}
    by_depth = [1]
    for _ in range(max_depth):
        nxt = {}
        for mat, word in frontier.items():
            for i, op in enumerate(OP_MATS):
                product = mat_mul(mat, op)
                if product not in result:
                    rep = word + (i,)
                    result[product] = rep
                    nxt[product] = rep
        by_depth.append(len(nxt))
        frontier = nxt
        if not frontier:
            break
    return result, by_depth


def main():
    products, by_depth = all_products(3)
    need(by_depth == [1, 56, 2352, 92318], "depth hist")
    need(len(products) == 94727, "product count")

    # Suffix-first: for each target and each suffix Q, ask whether
    # T Q^{-1} is a known prefix product (same identity as prefix-first).
    suffix_rows = [(inverse_word_product(w), w) for w in products.values()]

    hits = 0
    misses = 0
    endpoint_count = 0
    hit_tuples = []
    miss_tuples = []
    for w in itertools.product(range(N_GROUP), repeat=3):
        direct = DIST[w[0]] + DIST[w[1]] + DIST[w[2]]
        if direct < 7:
            continue
        endpoint_count += 1
        t = target_matrix(w)
        # (T Q^{-1})_{ij} = left_shift(Q^{-1}_{ij}, w_i) for diagonal monomial T.
        w0, w1, w2 = w
        found = False
        for qinv, qword in suffix_rows:
            needed = (
                LEFT_SHIFT[qinv[0]][w0], LEFT_SHIFT[qinv[1]][w0], LEFT_SHIFT[qinv[2]][w0],
                LEFT_SHIFT[qinv[3]][w1], LEFT_SHIFT[qinv[4]][w1], LEFT_SHIFT[qinv[5]][w1],
                LEFT_SHIFT[qinv[6]][w2], LEFT_SHIFT[qinv[7]][w2], LEFT_SHIFT[qinv[8]][w2],
            )
            pword = products.get(needed)
            if pword is None:
                continue
            if len(pword) + len(qword) > 6:
                continue
            full = pword + qword
            need(word_product(full) == t, "independent replay")
            found = True
            break
        if found:
            hits += 1
            hit_tuples.append(list(w))
        else:
            misses += 1
            miss_tuples.append(list(w))

    need(endpoint_count == 890, "890 eligible")
    need(hits == 0 and misses == 890, "zero hits")
    coverage = {
        "max_calls": 6,
        "minimum_direct_bill": 7,
        "endpoint_count": endpoint_count,
        "targets_with_word_at_most_cap": hits,
        "targets_without_word_at_most_cap": misses,
        "hit_tuples": hit_tuples,
        "miss_tuples": miss_tuples,
    }
    digest = sha256(json.dumps(coverage, separators=(",", ":")).encode()).hexdigest()
    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(digest == cert["depth_six_layer"]["coverage_sha256"], "coverage digest")
    need(cert["no_new_kappa"] is True, "kappa")
    print(MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
