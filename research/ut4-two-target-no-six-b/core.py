#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Self-contained two-role UT4(F2) profile/key primitives for the n_b=6 census.

Reimplements the r=2 formulas of CrocSwap/integer-mult-bounds#1690
(research/ut4-two-target-r2/search.py) needed here: rank-one couplings,
side tables, transport keys, and GL2-minimal zero-sum middle sequences.
Does not import that module. Prepared by Wentao Li with substantial AI
assistance. Apache-2.0.
"""
import itertools

PAR = [bin(m).count("1") & 1 for m in range(64)]
_SOL = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def mm(A, B, r=2):
    out = 0
    for i in range(r):
        for j in range(r):
            s = 0
            for k in range(r):
                s ^= (A >> (i * r + k)) & (B >> (k * r + j)) & 1
            out |= s << (i * r + j)
    return out


def rank_one(x, y, r=2):
    return sum(
        1 << (i * r + j)
        for i in range(r)
        for j in range(r)
        if (x >> i) & 1 and (y >> j) & 1
    )


def split(N, r=2):
    rows = [(N >> (i * r)) & ((1 << r) - 1) for i in range(r)]
    y = next(v for v in rows if v)
    x = sum(1 << i for i, v in enumerate(rows) if v)
    need(all(v in (0, y) for v in rows) and rank_one(x, y, r) == N, "not rank one")
    return x, y


def diag(w, r):
    return sum(1 << (i * r + i) for i in range(w))


def couplings(r=2):
    return [(x, y) for x in range(1, 1 << r) for y in range(1, 1 << r)]


def gl(r=2):
    I = diag(r, r)
    inv = {}
    for g in range(1 << (r * r)):
        for h in range(1 << (r * r)):
            if mm(g, h, r) == I:
                inv[g] = h
    return inv


def side_tables(bseq, r=2):
    tab = []
    for j, N in enumerate(bseq):
        L = R = 0
        for i, M in enumerate(bseq):
            if i < j:
                L ^= M
            elif i > j:
                R ^= M
        tab.append([
            mm(p, N, r)
            | mm(N, p, r) << 4
            | mm(mm(p, N, r), p, r) << 8
            | (mm(mm(L, p, r), N, r) ^ mm(mm(N, p, r), R, r)) << 12
            for p in range(16)
        ])
    return tab


def side_coeffs(bseq, P, r=2):
    ab = ba = aba = bab = 0
    for j, (N, p) in enumerate(zip(bseq, P)):
        pn = mm(p, N, r)
        ab ^= pn
        ba ^= mm(N, p, r)
        aba ^= mm(pn, p, r)
        for k in range(j + 1, len(bseq)):
            bab ^= mm(mm(N, P[k] ^ p, r), bseq[k], r)
    return ab, ba, aba, bab


def cross_coeffs(bseq, P, Q, r=2):
    abc = cba = 0
    for N, p, q in zip(bseq, P, Q):
        abc ^= mm(mm(p, N, r), q, r)
        cba ^= mm(mm(q, N, r), p, r)
    return abc, cba


def key(bseq, P):
    U, W = [0, 0], [0, 0]
    for j, (N, p) in enumerate(zip(bseq, P)):
        x, y = split(N)
        for s in range(2):
            u = w = 0
            for k in range(2):
                u ^= (p >> (2 * s + k)) & (x >> k) & 1
                w ^= (y >> k) & (p >> (2 * k + s)) & 1
            U[s] |= u << j
            W[s] |= w << j
    return U[0], U[1], W[0], W[1]


def key_cross(kp, kq):
    abc = cba = 0
    for s in range(2):
        for t in range(2):
            abc |= PAR[kp[s] & kq[2 + t]] << (2 * s + t)
            cba |= PAR[kq[s] & kp[2 + t]] << (2 * s + t)
    return abc, cba


def _sol(u0, u1, e0, e1):
    k = (u0, u1, e0, e1)
    if k not in _SOL:
        _SOL[k] = [m for m in range(64) if PAR[u0 & m] == e0 and PAR[u1 & m] == e1]
    return _SOL[k]


def key_pairs(akeys, ckeys=None, target=(9, 9)):
    ckeys = akeys if ckeys is None else ckeys
    abc = target[0]
    byW = {}
    for k in ckeys:
        byW.setdefault(k[2:], []).append(k)
    for ka in akeys:
        for m0 in _sol(ka[0], ka[1], abc & 1, abc >> 2 & 1):
            for m1 in _sol(ka[0], ka[1], abc >> 1 & 1, abc >> 3 & 1):
                for kc in byW.get((m0, m1), ()):
                    if key_cross(ka, kc) == target:
                        yield ka, kc


def middle_sequences(nb=6, symmetric=True, r=2):
    inv = gl(r)
    R1 = sorted(rank_one(x, y, r) for x, y in couplings(r))
    for bt in itertools.product(R1, repeat=nb):
        tot = 0
        for N in bt:
            tot ^= N
        if tot:
            continue
        if symmetric and any(
            tuple(mm(mm(g, N, r), h, r) for N in bt) < bt for g, h in inv.items()
        ):
            continue
        yield bt


def ranks_XY(bseq, r=2):
    xs, ys = [], []
    for N in bseq:
        x, y = split(N, r)
        xs.append(x)
        ys.append(y)

    def rk(vecs):
        rows = list(vecs)
        rank = 0
        for bit in range(r):
            piv = None
            for i in range(rank, len(rows)):
                if rows[i] >> bit & 1:
                    piv = i
                    break
            if piv is None:
                continue
            rows[rank], rows[piv] = rows[piv], rows[rank]
            for i in range(len(rows)):
                if i != rank and rows[i] >> bit & 1:
                    rows[i] ^= rows[rank]
            rank += 1
        return rank

    return rk(xs), rk(ys)


def side_zero_keys(bseq):
    """Set of transport keys of all side-zero 6-profiles, via 3+3 MITM on keys."""
    need(len(bseq) == 6, "n_b=6 only")
    tab = side_tables(bseq)
    ktab = []
    for j, N in enumerate(bseq):
        x, y = split(N)
        row = []
        for p in range(16):
            du = [0, 0]
            dw = [0, 0]
            for s in range(2):
                u = w = 0
                for k in range(2):
                    u ^= (p >> (2 * s + k)) & (x >> k) & 1
                    w ^= (y >> k) & (p >> (2 * k + s)) & 1
                du[s] = u
                dw[s] = w
            row.append((du[0], du[1], dw[0], dw[1]))
        ktab.append(row)
    left = {}
    for p0 in range(16):
        for p1 in range(16):
            for p2 in range(16):
                v = tab[0][p0] ^ tab[1][p1] ^ tab[2][p2]
                u0 = ktab[0][p0][0] | (ktab[1][p1][0] << 1) | (ktab[2][p2][0] << 2)
                u1 = ktab[0][p0][1] | (ktab[1][p1][1] << 1) | (ktab[2][p2][1] << 2)
                w0 = ktab[0][p0][2] | (ktab[1][p1][2] << 1) | (ktab[2][p2][2] << 2)
                w1 = ktab[0][p0][3] | (ktab[1][p1][3] << 1) | (ktab[2][p2][3] << 2)
                left.setdefault(v, set()).add((u0, u1, w0, w1))
    keys = set()
    joins = 0
    for p3 in range(16):
        for p4 in range(16):
            for p5 in range(16):
                v = tab[3][p3] ^ tab[4][p4] ^ tab[5][p5]
                L = left.get(v)
                if not L:
                    continue
                ru0 = ktab[3][p3][0] | (ktab[4][p4][0] << 1) | (ktab[5][p5][0] << 2)
                ru1 = ktab[3][p3][1] | (ktab[4][p4][1] << 1) | (ktab[5][p5][1] << 2)
                rw0 = ktab[3][p3][2] | (ktab[4][p4][2] << 1) | (ktab[5][p5][2] << 2)
                rw1 = ktab[3][p3][3] | (ktab[4][p4][3] << 1) | (ktab[5][p5][3] << 2)
                for u0, u1, w0, w1 in L:
                    joins += 1
                    keys.add((u0 | (ru0 << 3), u1 | (ru1 << 3), w0 | (rw0 << 3), w1 | (rw1 << 3)))
    return keys, joins


def count_key_pairs(keys, target=(9, 9)):
    return sum(1 for _ in key_pairs(list(keys), list(keys), target))
