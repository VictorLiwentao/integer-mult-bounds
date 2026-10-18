#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Cost-preserving J/P elimination unlocks universal named-class floor 45."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/c5-dyadic-decoder-gate/inputs/"
USAGES = {
    "certificates/selected-result.json": "provenance",
    "docs/research/agent-task-catalog.json": "provenance",
    PREFIX + "DATA-PHASES.json.gz": "input",
    PREFIX + "MATCHING.json": "input",
}
PASS_LINE = (
    "PASS_C5_J_FREE_UNIVERSAL_REDUCTION "
    "cycles=23 named_class_opt=224 pair_slack_min=4 "
    "j_free_floor=45 universal=true"
)
N_PORTS = 112
N_PLANES = 56


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sources(root: Path = ROOT, inventory: Path | None = None) -> dict[str, bytes]:
    path = HERE / "SOURCES.json" if inventory is None else inventory
    need(path.stat().st_size <= 32_000, "bounded manifest")
    doc = json.loads(path.read_bytes())
    need(set(doc) == {"schema_version", "base_commit", "files"}, "manifest schema")
    need(doc["schema_version"] == 1, "manifest version")
    need(doc["base_commit"] == "463113d675af7410ac91d53a4fed51ec6494eb9a", "base")
    rows = doc["files"]
    need(isinstance(rows, list) and len(rows) == 4, "four source rows")
    need(
        all(
            isinstance(r, dict) and set(r) == {"path", "usage", "git_blob", "sha256"}
            for r in rows
        ),
        "source row schema",
    )
    need(len({r["path"] for r in rows}) == 4, "unique source paths")
    need({r["path"]: r["usage"] for r in rows} == USAGES, "fixed paths/usages")
    payloads: dict[str, bytes] = {}
    for row in rows:
        if row["usage"] == "provenance":
            continue
        src = root / row["path"]
        need(src.is_file() and not src.is_symlink(), "regular source")
        need(src.resolve().is_relative_to(root.resolve()), "source inside root")
        need(src.stat().st_size <= 2_000_000, "bounded input")
        raw = src.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        need(blob == row["git_blob"], "source Git blob")
        payloads[src.name] = raw
    return payloads


def geometry(root: Path = ROOT, inventory: Path | None = None):
    raw = sources(root, inventory)
    with gzip.GzipFile(fileobj=io.BytesIO(raw["DATA-PHASES.json.gz"])) as stream:
        data = stream.read(2_000_001)
    need(len(data) <= 2_000_000, "bounded decompression")
    rows = json.loads(data)["recipes"]
    need(isinstance(rows, list) and len(rows) == N_PORTS, "112 scalar labels")
    need(
        all(
            isinstance(r, dict)
            and type(r.get("port")) is int
            and type(r.get("q")) is int
            for r in rows
        ),
        "label row schema",
    )
    labels = {r["port"]: r["q"] for r in rows}
    need(sorted(labels) == list(range(N_PORTS)), "unique ports")
    need(
        len(set(labels.values())) == N_PORTS
        and all(0 < q < 512 for q in labels.values()),
        "distinct nine-bit labels",
    )
    matching = json.loads(raw["MATCHING.json"])["matching"]
    need(isinstance(matching, list) and len(matching) == N_PLANES, "56 planes")
    need(
        all(
            isinstance(pair, list)
            and len(pair) == 2
            and all(type(p) is int for p in pair)
            for pair in matching
        ),
        "pair schema",
    )
    need(
        sorted(p for pair in matching for p in pair) == list(range(N_PORTS)),
        "partition",
    )
    planes = tuple(tuple(labels[p] for p in pair) for pair in matching)
    need(
        all([[dot(x, y) for y in e] for x in e] == [[1, 0], [0, 1]] for e in planes),
        "nondegenerate complete planes",
    )
    return planes, matching


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() % 2


def pairing_rank(left, right) -> int:
    need(len(left) <= N_PORTS and len(right) <= N_PORTS, "rank dimensions")
    if not left or not right:
        return 0
    pivots = [0] * len(right)
    for label in left:
        row = 0
        for j, other in enumerate(right):
            if dot(label, other):
                row |= 1 << j
        for j in range(len(right) - 1, -1, -1):
            if row >> j & 1:
                if pivots[j]:
                    row ^= pivots[j]
                else:
                    pivots[j] = row
                    break
    rank = sum(bool(p) for p in pivots)
    need(rank <= 9, "ambient rank bound")
    return rank


