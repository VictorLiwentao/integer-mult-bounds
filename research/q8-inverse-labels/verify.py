"""Exact paid-call minima for Q8 targets with inverse labels in formal F2[Q8].

Changed alphabet relative to CrocSwap/integer-mult-bounds#1822: paid labels are
x=i, x^{-1}=-i, y=j, y^{-1}=-j (24 generators at r=2), not only x,y. Targets
diag([z],[z]) and diag([xy],[yx]) with z=xyxy=x^2=y^2=-1. Free scalar GL_2(F2)
mixing is normalized by augmentation (predecessor argument; closure checked).

Engine A (BFS): formal 2x2 matrices over F2[Q8] with 8-bit coefficient masks.
Engine B (independent): frozenset formal matrices and Hamilton 4-tuple
quaternion multiplication. Acceptance is equality in every coefficient of the
full group algebra.

Stdlib only. python -I -O -B research/q8-inverse-labels/verify.py
"""
import hashlib
import json
import os
import sys

# ---------------------------------------------------------------- Q8, engine A
# element index = 4*sign + unit: 0=+1, 1=+i, 2=+j, 3=+k, 4=-1, 5=-i, 6=-j, 7=-k
_UNIT_MUL = [
    [0, 1, 2, 3],
    [1, 0, 3, 2],
    [2, 3, 0, 1],
    [3, 2, 1, 0],
]
_UNIT_SIGN = [
    [0, 0, 0, 0],
    [0, 1, 0, 1],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
]


def qmul(a, b):
    sa, ua = divmod(a, 4)
    sb, ub = divmod(b, 4)
    s = (sa + sb + _UNIT_SIGN[ua][ub]) & 1
    return 4 * s + _UNIT_MUL[ua][ub]


G_TAB = [[qmul(a, b) for b in range(8)] for a in range(8)]

MASK_MUL = [[0] * 256 for _ in range(256)]
for _a in range(256):
    for _b in range(256):
        _r = 0
        _bb = _b
        while _bb:
            _lb = _bb & -_bb
            _h = _lb.bit_length() - 1
            _aa = _a
            while _aa:
                _la = _aa & -_aa
                _g = _la.bit_length() - 1
                _r ^= 1 << G_TAB[_g][_h]
                _aa ^= _la
            _bb ^= _lb
        MASK_MUL[_a][_b] = _r


def mat_mul(A, B, r):
    C = [0] * (r * r)
    for i in range(r):
        for k in range(r):
            a = A[i * r + k]
            if a:
                m = MASK_MUL[a]
                for j in range(r):
                    C[i * r + j] ^= m[B[k * r + j]]
    return tuple(C)


def identity_state(r):
    return tuple(1 if i == j else 0 for i in range(r) for j in range(r))


def gen_state(g, N, r):
    lab = (1 << g) | 1
    cells = [0] * (r * r)
    for idx, bit in enumerate(N):
        if bit:
            cells[idx] ^= lab
    for i in range(r):
        cells[i * r + i] ^= 1
    return tuple(cells)


def diag_state(entries, r):
    cells = [0] * (r * r)
    for i, g in enumerate(entries):
        cells[i * r + i] = 1 << g
    return tuple(cells)


def rank_one_idempotents(r):
    out = []
    for u in range(1, 1 << r):
        for v in range(1, 1 << r):
            if (u & v).bit_count() & 1:
                N = tuple(
                    ((u >> i) & 1) * ((v >> j) & 1)
                    for i in range(r)
                    for j in range(r)
                )
                out.append((u, v, N))
    out.sort()
    return out


def bfs_ball(gens, r, max_depth):
    I0 = identity_state(r)
    seen = {I0: 0}
    parents = {I0: None}
    layers = [[I0]]
    frontier = [I0]
    for _d in range(1, max_depth + 1):
        nxt = []
        for s in frontier:
            for gi, g in enumerate(gens):
                t = mat_mul(g, s, r)
                if t not in seen:
                    seen[t] = _d
                    parents[t] = (s, gi)
                    nxt.append(t)
        layers.append(nxt)
        frontier = nxt
        if not frontier:
            break
    return layers, parents


