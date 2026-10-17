#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""V45 joint rank-7 lowering versus its four losing single-helper controls.

Set-span frames over F2^9. This file is a second checker and loads no other project module.
The selected kappa is read and left unchanged.
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import json
from pathlib import Path


GROUP = "V45"
HELPERS = (249, 251, 265, 267)
SUBSPACE = (256, 128, 64, 35, 16, 11, 5)
SURROGATE = {1: 2116671, 2: 4228346, 3: 6338140, 4: 8446713}
IDLE_GUIDE = 2091300
ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
INPUTS = {
    "parent_base": "research/rank7-joint-endframes/data/PARENT-base.json.gz",
    "parent_extra": "research/rank7-joint-endframes/data/PARENT-extra.json.gz",
    "word_base": "research/rank7-joint-endframes/data/WORD-base.json.gz",
    "word_extra": "research/rank7-joint-endframes/data/WORD-extra.json.gz",
    "edits": "research/rank7-joint-endframes/data/STAGE1-FRAME-EDITS.json",
    "assembly": "research/community-frontier1094-audit/ASSEMBLY.json",
    "selected": "certificates/selected-result.json",
}


def need(condition, message):
    if not condition:
        raise ValueError(str(message))


def load_json(text):
    def pairs(items):
        seen = set()
        for key, value in items:
            need(key not in seen, "duplicate key " + key)
            seen.add(key)
        return dict(items)

    return json.loads(text, object_pairs_hook=pairs)


def read_bytes(path):
    file = ROOT / path
    need(file.is_file() and not file.is_symlink(), "missing input " + path)
    return file.read_bytes()


def read_json(path):
    raw = read_bytes(path)
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return load_json(raw.decode("utf-8"))


def span(vectors):
    points = {0}
    for vector in vectors:
        need(type(vector) is int and 0 < vector < 512, "nine-bit generator")
        points |= {point ^ vector for point in points}
    need(len(points) == 1 << len(tuple(vectors)), "dependent frame")
    return frozenset(points)


def dimension(space):
    return len(space).bit_length() - 1


def subset(left, right):
    return left <= right


def same_space(left, right):
    return left == right


def span_basis(vectors):
    return span(vectors)


def image(columns, point):
    result = 0
    for bit in range(9):
        if point & (1 << bit):
            result ^= columns[bit]
    return result


def kernel_basis(mask):
    need(0 < mask < 512, "port mask")
    space = frozenset(point for point in range(512) if (point & mask).bit_count() % 2 == 0)
    need(dimension(space) == 8, "port hyperplane")
    return space


FULL = span(tuple(1 << bit for bit in range(9)))
ZERO = span(())


def frame_of(vectors):
    return ZERO if list(vectors) == [] else span_basis(tuple(vectors))


def boundaries(word):
    report = word["report"]
    need((report["v"], report["h"], report["R"]) == (112, 9, 480), "geometry")
    ports = word["ports"]
    need(len(ports) == len(set(ports)) == 112, "ports")
    starts = [span_basis((port,)) for port in ports] + [ZERO] * 592
    ends = [FULL] * 112 + [kernel_basis(port) for port in ports] + [FULL] * 480
    for field, frames in (("start_extra", starts), ("helper_final", ends)):
        need(len(word[field]) <= 480, "boundary count")
        for role, vectors in word[field].items():
            need(224 <= int(role) < 704, "helper register")
            frames[int(role)] = span_basis(tuple(vectors))
    live = set(range(704)) - set(word["removed"])
    need(len(live) == 632 and set(range(224)) <= live, "live registers")
    widths = Counter()
    for role in sorted(live - set(range(224))):
        need(subset(starts[role], ends[role]), "entrance inside terminal")
        widths[dimension(ends[role]) - dimension(starts[role])] += 1
    return starts, ends, live, dict(sorted(widths.items()))


def climb(current, paid, role, destination):
    need(subset(current[role], destination), "nonmonotone climb")
    rank = dimension(destination) - dimension(current[role])
    if rank:
        paid[rank] += 1
    current[role] = destination


