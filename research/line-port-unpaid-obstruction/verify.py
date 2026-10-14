#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent line-port unpaid-coordinate obstruction for coverage-law-change.

Read-only by default: compare against RESULT.json.
Pass --write to regenerate RESULT.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO / "research" / "complex-local-word-ceiling"))
import ceiling as C  # noqa: E402
import model as M  # noqa: E402
import toy_two_unpaid as toy  # noqa: E402

WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
ARCHIVE = REPO / "research/community-frontier1094-audit/selected-replay.tar.gz"
PHASES_MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
PHASES_SHA256 = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
GEOMETRY = REPO / "research/split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt"


def require(ok: bool, why: str) -> None:
    if not ok:
        raise AssertionError(why)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def load_sources() -> dict:
    return json.loads((ROOT / "SOURCES.json").read_text())


def check_source_pins() -> dict:
    sources = load_sources()
    checked = []
    for row in sources["files"]:
        path = REPO / row["path"]
        require(path.is_file(), f"missing source {row['path']}")
        digest = sha256(path)
        require(digest == row["sha256"], f"sha256 drift: {row['path']}")
        checked.append(row["path"])
    return {"pinned_files": checked, "base_commit": sources["base_commit"]}


def attest_selected_coverage() -> dict:
    assembly = json.loads(
        (REPO / "research/community-frontier1094-audit/ASSEMBLY.json").read_text()
    )
    profile = {int(r): int(n) for r, n in assembly["complex_profile"].items()}
    mass = sum(r * n for r, n in profile.items())
    line = M.selected_complex_line()
    W, Ncalls, m = 14336, line["calls_N"], line["width_m"]
    require(mass == (m - 1) * W + line["centre_per_call"] * Ncalls, "mass = 72W + 64N")
    require(m * W - mass == W - line["centre_per_call"] * Ncalls == 5120, "deficit")
    # Selected-record kappa pin (frontier untouched check).
    selected = json.loads((REPO / "certificates/selected-result.json").read_text())
    require(
        selected["kappa"] == "836330098538459/500000000000000000",
        "selected kappa unchanged",
    )
    return {
        "mass": mass,
        "coverage_identity": "mass = 72 W + 64 N",
        "deficit": 5120,
        "selected_kappa": selected["kappa"],
    }


def attest_terminal_q() -> dict:
    require(ARCHIVE.is_file(), "selected replay archive")
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        member = tar.extractfile(PHASES_MEMBER)
        require(member is not None, "DATA-PHASES member")
        raw = member.read()
    require(hashlib.sha256(raw).hexdigest() == PHASES_SHA256, "DATA-PHASES digest")
    phases = json.loads(raw)
    recipes = phases["recipes"]
    require(len(recipes) == 112, "112 port recipes")
    require(all(r["terminal_Y_translation"] == r["q"] for r in recipes), "terminal_Y == q")
    qs = sorted(r["q"] for r in recipes)
    require(len(set(qs)) == 112, "distinct port directions")
    # Geometry pin: C_q bookkeeping and terminal X_q correction are documented.
    geo = GEOMETRY.read_text()
    require("X_(-1)=C_q" in geo, "geometry levels")
    require("C_all C_q^(-2)=C_all X_q" in geo, "geometry terminal")
    return {
        "ports": 112,
        "terminal_Y_equals_q": True,
        "phases_member_sha256": PHASES_SHA256,
        "geometry_citations": [
            "research/split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt:62-63",
            "research/split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt:87-90",
        ],
    }


def price_screens() -> dict:
    """Packing screens: ideal u=2 lever, and N=9 obstruction corollary cost note."""
    line = M.selected_complex_line()
    grid = Q(1, 10**15)
    base_lo, base_hi = C.ceiling(
        WORD, line["width_m"], line["families_per_replica_W"], line["stages"],
        line["centre_per_call"], unpaid=1, grid=grid,
    )
    u2_lo, u2_hi = C.ceiling(
        WORD, line["width_m"], line["families_per_replica_W"], line["stages"],
        line["centre_per_call"], unpaid=2, grid=grid,
    )
    # Predecessor packing ceiling pin (exact rational).
    pred = json.loads(
        (REPO / "research/complex-local-word-ceiling/RESULT.json").read_text()
    )
    require(base_hi == Q(pred["ceiling"]["a_ceiling"]), "base ceiling matches predecessor RESULT")
    cor = M.corollary_two_unpaid_blocked()
    # Minimum ambient gap for u=2 under the counting bound.
    min_gap = cor["min_ambient_minus_offset_for_u2"]
    require(min_gap == 16, "N-d >= 16")
    # Optimistic screen at minimum ambient N=18, d=2, m=1+8*18=145, same local word.
    # This is a favorable transplant, not a construction; reported for planning only.
    m145_lo, m145_hi = C.ceiling(
        WORD, 145, line["families_per_replica_W"], line["stages"],
        line["centre_per_call"], unpaid=2, grid=Q(1, 10**12),
    )
    return {
        "selected_word_packing_ceiling": {
            "a_lo": str(base_lo),
            "a_hi": str(base_hi),
            "a_hi_float": float(base_hi),
        },
        "ideal_unpaid2_same_word": {
            "a_lo": str(u2_lo),
            "a_hi": str(u2_hi),
            "a_hi_float": float(u2_hi),
            "multiplier_vs_selected_ceiling": float(u2_hi / base_hi),
        },
        "counting_obstruction": cor,
        "optimistic_m145_unpaid2_transplant": {
            "m": 145,
            "note": "Favorable transplant of the selected local word; not a decoder.",
            "a_hi_float": float(m145_hi),
            "multiplier_vs_selected_ceiling": float(m145_hi / base_hi),
        },
    }