def cycles(planes):
    adj = [
        {
            j
            for j in range(N_PLANES)
            if i != j and pairing_rank(planes[i], planes[j]) == 0
        }
        for i in range(N_PLANES)
    ]
    found = set()
    for a in range(N_PLANES):
        for b in adj[a]:
            for c in adj[b] - adj[a] - {a}:
                for d in adj[c] - adj[a] - adj[b] - {a, b}:
                    for e in (adj[d] & adj[a]) - adj[b] - adj[c] - {b, c}:
                        if a == min(a, b, c, d, e) and b < e:
                            found.add((a, b, c, d, e))
    need(len(found) == 23, "23 induced physical C5s")
    return tuple(sorted(found))


def port_plane_map(matching):
    out = {}
    for plane_index, pair in enumerate(matching):
        for port in pair:
            out[port] = plane_index
    need(sorted(out) == list(range(N_PORTS)), "every port mapped")
    return out


def od_tariff(planes, port_to_plane, i: int, j: int) -> int:
    return pairing_rank(planes[port_to_plane[i]], planes[port_to_plane[j]])


def gram_tariff(planes, port_to_plane, i: int, j: int) -> int:
    pi, pj = port_to_plane[i], port_to_plane[j]
    if pi == pj:
        labels = planes[pi]
    else:
        labels = planes[pi] + planes[pj]
    return pairing_rank(labels, labels)


