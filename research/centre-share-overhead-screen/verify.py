#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Charged k=2 centre-path sharing screen for the selected complex local word.

Planning screen only: applies research/complex-local-word-ceiling/ceiling.py to
explicit copy/centre/overhead profiles. No new kappa, no supplier change, no
physical sharing construction.

Douglas Colkitt's packing ceiling is the predecessor. This package adds the
card's required overhead charge and separates copy-child amortization from a
reduced coverage-law centre charge.
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CEILING_DIR = ROOT / "research" / "complex-local-word-ceiling"
sys.path.insert(0, str(CEILING_DIR))
import ceiling as C  # noqa: E402

PACKAGE = Path(__file__).resolve().parent
M, FAM, ST = 73, 896, 9
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
# Match research/complex-local-word-ceiling/RESULT.json (ceiling.py default).
FINE_GRID = Q(1, 10**15)
# Coarser grid for monotone gate searches; still exact rational enclosures.
SEARCH_GRID = Q(1, 10**12)


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL_CENTRE_SHARE_OVERHEAD_SCREEN: {msg}")


def need(ok: bool, msg: str) -> None:
    if not ok:
        fail(msg)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pins() -> dict:
    return json.loads((PACKAGE / "SOURCES.json").read_text())


def check_pins(pins: dict) -> None:
    for entry in pins["files"]:
        path = ROOT / entry["path"]
        need(path.is_file(), f"missing pinned file {entry['path']}")
        digest = sha256_file(path)
        need(
            digest == entry["sha256"],
            f"sha256 mismatch for {entry['path']}: got {digest}",
        )


def profile_with_copies(copies) -> dict:
    local = {r: Q(n) for r, n in WORD.items() if r != 8}
    local[8] = Q(copies)
    return local


def add_overhead(local: dict, mass, rank: int) -> dict:
    out = {r: Q(n) for r, n in local.items()}
    out[rank] = out.get(rank, Q(0)) + Q(mass) / Q(rank)
    return out


def ceiling_hi(local: dict, centre, grid=FINE_GRID) -> Q:
    return C.ceiling(local, M, FAM, ST, centre, grid=grid)[1]


def as_float(x: Q) -> float:
    return float(x)


def clears_gate(a: Q, base: Q) -> bool:
    return a * 10 >= base * 11


def screen_row(name: str, local: dict, centre, base: Q, grid=FINE_GRID) -> dict:
    model = C.model(local, M, FAM, ST, centre)
    a = ceiling_hi(local, centre, grid=grid)
    return {
        "name": name,
        "centre": str(Q(centre)),
        "local_mass": str(model["local_mass"]),
        "idle_mass": str(model["idle_mass"]),
        "a_ceiling": str(a),
        "a_ceiling_float": as_float(a),
        "multiplier": str(a / base),
        "multiplier_float": as_float(a / base),
        "clears_10pct_gate": clears_gate(a, base),
        "grid": str(grid),
    }


def max_centre_clearing_gate(copies: int, base: Q) -> dict:
    """Largest integer centre charge with fixed copies that still clears +10%."""
    local = profile_with_copies(copies)
    lo, hi = 0, 64
    while lo < hi:
        mid = (lo + hi + 1) // 2
        a = ceiling_hi(local, mid, grid=SEARCH_GRID)
        if clears_gate(a, base):
            lo = mid
        else:
            hi = mid - 1
    # Confirm the SEARCH_GRID threshold on the FINE_GRID; adjust at most by one.
    a_lo = ceiling_hi(local, lo, grid=FINE_GRID)
    if not clears_gate(a_lo, base):
        need(lo > 0, "no centre charge clears the 10% gate with copies=4")
        lo -= 1
        a_lo = ceiling_hi(local, lo, grid=FINE_GRID)
        need(clears_gate(a_lo, base), "fine-grid confirmation failed below search threshold")
    if lo < 64:
        a_next = ceiling_hi(local, lo + 1, grid=FINE_GRID)
        need(not clears_gate(a_next, base), "fine-grid next centre unexpectedly clears")
    return {
        "copies": copies,
        "max_centre_charge": lo,
        "multiplier": str(a_lo / base),
        "multiplier_float": as_float(a_lo / base),
        "next_centre_fails": lo + 1 if lo < 64 else None,
        "next_multiplier_float": as_float(ceiling_hi(local, lo + 1, grid=FINE_GRID) / base)
        if lo < 64
        else None,
    }


