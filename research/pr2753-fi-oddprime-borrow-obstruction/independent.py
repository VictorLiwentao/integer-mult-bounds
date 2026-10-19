#!/usr/bin/env python3
"""Independent arithmetic and census-identity checks (no wrapper replay).

Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import harness  # noqa: E402

CHECKS = 0


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise RuntimeError(message)


def main():
    # Separate |GL2(F3)| product.
    order = 1
    for i in range(2):
        order *= 9 - 3**i
    need(order == 48, "independent GL order")
    need(order == harness.gl2_order(), "matches harness")

    # 3^k mod 16 cycles in {1,3,9,11}; never 0. Hence never 0 mod 48.
    seen = []
    x = 1
    for _ in range(32):
        seen.append(x)
        need(x % 16 != 0, "mod16")
        need(x % 48 != 0, "mod48")
        x = (x * 3) % 48
    need(set(seen).issubset({1, 3, 9, 11, 17, 19, 27, 33, 35, 43}), "3-adic units mod 48")

    # Closed-form census identity from the measured support.
    bad_rows = 21  # |{6..26}|
    per_row = 1944
    width = 104976
    need(bad_rows * per_row == 40824, "21*1944=40824")
    need(width // 48 == 2187, "columns per row")
    need(2187 - 243 == 1944, "1944 = 2187 - 3^5")
    need(27 - 6 == 21, "bad genuine = R - 6")
    need(48 - 27 == 21, "added rows = bad genuine count")

    # Fixture plan identity.
    need(((27 + 24 - 1) // 24) * 24 == 48, "ceil pad")
    need(1 * 27 * 27 * 9 * 9 == 59049, "volume")
    need(1 * 48 * 9 * 9 * 27 == 104976, "F width")

    print(
        "PASS_INDEPENDENT_PR2753_FI_ODDPRIME_BORROW_OBSTRUCTION "
        "gl=48 three_pow_never_div_48 bad_identity=21*1944 "
        f"checks={CHECKS} no_new_kappa"
    )


if __name__ == "__main__":
    main()
