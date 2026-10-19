#!/usr/bin/env python3
"""Verify depth-six Dic_3 diagonal obstruction (answers predecessor OQ).

Default mode is read-only: rebuild the census and compare CERTIFICATE.json.
Use --write only to regenerate the receipt. Admission uses need(); -O passes.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_BIT_DICYCLIC_DIAGONAL_SIX "
    "group=Dic_3 registers=3 ops=56 products=94727 "
    "eligible=890 hits=0 misses=890 max_calls=6 min_direct=7 no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"
PRIOR_EXPECTED = "research/bit-dicyclic-diagonal-seed620ca/EXPECTED.json"
INPUTS = (PRIOR_EXPECTED,)
BASE_COMMIT = "bb4bccbf42844d2801487450727c2f63e10d1d0f"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key: " + str(key))
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 8_000_000, "input exceeds 8 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    need(manifest["base_commit"] == BASE_COMMIT, "base commit pin")
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


def cross_check_predecessor(pinned):
    prior = json.loads(pinned[PRIOR_EXPECTED], object_pairs_hook=pairs_unique)
    need(prior["group"] == "Dic_3", "prior group")
    need(prior["paid_operation_types"] == 56, "prior ops")
    need(prior["group_elements"] == 12, "prior order")
    hist = prior["distinct_products_by_minimum_depth_through_three"]
    need(hist == {"0": 1, "1": 56, "2": 2352, "3": 92318}, "prior depth-3 hist")
    need(prior["depth_four_stage"]["eligible_targets_with_word"] == 0, "prior depth4")
    need(prior["depth_five_pivot"]["eligible_targets_with_word"] == 0, "prior depth5")
    return prior


def load_search():
    return runpy.run_path(str(HERE / "search.py"))


def build_certificate(ns, prior):
    report = ns["search"]()
    layer = report["depth_six_layer"]
    need(report["kappa_decimal"] == KAPPA_DECIMAL, "kappa decimal")
    need(report["kappa_fraction"] == KAPPA_FRACTION, "kappa fraction")
    need(report["no_new_kappa"] is True, "no new kappa")
    need(layer["max_calls"] == 6, "max_calls")
    need(layer["minimum_direct_bill"] == 7, "min direct")
    need(layer["endpoint_count"] == 890, "eligible count")
    need(layer["eligible_targets_with_word"] == 0, "hits")
    need(layer["eligible_targets_without_word"] == 890, "misses")
    need(layer["best"] is None, "best empty")
    need(report["result_hits"] == 0 and report["result_misses"] == 890, "result")
    for i in range(12):
        need(
            report["positive_generator_distances"][str(i)]
            == prior["positive_generator_distances"][str(i)],
            "distance at " + str(i),
        )
    return {
        "schema_version": 1,
        "package": "research/bit-dicyclic-diagonal-six",
        "claim": (
            "In the Dic_3 {u,v}-paid three-register model, every diagonal "
            "triple with positive-generator direct bill at least 7 has no "
            "paid word of length at most 6."
        ),
        "group": "Dic_3",
        "registers": 3,
        "paid_operation_types": 56,
        "distinct_product_count_through_three": 94727,
        "distinct_products_by_minimum_depth_through_three": {
            "0": 1,
            "1": 56,
            "2": 2352,
            "3": 92318,
        },
        "depth_six_layer": {
            "max_calls": 6,
            "minimum_direct_bill": 7,
            "endpoint_count": 890,
            "eligible_targets_with_word": 0,
            "eligible_targets_without_word": 890,
            "hits": [],
            "best": None,
            "coverage_sha256": layer["coverage_sha256"],
        },
        "predecessor_depth_four_hits": 0,
        "predecessor_depth_five_hits": 0,
        "no_new_kappa": True,
        "kappa_decimal": KAPPA_DECIMAL,
        "kappa_fraction": KAPPA_FRACTION,
        "selected_kappa_unchanged": True,
    }


def compare_certificate(fresh, committed_path):
    committed = read_json(committed_path)
    need(fresh == committed, "certificate mismatch versus committed receipt")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate CERTIFICATE.json (explicit write path)",
    )
    args = parser.parse_args(argv)
    pinned = pin_sources()
    prior = cross_check_predecessor(pinned)
    ns = load_search()
    cert = build_certificate(ns, prior)
    cert_path = HERE / "CERTIFICATE.json"
    if args.write:
        cert_path.write_text(
            json.dumps(cert, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        need(cert_path.is_file(), "committed CERTIFICATE.json missing")
        compare_certificate(cert, cert_path)
        # Read-only: working tree package files must still match pins for inputs.
        for path in INPUTS:
            raw = (ROOT / path).read_bytes()
            need(
                hashlib.sha256(raw).hexdigest()
                == hashlib.sha256(pinned[path]).hexdigest(),
                "input drifted during verify: " + path,
            )
    print(MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