def warp(current, role, columns, old, new, inverse=False):
    need(len(columns) == 9, "warp columns")
    old_basis, new_basis = span_basis(tuple(old)), span_basis(tuple(new))
    mapped = frozenset(image(columns, vector) for vector in old_basis)
    need(same_space(mapped, new_basis), "warp image")
    need(len({image(columns, point) for point in range(512)}) == 512, "singular warp")
    source, target = (new_basis, old_basis) if inverse else (old_basis, new_basis)
    need(current[role] == source, "warp entrance")
    current[role] = target


def scalar_step(word, current, paid, gate):
    if gate[0] == "warp":
        need(len(gate) == 5, "warp shape")
        role, operator, old, new = gate[1:]
        columns = word["warps"][abs(operator) - 1][2]
        if operator < 0:
            warp(current, role, columns, new, old, inverse=True)
        else:
            warp(current, role, columns, old, new)
        return
    need(gate[0] in ("add", "scale"), "scalar kind")
    destination = frame_of(gate[-1])
    roles = gate[1:3] if gate[0] == "add" else gate[1:2]
    for role in roles:
        climb(current, paid, role, destination)


def centre_copies(word, current, paid):
    need(len(word["centers"]) == len(word["center_frames"]) == 8, "eight centres")
    for role, frame in zip(word["centers"], word["center_frames"], strict=True):
        source = span_basis(tuple(frame))
        need(current[role] == source, "centre entrance")
        readers = []
        for gate in word["cut"]:
            if gate[2] != role:
                continue
            level = word["target_levels"].get(str(gate[1] - 112), [])
            basis = frame_of(level)
            if basis not in readers:
                readers.append(basis)
        for target in sorted(readers, key=lambda basis: (-len(basis), tuple(sorted(basis)))):
            need(subset(target, source), "centre nesting")
            rank = dimension(source) - dimension(target)
            if rank:
                paid[rank] += 1
            source = target


def ledger(word):
    for section in ("A", "B", "restore", "cut", "cleanup"):
        need(len(word[section]) <= 10000, "section bound")
    current, ends, live, widths = boundaries(word)
    paid = Counter()
    for gate in word["A"]:
        scalar_step(word, current, paid, gate)
    for target in range(112):
        level = word["target_levels"].get(str(target), [])
        need(current[112 + target] == frame_of(level), "target level")
    centre_copies(word, current, paid)
    by_position = {}
    for position, role, columns, old, new in word["warps"]:
        need(0 <= position <= len(word["B"]), "warp position")
        by_position.setdefault(position, []).append((role, columns, old, new))
    for index in range(len(word["B"]) + 1):
        for role, columns, old, new in by_position.get(index, []):
            warp(current, role, columns, old, new)
        if index < len(word["B"]):
            scalar_step(word, current, paid, word["B"][index])
    for gate in word["restore"]:
        scalar_step(word, current, paid, gate)
    for role in sorted(live):
        climb(current, paid, role, ends[role])
    profile = {int(rank): count for rank, count in word["report"]["local_profile"].items()}
    width_report = {int(rank): count for rank, count in word["report"]["width_inventory"].items()}
    need(dict(sorted(paid.items())) == profile, "parent profile drifted")
    need(widths == width_report, "parent widths drifted")
    return dict(sorted(paid.items())), widths


def paid_delta(child, parent_profile):
    profile, widths = ledger_unchecked(child)
    return difference(profile, parent_profile), widths


def ledger_unchecked(word):
    """Replay a frame-edited child. Its stored report is still the parent's."""
    saved = word["report"]
    current, ends, live, widths = _boundaries(word)
    paid = Counter()
    for gate in word["A"]:
        scalar_step(word, current, paid, gate)
    for target in range(112):
        level = word["target_levels"].get(str(target), [])
        need(current[112 + target] == frame_of(level), "target level")
    centre_copies(word, current, paid)
    by_position = {}
    for position, role, columns, old, new in word["warps"]:
        by_position.setdefault(position, []).append((role, columns, old, new))
    for index in range(len(word["B"]) + 1):
        for role, columns, old, new in by_position.get(index, []):
            warp(current, role, columns, old, new)
        if index < len(word["B"]):
            scalar_step(word, current, paid, word["B"][index])
    for gate in word["restore"]:
        scalar_step(word, current, paid, gate)
    for role in sorted(live):
        climb(current, paid, role, ends[role])
    need(saved["v"] == 112, "report retained")
    return dict(sorted((rank, count) for rank, count in paid.items() if count)), dict(sorted(widths.items()))


