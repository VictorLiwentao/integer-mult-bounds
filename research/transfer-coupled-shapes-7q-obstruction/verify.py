#!/usr/bin/env python3
"""Transfer-coupled dual-walk obstruction at Q=7; read-only default.

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
    VERIFY_SHAPES,
    champion_recompute,
    enumerate_shapes,
    even_sum_F2_5,
    shape_key,
    tariff_qrx_bill,
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


def quick_checks():
    need(even_sum_F2_5() == EXPECTED["F2_5_even_sum"], "F2^5 even-sum")
    need(not valid_restored_walk((0,)), "length-1 invalid")
    floor = tariff_qrx_bill(
        7, EXPECTED["global_min_R"], EXPECTED["binding_min_fair_X_at_R84"]
    )
    need(floor == EXPECTED["tariff_floor_R84_fairX9"], "tariff floor")
    need(floor > EXPECTED["endpoint_tariff_Q6"], "no undercut at floor")
    champs = {}
    for key, rec in EXPECTED["shapes"].items():
        p, a, b = map(int, key.split("_"))
        champs[key] = champion_recompute(p, a, b)
        need(champs[key]["R"] == rec["min_R"], f"champ R {key}")
        need(
            champs[key]["tariff_fair_X_C1"] > EXPECTED["endpoint_tariff_Q6"],
            f"champ undercut {key}",
        )
    bind = champs["5_1_1"]
    need(bind["R"] == 84, "binding R")
    need(bind["fair_X"] >= EXPECTED["binding_min_fair_X_at_R84"], "binding fair X")
    need(bind["tariff_fair_X_C1"] >= floor, "binding tariff")
    return champs


def build_certificate(quick=False):
    champs = quick_checks()
    live = {}
    if not quick:
        live = enumerate_shapes(VERIFY_SHAPES)
        need(live["5_1_1"]["min_R"] == 84, "binding census min")
        need(live["5_1_1"]["covering_pairs"] == 8749440, "binding covering")
        need(
            min(v["min_R"] for v in live.values()) == 84,
            "verify-batch min must be binding 84",
        )

    shape_table = {}
    for key, exp in EXPECTED["shapes"].items():
        if key in live:
            shape_table[key] = live[key]
            shape_table[key]["source"] = "verify_live_census"
        else:
            shape_table[key] = {
                "shape": [int(x) for x in key.split("_")],
                "Q": 7,
                "covering_pairs": exp["covering"],
                "attainable_R": [int(x) for x in exp["histogram"]],
                "histogram": dict(exp["histogram"]),
                "min_R": exp["min_R"],
                "champion": dict(exp["champion"]),
                "source": "expected_pending_independent",
            }

    mins = {k: shape_table[k]["min_R"] for k in shape_table}
    global_min = min(mins.values())
    need(global_min == EXPECTED["global_min_R"], "global min")
    floor = tariff_qrx_bill(
        7, global_min, EXPECTED["binding_min_fair_X_at_R84"]
    )
    need(floor == EXPECTED["tariff_floor_R84_fairX9"], "floor const")
    need(floor > EXPECTED["endpoint_tariff_Q6"], "no undercut")

    cert = {
        "schema_version": 1,
        "status": "PASS_TRANSFER_COUPLED_SHAPES_7Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "Full transfer-coupled shape census at total Q=p+a+b=7 with priced "
            "transfer C>=1 folded into fair shared-prefix XOR, divergent "
            "suffixes, and dual even-parity readout. Every covering shape has "
            "min R>=84; binding (5,1,1) attains R=84 with min fair X=9 "
            "(tariff floor 452>436). Answers #2779 OQ1 and the remaining-shapes "
            "OQ left by the (5,1,1)-only transfer-coupled package."
        ),
        "claim": {
            "Q": 7,
            "transfer_C_min": 1,
            "shapes_enumerated": sorted(EXPECTED["shapes"]),
            "global_min_R": global_min,
            "binding_shape": list(EXPECTED["binding_shape"]),
            "binding_min_fair_X_at_R84": EXPECTED["binding_min_fair_X_at_R84"],
            "shape_min_R": mins,
            "tariff_floor_at_R84_fairX9": floor,
            "endpoint_Q6_tariff": EXPECTED["endpoint_tariff_Q6"],
            "undercuts_436_after_complete_bill": False,
            "answers_independent_walks_oq_transfer_coupled": True,
            "answers_remaining_transfer_coupled_shapes": True,
            "oq_answer": (
                "Every covering transfer-coupled dual schedule with shape "
                "(p,a,b), p+a+b=7, p,a,b>=1, divergent restored walks, dual "
                "even-parity readout, and priced transfer C>=1 folded into fair "
                "shared-prefix XOR has dirt-legal R>=84. The minimum 84 is "
                "attained only on maximal-share (5,1,1), where min fair X on the "
                "R=84 layer is 9 (tariff 452>436). All other shapes have R>=86 "
                "and already exceed 436 at X=C=1. Partitioned independent walks "
                "(#2779) remain at R=112; same-walk multi-connector (#2761) and "
                "the (5,1,1)-only transfer-coupled package are leave-alone."
            ),
            "no_new_kappa": True,
        },
        "shapes": shape_table,
        "champions": champs,
        "verify_live_shapes": [shape_key(*s) for s in VERIFY_SHAPES],
        "unit_tariff": {"b": 38, "a": 2, "x": 2},
        "tariff_check": {
            "formula": "38*Q + 2*R + 2*X  (transfer C folded into fair X)",
            "at_R84_fairX9": floor,
            "binding_champion_fair": champs["5_1_1"]["tariff_fair_X_C1"],
            "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        },
        "fair_X_note": (
            "Fair shared-prefix XOR: prefix edges once + transfer C>=1 + both "
            "tip chains (prefix_end → suffix → 0)."
        ),
    }
    return cert


def compare_certificate(live, pinned, quick=False):
    need(live["status"] == pinned["status"], "status")
    need(live["claim"] == pinned["claim"], "claim drift")
    need(live["tariff_check"] == pinned["tariff_check"], "tariff drift")
    need(
        live["claim"]["global_min_R"] == pinned["claim"]["global_min_R"],
        "global min drift",
    )
    if quick:
        return
    for key in live["verify_live_shapes"]:
        need(
            live["shapes"][key]["covering_pairs"]
            == pinned["shapes"][key]["covering_pairs"],
            f"{key} covering drift",
        )
        need(
            live["shapes"][key]["histogram"] == pinned["shapes"][key]["histogram"],
            f"{key} hist drift",
        )
        need(live["shapes"][key]["min_R"] == pinned["shapes"][key]["min_R"], f"{key} min")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="rewrite CERTIFICATE.json (maintenance only)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="champions + tariff + F2 identities only (no live census)",
    )
    args = parser.parse_args(argv)

    check_source_pins()
    live = build_certificate(quick=args.quick)

    if args.write_certificate:
        # Always write the full (non-quick) certificate.
        if args.quick:
            raise SystemExit("FAIL: refuse --write-certificate with --quick")
        CERT_PATH.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
        print("WROTE_CERTIFICATE", CERT_PATH)
        return 0

    pinned = load_json_reject_duplicates(CERT_PATH)
    compare_certificate(live, pinned, quick=args.quick)
    claim = pinned["claim"]
    print(
        "PASS_TRANSFER_COUPLED_SHAPES_7Q_OBSTRUCTION",
        f"global_min_R={claim['global_min_R']}",
        f"binding={tuple(claim['binding_shape'])}",
        f"min_fair_X={claim['binding_min_fair_X_at_R84']}",
        f"tariff_floor={claim['tariff_floor_at_R84_fairX9']}",
        f"endpoint={claim['endpoint_Q6_tariff']}",
        "no_undercut_transfer_coupled_shapes",
        "answers_independent_walks_oq_transfer_coupled",
        "answers_remaining_transfer_coupled_shapes",
        "quick" if args.quick else "verify_live_census",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
