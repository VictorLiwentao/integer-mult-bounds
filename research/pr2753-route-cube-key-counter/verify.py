#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact PR2753 route_cube key/Counter invoice; read-only default.

Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from model import EXPECTED, FIXTURES, predicted, run_suite  # noqa: E402

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"
PASS = "PASS_PR2753_ROUTE_CUBE_KEY_COUNTER"


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=_hook)


def check_source_pins():
    sources = load_json_reject_duplicates(SOURCES_PATH)
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        live = ROOT / rec["path"]
        need(live.is_file(), f"missing input {rec['path']}")
        need(sha256(live) == rec["sha256"], f"source bytes mismatch: {rec['path']}")
    routes = next(r for r in sources["files"] if r["path"].endswith("/routes.py"))
    need(routes["sha256"] == EXPECTED["routes_sha256"], "routes.py digest")


def check_selected_decimal():
    selected = load_json_reject_duplicates(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == EXPECTED["selected_decimal"], "selected decimal")


def build_certificate():
    rows, width_checks = run_suite()
    need(len(rows) == len(FIXTURES), "fixture census")
    for row in rows:
        pred = predicted(row["q"], row["w"], row["dimension"], row["fibre_bits"])
        for key in (
            "partition_count",
            "append_word_calls",
            "append_word_cells",
            "read_word_calls",
            "high_key_calls",
            "copy_key_calls",
            "copy_key_cells",
            "counter_ctors",
            "counter_decrements",
            "counter_closes",
        ):
            need(row[key] == pred[key], f"predicted {key}")
        for key in (
            "append_word_calls",
            "append_word_cells",
            "read_word_calls",
            "high_key_calls",
            "copy_key_calls",
            "copy_key_cells",
            "counter_ctors",
            "counter_decrements",
            "counter_closes",
        ):
            need(row["measured_" + key] == pred[key], f"measured {key}")
        # Non-fibre: append_word cells = H*d^2*(L+1), independent of fibre length F.
        need(
            row["append_word_cells"]
            == row["highs"] * row["coords"] * (row["arena_bits"] + 1),
            "append_word closed form",
        )
    # Same (q,w,d), different F: append_word cells identical (not fibre-volume forced).
    by_qwd = {}
    for row in rows:
        key = (row["q"], row["w"], row["dimension"])
        by_qwd.setdefault(key, []).append(row)
    for key, group in by_qwd.items():
        cells = {r["append_word_cells"] for r in group}
        need(len(cells) == 1, f"append_word independent of F for {key}")
        fibres = {r["fibre_bits"] for r in group}
        if len(fibres) > 1:
            need(len(group) >= 2, "F-variation control present")
    for bits, width in width_checks.items():
        need(width == bits, f"word width lemma bits={bits}")

    return {
        "schema_version": 1,
        "kind": "exact_implementation_key_counter_invoice",
        "claim": {
            "primitive": "routes.route_cube",
            "source_pr": EXPECTED["source_pr"],
            "source_head": EXPECTED["source_head"],
            "fibre_predecessor_pr": EXPECTED["fibre_pr"],
            "metric": (
                "non-fibre: append_word cells/calls, read_word calls, high_key calls, "
                "partition copy_key cells/calls, partition-local Counter lifetimes"
            ),
            "append_word_calls": EXPECTED["append_word_calls"],
            "append_word_cells": EXPECTED["append_word_cells"],
            "read_word_calls": EXPECTED["read_word_calls"],
            "high_key_calls": EXPECTED["high_key_calls"],
            "partition_count_cap_gt_1": EXPECTED["partition_count_cap_gt_1"],
            "copy_key_calls": EXPECTED["copy_key_calls"],
            "copy_key_cells": EXPECTED["copy_key_cells"],
            "counter_ctors": EXPECTED["counter_ctors"],
            "counter_decrements": EXPECTED["counter_decrements"],
            "counter_closes": EXPECTED["counter_closes"],
            "L_identity": EXPECTED["L_identity"],
            "H_identity": EXPECTED["H_identity"],
            "word_width_lemma": EXPECTED["word_width_lemma"],
            "not_fibre_formula_reprint": EXPECTED["not_fibre_formula"],
            "not_high_key_numerical_invoice": EXPECTED["not_high_key_numerical"],
            "no_new_kappa": True,
            "no_supplier_admission": True,
            "selected_decimal": EXPECTED["selected_decimal"],
            "not_algorithmic_optimality": True,
            "not_h2_admission": True,
        },
        "fixtures": rows,
        "word_width_lemma": width_checks,
        "controls": [
            "scaled_chart_w2_d1",
            "cap_eq_1_w1_zero_partition_counters",
            "word_widths_3_5_6_8",
            "d2_w2_key_census",
            "append_word_independent_of_fibre_length",
        ],
    }


def compare_certificate(live, pinned):
    need(live["claim"] == pinned["claim"], "claim mismatch")
    live_w = {str(k): v for k, v in live["word_width_lemma"].items()}
    pinned_w = {str(k): v for k, v in pinned["word_width_lemma"].items()}
    need(live_w == pinned_w, "word width lemma mismatch")
    need(len(live["fixtures"]) == len(pinned["fixtures"]), "fixture count")
    fields = (
        "q", "w", "dimension", "fibre_bits", "arena_bits", "cap", "highs",
        "partition_count",
        "append_word_calls", "append_word_cells",
        "read_word_calls", "high_key_calls",
        "copy_key_calls", "copy_key_cells",
        "counter_ctors", "counter_decrements", "counter_closes",
        "measured_append_word_calls", "measured_append_word_cells",
        "measured_read_word_calls", "measured_high_key_calls",
        "measured_copy_key_calls", "measured_copy_key_cells",
        "measured_counter_ctors", "measured_counter_decrements",
        "measured_counter_closes",
    )
    for got, want in zip(live["fixtures"], pinned["fixtures"]):
        for key in fields:
            need(got[key] == want[key], f"fixture field {key}")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        type=Path,
        default=None,
        help="write a new certificate path; refuses overwrite",
    )
    args = parser.parse_args(argv)

    check_source_pins()
    check_selected_decimal()
    live = build_certificate()

    if args.write is not None:
        need(not args.write.exists(), "refusing to overwrite certificate")
        args.write.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
        print(f"WROTE {args.write}")
        return 0

    pinned = load_json_reject_duplicates(CERT_PATH)
    compare_certificate(live, pinned)
    n = len(live["fixtures"])
    print(f"{PASS} fixtures={n} word_bits={sorted(live['word_width_lemma'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
