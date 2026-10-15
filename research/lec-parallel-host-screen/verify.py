#!/usr/bin/env python3
"""Read-only schema/pin check for the deferred LEC-parallel host-magnitude screen.

Default verify is read-only: checkout files are not rewritten. A temp-copy
corruption of LEC-LINUX.json must be rejected. Assertions stay via require()
under python -O.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile

PACKAGE = Path(__file__).resolve().parent
RESULT = PACKAGE / "RESULT.json"
LEC = PACKAGE / "LEC-LINUX.json"
CYCLIC = PACKAGE / "CYCLIC-ZERO-LINUX.json"
ADAPTER_VERIFY = PACKAGE.parents[1] / "research/layer-end-controls-parallel/verify.py"

EXPECTED_LEC_STATUS = "PASS_LEC_PARALLEL_HOST_SCREEN"
EXPECTED_LEC_RATIO = 2.4478021978021975
EXPECTED_LEC_PER_ROUND = [
    2.6174863387978142,
    2.4256410256410255,
    2.484593837535014,
    2.507122507122507,
    2.4478021978021975,
]
EXPECTED_CYCLIC_RATIO = 1.2846126827208781
EXPECTED_CYCLIC_PER_ROUND = [
    1.2746079931734815,
    1.246539662331579,
    1.2490133629932878,
    1.2846126827208781,
    1.2864104292442078,
    1.2612320992029462,
    1.296680674525712,
]


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


def check_lec_pins(receipt: dict) -> None:
    require(receipt.get("status") == EXPECTED_LEC_STATUS, "LEC receipt status drift")
    require(receipt.get("identical_receipts") is True, "LEC receipts must be identical")
    require(receipt.get("disposition") == "DEFER_SOFT_OVERLAP", "LEC disposition drift")
    require(
        abs(float(receipt["ratio_of_medians"]) - EXPECTED_LEC_RATIO) < 1e-12,
        "LEC median ratio drift",
    )
    ratios = list(receipt["per_round_ratios"])
    require(len(ratios) == 5, "expected five LEC pairs")
    for actual, expected in zip(ratios, EXPECTED_LEC_PER_ROUND):
        require(abs(float(actual) - expected) < 1e-12, "LEC per-round ratio drift")
    require(abs(float(receipt["per_round_min"]) - min(EXPECTED_LEC_PER_ROUND)) < 1e-12, "LEC min drift")
    require(abs(float(receipt["per_round_max"]) - max(EXPECTED_LEC_PER_ROUND)) < 1e-12, "LEC max drift")
    require(float(receipt["median_serial_seconds"]) == 89.1, "LEC serial median drift")
    require(float(receipt["median_parallel_seconds"]) == 36.4, "LEC parallel median drift")


def check_cyclic_pins(receipt: dict) -> None:
    require(receipt.get("status") == "PASS_CYCLIC_ZERO_HOST_REMEASURE", "cyclic status drift")
    require(receipt.get("disposition") == "DEFER_MAGNITUDE", "cyclic disposition drift")
    require(
        abs(float(receipt["ratio_of_medians"]) - EXPECTED_CYCLIC_RATIO) < 1e-12,
        "cyclic median ratio drift",
    )
    ratios = list(receipt["per_round_ratios"])
    require(len(ratios) == 7, "expected seven cyclic pairs")
    for actual, expected in zip(ratios, EXPECTED_CYCLIC_PER_ROUND):
        require(abs(float(actual) - expected) < 1e-12, "cyclic per-round ratio drift")


def reject_corrupted_lec_copy(committed: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="lec-parallel-host-screen-") as tmp:
        bad = Path(tmp) / "LEC-LINUX.json"
        shutil.copyfile(LEC, bad)
        mutate = load_object(bad)
        mutate["ratio_of_medians"] = float(mutate["ratio_of_medians"]) + 0.25
        bad.write_text(json.dumps(mutate, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        try:
            check_lec_pins(load_object(bad))
        except AssertionError:
            pass
        else:
            raise AssertionError("corrupted LEC receipt was accepted")
    require(LEC.read_bytes() == committed, "checkout LEC receipt mutated")


def main() -> None:
    require(RESULT.is_file(), "missing RESULT.json")
    require(LEC.is_file(), "missing LEC-LINUX.json")
    require(CYCLIC.is_file(), "missing CYCLIC-ZERO-LINUX.json")
    require(ADAPTER_VERIFY.is_file(), "missing layer-end-controls-parallel/verify.py")

    committed_lec = LEC.read_bytes()
    committed_result = RESULT.read_bytes()
    committed_cyclic = CYCLIC.read_bytes()

    result = load_object(RESULT)
    require(result.get("no_new_kappa") is True, "kappa claim drift")
    require(result.get("production_files_changed") is False, "production-edit claim drift")
    require(
        result.get("status") == "DEFER_PRODUCTION_WIRING_SOFT_OVERLAP",
        "RESULT status drift",
    )
    require(result.get("author") == "Wentao Li", "author drift")

    lec = load_object(LEC)
    cyclic = load_object(CYCLIC)
    check_lec_pins(lec)
    check_cyclic_pins(cyclic)
    reject_corrupted_lec_copy(committed_lec)

    require(LEC.read_bytes() == committed_lec, "LEC mutated after checks")
    require(RESULT.read_bytes() == committed_result, "RESULT mutated after checks")
    require(CYCLIC.read_bytes() == committed_cyclic, "cyclic mutated after checks")

    print(
        "PASS_LEC_PARALLEL_HOST_SCREEN "
        "deferred=true no_production_edit "
        f"lec_ratio={EXPECTED_LEC_RATIO:.3f} "
        f"cyclic_ratio={EXPECTED_CYCLIC_RATIO:.3f} "
        "no_new_kappa"
    )


if __name__ == "__main__":
    main()
