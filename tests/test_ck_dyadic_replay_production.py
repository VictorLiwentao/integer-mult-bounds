"""Smoke registration for research/ck-dyadic-replay-production."""

from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/ck-dyadic-replay-production"


class TestCkDyadicReplayProduction(unittest.TestCase):
    def test_verify_passes(self):
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(PACKAGE / "verify.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS_CK_DYADIC_REPLAY_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
