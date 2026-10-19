#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Package fault controls for PR2753 route_cube key/Counter invoice.

Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PKG_NAME = "pr2753-route-cube-key-counter"
PASS = "PASS_PR2753_ROUTE_CUBE_KEY_COUNTER_PACKAGE_TESTS"


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_TEST: {message}")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True)


def mirror_inputs(tmp_root: Path):
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        src = ROOT / rec["path"]
        dst = tmp_root / rec["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main():
    # 1) Default read-only verify.
    proc = run([sys.executable, "-I", "-B", str(HERE / "verify.py")])
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_PR2753_ROUTE_CUBE_KEY_COUNTER" in proc.stdout, proc.stdout)

    # 2) -O admission via need().
    proc = run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py")])
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_PR2753_ROUTE_CUBE_KEY_COUNTER" in proc.stdout, proc.stdout)

    # 3) Corrupted temporary certificate fails.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        research = tmp_path / "research" / PKG_NAME
        shutil.copytree(HERE, research)
        mirror_inputs(tmp_path)
        cert_sel = tmp_path / "certificates"
        cert_sel.mkdir(parents=True)
        shutil.copy2(
            ROOT / "certificates/selected-result.json",
            cert_sel / "selected-result.json",
        )
        cert = research / "CERTIFICATE.json"
        data = json.loads(cert.read_text(encoding="utf-8"))
        data["claim"]["append_word_cells"] = "corrupted"
        cert.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        proc = run([sys.executable, "-I", "-B", str(research / "verify.py")], cwd=tmp_path)
        need(proc.returncode != 0, "corrupted certificate should fail")

    # 4) Source pin corruption rejection.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        research = tmp_path / "research" / PKG_NAME
        shutil.copytree(HERE, research)
        mirror_inputs(tmp_path)
        cert_sel = tmp_path / "certificates"
        cert_sel.mkdir(parents=True)
        shutil.copy2(
            ROOT / "certificates/selected-result.json",
            cert_sel / "selected-result.json",
        )
        routes = tmp_path / "research/selected-bit-recursive-caller/predecessor/vendor/routes.py"
        routes.write_bytes(routes.read_bytes() + b"\n# corrupt\n")
        proc = run([sys.executable, "-I", "-B", str(research / "verify.py")], cwd=tmp_path)
        need(proc.returncode != 0, "source drift should fail")

    # 5) Independent checker.
    proc = run([sys.executable, "-I", "-B", str(HERE / "independent.py")])
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_INDEPENDENT_PR2753_ROUTE_CUBE_KEY_COUNTER" in proc.stdout, proc.stdout)

    # 6) Duplicate JSON key rejection.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        research = tmp_path / "research" / PKG_NAME
        shutil.copytree(HERE, research)
        mirror_inputs(tmp_path)
        cert_sel = tmp_path / "certificates"
        cert_sel.mkdir(parents=True)
        shutil.copy2(
            ROOT / "certificates/selected-result.json",
            cert_sel / "selected-result.json",
        )
        cert = research / "CERTIFICATE.json"
        text = cert.read_text(encoding="utf-8")
        text = text.replace(
            '"schema_version": 1,',
            '"schema_version": 1,\n  "schema_version": 2,',
            1,
        )
        cert.write_text(text, encoding="utf-8")
        proc = run([sys.executable, "-I", "-B", str(research / "verify.py")], cwd=tmp_path)
        need(proc.returncode != 0, "duplicate JSON key should fail")

    print(f"{PASS} groups=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