def state_digest(layers):
    h = hashlib.sha256()
    for layer in layers:
        for s in sorted(layer):
            h.update(bytes(s))
    return h.hexdigest()


def word_to(parents, target):
    if target not in parents:
        return None
    word = []
    s = target
    while parents[s] is not None:
        s, gi = parents[s]
        word.append(gi)
    return list(reversed(word))


def product_equals(gens, word, r, T):
    acc = identity_state(r)
    for gi in word:
        acc = mat_mul(gens[gi], acc, r)
    return acc == T


# ------------------------------------------------- engine B (independent replay)
def ham_mul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    )


_HAM = [
    (1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1),
    (-1, 0, 0, 0),
    (0, -1, 0, 0),
    (0, 0, -1, 0),
    (0, 0, 0, -1),
]
_HAM_TO_IDX = {t: i for i, t in enumerate(_HAM)}


def ham_index(a, b):
    return _HAM_TO_IDX[ham_mul(_HAM[a], _HAM[b])]


def b_mat_mul(A, B, r):
    C = [set() for _ in range(r * r)]
    for i in range(r):
        for k in range(r):
            if A[i * r + k]:
                for j in range(r):
                    if B[k * r + j]:
                        base = C[i * r + j]
                        for ga in A[i * r + k]:
                            for gb in B[k * r + j]:
                                gh = ham_index(ga, gb)
                                if gh in base:
                                    base.remove(gh)
                                else:
                                    base.add(gh)
    return tuple(frozenset(s) for s in C)


def b_state(g, N, r):
    lab = {g, 0}
    cells = [set() for _ in range(r * r)]
    for idx, bit in enumerate(N):
        if bit:
            cells[idx] ^= lab
    for i in range(r):
        cells[i * r + i] ^= {0}
    return tuple(frozenset(s) for s in cells)


def b_diag(entries, r):
    cells = [frozenset() for _ in range(r * r)]
    for i, g in enumerate(entries):
        cells[i * r + i] = frozenset({g})
    return tuple(cells)


def replay_word(gens_b, word, r):
    acc = tuple(
        frozenset({0}) if i == j else frozenset()
        for i in range(r)
        for j in range(r)
    )
    for gi in word:
        acc = b_mat_mul(gens_b[gi], acc, r)
    return acc


# ------------------------------------------------------- GL_2(F2) normalisation
def det2(M, r):
    if r == 2:
        return M[0] * M[3] ^ M[1] * M[2]
    raise ValueError("this package only uses r=2")


def gl_elements(r):
    out = []
    for bits in range(1 << (r * r)):
        M = tuple((bits >> t) & 1 for t in range(r * r))
        if det2(M, r):
            out.append(M)
    return out


def gl_invert(M, r):
    a = [list(M[i * r:(i + 1) * r]) for i in range(r)]
    inv = [[1 if i == j else 0 for j in range(r)] for i in range(r)]
    for col in range(r):
        piv = next(rw for rw in range(col, r) if a[rw][col])
        a[col], a[piv] = a[piv], a[col]
        inv[col], inv[piv] = inv[piv], inv[col]
        for rw in range(r):
            if rw != col and a[rw][col]:
                for k in range(r):
                    a[rw][k] ^= a[col][k]
                    inv[rw][k] ^= inv[col][k]
    return tuple(x for row in inv for x in row)


def expect(name, cond, msg=""):
    if not cond:
        print("FAIL", name, msg)
        raise SystemExit(1)


