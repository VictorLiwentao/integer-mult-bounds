#!/usr/bin/env python3
"""Independent recompute of the #3696 OQ1 gate-operand guard census.

Does not import verify.py helpers. Standard library only.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = (
    "PASS_GATE_OPERAND_DEST_ABSENT_INDEPENDENT "
    "dest_absent_rejects_divergent=3492 "
    "dest_absent_rejects_dest_free_agree=0 "
    "simple_rejects_dest_free_agree=3450"
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def sym_coeffs(d, srcs, n):
    basis = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    acc = [0] * n
    for s in srcs:
        acc = [a ^ b for a, b in zip(acc, basis[s])]
    return tuple(a ^ b for a, b in zip(basis[d], acc))


def exp_coeffs(d, srcs, n):
    cur = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for s in srcs:
        cur[d] = [a ^ b for a, b in zip(cur[d], cur[s])]
    return tuple(cur[d])


def main():
    n = 6
    max_len = 4
    dest_free_agree = 0
    dest_in_disagree = 0
    simple_reject_dfa = 0
    dest_absent_reject_dfa = 0
    simple_miss_divergent = 0
    dest_absent_miss_divergent = 0
    for length in range(0, max_len + 1):
        for srcs in itertools.product(range(n), repeat=length):
            for d in range(n):
                agree = sym_coeffs(d, srcs, n) == exp_coeffs(d, srcs, n)
                free = d not in srcs
                simple = len(set([d] + list(srcs))) == len([d] + list(srcs))
                absent = d not in srcs
                if free and agree:
                    dest_free_agree += 1
                    if not simple:
                        simple_reject_dfa += 1
                    if not absent:
                        dest_absent_reject_dfa += 1
                if (not free) and (not agree):
                    dest_in_disagree += 1
                    if simple:
                        simple_miss_divergent += 1
                    if absent:
                        dest_absent_miss_divergent += 1

    need(dest_free_agree == 4686, "dest-free agree")
    need(dest_in_disagree == 3492, "dest-in disagree")
    need(simple_miss_divergent == 0, "simple catches all divergent")
    need(dest_absent_miss_divergent == 0, "dest-absent catches all divergent")
    need(dest_absent_reject_dfa == 0, "dest-absent preserves dest-free agree")
    need(simple_reject_dfa == 3450, "simple rejects agreeing dest-free")

    # Named controls: simple rejects agreeing dest-free dup; dest-absent accepts it.
    need(sym_coeffs(0, [1, 1], 3) == exp_coeffs(0, [1, 1], 3), "dup agrees")
    need(0 not in [1, 1], "dup dest-absent")
    need(len(set([0, 1, 1])) != 3, "dup fails simple")
    # Divergent #3696 witnesses rejected by both.
    need(sym_coeffs(0, [0, 0], 3) != exp_coeffs(0, [0, 0], 3), "self_even")
    need(sym_coeffs(0, [1, 0], 3) != exp_coeffs(0, [1, 0], 3), "dest_with_src")

    cert = json.loads(
        (HERE / "CERTIFICATE.json").read_text(),
        object_pairs_hook=pairs_unique,
    )
    need(cert["status"] == "PASS_GATE_OPERAND_DEST_ABSENT_GUARD", "cert status")
    need(cert["claim"]["oq1_dest_absent_preserves_dest_free_agree"] is True,
         "dest-absent answer")
    need(cert["claim"]["oq1_simple_support_preserves_dest_free_agree"] is False,
         "simple-support answer")
    need(cert["no_new_kappa"] is True, "no new kappa")
    print(MARKER)


if __name__ == "__main__":
    main()
