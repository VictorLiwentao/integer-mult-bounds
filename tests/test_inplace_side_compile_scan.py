"""Focused controls for the faster inplace-side compile_side tooling package."""
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from experiments import inplace_side as optimized


ORIGINAL_SHA256 = "4397b84f3ac52554bf14303171410a2799af0bf8dae11ec64594bb5c011e93a2"
IDENTITY_H = (6, 10, 14, 18, 22, 26, 30)


def load_baseline():
    path = ROOT / "research/inplace-side-compile-scan/baseline.py"
    spec = importlib.util.spec_from_file_location("inplace_side_compile_baseline", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InplaceSideCompileScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_bytes_match_original_pin(self):
        data = (ROOT / "research/inplace-side-compile-scan/baseline.py").read_bytes()
        self.assertEqual(sha256(data).hexdigest(), ORIGINAL_SHA256)
        self.assertNotEqual(
            sha256((ROOT / "scripts/experiments/inplace_side.py").read_bytes()).hexdigest(),
            ORIGINAL_SHA256,
        )

    def test_compile_side_matches_baseline_fieldwise(self):
        for h in IDENTITY_H:
            self.assertEqual(
                optimized.compile_side(h),
                self.baseline.compile_side(h),
                msg=f"h={h}",
            )

    def test_greatest_unused_mutant_differs(self):
        path = ROOT / "research/inplace-side-compile-scan/verify.py"
        spec = importlib.util.spec_from_file_location("inplace_side_compile_scan_verify", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        mutant = module.greatest_unused_mutant_compile_side
        for h in (6, 10, 14):
            self.assertNotEqual(mutant(h), self.baseline.compile_side(h), msg=f"h={h}")

    def test_certificate_only_source_pin_changes(self):
        import subprocess
        from audit_inplace_side import certificate
        from prepare_layers import serializable

        base = json.loads(
            subprocess.check_output(
                ["git", "show", "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2:certificates/inplace-side.json"],
                cwd=ROOT,
            )
        )
        regenerated = json.loads(json.dumps(serializable(certificate())))
        committed = json.loads((ROOT / "certificates/inplace-side.json").read_text(encoding="utf-8"))
        self.assertEqual(committed, regenerated)
        old_pin = base["source_sha256"].pop("scripts/experiments/inplace_side.py")
        new_pin = regenerated["source_sha256"].pop("scripts/experiments/inplace_side.py")
        self.assertEqual(old_pin, ORIGINAL_SHA256)
        self.assertEqual(
            new_pin,
            sha256((ROOT / "scripts/experiments/inplace_side.py").read_bytes()).hexdigest(),
        )
        self.assertEqual(base, regenerated)


if __name__ == "__main__":
    unittest.main()
