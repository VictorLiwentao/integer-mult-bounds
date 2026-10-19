#!/usr/bin/env python3
"""Shared-dirt one-repeat partitioned duals at Q=8; read-only default.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
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
from model import (  # noqa: E402
    EXPECTED,
    census_shared_dirt_onerepeat_26,
    champion_analysis,
    dual_independent_short_long,
    dual_shared_short_long,
    even_odd_tables,
    is_one_repeat_long,
    structural_shared_rank4_outside,
    tariff_qrx,
    valid_restored_walk,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"


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


def build_certificate():
    need(not valid_restored_walk((0,)), "length-1 invalid")

    census = census_shared_dirt_onerepeat_26()
    need(census["covering_pairs"] == EXPECTED["covering_pairs"], "covering")
    need(census["min_R"] == EXPECTED["min_R"], "min R")
    need(census["histogram"] == EXPECTED["histogram"], "hist")
    need(census["valid_one_repeat_walks"] == EXPECTED["valid_one_repeat_walks"], "valid")
    need(
        census["rank4_one_repeat_walks"] == EXPECTED["rank4_one_repeat_walks"],
        "rank4",
    )
    need(
        census["valid_rank_lt4_walks"] == EXPECTED["valid_rank_lt4_walks"],
        "rank_lt4",
    )
    need(census["covering_rank_lt4"] == 0, "rank<4 never covers")

    champ = champion_analysis()
    need(champ["tariff_floor_at_X0"] == EXPECTED["tariff_floor_at_X0"], "tariff floor")
    need(champ["tariff_floor_at_X0"] > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(champ["beats_independent_one_repeat"] is True, "beats independent one-repeat")
    need(champ["beats_shared_dirt_distinct_82"] is False, "does not beat shared-dirt 82")

    w_short, w_long = EXPECTED["champion_walks"]
    need(is_one_repeat_long(w_long), "champ one-repeat")
    e, o = even_odd_tables(w_long)
    need(dual_shared_short_long(e, o, w_short[1]) == 96, "recompute shared R")
    need(dual_independent_short_long(e, w_short[1]) == 112, "recompute independent R")
    need(structural_shared_rank4_outside(w_short[1], w_long)["R_shared"] == 96, "struct")

    cert = {
        "schema_version": 1,
        "status": "PASS_SHARED_DIRT_ONEREPEAT_8Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898) at "
            "(b,a,x)=(38,2,2). Freestanding mixed shared-dirt + one-repeat "
            "partitioned dual at total Q=8 on shape (2,6): every covering "
            "one-repeat length-6 long walk paired with short (0,σ) under joint "
            "even live-read parity has exact R=96; tariff floor at X=0 is "
            "496>436. Saves 16 versus independent one-repeat R=112 but does not "
            "undercut shared-dirt distinct floor R=82 or the six-query endpoint. "
            "Answers independent-walks-9q OQ2 without editing leave-alones "
            "through #2883/#2868/#2867/#2861/#2860/#2858/#2851."
        ),
        "claim": {
            "Q": 8,
            "partition": [2, 6],
            "alphabet": "shared_dirt_one_repeat_partitioned_dual",
            "covering_pairs": EXPECTED["covering_pairs"],
            "min_R": 96,
            "valid_one_repeat_walks": EXPECTED["valid_one_repeat_walks"],
            "rank4_one_repeat_walks": EXPECTED["rank4_one_repeat_walks"],
            "valid_rank_lt4_walks": EXPECTED["valid_rank_lt4_walks"],
            "covering_rank_lt4": 0,
            "independent_one_repeat_min_R": 112,
            "shared_dirt_distinct_min_R": 82,
            "save_vs_independent": 16,
            "tariff_floor_at_X0": EXPECTED["tariff_floor_at_X0"],
            "endpoint_Q6_tariff": EXPECTED["endpoint_tariff_Q6"],
            "undercuts_436_after_complete_bill": False,
            "beats_independent_one_repeat": True,
            "beats_shared_dirt_distinct_82": False,
            "answers_independent_walks_9q_oq2_mixed_shared_dirt_excess": True,
            "oq_answer": (
                "Every covering shared-dirt one-repeat partitioned dual on "
                "shape (2,6) (short walk (0,σ); long walk of length 6 whose five "
                "nonzero slots contain exactly one repeated nonzero label; "
                "shared dirt / joint even live-read parity) has R=96 exactly "
                "(covering 59996160; spectrum {96}). Only rank-4 longs cover, "
                "always with Σe=40 and σ outside the long span (16 choices); "
                "independent dirt on the same pairs has R=112, so shared dirt "
                "saves exactly 16. All 781200 rank<4 valid longs admit "
                "covering_rank_lt4=0; sigma-in-span never covers. Shared-dirt "
                "distinct floor R=82 is not undercut. At X=0 the abstract tariff "
                "is already 496>436 under (b,a,x)=(38,2,2). Leave-alones through "
                "#2883/#2868/#2867/#2861/#2860/#2858/#2851 are not reopened."
            ),
            "no_new_kappa": True,
            "kappa_decimal": "0.001672660197076918",
        },
        "shared_dirt_one_repeat_2_plus_6": census,
        "champion": champ,
        "unit_tariff": {"b": 38, "a": 2, "x": 2},
        "tariff_check": {
            "formula": "38*Q + 2*R + 2*X",
            "at_R96_X0": tariff_qrx(8, 96, 0),
            "champion": tariff_qrx(8, 96, champ["champion"]["path_X"]),
            "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
            "independent_one_repeat_at_R112_X0": tariff_qrx(8, 112, 0),
            "shared_dirt_distinct_at_R82_X0": tariff_qrx(8, 82, 0),
        },
    }
    return cert


def compare_certificate(live, pinned):
    need(live["status"] == pinned["status"], "status")
    need(live["claim"] == pinned["claim"], "claim drift")
    need(
        live["shared_dirt_one_repeat_2_plus_6"]["covering_pairs"]
        == pinned["shared_dirt_one_repeat_2_plus_6"]["covering_pairs"],
        "covering drift",
    )
    need(
        live["shared_dirt_one_repeat_2_plus_6"]["valid_rank_lt4_walks"]
        == pinned["shared_dirt_one_repeat_2_plus_6"]["valid_rank_lt4_walks"],
        "rank_lt4 drift",
    )
    need(
        live["shared_dirt_one_repeat_2_plus_6"]["covering_rank_lt4"]
        == pinned["shared_dirt_one_repeat_2_plus_6"]["covering_rank_lt4"]
        == 0,
        "rank_lt4 cover drift",
    )
    need(
        live["shared_dirt_one_repeat_2_plus_6"]["histogram"]
        == pinned["shared_dirt_one_repeat_2_plus_6"]["histogram"],
        "hist drift",
    )
    need(
        live["shared_dirt_one_repeat_2_plus_6"]["min_R"]
        == pinned["shared_dirt_one_repeat_2_plus_6"]["min_R"],
        "min drift",
    )
    need(live["tariff_check"] == pinned["tariff_check"], "tariff drift")
    need(
        live["champion"]["tariff_floor_at_X0"]
        == pinned["champion"]["tariff_floor_at_X0"],
        "floor",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="rewrite CERTIFICATE.json (maintenance only)",
    )
    args = parser.parse_args(argv)

    check_source_pins()
    live = build_certificate()

    if args.write_certificate:
        CERT_PATH.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
        print("WROTE_CERTIFICATE", CERT_PATH)
        return 0

    pinned = load_json_reject_duplicates(CERT_PATH)
    compare_certificate(live, pinned)
    claim = pinned["claim"]
    print(
        "PASS_SHARED_DIRT_ONEREPEAT_8Q_OBSTRUCTION",
        f"shared_dirt_onerepeat_min_R={claim['min_R']}",
        f"covering={claim['covering_pairs']}",
        f"tariff_floor={claim['tariff_floor_at_X0']}",
        f"independent_one_repeat_min_R={claim['independent_one_repeat_min_R']}",
        f"shared_dirt_distinct_min_R={claim['shared_dirt_distinct_min_R']}",
        "answers_independent_walks_9q_oq2_mixed_shared_dirt_excess",
        "no_undercut_436",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