def max_rank1_overhead_still_clearing(centre, copies, base: Q) -> dict:
    """Max rank-1 overhead mass still clearing +10%, limited by idle budget."""
    local0 = profile_with_copies(copies)
    idle0 = C.model(local0, M, FAM, ST, centre)["idle_mass"]
    need(idle0 >= 0, "shared profile violates coverage")
    # Prefer the whole idle budget if it still clears (the interesting case).
    local_all = add_overhead(local0, idle0, 1)
    a_all = ceiling_hi(local_all, centre, grid=FINE_GRID)
    if clears_gate(a_all, base):
        return {
            "centre": str(Q(centre)),
            "copies": copies,
            "idle_budget": str(idle0),
            "max_rank1_overhead_mass": str(idle0),
            "consumes_entire_idle_budget": True,
            "multiplier_at_max": str(a_all / base),
            "multiplier_at_max_float": as_float(a_all / base),
            "clears_10pct_gate": True,
        }
    lo, hi = 0, int(idle0)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        local = add_overhead(local0, mid, 1)
        model = C.model(local, M, FAM, ST, centre)
        if model["idle_mass"] < 0:
            hi = mid - 1
            continue
        a = ceiling_hi(local, centre, grid=SEARCH_GRID)
        if clears_gate(a, base):
            lo = mid
        else:
            hi = mid - 1
    local = add_overhead(local0, lo, 1)
    a = ceiling_hi(local, centre, grid=FINE_GRID)
    return {
        "centre": str(Q(centre)),
        "copies": copies,
        "idle_budget": str(idle0),
        "max_rank1_overhead_mass": lo,
        "consumes_entire_idle_budget": Q(lo) == idle0,
        "multiplier_at_max": str(a / base),
        "multiplier_at_max_float": as_float(a / base),
        "clears_10pct_gate": clears_gate(a, base),
    }


def run_controls(base: Q, ideal: Q) -> None:
    need(ideal * 100 >= base * 190, "ideal share-by-2 should be about 1.90x")
    need(clears_gate(ideal, base), "ideal share-by-2 must clear the card's 10% gate")

    copy_only = ceiling_hi(profile_with_copies(4), 64)
    need(
        not clears_gate(copy_only, base),
        "copy-only sharing at centre=64 unexpectedly clears 10%",
    )
    need(copy_only > base, "copy-only sharing should still beat baseline slightly")

    no_copies = {r: Q(n) for r, n in WORD.items() if r != 8}
    no_copy_a = ceiling_hi(no_copies, 64)
    need(
        not clears_gate(no_copy_a, base),
        "deleting rank-8 copies at centre=64 unexpectedly clears 10%",
    )

    selected = ceiling_hi(WORD, 64)
    need(selected == base, "baseline ceiling drifted")

    bloated = add_overhead(profile_with_copies(4), 10**9, 1)
    try:
        C.model(bloated, M, FAM, ST, 32)
    except ValueError as exc:
        need("coverage" in str(exc).lower() or "mass" in str(exc).lower(), str(exc))
    else:
        fail("expected coverage rejection for impossible overhead")

    threshold = max_centre_clearing_gate(4, base)
    need(threshold["max_centre_charge"] == 60, "expected max centre charge 60 for copies=4")
    need(
        not clears_gate(ceiling_hi(profile_with_copies(4), 61), base),
        "centre=61 should fail the 10% gate",
    )


