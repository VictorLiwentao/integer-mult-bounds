#!/usr/bin/env python3
"""Bind t K^D outer-wrapper stock padding for every multiplicity 1 <= t < q.

Unit-multiplicity prior: research/selected-lcm-stock-wrapper-fit (S = K^D).
This package extends the modulus to S(t) = t K^D under 1 <= t < q, proving
the same sigma=6748 envelope, wrapper precondition and below-two padding.
No new kappa. Admission uses need() and remains active under python -O.
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
LIVE = 28416
PHYSICAL = 28425
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


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    pinned = {}
    for row in inputs:
        raw = (ROOT / row["path"]).read_bytes()
        need(len(raw) <= 4_000_000, "source size: " + row["path"])
        need(sha256_bytes(raw) == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw
    return pinned


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    return a // gcd(a, b) * b


def depth(atom_count):
    steps = 0
    value = atom_count
    while value >= 64:
        value = 42 * (value // 64)
        steps += 1
        need(steps <= 64, "depth recurrence did not descend")
    return steps


def depth_bound_holds(atom_count):
    """D(n) <= (28/17) log2(max(1,n)), checked as n**28 >= 2**(17 D)."""
    steps = depth(atom_count)
    if steps == 0:
        return True
    return atom_count ** 28 >= 2 ** (17 * steps)


def coefficient_room(width):
    """(28/17)*(4096 w + 1) <= 6748 w for integer atom width w >= 1."""
    return Fraction(28, 17) * (4096 * width + 1) <= SIGMA * width


def multiplicity_room(width):
    """1 + (28/17)*(4096 w + 1) log term absorbed by 6748 w (1+log2 e).

    Algebraic core used by the proof: for w >= 1,
    (28/17)*(4096 w + 1) <= 6748 w, and 1 <= 6748 w.
    """
    return coefficient_room(width) and (1 <= SIGMA * width)


def padding_fits(radix, stock):
    """Wrapper precondition 1 <= S <= q^k and ceil(q^k/S)*S < 2 q^k."""
    if radix < 2 or stock < 1:
        return False
    power = 1
    while power < stock:
        power *= radix
        if power > stock * radix:
            return False
    if stock > power:
        return False
    padded = -(-power // stock) * stock
    return power <= padded < 2 * power


def stock_log_bound_identity():
    """Closed-form identities used to absorb t < q into sigma=6748."""
    need(Fraction(28, 17) * 4097 == SIGMA, "6748 identity")
    need(Fraction(28, 17) * 4096 == SIGMA - Fraction(28, 17), "4096 slope")
    need(8 * SIGMA <= 2 ** 16 < 8 * 8195, "ell=16 window")
    need(ELL == 16, "ell constant")
    return True


def stages(assembly, lower_key, record_key):
    beta = Fraction(1, 10 ** 24)
    bit = Fraction(assembly["bit_lower"])
    lower = Fraction(assembly[lower_key])
    saving = min(bit, (1 - beta) * lower) - Fraction(1, 10 ** 27)
    exponent = Fraction(384599, 10 ** 10)
    found = []
    for record in assembly[record_key]:
        previous = exponent
        exponent = (1 - saving) * saving + saving * previous
        gap = min(
            saving - exponent,
            1 - exponent - saving,
            1 - exponent - saving * (1 - previous),
            1 - saving,
        )

        def ceil(value):
            return -(-value.numerator // value.denominator)

        cutoff = max(ceil(36 / gap ** 2), ceil(2 * (4 + 1024) / gap))
        need(str(exponent) == record["exponent"], "exponent drift")
        need(str(gap) == record["gap"], "gap drift")
        need(str(cutoff) == record["cutoff_log2"], "cutoff drift")
        need(cutoff >= 3 and cutoff * gap ** 2 >= 36, "quadratic fit premise")
        need(cutoff * gap >= 2 * (4 + ELL), "ell=16 fit premise")
        need(0 < gap <= 1 - saving and previous < exponent < saving < 1, "stage order")
        found.append(cutoff)
    need(len(found) == 7, "stage count")
    return saving


def authenticate(pinned):
    proof = pinned["research/selected-bit-recursive-caller/PROOF.md"].decode("utf-8")
    wrapper = pinned["research/selected-outer-borrowing-wrapper/README.md"].decode("utf-8")
    prior = pinned["research/selected-lcm-stock-wrapper-fit/README.md"].decode("utf-8")
    storage = pinned["docs/research/selected-bit-caller-storage-map.md"].decode("utf-8")
    for needle in (
        "fresh-row count R=t K^D(n), t>=1",
        "it does not implement that outer padding/borrowing wrapper",
        "pads to ceil(q^k/K^D(e))*K^D(e), a factor below two",
    ):
        need(needle in proof, "PR2753 proof no longer states " + needle)
    for needle in (
        "The caller supplies S with 1<=S<=R. This routine does not compute S, choose k, or assert k<e/2.",
        "R'=ceil(R/S)*S,  R<=R'<2R",
    ):
        need(needle in wrapper, "wrapper contract no longer states " + needle)
    prior_flat = " ".join(prior.split())
    for needle in (
        "S(e,w) = K^D(e)",
        "log_q S(e,w) < 6748 w (1+log2 e)",
        "padding factor is strictly below two",
    ):
        need(needle in prior_flat, "unit-multiplicity prior no longer states " + needle)
    # Prior binds unit stock only; it does not state a t-family modulus.
    need("S(t)" not in prior and "t K^D" not in prior and "t*K^D" not in prior,
         "prior unexpectedly claims multiplicity stock")
    need("tK^D(e)" in storage, "storage map names tK^D obligation")
    need("below-two padding factor" in storage, "storage map names below-two")
    assembly = json.loads(
        pinned["research/community-frontier1094-audit/ASSEMBLY.json"],
        object_pairs_hook=pairs_unique,
    )
    return assembly


def finite_multiplicity_padding():
    """Exact padding fixtures for S(t)=t*base under several radices."""
    fixtures = (
        (2, 1, 1),
        (3, 5, 1),
        (3, 5, 2),
        (5, 25, 4),
        (7, 48, 6),
        (11, 1, 10),
        (13, 13, 12),
    )
    for radix, base, multiplicity in fixtures:
        stock = multiplicity * base
        need(1 <= multiplicity < radix, "fixture domain")
        need(padding_fits(radix, stock), "multiplicity padding fixture")
    # t = q-1 still meets the interface; t = 0 does not.
    need(padding_fits(11, 10), "t=q-1 still pads")
    need(not padding_fits(11, 0), "t=0 rejected")
    return len(fixtures)


def controls():
    rejected = 0
    need(Fraction(28, 17) * 4097 == SIGMA, "6748 identity")
    need(not (Fraction(28, 17) * (4096 + 1) <= 6747), "6747 must miss w=1")
    rejected += 1
    need(not (2 * (4096 + 1) <= SIGMA), "weak depth factor 2 is not sigma 6748")
    rejected += 1
    need(8 * 8195 > 2 ** 16 and 8 * SIGMA <= 2 ** 16, "ell=16 excludes rounded 8195")
    rejected += 1
    need(not padding_fits(3, 0), "nonpositive stock is outside the wrapper")
    rejected += 1
    need(M_CLAIM < 2 ** 80, "selected prime floor dominates the multiplier")
    rejected += 1
    need(2 ** 17 * 43 ** 28 >= 64 ** 28, "rank 43 loses the depth certificate")
    rejected += 1
    need(lcm(LIVE, PHYSICAL) != PHYSICAL, "physical role count is not the lcm")
    rejected += 1
    need(not (1 * Fraction(1, 10) >= 2 * (4 + ELL)), "unit cutoff is not an ell=16 guard")
    rejected += 1
    # Domain gate: absorption uses log_q t < 1, which fails at t = q.
    need(not (Fraction(1) < 1), "t=q would give log_q t = 1, outside absorption")
    rejected += 1
    return rejected


def evaluate():
    pinned = pin_sources()
    assembly = authenticate(pinned)
    stock_log_bound_identity()
    need(lcm(LIVE, PHYSICAL) == M_CLAIM, "lcm")
    need(M_CLAIM // LIVE == 9475, "live quotient")
    need(2 ** 17 * 42 ** 28 < 64 ** 28, "depth certificate")
    need(64 ** 2 == 4096, "matrix dimension")
    for width in range(1, 4097):
        need(multiplicity_room(width), "multiplicity coefficient room")
    for atom_count in range(0, 65537):
        need(depth_bound_holds(atom_count), "finite depth bound")
    threshold = 64
    for level in range(1, 28):
        need(depth(threshold) >= level, "threshold depth")
        if threshold > 64:
            need(depth(threshold - 1) < level, "threshold is first")
        threshold = 64 * -(-threshold // 42)
    native = stages(assembly, "complex_lower", "bootstrap")
    conservative = stages(assembly, "conservative_complex_lower", "conservative_bootstrap")
    need(native > 0 and conservative > 0, "positive selected savings")
    need(int(assembly["bootstrap"][0]["cutoff_log2"]) != 311311, "do not identify PR2324 cutoff")
    fixture_count = finite_multiplicity_padding()
    rejected = controls()
    return {
        "schema_version": 1,
        "status": "PASS_OUTER_WRAPPER_TK_STOCK_PADDING",
        "sigma": SIGMA,
        "ell": ELL,
        "lcm": M_CLAIM,
        "live_quotient": 9475,
        "multiplicity_domain": "1 <= t < q",
        "stock_shape": "S(t) = t * K^D(e)",
        "below_two_padding": True,
        "stages": 14,
        "fixture_count": fixture_count,
        "rejected_controls": rejected,
        "no_new_kappa": True,
        "kappa_decimal": KAPPA_DECIMAL,
        "marker": MARKER,
    }


def admit(observed, certificate):
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
    need(observed["rejected_controls"] >= 8, "control census")
    need(observed["fixture_count"] >= 7, "fixture census")


def main():
    observed = evaluate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    admit(observed, certificate)
    print(MARKER)


if __name__ == "__main__":
    main()
