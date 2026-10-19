#!/usr/bin/env python3
"""Read-only verifier for the priced park invoice on the interrupt path.

Uses need() so admission survives python -O. Rejects duplicate JSON keys
and compares the on-disk certificate without rewriting it.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_BIT_PRICED_PARK_INVOICE "
    "callback_abort_tape_formula "
    "park_restore_table "
    "interrupt_no_output_disposal "
    "three_mutants "
    "no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
INPUTS = (
    "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/controller.py",
    "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/records.py",
    "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/words.py",
    "research/selected-bit-physical-caller/inputs/pr2769/vendor/parking_machine.py",
    "research/selected-bit-physical-caller/inputs/pr2769/PROOF.md",
    "research/selected-bit-physical-caller/numerical_frame.py",
    "docs/research/selected-bit-physical-contract-map.md",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def load_independent():
    spec = importlib.util.spec_from_file_location(
        "selected_bit_priced_park_invoice_independent", HERE / "independent.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    need(
        manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "base pin",
    )
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    for row in inputs:
        raw = (ROOT / row["path"]).read_bytes()
        need(len(raw) <= 4_000_000, "source size")
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
        need(
            hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            == row["git_blob"],
            "git blob: " + row["path"],
        )
    selected = read_json(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == KAPPA_DECIMAL, "selected decimal")
    return selected


def admit(observed, certificate):
    need(certificate.get("status") == observed["status"], "certificate mismatch")
    need(certificate.get("marker") == observed["marker"], "certificate mismatch")
    need(certificate.get("kappa_decimal") == KAPPA_DECIMAL, "certificate mismatch")
    need(certificate.get("no_new_kappa") is True, "certificate mismatch")
    need(certificate.get("callback_abort_tape_formula") is True, "certificate mismatch")
    need(certificate.get("park_restore_table") is True, "certificate mismatch")
    need(certificate.get("interrupt_no_output_disposal") is True, "certificate mismatch")
    need(certificate.get("abort_tape") == observed["abort_tape"], "certificate mismatch")
    need(certificate.get("park_restore") == observed["park_restore"], "certificate mismatch")
    need(certificate.get("face_lengths") == observed["face_lengths"], "certificate mismatch")
    need(certificate.get("mutants") == observed["mutants"], "certificate mismatch")
    need(
        certificate.get("source_correspondence") == observed["source_correspondence"],
        "certificate mismatch",
    )


def evaluate():
    pin_sources()
    return load_independent().evaluate()


def main():
    write = "--write" in __import__("sys").argv[1:]
    observed = evaluate()
    path = HERE / "CERTIFICATE.json"
    if write:
        path.write_text(json.dumps(observed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    certificate = read_json(path)
    admit(observed, certificate)
    print(observed["marker"])


if __name__ == "__main__":
    main()