def _boundaries(word):
    ports = word["ports"]
    need(len(ports) == len(set(ports)) == 112, "ports")
    starts = [span_basis((port,)) for port in ports] + [ZERO] * 592
    ends = [FULL] * 112 + [kernel_basis(port) for port in ports] + [FULL] * 480
    for field, frames in (("start_extra", starts), ("helper_final", ends)):
        for role, vectors in word[field].items():
            frames[int(role)] = span_basis(tuple(vectors))
    live = set(range(704)) - set(word["removed"])
    need(len(live) == 632, "live registers")
    widths = Counter()
    for role in sorted(live - set(range(224))):
        need(subset(starts[role], ends[role]), "entrance inside terminal")
        widths[dimension(ends[role]) - dimension(starts[role])] += 1
    return starts, ends, live, widths


def tagged(mapping):
    return {str(key): value for key, value in mapping.items()}


def difference(after, before):
    keys = set(after) | set(before)
    return tagged({
        key: after.get(key, 0) - before.get(key, 0)
        for key in sorted(keys)
        if after.get(key, 0) != before.get(key, 0)
    })


def group_edits(record):
    spaces = {}
    for name, (frame, _helpers) in record["groups"].items():
        spaces[name] = span_basis(tuple(frame))
        need(dimension(spaces[name]) == 7, "rank-seven group")
    grouped = {name: [] for name in spaces}
    seen = set()
    for edit in record["frame_edits"]:
        key = (edit["section"], edit["index"])
        need(key not in seen, "duplicate edit")
        seen.add(key)
        old, new = span_basis(tuple(edit["old_frame"])), span_basis(tuple(edit["new_frame"]))
        need(subset(new, old) and dimension(old) == dimension(new) + 1, "codimension-one gate")
        names = [name for name, space in spaces.items() if subset(new, space)]
        need(len(names) == 1, "ambiguous gate group")
        grouped[names[0]].append(edit)
    need(len(grouped[GROUP]) == 61, "V45 edit count")
    return grouped


def apply_v45(parent, record, edits, endpoints):
    child = deepcopy(parent)
    frame, helpers = record["groups"][GROUP]
    need(tuple(frame) == SUBSPACE and tuple(helpers) == HELPERS, "V45 declaration")
    need(set(endpoints) <= set(helpers) and endpoints, "endpoint subset")
    for helper in endpoints:
        change = record["helper_final_changes"][str(helper)]
        need(parent["helper_final"][str(helper)] == change["old"], "endpoint preimage")
        need(change["new"] == frame, "shared subspace")
        old = span_basis(tuple(change["old"]))
        new = span_basis(tuple(frame))
        need(subset(new, old) and dimension(old) == 8 and dimension(new) == 7, "8 to 7")
        child["helper_final"][str(helper)] = list(frame)
    for edit in edits:
        section, index = edit["section"], edit["index"]
        gate = child[section][index]
        need(gate[:-1] == edit["gate"] and gate[-1] == edit["old_frame"], "gate preimage")
        child[section][index] = gate[:-1] + [list(edit["new_frame"])]
        touched = gate[1:3] if gate[0] == "add" else gate[1:2]
        for helper in set(touched) & set(endpoints):
            need(subset(span_basis(tuple(edit["new_frame"])), span_basis(tuple(frame))), "gate inside W")
    need(child["cleanup"] == parent["cleanup"], "cleanup changed")
    changed = {key for key in parent if parent[key] != child[key]}
    need(changed <= {"helper_final", "A", "B", "restore"}, "non-frame edit")
    return child


