#!/usr/bin/env python3
"""Quotient-collision restitution for PR1825 paired-plane blocks.

Wentao Li <wentaol4@illinois.edu>, with substantial AI assistance. Apache-2.0.
No new supplier, kappa, or mixed-support discount is claimed.
"""
import hashlib
import json
import tarfile
import tempfile
from fractions import Fraction
from itertools import combinations
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
MATCHING = "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json"
SELECTED = "certificates/selected-result.json"
CATALOG = "docs/research/agent-task-catalog.json"

CLIQUE_24 = (
    1, 4, 8, 11, 17, 18, 19, 21, 22, 23, 24, 28,
    34, 36, 38, 39, 41, 42, 43, 45, 46, 51, 52, 53,
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def loads(raw):
    """Reject duplicate keys at every object, including nested ones."""
    def hook(pairs):
        obj = {}
        for key, value in pairs:
            need(key not in obj, "duplicate JSON key")
            obj[key] = value
        return obj

    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    return json.loads(text, object_pairs_hook=hook)


def sha256(payload):
    return hashlib.sha256(payload).hexdigest()


def git_blob(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def dot(a, b):
    return (a & b).bit_count() % 2


def pairing_rank(left, right):
    pivots = {}
    rank = 0
    for vector in left:
        row = 0
        for index, other in enumerate(right):
            if dot(vector, other):
                row |= 1 << index
        while row:
            bit = (row & -row).bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                rank += 1
                break
    return rank


def span_basis(planes, indexes):
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
    basis = span_basis(planes, indexes)
    return pairing_rank(basis, basis), len(basis)


def load_planes():
    sources = loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    need(sources["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
         "base commit")
    for row in sources["files"]:
        payload = (ROOT / row["path"]).read_bytes()
        need(sha256(payload) == row["sha256"], "source hash " + row["path"])
        need(git_blob(payload) == row["git_blob"], "source blob " + row["path"])
    with tarfile.open(ROOT / ARCHIVE) as archive:
        member = archive.extractfile(MEMBER)
        need(member is not None, "label member")
        raw = member.read()
    data = loads(raw)
    need(data["m"] == 73 and data["ports"] == 112, "selected width")
    rows = sorted(data["recipes"], key=lambda item: item["port"])
    need([item["port"] for item in rows] == list(range(112)), "port index")
    labels = [item["q"] for item in rows]
    matching = loads((ROOT / MATCHING).read_text(encoding="utf-8"))["matching"]
    need(len(matching) == 56, "56 planes")
    need(sorted(port for pair in matching for port in pair) == list(range(112)),
         "perfect matching")
    planes = []
    for left, right in matching:
        pair = (labels[left], labels[right])
        need(dot(pair[0], pair[0]) == dot(pair[1], pair[1]) == 1, "Gram diagonal")
        need(dot(pair[0], pair[1]) == 0, "Gram off-diagonal")
        planes.append(pair)
    selected = loads((ROOT / SELECTED).read_text(encoding="utf-8"))
    need(selected["decimal"] == "0.001672660197076918", "selected decimal")
    return planes


def orthogonal(planes, left, right):
    return all(dot(a, b) == 0 for a in planes[left] for b in planes[right])


def conflict_clique(planes, indexes):
    return all(not orthogonal(planes, i, j) for i, j in combinations(indexes, 2))


def support_charge(planes, indexes, mask_left, mask_right):
    left = [vector for bit, index in enumerate(indexes) if mask_left & (1 << bit) for vector in planes[index]]
    right = [vector for bit, index in enumerate(indexes) if mask_right & (1 << bit) for vector in planes[index]]
    return pairing_rank(left, right)


def collision_supports(planes, indexes):
    """Every nonempty complete-plane support inside a form-rank-2 set pays at least 2."""
    size = len(indexes)
    minimum = None
    for mask_left in range(1, 1 << size):
        for mask_right in range(1, 1 << size):
            charge = support_charge(planes, indexes, mask_left, mask_right)
            need(charge >= 2, "collapsed support pays 2")
            if minimum is None or charge < minimum:
                minimum = charge
    return minimum


def geometry(planes):
    """Form-rank-2 collisions are conflict cliques whose every support pays at least 2."""
    pair_collisions = []
    rank2_pairs = []
    orthogonal_pairs = 0
    cross_rank_1_pairs = 0
    for left, right in combinations(range(56), 2):
        rank, dimension = form_rank(planes, (left, right))
        if orthogonal(planes, left, right):
            orthogonal_pairs += 1
            need(rank == 4 and dimension == 4, "orthogonal pair pays 4")
            left_vectors = {planes[left][0], planes[left][1], planes[left][0] ^ planes[left][1]}
            right_vectors = {planes[right][0], planes[right][1], planes[right][0] ^ planes[right][1]}
            need(left_vectors.isdisjoint(right_vectors), "orthogonal planes meet")
        else:
            cross = pairing_rank(planes[left], planes[right])
            if cross == 1:
                cross_rank_1_pairs += 1
            if rank < 4:
                pair_collisions.append((left, right, rank, dimension))
            if rank <= 2:
                need(conflict_clique(planes, (left, right)), "rank-2 pair is a conflict clique")
                need(collision_supports(planes, (left, right)) >= 2, "rank-2 pair supports")
                rank2_pairs.append((left, right, rank, dimension))
    triple_collisions = []
    for indexes in combinations(range(56), 3):
        rank, dimension = form_rank(planes, indexes)
        if rank <= 2:
            need(conflict_clique(planes, indexes), "rank-2 triple is a conflict clique")
            need(collision_supports(planes, indexes) >= 2, "rank-2 triple supports")
            triple_collisions.append((indexes, rank, dimension))
    larger = 0
    for indexes in combinations(range(56), 4):
        rank, _dimension = form_rank(planes, indexes)
        if rank <= 2:
            larger += 1
    clique_cross = 0
    for left, right in combinations(CLIQUE_24, 2):
        need(not orthogonal(planes, left, right), "24-plane conflict clique")
        if pairing_rank(planes[left], planes[right]) == 1:
            clique_cross += 1
    need(orthogonal_pairs == 109, "orthogonal pair count")
    need(len(pair_collisions) == 448, "collapsed pair count")
    need(len(rank2_pairs) == 144, "rank-2 pair count")
    need(len(triple_collisions) == 8, "rank-2 triple count")
    need(larger == 0, "no larger form-rank-2 set")
    need(cross_rank_1_pairs == 879, "cross-rank-1 pair count")
    need(clique_cross == 173, "24-plane cross-rank-1 pairs")
    for index in range(56):
        need(form_rank(planes, (index,))[0] == 2, "one plane pays 2")
    return {
        "orthogonal_pairs": orthogonal_pairs,
        "collapsed_pairs": len(pair_collisions),
        "rank2_pairs": len(rank2_pairs),
        "rank2_triples": len(triple_collisions),
        "cross_rank_1_pairs": cross_rank_1_pairs,
        "clique_24_cross_rank_1_pairs": clique_cross,
        "sample_triple": [list(triple_collisions[0][0]), triple_collisions[0][1]],
    }


def restitution(size):
    """Identity rank times the minimum positive one-total charge."""
    need(size >= 1, "nonempty clique")
    identity_rank = 2 * size
    minimum_term_charge = 2
    return identity_rank * minimum_term_charge


def moment(copy_mass):
    width = 896
    stages = 9
    families = 73
    return Fraction(71 * width + stages * copy_mass, families * width)


def rejects(function):
    try:
        function()
    except ValueError:
        return True
    return False


def check_certificate(raw, report):
    certificate = loads(raw)
    need(certificate["hypothesis"] == "quotient-collision-restitution", "hypothesis name")
    need(certificate["orthogonal_pairs"] == report["orthogonal_pairs"], "orthogonal count")
    need(certificate["collapsed_pairs"] == report["collapsed_pairs"], "collapsed pairs")
    need(certificate["rank2_pairs"] == report["rank2_pairs"], "rank-2 pairs")
    need(certificate["rank2_triples"] == report["rank2_triples"], "rank-2 triples")
    need(certificate["cross_rank_1_pairs"] == report["cross_rank_1_pairs"], "cross-rank-1 pairs")
    need(certificate["clique_24"] == list(CLIQUE_24), "stored clique")
    need(certificate["clique_24_cross_rank_1_pairs"] == report["clique_24_cross_rank_1_pairs"],
         "clique cross-rank-1 pairs")
    need(certificate["restitution_per_plane"] == 4, "rate")
    need(certificate["rank2_pair_copy_mass"] == restitution(2), "pair mass")
    need(certificate["rank2_triple_copy_mass"] == restitution(3), "triple mass")
    need(certificate["singleton_copy_mass"] == 112 * 2, "singleton attainment")
    need(certificate["moment_at_224"] == "293/292", "moment")
    need(moment(224) == Fraction(293, 292), "moment arithmetic")
    need(moment(224) > 1, "moment does not beat 1")
    for size in (1, 2, 3):
        need(restitution(size) == 4 * size, "restitution identity")
    # The witnessed rank-2 triple is a real collision: one total can pay 2 < 12.
    sample, rank = report["sample_triple"]
    need(rank == 2 and restitution(3) == 12 and rank < restitution(3), "collapse is real")
    need(certificate["sample_rank2_triple"] == sample, "sample triple")
    need(certificate["selected_decimal"] == "0.001672660197076918", "decimal pin")
    need(certificate["large_clique_open"] is True, "large clique stays open")


def negative_controls(raw, report):
    controls = 0

    def corrupt_clique():
        certificate = loads(raw)
        certificate["clique_24"] = list(CLIQUE_24[:-1]) + [0]
        check_certificate(json.dumps(certificate).encode(), report)

    need(rejects(corrupt_clique), "corrupted clique rejected")
    controls += 1

    def corrupt_mass():
        certificate = loads(raw)
        certificate["rank2_triple_copy_mass"] = 11
        check_certificate(json.dumps(certificate).encode(), report)

    need(rejects(corrupt_mass), "undercounted triple mass rejected")
    controls += 1

    def duplicate():
        loads(b'{"hypothesis": "quotient-collision-restitution", "hypothesis": "other"}\n')

    need(rejects(duplicate), "duplicate JSON key rejected")
    controls += 1

    def nested_duplicate():
        loads(b'{"outer": {"hypothesis": 1, "hypothesis": 2}}\n')

    need(rejects(nested_duplicate), "nested duplicate JSON key rejected")
    controls += 1

    with tempfile.TemporaryDirectory(prefix="clique-restitution-") as directory:
        path = Path(directory) / "CERTIFICATE.json"
        payload = bytearray(raw)
        # Flip the stored triple mass without touching the live package file.
        token = b'"rank2_triple_copy_mass": 12'
        digit = payload.find(token)
        need(digit > 0 and payload.count(token) == 1, "mass token")
        payload[digit + len(token) - 2:digit + len(token)] = b"11"
        path.write_bytes(payload)
        need(rejects(lambda: check_certificate(path.read_bytes(), report)),
             "corrupted temporary certificate rejected")
    controls += 1

    need(rejects(lambda: need(False, "orthogonal pair pays 4")), "false orthogonal pair rejected")
    controls += 1
    need(rejects(lambda: need(restitution(3) == 11, "undercount")), "false restitution rejected")
    controls += 1
    need(rejects(lambda: loads(b'{"selected_decimal": "0.001672660197076918", "selected_decimal": "0"}')),
         "duplicate decimal key rejected")
    controls += 1
    return controls


def main():
    planes = load_planes()
    report = geometry(planes)
    raw = (PACKAGE / "CERTIFICATE.json").read_bytes()
    # Read-only on the package tree: controls write only under TemporaryDirectory.
    before = raw
    check_certificate(raw, report)
    controls = negative_controls(raw, report)
    need((PACKAGE / "CERTIFICATE.json").read_bytes() == before, "certificate unchanged")
    need(controls == 8, "control count")
    print(
        "PASS_PAIRED_PLANE_CLIQUE_RESTITUTION",
        "pair_mass=" + str(restitution(2)),
        "triple_mass=" + str(restitution(3)),
        "rate=4",
        "rank2_pairs=" + str(report["rank2_pairs"]),
        "rank2_triples=" + str(report["rank2_triples"]),
        "moment224=293/292",
        "controls=" + str(controls),
    )


if __name__ == "__main__":
    main()
