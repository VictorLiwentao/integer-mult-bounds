#!/usr/bin/env python3
"""§7 nonadjacent exposure chunk-swap ledger; read-only default."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from ledger import (  # noqa: E402
    EPSILON,
    PUBLISHED_SAVING,
    SELECTED_KAPPA,
    TAU,
    asymptotic_constant,
    census,
    composite_exchange_multiplier,
    m_upper_linear,
    need,
    pair_primitives,
    section7_exponent,
    section7_saving,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"


def sha256_file(path: Path) -> str:
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


def load_physical():
    path = ROOT / "research" / "synthetic-layout-independent" / "physical.py"
    need(path.is_file(), "missing physical.py")
    import importlib.util

    spec = importlib.util.spec_from_file_location("physical_pin", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.move_address


def physical_unit_checks() -> int:
    """Pinned oracle accepts the lem:chunk-swap primitives used by the ledger."""
    move_address = load_physical()
    checked = 0
    # Equal-width interchange of 3-bit fields.
    idx = 0b111_000
    out = move_address(idx, 6, ("swap", 0, 3, 3))
    need(out == 0b000_111, f"equal swap failed: {out:#b}")
    checked += 1
    # Single-bit move (one-extra-bit companion).
    out = move_address(0b1000, 4, ("move", 0, 3, 1))
    need(isinstance(out, int) and 0 <= out < 16, "bit move range")
    checked += 1
    # Pair-primitive shapes match the audit identities.
    need(pair_primitives(4, 3, 4) == ("interchange", "bit_move"), "long-first")
    need(pair_primitives(3, 4, 4) == ("bit_move", "interchange"), "long-last")
    need(pair_primitives(3, 3, 4) == ("interchange",), "equal")
    checked += 3
    return checked


def build_certificate() -> dict:
    data = census(max_d=8, short=3, long=4)
    need(data["saving_matches_published"], "saving identity")
    need(section7_saving() == PUBLISHED_SAVING, "published saving")
    need(section7_exponent() == TAU + EPSILON * (1 - TAU), "exponent form")
    need(section7_saving() == 1 - section7_exponent(), "saving vs exponent")
    asym = asymptotic_constant()
    physical = physical_unit_checks()
    need(data["multipliers"]["8"]["M"] == 22, "d=8 M")
    need(data["multipliers"]["8"]["linear_majorant"] == 22, "d=8 sharp")
    need(data["pattern_count"] == 510, "census size")
    # Every row meets coarse/linear charges.
    for row in data["rows"]:
        need(Fraction(row["exchanges"]) <= Fraction(m_upper_linear(row["d"])), "row M")
        need(row["exchanges"] == composite_exchange_multiplier(row["d"]), "row exchanges")
    max_bit_moves = max(row["bit_moves"] for row in data["rows"])
    return {
        "schema_version": 1,
        "model": {
            "claim": (
                "Exact composite chunk-swap ledger for PR2298 §7 nonadjacent "
                "CRT + line exposure: M(d)=2*floor(d/2)+2(d-1) exchanges, "
                "each charged at most (1+ell^tau) by lem:chunk-swap; "
                "M(d)<=3d-2 (sharp on even d); saving (1-tau)*(1-epsilon) "
                "matches published 6618729/4000000000; answers #4075 OQ2 on "
                "the adjacent {3,4} domain at d<=8."
            ),
            "tau": data["tau"],
            "epsilon": data["epsilon"],
            "section7_exponent": data["section7_exponent"],
            "section7_saving": data["section7_saving"],
            "published_saving": data["published_saving"],
            "ell": data["ell"],
            "max_d": data["max_d"],
            "selected_kappa": SELECTED_KAPPA,
            "no_new_kappa": True,
        },
        "multipliers": data["multipliers"],
        "per_d_ledger": data["per_d_ledger"],
        "asymptotic_constant": asym,
        "pattern_count": data["pattern_count"],
        "max_bit_moves": max_bit_moves,
        "physical_unit_checks": physical,
        "saving_matches_published": True,
        "even_d_sharp": True,
        "row_digest_sha256": hashlib.sha256(
            json.dumps(
                [
                    {
                        "d": r["d"],
                        "widths": r["widths"],
                        "exchanges": r["exchanges"],
                        "bit_moves": r["bit_moves"],
                        "pattern_charge": r["pattern_charge"],
                    }
                    for r in data["rows"]
                ],
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate CERTIFICATE.json")
    args = parser.parse_args(argv)
    check_source_pins()
    fresh = build_certificate()
    if args.write:
        CERT_PATH.write_text(json.dumps(fresh, indent=2) + "\n", encoding="utf-8")
        print("WROTE_CERTIFICATE", CERT_PATH)
    else:
        committed = load_json_reject_duplicates(CERT_PATH)
        need(fresh == committed, "certificate drift")
    print(
        "PASS_PR2298_SECTION7_EXPOSURE_LEDGER",
        f"patterns={fresh['pattern_count']}",
        f"max_d={fresh['model']['max_d']}",
        f"M8={fresh['multipliers']['8']['M']}",
        f"saving={fresh['model']['section7_saving']}",
        f"exponent={fresh['model']['section7_exponent']}",
        "even_d_sharp=true",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL_PR2298_SECTION7_EXPOSURE_LEDGER {exc}", file=sys.stderr)
        raise SystemExit(1)
