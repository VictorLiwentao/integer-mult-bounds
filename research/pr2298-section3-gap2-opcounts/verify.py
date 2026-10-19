#!/usr/bin/env python3
"""Exact PR2298 §3 gap-g opcount census; read-only default. Wentao Li + AI, Apache-2.0."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from schedule import (  # noqa: E402
    census,
    gap_unit_cases,
    need,
    physical_reversal_ok,
    reversal_schedule,
    tensor_map_schedule,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"
SELECTED_KAPPA = "0.001672660197076918"
MAX_D = 6
SHORT = 3
LONG = 5
EXPECTED_PATTERNS = sum(2**d for d in range(1, MAX_D + 1))  # 126


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


def load_physical():
    path = ROOT / "research" / "synthetic-layout-independent" / "physical.py"
    need(path.is_file(), "missing synthetic-layout-independent/physical.py")
    import importlib.util

    spec = importlib.util.spec_from_file_location("physical_pin", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.move_address


def build_certificate():
    data = census(max_d=MAX_D, short=SHORT, long=LONG)
    need(data["gap"] == LONG - SHORT, "gap")
    need(data["gap"] >= 2, "non-adjacent gap")
    need(data["all_reversals_exact"], "reversal exactness failed")
    need(data["all_tensors_exact"], "tensor exactness failed")
    need(data["pattern_count"] == EXPECTED_PATTERNS, f"2+…+2^{MAX_D} = {EXPECTED_PATTERNS}")
    move_address = load_physical()
    samples = [
        [5, 3],
        [3, 5],
        [5, 3, 5],
        [3, 5, 3, 5],
        [5, 3, 5, 3, 5],
        [3, 5, 3, 5, 3, 5],
        [5, 5, 3, 3],
        [3, 3, 5, 5],
    ]
    for widths in samples:
        need(physical_reversal_ok(widths, move_address), f"physical reversal {widths}")
        rev = reversal_schedule(list(widths))
        ten = tensor_map_schedule(list(widths))
        need(rev["exchanges"] == len(widths) // 2, "reversal exchange count")
        need(ten["exchanges"] == 2 * max(len(widths) - 1, 0), "tensor exchange count")
    unit = gap_unit_cases(SHORT, LONG)
    need(unit[0]["bit_moves"] == data["gap"], "unit long_first")
    need(unit[1]["bit_moves"] == data["gap"], "unit long_last")
    need(unit[2]["bit_moves"] == 0 and unit[3]["bit_moves"] == 0, "unit equal")
    # Bound sharpness: d=6 all-long attains floor(6/2)=3 and 2*5=10.
    sharp = next(r for r in data["rows"] if r["widths"] == [LONG] * MAX_D)
    need(sharp["reversal_exchanges"] == MAX_D // 2, "sharp reversal at max_d")
    need(sharp["tensor_exchanges"] == 2 * (MAX_D - 1), "sharp tensor at max_d")
    # Adjacent control: gap-1 still matches the #4075 one-extra-bit invoice.
    from schedule import pair_invoice

    adj = pair_invoice(4, 3)
    need(adj["gap"] == 1 and adj["bit_moves"] == 1, "adjacent specialization")
    return {
        "claim": (
            "PR2298 §3 exchange counts extend to non-adjacent gap-g bit-widths "
            "via the multi-bit normal form (1 interchange + g bit_moves): on every "
            f"mixed pattern at d<={MAX_D} with widths in {{{SHORT},{LONG}}} (gap "
            f"{data['gap']}), reversal exchanges = floor(d/2) and tensor-map "
            "exchanges = 2(d-1); physical (swap|move) streams recover reversed "
            "field coordinates."
        ),
        "kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
        "max_d": data["max_d"],
        "short_width": data["short_width"],
        "long_width": data["long_width"],
        "gap": data["gap"],
        "pattern_count": data["pattern_count"],
        "max_reversal_exchanges": data["max_reversal_exchanges"],
        "max_tensor_exchanges": data["max_tensor_exchanges"],
        "all_reversals_exact": True,
        "all_tensors_exact": True,
        "unit_gap_pairs": data["unit_gap_pairs"],
        "bounds": data["bounds"],
        "physical_samples": samples,
        "sharp_d_max": {
            "widths": sharp["widths"],
            "reversal_exchanges": sharp["reversal_exchanges"],
            "tensor_exchanges": sharp["tensor_exchanges"],
        },
        "adjacent_specialization": {"wi": 4, "wj": 3, "gap": 1, "bit_moves": 1},
        "row_digests": [
            {
                "d": r["d"],
                "widths": r["widths"],
                "rev": [
                    r["reversal_exchanges"],
                    r["reversal_interchanges"],
                    r["reversal_bit_moves"],
                ],
                "ten": [
                    r["tensor_exchanges"],
                    r["tensor_interchanges"],
                    r["tensor_bit_moves"],
                ],
            }
            for r in data["rows"]
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate CERTIFICATE.json")
    args = parser.parse_args(argv)
    check_source_pins()
    cert = build_certificate()
    if args.write:
        CERT_PATH.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE {CERT_PATH}")
    else:
        committed = load_json_reject_duplicates(CERT_PATH)
        need(committed == cert, "CERTIFICATE.json drift; pass --write to regenerate")
    print(
        "PASS_PR2298_SECTION3_GAP2_OPCOUNTS "
        f"patterns={cert['pattern_count']} max_d={cert['max_d']} "
        f"gap={cert['gap']} widths={{{cert['short_width']},{cert['long_width']}}} "
        f"rev_bound=floor(d/2) tensor_bound=2(d-1) "
        f"pair_invoice=1+g "
        f"sharp_d{cert['max_d']}_rev={cert['sharp_d_max']['reversal_exchanges']} "
        f"sharp_d{cert['max_d']}_tensor={cert['sharp_d_max']['tensor_exchanges']} "
        "no_new_kappa"
    )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(f"FAIL_PR2298_SECTION3_GAP2_OPCOUNTS {exc}") from exc
