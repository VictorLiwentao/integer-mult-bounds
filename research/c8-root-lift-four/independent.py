#!/usr/bin/env python3
"""Exhaustive meet-in-the-middle check that no C8 word of length <= 3 hits.

This file does not import verify.py or algebra.py. Matrix products are the
only exclusion; the augmentation case split is not repeated.
"""

import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
MODULUS = 8
REGISTERS = 4
MARKER = "PASS_C8_ROOT_LIFT_INDEPENDENT searched_length<=3 hits=0 direct=4 no_new_kappa"


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL_C8_ROOT_LIFT_INDEPENDENT " + message)


def load_json(path):
    def pairs(items):
        keys = [key for key, _ in items]
        need(len(keys) == len(set(keys)), "duplicate JSON key in " + path.name)
        return dict(items)

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def algebra_mul(left, right):
    out = 0
    shift = 0
    bits = left
    while bits:
        if bits & 1:
            out ^= right << shift
        bits >>= 1
        shift += 1
    return out & ((1 << MODULUS) - 1)


def build_table():
    table = [[0] * (1 << MODULUS) for _ in range(1 << MODULUS)]
    for left in range(1 << MODULUS):
        for right in range(1 << MODULUS):
            table[left][right] = algebra_mul(left, right)
    return table


def idempotents():
    found = []
    width = 1 << REGISTERS
    for column in range(1, width):
        for row in range(1, width):
            dot = 0
            left, right = column, row
            while left:
                dot ^= (left & 1) & (right & 1)
                left >>= 1
                right >>= 1
            if dot != 1:
                continue
            matrix = 0
            for i in range(REGISTERS):
                if (column >> i) & 1:
                    for j in range(REGISTERS):
                        if (row >> j) & 1:
                            matrix |= 1 << (i * REGISTERS + j)
            found.append(matrix)
    return sorted(set(found))


def increment(exponent, table):
    acc = 1
    base = 0b11
    power = exponent
    while power:
        if power & 1:
            acc = table[acc][base]
        base = table[base][base]
        power >>= 1
    return acc ^ 1


def identity():
    return tuple(1 if i == j else 0 for i in range(REGISTERS) for j in range(REGISTERS))


def target():
    twist = 1 ^ (1 << 4)
    return tuple(twist if i == j else 0 for i in range(REGISTERS) for j in range(REGISTERS))


def factor(matrix, delta):
    out = list(identity())
    for i in range(REGISTERS):
        for j in range(REGISTERS):
            if (matrix >> (i * REGISTERS + j)) & 1:
                out[i * REGISTERS + j] ^= delta
    return tuple(out)


def mul(left, right, table):
    out = [0] * (REGISTERS * REGISTERS)
    for i in range(REGISTERS):
        base_i = i * REGISTERS
        for k in range(REGISTERS):
            entry = left[base_i + k]
            if not entry:
                continue
            row = table[entry]
            base_k = k * REGISTERS
            for j in range(REGISTERS):
                out[base_i + j] ^= row[right[base_k + j]]
    return tuple(out)


def inverse_factor(matrix, delta, table):
    """(I+δN)^{-1} = I + sum_{t>=1} δ^t N, since N^2=N and δ^8=0."""
    out = list(identity())
    power = delta
    for _ in range(1, MODULUS):
        for i in range(REGISTERS):
            for j in range(REGISTERS):
                if (matrix >> (i * REGISTERS + j)) & 1:
                    out[i * REGISTERS + j] ^= power
        power = table[power][delta]
    return tuple(out)


def search():
    table = build_table()
    matrices = idempotents()
    need(len(matrices) == 120, "idempotent count")
    factors = []
    inverses = []
    for exponent in range(1, MODULUS):
        delta = increment(exponent, table)
        for matrix in matrices:
            made = factor(matrix, delta)
            factors.append(made)
            inverses.append(inverse_factor(matrix, delta, table))
            check = mul(made, inverses[-1], table)
            need(check == identity(), "factor inverse")
    need(len(factors) == 840, "factor count")
    goal = target()
    hit1 = goal in set(factors)
    length2 = set()
    for left in factors:
        for right in factors:
            length2.add(mul(left, right, table))
    hit2 = goal in length2
    hit3 = 0
    for inverse in inverses:
        if mul(goal, inverse, table) in length2:
            hit3 += 1
    direct = identity()
    delta = increment(4, table)
    for index in range(REGISTERS):
        axis = 1 << (index * REGISTERS + index)
        direct = mul(direct, factor(axis, delta), table)
    return {
        "hit_length_1": hit1,
        "hit_length_2": hit2,
        "hit_length_3": hit3,
        "length_2_products": len(length2),
        "direct_equals_target": direct == goal,
        "factors": len(factors),
    }


def main():
    found = search()
    need(not found["hit_length_1"] and not found["hit_length_2"], "short hit")
    need(found["hit_length_3"] == 0 and found["direct_equals_target"], "length 3 or direct")
    stored = load_json(PACKAGE / "RESULT.json")
    need(stored["minimum"] == 4, "receipt minimum")
    need(stored["no_word_length_at_most_3"] is True, "receipt exclusion")
    need(stored["idempotents"] == 120 and stored["direct_word_length"] == 4, "receipt shape")
    need(stored["no_new_kappa"] is True, "kappa")
    print(MARKER + " length2_products=" + str(found["length_2_products"]))


if __name__ == "__main__":
    main()
