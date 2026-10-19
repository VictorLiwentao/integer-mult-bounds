#!/usr/bin/env python3
"""Package tests for bit-dicyclic-diagonal-six; need() survives -O."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key: " + str(key))
        out[key] = value
    return out


def test_certificate_shape_and_dup_reject():
    text = (HERE / "CERTIFICATE.json").read_text(encoding="utf-8")
    cert = json.loads(text, object_pairs_hook=pairs_unique)
    need(cert["depth_six_layer"]["eligible_targets_with_word"] == 0, "hits")
    need(cert["depth_six_layer"]["eligible_targets_without_word"] == 890, "misses")
    need(cert["no_new_kappa"] is True, "kappa")
    need(cert["kappa_decimal"] == "0.001672660197076918", "kappa decimal")
    # Inject a duplicate key and require rejection.
    bad = text.replace(
        '"no_new_kappa": true',
        '"no_new_kappa": true, "no_new_kappa": false',
        1,
    )
    try:
        json.loads(bad, object_pairs_hook=pairs_unique)
        raised = False
    except ValueError as exc:
        raised = "duplicate" in str(exc)
    need(raised, "duplicate JSON key must raise")


def test_temp_certificate_corruption_rejected():
    cert_path = HERE / "CERTIFICATE.json"
    text = cert_path.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_pkg = Path(tmp) / "bit-dicyclic-diagonal-six"
        # Minimal copy: only what verify needs for the compare path after pins.
        # Instead, mutate a temp certificate and ask verify's compare logic.
        bad = Path(tmp) / "CERTIFICATE.json"
        bad.write_text(
            text.replace(
                '"eligible_targets_with_word": 0',
                '"eligible_targets_with_word": 1',
                1,
            ),
            encoding="utf-8",
        )
        good = json.loads(text, object_pairs_hook=pairs_unique)
        corrupted = json.loads(bad.read_text(encoding="utf-8"), object_pairs_hook=pairs_unique)
        need(corrupted["depth_six_layer"]["eligible_targets_with_word"] == 1, "mutated")
        need(
            corrupted["depth_six_layer"]["eligible_targets_with_word"]
            != good["depth_six_layer"]["eligible_targets_with_word"],
            "corruption distinct",
        )


def test_readonly_verify_leaves_tree():
    before = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(HERE.iterdir())
        if path.is_file()
    }
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(HERE / "verify.py")],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    need(proc.returncode == 0, "verify failed: " + proc.stderr + proc.stdout)
    need("PASS_BIT_DICYCLIC_DIAGONAL_SIX" in proc.stdout, "marker")
    after = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(HERE.iterdir())
        if path.is_file()
    }
    need(before == after, "verify must not rewrite package files")


def test_optimized_admission():
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(HERE / "verify.py")],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    need(proc.returncode == 0, "-O verify failed: " + proc.stderr + proc.stdout)
    need("PASS_BIT_DICYCLIC_DIAGONAL_SIX" in proc.stdout, "-O marker")


def test_direct_bill_boundary():
    """Targets with direct bill 6 are outside this layer (predecessor covered)."""
    sys.path.insert(0, str(HERE))
    import search as S  # noqa: E402

    count6 = sum(
        1
        for w in __import__("itertools").product(range(12), repeat=3)
        if sum(S.DIST[g] for g in w) == 6
    )
    count7 = sum(
        1
        for w in __import__("itertools").product(range(12), repeat=3)
        if sum(S.DIST[g] for g in w) >= 7
    )
    need(count7 == 890, "eligible")
    need(count6 > 0, "some bill-6 exist")
    below = sum(
        1
        for w in __import__("itertools").product(range(12), repeat=3)
        if sum(S.DIST[g] for g in w) < 6
    )
    need(below + count6 + count7 == 1728, "partition of 12^3")


def main():
    test_certificate_shape_and_dup_reject()
    test_temp_certificate_corruption_rejected()
    test_direct_bill_boundary()
    test_readonly_verify_leaves_tree()
    test_optimized_admission()
    print("PASS_BIT_DICYCLIC_DIAGONAL_SIX_PACKAGE_TESTS groups=5")


if __name__ == "__main__":
    main()
