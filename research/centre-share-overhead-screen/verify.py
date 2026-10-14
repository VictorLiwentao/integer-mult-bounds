#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Charged k=2 centre-path sharing screen for the selected complex local word.

Planning screen only: applies research/complex-local-word-ceiling/ceiling.py to
explicit copy/centre/overhead profiles. No new kappa, no supplier change, no
physical sharing construction.

Default invocation is read-only: recomputes evidence, compares to the committed
RESULT.json, rejects receipt corruption, and leaves the checkout unchanged.
Pass --write to regenerate RESULT.json explicitly.

Gate decisions use certified rational interval comparisons against the packing
ceiling bracket (a_lo, a_hi) from ceiling.ceiling. Upper-endpoint ratios alone
do not certify a pass or a fail.

Predecessor packing ceiling: Douglas Colkitt (research/complex-local-word-ceiling).
Package author: Wentao Li (@VictorLiwentao), with substantial Cursor/Composer AI
assistance.
"""
from __future__ import annotations

import argparse
import copy
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
RESULT_PATH = PACKAGE / "RESULT.json"
M, FAM, ST = 73, 896, 9
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
FINE_GRID = Q(1, 10**15)
SEARCH_GRID = Q(1, 10**12)
GATE = Q(11, 10)


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


def bracket(local: dict, centre, grid=FINE_GRID) -> tuple[Q, Q]:
    """Return (a_lo, a_hi) from ceiling.ceiling; true packing ceiling is in (a_lo, a_hi)."""
    return C.ceiling(local, M, FAM, ST, centre, grid=grid)


def as_float(x: Q) -> float:
    return float(x)


def gate_status(a_lo: Q, a_hi: Q, base_lo: Q, base_hi: Q) -> str:
    """Certified comparison of new ceiling vs GATE * baseline.

    PASS only if even the lower new bracket clears GATE times the upper baseline.
    FAIL only if even the upper new bracket misses GATE times the lower baseline.
    Otherwise INCONCLUSIVE (enclosure too wide to decide the gate).
    """
    if a_lo * 1 >= GATE * base_hi:
        return "PASS"
    if a_hi * 1 < GATE * base_lo:
        return "FAIL"
    return "INCONCLUSIVE"


def clears_certified(a_lo: Q, a_hi: Q, base_lo: Q, base_hi: Q) -> bool:
    return gate_status(a_lo, a_hi, base_lo, base_hi) == "PASS"


def fails_certified(a_lo: Q, a_hi: Q, base_lo: Q, base_hi: Q) -> bool:
    return gate_status(a_lo, a_hi, base_lo, base_hi) == "FAIL"


def screen_row(name: str, local: dict, centre, base_lo: Q, base_hi: Q, grid=FINE_GRID) -> dict:
    model = C.model(local, M, FAM, ST, centre)
    a_lo, a_hi = bracket(local, centre, grid=grid)
    status = gate_status(a_lo, a_hi, base_lo, base_hi)
    return {
        "name": name,
        "centre": str(Q(centre)),
        "local_mass": str(model["local_mass"]),
        "idle_mass": str(model["idle_mass"]),
        "a_lo": str(a_lo),
        "a_hi": str(a_hi),
        "a_ceiling": str(a_hi),
        "a_ceiling_float": as_float(a_hi),
        "multiplier_lo_vs_base_hi": str(a_lo / base_hi),
        "multiplier_hi_vs_base_lo": str(a_hi / base_lo),
        "multiplier_hi_vs_base_hi": str(a_hi / base_hi),
        "multiplier_float": as_float(a_hi / base_hi),
        "gate_status": status,
        "clears_10pct_gate_certified": status == "PASS",
        "fails_10pct_gate_certified": status == "FAIL",
        "grid": str(grid),
    }


def max_centre_clearing_gate(copies: int, base_lo: Q, base_hi: Q) -> dict:
    """Largest integer centre with certified PASS at fixed copies; next must FAIL."""
    local = profile_with_copies(copies)
    # Coarse search using certified PASS (conservative).
    lo, hi = 0, 64
    while lo < hi:
        mid = (lo + hi + 1) // 2
        a_lo, a_hi = bracket(local, mid, grid=SEARCH_GRID)
        if clears_certified(a_lo, a_hi, base_lo, base_hi):
            lo = mid
        else:
            hi = mid - 1
    # Confirm on FINE_GRID with full interval logic.
    a_lo, a_hi = bracket(local, lo, grid=FINE_GRID)
    if not clears_certified(a_lo, a_hi, base_lo, base_hi):
        need(lo > 0, "no centre charge certifies the 10% gate with copies=4")
        lo -= 1
        a_lo, a_hi = bracket(local, lo, grid=FINE_GRID)
        need(
            clears_certified(a_lo, a_hi, base_lo, base_hi),
            "fine-grid confirmation failed below search threshold",
        )
    if lo < 64:
        n_lo, n_hi = bracket(local, lo + 1, grid=FINE_GRID)
        need(
            fails_certified(n_lo, n_hi, base_lo, base_hi),
            f"centre={lo + 1} must be a certified FAIL, got "
            f"{gate_status(n_lo, n_hi, base_lo, base_hi)}",
        )
    # Independent threshold proof: scan the critical window and require a single cut.
    statuses = {}
    for centre in range(max(0, lo - 2), min(64, lo + 3) + 1):
        c_lo, c_hi = bracket(local, centre, grid=FINE_GRID)
        statuses[centre] = gate_status(c_lo, c_hi, base_lo, base_hi)
    need(statuses.get(lo) == "PASS", "threshold centre not certified PASS")
    if lo < 64:
        need(statuses.get(lo + 1) == "FAIL", "next centre not certified FAIL")
    for centre, status in statuses.items():
        if centre <= lo:
            need(status == "PASS", f"centre {centre} below threshold not PASS ({status})")
        else:
            need(status == "FAIL", f"centre {centre} above threshold not FAIL ({status})")
    return {
        "copies": copies,
        "max_centre_charge": lo,
        "a_lo": str(a_lo),
        "a_hi": str(a_hi),
        "multiplier_lo_vs_base_hi": str(a_lo / base_hi),
        "multiplier_hi_vs_base_hi": str(a_hi / base_hi),
        "multiplier_float": as_float(a_hi / base_hi),
        "next_centre_fails": lo + 1 if lo < 64 else None,
        "next_gate_status": statuses.get(lo + 1),
        "window_statuses": {str(k): v for k, v in sorted(statuses.items())},
        "certification": (
            "PASS requires a_lo(new) >= (11/10)*a_hi(base); "
            "FAIL requires a_hi(new) < (11/10)*a_lo(base)"
        ),
    }


def max_rank1_overhead_still_clearing(centre, copies, base_lo: Q, base_hi: Q) -> dict:
    """Max rank-1 overhead mass with certified PASS, limited by idle budget."""
    local0 = profile_with_copies(copies)
    idle0 = C.model(local0, M, FAM, ST, centre)["idle_mass"]
    need(idle0 >= 0, "shared profile violates coverage")
    local_all = add_overhead(local0, idle0, 1)
    a_lo, a_hi = bracket(local_all, centre, grid=FINE_GRID)
    if clears_certified(a_lo, a_hi, base_lo, base_hi):
        return {
            "centre": str(Q(centre)),
            "copies": copies,
            "idle_budget": str(idle0),
            "max_rank1_overhead_mass": str(idle0),
            "consumes_entire_idle_budget": True,
            "a_lo": str(a_lo),
            "a_hi": str(a_hi),
            "multiplier_lo_vs_base_hi": str(a_lo / base_hi),
            "multiplier_float": as_float(a_hi / base_hi),
            "gate_status": "PASS",
            "clears_10pct_gate_certified": True,
        }
    lo, hi = 0, int(idle0)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        local = add_overhead(local0, mid, 1)
        model = C.model(local, M, FAM, ST, centre)
        if model["idle_mass"] < 0:
            hi = mid - 1
            continue
        m_lo, m_hi = bracket(local, centre, grid=SEARCH_GRID)
        if clears_certified(m_lo, m_hi, base_lo, base_hi):
            lo = mid
        else:
            hi = mid - 1
    local = add_overhead(local0, lo, 1)
    a_lo, a_hi = bracket(local, centre, grid=FINE_GRID)
    status = gate_status(a_lo, a_hi, base_lo, base_hi)
    return {
        "centre": str(Q(centre)),
        "copies": copies,
        "idle_budget": str(idle0),
        "max_rank1_overhead_mass": lo,
        "consumes_entire_idle_budget": Q(lo) == idle0,
        "a_lo": str(a_lo),
        "a_hi": str(a_hi),
        "multiplier_lo_vs_base_hi": str(a_lo / base_hi),
        "multiplier_float": as_float(a_hi / base_hi),
        "gate_status": status,
        "clears_10pct_gate_certified": status == "PASS",
    }


def run_controls(base_lo: Q, base_hi: Q, ideal_lo: Q, ideal_hi: Q) -> int:
    controls = 0
    # Ideal share-by-2 must be a certified PASS and about 1.90x on upper/upper for orientation.
    need(
        clears_certified(ideal_lo, ideal_hi, base_lo, base_hi),
        "ideal share-by-2 must certify the card's 10% gate",
    )
    controls += 1
    need(ideal_hi * 100 >= base_hi * 190, "ideal share-by-2 upper figure should be about 1.90x")
    controls += 1

    c_lo, c_hi = bracket(profile_with_copies(4), 64)
    need(
        fails_certified(c_lo, c_hi, base_lo, base_hi),
        "copy-only sharing at centre=64 must be a certified FAIL",
    )
    controls += 1
    need(c_hi > base_hi, "copy-only sharing should still beat baseline slightly on a_hi")
    controls += 1

    no_copies = {r: Q(n) for r, n in WORD.items() if r != 8}
    n_lo, n_hi = bracket(no_copies, 64)
    need(
        fails_certified(n_lo, n_hi, base_lo, base_hi),
        "deleting rank-8 copies at centre=64 must be a certified FAIL",
    )
    controls += 1

    s_lo, s_hi = bracket(WORD, 64)
    need(s_lo == base_lo and s_hi == base_hi, "baseline ceiling drifted")
    controls += 1

    bloated = add_overhead(profile_with_copies(4), 10**9, 1)
    try:
        C.model(bloated, M, FAM, ST, 32)
    except ValueError as exc:
        need("coverage" in str(exc).lower() or "mass" in str(exc).lower(), str(exc))
    else:
        fail("expected coverage rejection for impossible overhead")
    controls += 1

    # Interval logic itself: a wide fake bracket must be INCONCLUSIVE, not PASS/FAIL.
    need(
        gate_status(base_hi * Q(105, 100), base_hi * Q(115, 100), base_lo, base_hi)
        == "INCONCLUSIVE",
        "gate_status must leave overlapping brackets inconclusive",
    )
    controls += 1
    return controls


def compute_result() -> dict:
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

    base_lo, base_hi = bracket(WORD, 64)
    need(base_hi == pred_a, f"baseline a_hi {base_hi} != predecessor {pred_a}")

    ideal_local = profile_with_copies(4)
    ideal_lo, ideal_hi = bracket(ideal_local, 32)
    n_controls = run_controls(base_lo, base_hi, ideal_lo, ideal_hi)

    idle32 = C.model(ideal_local, M, FAM, ST, 32)["idle_mass"]
    rows = [
        screen_row("selected_baseline", WORD, 64, base_lo, base_hi),
        screen_row("ideal_share_k2_centre32_copies4", ideal_local, 32, base_lo, base_hi),
        screen_row("copy_only_centre64_copies4", profile_with_copies(4), 64, base_lo, base_hi),
        screen_row(
            "no_rank8_copies_centre64",
            {r: Q(n) for r, n in WORD.items() if r != 8},
            64,
            base_lo,
            base_hi,
        ),
        screen_row(
            "share_k2_plus_rank1_overhead4",
            add_overhead(profile_with_copies(4), 4, 1),
            32,
            base_lo,
            base_hi,
        ),
        screen_row(
            "share_k2_plus_rank8_overhead4",
            add_overhead(profile_with_copies(4), 4, 8),
            32,
            base_lo,
            base_hi,
        ),
        screen_row(
            "share_k2_plus_rank1_overhead_all_idle",
            add_overhead(profile_with_copies(4), idle32, 1),
            32,
            base_lo,
            base_hi,
        ),
        screen_row("share_k2_centre60_copies4", profile_with_copies(4), 60, base_lo, base_hi),
        screen_row("share_k2_centre61_copies4", profile_with_copies(4), 61, base_lo, base_hi),
    ]

    centre_threshold = max_centre_clearing_gate(4, base_lo, base_hi)
    rank1_budget = max_rank1_overhead_still_clearing(32, 4, base_lo, base_hi)

    centre_curve = []
    for centre in (64, 60, 56, 48, 40, 32, 16, 0):
        centre_curve.append(
            screen_row(
                f"copies4_centre{centre}",
                profile_with_copies(4),
                centre,
                base_lo,
                base_hi,
            )
        )

    need(rows[1]["gate_status"] == "PASS", "ideal row must PASS")
    need(rows[2]["gate_status"] == "FAIL", "copy-only row must FAIL")
    need(rows[7]["gate_status"] == "PASS", "centre 60 row must PASS")
    need(rows[8]["gate_status"] == "FAIL", "centre 61 row must FAIL")
    need(rank1_budget["clears_10pct_gate_certified"], "full idle overhead must certify PASS")
    need(centre_threshold["max_centre_charge"] == 60, "expected max centre charge 60")

    return {
        "status": "PASS_CENTRE_SHARE_OVERHEAD_SCREEN",
        "task_id": "centre-path-sharing",
        "scope_status": "refined",
        "selected_kappa": selected["kappa"],
        "author": "Wentao Li",
        "model": {
            "m": M,
            "families": FAM,
            "stages": ST,
            "R": C.max_idle_rank(M),
            "selected_word": {str(k): v for k, v in WORD.items()},
            "fine_grid": str(FINE_GRID),
            "search_grid": str(SEARCH_GRID),
            "gate": "+10% screened ceiling vs selected-word packing ceiling",
            "gate_certification": (
                "PASS: a_lo(new) >= (11/10)*a_hi(base); "
                "FAIL: a_hi(new) < (11/10)*a_lo(base); else INCONCLUSIVE"
            ),
        },
        "baseline_a_lo": str(base_lo),
        "baseline_a_ceiling": str(base_hi),
        "ideal_share_k2": rows[1],
        "copy_only_fails_gate": rows[2],
        "centre_charge_threshold": centre_threshold,
        "rank1_overhead_at_centre32": rank1_budget,
        "rows": rows,
        "centre_curve_copies4": centre_curve,
        "findings": [
            "Ideal k=2 sharing (centre charge 32, four rank-8 copies) certifies the +10% gate (a_lo clears (11/10)*a_hi(base)); a_hi/a_hi(base) ≈ 1.90 matching levers.py.",
            "Halving only the rank-8 COPY children while leaving the coverage-law centre charge at 64 is a certified FAIL of the +10% gate.",
            "With copies fixed at 4, the coverage-law centre charge must be at most 60 for a certified PASS; charge 61 is a certified FAIL (independent window scan).",
            "When the centre charge is reduced to 32, even consuming the entire idle mass as adversarial rank-1 overhead still certifies +10%.",
            "Therefore the binding obligation for this route is reducing the coverage-law centre charge (or an equivalent fully charged replacement model), not merely amortizing the eight private COPY/ERASE children.",
        ],
        "not_checked": [
            "No physical two-call sharing circuit, restoration lemma, or dirty-temp contract.",
            "No change to the selected supplier, cold replay, or kappa record.",
            "Ceiling model hypotheses (coverage law, halving guard, fractional idle packing) are inherited from research/complex-local-word-ceiling.",
        ],
        "controls": n_controls,
    }


STABLE_IGNORE = set()  # compare full receipt; floats are derived but committed


def canonical(obj):
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def compare_receipt(computed: dict, committed: dict) -> None:
    # Exact structural equality on the canonical JSON form.
    c1 = canonical(computed)
    c2 = canonical(committed)
    need(c1 == c2, "committed RESULT.json differs from recomputed evidence")


def reject_corruption(computed: dict) -> None:
    """Mutate critical fields of a deep copy and require mismatch detection."""
    committed = copy.deepcopy(computed)
    mutants = [
        ("status", "PASS_FORGED"),
        ("centre_charge_threshold.max_centre_charge", 61),
        ("copy_only_fails_gate.gate_status", "PASS"),
        ("ideal_share_k2.gate_status", "FAIL"),
        ("baseline_a_ceiling", "0"),
        ("rows.0.a_hi", "0"),
    ]
    for path, value in mutants:
        forged = copy.deepcopy(committed)
        cur = forged
        parts = path.split(".")
        for p in parts[:-1]:
            cur = cur[int(p)] if p.isdigit() else cur[p]
        last = parts[-1]
        if last.isdigit():
            cur[int(last)] = value
        else:
            cur[last] = value
        try:
            compare_receipt(computed, forged)
        except SystemExit:
            continue
        fail(f"corruption of {path} was not rejected")


def snapshot_package_hashes() -> dict[str, str]:
    return {
        p.name: sha256_file(p)
        for p in sorted(PACKAGE.iterdir())
        if p.is_file() and p.suffix in {".py", ".json", ".md"}
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate RESULT.json; default is read-only verify against the committed receipt",
    )
    args = parser.parse_args(argv)

    before = snapshot_package_hashes()
    computed = compute_result()

    if args.write:
        RESULT_PATH.write_text(canonical(computed))
        print(
            "WROTE_CENTRE_SHARE_OVERHEAD_SCREEN "
            f"ideal_gate={computed['ideal_share_k2']['gate_status']} "
            f"copy_only_gate={computed['copy_only_fails_gate']['gate_status']} "
            f"max_centre_for_10pct={computed['centre_charge_threshold']['max_centre_charge']} "
            f"rank1_overhead_clears_all_idle="
            f"{computed['rank1_overhead_at_centre32']['consumes_entire_idle_budget']} "
            f"controls={computed['controls']} no_new_kappa"
        )
        return

    need(RESULT_PATH.is_file(), "missing committed RESULT.json (run with --write to regenerate)")
    committed = json.loads(RESULT_PATH.read_text())
    compare_receipt(computed, committed)
    reject_corruption(computed)

    after = snapshot_package_hashes()
    need(before == after, "read-only verify mutated package files")

    print(
        "PASS_CENTRE_SHARE_OVERHEAD_SCREEN "
        f"ideal_gate={computed['ideal_share_k2']['gate_status']} "
        f"copy_only_gate={computed['copy_only_fails_gate']['gate_status']} "
        f"max_centre_for_10pct={computed['centre_charge_threshold']['max_centre_charge']} "
        f"rank1_overhead_clears_all_idle="
        f"{computed['rank1_overhead_at_centre32']['consumes_entire_idle_budget']} "
        f"controls={computed['controls']} no_new_kappa"
    )


if __name__ == "__main__":
    main()
