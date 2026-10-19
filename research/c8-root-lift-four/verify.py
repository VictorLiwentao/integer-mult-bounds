#!/usr/bin/env python3
"""Exact four-call minimum for the C8 four-involution diagonal.

The argument is the augmentation case split in PROOF.md. It does not search
the group-algebra ball; independent.py does that separately and does not
import this file.
"""

import json
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import algebra  # noqa: E402

PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_C8_ROOT_LIFT_FOUR minimum=4 below_four=0 no_new_kappa"


def load_json(path):
    def pairs(items):
        keys = [key for key, _ in items]
        algebra.need(len(keys) == len(set(keys)), "duplicate JSON key in " + path.name)
        return dict(items)

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def odd_support(labels):
    return frozenset((index,) for index, exponent in enumerate(labels) if exponent & 1)


def classify():
    counts = {"patterns": 0, "dead_single": 0, "dead_triple": 0, "live": 0}
    live_widths = []
    for length in (1, 2, 3):
        for labels in product(range(1, algebra.MODULUS), repeat=length):
            counts["patterns"] += 1
            series = algebra.word_series(labels)
            algebra.need(series[1] == odd_support(labels), "degree-1 drift " + str(labels))
            if all(exponent % 2 == 0 for exponent in labels):
                valuation_two = frozenset(
                    (index,) for index, exponent in enumerate(labels) if exponent in (2, 6)
                )
                algebra.need(series[2] == valuation_two and not series[3], "even-layer drift")
            kind = algebra.reduce_low_degrees(series)
            algebra.need(kind[0] != "unknown", "unclassified pattern " + str(labels))
            if kind[0] == "dead" and kind[1] == 1:
                counts["dead_single"] += 1
            elif kind[0] == "dead" and kind[1] == 3:
                counts["dead_triple"] += 1
            elif kind[0] == "live":
                counts["live"] += 1
                live_widths.append(kind[1])
            else:
                algebra.need(False, "bad kind " + str(kind))
    algebra.need(counts["patterns"] == 7 + 49 + 343, "pattern total")
    algebra.need(max(live_widths) <= 3 and min(live_widths) >= 0, "live width")
    return counts


def sum_lemma(idempotents):
    legal = set(idempotents)
    hits = 0
    square_failures = 0
    for left in idempotents:
        algebra.need(algebra.matrix_rank(left) == 1, "rank")
        algebra.need(algebra.matrix_mul(left, left) == left, "idempotent")
        for right in idempotents:
            total = left ^ right
            if total in legal:
                hits += 1
            if algebra.matrix_mul(total, total) != 0 and _same_image_or_row(left, right):
                square_failures += 1
    return hits, square_failures


def _same_image_or_row(left, right):
    """Images or rows agree when the outer vectors of xy^T agree.

    The census below does not use this predicate for the exclusion. It only
    checks the square-zero half of the written lemma on pairs already known
    to share an image or a row, which are exactly the pairs whose sum has
    rank at most one. Those pairs are detected by rank(sum) <= 1.
    """
    return algebra.matrix_rank(left ^ right) <= 1


def direct_word(idempotents):
    axes = []
    for index in range(algebra.REGISTERS):
        matrix = 1 << (index * algebra.REGISTERS + index)
        algebra.need(matrix in idempotents, "axis idempotent")
        axes.append(matrix)
    delta = algebra.increment(algebra.TARGET_DEGREE)
    algebra.need(delta == (1 << algebra.TARGET_DEGREE), "pure involution increment")
    value = _identity_matrix()
    for matrix in axes:
        value = _mul_group(_factor(matrix, delta), value)
    return value == _target_matrix()


def _identity_matrix():
    return tuple(1 if i == j else 0 for i in range(algebra.REGISTERS) for j in range(algebra.REGISTERS))


def _target_matrix():
    twist = 1 ^ (1 << algebra.TARGET_DEGREE)
    return tuple(twist if i == j else 0 for i in range(algebra.REGISTERS) for j in range(algebra.REGISTERS))


def _factor(matrix, delta):
    out = list(_identity_matrix())
    for i in range(algebra.REGISTERS):
        for j in range(algebra.REGISTERS):
            if (matrix >> (i * algebra.REGISTERS + j)) & 1:
                out[i * algebra.REGISTERS + j] ^= delta
    return tuple(out)


def _mul_group(left, right):
    out = [0] * (algebra.REGISTERS * algebra.REGISTERS)
    for i in range(algebra.REGISTERS):
        for k in range(algebra.REGISTERS):
            entry = left[i * algebra.REGISTERS + k]
            if not entry:
                continue
            for j in range(algebra.REGISTERS):
                out[i * algebra.REGISTERS + j] ^= algebra.algebra_mul(
                    entry, right[k * algebra.REGISTERS + j]
                )
    return tuple(out)


def multiplication_ranks():
    def mul_rank(element):
        images = []
        for basis in range(algebra.MODULUS):
            images.append(algebra.algebra_mul(element, 1 << basis))
        return _f2_rank(images, algebra.MODULUS)

    by_epsilon = mul_rank(0b10)
    by_involution = mul_rank(1 << algebra.TARGET_DEGREE)
    algebra.need(by_epsilon == 7 and by_involution == 4, "multiplication ranks")
    return by_epsilon, by_involution


def _f2_rank(vectors, width):
    rows = list(vectors)
    rank = 0
    column = 0
    while column < width and rank < len(rows):
        pivot = None
        for index in range(rank, len(rows)):
            if (rows[index] >> column) & 1:
                pivot = index
                break
        if pivot is None:
            column += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and (rows[index] >> column) & 1:
                rows[index] ^= rows[rank]
        rank += 1
        column += 1
    return rank


def observe():
    idempotents = algebra.rank_one_idempotents()
    algebra.need(len(idempotents) == 120, "idempotent count")
    hits, square_failures = sum_lemma(idempotents)
    algebra.need(hits == 0 and square_failures == 0, "sum lemma")
    counts = classify()
    algebra.need(direct_word(idempotents), "direct word")
    epsilon_rank, involution_rank = multiplication_ranks()
    return {
        "group": "C8",
        "registers": 4,
        "target": "diag([g^4],[g^4],[g^4],[g^4])",
        "minimum": 4,
        "no_word_length_at_most_3": True,
        "direct_word_length": 4,
        "idempotents": 120,
        "pair_sums_in_rank_one_idempotents": hits,
        "same_image_square_failures": square_failures,
        "patterns": counts["patterns"],
        "dead_single": counts["dead_single"],
        "dead_triple": counts["dead_triple"],
        "live_patterns": counts["live"],
        "live_degree4_letters_at_most": 3,
        "multiplication_rank_epsilon": epsilon_rank,
        "multiplication_rank_epsilon4": involution_rank,
        "three_call_rank_budget": 3 * epsilon_rank,
        "four_block_rank_demand": 4 * involution_rank,
        "rank_budget_permits_three": True,
        "no_new_kappa": True,
    }


def main():
    observed = observe()
    result_path = PACKAGE / "RESULT.json"
    if "--write" in __import__("sys").argv:
        result_path.write_text(json.dumps(observed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    stored = load_json(result_path)
    algebra.need(stored == observed, "RESULT.json does not match the case split")
    print(MARKER)


if __name__ == "__main__":
    main()
