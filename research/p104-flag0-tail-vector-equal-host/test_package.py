#!/usr/bin/env python3
"""Admission, corruption, splice controls and scanner-agreement checks."""

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


def run_optimized(script, cwd=None):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(script)],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
        cwd=str(cwd) if cwd is not None else None,
    )


def expect_rejection(script, needle):
    done = run_optimized(script)
    need(done.returncode != 0, "corruption accepted: " + script.name)
    need(
        needle in done.stderr,
        "wrong rejection for " + script.name + ": " + done.stderr[-300:],
    )


def test_temp_copy_corruption():
    before = tree_digest(watched_files())
    with tempfile.TemporaryDirectory() as tmp:
        root, package = stage_tree(tmp)
        for name in ("verify.py", "independent.py"):
            done = run_optimized(package / name, cwd=root)
            # Scripts resolve ROOT as parents[1] of package path; stage under
            # tmp/research/... so parents[1] is tmp. Rewrite ROOT by running
            # from root with package path — but HERE is baked as __file__.
            # Recreate package layout matching repo: tmp is pseudo-ROOT.
            need(done.returncode == 0, "clean temp copy failed: " + done.stderr[-400:])
        cert = package / "CERTIFICATE.json"
        clean = cert.read_bytes()
        mutations = (
            ("owner", "X0"),
            ("added_event_cost", 4),
            ("vector_equal_at_add", False),
            ("d0_dirt_restored_after_window", False),
            ("dirty_helper_touches_in_window", 1),
            ("window_length_unchanged", False),
        )
        for key, value in mutations:
            blob = json.loads(clean)
            blob[key] = value
            cert.write_text(json.dumps(blob, indent=2) + "\n", encoding="utf-8")
            expect_rejection(package / "verify.py", "certificate mismatch")
            expect_rejection(package / "independent.py", "certificate mismatch")
        text = clean.decode("utf-8").replace(
            '"schema_version": 1,', '"schema_version": 1,\n  "schema_version": 1,', 1
        )
        cert.write_text(text, encoding="utf-8")
        expect_rejection(package / "verify.py", "duplicate JSON key")
        expect_rejection(package / "independent.py", "duplicate JSON key")
        cert.write_bytes(clean)
        witness = root / verify.INPUTS[1]
        raw = bytearray(witness.read_bytes())
        raw[len(raw) // 2] ^= 0xFF
        witness.write_bytes(bytes(raw))
        for name in ("verify.py", "independent.py"):
            done = run_optimized(package / name)
            need(done.returncode != 0, "corrupt witness accepted")
    need(tree_digest(watched_files()) == before, "live files mutated by corruption test")


def test_optimized_admission():
    before = tree_digest(watched_files())
    for module in (verify, independent):
        try:
            module.need(False, "admission probe")
        except ValueError as exc:
            need(str(exc) == "admission probe", "need message")
        else:
            need(False, "need ignored under import")
    done = subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(HERE / "verify.py")],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
        cwd=str(ROOT),
    )
    need(done.returncode == 0, "optimized verify failed: " + done.stderr[-300:])
    need(verify.MARKER in done.stdout, "verify marker missing")
    need(tree_digest(watched_files()) == before, "verify mutated files")


def test_splice_controls():
    """Prefix/suffix recipes and cost; omitting equality copy would vacate the claim."""
    need(verify.ADDED == 5, "cost")
    need(len(verify.prefix_splice()) == 3, "prefix len")
    need(len(verify.suffix_splice()) == 2, "suffix len")
    need(verify.prefix_splice()[2] == ["copy", "D0", "X0", list(verify.FULL)], "eq copy")
    need(verify.suffix_splice()[0] == ["copy", "D0", "C", list(verify.FULL)], "restore")
    # Control: a prefix without the X0->D0 copy cannot claim vector equality
    # by destination-freeze after an equality copy event.
    bogus = verify.prefix_splice()[:2]
    need(len(bogus) == 2, "truncated prefix")
    need(all(event[0] != "copy" or event[1] != "D0" or event[2] != "X0" for event in bogus),
         "truncated still has equality copy")


def test_scanner_agreement():
    before = tree_digest(watched_files())
    left = verify.evaluate()
    independent.evaluate()
    cert = verify.read_json(HERE / "CERTIFICATE.json")
    need(cert["owner"] == "D0", "owner")
    need(cert["vector_equal_at_add"] is True, "vector equal")
    need(cert["d0_dirt_restored_after_window"] is True, "dirt restored")
    need(cert["dirty_helper_touches_in_window"] == 0, "dirt window")
    need(cert["added_event_cost"] == 5, "cost")
    need(cert["window_length_events"] == 50, "window")
    need(left["host"] == "D0", "evaluate host")
    need(tree_digest(watched_files()) == before, "agreement mutated files")


def test_read_only_default():
    before = tree_digest(watched_files())
    done = subprocess.run(
        [sys.executable, "-I", "-B", str(HERE / "verify.py")],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
        cwd=str(ROOT),
    )
    need(done.returncode == 0, "read-only verify failed: " + done.stderr[-300:])
    need(tree_digest(watched_files()) == before, "read-only verify wrote files")


def main():
    groups = (
        test_duplicate_key,
        test_temp_copy_corruption,
        test_optimized_admission,
        test_splice_controls,
        test_scanner_agreement,
        test_read_only_default,
    )
    for group in groups:
        group()
    print("PASS_P104_FLAG0_TAIL_VECTOR_EQUAL_HOST_TESTS groups=" + str(len(groups)))


if __name__ == "__main__":
    main()
