#!/usr/bin/env python3
"""Package fault controls for transfer-coupled 7q obstruction. Wentao Li + AI."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PKG_NAME = "transfer-coupled-7q-obstruction"


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_TEST: {message}")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True)


def main():
    # 1) Quick read-only verify (champions + tariff).
    proc = run([sys.executable, "-I", "-B", str(HERE / "verify.py"), "--quick"])
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_TRANSFER_COUPLED_7Q_OBSTRUCTION" in proc.stdout, proc.stdout)

    # 2) -O admission via need().
    proc = run(
        [sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"), "--quick"]
    )
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_TRANSFER_COUPLED_7Q_OBSTRUCTION" in proc.stdout, proc.stdout)

    # 3) Certificate claim corruption fails.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        research = tmp_path / "research" / PKG_NAME
        shutil.copytree(HERE, research)
        pinned = tmp_path / "research" / "mutable-source-shear-cost"
        pinned.mkdir(parents=True)
        shutil.copy2(
            ROOT / "research" / "mutable-source-shear-cost" / "CERTIFICATE.json",
            pinned / "CERTIFICATE.json",
        )
        cert = research / "CERTIFICATE.json"
        data = json.loads(cert.read_text(encoding="utf-8"))
        data["claim"]["global_min_R"] = 0
        cert.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        proc = run(
            [sys.executable, "-I", "-B", str(research / "verify.py"), "--quick"],
            cwd=tmp_path,
        )
        need(proc.returncode != 0, "corrupted certificate should fail")

    # 4) Source pin corruption rejection.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        research = tmp_path / "research" / PKG_NAME
        shutil.copytree(HERE, research)
        pinned = tmp_path / "research" / "mutable-source-shear-cost"
        pinned.mkdir(parents=True)
        src = ROOT / "research" / "mutable-source-shear-cost" / "CERTIFICATE.json"
        (pinned / "CERTIFICATE.json").write_bytes(src.read_bytes() + b"\n")
        proc = run(
            [sys.executable, "-I", "-B", str(research / "verify.py"), "--quick"],
            cwd=tmp_path,
        )
        need(proc.returncode != 0, "source drift should fail")

    # 5) Binding champion dual (lightweight independent smoke).
    proc = run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            (
                "import json,sys; from pathlib import Path; "
                "sys.path.insert(0, str(Path('research/transfer-coupled-7q-obstruction').resolve())); "
                "from model import even_table, dual_independent_R, tariff_with_transfer; "
                "r=dual_independent_R(even_table((0,1,2,4,8,15)), even_table((0,1,2,4,8,16))); "
                "assert r==84; assert tariff_with_transfer(7,84,0,1)==436; "
                "print('PASS_TRANSFER_COUPLED_SMOKE R=84 tariff=436')"
            ),
        ]
    )
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_TRANSFER_COUPLED_SMOKE" in proc.stdout, proc.stdout)

    # 6) Duplicate JSON key rejection.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        research = tmp_path / "research" / PKG_NAME
        shutil.copytree(HERE, research)
        pinned = tmp_path / "research" / "mutable-source-shear-cost"
        pinned.mkdir(parents=True)
        shutil.copy2(
            ROOT / "research" / "mutable-source-shear-cost" / "CERTIFICATE.json",
            pinned / "CERTIFICATE.json",
        )
        cert = research / "CERTIFICATE.json"
        raw = cert.read_text(encoding="utf-8")
        corrupted = raw.replace(
            '"schema_version": 1,',
            '"schema_version": 1,\n  "schema_version": 2,',
            1,
        )
        need(corrupted != raw, "failed to inject duplicate key")
        cert.write_text(corrupted, encoding="utf-8")
        proc = run(
            [sys.executable, "-I", "-B", str(research / "verify.py"), "--quick"],
            cwd=tmp_path,
        )
        need(proc.returncode != 0, "duplicate JSON key should fail")

    print("PASS_TRANSFER_COUPLED_7Q_PACKAGE_TESTS groups=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
