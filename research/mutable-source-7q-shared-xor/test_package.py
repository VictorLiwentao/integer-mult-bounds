#!/usr/bin/env python3
"""Package fault controls for the 7Q shared-XOR obstruction. Wentao Li + AI, Apache-2.0."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_TEST: {message}")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True)


def main():
    # 1) Quick verify against committed certificate.
    proc = run([sys.executable, "-I", "-B", str(HERE / "verify.py"), "--quick"])
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_MUTABLE_SOURCE_7Q_SHARED_XOR_QUICK" in proc.stdout, proc.stdout)

    # 2) -O quick admission.
    proc = run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"), "--quick"])
    need(proc.returncode == 0, "quick under -O: " + proc.stderr + proc.stdout)

    # 3) Certificate drift rejection on a temp copy (quick path).
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pkg = tmp_path / "research" / "mutable-source-7q-shared-xor"
        shutil.copytree(HERE, pkg)
        for rel in (
            "research/mutable-source-shear-cost/README.md",
            "research/mutable-source-connector/README.md",
            "certificates/selected-result.json",
            "docs/research/agent-task-catalog.json",
        ):
            dest = tmp_path / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)
        cert_path = pkg / "CERTIFICATE.json"
        data = json.loads(cert_path.read_text())
        data["interleaved_census"]["paths_with_X_le_2"] = 99
        cert_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        proc = run(
            [sys.executable, "-I", "-B", str(pkg / "verify.py"), "--quick"],
            cwd=tmp_path,
        )
        need(proc.returncode != 0, "corrupted certificate should fail quick verify")

    # 4) Source pin corruption rejection.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pkg = tmp_path / "research" / "mutable-source-7q-shared-xor"
        shutil.copytree(HERE, pkg)
        for rel in (
            "research/mutable-source-shear-cost/README.md",
            "research/mutable-source-connector/README.md",
            "certificates/selected-result.json",
            "docs/research/agent-task-catalog.json",
        ):
            dest = tmp_path / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)
        target = tmp_path / "research/mutable-source-shear-cost/README.md"
        target.write_bytes(target.read_bytes() + b"\n")
        proc = run(
            [sys.executable, "-I", "-B", str(pkg / "verify.py"), "--quick"],
            cwd=tmp_path,
        )
        need(proc.returncode != 0, "source drift should fail")

    # 5) Independent checker.
    proc = run([sys.executable, "-I", "-B", str(HERE / "independent.py")])
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_INDEPENDENT_7Q_SHARED_XOR" in proc.stdout, proc.stdout)

    # 6) Duplicate JSON key detector armed.
    text = (HERE / "CERTIFICATE.json").read_text()
    bad = text.replace('"no_new_kappa": true', '"no_new_kappa": true, "no_new_kappa": false', 1)
    dup = []

    def hook(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            dup.append(True)
        return dict(items)

    json.loads(bad, object_pairs_hook=hook)
    need(dup, "duplicate key detector armed")

    print("PASS_MUTABLE_SOURCE_7Q_SHARED_XOR_PACKAGE_TESTS groups=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
