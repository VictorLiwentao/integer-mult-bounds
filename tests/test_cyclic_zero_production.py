#!/usr/bin/env python3
"""Smoke tests for research/cyclic-zero-production."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/cyclic-zero-production"
PRODUCTION = ROOT / "research/prime-power-cyclic-inverse/verify.py"
BASELINE = PACKAGE / "baseline.py"
OPTIMIZED_SHA256 = "0554c62ce62dc30df2a889f4408f0491076fc6a3aba598d955408cfad946f5c0"
ORIGINAL_SHA256 = "40e5e18cbd98d39ba6d0bb036778ccacc077dff009099a54b9c8f441af5d6a56"


class CyclicZeroProductionTests(unittest.TestCase):
    def test_production_differs_from_baseline_and_matches_digest(self):
        self.assertEqual(sha256(BASELINE.read_bytes()).hexdigest(), ORIGINAL_SHA256)
        self.assertEqual(sha256(PRODUCTION.read_bytes()).hexdigest(), OPTIMIZED_SHA256)
        self.assertNotEqual(PRODUCTION.read_bytes(), BASELINE.read_bytes())
        self.assertIn("if value == k.zero:", PRODUCTION.read_text(encoding="utf-8"))

    def test_verify_script(self):
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(PACKAGE / "verify.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS_CYCLIC_ZERO_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