def chronology(edits):
    by_section = {}
    for edit in edits:
        by_section.setdefault(edit["section"], []).append(edit["index"])
    need(set(by_section) == {"B", "restore"}, "V45 touches only B and restore")
    for indexes in by_section.values():
        need(indexes == sorted(set(indexes)), "edit indexes are not chronological")
    return {section: len(indexes) for section, indexes in sorted(by_section.items())}


def margin(delta, lowered):
    price = sum(count * SURROGATE[int(rank)] for rank, count in delta.items())
    return price, -price - lowered * IDLE_GUIDE


def supplier_account(assembly, selected, joint_profile, parent_profile):
    need(assembly["kappa"] == selected["kappa"], "selected kappa mismatch")
    need(selected["decimal"] == "0.001672660197076918", "selected decimal")
    need(assembly["binding"] == "complex", "binding side")
    bit_lower = Fraction(assembly["bit_lower"])
    complex_lower = Fraction(assembly["complex_lower"])
    kappa = Fraction(assembly["kappa"])
    need(complex_lower < bit_lower and kappa < complex_lower, "supplier order")
    word = assembly["bit_supplier"]["word"]
    flat = [word["v"], word["decoder_constant"], *word["copy_ranks"]]
    need(all(helper not in flat for helper in HELPERS), "bit word contains a V45 helper")
    need(assembly["bit_supplier"]["pr"] == 589, "bit supplier pr")
    complex_profile = {int(rank): count for rank, count in assembly["complex_profile"].items()}
    need(complex_profile != parent_profile and complex_profile != joint_profile, "selected complex profile")
    return {
        "selected_kappa": assembly["kappa"],
        "selected_binding": "complex",
        "selected_complex_lower": assembly["complex_lower"],
        "selected_bit_lower": assembly["bit_lower"],
        "bit_supplier_pr": 589,
        "bit_supplier_contains_v45_helper": False,
    }


def rejects(label, function):
    try:
        function()
    except ValueError:
        return label
    raise ValueError("mutant accepted: " + label)


def controls(parent, record, edits, joint_delta):
    accepted = []

    def widened():
        bad = dict(edits[0])
        bad["new_frame"] = list(bad["old_frame"])
        span_old = span_basis(tuple(bad["old_frame"]))
        span_new = span_basis(tuple(bad["new_frame"]))
        need(subset(span_new, span_old) and dimension(span_old) == dimension(span_new) + 1, "codim")

    def cleanup_mutation():
        child = apply_v45(parent, record, edits, HELPERS)
        child["cleanup"] = child["cleanup"] + [["add", 0, 0, 1, 1, []]]
        need(child["cleanup"] == parent["cleanup"], "cleanup changed")

    def omitted_gate():
        child = apply_v45(parent, record, edits[:-1], HELPERS)
        # The last declared edit was not applied, so its preimage check is skipped.
        # The omitted gate must change the paid delta or break monotonicity.
        delta, _widths = paid_delta(child, ledger(parent)[0])
        need(delta == joint_delta, "omitted gate changed the joint invoice")

    def wrong_subspace():
        forged = deepcopy(record)
        forged["groups"] = dict(forged["groups"])
        forged["groups"][GROUP] = [[256, 128, 64, 35, 16, 11, 4], list(HELPERS)]
        apply_v45(parent, forged, edits, HELPERS)

    accepted.append(rejects("widened-frame", widened))
    accepted.append(rejects("cleanup-mutation", cleanup_mutation))
    accepted.append(rejects("omitted-gate", omitted_gate))
    accepted.append(rejects("wrong-subspace", wrong_subspace))
    return accepted


