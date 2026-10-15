#!/usr/bin/env python3
"""Read-only schema/pin check for the deferred host-magnitude screen.

Default verify is read-only: checkout files are not rewritten. A temp-copy
corruption of PHASE-REUSE-LINUX.json must be rejected. Assertions stay via
require() under python -O (compile(..., optimize=0) not required here).
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
RESULT = PACKAGE / "RESULT.json"
PHASE = PACKAGE / "PHASE-REUSE-LINUX.json"
PROOF = PACKAGE.parents[1] / "research/clifford-state-reuse/PROOF.md"

EXPECTED_PHASE_STATUS = "PASS_EXACT_SOURCE_BOUND_PHASE_REUSE"
EXPECTED_RATIO = 1.4855024351517547
EXPECTED_PER_ROUND = [1.5177954827973084, 1.4536024592518144, 1.5492733351150956]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_object(path: Path) -> dict:
    def object_pairs(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, f"duplicate JSON key in {path.name}: {key}")
            out[key] = value
        return out

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=object_pairs)


def check_phase_pins(phase: dict) -> None:
    require(phase.get("status") == EXPECTED_PHASE_STATUS, "phase receipt status drift")
    require(phase.get("all_complete_recipe_bytes_equal") is True, "phase recipes must be identical")
    require(abs(float(phase["median_speed_ratio"]) - EXPECTED_RATIO) < 1e-12, "phase median ratio drift")
    baseline = list(phase["baseline_seconds"])
    candidate = list(phase["candidate_seconds"])
    require(len(baseline) == 3 and len(candidate) == 3, "expected three alternating pairs")
    ratios = [b / c for b, c in zip(baseline, candidate)]
    for actual, expected in zip(ratios, EXPECTED_PER_ROUND):
        require(abs(actual - expected) < 1e-12, "per-round ratio drift")


def reject_corrupted_phase_copy(committed: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="clifford-reuse-host-screen-") as tmp:
        bad = Path(tmp) / "PHASE-REUSE-LINUX.json"
        shutil.copyfile(PHASE, bad)
        mutate = load_object(bad)
        mutate["median_speed_ratio"] = float(mutate["median_speed_ratio"]) + 0.25
        bad.write_text(json.dumps(mutate, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        try:
            check_phase_pins(load_object(bad))
        except AssertionError:
            pass
        else:
            raise AssertionError("corrupted phase receipt was accepted")
    require(PHASE.read_bytes() == committed, "checkout PHASE receipt mutated")


def main() -> None:
    require(RESULT.is_file(), "missing RESULT.json")
    require(PHASE.is_file(), "missing PHASE-REUSE-LINUX.json")
    require(PROOF.is_file(), "missing clifford-state-reuse PROOF.md")

    committed_phase = PHASE.read_bytes()
    committed_result = RESULT.read_bytes()

    result = load_object(RESULT)
    phase = load_object(PHASE)

    require(result.get("status") == "DEFER_PRODUCTION_WIRING_HOST_MAGNITUDE", "unexpected RESULT status")
    require(result.get("production_files_changed") is False, "screen must not claim a production edit")
    require(result.get("no_new_kappa") is True, "must declare no new kappa")

    check_phase_pins(phase)
    reject_corrupted_phase_copy(committed_phase)

    screen = result["candidates"][0]
    require(screen["disposition"] == "DEFER_MAGNITUDE", "leading candidate must defer")
    require(abs(float(screen["ratio_of_medians"]) - EXPECTED_RATIO) < 1e-12, "RESULT ratio drift")

    phase_digest = sha256(committed_phase).hexdigest()
    require(len(phase_digest) == 64, "phase digest")
    require(RESULT.read_bytes() == committed_result, "checkout RESULT mutated")
    require(PHASE.read_bytes() == committed_phase, "checkout PHASE mutated after verify")

    print(
        "PASS_CLIFFORD_REUSE_HOST_SCREEN",
        f"deferred=true ratio_of_medians={EXPECTED_RATIO:.6f}",
        f"per_round={min(EXPECTED_PER_ROUND):.3f}-{max(EXPECTED_PER_ROUND):.3f}",
        "no_production_edit no_new_kappa corruption_rejected",
    )


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print("FAIL_CLIFFORD_REUSE_HOST_SCREEN", exc, file=sys.stderr)
        sys.exit(1)
