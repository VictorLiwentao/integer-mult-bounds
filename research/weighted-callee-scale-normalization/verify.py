#!/usr/bin/env python3
"""Scale-normalize the failing P_(2,1) callee for the ordinary wrapper.

Answers weighted-wrapper-contract OQ1 with an exact paid normalization bill.
No new kappa. Admission uses need(); remains active under python -O.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_WEIGHTED_CALLEE_SCALE_NORMALIZATION "
    "M=3 n=2 a=(2,1) "
    "raw_agreements=9/81 "
    "normalized_agreements=81/81 "
    "scales_two_F=36 "
    "no_new_kappa"
)
PRIOR_TASK = "research/weighted-wrapper-contract/TASK.json"
PRIOR_README = "research/weighted-wrapper-contract/README.md"
PRIOR_ALGEBRA = "research/weighted-wrapper-contract/algebra.py"
INPUTS = (PRIOR_TASK, PRIOR_README, PRIOR_ALGEBRA)


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
    need(
        manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "base commit pin",
    )
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    pinned = {}
    for row in rows:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(len(raw) == row["size_bytes"], "source size: " + row["path"])
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw
    return pinned


def bind_prior_oq(pinned):
    task = pinned[PRIOR_TASK].decode("utf-8")
    readme = pinned[PRIOR_README].decode("utf-8")
    need(
        "Can a proposed weighted callee be normalized cheaply enough"
        in task,
        "cite: weighted-wrapper-contract TASK OQ1",
    )
    need(
        "Can one concrete weighted callee be normalized at an affordable complete cost?"
        in readme,
        "cite: weighted-wrapper-contract README OQ",
    )
    need("Theorem 1 (necessary and sufficient contract)" in readme, "cite: Thm 1")
    need("a_i a_(n-1-i)=1 mod M" in readme, "cite: weight involution criterion")

def load_normalize():
    return runpy.run_path(str(HERE / "normalize.py"))


def cross_check_prior_algebra(pinned, norm):
    """Prior word() on index encoding must agree with our wrapper on raw F_a."""
    algebra = runpy.run_path(str(ROOT / PRIOR_ALGEBRA))
    vectors = norm["vectors"]()
    index = {v: i for i, v in enumerate(vectors)}
    # Build P and Pinv as index maps matching prior linear style.
    p_map = []
    pinv_map = []
    for v in vectors:
        p_map.append(index[norm["apply_P"](v)])
        pinv_map.append(index[norm["apply_P_inv"](v)])
    add = tuple(
        tuple(index[tuple((a + b) % 3 for a, b in zip(x, y))] for y in vectors)
        for x in vectors
    )
    sub = tuple(
        tuple(index[tuple((a - b) % 3 for a, b in zip(x, y))] for y in vectors)
        for x in vectors
    )
    agrees = 0
    for h in range(len(vectors)):
        for d in range(len(vectors)):
            oh, od = algebra["word"](h, d, p_map, pinv_map, p_map, pinv_map, add, sub)
            if (oh, od) == (d, h):
                agrees += 1
            # Our wrapper with F_a must match prior word on the same pair.
            hv, dv = vectors[h], vectors[d]
            oh2, od2 = norm["wrapper_word"](hv, dv, norm["F_a"])
            need(
                (index[oh2], index[od2]) == (oh, od),
                f"prior word mismatch at {hv},{dv}",
            )
    need(agrees == norm["RAW_AGREEMENTS"], "prior raw agreement count")


def evaluate(write=False):
    pinned = pin_sources()
    bind_prior_oq(pinned)
    norm = load_normalize()

    need(norm["MODULUS"] == 3 and norm["DIMENSION"] == 2, "fixture shape")
    need(norm["WEIGHTS"] == (2, 1), "proposed weights")
    need(norm["V"] == 9, "volume")
    need(norm["SCALES_TWO_F"] == 36, "two-call scale bill")

    # P^2 = 2 I on the proposed map.
    for v in norm["vectors"]():
        twice = norm["apply_P"](norm["apply_P"](v))
        need(twice == tuple((2 * x) % 3 for x in v), f"P^2=2I at {v}")

    # P' = T P is an involution.
    for v in norm["vectors"]():
        need(
            norm["apply_P_prime"](norm["apply_P_prime"](v)) == v,
            f"(P')^2=I at {v}",
        )

    # Norm o F_a equals F_{P'} pointwise.
    for h in norm["vectors"]():
        for d in norm["vectors"]():
            need(
                norm["F_normalized"](h, d) == norm["F_prime"](h, d),
                f"Norm o F_a = F_P' at {h},{d}",
            )

    # Raw wrapper fails; formula (5) matches.
    raw_agrees, raw_total = norm["census"](norm["F_a"])
    need(raw_total == 81, "raw total")
    need(raw_agrees == norm["RAW_AGREEMENTS"], "raw agreements constant")
    need(
        raw_agrees == norm["formula5_agreements"](),
        "formula (5) raw agreements",
    )
    need(raw_agrees == 9, "raw agreements = 9")
    need(raw_total - raw_agrees == 72, "raw failures = 72")

    # Normalized wrapper attains J everywhere.
    norm_agrees, norm_total = norm["census"](norm["F_normalized"])
    need(norm_total == 81, "normalized total")
    need(norm_agrees == 81, "normalized perfect")
    # Direct F_prime path agrees.
    prime_agrees, _ = norm["census"](norm["F_prime"])
    need(prime_agrees == 81, "direct P' path")

    cross_check_prior_algebra(pinned, norm)

    bill = norm["bill"]()
    need(bill["scales_two_F"] == 36, "bill scales")
    need(bill["input_restores"] == 0, "no input restore")
    need(bill["weight_table_rewrites"] == 0, "weights stay (2,1)")

    # Selected kappa unchanged.
    selected = read_json(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == norm["KAPPA_DECIMAL"], "kappa decimal")
    need(selected["kappa"] == norm["KAPPA_FRACTION"], "kappa fraction")

    # Negative controls: omitted scales, wrong factor, and raw F_a (already counted).
    def omit_both_scales(h, d, modulus=3):
        return norm["F_a"](h, d, modulus=modulus)

    def omit_d_scale(h, d, modulus=3):
        hh, dd = norm["F_a"](h, d, modulus=modulus)
        hh = list(hh)
        hh[1] = (hh[1] * 2) % modulus
        return tuple(hh), dd  # D'[0] not scaled

    def wrong_factor(h, d, modulus=3):
        hh, dd = norm["F_a"](h, d, modulus=modulus)
        hh = list(hh)
        dd = list(dd)
        hh[1] = (hh[1] * 0) % modulus  # annihilating scale
        dd[0] = (dd[0] * 2) % modulus
        return tuple(hh), tuple(dd)

    for name, callee, expect_agrees in (
        ("omit_both_scales", omit_both_scales, 9),
        ("omit_d_scale", omit_d_scale, None),
        ("wrong_factor", wrong_factor, None),
    ):
        agrees, total = norm["census"](callee)
        need(agrees < total, f"control {name} must not be perfect")
        need(agrees != 81, f"control {name} imperfect")
        if expect_agrees is not None:
            need(agrees == expect_agrees, f"control {name} agreements")
    certificate = {
        "schema_version": 1,
        "claim": (
            "Post-scales T=diag(1,2) after each F_(2,1) realize involutory P'; "
            "ordinary wrapper attains J with exact bill scales_two_F=4V=36"
        ),
        "fixture": {
            "modulus": 3,
            "dimension": 2,
            "weights": [2, 1],
            "scale_T": [1, 2],
            "volume_V": 9,
        },
        "counts": {
            "raw_agreements": raw_agrees,
            "raw_total": raw_total,
            "raw_failures": raw_total - raw_agrees,
            "normalized_agreements": norm_agrees,
            "normalized_total": norm_total,
            "scales_per_F": bill["scales_per_F"],
            "scales_two_F": bill["scales_two_F"],
            "input_restores": 0,
            "weight_table_rewrites": 0,
            "negative_controls": 3,
        },
        "kappa": {
            "decimal": norm["KAPPA_DECIMAL"],
            "fraction": norm["KAPPA_FRACTION"],
            "changed": False,
        },
        "marker": MARKER,
    }

    receipt = HERE / "CERTIFICATE.json"
    if write:
        receipt.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    else:
        need(receipt.is_file(), "CERTIFICATE.json missing")
        committed = read_json(receipt)
        need(committed == certificate, "certificate mismatch")

    print(MARKER)
    return certificate


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate CERTIFICATE.json (explicit write path only)",
    )
    args = parser.parse_args(argv)
    evaluate(write=args.write)


if __name__ == "__main__":
    main()
