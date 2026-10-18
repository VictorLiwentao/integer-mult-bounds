#!/usr/bin/env python3
"""Package controls: duplicate JSON keys, certificate corruption, read-only verify.

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
MARKER = "PASS_ODD_KERNEL_ALT_TARIFF_CENSUS_PACKAGE_TESTS"


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
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "dup.json"
        path.write_text(bad)
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
        corrupt["counts"]["odd_fused_beats_dyadic_total"] = 99
        cert.write_text(json.dumps(corrupt, indent=2, sort_keys=True) + "\n")
        proc = run(
            ["python3.12", "-I", "-B", str(HERE / "verify.py")],
            check=False,
        )
        need(proc.returncode != 0, "corrupt certificate must fail")
        need("certificate mismatch" in (proc.stderr + proc.stdout),
             "mismatch message")
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
    need("PASS_ODD_KERNEL_ALT_TARIFF_CENSUS" in proc.stdout, "pass marker")
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
    need("PASS_ODD_KERNEL_ALT_TARIFF_CENSUS" in proc.stdout, "pass under -O")


def main():
    test_duplicate_json_keys()
    test_certificate_corruption_rejected()
    test_readonly_verify_unchanged()
    test_optimize_still_admits()
    print(MARKER + " groups=4")


if __name__ == "__main__":
    main()
