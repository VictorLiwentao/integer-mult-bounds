#!/usr/bin/env python3
"""unittest entry for research/scalar-fused-dyadic-production."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScalarFusedDyadicProductionTests(unittest.TestCase):
    def test_verify(self):
        proc = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                str(ROOT / "research/scalar-fused-dyadic-production/verify.py"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("PASS_SCALAR_FUSED_DYADIC_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
