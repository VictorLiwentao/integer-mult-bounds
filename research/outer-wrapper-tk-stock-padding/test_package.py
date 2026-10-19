#!/usr/bin/env python3
"""Admission, corruption, and scanner-agreement checks. No assert statements."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent
import verify


def need(ok, message):
    if not ok:
        raise ValueError(message)


def test_duplicate_key():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "dup.json"
        path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
        try:
            verify.read_json(path)
        except ValueError as exc:
            need(str(exc) == "duplicate JSON key", "duplicate message")
        else:
            need(False, "duplicate key accepted")


def test_corrupt_certificate():
    observed = verify.evaluate()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "CERTIFICATE.json"
        blob = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
        blob["sigma"] = 6747
        path.write_text(json.dumps(blob), encoding="utf-8")
        bad = verify.read_json(path)
        try:
            verify.admit(observed, bad)
        except ValueError as exc:
            need(str(exc) == "certificate mismatch", "corruption message")
        else:
            need(False, "corrupt certificate accepted")
    live = verify.read_json(HERE / "CERTIFICATE.json")
    need(live["sigma"] == 6748, "on-disk certificate mutated")


def test_optimized_admission():
    script = (
        "import sys\n"
        "from pathlib import Path\n"
        f"sys.path.insert(0, {str(HERE)!r})\n"
        "import verify\n"
        "verify.need(__debug__ is False, 'optimization off')\n"
        "try:\n"
        "    verify.need(False, 'admission')\n"
        "except ValueError as exc:\n"
        "    if str(exc) != 'admission':\n"
        "        raise SystemExit('wrong admission')\n"
        "else:\n"
        "    raise SystemExit('admission skipped')\n"
        "print('PASS_OPTIMIZED_ADMISSION')\n"
    )
    done = subprocess.run(
        [sys.executable, "-O", "-I", "-B", "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    need(done.returncode == 0, "optimized admission failed: " + done.stderr)
    need("PASS_OPTIMIZED_ADMISSION" in done.stdout, "optimized marker")


def test_padding_domain():
    need(verify.padding_fits(11, 10), "t=q-1 accepted")
    need(not verify.padding_fits(11, 0), "t=0 rejected")
    need(not verify.padding_fits(2, -1), "negative stock rejected")
    need(verify.multiplicity_room(1), "w=1 room")
    need(Fraction(28, 17) * 4097 == 6748, "6748 identity")
    need(Fraction(28, 17) * 4097 != 6747, "6747 rejected")


def test_hash_rejection():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "blob.txt"
        path.write_bytes(b"nope")
        try:
            verify.need(
                hashlib.sha256(path.read_bytes()).hexdigest() == "0" * 64,
                "source hash: temp",
            )
        except ValueError as exc:
            need("source hash" in str(exc), "hash message")
        else:
            need(False, "bad hash accepted")


def test_scanners_agree():
    primary = verify.evaluate()
    secondary = independent.evaluate()
    for key in (
        "status",
        "sigma",
        "ell",
        "lcm",
        "multiplicity_domain",
        "stock_shape",
        "below_two_padding",
        "stages",
        "no_new_kappa",
        "kappa_decimal",
        "marker",
    ):
        need(primary[key] == secondary[key], "scanner disagree: " + key)


def test_package_read_only():
    before = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in HERE.iterdir()
        if path.is_file()
    }
    verify.evaluate()
    independent.evaluate()
    after = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in HERE.iterdir()
        if path.is_file()
    }
    need(before == after, "package files mutated")


def main():
    tests = (
        test_duplicate_key,
        test_corrupt_certificate,
        test_optimized_admission,
        test_padding_domain,
        test_hash_rejection,
        test_scanners_agree,
        test_package_read_only,
    )
    for test in tests:
        test()
    print("PASS_OUTER_WRAPPER_TK_STOCK_PADDING_TESTS groups=" + str(len(tests)))


if __name__ == "__main__":
    main()
