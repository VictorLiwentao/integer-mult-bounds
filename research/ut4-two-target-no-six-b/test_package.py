#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Relocation, -O/need, certificate corruption and independent-import controls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(root):
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }


def main():
    checks = []
    with tempfile.TemporaryDirectory(prefix="nb6-pkg-") as directory:
        target = Path(directory) / "isolated-package"
        shutil.copytree(
            HERE,
            target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.txt"),
        )

        # Keep cwd at the repository root so live SOURCES inputs resolve.
        repo = HERE.parents[1]

        def run(script="verify.py", expected_error=None):
            result = subprocess.run(
                [sys.executable, "-I", "-O", "-B", str(target / script)],
                cwd=str(repo),
                text=True,
                capture_output=True,
                timeout=300,
            )
            if expected_error is None:
                need(
                    result.returncode == 0
                    and "PASS_UT4_TWO_TARGET_NO_NB6" in result.stdout,
                    "isolated replay failed: " + result.stderr + result.stdout,
                )
            else:
                need(
                    result.returncode != 0
                    and expected_error in (result.stderr + result.stdout),
                    "corruption escaped or wrong reason: " + result.stderr,
                )

        before = inventory(target)
        for path in target.rglob("*"):
            if path.is_file():
                path.chmod(0o444)
        run()
        need(inventory(target) == before, "normal replay mutated the isolated package")
        checks.append("isolated-optimized-read-only-replay")
        for path in target.rglob("*"):
            if path.is_file():
                path.chmod(0o644)

        result = subprocess.run(
            [sys.executable, "-I", "-O", "-B", str(target / "independent.py")],
            cwd=str(repo),
            text=True,
            capture_output=True,
            timeout=300,
        )
        need(
            result.returncode == 0
            and "PASS_UT4_TWO_TARGET_NO_NB6_INDEPENDENT" in result.stdout,
            "independent failed: " + result.stderr,
        )
        import ast

        tree = ast.parse((target / "independent.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                need(all(a.name.split(".")[0] != "verify" for a in node.names),
                     "independent imports verify")
            if isinstance(node, ast.ImportFrom) and node.module:
                need(node.module.split(".")[0] != "verify", "independent imports verify")
        checks.append("independent-no-verify-import")

        def mutate(name, filename, edit, message):
            path = target / filename
            saved = path.read_bytes()
            path.write_bytes(edit(saved))
            try:
                run(expected_error=message)
                checks.append(name)
            finally:
                path.write_bytes(saved)

        def json_edit(data, edit):
            obj = json.loads(data)
            edit(obj)
            return (json.dumps(obj, sort_keys=True) + "\n").encode()

        mutate(
            "corrupted-certificate-pairs",
            "CERTIFICATE.json",
            lambda data: json_edit(data, lambda x: x.update(key_pairs_abc_cba_I=1)),
            "certificate mismatch",
        )
        mutate(
            "duplicate-json-key",
            "CERTIFICATE.json",
            lambda data: b'{"status":"first","status":"second"}\n',
            "duplicate JSON key",
        )
        mutate(
            "sources-base-drift",
            "SOURCES.json",
            lambda data: json_edit(data, lambda x: x.update(base_commit="0" * 40)),
            "base pin",
        )

        need(inventory(target) == before, "corruption controls failed to restore source bytes")
        checks.append("need-survives-python-O")

    print("PASS_UT4_TWO_TARGET_NO_NB6_PACKAGE_CONTROLS", "checks=" + str(len(checks)))
    print(json.dumps(checks))


if __name__ == "__main__":
    main()
