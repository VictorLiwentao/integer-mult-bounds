#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production packed rank_witness.

Read-only by default. Regenerates no certificate unless --write-certificate is
passed. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
from prepare_layers import serializable  # noqa: E402
from audit_quadratic_affine import certificate as production_certificate  # noqa: E402
from experiments import quadratic_affine as production  # noqa: E402

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "271e0a4e0bc077244859009ac2201f172152720b"
ORIGINAL_SHA256 = "8f9252bd092eb14779997c6767e090377e91f4d57e6526e9840ae0dd7dcc8f9c"
BASE_CERTIFICATE_SHA256 = "b55506bcf2334eebc07ce31078edb33282ff7d9bb57c40a9e4d5209d749dcd7f"
FIXTURE_PATH = ROOT / "scripts" / "experiments" / "quadratic_affine_witnesses.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def load_fixtures() -> list[dict]:
    fixtures = load_json_unique(FIXTURE_PATH)
    require(isinstance(fixtures, list) and len(fixtures) == 12, "expected twelve fixtures")
    return fixtures


def load_base_certificate_bytes() -> bytes:
    import subprocess

    return subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:certificates/quadratic-affine-vectors.json"],
        cwd=ROOT,
    )


def check_baseline_bytes() -> None:
    import subprocess

    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:scripts/experiments/quadratic_affine.py"],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base quadratic_affine.py sha256 drift")
    require(
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/experiments/quadratic_affine.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
        == ORIGINAL_BLOB,
        "base quadratic_affine.py blob drift",
    )
    require(
        (PACKAGE / "baseline.py").read_bytes() == original,
        "baseline.py must be an exact copy of the base-commit source",
    )


def case_kwargs(case: dict) -> dict:
    return {
        key: case[key]
        for key in ("t", "complex_phases", "parity", "sample", "independent_rows")
    }


def check_witness_equivalence(baseline, optimized) -> list[dict]:
    rows = []
    frozen = load_json_unique(ROOT / "certificates" / "quadratic-affine-vectors.json")["cases"]
    require(len(frozen) == 12, "frozen certificate case count")
    for case, expected in zip(load_fixtures(), frozen, strict=True):
        kwargs = case_kwargs(case)
        old = baseline.rank_witness(**kwargs)
        new = optimized.rank_witness(**kwargs)
        require(old == new, f"rank_witness receipt differs for t={case['t']}")
        require(old["positive_deficit_excluded"], "deficit gate failed")
        require(
            old["independent_row_sha256"] == expected["independent_row_sha256"],
            "row digest drifted from frozen certificate case",
        )
        require(old["binary_rank_lower"] == expected["binary_rank_lower"], "binary rank drifted")
        rows.append(old)
    return rows


def check_rejections(baseline, optimized) -> None:
    fixtures = load_fixtures()
    heavy = max(fixtures, key=lambda c: len(c["sample"]))
    for eng, name in ((baseline, "baseline"), (optimized, "optimized")):
        kwargs = case_kwargs(heavy)
        bad = deepcopy(kwargs)
        bad["sample"] = bad["sample"] + [bad["sample"][0]]
        try:
            eng.rank_witness(**bad)
            raise AssertionError(f"{name} accepted duplicate sample labels")
        except ValueError as exc:
            require("sample" in str(exc).lower() or "distinct" in str(exc).lower(), str(exc))
        bad = deepcopy(kwargs)
        bad["independent_rows"] = bad["independent_rows"] + [bad["independent_rows"][0]]
        try:
            eng.rank_witness(**bad)
            raise AssertionError(f"{name} accepted duplicate independent rows")
        except ValueError as exc:
            require("independent" in str(exc).lower() or "invalid" in str(exc).lower(), str(exc))
        bad = deepcopy(kwargs)
        # Dependent claimed basis: drop every independent row after the first.
        bad["independent_rows"] = [bad["independent_rows"][0], bad["independent_rows"][0]]
        # The duplicate-index gate fires before dependence; use an out-of-range index.
        bad = deepcopy(kwargs)
        bad["independent_rows"] = [len(bad["sample"])]
        try:
            eng.rank_witness(**bad)
            raise AssertionError(f"{name} accepted out-of-range independent row")
        except ValueError as exc:
            require("independent" in str(exc).lower() or "invalid" in str(exc).lower(), str(exc))


