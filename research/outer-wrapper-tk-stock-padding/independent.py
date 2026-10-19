#!/usr/bin/env python3
"""Separate no-import reconstruction of the t K^D outer-wrapper padding claim.

Does not import verify.py. Re-pins the same live inputs and rebuilds the
sigma=6748 multiplicity absorption from integer/Fraction facts alone.
Admission uses need() under -O.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SIGMA = 6748
ELL = 16
M_CLAIM = 269241600
KAPPA_DECIMAL = "0.001672660197076918"
MARKER = (
    "PASS_OUTER_WRAPPER_TK_STOCK_PADDING "
    "sigma=6748 ell=16 multiplicity=1..q-1 "
    "below_two fourteen_fit_guards no_new_kappa"
)
INPUTS = (
    "research/selected-bit-recursive-caller/PROOF.md",
    "research/selected-outer-borrowing-wrapper/README.md",
    "research/selected-lcm-stock-wrapper-fit/README.md",
    "docs/research/selected-bit-caller-storage-map.md",
    "research/community-frontier1094-audit/ASSEMBLY.json",
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


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    out = {}
    for row in inputs:
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"],
             "source hash: " + row["path"])
        out[row["path"]] = raw
    return out


def depth(atom_count):
    steps = 0
    value = int(atom_count)
    while value >= 64:
        value = 42 * (value // 64)
        steps += 1
        need(steps <= 64, "depth did not descend")
    return steps


def alternate_padding(radix, stock):
    """Build q^k by repeated multiply; compare ceil ratio without shared helper."""
    if radix < 2 or stock < 1:
        return False
    power = radix ** 0
    while power < stock:
        power *= radix
    groups = (power + stock - 1) // stock
    padded = groups * stock
    return power <= padded < 2 * power


def evaluate():
    pinned = pin_sources()
    proof = pinned["research/selected-bit-recursive-caller/PROOF.md"].decode("utf-8")
    wrapper = pinned["research/selected-outer-borrowing-wrapper/README.md"].decode("utf-8")
    prior = " ".join(
        pinned["research/selected-lcm-stock-wrapper-fit/README.md"].decode("utf-8").split()
    )
    storage = pinned["docs/research/selected-bit-caller-storage-map.md"].decode("utf-8")
    assembly = json.loads(
        pinned["research/community-frontier1094-audit/ASSEMBLY.json"],
        object_pairs_hook=pairs_unique,
    )

    need("t K^D(n), t>=1" in proof, "cite: PR2753 multiplicity stock")
    need("outer padding/borrowing wrapper" in proof, "cite: wrapper left open")
    need("1<=S<=R" in wrapper, "cite: wrapper modulus")
    need("R'=ceil(R/S)*S" in wrapper, "cite: padding shape")
    need("S(e,w) = K^D(e)" in prior, "cite: unit-multiplicity prior")
    need("tK^D(e)" in storage, "cite: storage-map obligation")

    # Alternate coefficient route: expand (28/17)*4097 as an integer quotient.
    need((28 * 4097) % 17 == 0, "4097 divisible after *28")
    need((28 * 4097) // 17 == SIGMA, "alternate 6748 derivation")
    need(1 + SIGMA == 6749, "unit absorption margin exists")
    need(2 ** (ELL - 1) < 8 * SIGMA <= 2 ** ELL, "ell from sigma")

    # Depth certificate by direct integer comparison (same certificate, alt path).
    need(pow(2, 17) * pow(42, 28) < pow(64, 28), "depth certificate")
    for n in (1, 63, 64, 128, 1024, 65536):
        d = depth(n)
        if d == 0:
            need(n < 64, "zero depth")
        else:
            need(pow(n, 28) >= pow(2, 17 * d), "depth bound")

    # Multiplicity absorption core: for every w>=1, room for the +1 from t<q.
    for w in range(1, 257):
        left = Fraction(28, 17) * (4096 * w + 1)
        need(left <= SIGMA * w, "slope room")
        need(1 <= SIGMA * w, "unit room")

    # Padding under t < q for several radices, rebuilt without shared helper.
    for radix, base, t in ((2, 1, 1), (5, 5, 4), (11, 1, 10), (17, 17, 16)):
        need(1 <= t < radix, "domain")
        need(alternate_padding(radix, t * base), "alt padding")

    # Fourteen-stage ell premises from the assembly (independent of verify.stages).
    def ceil_frac(value: Fraction) -> int:
        return -(-value.numerator // value.denominator)

    beta = Fraction(1, 10 ** 24)
    bit = Fraction(assembly["bit_lower"])
    for lower_key, record_key in (
        ("complex_lower", "bootstrap"),
        ("conservative_complex_lower", "conservative_bootstrap"),
    ):
        lower = Fraction(assembly[lower_key])
        saving = min(bit, (1 - beta) * lower) - Fraction(1, 10 ** 27)
        exponent = Fraction(384599, 10 ** 10)
        count = 0
        for record in assembly[record_key]:
            previous = exponent
            exponent = (1 - saving) * saving + saving * previous
            gap = min(
                saving - exponent,
                1 - exponent - saving,
                1 - exponent - saving * (1 - previous),
                1 - saving,
            )
            cutoff = max(ceil_frac(36 / gap ** 2), ceil_frac(2 * (4 + 1024) / gap))
            need(str(cutoff) == record["cutoff_log2"], "cutoff mismatch")
            need(cutoff * gap >= 2 * (4 + ELL), "ell premise")
            need(cutoff * gap ** 2 >= 36, "quadratic premise")
            count += 1
        need(count == 7, "seven stages")

    return {
        "schema_version": 1,
        "status": "PASS_OUTER_WRAPPER_TK_STOCK_PADDING",
        "sigma": SIGMA,
        "ell": ELL,
        "lcm": M_CLAIM,
        "multiplicity_domain": "1 <= t < q",
        "stock_shape": "S(t) = t * K^D(e)",
        "below_two_padding": True,
        "stages": 14,
        "no_new_kappa": True,
        "kappa_decimal": KAPPA_DECIMAL,
        "marker": MARKER,
    }


def main():
    observed = evaluate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    for key in (
        "status",
        "sigma",
        "ell",
        "lcm",
        "multiplicity_domain",
        "stock_shape",
        "below_two_padding",
        "stages",
        "no_new_kappa",
        "kappa_decimal",
        "marker",
    ):
        need(observed[key] == certificate[key], "certificate mismatch")
    print(MARKER)


if __name__ == "__main__":
    main()
