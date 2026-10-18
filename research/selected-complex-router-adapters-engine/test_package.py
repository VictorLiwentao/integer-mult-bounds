#!/usr/bin/env python3
"""Admission, corruption, and scanner-agreement checks. No assert statements."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent
import router
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
        blob["routing_adapters_rho_contribution"] = 1
        path.write_text(json.dumps(blob), encoding="utf-8")
        bad = verify.read_json(path)
        try:
            verify.admit(observed, bad)
        except ValueError as exc:
            need(str(exc) == "certificate mismatch", "corruption message")
        else:
            need(False, "corrupt certificate accepted")
    live = verify.read_json(HERE / "CERTIFICATE.json")
    need(live["routing_adapters_rho_contribution"] == 0, "on-disk certificate mutated")


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


def test_ordinary_mutant_measured():
    out = router.run_router_adapters([1, 0], [0, 1], mutate="ordinary")
    need(out["ordinary_leaf_calls"] == 1, "ordinary not measured")
    need(out["rho_contrib"] == 1, "ordinary rho")


def test_endpoint_closed_form():
    F = router.identity(3)
    s = [1, 0, 1]
    x = [1, 1, 0]
    y = [0, 0, 1]
    out = router.run_router_adapters(x, y, F=F, pauli_support=s)
    exp_x, exp_y = router.expected_endpoint(x, y, F, s)
    need(out["x"] == exp_x and out["y"] == exp_y, "closed form")


def test_read_only_package_hash():
    before = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(HERE.iterdir())
        if path.is_file()
    }
    verify.evaluate()
    independent.main()
    after = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(HERE.iterdir())
        if path.is_file()
    }
    need(before == after, "package files mutated by replay")


def main():
    test_duplicate_key()
    test_corrupt_certificate()
    test_optimized_admission()
    test_ordinary_mutant_measured()
    test_endpoint_closed_form()
    test_read_only_package_hash()
    print("PASS_SELECTED_COMPLEX_ROUTER_ADAPTERS_ENGINE_TESTS groups=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
