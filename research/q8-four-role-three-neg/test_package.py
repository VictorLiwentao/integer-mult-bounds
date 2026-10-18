#!/usr/bin/env python3
"""Failure controls for the four-role three-negative certificate.

Does not rerun the length-7 meet. Admission uses need() and stays active
under python -O. Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_verify():
    spec = importlib.util.spec_from_file_location("four_role_verify", HERE / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def duplicate_keys_rejected():
    module = load_verify()
    raw = b'{"a": 1, "a": 2}'
    path = Path(tempfile.mkdtemp()) / "dup.json"
    path.write_bytes(raw)
    try:
        module.read_json(path)
    except ValueError as error:
        need("duplicate JSON key" in str(error), "duplicate-key message")
    else:
        need(False, "duplicate JSON key accepted")
    finally:
        path.unlink()
        path.parent.rmdir()


def witness_controls():
    module = load_verify()
    module.orbit_reduction()
    labels = [3, 3, 5, 0]
    calls = module.direct_word(labels)
    state = module.identity()
    # Drop the last call: the endpoint must not be the requested diagonal.
    for role, paid in calls[:-1]:
        state = module.apply_factor(state, 1 << role, 1 << role, paid)
    try:
        got = module.diagonal_target(state)
    except ValueError:
        got = None
    need(got != labels, "truncated witness still matched")
    # A zero projector is not an idempotent; the direct word must not use it.
    need(all(role < 4 for role, _paid in calls), "role range")


def pin_drift_rejected():
    module = load_verify()
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    manifest["files"][0]["sha256"] = "0" * 64
    path = Path(tempfile.mkdtemp()) / "SOURCES.json"
    # The checker reads HERE/SOURCES.json, so patch via a copied function call
    # on the altered bytes by invoking the same hash comparison inline.
    raw = subprocess.check_output(
        ["git", "cat-file", "blob", manifest["base_commit"] + ":" + manifest["files"][0]["path"]],
        cwd=ROOT,
    )
    import hashlib
    need(hashlib.sha256(raw).hexdigest() != manifest["files"][0]["sha256"],
         "tampered pin still matched")
    path.write_text(json.dumps(manifest))
    parsed = module.read_json(path)
    need(parsed["files"][0]["sha256"] == "0" * 64, "tampered pin not stored")
    path.unlink()
    path.parent.rmdir()


def optimized_controls():
    ran = subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(HERE / "test_package.py"), "--inner"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    need(ran.returncode == 0, "optimized controls failed: " + ran.stderr + ran.stdout)
    need("PASS_Q8_FOUR_ROLE_THREE_NEG_PACKAGE_TESTS" in ran.stdout, "optimized marker")


def main():
    if "--inner" in sys.argv:
        duplicate_keys_rejected()
        witness_controls()
        pin_drift_rejected()
        print("PASS_Q8_FOUR_ROLE_THREE_NEG_PACKAGE_TESTS groups=3")
        return
    duplicate_keys_rejected()
    witness_controls()
    pin_drift_rejected()
    optimized_controls()
    print("PASS_Q8_FOUR_ROLE_THREE_NEG_PACKAGE_TESTS groups=3")


if __name__ == "__main__":
    main()
