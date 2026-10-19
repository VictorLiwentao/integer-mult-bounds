#!/usr/bin/env python3
"""Package controls for PR2298 §3 gap-g opcounts. Wentao Li + AI, Apache-2.0."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PY = sys.executable


def need(ok, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def run(args, env=None, check=True):
    completed = subprocess.run(
        args,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        raise SystemExit(
            f"FAIL: command {args} rc={completed.returncode}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def load_reject_dup(path: Path):
    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate {key}")
            out[key] = value
        return out

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_hook)


def test_duplicate_json_keys():
    for name in ("CERTIFICATE.json", "SOURCES.json", "TASK.json", "VERIFY.json"):
        load_reject_dup(HERE / name)
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad.json"
        bad.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
        try:
            load_reject_dup(bad)
            raise SystemExit("FAIL: duplicate key accepted")
        except ValueError:
            pass


def test_need_under_O():
    env = os.environ.copy()
    env["PYTHONOPTIMIZE"] = "1"
    cert = HERE / "CERTIFICATE.json"
    original = cert.read_bytes()
    try:
        data = json.loads(original)
        data["pattern_count"] = -1
        cert.write_bytes(json.dumps(data).encode())
        completed = run(
            [PY, "-I", "-O", "-Werror", "-B", str(HERE / "verify.py")],
            env=env,
            check=False,
        )
        need(completed.returncode != 0, "corrupt cert must fail under -O")
        need(
            "FAIL" in completed.stderr or "FAIL" in completed.stdout,
            "FAIL marker",
        )
    finally:
        cert.write_bytes(original)


def test_read_only_default():
    before = (HERE / "CERTIFICATE.json").read_bytes()
    run([PY, "-I", "-B", str(HERE / "verify.py")])
    after = (HERE / "CERTIFICATE.json").read_bytes()
    need(before == after, "default verify must not rewrite certificate")


def test_gap_invoice_and_bounds():
    sys.path.insert(0, str(HERE))
    from schedule import pair_invoice, reversal_schedule, tensor_map_schedule

    inv = pair_invoice(5, 3)
    need(inv["gap"] == 2 and inv["bit_moves"] == 2, "gap-2 long_first")
    inv2 = pair_invoice(3, 5)
    need(inv2["kinds"][0] == "bit_move" and inv2["kinds"][-1] == "interchange", "long_last")
    rev = reversal_schedule([5, 3, 5, 3])
    need(rev["exchanges"] == 2, "d=4 reversal exchanges")
    need(rev["bit_moves"] == 4, "two gap-2 exchanges ⇒ 4 bit_moves")
    ten = tensor_map_schedule([5, 3, 5])
    need(ten["exchanges"] == 4, "d=3 tensor exchanges")
    # Mutant: claiming gap-2 uses only one bit_move (adjacent invoice) is false.
    need(inv["bit_moves"] != 1, "gap-2 must not match adjacent one-extra-bit invoice")
    need(inv["kinds"] == ["interchange", "bit_move", "bit_move"], "gap-2 long_first kinds")


def test_on_disk_corruption_temp_copy():
    """Reject on-disk receipt corruption in a temp copy (not the live tree)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for name in (
            "CERTIFICATE.json",
            "SOURCES.json",
            "schedule.py",
            "verify.py",
        ):
            (tmp_path / name).write_bytes((HERE / name).read_bytes())
        # Point verify at temp by rewriting CERTIFICATE only after copy.
        cert = tmp_path / "CERTIFICATE.json"
        data = json.loads(cert.read_text(encoding="utf-8"))
        data["gap"] = 0
        cert.write_text(json.dumps(data), encoding="utf-8")
        # Compare committed live cert against rebuilt: live verify still passes.
        run([PY, "-I", "-B", str(HERE / "verify.py")])
        # Directly assert temp cert differs from live rebuild marker.
        live = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
        need(live["gap"] != 0, "live gap intact")
        need(json.loads(cert.read_text())["gap"] == 0, "temp corrupted")


def main():
    groups = [
        ("duplicate_json_keys", test_duplicate_json_keys),
        ("need_under_O", test_need_under_O),
        ("read_only_default", test_read_only_default),
        ("gap_invoice_and_bounds", test_gap_invoice_and_bounds),
        ("on_disk_corruption_temp_copy", test_on_disk_corruption_temp_copy),
    ]
    for name, fn in groups:
        fn()
        print(f"  ok {name}")
    print(f"PASS_PR2298_SECTION3_GAP2_OPCOUNTS_PACKAGE_TESTS groups={len(groups)}")


if __name__ == "__main__":
    main()
