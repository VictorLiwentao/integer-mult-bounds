#!/usr/bin/env python3
"""Read-only schema/pin check for the deferred U8 dyadic host-magnitude screen.

Default verify is read-only: checkout files are not rewritten. A temp-copy
corruption of U8-DYADIC-LINUX.json must be rejected. Assertions stay via
require() under python -O.
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
U8 = PACKAGE / "U8-DYADIC-LINUX.json"
CYCLIC = PACKAGE / "CYCLIC-ZERO-LINUX.json"
FAST = PACKAGE.parents[1] / "research/ck-dyadic-replay-fast/fast_rows.py"

EXPECTED_U8_STATUS = "PASS_U8_DYADIC_KERNEL_HOST_SCREEN"
EXPECTED_U8_RATIO = 1.3499034212041068
EXPECTED_U8_PER_ROUND = [
    1.3875237660179247,
    1.349754834618645,
    1.3609679946031341,
    1.3396315224303865,
    1.3018413989420436,
]
EXPECTED_CYCLIC_RATIO = 1.3426123408947084


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


def check_u8_pins(receipt: dict) -> None:
    require(receipt.get("status") == EXPECTED_U8_STATUS, "U8 receipt status drift")
    require(receipt.get("identical_integer_receipts") is True, "U8 receipts must be identical")
    require(receipt.get("disposition") == "DEFER_MAGNITUDE", "U8 disposition drift")
    require(abs(float(receipt["ratio_of_medians"]) - EXPECTED_U8_RATIO) < 1e-12, "U8 median ratio drift")
    ratios = list(receipt["per_round_ratios"])
    require(len(ratios) == 5, "expected five U8 pairs")
    for actual, expected in zip(ratios, EXPECTED_U8_PER_ROUND):
        require(abs(float(actual) - expected) < 1e-12, "U8 per-round ratio drift")
    require(abs(float(receipt["per_round_min"]) - min(EXPECTED_U8_PER_ROUND)) < 1e-12, "U8 min drift")
    require(abs(float(receipt["per_round_max"]) - max(EXPECTED_U8_PER_ROUND)) < 1e-12, "U8 max drift")


def check_cyclic_pins(receipt: dict) -> None:
    require(receipt.get("status") == "PASS_CYCLIC_ZERO_HOST_REMEASURE", "cyclic status drift")
    require(receipt.get("disposition") == "DEFER_MAGNITUDE", "cyclic disposition drift")
    require(
        abs(float(receipt["ratio_of_medians"]) - EXPECTED_CYCLIC_RATIO) < 1e-12,
        "cyclic median ratio drift",
    )


def reject_corrupted_u8_copy(committed: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="u8-dyadic-host-screen-") as tmp:
        bad = Path(tmp) / "U8-DYADIC-LINUX.json"
        shutil.copyfile(U8, bad)
        mutate = load_object(bad)
        mutate["ratio_of_medians"] = float(mutate["ratio_of_medians"]) + 0.25
        bad.write_text(json.dumps(mutate, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        try:
            check_u8_pins(load_object(bad))
        except AssertionError:
            pass
        else:
            raise AssertionError("corrupted U8 receipt was accepted")
    require(U8.read_bytes() == committed, "checkout U8 receipt mutated")


def main() -> None:
    require(RESULT.is_file(), "missing RESULT.json")
    require(U8.is_file(), "missing U8-DYADIC-LINUX.json")
    require(CYCLIC.is_file(), "missing CYCLIC-ZERO-LINUX.json")
    require(FAST.is_file(), "missing ck-dyadic-replay-fast/fast_rows.py")

    committed_u8 = U8.read_bytes()
    committed_result = RESULT.read_bytes()
    committed_cyclic = CYCLIC.read_bytes()

    result = load_object(RESULT)
    u8 = load_object(U8)
    cyclic = load_object(CYCLIC)

    require(result.get("status") == "DEFER_PRODUCTION_WIRING_HOST_MAGNITUDE", "unexpected RESULT status")
    require(result.get("production_files_changed") is False, "screen must not claim a production edit")
    require(result.get("no_new_kappa") is True, "must declare no new kappa")

    check_u8_pins(u8)
    check_cyclic_pins(cyclic)
    reject_corrupted_u8_copy(committed_u8)

    screen = result["candidates"][0]
    require(screen["disposition"] == "DEFER_MAGNITUDE", "leading candidate must defer")
    require(abs(float(screen["ratio_of_medians"]) - EXPECTED_U8_RATIO) < 1e-12, "RESULT U8 ratio drift")

    require(RESULT.read_bytes() == committed_result, "checkout RESULT mutated")
    require(U8.read_bytes() == committed_u8, "checkout U8 mutated after verify")
    require(CYCLIC.read_bytes() == committed_cyclic, "checkout cyclic mutated after verify")
    require(len(sha256(committed_u8).hexdigest()) == 64, "U8 digest")

    print(
        "PASS_U8_DYADIC_HOST_SCREEN",
        f"deferred=true ratio_of_medians={EXPECTED_U8_RATIO:.6f}",
        f"per_round={min(EXPECTED_U8_PER_ROUND):.3f}-{max(EXPECTED_U8_PER_ROUND):.3f}",
        f"cyclic={EXPECTED_CYCLIC_RATIO:.3f}",
        "no_production_edit no_new_kappa corruption_rejected",
    )


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print("FAIL_U8_DYADIC_HOST_SCREEN", exc, file=sys.stderr)
        sys.exit(1)
