"""Shared-free helpers are duplicated on purpose in the two checkers.

This module is the primary augmentation calculus. independent.py does not
import it.
"""

from __future__ import annotations

MODULUS = 8
TARGET_DEGREE = 4
REGISTERS = 4


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL_C8_ROOT_LIFT_FOUR " + message)


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


def increment(exponent):
    """Return (1+ε)^exponent + 1 in F2[ε]/(ε^8)."""
    need(1 <= exponent < MODULUS, "exponent")
    acc = 1
    base = 0b11
    power = exponent
    while power:
        if power & 1:
            acc = algebra_mul(acc, base)
        base = algebra_mul(base, base)
        power >>= 1
    return acc ^ 1


def reduce_word(word):
    out = []
    for index in word:
        if out and out[-1] == index:
            continue
        out.append(index)
    return tuple(out)


def multiply_expr(left, right):
    out = set()
    for prefix in left:
        for suffix in right:
            word = reduce_word(prefix + suffix)
            if word in out:
                out.remove(word)
            else:
                out.add(word)
    return frozenset(out)


def add_expr(left, right):
    return left.symmetric_difference(right)


def factor_series(poly, index):
    series = [frozenset() for _ in range(MODULUS)]
    series[0] = frozenset([()])
    letter = frozenset([(index,)])
    bit = 0
    value = poly
    while value:
        if value & 1:
            series[bit] = add_expr(series[bit], letter)
        value >>= 1
        bit += 1
    return series


def multiply_series(left, right):
    out = [frozenset() for _ in range(MODULUS)]
    for i, term in enumerate(left):
        if not term:
            continue
        for j, other in enumerate(right):
            if not other or i + j >= MODULUS:
                continue
            out[i + j] = add_expr(out[i + j], multiply_expr(term, other))
    return out


def word_series(labels):
    series = [frozenset() for _ in range(MODULUS)]
    series[0] = frozenset([()])
    for index, exponent in enumerate(labels):
        series = multiply_series(series, factor_series(increment(exponent), index))
    return series


def substitute(expr, source, dest):
    out = set()
    for word in expr:
        replaced = reduce_word(tuple(dest if item == source else item for item in word))
        if replaced in out:
            out.remove(replaced)
        else:
            out.add(replaced)
    return frozenset(out)


def reduce_low_degrees(series):
    """Cancel pure two-letter low degrees. Return dead, live, or unknown."""
    exprs = [set(term) for term in series]
    for _ in range(8):
        acted = False
        for degree in (1, 2, 3):
            term = exprs[degree]
            if not term:
                continue
            pure = all(len(word) == 1 for word in term)
            if pure and len(term) in (1, 3):
                return ("dead", len(term), degree, None)
            if pure and len(term) == 2:
                first, second = sorted(word[0] for word in term)
                exprs = [substitute(item, second, first) for item in exprs]
                acted = True
                break
        if acted:
            continue
        for degree in (1, 2, 3):
            if exprs[degree]:
                return ("unknown", degree, None, None)
        degree4 = exprs[4]
        if any(len(word) != 1 for word in degree4) or len(degree4) > 3:
            return ("unknown", 4, None, None)
        return ("live", len(degree4), None, frozenset(degree4))
    return ("unknown", None, None, None)


def rank_one_idempotents(registers=REGISTERS):
    found = []
    width = 1 << registers
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
            for i in range(registers):
                if (column >> i) & 1:
                    for j in range(registers):
                        if (row >> j) & 1:
                            matrix |= 1 << (i * registers + j)
            found.append(matrix)
    return sorted(set(found))


def matrix_rank(matrix, registers=REGISTERS):
    rows = [(matrix >> (i * registers)) & ((1 << registers) - 1) for i in range(registers)]
    rank = 0
    column = 0
    while column < registers and rank < registers:
        pivot = None
        for index in range(rank, registers):
            if (rows[index] >> column) & 1:
                pivot = index
                break
        if pivot is None:
            column += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(registers):
            if index != rank and (rows[index] >> column) & 1:
                rows[index] ^= rows[rank]
        rank += 1
        column += 1
    return rank


def matrix_mul(left, right, registers=REGISTERS):
    out = 0
    for i in range(registers):
        for k in range(registers):
            if (left >> (i * registers + k)) & 1:
                for j in range(registers):
                    if (right >> (k * registers + j)) & 1:
                        out ^= 1 << (i * registers + j)
    return out