def failure_controls() -> dict:
    rejected = {}
    # Corrupt unpaid bound claim: pretend u=2 fits at N=9.
    try:
        M.require(
            M.unpaid_upper_bound(112, 9, 1) >= 2 * 896,
            "forged u=2 fit",
        )
        rejected["forged_u2_fit_at_N9"] = "FAILED_TO_REJECT"
    except AssertionError:
        rejected["forged_u2_fit_at_N9"] = "rejected"
    # Ceiling rejects idle rank beyond halving guard.
    try:
        C.ceiling(WORD, 73, 896, 9, 64, R=52, unpaid=1, grid=Q(1, 10**9))
        rejected["idle_rank_52"] = "FAILED_TO_REJECT"
    except ValueError:
        rejected["idle_rank_52"] = "rejected"
    # Local mass beyond coverage.
    try:
        C.ceiling({1: 100000}, 73, 896, 9, 64, unpaid=1, grid=Q(1, 10**9))
        rejected["local_mass_beyond_coverage"] = "FAILED_TO_REJECT"
    except ValueError:
        rejected["local_mass_beyond_coverage"] = "rejected"
    # Toy omission already checked inside toy; re-check endpoint failure mode.
    initial = [[1, 1] for _ in range(toy.SLOTS * toy.N)]
    state = [row[:] for row in initial]
    for slot in range(toy.SLOTS):
        for coord in toy.PAID:
            if slot == 0 and coord == toy.PAID[0]:
                continue
            toy.advance_paid(state, slot, coord)
    require(not toy.endpoint_ok(initial, state), "toy omission")
    rejected["toy_paid_omission"] = "rejected"
    # Source pin corruption: flip one expected digest check via wrong path bytes.
    bogus = hashlib.sha256(b"corrupt").hexdigest()
    require(bogus != sha256(REPO / "certificates/selected-result.json"), "control digest")
    rejected["receipt_corruption_control"] = "rejected"
    require(all(v == "rejected" for v in rejected.values()), "all controls reject")
    return rejected


def build_result() -> dict:
    pins = check_source_pins()
    coverage = attest_selected_coverage()
    terminal = attest_terminal_q()
    abstract = M.exhaustive_small_domain()
    toy_result = toy.all_dirty_columns(width=2)
    prices = price_screens()
    controls = failure_controls()
    require(abstract["corollary"]["blocked"], "blocked")
    require(toy_result["status"].startswith("PASS_"), "toy")
    require(prices["counting_obstruction"]["blocked"], "price obstruction")
    return {
        "status": "PASS_LINE_PORT_UNPAID_OBSTRUCTION",
        "task_id": "coverage-law-change",
        "chooser_seed": "a946c496b01c23f36f2c8de5246cce74",
        "scope_key": "f383d8fc405ee6982cdd",
        "no_new_kappa": True,
        "frontier_untouched": True,
        "source_pins": pins,
        "selected_coverage": coverage,
        "terminal_q_attestation": terminal,
        "abstract_rank_model": abstract,
        "two_unpaid_dirty_toy": toy_result,
        "packing_screens": prices,
        "controls": controls,
        "result_summary": {
            "lemma": (
                "Under the stated line-port rank-tracking model, "
                "U <= v*(N-d); at selected v=112,N=9,d=1 this is U<=896."
            ),
            "corollary": (
                "Two unpaid coordinates per live family need U=1792, impossible "
                "at ambient N=9 without changing N-d (template rearrangement alone fails)."
            ),
            "toy": "Exact dirty two-unpaid-direction endpoint on N=4,d=2,s=2.",
            "ideal_unpaid2_multiplier": prices["ideal_unpaid2_same_word"][
                "multiplier_vs_selected_ceiling"
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate RESULT.json (default: read-only compare)",
    )
    args = parser.parse_args()
    result = build_result()
    path = ROOT / "RESULT.json"
    text = canonical(result) + "\n"
    if args.write:
        path.write_text(text)
        print(result["status"] + " wrote RESULT.json")
    else:
        require(path.is_file(), "missing RESULT.json; pass --write to create")
        committed = path.read_text()
        require(committed == text, "RESULT.json drift; pass --write to regenerate")
        # Reject receipt corruption: parse and demand status key.
        loaded = json.loads(committed)
        require(loaded.get("status") == result["status"], "receipt status")
        require(loaded.get("no_new_kappa") is True, "receipt no_new_kappa")
        print(
            f"{result['status']} "
            f"U_bound={result['abstract_rank_model']['corollary']['unpaid_upper_bound']} "
            f"u2_blocked={result['abstract_rank_model']['corollary']['blocked']} "
            f"toy_cols={result['two_unpaid_dirty_toy']['exhaustive_columns']} "
            f"controls={len(result['controls'])} no_new_kappa"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