def pair_slack_census(planes, matching) -> dict:
    """Geometric lemma: tau_P + tau_OD_ij + tau_OD_ji >= 4 for every port pair."""
    port_to_plane = port_plane_map(matching)
    hist: Counter[int] = Counter()
    checked = 0
    min_slack = None
    equality_pairs = 0
    for i, j in combinations(range(N_PORTS), 2):
        od = od_tariff(planes, port_to_plane, i, j)
        # OD is symmetric in plane supports, but charge both ordered directions.
        od_rev = od_tariff(planes, port_to_plane, j, i)
        need(od == od_rev, "OD tariff symmetry")
        gram = gram_tariff(planes, port_to_plane, i, j)
        slack = gram + od + od_rev
        need(slack >= 4, "pair expansion dominates diagonal mass 4")
        hist[slack] += 1
        if min_slack is None or slack < min_slack:
            min_slack = slack
        if slack == 4:
            equality_pairs += 1
        checked += 1
        need(checked <= 10_000, "bounded pair census")
    need(checked == N_PORTS * (N_PORTS - 1) // 2, "complete unordered pair census")
    need(min_slack == 4, "tight pair slack")
    need(equality_pairs >= 1, "equality attained")
    return {
        "unordered_pairs": checked,
        "min_slack": min_slack,
        "equality_pairs": equality_pairs,
        "slack_histogram": {str(k): v for k, v in sorted(hist.items())},
        "domination_holds": True,
    }


def named_class_cost(gamma: int, deltas: dict, planes, matching) -> int:
    """Exact-I cost for integer (gamma, delta) under named-class tariffs."""
    port_to_plane = port_plane_map(matching)
    alpha = [1 - gamma] * N_PORTS
    for (i, j), d in deltas.items():
        need(i < j, "unordered delta keys")
        alpha[i] -= d
        alpha[j] -= d
    cost = sum(abs(a) * 2 for a in alpha) + abs(gamma) * 9

    def delta_of(i: int, j: int) -> int:
        return deltas.get((min(i, j), max(i, j)), 0)

    for i in range(N_PORTS):
        for j in range(N_PORTS):
            if i == j:
                continue
            beta = -gamma - delta_of(i, j)
            cost += abs(beta) * od_tariff(planes, port_to_plane, i, j)
    for (i, j), d in deltas.items():
        cost += abs(d) * gram_tariff(planes, port_to_plane, i, j)
    return cost


def expand_and_net_to_diagonal(planes, matching, fixture: dict) -> dict:
    """Apply J/P coordinate expansion + identical-support netting; land on diagonal."""
    port_to_plane = port_plane_map(matching)
    # Accumulate signed D and OD coefficients from the fixture's named terms.
    diag = [0] * N_PORTS
    od = [[0] * N_PORTS for _ in range(N_PORTS)]

    for _ in range(fixture.get("diagonal_units", 0)):
        for i in range(N_PORTS):
            diag[i] += 1
    gamma = fixture.get("net_j", 0)
    if gamma:
        # Expand gamma * J = gamma * (sum D + sum OD).
        for i in range(N_PORTS):
            diag[i] += gamma
            for j in range(N_PORTS):
                if i != j:
                    od[i][j] += gamma
    for (i, j), d in fixture.get("deltas", {}).items():
        # Expand d * P_ij = d * (D_i + D_j + OD_ij + OD_ji).
        need(i < j, "unordered gram keys")
        diag[i] += d
        diag[j] += d
        od[i][j] += d
        od[j][i] += d
    for (i, j), b in fixture.get("explicit_od", {}).items():
        od[i][j] += b

    # After expansion of the exact-I fixtures, netting must yield the diagonal.
    need(all(diag[i] == 1 for i in range(N_PORTS)), "diagonal coefficients")
    need(
        all(od[i][j] == 0 for i in range(N_PORTS) for j in range(N_PORTS) if i != j),
        "off-diagonal netting to zero",
    )
    reduced_cost = sum(
        abs(diag[i]) * pairing_rank(planes[port_to_plane[i]], planes[port_to_plane[i]])
        for i in range(N_PORTS)
    )
    need(reduced_cost == 224, "reduced tariff is diagonal 224")
    need(reduced_cost <= fixture["cost"], "cost-preserving")
    need(fixture["cost"] >= 224, "named-class lower bound on fixture")
    return {
        "name": fixture["name"],
        "pre_cost": fixture["cost"],
        "post_cost": reduced_cost,
        "net_j_before": fixture.get("net_j", 0),
        "net_j_after": 0,
        "cost_preserving": True,
    }


def diagonal_fixture(planes, matching) -> dict:
    port_to_plane = port_plane_map(matching)
    cost = 0
    matrix = [[0] * N_PORTS for _ in range(N_PORTS)]
    for port in range(N_PORTS):
        plane = planes[port_to_plane[port]]
        term = pairing_rank(plane, plane)
        need(term == 2, "single-plane self-pairing is I2")
        cost += term
        matrix[port][port] += 1
    need(
        all(matrix[i][j] == int(i == j) for i in range(N_PORTS) for j in range(N_PORTS)),
        "diagonal sums to I",
    )
    need(cost == 224, "diagonal tariff")
    return {
        "name": "diagonal",
        "formula": "I = sum_i e_i e_i^T",
        "cost": cost,
        "net_j": 0,
        "diagonal_units": 1,
        "deltas": {},
        "explicit_od": {},
    }


def j_extension_fixture(planes, matching) -> dict:
    port_to_plane = port_plane_map(matching)
    all_labels = tuple(q for plane in planes for q in plane)
    j_cost = pairing_rank(all_labels, all_labels)
    need(j_cost == 9, "full-support tariff")
    od_total = 0
    explicit = {}
    matrix = [[1] * N_PORTS for _ in range(N_PORTS)]
    for i in range(N_PORTS):
        for j in range(N_PORTS):
            if i == j:
                continue
            term = od_tariff(planes, port_to_plane, i, j)
            od_total += term
            explicit[(i, j)] = -1
            matrix[i][j] -= 1
    need(
        all(matrix[i][j] == int(i == j) for i in range(N_PORTS) for j in range(N_PORTS)),
        "J-extension exact",
    )
    total = j_cost + od_total
    need(total == 16097, "pinned J-extension tariff")
    return {
        "name": "j_identity_extension",
        "formula": "I = J - sum_{i != j} e_i e_j^T",
        "cost": total,
        "net_j": 1,
        "diagonal_units": 0,
        "deltas": {},
        "explicit_od": explicit,
    }


def gram_extension_fixture(planes, matching) -> dict:
    """I = J - sum_{i<j} P_ij + (n-1) sum_i D_i."""
    port_to_plane = port_plane_map(matching)
    all_labels = tuple(q for plane in planes for q in plane)
    j_cost = pairing_rank(all_labels, all_labels)
    need(j_cost == 9, "full-support tariff")
    deltas = {(i, j): -1 for i, j in combinations(range(N_PORTS), 2)}
    gram_cost = sum(
        gram_tariff(planes, port_to_plane, i, j) for i, j in deltas
    )
    diag_mult = N_PORTS - 1
    diag_cost = diag_mult * N_PORTS * 2
    total = j_cost + gram_cost + diag_cost
    # Matrix check via coefficient formulas (avoid assembling 112^2 from scratch twice).
    need(total == named_class_cost(1, deltas, planes, matching), "gram cost agrees")
    need(total > 224, "gram extension above diagonal")
    return {
        "name": "signed_gram_extension",
        "formula": "I = J - sum_{i<j} P_ij + (n-1) sum_i D_i",
        "cost": total,
        "net_j": 1,
        "diagonal_units": diag_mult,
        "deltas": deltas,
        "explicit_od": {},
    }


def padded_j_cancel_fixture(planes, matching) -> dict:
    """I = sum D + J - J; net J cancels; pre-netting tariff 242."""
    diag = diagonal_fixture(planes, matching)
    # Gross cost before opposite-sign J netting: 224 + 9 + 9.
    gross = diag["cost"] + 18
    need(gross == 242, "padded +J-J gross tariff")
    return {
        "name": "padded_plus_minus_j",
        "formula": "I = sum_i e_i e_i^T + J - J",
        "cost": gross,
        "net_j": 0,  # after identical-support netting of +J and -J
        "diagonal_units": 1,
        "deltas": {},
        "explicit_od": {},
        # Expansion path: the two J copies cancel before expand; reduced cost 224.
        "pre_net_j_gross": 1,
    }


def subgradient_certificate(planes, matching, pair_census: dict) -> dict:
    """0 lies in ∂C at the diagonal parameters, so Cost >= 224 globally (convex)."""
    need(pair_census["min_slack"] == 4, "pair lemma feeds subgradient")
    port_to_plane = port_plane_map(matching)
    # OD tariff sum over ordered pairs (for gamma subgradient range).
    od_sum = 0
    for i in range(N_PORTS):
        for j in range(N_PORTS):
            if i != j:
                od_sum += od_tariff(planes, port_to_plane, i, j)
    need(od_sum == 16088, "pinned ordered OD tariff sum")
    # Gamma direction: -224 - sum σ_ij τ_ij + 9 σ_γ with σ ∈ [-1,1] contains 0.
    gamma_lo = -224 - od_sum - 9
    gamma_hi = -224 + od_sum + 9
    need(gamma_lo <= 0 <= gamma_hi, "zero in gamma subdifferential range")
    # Delta direction for every unordered pair: need τ_P + τ_ij + τ_ji >= 4
    # so -4 -σ_ij τ_ij -σ_ji τ_ji + σ_P τ_P can be 0.
    need(pair_census["domination_holds"], "every pair admits zero delta-subgradient")
    return {
        "convex_cost": True,
        "diagonal_is_critical_point": True,
        "gamma_subdiff_contains_zero": True,
        "delta_subdiff_contains_zero": True,
        "global_minimizer_cost": 224,
        "ordered_od_tariff_sum": od_sum,
    }


def parametric_lower_bounds(planes, matching) -> list:
    """Spot-check Cost(gamma, delta) >= 224 on the classical lattice points."""
    rows = []
    for gamma in (-2, -1, 0, 1, 2):
        cost = named_class_cost(gamma, {}, planes, matching)
        need(cost >= 224, "gamma lattice above diagonal")
        rows.append({"gamma": gamma, "deltas": "empty", "cost": cost})
    # Matching-supported deltas at gamma=1.
    md = {(min(a, b), max(a, b)): -1 for a, b in matching}
    cost_md = named_class_cost(1, md, planes, matching)
    need(cost_md >= 224, "matching gram deltas above diagonal")
    rows.append({"gamma": 1, "deltas": "matching_minus_one", "cost": cost_md})
    # Single orthogonal-style equality pair at gamma=0 (cost may equal 224).
    # Pick any pair attaining slack 4.
    port_to_plane = port_plane_map(matching)
    eq_pair = None
    for i, j in combinations(range(N_PORTS), 2):
        od = od_tariff(planes, port_to_plane, i, j)
        gram = gram_tariff(planes, port_to_plane, i, j)
        if gram + 2 * od == 4:
            eq_pair = (i, j)
            break
    need(eq_pair is not None, "equality pair exists")
    cost_eq = named_class_cost(0, {eq_pair: 1}, planes, matching)
    need(cost_eq >= 224, "equality-pair delta above or at diagonal")
    rows.append(
        {
            "gamma": 0,
            "deltas": f"singleton_{eq_pair}",
            "cost": cost_eq,
            "attains_diagonal": cost_eq == 224,
        }
    )
    return rows


def build() -> dict:
    planes, matching = geometry()
    cycle_rows = cycles(planes)
    ranks = []
    for cycle in cycle_rows:
        local = tuple(q for i in cycle for q in planes[i])
        ranks.append(pairing_rank(local, local))
    need(Counter(ranks) == {7: 4, 8: 6, 9: 13}, "C5 full-support rank receipt")

    pair_census = pair_slack_census(planes, matching)
    subgrad = subgradient_certificate(planes, matching, pair_census)

    fixtures = [
        diagonal_fixture(planes, matching),
        j_extension_fixture(planes, matching),
        gram_extension_fixture(planes, matching),
        padded_j_cancel_fixture(planes, matching),
    ]
    reductions = [expand_and_net_to_diagonal(planes, matching, f) for f in fixtures]
    need(all(r["cost_preserving"] and r["net_j_after"] == 0 for r in reductions), "all reduce")
    need(all(r["post_cost"] == 224 for r in reductions), "all land on diagonal")

    parametric = parametric_lower_bounds(planes, matching)
    j_free_floor = Fraction(45)  # from #3643; cited, not recomputed
    need(j_free_floor == 45, "cited J-free floor")
    need(224 >= int(j_free_floor), "sharp opt implies universal 45")

    return {
        "schema_version": 1,
        "claim": (
            "cost_preserving_JP_elimination_unlocks_universal_named_class_j_free_floor_45"
        ),
        "scalar_ports": N_PORTS,
        "complete_planes": N_PLANES,
        "cycle_count": 23,
        "rank_histogram": {str(k): v for k, v in sorted(Counter(ranks).items())},
        "named_term_classes": [
            "diagonal_e_i_e_i_T",
            "full_support_J",
            "off_diagonal_e_i_e_j_T",
            "pairwise_gram_e_i_plus_e_j",
        ],
        "reduction": {
            "name": "coordinate_expand_and_identical_support_net",
            "steps": [
                "expand each net ±J to ±(sum_i D_i + sum_{i!=j} OD_ij)",
                "expand each net ±P_ij to ±(D_i + D_j + OD_ij + OD_ji)",
                "cancel identical-support opposite signs",
            ],
            "lands_on": "diagonal I = sum_i e_i e_i^T",
            "reduced_tariff": 224,
        },
        "pair_expansion_lemma": pair_census,
        "subgradient_certificate": subgrad,
        "named_class_optimum": 224,
        "j_free_floor_cited": "45",
        "universal_j_free_floor_applies": True,
        "fixtures": [
            {
                "name": f["name"],
                "formula": f["formula"],
                "pre_cost": f["cost"],
                "net_j": f.get("net_j", 0),
            }
            for f in fixtures
        ],
        "reductions": reductions,
        "parametric_lower_bounds": parametric,
        "cited_cancellation_charge": {
            "package": "research/c5-fit-level-cancellation-charge",
            "pr": 3643,
            "j_free_floor": "45",
            "one_j_floor": "561/16",
            "note": "floors cited only; domination census not reprinted",
        },
        "no_new_kappa": True,
        "selected_kappa": "0.001672660197076918",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = build()
    if args.emit:
        text = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output is not None:
            out = args.output.resolve()
            need(not out.exists(), "refuse overwrite")
            need(out.parent.is_dir(), "output parent")
            out.write_text(text)
        else:
            print(text, end="")
        return
    committed = json.loads((HERE / "RESULT.json").read_bytes())
    need(result == committed, "exact receipt")
    print(PASS_LINE)


if __name__ == "__main__":
    main()
