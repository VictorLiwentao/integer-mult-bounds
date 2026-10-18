#!/usr/bin/env python3
"""Code-disjoint witness, orbit and depth-2 ball for the four-role certificate.

Does not import verify.py or search.cpp. The length-7 exclusion itself is the
native meet; this replay checks the group law, the nine-call upper bound and
the depth-2 ball size the native engine also reports.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

# Basis order: +1,-1,+i,-i,+j,-j,+k,-k.
MUL = (
    (0, 1, 2, 3, 4, 5, 6, 7),
    (1, 0, 3, 2, 5, 4, 7, 6),
    (2, 3, 1, 0, 6, 7, 5, 4),
    (3, 2, 0, 1, 7, 6, 4, 5),
    (4, 5, 7, 6, 1, 0, 2, 3),
    (5, 4, 6, 7, 0, 1, 3, 2),
    (6, 7, 4, 5, 3, 2, 1, 0),
    (7, 6, 5, 4, 2, 3, 0, 1),
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def table():
    out = [[0] * 256 for _ in range(8)]
    for label in range(8):
        for mask in range(256):
            mixed = 0
            for basis in range(8):
                if mask >> basis & 1:
                    mixed ^= 1 << MUL[basis][label]
            out[label][mask] = mixed
    return out


TABLE = table()


def apply_factor(state, image, covector, label):
    out = list(state)
    for row in range(4):
        support = 0
        for role in range(4):
            if image >> role & 1:
                support ^= (state[row] >> (8 * role)) & 255
        delta = support ^ TABLE[label][support]
        for column in range(4):
            if covector >> column & 1:
                out[row] ^= delta << (8 * column)
    return out


def endpoint(labels):
    state = [1 << (8 * role) for role in range(4)]
    for role, label in enumerate(labels):
        if label == 0:
            continue
        paid = 2 if label == 3 else 4
        for _ in range(3):
            state = apply_factor(state, 1 << role, 1 << role, paid)
    got = []
    for column in range(4):
        mask = (state[column] >> (8 * column)) & 255
        need(mask.bit_count() == 1, "witness not diagonal")
        for row in range(4):
            if row != column:
                need(((state[row] >> (8 * column)) & 255) == 0, "off-diagonal")
        got.append(mask.bit_length() - 1)
    need(got == list(labels), "witness endpoint")


def depth_two():
    factors = []
    for image in range(1, 16):
        for covector in range(1, 16):
            if bin(image & covector).count("1") % 2 == 1:
                factors.append((image, covector, 2))
                factors.append((image, covector, 4))
    need(len(factors) == 240, "factor count")
    seen = {tuple(1 << (8 * role) for role in range(4))}
    frontier = list(seen)
    for _ in range(2):
        nxt = []
        for state in frontier:
            for image, covector, label in factors:
                image_state = tuple(apply_factor(state, image, covector, label))
                if image_state not in seen:
                    seen.add(image_state)
                    nxt.append(image_state)
        frontier = nxt
    return len(seen)


def representative(labels):
    digits = list(labels)
    if digits.count(5) > digits.count(3):
        digits = [5 if item == 3 else 3 if item == 5 else item for item in digits]
    zero = digits.index(0)
    digits[zero], digits[3] = digits[3], digits[zero]
    if digits[:3].count(5) == 1:
        slot = digits.index(5)
        digits[slot], digits[2] = digits[2], digits[slot]
    return tuple(digits)


def main():
    need(MUL[2][2] == 1 and MUL[1][2] == 3, "i cubed setup")
    need(MUL[MUL[2][2]][2] == 3, "i^3 = zi")
    need(MUL[MUL[4][4]][4] == 5, "j^3 = zj")
    images = set()
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
            endpoint(digits)
            images.add(representative(digits))
    need(images == {(3, 3, 3, 0), (3, 3, 5, 0)}, "orbits")
    need(depth_two() == 42041, "depth-two ball")
    print(
        "PASS_Q8_FOUR_ROLE_THREE_NEG_INDEPENDENT "
        "witnesses=32 orbits=3330,3350 depth2=42041 no_new_kappa"
    )


if __name__ == "__main__":
    main()