def group_laws():
    for a in range(8):
        for b in range(8):
            for c in range(8):
                expect("assoc", qmul(qmul(a, b), c) == qmul(a, qmul(b, c)))
    for a in range(8):
        for b in range(8):
            expect("ham-agree", ham_index(a, b) == qmul(a, b))
    x, y, z = 1, 2, 4
    xi, yi = 5, 6
    expect("x2=z", qmul(x, x) == z)
    expect("y2=z", qmul(y, y) == z)
    expect("xi2=z", qmul(xi, xi) == z)
    expect("yi2=z", qmul(yi, yi) == z)
    expect("x*xi=e", qmul(x, xi) == 0)
    expect("y*yi=e", qmul(y, yi) == 0)
    expect("xyxy=z", qmul(qmul(qmul(x, y), x), y) == z)
    expect("z2=e", qmul(z, z) == 0)
    for a in range(8):
        expect("z-central", qmul(z, a) == qmul(a, z))
    expect("commutator", qmul(qmul(qmul(x, y), xi), yi) == z)


def main():
    group_laws()
    r = 2
    idem = rank_one_idempotents(r)
    expect("idem-count", len(idem) == 6, str(len(idem)))
    for u, v, N in idem:
        expect("idempotent", mat_mul(N, N, r) == N)

    x, y, xi, yi, z = 1, 2, 5, 6, 4
    labels = (x, xi, y, yi)
    here = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(here, "CERTIFICATE.json")

    gen_triples = [[g, u, v] for g in labels for (u, v, N) in idem]
    gens = [gen_state(g, N, r) for g in labels for (u, v, N) in idem]
    expect("gen-count", len(gens) == 24, str(len(gens)))

    # Positive-only alphabet is a proper subset (control that inverses enlarge).
    pos_gens = {gen_state(g, N, r) for g in (x, y) for (u, v, N) in idem}
    expect("pos-subset", len(pos_gens) == 12)
    expect("inverses-enlarge", not set(gens).issubset(pos_gens))
    expect("pos-inside", pos_gens.issubset(set(gens)))

    for g_lbl, u, v in gen_triples:
        N = next(N for (u2, v2, N) in idem if (u2, v2) == (u, v))
        expect(
            "D-square",
            mat_mul(gen_state(g_lbl, N, r), gen_state(g_lbl, N, r), r)
            == gen_state(qmul(g_lbl, g_lbl), N, r),
        )

    gls = gl_elements(r)
    gen_set = set(gens)
    for S in gls:
        Sinv = gl_invert(S, r)
        for g in gens:
            conj = mat_mul(mat_mul(S, g, r), Sinv, r)
            expect("gl-closure", conj in gen_set)
    expect("gl-order", len(gls) == 6)

    depth = 4
    layers, parents = bfs_ball(gens, r, depth)
    layer_sizes = [len(L) for L in layers]
    ball_sha = state_digest(layers)

    T_zz = diag_state([z, z], r)
    T_xy = diag_state([qmul(x, y), qmul(y, x)], r)
    C0 = identity_state(r)
    Cx = diag_state([x, 0], r)
    Cz = diag_state([z, 0], r)
    Cxi = diag_state([xi, 0], r)

    expect("control-I", word_to(parents, C0) == [])
    w_Cx = word_to(parents, Cx)
    w_Cxi = word_to(parents, Cxi)
    w_Cz = word_to(parents, Cz)
    expect("control-x", w_Cx is not None and len(w_Cx) == 1, str(w_Cx))
    expect("control-xi", w_Cxi is not None and len(w_Cxi) == 1, str(w_Cxi))
    expect("control-z", w_Cz is not None and len(w_Cz) == 2, str(w_Cz))

    # Depth-3 ball must miss both pair targets (no word of length <= 3).
    layers3, parents3 = bfs_ball(gens, r, 3)
    expect("depth3-miss-zz", word_to(parents3, T_zz) is None)
    expect("depth3-miss-xy", word_to(parents3, T_xy) is None)
    expect("depth3-layers", [len(L) for L in layers3] == layer_sizes[:4])

    idx = {tuple(t): i for i, t in enumerate(gen_triples)}

    def direct_pair(entries, square_label=None):
        word = []
        sq = x if square_label is None else square_label
        letters = {
            z: [sq, sq],
            x: [x],
            y: [y],
            xi: [xi],
            yi: [yi],
            qmul(x, y): [x, y],
            qmul(y, x): [y, x],
        }
        for pos, g in enumerate(entries):
            if g == 0:
                continue
            u = v = 1 << pos
            for let in letters[g]:
                word.append(idx[(let, u, v)])
        return list(reversed(word))

    direct = {
        "diag_z_z_r2": direct_pair([z, z]),
        "diag_xy_yx_r2": direct_pair([qmul(x, y), qmul(y, x)]),
        "diag_z_z_r2_via_inverses": direct_pair([z, z], square_label=xi),
    }

    targets = {
        "diag_z_z_r2": T_zz,
        "diag_xy_yx_r2": T_xy,
    }

    endpoints = {}
    gens_b = [b_state(g, N, r) for g in labels for (u, v, N) in idem]
    Tb = {
        "diag_z_z_r2": b_diag([z, z], r),
        "diag_xy_yx_r2": b_diag([qmul(x, y), qmul(y, x)], r),
    }

    expect("direct-zz", product_equals(gens, direct["diag_z_z_r2"], r, T_zz))
    expect(
        "direct-zz-inv",
        product_equals(gens, direct["diag_z_z_r2_via_inverses"], r, T_zz),
    )
    expect("direct-xy", product_equals(gens, direct["diag_xy_yx_r2"], r, T_xy))

    for name, T in targets.items():
        w = word_to(parents, T)
        expect("reachable-" + name, w is not None)
        expect("exact-distance-" + name, len(w) == 4, str(w))
        expect("direct-len-" + name, len(direct[name]) == 4)
        endpoints[name] = dict(
            minimum=4,
            witness=w,
            direct=direct[name],
            proven=(
                "complete BFS to depth 3 excludes words of length <= 3; "
                "BFS distance 4 equals the direct bill"
            ),
            registers=2,
        )
        expect("indep-witness", replay_word(gens_b, w, r) == Tb[name], name)
        expect("indep-direct", replay_word(gens_b, direct[name], r) == Tb[name], name)
        for pos in range(len(w)):
            sub = w[:pos] + w[pos + 1:]
            expect(
                "omission",
                not product_equals(gens, sub, r, T),
                f"{name} del {pos}",
            )

    expect(
        "indep-via-inv",
        replay_word(gens_b, direct["diag_z_z_r2_via_inverses"], r) == Tb["diag_z_z_r2"],
    )

    mut = list(T_zz)
    mut[0] ^= 1
    mut = tuple(mut)
    expect("mutated-not-target", mut != T_zz)
    expect(
        "mutated-witness-fails",
        not product_equals(gens, endpoints["diag_z_z_r2"]["witness"], r, mut),
    )

    out = dict(
        status="PASS_Q8_INVERSE_LABELS",
        group_order=8,
        paid_labels=["x=i", "x_inv=-i", "y=j", "y_inv=-j"],
        generator_count=24,
        endpoints=endpoints,
        via_inverses_direct=direct["diag_z_z_r2_via_inverses"],
        layers=layer_sizes,
        depth3_layers=[len(L) for L in layers3],
        ball_sha256=ball_sha,
        depth3_ball_sha256=state_digest(layers3),
        generators=gen_triples,
        gl2_order=len(gls),
        omission_controls=sum(len(v["witness"]) for v in endpoints.values()),
        controls=5,
        independent_engine_b=True,
        new_kappa=False,
        alphabet_change=(
            "Adds inverse paid labels x^{-1}, y^{-1} to the Q8 pair model of "
            "CrocSwap/integer-mult-bounds#1822; exact minima remain 4."
        ),
    )

    if "--emit" in sys.argv:
        with open(cert_path, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print("EMITTED", cert_path)

    with open(cert_path, "r", encoding="utf-8") as fh:
        cert = json.load(fh)
    for key, val in out.items():
        expect(
            "cert-" + key,
            cert.get(key) == val,
            f"{key}: cert={cert.get(key)!r} got={val!r}",
        )

    print(
        "PASS_Q8_INVERSE_LABELS",
        " ".join(f"{k}:{v['minimum']}" for k, v in endpoints.items()),
        f"layers={layer_sizes}",
        "gens=24",
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
