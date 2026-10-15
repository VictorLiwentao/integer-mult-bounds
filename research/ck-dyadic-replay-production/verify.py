#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production CK dyadic kernels.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/complex-ck-two-sided/independent.py"
BASELINE = PACKAGE / "baseline.py"
FAST_ROWS = ROOT / "research/ck-dyadic-replay-fast/fast_rows.py"
PREDECESSOR = ROOT / "research/complex-ck-two-sided"

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "26d47eb64dc8ba31444f285daa4ec53823da3fb4"
ORIGINAL_SHA256 = "87d690c534409047322c1dc625586adf4c192a9746941eae06c3da6e0add3aa2"
OPTIMIZED_SHA256 = "53f4a92ee8de3fd5ff3dc1cccddfa8b72a80b2ae8d81a786663ebb30f60a0cae"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_module(name: str, path: Path):
    """Load with assertions enforced even when the parent process used -O."""
    source = path.read_text(encoding="utf-8")
    code = compile(source, str(path), "exec", optimize=0)
    module = importlib.util.module_from_spec(
        importlib.util.spec_from_file_location(name, path)
    )
    sys.modules[name] = module
    exec(code, module.__dict__)
    return module


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/complex-ck-two-sided/independent.py"],
        cwd=ROOT,
    )
    require(hashlib.sha256(original).hexdigest() == ORIGINAL_SHA256, "base independent.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/complex-ck-two-sided/independent.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base independent.py blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit independent.py")
    require(
        digest_file(PRODUCTION) == OPTIMIZED_SHA256,
        "production independent.py does not match the claimed optimized digest",
    )
    require(PRODUCTION.read_bytes() != original, "production must differ from the pairwise baseline")

    fast = load_module("ck_fast_rows_pin", FAST_ROWS)
    prod = load_module("ck_prod_pin", PRODUCTION)
    # Spot-check that production callables match the opt-in kernels on a few rows.
    cases = [
        ({}, 0),
        ({0: 2, 1: 4}, 3),
        ({0: 1, 1: -2}, 2),
        ({3: -8, 5: 24}, 5),
    ]
    for terms, exp in cases:
        require(
            prod._normal_row(dict(terms), exp) == fast.normal_row(dict(terms), exp),
            "production normal_row diverges from opt-in kernel",
        )
    left = ({0: 1, 2: -3}, 2)
    right = ({0: 1, 1: 5}, 4)
    for sign in (1, -1):
        require(
            prod._sum_rows(left, right, sign) == fast.sum_rows(left, right, sign),
            "production sum_rows diverges from opt-in kernel",
        )


def predecessor_programs(independent_path: Path):
    experiment = load_module("ck917_experiment_prod", PREDECESSOR / "experiment.py")
    independent = load_module("ck917_independent_prod", independent_path)
    sys.modules["experiment"] = experiment
    sys.modules["independent"] = independent
    word, original, _ = experiment.load()
    panel, recipe = experiment.construct(word)
    require(
        canonical(recipe) == canonical(experiment.read(PREDECESSOR / "RECIPE.json")),
        "recipe reconstruction changed",
    )
    candidate = experiment.replace_programs(word, original, panel)
    programs = {
        label + "_" + orientation: list(experiment.primitives(events[orientation]))
        for label, events in (("baseline", original), ("candidate", candidate))
        for orientation in ("forward", "backward")
    }
    return experiment, independent, programs


def check_identical_streams() -> dict:
    _, baseline_mod, programs = predecessor_programs(BASELINE)
    _, production_mod, programs_prod = predecessor_programs(PRODUCTION)
    require(list(programs) == list(programs_prod), "program labels drifted")
    for name, program in programs.items():
        require(program == programs_prod[name], "primitive stream drifted: " + name)
        base = baseline_mod.replay(program)
        prod = production_mod.replay(program)
        require(canonical(base) == canonical(prod), "stream receipt disagreement: " + name)
        orientation = name.rsplit("_", 1)[1]
        baseline_mod.check_endpoint(base, orientation)
        production_mod.check_endpoint(prod, orientation)
    return {"streams": len(programs), "primitives": sum(map(len, programs.values()))}


def check_full_predecessor_receipt() -> dict:
    experiment = load_module("ck917_experiment_full", PREDECESSOR / "experiment.py")
    independent = load_module("ck917_independent_full", PRODUCTION)
    sys.modules["experiment"] = experiment
    sys.modules["independent"] = independent
    verifier = load_module("ck917_verifier_full", PREDECESSOR / "verify.py")
    require(verifier.e is experiment and verifier.independent is independent, "unexpected imports")
    output = io.StringIO()
    # Capture stdout from the historical verifier.
    saved_stdout = sys.stdout
    sys.stdout = output
    try:
        full = verifier.verify()
    finally:
        sys.stdout = saved_stdout
    expected = json.loads((PREDECESSOR / "EXPECTED.json").read_text(encoding="utf-8"))
    require(canonical(full) == canonical(expected), "full predecessor receipt changed")
    return {
        "full_receipt_sha256": digest(full),
        "controls": len(full["controls"]["rejected"]),
        "native_controls": len(full["native"]["negative_controls_rejected"]),
        "stdout_lines": len(output.getvalue().splitlines()),
    }


def check_temp_corruption_rejection() -> dict:
    """On-disk foil that drops right-hand ADD terms must diverge or fail."""
    _, baseline_mod, programs = predecessor_programs(BASELINE)
    honest = {name: baseline_mod.replay(program) for name, program in programs.items()}

    text = PRODUCTION.read_text(encoding="utf-8")
    needle = "for column, value in right_terms.items():"
    require(needle in text, "sum_rows right-term loop missing for corruption control")
    # Replace the right-hand iterator with an empty one so ADD ignores the right row.
    foil_text = text.replace(needle, "for column, value in dict().items():", 1)
    require(foil_text != text, "mutant must differ on disk")

    with tempfile.TemporaryDirectory(prefix="ck-dyadic-prod-foil-") as tmp:
        mutant = Path(tmp) / "independent.py"
        mutant.write_text(foil_text, encoding="utf-8")
        try:
            _, foil_mod, programs_foil = predecessor_programs(mutant)
            bad = {name: foil_mod.replay(program) for name, program in programs_foil.items()}
        except Exception as exc:
            return {"rejected": True, "mode": "runtime_failure", "detail": str(exc)[:240]}
        require(canonical(bad) != canonical(honest), "kernel foil must change a stream receipt")
        return {"rejected": True, "mode": "receipt_divergence"}


def check_assertions_site() -> int:
    """Production rewrite should not remove assert statements from the module body."""
    tree = ast.parse(PRODUCTION.read_text(encoding="utf-8"))
    asserts = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    # independent.py uses ReplayError via _require rather than assert; count _require calls.
    requires = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_require"
    ]
    require(len(requires) >= 1, "production must retain _require gates")
    return len(requires)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    check_baseline_bytes()
    requires = check_assertions_site()
    streams = check_identical_streams()
    full = check_full_predecessor_receipt()
    corruption = check_temp_corruption_rejection()
    require(corruption["rejected"], "corruption control must reject")
    print(
        "PASS_CK_DYADIC_REPLAY_PRODUCTION "
        f"requires={requires} "
        f"streams={streams['streams']} "
        f"primitives={streams['primitives']} "
        f"controls={full['controls']}+{full['native_controls']} "
        f"corruption={corruption['mode']} "
        "certs=1 no_new_kappa",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
