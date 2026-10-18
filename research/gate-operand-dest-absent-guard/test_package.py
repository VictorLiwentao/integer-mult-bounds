#!/usr/bin/env python3
"""Behavioral controls for gate-operand-dest-absent-guard."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import verify  # noqa: E402

MARKER = "PASS_GATE_OPERAND_DEST_ABSENT_PACKAGE_TESTS"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def file_hashes(directory):
    rows = {}
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            rows[str(path.relative_to(directory))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return rows


def test_duplicate_json_keys():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "dup.json"
        path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
        try:
            verify.read_json(path)
        except ValueError as exc:
            need(str(exc) == "duplicate JSON key", "duplicate message")
        else:
            need(False, "duplicate key accepted")


def test_certificate_corruption_rejected():
    observed = verify.evaluate()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "CERTIFICATE.json"
        blob = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
        blob["claim"]["oq1_dest_absent_preserves_dest_free_agree"] = False
        path.write_text(json.dumps(blob, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        bad = verify.read_json(path)
        try:
            verify.need(observed == bad, "certificate mismatch")
        except ValueError as exc:
            need(str(exc) == "certificate mismatch", "corruption message")
        else:
            need(False, "corrupt certificate accepted")
    live = verify.read_json(HERE / "CERTIFICATE.json")
    need(live["claim"]["oq1_dest_absent_preserves_dest_free_agree"] is True,
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


def test_readonly_verify_unchanged():
    before = file_hashes(HERE)
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(HERE / "verify.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    need(proc.returncode == 0, "verify failed: " + proc.stderr)
    need("PASS_GATE_OPERAND_DEST_ABSENT_GUARD" in proc.stdout, "missing PASS marker")
    after = file_hashes(HERE)
    need(before == after, "verify must be read-only")


def test_predecessor_package_untouched():
    """Leave-alone: do not rewrite #3696 census claim or package marker."""
    pred = ROOT / "research" / "gate-operand-export-parity"
    need(pred.is_dir(), "predecessor package present")
    cert = json.loads((pred / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(cert["status"] == "PASS_GATE_OPERAND_EXPORT_PARITY", "predecessor status")
    need(cert["claim"]["small_domain"]["dest_free_agree"] == 4686, "leave census")
    need(cert["selected_word"]["gates"] == 5472, "leave selected count")


def main():
    test_duplicate_json_keys()
    test_certificate_corruption_rejected()
    test_optimized_admission()
    test_readonly_verify_unchanged()
    test_predecessor_package_untouched()
    print(MARKER)


if __name__ == "__main__":
    main()
