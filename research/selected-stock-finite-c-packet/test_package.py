#!/usr/bin/env python3
"""Admission, corruption, and scanner-agreement checks. No assert statements."""

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
        blob["packet_cardinality_factors"]["packet_bits"] = 2641
        path.write_text(json.dumps(blob), encoding="utf-8")
        bad = verify.read_json(path)
        try:
            verify.admit(observed, bad)
        except ValueError as exc:
            need(str(exc) == "certificate mismatch", "corruption message")
        else:
            need(False, "corrupt certificate accepted")
    live = verify.read_json(HERE / "CERTIFICATE.json")
    need(live["packet_cardinality_factors"]["packet_bits"] == 2642,
         "on-disk certificate mutated")


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


def test_w_injection_control():
    need(
        not verify.atom_width_free("group=2**(36*36); stock=group*q**(w-1)"),
        "w injection accepted",
    )
    need(
        verify.atom_width_free(
            "group=2**(36*36)\n for j in range(1,37):group*=2**(2*j)-1\n"
            " stock=group*invoice['physical']\n"
        ),
        "clean stock block rejected",
    )


def test_omit_restore_control():
    fixture = verify.coarse_residual_fixture(5, 2)
    need(fixture["omit_restore_diverges"] is True, "omit-restore control")


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
    before = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in HERE.iterdir()
        if path.is_file()
    }
    left = verify.evaluate()
    right = independent.evaluate()
    need(
        left["packet_cardinality_factors"]["packet_bits"]
        == right["packet_cardinality_factors"]["packet_bits"]
        == 2642,
        "packet bits disagreement",
    )
    need(left["marker"] == right["marker"], "marker disagreement")
    need(left["atom_width_free_stock_block"] is True, "w-free flag")
    need(left["rho"] == right["rho"] == "unbound", "rho disagreement")
    need(left["outer_adoption"] == "not_claimed", "adoption oversell")
    verify.admit(left, verify.read_json(HERE / "CERTIFICATE.json"))
    after = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in HERE.iterdir()
        if path.is_file()
    }
    need(before == after, "package files mutated")


def main():
    test_duplicate_key()
    test_corrupt_certificate()
    test_optimized_admission()
    test_w_injection_control()
    test_omit_restore_control()
    test_hash_rejection()
    test_scanners_agree()
    print("PASS_SELECTED_STOCK_FINITE_C_PACKET_TESTS groups=7")


if __name__ == "__main__":
    main()
