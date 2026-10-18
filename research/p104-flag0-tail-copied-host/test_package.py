#!/usr/bin/env python3
"""Admission, corruption, census controls and scanner-agreement checks."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import independent
import verify

SLUG = "research/" + HERE.name


def need(ok, message):
    if not ok:
        raise ValueError(message)


def tree_digest(paths):
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def watched_files():
    files = [path for path in HERE.iterdir() if path.is_file()]
    files.extend(ROOT / name for name in verify.INPUTS)
    return sorted(files)


def test_duplicate_key():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "dup.json"
        path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
        for reader in (verify.read_json, independent.read_json):
            try:
                reader(path)
            except ValueError as exc:
                need(str(exc) == "duplicate JSON key", "duplicate message")
            else:
                need(False, "duplicate key accepted")


def stage_tree(tmp):
    root = Path(tmp)
    for name in verify.INPUTS:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    package = root / SLUG
    package.mkdir(parents=True)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in (".py", ".json"):
            shutil.copyfile(path, package / path.name)
    return root, package


def run_optimized(script):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(script)],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )


def expect_rejection(script, needle):
    done = run_optimized(script)
    need(done.returncode != 0, "corruption accepted: " + script.name)
    need(needle in done.stderr, "wrong rejection for " + script.name + ": " + done.stderr[-300:])


def test_temp_copy_corruption():
    before = tree_digest(watched_files())
    with tempfile.TemporaryDirectory() as tmp:
        root, package = stage_tree(tmp)
        for name in ("verify.py", "independent.py"):
            done = run_optimized(package / name)
            need(done.returncode == 0, "clean temp copy failed: " + done.stderr[-300:])
        cert = package / "CERTIFICATE.json"
        clean = cert.read_bytes()
        mutations = (
            ("nonself_cochart_host_count", 0),
            ("dirty_helper_touches_in_window", 1),
            ("endpoint_repay_x0_to_initial", True),
            ("all_x_cochart_nonself_count", 0),
            ("exemplar_nonself_owner", "D0"),
            ("unique_owner_among_add_5759_named_registers", False),
        )
        for key, value in mutations:
            blob = json.loads(clean)
            blob[key] = value
            cert.write_text(json.dumps(blob, indent=2) + "\n", encoding="utf-8")
            for script_name in ("verify.py", "independent.py"):
                expect_rejection(package / script_name, "certificate mismatch")
            cert.write_bytes(clean)
        # Corrupt gzipped witness in the staged tree.
        witness = root / verify.INPUTS[1]
        witness.write_bytes(b"not-a-gzip")
        for script_name in ("verify.py", "independent.py"):
            done = run_optimized(package / script_name)
            need(done.returncode != 0, "corrupt witness accepted")
    after = tree_digest(watched_files())
    need(before == after, "checkout mutated by temp-copy tests")


def test_optimized_admission():
    before = tree_digest(watched_files())
    # Force a failing need under -O: wrong certificate kappa.
    with tempfile.TemporaryDirectory() as tmp:
        _root, package = stage_tree(tmp)
        cert = package / "CERTIFICATE.json"
        blob = json.loads(cert.read_text(encoding="utf-8"))
        blob["selected_kappa"] = "0"
        cert.write_text(json.dumps(blob, indent=2) + "\n", encoding="utf-8")
        for script_name in ("verify.py", "independent.py"):
            expect_rejection(package / script_name, "certificate mismatch")
    after = tree_digest(watched_files())
    need(before == after, "checkout mutated by admission tests")


def test_census_control():
    """Dropping one nonself host from the certificate must fail."""
    before = tree_digest(watched_files())
    with tempfile.TemporaryDirectory() as tmp:
        _root, package = stage_tree(tmp)
        cert = package / "CERTIFICATE.json"
        blob = json.loads(cert.read_text(encoding="utf-8"))
        blob["nonself_cochart_hosts"] = blob["nonself_cochart_hosts"][:-1]
        blob["nonself_cochart_host_count"] = 46
        cert.write_text(json.dumps(blob, indent=2) + "\n", encoding="utf-8")
        for script_name in ("verify.py", "independent.py"):
            expect_rejection(package / script_name, "certificate mismatch")
    after = tree_digest(watched_files())
    need(before == after, "checkout mutated by census control")


def test_scanner_agreement():
    forward = verify.evaluate()
    indexed = independent.evaluate()
    need(forward["nonself_cochart"] == indexed["nonself_cochart"] == 47, "nonself agree")
    need(
        forward["all_x_cochart_nonself"] == indexed["all_x_cochart_nonself"] == 103,
        "all-X agree",
    )
    need(forward["dirty_helper_touches"] == indexed["dirty_helper_touches"] == 0, "dirt")
    need(forward["endpoint_repay"] == indexed["endpoint_repay"] == 0, "repay")


def test_read_only_replay():
    before = tree_digest(watched_files())
    for script in (HERE / "verify.py", HERE / "independent.py"):
        done = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )
        need(done.returncode == 0, script.name + " failed: " + done.stderr[-300:])
        need("PASS_P104_FLAG0_TAIL_COPIED_HOST" in done.stdout, script.name + " marker")
    after = tree_digest(watched_files())
    need(before == after, "checkout mutated by read-only replay")


def main():
    test_duplicate_key()
    test_temp_copy_corruption()
    test_optimized_admission()
    test_census_control()
    test_scanner_agreement()
    test_read_only_replay()
    print("PASS_P104_FLAG0_TAIL_COPIED_HOST_TESTS groups=6")


if __name__ == "__main__":
    main()
