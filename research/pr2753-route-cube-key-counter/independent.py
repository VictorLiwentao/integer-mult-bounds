#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent closed-form check for PR2753 route_cube key/Counter invoice.

Does not import verify.py or model.py. Re-derives the non-fibre formulas from
the authenticated routes.py loop shape and recomputes fixture arithmetic.

Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERT_PATH = HERE / "CERTIFICATE.json"
ROUTES = ROOT / "research/selected-bit-recursive-caller/predecessor/vendor/routes.py"
PASS = "PASS_INDEPENDENT_PR2753_ROUTE_CUBE_KEY_COUNTER"


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=_hook)


def predict(q, w, dimension, fibre_bits):
    modulus = q**w
    bits = modulus.bit_length() + 1
    cap = modulus // q
    highs = cap ** (dimension * dimension)
    coords = dimension * dimension
    partitions = coords * bits if cap > 1 else 0
    word_cells = bits + 1
    append_calls = highs * coords
    append_cells = append_calls * word_cells
    return {
        "arena_bits": bits,
        "cap": cap,
        "highs": highs,
        "partition_count": partitions,
        "append_word_calls": append_calls,
        "append_word_cells": append_cells,
        "read_word_calls": highs * coords,
        "high_key_calls": highs,
        "copy_key_calls": 2 * highs * partitions,
        "copy_key_cells": 2 * highs * partitions * coords * word_cells,
        "counter_ctors": 3 * partitions,
        "counter_decrements": 2 * highs * partitions,
        "counter_closes": 3 * partitions,
    }


def check_routes_structure():
    text = ROUTES.read_text(encoding="utf-8")
    digest = hashlib.sha256(ROUTES.read_bytes()).hexdigest()
    if digest != "ed7dc3679451696ab1dd841146b215c9515a3eec5e4ff3763f33c315f1696ada":
        fail("routes.py digest drift")
    for needle in (
        "def route_cube(",
        "def partition(",
        "def high_key(",
        "def copy_key(",
        "append_word(decorated, digit)",
        "bit = copy_key(source, key, context, coordinate, cursor)",
        "copy_key(bucket, output, context)",
        "records = Counter(context.highs)",
        "remaining = Counter(count)",
        "actual = read_word(current, arena)",
        "key = high_key(high.digits, route, chart, context)",
        "if context.raw.compare(context.cap, context.ring.one) > 0:",
    ):
        if needle not in text:
            fail(f"missing structural marker: {needle}")
    # Must not claim the fibre write formula in this package's certificate path.
    if "(2*d*d*L + 2)*V" in text:
        fail("unexpected fibre formula text inside routes.py")


def main():
    check_routes_structure()
    cert = load_json_reject_duplicates(CERT_PATH)
    claim = cert["claim"]
    if claim["append_word_cells"] != "H*d*d*(L+1)":
        fail("append_word formula text")
    if claim["counter_decrements"] != "2*H*P":
        fail("counter formula text")
    if claim["selected_decimal"] != "0.001672660197076918":
        fail("selected decimal")
    if claim["no_new_kappa"] is not True or claim["no_supplier_admission"] is not True:
        fail("kappa/supplier flags")
    if claim["not_fibre_formula_reprint"] is not True:
        fail("must not reprint fibre formula")
    if claim["not_high_key_numerical_invoice"] is not True:
        fail("high_key numerical remains open")
    # Certificate must not embed the fibre write identity.
    blob = json.dumps(cert, sort_keys=True)
    if "(2*d*d*L + 2)*V" in blob or "(2*d*d*L+2)*V" in blob:
        fail("certificate reprints fibre formula")

    for row in cert["fixtures"]:
        pred = predict(row["q"], row["w"], row["dimension"], row["fibre_bits"])
        for key, value in pred.items():
            if row[key] != value:
                fail(f"closed form drift for {key} in {row}")
            measured = "measured_" + key
            if measured in row and row[measured] != value:
                fail(f"measured drift for {key}")

    for bits, width in cert["word_width_lemma"].items():
        if int(bits) != width:
            fail(f"word width lemma {bits}")

    # F-independence of append_word cells.
    groups = {}
    for row in cert["fixtures"]:
        groups.setdefault((row["q"], row["w"], row["dimension"]), []).append(row)
    saw_f_variation = False
    for group in groups.values():
        if len({r["fibre_bits"] for r in group}) > 1:
            saw_f_variation = True
            if len({r["append_word_cells"] for r in group}) != 1:
                fail("append_word depends on F")
    if not saw_f_variation:
        fail("missing F-variation control")

    print(f"{PASS} fixtures={len(cert['fixtures'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