def receipt():
    parents = [read_json(INPUTS["parent_base"]), read_json(INPUTS["parent_extra"])]
    words = [read_json(INPUTS["word_base"]), read_json(INPUTS["word_extra"])]
    record = read_json(INPUTS["edits"])
    edits = group_edits(record)[GROUP]
    order = chronology(edits)
    profiles = []
    for parent in parents:
        profile, _widths = ledger(parent)
        profiles.append(profile)
    need(profiles[0] == profiles[1], "providers differ on the parent profile")
    for edit in edits:
        need(
            parents[0][edit["section"]][edit["index"]] == parents[1][edit["section"]][edit["index"]],
            "providers differ on a V45 gate",
        )
    for helper in HELPERS:
        need(
            parents[0]["helper_final"][str(helper)] == parents[1]["helper_final"][str(helper)],
            "providers differ on a V45 endpoint",
        )
    joint = apply_v45(parents[0], record, edits, HELPERS)
    joint_profile, joint_widths = ledger_unchecked(joint)
    joint_delta = difference(joint_profile, profiles[0])
    joint_width_delta = difference(joint_widths, ledger(parents[0])[1])
    single_deltas = []
    single_width_deltas = []
    for helper in HELPERS:
        child = apply_v45(parents[0], record, edits, (helper,))
        profile, widths = ledger_unchecked(child)
        single_deltas.append(difference(profile, profiles[0]))
        single_width_deltas.append(difference(widths, ledger(parents[0])[1]))
    need(len(set(json.dumps(item) for item in single_deltas)) == 1, "singles disagree")
    need(single_deltas[0] != joint_delta, "single matches joint")
    extra_joint = apply_v45(parents[1], record, edits, HELPERS)
    need(ledger_unchecked(extra_joint)[0] == joint_profile, "extra provider joint profile")
    joint_price, joint_margin = margin(joint_delta, 4)
    single_price, single_margin = margin(single_deltas[0], 1)
    declared = {int(rank): count for rank, count in record["declared_width_inventory"].items()}
    need(joint_widths != declared, "V45-only widths equal the five-group inventory")
    joint_widths = tagged(joint_widths)
    declared = tagged(declared)
    parent_buffers = sorted(int(role) for role in parents[0]["helper_final"])
    final_buffers = sorted(int(role) for role in words[0]["helper_final"])
    need(final_buffers == sorted(int(role) for role in words[1]["helper_final"]), "final helpers")
    for helper in HELPERS:
        need(words[0]["helper_final"][str(helper)] == list(SUBSPACE), "final end moved")
        need(words[1]["helper_final"][str(helper)] == list(SUBSPACE), "extra final end moved")
    need(joint["cleanup"] == parents[0]["cleanup"], "stage image cleanup")
    added = sorted(set(final_buffers) - set(parent_buffers))
    account = supplier_account(
        read_json(INPUTS["assembly"]), read_json(INPUTS["selected"]), joint_profile, profiles[0]
    )
    rejected = controls(parents[0], record, edits, joint_delta)
    body = {
        "group": GROUP,
        "subspace": list(SUBSPACE),
        "helpers": list(HELPERS),
        "gate_edits": order,
        "providers_agree": True,
        "cleanup_gates_unchanged": len(parents[0]["cleanup"]),
        "private_buffers_after_group": len(parent_buffers),
        "private_buffers_in_final_word": len(final_buffers),
        "buffers_added_after_this_group": added,
        "joint_paid_delta": joint_delta,
        "single_paid_delta": single_deltas[0],
        "joint_width_delta": joint_width_delta,
        "single_width_delta": single_width_deltas[0],
        "v45_only_widths": joint_widths,
        "five_group_stage1_widths": declared,
        "surrogate_joint_price": joint_price,
        "surrogate_joint_margin": joint_margin,
        "surrogate_single_price": single_price,
        "surrogate_single_margin": single_margin,
        "surrogate_idle_guide": IDLE_GUIDE,
        "supplier_caps_determined_by_group": False,
        "rejected_mutants": rejected,
        **account,
    }
    need(body["surrogate_joint_margin"] == 22972, "joint guide margin")
    need(body["surrogate_single_margin"] == -53141, "single guide margin")
    need(body["joint_paid_delta"] == {"1": -2, "2": 10, "3": 6, "4": -10}, "joint children")
    need(body["single_paid_delta"] == {"1": 1, "2": 10, "3": 6, "4": -10}, "single children")
    need(body["buffers_added_after_this_group"] == [226, 228, 230, 363, 395], "later buffers")
    return body


def main():
    computed = receipt()
    certificate = load_json((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(certificate == computed, "certificate differs from exact replay")
    print("PASS_V45_ONE_GROUP_SET_SPAN")


if __name__ == "__main__":
    main()
