#!/usr/bin/env python3
"""Odd-kernel source-return host bill vs dyadic (answers #2687 OQ1 first step).

Under the named admitted-screen source-return host bill, coefficient-bit prep
alone (I=0) yields 0 odd fused beats of dyadic on j=0..32, while unit
instantiate/routing I=1 yields exactly one beat at (q=3,j=0). Critical
threshold I*=14/17. No new kappa.

Admission uses need() and remains active under python -O.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_ODD_KERNEL_SOURCE_RETURN_HOST "
    "kernels=[1, 3, 5, 7, 9, 15] j=0..32 "
    "I0_beats=0 I1_beats=1 critical_I=14/17 "
    "first_beat=(3,0) no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"
PRIOR_README = "research/odd-kernel-query-pair/README.md"
PRIOR_TASK = "research/odd-kernel-query-pair/TASK.json"
PRIOR_PROGRAM = "research/odd-kernel-query-pair/program.py"
INPUTS = (PRIOR_PROGRAM,)


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
    need(manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
         "base commit pin")
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


def load_bill():
    return runpy.run_path(str(HERE / "host_bill.py"))


def bind_prior_oq(pinned):
    readme = pinned[PRIOR_README].decode("utf-8")
    task = pinned[PRIOR_TASK].decode("utf-8")
    need("admitted BIT supplier host some small odd-kernel shear" in readme
         or "admitted BIT supplier host" in readme,
         "cite: #2687 README OQ1")
    need("exact source-return boundary" in readme, "cite: source-return first step")
    need("Can an admitted BIT supplier host some small odd-kernel shear"
         in task,
         "cite: #2687 TASK OQ1")
    prog = pinned[PRIOR_PROGRAM].decode("utf-8")
    need("def address_word(k):" in prog, "cite: prior address_word")
    need("def modulus_admits_kernel" in prog, "cite: prior admission")


def cross_check_prior_program(pinned, bill):
    prior = runpy.run_path(str(ROOT / PRIOR_PROGRAM))
    for k in (1, -1, 3, 4, 5, 12, 15, 16, 48, -20, 40):
        ours = bill["word_coefficients"](k)
        theirs = []
        for event in prior["address_word"](k):
            if event[0] != "affine":
                continue
            theirs.append(event[2])
            for _, c in event[3]:
                theirs.append(c)
        need(tuple(ours) == tuple(theirs), f"coeff match k={k}")
        need(bill["T_word"](k) == sum(
            bill["coeff_bit_length"](c) for c in theirs
        ), f"T_word match k={k}")
    # Admission closed form agrees with prior on the named screen.
    for q in bill["KERNELS"]:
        for m in bill["SCREEN"]:
            need(prior["modulus_admits_kernel"](q, m) == (
                m % 2 == 1 and __import__("math").gcd(m, q) == 1
            ), f"admit q={q} m={m}")


def evaluate(write=False):
    pinned = pin_sources()
    bind_prior_oq(pinned)
    bill = load_bill()

    need(len(bill["SCREEN"]) == 49, "screen size 49")
    need(bill["SCREEN"][0] == 3 and bill["SCREEN"][-1] == 99, "screen ends")
    need(bill["fused_fixed"]() == 500, "fused fixed 500")
    need(bill["baseline_fixed"]() == 710, "baseline fixed 710")
    for q, expected in ((1, 49), (3, 32), (5, 39), (7, 42), (9, 32), (15, 25)):
        need(bill["admitted_count"](q) == expected, f"A({q})")

    for k in list(range(-64, 0)) + list(range(1, 65)):
        need(bill["T_word"](k) == bill["closed_form_T_word"](k),
             f"closed form k={k}")

    cross_check_prior_program(pinned, bill)

    # I=0 recovers coefficient-only comparison: zero odd fused beats.
    beats0 = bill["odd_fused_beats"](0)
    need(beats0 == [], "I=0 recovers zero beats")
    for j in range(0, bill["J_MAX"] + 1):
        dy = bill["H_fused"](j, 1, 0)
        for q in bill["ODD_KERNELS"]:
            need(bill["H_fused"](j, q, 0) > dy, f"I=0 odd exceeds q={q} j={j}")

    # Critical I* = 14/17 at (3,0); first integer I with a beat is 1.
    crit = bill["critical_I"](0, 3)
    need(crit == Fraction(14, 17), "critical I*=14/17")
    need(crit < 1 < bill["critical_I"](1, 3), "I=1 is first integer threshold")

    beats1 = bill["odd_fused_beats"](1)
    need(len(beats1) == 1, "exactly one I=1 beat")
    need(beats1[0][:2] == (3, 0), "first beat (3,0)")
    need(beats1[0][2] == 674 and beats1[0][3] == 677, "H(3,0)=674 < 677")

    beats2 = bill["odd_fused_beats"](2)
    need(len(beats2) == 33, "I=2 yields 33 beats (all j for q=3)")
    need(all(q == 3 for q, j, _, _ in beats2), "I=2 beats only q=3")
    need([j for q, j, _, _ in beats2] == list(range(0, 33)), "I=2 all j")

    # Fusion always beats baseline under the full host bill (I-independent save).
    for I in (0, 1, 2, 10):
        for j in range(0, bill["J_MAX"] + 1):
            for q in bill["KERNELS"]:
                save = bill["H_baseline"](j, q, I) - bill["H_fused"](j, q, I)
                need(save > 0, f"fusion saves q={q} j={j} I={I}")
                # Save = 210 + 2 T(a) - T(2a); independent of I and A(q).
                a = q * (1 << j)
                need(save == 210 + 2 * bill["T_word"](a) - bill["T_word"](2 * a),
                     "fusion save closed form")

    # Source-return boundary structural controls.
    for j in (0, 1, 4):
        for q in bill["KERNELS"]:
            need(len(bill["fused_powers"](j, q)) == 3, "fused three queries")
            need(len(bill["baseline_powers"](j, q)) == 4, "baseline four queries")

    selected = read_json(ROOT / "certificates/selected-result.json")
    need(selected.get("kappa") == KAPPA_FRACTION, "selected kappa unchanged")

    # Adversarial: I=0 must not report the I=1 beat; inflated dyadic would fake beats.
    need(not (bill["H_fused"](0, 3, 0) < bill["H_fused"](0, 1, 0)),
         "control: no beat at I=0")
    fake_dy = bill["H_fused"](0, 1, 1) + 100
    need(bill["H_fused"](0, 3, 1) < fake_dy, "positive control inflated dyadic")

    certificate = {
        "schema_version": 1,
        "status": "PASS_ODD_KERNEL_SOURCE_RETURN_HOST",
        "kappa_decimal": KAPPA_DECIMAL,
        "kappa_fraction": KAPPA_FRACTION,
        "no_new_kappa": True,
        "kernels": list(bill["KERNELS"]),
        "odd_kernels": list(bill["ODD_KERNELS"]),
        "j_max": bill["J_MAX"],
        "units": {"C": bill["C"], "X": bill["X"], "D": bill["D"], "R_SR": bill["R_SR"]},
        "fused_fixed": bill["fused_fixed"](),
        "baseline_fixed": bill["baseline_fixed"](),
        "screen": {
            "name": "ODD_MODULI_3_99",
            "size": len(bill["SCREEN"]),
            "first": bill["SCREEN"][0],
            "last": bill["SCREEN"][-1],
            "admitted_counts": {str(q): bill["admitted_count"](q)
                                for q in bill["KERNELS"]},
        },
        "bill": {
            "name": "source_return_admitted_screen_host",
            "definition": (
                "H_fused(q,j;I)=3C+2X+18D+R_SR+T_fused(q,j)+I*A(q); "
                "H_baseline(q,j;I)=4C+4X+24D+R_SR+T_baseline(q,j)+I*A(q); "
                "T_* is ADDRESS_affine_coeff_num_den_bit_sum; "
                "A(q)=|{m in SCREEN: gcd(m,q)=1}|; "
                "R_SR charges immutable-source certificate + exclusive-target return once."
            ),
        },
        "counts": {
            "I0_odd_fused_beats_dyadic": 0,
            "I1_odd_fused_beats_dyadic": 1,
            "I2_odd_fused_beats_dyadic": 33,
        },
        "critical_I": {
            "kernel": 3,
            "j": 0,
            "fraction": "14/17",
            "numerator": 14,
            "denominator": 17,
        },
        "first_beat_I1": {
            "kernel": 3,
            "j": 0,
            "H_odd": 674,
            "H_dyadic": 677,
            "margin": 3,
        },
        "claim": {
            "I0_recovers_coeff_only_zero_beats": True,
            "I1_has_exactly_one_odd_fused_beat": True,
            "fusion_always_beats_baseline_on_grid": True,
            "source_return_boundary_named": True,
        },
    }

    cert_path = HERE / "CERTIFICATE.json"
    if write:
        cert_path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    else:
        on_disk = read_json(cert_path)
        need(on_disk == certificate, "certificate mismatch")

    print(MARKER)
    return certificate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true",
                        help="regenerate CERTIFICATE.json")
    args = parser.parse_args()
    evaluate(write=args.write)


if __name__ == "__main__":
    main()
