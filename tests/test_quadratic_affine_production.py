#!/usr/bin/env python3
"""Focused controls for the production packed quadratic-affine tooling package."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import subprocess
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "quadratic-affine-production"
sys.path.insert(0, str(ROOT / "scripts"))

from experiments import quadratic_affine as production  # noqa: E402

ORIGINAL_SHA256 = "8f9252bd092eb14779997c6767e090377e91f4d57e6526e9840ae0dd7dcc8f9c"
BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"


class QuadraticAffineProductionTests(unittest.TestCase):
    def test_baseline_matches_base_commit_bytes(self):
        original = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:scripts/experiments/quadratic_affine.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(sha256(original).hexdigest(), ORIGINAL_SHA256)
        self.assertNotEqual(
            sha256((ROOT / "scripts/experiments/quadratic_affine.py").read_bytes()).hexdigest(),
            ORIGINAL_SHA256,
        )

    def test_packed_matches_baseline_on_small_cases(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "quadratic_affine_baseline", PACKAGE / "baseline.py"
        )
        baseline = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(baseline)
        fixtures = json.loads(
            (ROOT / "scripts/experiments/quadratic_affine_witnesses.json").read_text(
                encoding="utf-8"
            )
        )
        for case in fixtures[:3]:
            kwargs = {
                k: case[k]
                for k in ("t", "complex_phases", "parity", "sample", "independent_rows")
            }
            self.assertEqual(baseline.rank_witness(**kwargs), production.rank_witness(**kwargs))

    def test_certificate_only_changes_quadratic_affine_pin(self):
        base = json.loads(
            subprocess.check_output(
                ["git", "show", f"{BASE_COMMIT}:certificates/quadratic-affine-vectors.json"],
                cwd=ROOT,
            )
        )
        live = json.loads(
            (ROOT / "certificates/quadratic-affine-vectors.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            live["source_sha256"]["scripts/experiments/quadratic_affine.py"],
            sha256((ROOT / "scripts/experiments/quadratic_affine.py").read_bytes()).hexdigest(),
        )
        restored = deepcopy(live)
        restored["source_sha256"]["scripts/experiments/quadratic_affine.py"] = ORIGINAL_SHA256
        self.assertEqual(restored, base)

    def test_package_verify_script(self):
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(PACKAGE / "verify.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("PASS_QUADRATIC_AFFINE_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
