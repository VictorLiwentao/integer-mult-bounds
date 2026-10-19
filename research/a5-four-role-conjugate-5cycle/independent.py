#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent even-permutation / uv^T replay of the four-role A5 census."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

ROLES = 4
GROUP_ORDER = 60
EXPECTED_IDEM = 120
EXPECTED_CALLS = 240
NCELL = ROLES * ROLES
SHORT_DEPTH = 3
LAYER_SIZES = (1, 240, 37285, 5150035)
SEEN_TOTAL = 5187561
PRED_DIGEST = "9030f2eebc1fe7d848d7946a9c254306f7d0221fb68109e3b0d7c2dcb498e217"
X_PERM = (1, 0, 3, 2, 4)
Y_PERM = (2, 1, 4, 3, 0)
E_PERM = (0, 1, 2, 3, 4)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL_INDEPENDENT_A5_FOUR_ROLE_CONJUGATE: {message}")


def compose(a, b):
    return tuple(a[b[i]] for i in range(5))


def even_permutation(p) -> bool:
    inversions = sum(p[i] > p[j] for i in range(5) for j in range(i + 1, 5))
    return inversions % 2 == 0


def build_even_group():
    elements = tuple(
        sorted(p for p in itertools.permutations(range(5)) if even_permutation(p))
    )
    need(len(elements) == GROUP_ORDER, "even A5 order")
    index = {g: i for i, g in enumerate(elements)}
    table = tuple(tuple(index[compose(a, b)] for b in elements) for a in elements)
    return elements, index, table


def right_permute(mask: int, g: int, table) -> int:
    out = 0
    remaining = mask
    while remaining:
        bit = remaining & -remaining
        a = bit.bit_length() - 1
        out ^= 1 << table[a][g]
        remaining ^= bit
    return out


def rank_one_idempotents_uv():
    """Enumerate N=u v^T with v^T u=1; do not import primary CALLS."""
    out = []
    for u in range(1, 1 << ROLES):
        for v in range(1, 1 << ROLES):
            if ((u & v).bit_count() & 1) != 1:
                continue
            matrix = tuple(
                ((u >> row) & 1) & ((v >> col) & 1)
                for row in range(ROLES)
                for col in range(ROLES)
            )
            out.append((matrix, u, v))
    # Deduplicate by matrix; keep one (u,v) representative.
    by_matrix = {}
    for matrix, u, v in out:
        by_matrix.setdefault(matrix, (u, v))
    need(len(by_matrix) == EXPECTED_IDEM, "uv^T idempotent count")
    return sorted(by_matrix.items())


def main() -> int:
    elements, index, table = build_even_group()
    e = index[E_PERM]
    x = index[X_PERM]
    y = index[Y_PERM]
    xy = table[x][y]
    yx = table[y][x]

    lines = ["".join(map(str, element)) for element in elements]
    digest = hashlib.sha256("\n".join(lines).encode("ascii")).hexdigest()
    need(digest == PRED_DIGEST, "independent group digest")

    idem = rank_one_idempotents_uv()
    factors = []
    for _matrix, (u, v) in idem:
        for g in (x, y):
            factors.append((g, u, v))
    need(len(factors) == EXPECTED_CALLS, "factor count")

    def apply(state, g, u, v):
        cells = list(state)
        for row in range(ROLES):
            value = 0
            for middle in range(ROLES):
                if (u >> middle) & 1:
                    value ^= cells[ROLES * row + middle]
            delta = value ^ right_permute(value, g, table)
            for col in range(ROLES):
                if (v >> col) & 1:
                    cells[ROLES * row + col] ^= delta
        return tuple(cells)

    identity = tuple(1 << e if i % ROLES == i // ROLES else 0 for i in range(NCELL))
    target = list(identity)
    target[0] = 1 << xy
    target[ROLES + 1] = 1 << yx
    target = tuple(target)

    st = identity
    for g, u, v in (
        (x, 1, 1),
        (y, 1, 1),
        (y, 2, 2),
        (x, 2, 2),
    ):
        st = apply(st, g, u, v)
    need(st == target, "independent direct word")

    frontier = {identity}
    seen = {identity}
    layer_sizes = [1]
    hits = []
    for _depth in range(1, SHORT_DEPTH + 1):
        nxt = set()
        hit = 0
        for st0 in frontier:
            for g, u, v in factors:
                ns = apply(st0, g, u, v)
                if ns not in seen:
                    seen.add(ns)
                    nxt.add(ns)
                if ns == target:
                    hit += 1
        frontier = nxt
        layer_sizes.append(len(nxt))
        hits.append(hit)

    need(tuple(layer_sizes) == LAYER_SIZES, "independent layer sizes")
    need(hits == [0, 0, 0], "independent hits")
    need(len(seen) == SEEN_TOTAL, "independent seen total")

    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(cert["layer_sizes"] == layer_sizes, "certificate layer pin")
    need(cert["hits_by_depth"] == hits, "certificate hit pin")
    need(cert["result_minimum"] == 4, "certificate minimum")
    need(cert["dirty_lowers"] is False, "certificate dirty_lowers")

    print(
        "PASS_INDEPENDENT_A5_FOUR_ROLE_CONJUGATE "
        f"roles={ROLES} calls={EXPECTED_CALLS} target_minimum=4 "
        f"layers={layer_sizes} hits={hits} dirty_lowers=false no_new_kappa",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