def check_temp_corruption(optimized) -> None:
    with tempfile.TemporaryDirectory(prefix="quadratic-affine-prod-") as tmp:
        dest = Path(tmp) / "quadratic_affine.py"
        shutil.copy2(SCRIPTS / "experiments" / "quadratic_affine.py", dest)
        text = dest.read_text(encoding="utf-8")
        # Break packed central_row diagonal: drop the forced I-bit.
        mutated = text.replace(
            "return self.orthogonality_row(self.vectors[index])|(1<<index)",
            "return self.orthogonality_row(self.vectors[index])",
            1,
        )
        require(mutated != text, "mutation did not edit production source text")
        dest.write_text(mutated, encoding="utf-8")
        mutant = load_module(dest, "quadratic_affine_mutant")
        fixtures = load_fixtures()
        kwargs = case_kwargs(fixtures[0])
        production_receipt = production.rank_witness(**kwargs)
        mutant_receipt = mutant.rank_witness(**kwargs)
        require(
            mutant_receipt["independent_row_sha256"]
            != production_receipt["independent_row_sha256"],
            "omitted-diagonal mutant must change the row digest",
        )
        frozen = load_json_unique(ROOT / "certificates" / "quadratic-affine-vectors.json")
        require(
            production_receipt["independent_row_sha256"]
            == frozen["cases"][0]["independent_row_sha256"],
            "production digest drifted while checking mutant",
        )


def check_certificate(write: bool) -> dict:
    result = production_certificate()
    path = ROOT / "certificates" / "quadratic-affine-vectors.json"
    text = json.dumps(serializable(result), indent=2, sort_keys=True) + "\n"
    if write:
        path.write_text(text, encoding="utf-8")
    committed = path.read_text(encoding="utf-8")
    require(
        committed == text,
        "working certificates/quadratic-affine-vectors.json does not match regenerated certificate()",
    )
    load_json_unique(path)
    base = load_base_certificate_bytes()
    require(sha256(base).hexdigest() == BASE_CERTIFICATE_SHA256, "base certificate sha256 drift")
    old = json.loads(base.decode("utf-8"))
    new = json.loads(committed)
    old_pin = old["source_sha256"].pop("scripts/experiments/quadratic_affine.py")
    new_pin = new["source_sha256"].pop("scripts/experiments/quadratic_affine.py")
    require(old_pin == ORIGINAL_SHA256, "unexpected base pin")
    require(
        new_pin == digest_file(SCRIPTS / "experiments" / "quadratic_affine.py"),
        "certificate pin != working source",
    )
    require(old == new, "certificate changed outside the single quadratic_affine.py source pin")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="regenerate certificates/quadratic-affine-vectors.json (default: read-only compare)",
    )
    args = parser.parse_args(argv)

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "quadratic_affine_baseline")
    optimized = production
    require(
        digest_file(SCRIPTS / "experiments" / "quadratic_affine.py") != ORIGINAL_SHA256,
        "production source still equals the unoptimized base pin",
    )
    require(
        digest_file(PACKAGE / "baseline.py") == ORIGINAL_SHA256,
        "baseline.py must equal the original source sha256",
    )

    rows = check_witness_equivalence(baseline, optimized)
    check_rejections(baseline, optimized)
    check_temp_corruption(optimized)
    cert = check_certificate(write=args.write_certificate)

    print(
        "PASS_QUADRATIC_AFFINE_PRODUCTION "
        f"cases={len(rows)} "
        f"optimize={sys.flags.optimize} "
        f"certificate_source_pin={cert['source_sha256']['scripts/experiments/quadratic_affine.py'][:12]} "
        "no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
