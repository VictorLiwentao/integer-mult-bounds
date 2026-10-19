#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Package controls for the four-role A5 conjugate 5-cycle census."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from model import (  # noqa: E402
    CALLS,
    E,
    EXPECTED_CALLS,
    EXPECTED_IDEM,
    ROLES,
    X,
    Y,
    identity_state,
    make_direct_word,
    need,
    order_of,
    target_state,
    word_state,
)


def group_relations() -> None:
    need(order_of(X) == 2, "x order")
    need(order_of(Y) == 3, "y order")
    need(len(CALLS) == EXPECTED_CALLS, "call count")
    need(EXPECTED_IDEM == 120, "idempotent count")


def direct_and_omissions() -> None:
    direct = make_direct_word()
    target = target_state()
    need(word_state(direct) == target, "direct word")
    for pos in range(len(direct)):
        reduced = direct[:pos] + direct[pos + 1 :]
        need(word_state(reduced) != target, f"omission {pos}")
    # Spectator diagonals stay identity.
    need(target[2 * ROLES + 2] == (1 << E), "spectator role 2")
    need(target[3 * ROLES + 3] == (1 << E), "spectator role 3")


def dirty_toggle() -> None:
    """Flipping a spectator target cell away from [e] rejects the direct word."""
    direct = make_direct_word()
    bad = list(target_state())
    bad[2 * ROLES + 2] = 1 << X
    need(word_state(direct) != tuple(bad), "dirty toggle must reject")


def duplicate_json_key_reject() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad.json"
        path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")

        def _hook(pairs):
            out = {}
            for key, value in pairs:
                if key in out:
                    raise ValueError("duplicate")
                out[key] = value
            return out

        try:
            json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_hook)
        except ValueError:
            return
        raise SystemExit("FAIL_A5_FOUR_ROLE_CONJUGATE_PACKAGE_TESTS: dup key accepted")


def certificate_corruption_reject() -> None:
    cert_path = HERE / "CERTIFICATE.json"
    need(cert_path.is_file(), "certificate present")
    original = cert_path.read_text(encoding="utf-8")
    try:
        bad = json.loads(original)
        bad["result_minimum"] = int(bad["result_minimum"]) + 1
        cert_path.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n")
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(HERE / "verify.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        need(proc.returncode != 0, "corrupted certificate must fail verify")
        need("FAIL_" in proc.stdout + proc.stderr, "corruption failure marker")
    finally:
        cert_path.write_text(original, encoding="utf-8")


def identity_not_target() -> None:
    need(identity_state() != target_state(), "identity is not the target")


def main() -> int:
    group_relations()
    direct_and_omissions()
    dirty_toggle()
    duplicate_json_key_reject()
    identity_not_target()
    certificate_corruption_reject()
    print(
        "PASS_A5_FOUR_ROLE_CONJUGATE_PACKAGE_TESTS groups=6",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
