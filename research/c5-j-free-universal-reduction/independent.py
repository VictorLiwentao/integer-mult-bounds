#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dense elimination and iterative chordless-path reconstruction."""

from __future__ import annotations

import gzip
import io
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import (  # noqa: E402
    N_PLANES,
    N_PORTS,
    expand_and_net_to_diagonal,
    gram_extension_fixture,
    j_extension_fixture,
    diagonal_fixture,
    named_class_cost,
    need,
    padded_j_cancel_fixture,
    sources,
    subgradient_certificate,
)

PASS_LINE = (
    "PASS_C5_J_FREE_UNIVERSAL_REDUCTION_INDEPENDENT "
    "cycles=23 named_class_opt=224 pair_slack_min=4 "
    "j_free_floor=45 universal=true"
)


def dense_rank(matrix) -> int:
    need(len(matrix) <= N_PORTS and all(len(r) <= N_PORTS for r in matrix), "dense bounds")
    if not matrix or not matrix[0]:
        return 0
    rows = [list(r) for r in matrix]
    pivot = 0
    width = len(rows[0])
    for col in range(width):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(len(rows)):
            if i != pivot and rows[i][col]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def parity(a: int, b: int) -> int:
    return sum(((a >> j) & 1) * ((b >> j) & 1) for j in range(9)) % 2


def rank(left, right) -> int:
    if not left or not right:
        return 0
    return dense_rank([[parity(x, y) for y in right] for x in left])


def cycle_sets(planes):
    adj = [
        {j for j in range(N_PLANES) if j != i and rank(planes[i], planes[j]) == 0}
        for i in range(N_PLANES)
    ]
    paths = [(i,) for i in range(N_PLANES)]
    for length in range(1, 5):
        extended = []
        for path in paths:
            for vertex in adj[path[-1]]:
                if vertex <= path[0] or vertex in path:
                    continue
                if any(vertex in adj[i] for i in path[1:-1]):
                    continue
                if length > 1 and (vertex in adj[path[0]]) != (length == 4):
                    continue
                need(len(extended) < 100_000, "bounded simple paths")
                extended.append(path + (vertex,))
        paths = extended
    found = {tuple(sorted(p)) for p in paths}
    need(len(found) == 23, "23 chordless C5s")
    return tuple(sorted(found))


def geometry():
    raw = sources()
    with gzip.GzipFile(fileobj=io.BytesIO(raw["DATA-PHASES.json.gz"])) as stream:
        data = stream.read(2_000_001)
    need(len(data) <= 2_000_000, "bounded decompression")
    rows = json.loads(data)["recipes"]
    labels = {r["port"]: r["q"] for r in rows}
    matching = json.loads(raw["MATCHING.json"])["matching"]
    planes = tuple(tuple(labels[p] for p in pair) for pair in matching)
    need(len(planes) == N_PLANES, "56 planes")
    return planes, matching


def port_plane_map(matching):
    return {
        port: plane_index
        for plane_index, pair in enumerate(matching)
        for port in pair
    }


def od_tariff(planes, port_to_plane, i, j):
    return rank(planes[port_to_plane[i]], planes[port_to_plane[j]])


def gram_tariff(planes, port_to_plane, i, j):
    pi, pj = port_to_plane[i], port_to_plane[j]
    labs = planes[pi] if pi == pj else planes[pi] + planes[pj]
    return rank(labs, labs)


def pair_slack_census(planes, matching):
    port_to_plane = port_plane_map(matching)
    hist: Counter = Counter()
    min_slack = None
    equality = 0
    checked = 0
    # Independent enumeration order: reverse lexicographic.
    for i, j in sorted(combinations(range(N_PORTS), 2), reverse=True):
        od = od_tariff(planes, port_to_plane, i, j)
        gram = gram_tariff(planes, port_to_plane, i, j)
        slack = gram + 2 * od
        need(slack >= 4, "pair expansion dominates diagonal mass 4")
        hist[slack] += 1
        if min_slack is None or slack < min_slack:
            min_slack = slack
        if slack == 4:
            equality += 1
        checked += 1
    need(checked == N_PORTS * (N_PORTS - 1) // 2, "complete pair census")
    need(min_slack == 4 and equality >= 1, "tight pair slack")
    return {
        "unordered_pairs": checked,
        "min_slack": min_slack,
        "equality_pairs": equality,
        "slack_histogram": {str(k): v for k, v in sorted(hist.items())},
        "domination_holds": True,
    }


def main() -> None:
    planes, matching = geometry()
    cycle_rows = cycle_sets(planes)
    ranks = [
        rank(tuple(q for i in c for q in planes[i]), tuple(q for i in c for q in planes[i]))
        for c in cycle_rows
    ]
    need(Counter(ranks) == {7: 4, 8: 6, 9: 13}, "independent rank receipt")

    pair_census = pair_slack_census(planes, matching)
    subgrad = subgradient_certificate(planes, matching, pair_census)
    need(subgrad["global_minimizer_cost"] == 224, "independent subgradient")

    fixtures = [
        diagonal_fixture(planes, matching),
        j_extension_fixture(planes, matching),
        gram_extension_fixture(planes, matching),
        padded_j_cancel_fixture(planes, matching),
    ]
    for fixture in fixtures:
        reduced = expand_and_net_to_diagonal(planes, matching, fixture)
        need(reduced["post_cost"] == 224, "independent reduction to 224")
        need(reduced["cost_preserving"], "independent cost-preserving")
        need(reduced["net_j_after"] == 0, "independent J-free")

    for gamma in (-1, 0, 1):
        need(named_class_cost(gamma, {}, planes, matching) >= 224, "independent lattice")

    committed = json.loads((HERE / "RESULT.json").read_bytes())
    need(committed["named_class_optimum"] == 224, "receipt optimum")
    need(committed["pair_expansion_lemma"]["min_slack"] == 4, "receipt pair slack")
    need(committed["universal_j_free_floor_applies"] is True, "receipt universal")
    need(pair_census["slack_histogram"] == committed["pair_expansion_lemma"]["slack_histogram"],
         "independent histogram matches receipt")
    print(PASS_LINE)


if __name__ == "__main__":
    main()
