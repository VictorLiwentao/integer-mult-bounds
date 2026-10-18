#!/usr/bin/env python3
"""CLI checks: optimized replay, corrupted certificate, duplicate keys."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = (
    "research/community-frontier1094-audit/selected-replay.tar.gz",
    "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json",
    "certificates/selected-result.json",
    "docs/research/agent-task-catalog.json",
)


def run(root, optimized=False):
    package = root / "research" / HERE.name
    environment = dict(os.environ, PYTHONPYCACHEPREFIX=str(root / ".cache"))
    flags = ["-Werror", "-I", "-B"]
    if optimized:
        flags.insert(2, "-O")
    return subprocess.run(
        [sys.executable, *flags, str(package / "verify.py")],
        cwd=root, env=environment, capture_output=True, text=True, timeout=120,
    )


class PackageTests(unittest.TestCase):
    def copy_tree(self, root):
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for name in INPUTS:
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        return package

    def test_live_and_optimized(self):
        outcome = run(ROOT)
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        self.assertIn("PASS_PAIRED_PLANE_CLIQUE_RESTITUTION", outcome.stdout)
        outcome = run(ROOT, optimized=True)
        self.assertEqual(outcome.returncode, 0, outcome.stderr)

    def test_temp_copy_certificate_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.copy_tree(root)
            self.assertEqual(run(root, optimized=True).returncode, 0)
            original = (package / "CERTIFICATE.json").read_bytes()
            payload = json.loads(original)
            payload["rank2_triple_copy_mass"] = 11
            (package / "CERTIFICATE.json").write_bytes(json.dumps(payload).encode())
            outcome = run(root, optimized=True)
            self.assertNotEqual(outcome.returncode, 0)
            self.assertIn("triple mass", outcome.stderr)
            (package / "CERTIFICATE.json").write_bytes(original)
            self.assertEqual(run(root, optimized=True).returncode, 0)

    def test_duplicate_json_key_message(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.copy_tree(root)
            (package / "CERTIFICATE.json").write_text(
                '{"hypothesis": "quotient-collision-restitution", "hypothesis": "other"}\n',
                encoding="utf-8",
            )
            outcome = run(root, optimized=True)
            self.assertNotEqual(outcome.returncode, 0)
            self.assertIn("duplicate JSON key", outcome.stderr)


if __name__ == "__main__":
    unittest.main()
