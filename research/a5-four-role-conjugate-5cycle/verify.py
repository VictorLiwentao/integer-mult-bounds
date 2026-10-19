#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Four-role A5 conjugate 5-cycle; read-only default verify."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from model import (  # noqa: E402
    CALLS,
    DIRECT_LEN,
    E,
    EXPECTED_CALLS,
    EXPECTED_IDEM,
    GROUP_ORDER,
    KAPPA,
    LAYER_SIZES,
    ROLES,
    SEEN_AT_DEPTH3,
    SHORT_DEPTH,
    X,
    XY,
    Y,
    YX,
    bfs_short_layers,
    formal_matrix_product,
    group_elements_digest,
    identity_state,
    make_direct_word,
    need,
    order_of,
    state_digest,
    target_state,
    word_state,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"
PRED_CERT = ROOT / "research/a5-conjugate-5cycle-seedd316f8/CERTIFICATE.json"
PRED_DIGEST = "9030f2eebc1fe7d848d7946a9c254306f7d0221fb68109e3b0d7c2dcb498e217"


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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_source_pins() -> None:
    sources = load_json_reject_duplicates(SOURCES_PATH)
    need(
        sources["base_commit"] == "bb4bccbf42844d2801487450727c2f63e10d1d0f",
        "base_commit pin",
    )
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        live = ROOT / rec["path"]
        need(live.is_file(), f"missing input {rec['path']}")
        need(sha256_file(live) == rec["sha256"], f"source bytes mismatch: {rec['path']}")


def reject_certificate_corruption(expected: dict) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bad_path = Path(tmp) / "CERTIFICATE.json"
        corrupted = dict(expected)
        corrupted["result_minimum"] = int(expected["result_minimum"]) + 1
        bad_path.write_text(
            json.dumps(corrupted, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        loaded = load_json_reject_duplicates(bad_path)
        need(loaded != expected, "temp corruption must differ from committed receipt")


def controls(direct, target) -> None:
    need(word_state(direct) == target, "direct four-call identity failed")
    need(
        formal_matrix_product(direct) == target,
        "literal formal product disagrees with step",
    )
    for pos in range(len(direct)):
        reduced = direct[:pos] + direct[pos + 1 :]
        need(
            word_state(reduced) != target,
            f"omission control unexpectedly passed at direct position {pos}",
        )
    g, u, v = direct[-1]
    mutated = list(direct)
    mutated[-1] = (g, u, v ^ 1 if v != 1 else v ^ 2)
    need(mutated[-1] in {(c[0], c[1], c[2]) for c in CALLS}, "mutated call legal")
    need(
        word_state(tuple(mutated)) != target,
        "mutated-projector control unexpectedly passed",
    )
    # Dirty spectator roles stay at [e].
    need(target[2 * ROLES + 2] == (1 << E), "role 2 must be [e]")
    need(target[3 * ROLES + 3] == (1 << E), "role 3 must be [e]")
    need(target[0] == (1 << XY), "role 0 must be [xy]")
    need(target[ROLES + 1] == (1 << YX), "role 1 must be [yx]")
    # Positive short control: single x on role 0.
    pos_target = list(identity_state())
    pos_target[0] = 1 << X
    pos_word = ((X, 1, 1),)
    need(word_state(pos_word) == tuple(pos_target), "positive single-call control")


def build_certificate(bfs) -> dict:
    return {
        "schema_version": 1,
        "package": "research/a5-four-role-conjugate-5cycle",
        "group": "A5=<x,y | x^2=y^3=(xy)^5=e>",
        "group_order": GROUP_ORDER,
        "group_elements_sha256": group_elements_digest(),
        "roles": ROLES,
        "paid_labels": ["x", "y"],
        "rank_one_idempotents": EXPECTED_IDEM,
        "paid_factors": EXPECTED_CALLS,
        "target": "diag([xy],[yx],[e],[e])",
        "direct_paid_calls": DIRECT_LEN,
        "direct_word": [
            ["x", "E11"],
            ["y", "E11"],
            ["y", "E22"],
            ["x", "E22"],
        ],
        "short_depth": SHORT_DEPTH,
        "layer_sizes": list(bfs["layer_sizes"]),
        "seen_total_through_short_depth": bfs["seen_total"],
        "hits_by_depth": list(bfs["hits_by_depth"]),
        "short_witness": bfs["short_witness"],
        "result_minimum": DIRECT_LEN,
        "dirty_lowers": False,
        "identity_digest": state_digest(identity_state()),
        "target_digest": state_digest(target_state()),
        "predecessor_package": "research/a5-conjugate-5cycle-seedd316f8",
        "predecessor_group_elements_sha256": PRED_DIGEST,
        "selected_kappa": KAPPA,
        "no_new_kappa": True,
        "relations": {
            "x_order": order_of(X),
            "y_order": order_of(Y),
            "xy_order": order_of(XY),
            "yx_order": order_of(YX),
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate CERTIFICATE.json (explicit write only).",
    )
    args = parser.parse_args(argv)

    check_source_pins()
    need(PRED_CERT.is_file(), "missing predecessor certificate")
    pred = load_json_reject_duplicates(PRED_CERT)
    need(pred["group_order"] == 60, "predecessor group order")
    need(
        pred["group_elements_sha256"] == PRED_DIGEST,
        "predecessor group digest pin",
    )
    need(
        any(s.get("direct_paid_calls") == 4 for s in pred["searches"]),
        "predecessor must certify four-call direct word",
    )

    digest = group_elements_digest()
    need(digest == PRED_DIGEST, "group element digest must match predecessor")

    target = target_state()
    direct = make_direct_word()
    need(len(direct) == DIRECT_LEN, "direct word length")
    controls(direct, target)

    bfs = bfs_short_layers(target)
    need(bfs["layer_sizes"] == LAYER_SIZES, "layer sizes mismatch")
    need(bfs["seen_total"] == SEEN_AT_DEPTH3, "seen-total mismatch")
    need(bfs["hits_by_depth"] == (0, 0, 0), "unexpected short witness")
    need(bfs["short_witness"] is None, "short_witness must be none")

    cert = build_certificate(bfs)
    if args.write:
        CERT_PATH.write_text(
            json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(
            "WROTE_A5_FOUR_ROLE_CONJUGATE "
            f"roles={ROLES} calls={EXPECTED_CALLS} idempotents={EXPECTED_IDEM} "
            f"target_minimum={DIRECT_LEN} layers={list(bfs['layer_sizes'])} "
            f"hits={list(bfs['hits_by_depth'])} dirty_lowers=false "
            f"short_witness=none no_new_kappa",
            flush=True,
        )
        return 0

    need(CERT_PATH.is_file(), "missing CERTIFICATE.json")
    committed = load_json_reject_duplicates(CERT_PATH)
    need(committed == cert, "CERTIFICATE.json disagrees with fresh rebuild")
    reject_certificate_corruption(committed)

    print(
        "PASS_A5_FOUR_ROLE_CONJUGATE "
        f"roles={ROLES} calls={EXPECTED_CALLS} idempotents={EXPECTED_IDEM} "
        f"target_minimum={DIRECT_LEN} layers={list(bfs['layer_sizes'])} "
        f"hits={list(bfs['hits_by_depth'])} dirty_lowers=false "
        f"short_witness=none no_new_kappa",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
