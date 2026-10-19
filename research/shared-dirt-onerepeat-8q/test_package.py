#!/usr/bin/env python3
"""Package fault controls for shared-dirt one-repeat 8q. Wentao Li + AI.

Full census replay is registered on verify.py / independent.py. This harness
only exercises certificate corruption, source-pin drift, duplicate JSON keys,
and need()-under--O admission without re-running the multi-minute census.
"""
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
PKG_NAME = "shared-dirt-onerepeat-8q"
sys.path.insert(0, str(HERE))
import verify as verify_mod  # noqa: E402


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_TEST: {message}")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True)


def main():
    # 1) need() still fires under -O (admission gate).
    proc = run(
        [
            sys.executable,
            "-I",
            "-O",
            "-B",
            "-c",
            (
                "import sys; sys.path.insert(0, "
                + repr(str(HERE))
                + "); import verify; "
                "verify.need(False, 'expected');"
            ),
        ]
    )
    need(proc.returncode != 0, "-O need() must fail closed")
    need("FAIL: expected" in (proc.stderr + proc.stdout), proc.stderr + proc.stdout)

    # 2) Duplicate JSON key rejection.
    with tempfile.TemporaryDirectory() as tmp:
        cert = Path(tmp) / "CERTIFICATE.json"
        raw = (HERE / "CERTIFICATE.json").read_text(encoding="utf-8")
        corrupted = raw.replace(
            '"schema_version": 1,',
            '"schema_version": 1,\n  "schema_version": 2,',
            1,
        )
        need(corrupted != raw, "failed to inject duplicate key")
        cert.write_text(corrupted, encoding="utf-8")
        try:
            verify_mod.load_json_reject_duplicates(cert)
            need(False, "duplicate JSON key should raise")
        except ValueError as exc:
            need("duplicate JSON key" in str(exc), str(exc))

    # 3) Corrupted claim fails compare_certificate.
    live = verify_mod.load_json_reject_duplicates(HERE / "CERTIFICATE.json")
    pinned = json.loads(json.dumps(live))
    pinned["claim"]["min_R"] = 0
    try:
        verify_mod.compare_certificate(live, pinned)
        need(False, "corrupted certificate should fail compare")
    except SystemExit as exc:
        need("FAIL:" in str(exc), str(exc))

    # 4) Source pin corruption rejection (hash mismatch without full census).
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        research = tmp_path / "research" / PKG_NAME
        shutil.copytree(HERE, research)
        pinned_dir = tmp_path / "research" / "mutable-source-shear-cost"
        pinned_dir.mkdir(parents=True)
        src = ROOT / "research" / "mutable-source-shear-cost" / "CERTIFICATE.json"
        (pinned_dir / "CERTIFICATE.json").write_bytes(src.read_bytes() + b"\n")
        # Point verify's ROOT at the temp tree via a tiny driver.
        driver = research / "_pin_check.py"
        driver.write_text(
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
            "import verify\n"
            "verify.ROOT = Path(__file__).resolve().parents[2]\n"
            "verify.HERE = Path(__file__).resolve().parent\n"
            "verify.SOURCES_PATH = verify.HERE / 'SOURCES.json'\n"
            "verify.check_source_pins()\n",
            encoding="utf-8",
        )
        proc = run([sys.executable, "-I", "-B", str(driver)], cwd=tmp_path)
        need(proc.returncode != 0, "source drift should fail")
        need("source bytes mismatch" in (proc.stderr + proc.stdout), proc.stderr + proc.stdout)

    # 5) Live source pin still matches.
    sources = verify_mod.load_json_reject_duplicates(HERE / "SOURCES.json")
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        live_path = ROOT / rec["path"]
        digest = hashlib.sha256(live_path.read_bytes()).hexdigest()
        need(digest == rec["sha256"], f"live pin drift {rec['path']}")

    # 6) Certificate status marker present.
    cert = verify_mod.load_json_reject_duplicates(HERE / "CERTIFICATE.json")
    need(
        cert["status"] == "PASS_SHARED_DIRT_ONEREPEAT_8Q_OBSTRUCTION",
        "status marker",
    )
    need(cert["claim"]["min_R"] == 96, "min_R")
    need(cert["claim"]["tariff_floor_at_X0"] == 496, "tariff")
    need(cert["claim"]["no_new_kappa"] is True, "no_new_kappa")

    print("PASS_SHARED_DIRT_ONEREPEAT_8Q_PACKAGE_TESTS groups=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
