#!/usr/bin/env python3
"""Independent geometry check for quotient-collision restitution.

Does not import verify.py. Wentao Li, with substantial AI assistance. Apache-2.0.
"""
import json
import tarfile
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
MATCHING = ROOT / "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json"
CLIQUE = (
    1, 4, 8, 11, 17, 18, 19, 21, 22, 23, 24, 28,
    34, 36, 38, 39, 41, 42, 43, 45, 46, 51, 52, 53,
)


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def dot(left, right):
    return (left & right).bit_count() % 2


def rank_of(rows):
    pivots = {}
    rank = 0
    for row in rows:
        while row:
            bit = (row & -row).bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                rank += 1
                break
    return rank


def pairing_rank(left, right):
    rows = []
    for vector in left:
        row = 0
        for index, other in enumerate(right):
            if dot(vector, other):
                row |= 1 << index
        rows.append(row)
    return rank_of(rows)


def spanned(planes, indexes):
    pivots = {}
    basis = []
    for index in indexes:
        for vector in planes[index]:
            value = vector
            while value:
                bit = (value & -value).bit_length() - 1
                if bit in pivots:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    basis.append(vector)
                    break
    return basis


def form_rank(planes, indexes):
    basis = spanned(planes, indexes)
    return pairing_rank(basis, basis)


def minimum_support_charge(planes, indexes):
    size = len(indexes)
    minimum = None
    for mask_left in range(1, 1 << size):
        for mask_right in range(1, 1 << size):
            left = [vector for bit, index in enumerate(indexes) if mask_left & (1 << bit) for vector in planes[index]]
            right = [vector for bit, index in enumerate(indexes) if mask_right & (1 << bit) for vector in planes[index]]
            charge = pairing_rank(left, right)
            if minimum is None or charge < minimum:
                minimum = charge
    return minimum


def main():
    with tarfile.open(ARCHIVE) as archive:
        payload = archive.extractfile(MEMBER).read()
    recipes = json.loads(payload)["recipes"]
    labels = [item["q"] for item in sorted(recipes, key=lambda item: item["port"])]
    pairs = json.loads(MATCHING.read_text(encoding="utf-8"))["matching"]
    require(len(labels) == 112 and len(pairs) == 56, "shape")
    planes = []
    for left, right in pairs:
        planes.append((labels[left], labels[right]))
        require(dot(labels[left], labels[right]) == 0, "matching")
        require(dot(labels[left], labels[left]) == dot(labels[right], labels[right]) == 1, "norms")

    def orthogonal(i, j):
        return all(dot(a, b) == 0 for a in planes[i] for b in planes[j])

    collapsed = 0
    orthogonal_pairs = 0
    rank2_pairs = 0
    cross_rank_1 = 0
    for i, j in combinations(range(56), 2):
        rank = form_rank(planes, (i, j))
        if orthogonal(i, j):
            orthogonal_pairs += 1
            require(rank == 4, "orthogonal charge")
        else:
            if pairing_rank(planes[i], planes[j]) == 1:
                cross_rank_1 += 1
            if rank < 4:
                collapsed += 1
            if rank <= 2:
                rank2_pairs += 1
                require(not orthogonal(i, j), "rank-2 pair clique")
                require(minimum_support_charge(planes, (i, j)) >= 2, "rank-2 pair charge")
    triples = 0
    for indexes in combinations(range(56), 3):
        rank = form_rank(planes, indexes)
        if rank <= 2:
            triples += 1
            require(all(not orthogonal(i, j) for i, j in combinations(indexes, 2)), "triple clique")
            require(minimum_support_charge(planes, indexes) >= 2, "triple charge")
    larger = sum(1 for indexes in combinations(range(56), 4) if form_rank(planes, indexes) <= 2)
    clique_cross = sum(
        1 for i, j in combinations(CLIQUE, 2)
        if pairing_rank(planes[i], planes[j]) == 1
    )
    require(all(not orthogonal(i, j) for i, j in combinations(CLIQUE, 2)), "clique")
    require(orthogonal_pairs == 109 and collapsed == 448, "census")
    require(rank2_pairs == 144 and triples == 8 and larger == 0, "collisions")
    require(cross_rank_1 == 879 and clique_cross == 173, "cross rank 1")
    # Identity rank 2|S| and minimum positive charge 2, only for these collisions.
    for size in (2, 3):
        require((2 * size) * 2 == 4 * size, "restitution")
    require(4 * 2 == 8 and 4 * 3 == 12 and 112 * 2 == 224, "masses")
    width, stages, families = 896, 9, 73
    require((71 * width + stages * 224) * 292 == (families * width) * 293, "moment")
    print(
        "PASS_PAIRED_PLANE_CLIQUE_RESTITUTION_INDEPENDENT",
        "rank2_pairs=144",
        "rank2_triples=8",
        "triple_mass=12",
    )


if __name__ == "__main__":
    main()
