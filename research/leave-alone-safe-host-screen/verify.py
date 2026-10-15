#!/usr/bin/env python3
"""Read-only schema/pin check for the leave-alone-safe adapter host screen.

Default verify is read-only: checkout files are not rewritten. A temp-copy
corruption of GRAM-PREFIX-LINUX.json must be rejected. Assertions stay via
require() under python -O.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile

PACKAGE = Path(__file__).resolve().parent
RESULT = PACKAGE / "RESULT.json"
GRAM = PACKAGE / "GRAM-PREFIX-LINUX.json"
CYCLIC = PACKAGE / "CYCLIC-ZERO-LINUX.json"
KERNEL = PACKAGE.parents[1] / "research/gram-prefix-performance/kernel.py"
PW = PACKAGE.parents[1] / "research/e8-bit-carrier-skeleton/code/pricing/prime_witnesses.py"

EXPECTED_GRAM_FULL_RATIO = 1.0774809140004251
EXPECTED_GRAM_FULL_PER_ROUND = [
    1.071420857978787,
    1.1007059736806382,
    1.0649484303566177,
    1.0790754093094208,
    1.1197521621189357,
]
EXPECTED_GRAM_BATCH_RATIO = 1.5091645129958993
EXPECTED_CYCLIC_RATIO = 1.2790328616909987
EXPECTED_CYCLIC_PER_ROUND = [
    1.3070740177212552,
    1.2278889185298498,
    1.3000855634871102,
    1.2232644617783324,
    1.2988251869204033,
    1.253640979114562,
    1.167969146400223,
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


def check_gram_pins(receipt: dict) -> None:
    require(receipt.get("status") == "PASS_GRAM_PREFIX_HOST_SCREEN", "gram status drift")
    require(receipt.get("disposition") == "DEFER_MAGNITUDE", "gram disposition drift")
    require(receipt.get("identical_receipts") is True, "gram receipts must be identical")
    require(int(receipt.get("frames", -1)) == 672, "gram frame count drift")
    full = receipt["full_checker"]
    require(
        abs(float(full["ratio_of_medians"]) - EXPECTED_GRAM_FULL_RATIO) < 1e-12,
        "gram full median ratio drift",
    )
    ratios = list(full["per_round_ratios"])
    require(len(ratios) == 5, "expected five gram full pairs")
    for actual, expected in zip(ratios, EXPECTED_GRAM_FULL_PER_ROUND):
        require(abs(float(actual) - expected) < 1e-12, "gram full per-round ratio drift")
    require(abs(float(full["per_round_min"]) - min(EXPECTED_GRAM_FULL_PER_ROUND)) < 1e-12, "gram min drift")
    require(abs(float(full["per_round_max"]) - max(EXPECTED_GRAM_FULL_PER_ROUND)) < 1e-12, "gram max drift")
    batch = receipt["determinant_batch"]
    require(
        abs(float(batch["ratio_of_medians"]) - EXPECTED_GRAM_BATCH_RATIO) < 1e-12,
        "gram batch median ratio drift",
    )


def check_cyclic_pins(receipt: dict) -> None:
    require(receipt.get("status") == "PASS_CYCLIC_ZERO_HOST_REMEASURE", "cyclic status drift")
    require(receipt.get("disposition") == "DEFER_MAGNITUDE", "cyclic disposition drift")
    require(receipt.get("identical_receipts") is True, "cyclic receipts must be identical")
    require(
        abs(float(receipt["ratio_of_medians"]) - EXPECTED_CYCLIC_RATIO) < 1e-12,
        "cyclic median ratio drift",
    )
    ratios = list(receipt["per_round_ratios"])
    require(len(ratios) == 7, "expected seven cyclic pairs")
    for actual, expected in zip(ratios, EXPECTED_CYCLIC_PER_ROUND):
        require(abs(float(actual) - expected) < 1e-12, "cyclic per-round ratio drift")


def reject_corrupted_gram_copy(committed: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="leave-alone-safe-host-screen-") as tmp:
        bad = Path(tmp) / "GRAM-PREFIX-LINUX.json"
        shutil.copyfile(GRAM, bad)
        mutate = load_object(bad)
        mutate["full_checker"]["ratio_of_medians"] = float(mutate["full_checker"]["ratio_of_medians"]) + 0.25
        bad.write_text(json.dumps(mutate, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        try:
            check_gram_pins(load_object(bad))
        except AssertionError:
            pass
        else:
            raise AssertionError("corrupted gram receipt was accepted")
    require(GRAM.read_bytes() == committed, "checkout gram receipt mutated")


def main() -> None:
    require(RESULT.is_file(), "missing RESULT.json")
    require(GRAM.is_file(), "missing GRAM-PREFIX-LINUX.json")
    require(CYCLIC.is_file(), "missing CYCLIC-ZERO-LINUX.json")
    require(KERNEL.is_file(), "missing gram-prefix-performance/kernel.py")
    require(PW.is_file(), "missing prime_witnesses.py")

    committed_gram = GRAM.read_bytes()
    committed_result = RESULT.read_bytes()
    committed_cyclic = CYCLIC.read_bytes()

    result = load_object(RESULT)
    require(result.get("no_new_kappa") is True, "kappa claim drift")
    require(result.get("production_files_changed") is False, "production-edit claim drift")
    require(
        result.get("status") == "DEFER_TOOLING_INVENTORY_EXHAUSTED",
        "RESULT status drift",
    )
    require(result.get("author") == "Wentao Li", "author drift")

    gram = load_object(GRAM)
    cyclic = load_object(CYCLIC)
    check_gram_pins(gram)
    check_cyclic_pins(cyclic)
    reject_corrupted_gram_copy(committed_gram)

    require(GRAM.read_bytes() == committed_gram, "gram mutated after checks")
    require(RESULT.read_bytes() == committed_result, "RESULT mutated after checks")
    require(CYCLIC.read_bytes() == committed_cyclic, "cyclic mutated after checks")

    print(
        "PASS_LEAVE_ALONE_SAFE_HOST_SCREEN "
        "deferred=true no_production_edit "
        f"gram_full_ratio={EXPECTED_GRAM_FULL_RATIO:.3f} "
        f"cyclic_ratio={EXPECTED_CYCLIC_RATIO:.3f} "
        "no_new_kappa"
    )


if __name__ == "__main__":
    main()
