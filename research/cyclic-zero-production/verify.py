#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production cyclic zero-row skip.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/prime-power-cyclic-inverse/verify.py"
BASELINE = PACKAGE / "baseline.py"
EXPECTED = ROOT / "research/prime-power-cyclic-inverse/EXPECTED.json"

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "20a069f42ac2e7102d8b1ddac4f568b83e077074"
ORIGINAL_SHA256 = "40e5e18cbd98d39ba6d0bb036778ccacc077dff009099a54b9c8f441af5d6a56"
OPTIMIZED_SHA256 = "0554c62ce62dc30df2a889f4408f0491076fc6a3aba598d955408cfad946f5c0"
RECEIPT_SHA256 = "2c4ab855129670053f4f39ee14269cc9b5bda015eab71d5a226dd0d395740ebd"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json_unique(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def run_verifier(script: Path) -> tuple[bytes, dict]:
    """Run one verifier under assertion-enabled -I -B (never inherit -O)."""
    env = {k: v for k, v in __import__("os").environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(script)],
        cwd=ROOT,
        env=env,
        capture_output=True,
    )
    require(proc.returncode == 0, f"{script.name} failed\n{proc.stderr.decode()}\n{proc.stdout.decode()}")
    text = proc.stdout
    require(sha256(text).hexdigest() == RECEIPT_SHA256, f"{script.name} stdout digest drift")
    require(text == EXPECTED.read_bytes(), f"{script.name} stdout != EXPECTED.json")
    receipt = json.loads(text.decode(), object_pairs_hook=unique_object)
    return text, receipt


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/prime-power-cyclic-inverse/verify.py"],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base verify.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/prime-power-cyclic-inverse/verify.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base verify.py blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit verify.py")
    require(
        digest_file(PRODUCTION) == OPTIMIZED_SHA256,
        "production verify.py does not match the claimed optimized digest",
    )
    require(PRODUCTION.read_bytes() != original, "production must differ from the pairwise baseline")
    text = PRODUCTION.read_text(encoding="utf-8")
    require("if value == k.zero:\n                continue" in text, "production missing zero-row skip")
    require(text.count("if value == k.zero:") == 1, "expected exactly one zero-row guard")


def check_equivalence() -> dict:
    expected = load_json_unique(EXPECTED)
    base_text, base_receipt = run_verifier(BASELINE)
    prod_text, prod_receipt = run_verifier(PRODUCTION)
    require(base_text == prod_text, "baseline/production stdout bytes diverge")
    require(base_receipt == prod_receipt == expected, "receipt field mismatch versus EXPECTED.json")
    return {
        "cases": expected.get("cases") if isinstance(expected.get("cases"), list) else None,
        "stdout_sha256": RECEIPT_SHA256,
        "keys": sorted(prod_receipt),
    }


def check_temp_corruption_rejection() -> dict:
    """On-disk mutant in a temp copy must fail the inherited identity checks."""
    honest, _ = run_verifier(PRODUCTION)
    with tempfile.TemporaryDirectory(prefix="cyclic-zero-prod-") as tmp:
        mutant = Path(tmp) / "verify.py"
        text = PRODUCTION.read_text(encoding="utf-8")
        needle = "if value == k.zero:"
        require(needle in text, "zero-row guard missing for corruption control")
        foil = text.replace(needle, "if value != k.zero:", 1)
        mutant.write_text(foil, encoding="utf-8")
        require(mutant.read_bytes() != PRODUCTION.read_bytes(), "mutant must differ on disk")
        env = {k: v for k, v in __import__("os").environ.items() if k != "PYTHONOPTIMIZE"}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(mutant)],
            cwd=ROOT,
            env=env,
            capture_output=True,
        )
        if proc.returncode != 0:
            return {
                "rejected": True,
                "mode": "subprocess_failure",
                "detail": (proc.stderr or proc.stdout).decode()[:240],
            }
        require(proc.stdout != honest, "inverted zero-skip guard must change the receipt")
        return {
            "rejected": True,
            "mode": "receipt_divergence",
            "honest_sha256": sha256(honest).hexdigest(),
            "mutant_sha256": sha256(proc.stdout).hexdigest(),
        }


def check_opt_in_adapter() -> None:
    """Historical opt-in package still replays against its vendored pairwise baseline."""
    env = {k: v for k, v in __import__("os").environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(ROOT / "research/cyclic-zero-elimination/verify.py"),
            "--output",
            str(Path(tempfile.mkdtemp(prefix="cyclic-zero-optin-")) / "out.json"),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    require(proc.returncode == 0, f"opt-in adapter failed\n{proc.stderr}\n{proc.stdout}")
    require("PASS_CYCLIC_ZERO_ELIMINATION" in proc.stdout, "opt-in adapter marker")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-result",
        action="store_true",
        help="unused placeholder; default verify is read-only and never writes certificates",
    )
    args = parser.parse_args(argv)
    require(not args.write_result, "default verify is read-only; do not pass --write-result")

    check_baseline_bytes()
    receipt = check_equivalence()
    corruption = check_temp_corruption_rejection()
    check_opt_in_adapter()

    print(
        "PASS_CYCLIC_ZERO_PRODUCTION "
        f"keys={len(receipt['keys'])} "
        f"corruption={corruption['mode']} "
        "certs=1 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
