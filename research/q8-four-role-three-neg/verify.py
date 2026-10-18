#!/usr/bin/env python3
"""Four-role three-negative Q8 minimum is exactly nine calls.

Admission uses need() and stays active under python -O.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_Q8_FOUR_ROLE_THREE_NEG "
    "r4_hits=0+0 minimum=9 "
    "r3_333_hits=0 r3_332_hits=6774 "
    "no_new_kappa"
)
KAPPA = "0.001672660197076918"
BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key: " + key)
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def group_product(left, right):
    x, y = left >> 1, right >> 1
    neg = (left & 1) ^ (right & 1) ^ int(
        (x != 0 and x == y) or (x == 2 and y == 1) or (x == 3 and y == 2) or (x == 1 and y == 3)
    )
    return ((x ^ y) << 1) | neg


def multiplication_table():
    table = [[0] * 256 for _ in range(8)]
    for label in range(8):
        for mask in range(256):
            mixed = 0
            for basis in range(8):
                if mask >> basis & 1:
                    mixed ^= 1 << group_product(basis, label)
            table[label][mask] = mixed
    return table


TABLE = multiplication_table()


def identity(roles=4):
    return [1 << (8 * role) for role in range(roles)]


def apply_factor(state, image, covector, label, roles=4):
    out = list(state)
    for row in range(roles):
        support = 0
        for role in range(roles):
            if image >> role & 1:
                support ^= (state[row] >> (8 * role)) & 255
        delta = support ^ TABLE[label][support]
        for column in range(roles):
            if covector >> column & 1:
                out[row] ^= delta << (8 * column)
    return out


def diagonal_target(state, roles=4):
    labels = []
    for column in range(roles):
        masks = [(state[row] >> (8 * column)) & 255 for row in range(roles)]
        need(masks[column].bit_count() == 1 and all(
            masks[row] == 0 for row in range(roles) if row != column
        ), "endpoint is not diagonal")
        labels.append(masks[column].bit_length() - 1)
    return labels


def direct_word(labels):
    """Three calls of one label on each non-identity role. Identity is digit 0."""
    need(len(labels) == 4 and labels.count(0) == 1, "four-role spectator shape")
    state = identity()
    calls = []
    for role, label in enumerate(labels):
        if label == 0:
            continue
        paid = 2 if label == 3 else 4
        need(label in (3, 5), "target label")
        for _ in range(3):
            calls.append((role, paid))
            state = apply_factor(state, 1 << role, 1 << role, paid)
    need(diagonal_target(state) == list(labels), "direct word missed its endpoint")
    need(len(calls) == 9, "direct word length")
    return calls


def deleted_word_misses(labels):
    calls = direct_word(labels)
    for omit in range(len(calls)):
        state = identity()
        for index, (role, paid) in enumerate(calls):
            if index == omit:
                continue
            state = apply_factor(state, 1 << role, 1 << role, paid)
        try:
            got = diagonal_target(state)
        except ValueError:
            continue
        need(got != list(labels), "deleted call still realizes the endpoint")


def representative(labels):
    digits = list(labels)
    need(digits.count(0) == 1 and set(digits) <= {0, 3, 5}, "three-negative shape")
    if digits.count(5) > digits.count(3):
        digits = [5 if item == 3 else 3 if item == 5 else item for item in digits]
    zero = digits.index(0)
    digits[zero], digits[3] = digits[3], digits[zero]
    if digits[:3].count(5) == 1:
        slot = digits.index(5)
        digits[slot], digits[2] = digits[2], digits[slot]
    return tuple(digits)


def all_targets():
    targets = []
    for zero in range(4):
        for mask in range(8):
            digits = []
            bit = 0
            for role in range(4):
                if role == zero:
                    digits.append(0)
                else:
                    digits.append(3 if (mask >> bit) & 1 else 5)
                    bit += 1
            targets.append(tuple(digits))
    need(len(targets) == 32 and len(set(targets)) == 32, "target inventory")
    return targets


def orbit_reduction():
    images = {representative(target) for target in all_targets()}
    need(images == {(3, 3, 3, 0), (3, 3, 5, 0)}, "symmetry representatives")
    for target in all_targets():
        direct_word(target)
        deleted_word_misses(target)


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    need(manifest["base_commit"] == BASE, "base commit pin")
    selected = None
    for row in manifest["files"]:
        raw = subprocess.check_output(
            ["git", "cat-file", "blob", manifest["base_commit"] + ":" + row["path"]],
            cwd=ROOT,
        )
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "pin hash " + row["path"])
        blob = subprocess.check_output(
            ["git", "rev-parse", manifest["base_commit"] + ":" + row["path"]],
            cwd=ROOT,
            text=True,
        ).strip()
        need(blob == row["git_blob"], "pin blob " + row["path"])
        if row["path"] == "certificates/selected-result.json":
            selected = json.loads(raw, object_pairs_hook=pairs_unique)
    need(selected is not None, "selected record pin")
    kappa = selected.get("kappa_decimal") or selected.get("decimal")
    # Selected record schema varies; require the revision-6 decimal somewhere.
    need(KAPPA in raw_selected_text(selected), "selected kappa pin")


def raw_selected_text(selected):
    return json.dumps(selected)


def run_search():
    binary_dir = Path(tempfile.mkdtemp(prefix="q8-four-role-"))
    binary = binary_dir / "search"
    compiled = subprocess.run(
        ["g++", "-O3", "-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
         "-o", str(binary), str(HERE / "search.cpp")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    need(compiled.returncode == 0, "compile failed: " + compiled.stderr)
    ran = subprocess.run([str(binary)], cwd=ROOT, capture_output=True, text=True)
    need(ran.returncode == 0, "search failed: " + ran.stderr)
    payload = json.loads(ran.stdout, object_pairs_hook=pairs_unique)
    binary.unlink()
    binary_dir.rmdir()
    return payload


def main():
    pin_sources()
    for left in range(8):
        for right in range(8):
            for third in range(8):
                need(group_product(group_product(left, right), third)
                     == group_product(left, group_product(right, third)),
                     "associativity")
    need(group_product(group_product(2, 2), 2) == 3, "i cubed is zi")
    need(group_product(group_product(4, 4), 4) == 5, "j cubed is zj")
    orbit_reduction()
    counts = run_search()
    need(counts["r4_3330_hits"] == 0 and counts["r4_3350_hits"] == 0, "four-role hit")
    need(counts["r4_inverse"] == 6735641, "four-role inverse ball")
    need(counts["r4_prefix"] == 6735641, "four-role prefix ball")
    need(counts["r4_candidates"] == 1623289481, "candidate stream")
    need(counts["r4_3350_candidates"] == counts["r4_candidates"], "mixed stream")
    need(counts["r3_333_hits"] == 0, "three-role calibration")
    need(counts["r3_332_hits"] == 6774, "two-negative positive control")
    need(counts["r3_inverse"] == 91955, "three-role ball")
    need(counts["factors_r4"] == 240 and counts["factors_r3"] == 56, "factor counts")
    need(counts["r4_depth2"] == 42041, "depth-two ball")
    print(MARKER)


if __name__ == "__main__":
    main()
