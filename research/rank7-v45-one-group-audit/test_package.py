#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Temp-copy corruption, duplicate-key, and read-only replay controls."""

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


@contextmanager
def isolated():
    with tempfile.TemporaryDirectory(prefix="v45-one-group-") as temporary:
        package = Path(temporary) / "relocated"
        package.mkdir()
        for name in ("verify.py", "independent.py", "CERTIFICATE.json"):
            shutil.copyfile(HERE / name, package / name)
        try:
            yield package
        finally:
            package.chmod(0o755)
            for path in package.iterdir():
                path.chmod(0o644)


def replay(package, script, optimized=False):
    flags = ["-I", "-B"] + (["-O"] if optimized else [])
    return subprocess.run(
        [sys.executable, *flags, str(package / script)],
        cwd=REPO,
        text=True,
        capture_output=True,
        timeout=180,
    )


def tree_hashes(package):
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in package.iterdir()}


class PackageTests(unittest.TestCase):
    def test_duplicate_json_key_is_rejected(self):
        with isolated() as package:
            text = (package / "CERTIFICATE.json").read_text(encoding="utf-8")
            forged = text.replace('"group": "V45"', '"group": "V45", "group": "V45"', 1)
            self.assertNotEqual(forged, text)
            (package / "CERTIFICATE.json").write_text(forged)
            result = replay(package, "verify.py", optimized=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("PASS_V45_", result.stdout)
            self.assertIn("duplicate key group", result.stderr)

    def test_temp_copy_certificate_corruption_is_rejected(self):
        with isolated() as package:
            receipt = json.loads((package / "CERTIFICATE.json").read_text(encoding="utf-8"))
            receipt["surrogate_joint_margin"] = 0
            (package / "CERTIFICATE.json").write_text(json.dumps(receipt))
            result = replay(package, "independent.py", optimized=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("PASS_V45_", result.stdout)
            self.assertIn("certificate differs from exact replay", result.stderr)

    def test_missing_certificate_is_rejected(self):
        with isolated() as package:
            (package / "CERTIFICATE.json").unlink()
            result = replay(package, "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FileNotFoundError", result.stderr)

    def test_sources_do_not_import_each_other(self):
        import ast

        for name in ("verify.py", "independent.py"):
            tree = ast.parse((HERE / name).read_text(encoding="utf-8"))
            modules = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules.extend(alias.name for alias in node.names)
                if isinstance(node, ast.ImportFrom) and node.module:
                    modules.append(node.module)
            self.assertFalse(any(item.startswith(("verify", "independent", "rank7")) for item in modules))

    def test_optimized_read_only_relocated_replay(self):
        with isolated() as package:
            before = tree_hashes(package)
            for path in package.iterdir():
                path.chmod(0o444)
            package.chmod(0o555)
            for script, marker in (
                ("verify.py", "PASS_V45_ONE_GROUP_SUPPLIER_OBSTRUCTION"),
                ("independent.py", "PASS_V45_ONE_GROUP_SET_SPAN"),
            ):
                result = replay(package, script, optimized=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(marker, result.stdout)
            self.assertEqual(before, tree_hashes(package))


if __name__ == "__main__":
    unittest.main(verbosity=2)
