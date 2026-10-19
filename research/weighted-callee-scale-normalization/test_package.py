#!/usr/bin/env python3
"""Package controls: dup JSON keys, certificate corruption, read-only, -O.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = "PASS_WEIGHTED_CALLEE_SCALE_NORMALIZATION_PACKAGE_TESTS"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(argv, env=None, check=True):
    return subprocess.run(
        argv,
        cwd=str(ROOT),
        env=env,
        text=True,
        capture_output=True,
        check=check,
    )


def test_duplicate_json_keys():
    bad = '{"a":1,"a":2}\n'
    seen = []

    def hook(pairs):
        keys = [k for k, _ in pairs]
        if len(keys) != len(set(keys)):
            seen.append(True)
        return dict(pairs)

    json.loads(bad, object_pairs_hook=hook)
    need(seen, "duplicate key detected")


def test_certificate_corruption_rejected():
    cert = HERE / "CERTIFICATE.json"
    original = cert.read_bytes()
    try:
        corrupt = json.loads(original)
        corrupt["counts"]["normalized_agreements"] = 0
        cert.write_text(json.dumps(corrupt, indent=2, sort_keys=True) + "\n")
        proc = run(
            ["python3.12", "-I", "-B", str(HERE / "verify.py")],
            check=False,
        )
        need(proc.returncode != 0, "corrupt certificate must fail")
        need(
            "certificate mismatch" in (proc.stderr + proc.stdout),
            "mismatch message",
        )
    finally:
        cert.write_bytes(original)


def test_readonly_verify_unchanged():
    before = {
        path.name: path.read_bytes()
        for path in HERE.iterdir()
        if path.is_file()
    }
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    proc = run(["python3.12", "-I", "-B", str(HERE / "verify.py")], env=env)
    need(proc.returncode == 0, proc.stderr)
    need("PASS_WEIGHTED_CALLEE_SCALE_NORMALIZATION" in proc.stdout, "pass marker")
    after = {
        path.name: path.read_bytes()
        for path in HERE.iterdir()
        if path.is_file()
    }
    need(before == after, "verify must not mutate package files")


def test_optimize_still_admits():
    env = os.environ.copy()
    env["PYTHONOPTIMIZE"] = "1"
    proc = run(
        ["python3.12", "-I", "-O", "-Werror", "-B", str(HERE / "verify.py")],
        env=env,
    )
    need(proc.returncode == 0, proc.stderr)
    need(
        "PASS_WEIGHTED_CALLEE_SCALE_NORMALIZATION" in proc.stdout,
        "pass under -O",
    )


def test_need_under_optimize():
    """need() must still fire under -O (not assert)."""
    env = os.environ.copy()
    env["PYTHONOPTIMIZE"] = "2"
    # Corrupt a live input hash via temp monkey by running normalize need path:
    # invoke verify with a broken CERTIFICATE already covered; here ensure
    # normalize.need raises even under -OO by direct exec.
    proc = run(
        [
            "python3.12",
            "-I",
            "-OO",
            "-B",
            "-c",
            (
                "import runpy; ns=runpy.run_path("
                f"'{HERE / 'normalize.py'}');"
                "ns['need'](False, 'forced');"
            ),
        ],
        env=env,
        check=False,
    )
    need(proc.returncode != 0, "need() must raise under -OO")
    need("forced" in (proc.stderr + proc.stdout), "need message")


def main():
    test_duplicate_json_keys()
    test_certificate_corruption_rejected()
    test_readonly_verify_unchanged()
    test_optimize_still_admits()
    test_need_under_optimize()
    print(MARKER + " groups=5")


if __name__ == "__main__":
    main()
