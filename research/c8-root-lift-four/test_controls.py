#!/usr/bin/env python3
"""Failure controls for the C8 root-lift package. The package tree is not modified."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
PY = sys.executable


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL_C8_ROOT_LIFT_CONTROLS " + message)


def run(argv, cwd):
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positive(copy):
    observed = run([PY, "-I", "-O", "-Werror", "-B", "verify.py"], copy)
    need(observed.returncode == 0 and "PASS_C8_ROOT_LIFT_FOUR" in observed.stdout, "positive verify")
    other = run([PY, "-I", "-O", "-Werror", "-B", "independent.py"], copy)
    need(other.returncode == 0 and "PASS_C8_ROOT_LIFT_INDEPENDENT" in other.stdout, "positive independent")


def main():
    before = {path.name: sha256(path) for path in PACKAGE.iterdir() if path.is_file()}
    with tempfile.TemporaryDirectory(prefix="c8-root-") as tmp:
        copy = Path(tmp) / "pkg"
        shutil.copytree(PACKAGE, copy, ignore=shutil.ignore_patterns("__pycache__"))
        positive(copy)
        receipt = sha256(copy / "RESULT.json")
        again = run([PY, "-I", "-O", "-Werror", "-B", "verify.py"], copy)
        need(again.returncode == 0 and sha256(copy / "RESULT.json") == receipt, "read-only verify")

        broken = json.loads((copy / "RESULT.json").read_text(encoding="utf-8"))
        broken["minimum"] = 3
        (copy / "RESULT.json").write_text(json.dumps(broken, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        mismatch = run([PY, "-I", "-O", "-Werror", "-B", "verify.py"], copy)
        need(mismatch.returncode != 0, "tampered minimum was accepted")
        (copy / "RESULT.json").write_bytes((PACKAGE / "RESULT.json").read_bytes())

        text = (copy / "RESULT.json").read_text(encoding="utf-8")
        text = text.replace('"minimum": 4,', '"minimum": 4,\n  "minimum": 4,', 1)
        (copy / "RESULT.json").write_text(text, encoding="utf-8")
        duplicate = run([PY, "-I", "-O", "-Werror", "-B", "verify.py"], copy)
        need(duplicate.returncode != 0 and "duplicate JSON key" in (duplicate.stdout + duplicate.stderr), "duplicate key")
        (copy / "RESULT.json").write_bytes((PACKAGE / "RESULT.json").read_bytes())

        source = (copy / "algebra.py").read_text(encoding="utf-8")
        need("len(term) in (1, 3)" in source, "dead-branch marker moved")
        (copy / "algebra.py").write_text(
            source.replace("len(term) in (1, 3)", "len(term) == 1", 1), encoding="utf-8"
        )
        weakened = run([PY, "-I", "-O", "-Werror", "-B", "verify.py"], copy)
        need(weakened.returncode != 0, "weakened triple exclusion was accepted")
        (copy / "algebra.py").write_text(source, encoding="utf-8")

        search = (copy / "independent.py").read_text(encoding="utf-8")
        planted = search.replace(
            "if mul(goal, inverse, table) in length2:",
            "if True or mul(goal, inverse, table) in length2:",
            1,
        )
        (copy / "independent.py").write_text(planted, encoding="utf-8")
        false_hit = run([PY, "-I", "-O", "-Werror", "-B", "independent.py"], copy)
        need(false_hit.returncode != 0, "planted length-3 hit was accepted")
        (copy / "independent.py").write_text(search, encoding="utf-8")
        positive(copy)

    after = {path.name: sha256(path) for path in PACKAGE.iterdir() if path.is_file()}
    need(before == after, "package bytes changed")
    print(
        "PASS_C8_ROOT_LIFT_CONTROLS faults=4 optimized_cli=4 "
        "duplicate_key=1 read_only=1 source_immutable"
    )


if __name__ == "__main__":
    main()