def main() -> None:
    pins = load_pins()
    check_pins(pins)

    selected = json.loads((ROOT / "certificates" / "selected-result.json").read_text())
    need(
        selected["kappa"] == "836330098538459/500000000000000000",
        "selected kappa pin drifted",
    )

    pred = json.loads((CEILING_DIR / "RESULT.json").read_text())
    pred_ceiling = pred.get("ceiling", pred)
    need(
        "a_ceiling" in pred_ceiling,
        f"unrecognized predecessor RESULT.json shape: {sorted(pred)}",
    )
    pred_a = Q(pred_ceiling["a_ceiling"])

    base = ceiling_hi(WORD, 64)
    need(base == pred_a, f"baseline ceiling {base} != predecessor {pred_a}")

    ideal_local = profile_with_copies(4)
    ideal = ceiling_hi(ideal_local, 32)
    run_controls(base, ideal)

    idle32 = C.model(ideal_local, M, FAM, ST, 32)["idle_mass"]
    rows = [
        screen_row("selected_baseline", WORD, 64, base),
        screen_row("ideal_share_k2_centre32_copies4", ideal_local, 32, base),
        screen_row("copy_only_centre64_copies4", profile_with_copies(4), 64, base),
        screen_row(
            "no_rank8_copies_centre64",
            {r: Q(n) for r, n in WORD.items() if r != 8},
            64,
            base,
        ),
        screen_row(
            "share_k2_plus_rank1_overhead4",
            add_overhead(profile_with_copies(4), 4, 1),
            32,
            base,
        ),
        screen_row(
            "share_k2_plus_rank8_overhead4",
            add_overhead(profile_with_copies(4), 4, 8),
            32,
            base,
        ),
        screen_row(
            "share_k2_plus_rank1_overhead_all_idle",
            add_overhead(profile_with_copies(4), idle32, 1),
            32,
            base,
        ),
        screen_row("share_k2_centre60_copies4", profile_with_copies(4), 60, base),
        screen_row("share_k2_centre61_copies4", profile_with_copies(4), 61, base),
    ]

    centre_threshold = max_centre_clearing_gate(4, base)
    rank1_budget = max_rank1_overhead_still_clearing(32, 4, base)

    centre_curve = []
    for centre in (64, 60, 56, 48, 40, 32, 16, 0):
        centre_curve.append(
            screen_row(f"copies4_centre{centre}", profile_with_copies(4), centre, base)
        )

    result = {
        "status": "PASS_CENTRE_SHARE_OVERHEAD_SCREEN",
        "task_id": "centre-path-sharing",
        "scope_status": "refined",
        "selected_kappa": selected["kappa"],
        "model": {
            "m": M,
            "families": FAM,
            "stages": ST,
            "R": C.max_idle_rank(M),
            "selected_word": {str(k): v for k, v in WORD.items()},
            "fine_grid": str(FINE_GRID),
            "search_grid": str(SEARCH_GRID),
            "gate": "+10% screened ceiling vs selected-word packing ceiling",
        },
        "baseline_a_ceiling": str(base),
        "ideal_share_k2": rows[1],
        "copy_only_fails_gate": rows[2],
        "centre_charge_threshold": centre_threshold,
        "rank1_overhead_at_centre32": rank1_budget,
        "rows": rows,
        "centre_curve_copies4": centre_curve,
        "findings": [
            "Ideal k=2 sharing (centre charge 32, four rank-8 copies) clears the +10% gate at about 1.90x, matching levers.py.",
            "Halving only the rank-8 COPY children while leaving the coverage-law centre charge at 64 yields only about +0.28% and fails the +10% gate.",
            "With copies fixed at 4, the coverage-law centre charge must be at most 60 to clear +10%; centre 61 fails.",
            "When the centre charge is reduced to 32, even consuming the entire idle mass as adversarial rank-1 overhead still clears +10%.",
            "Therefore the binding obligation for this route is reducing the coverage-law centre charge (or an equivalent fully charged replacement model), not merely amortizing the eight private COPY/ERASE children.",
        ],
        "not_checked": [
            "No physical two-call sharing circuit, restoration lemma, or dirty-temp contract.",
            "No change to the selected supplier, cold replay, or kappa record.",
            "Ceiling model hypotheses (coverage law, halving guard, fractional idle packing) are inherited from research/complex-local-word-ceiling.",
        ],
        "controls": 7,
    }

    out = PACKAGE / "RESULT.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print(
        "PASS_CENTRE_SHARE_OVERHEAD_SCREEN "
        f"ideal_x={rows[1]['multiplier_float']:.4f} "
        f"copy_only_x={rows[2]['multiplier_float']:.4f} "
        f"max_centre_for_10pct={centre_threshold['max_centre_charge']} "
        f"rank1_overhead_clears_all_idle={rank1_budget['consumes_entire_idle_budget']} "
        f"controls=7 no_new_kappa"
    )


if __name__ == "__main__":
    main()
