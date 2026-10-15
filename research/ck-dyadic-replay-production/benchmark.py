#!/usr/bin/env python3
"""Paired wall-time samples for production CK dyadic kernels.

Descriptive only: timing is not a correctness gate.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/complex-ck-two-sided/independent.py"
BASELINE = PACKAGE / "baseline.py"
PREDECESSOR = ROOT / "research/complex-ck-two-sided"


def load_module(name: str, path: Path):
    source = path.read_text(encoding="utf-8")
    code = compile(source, str(path), "exec", optimize=0)
    module = importlib.util.module_from_spec(
        importlib.util.spec_from_file_location(name, path)
    )
    sys.modules[name] = module
    exec(code, module.__dict__)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def programs_for(independent_path: Path):
    experiment = load_module(f"ck917_experiment_{independent_path.name}", PREDECESSOR / "experiment.py")
    independent = load_module(f"ck917_independent_{independent_path.name}", independent_path)
    word, original, _ = experiment.load()
    panel, _recipe = experiment.construct(word)
    candidate = experiment.replace_programs(word, original, panel)
    programs = {
        label + "_" + orientation: list(experiment.primitives(events[orientation]))
        for label, events in (("baseline", original), ("candidate", candidate))
        for orientation in ("forward", "backward")
    }
    return independent, programs


def run_streams(independent, programs):
    started = time.perf_counter()
    results = {name: independent.replay(program) for name, program in programs.items()}
    elapsed = time.perf_counter() - started
    receipts = {name: digest(result) for name, result in results.items()}
    return elapsed, receipts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args(argv)

    base_mod, programs = programs_for(BASELINE)
    prod_mod, programs_prod = programs_for(PRODUCTION)
    if list(programs) != list(programs_prod):
        raise SystemExit("program labels drifted")
    for name in programs:
        if programs[name] != programs_prod[name]:
            raise SystemExit("primitive stream drifted: " + name)

    base_times = []
    prod_times = []
    reference = None
    for i in range(args.rounds):
        order = ("baseline", "production") if i % 2 == 0 else ("production", "baseline")
        sample = {}
        for engine in order:
            if engine == "baseline":
                dt, receipts = run_streams(base_mod, programs)
                base_times.append(dt)
            else:
                dt, receipts = run_streams(prod_mod, programs_prod)
                prod_times.append(dt)
            sample[engine] = receipts
        if sample["baseline"] != sample["production"]:
            raise SystemExit("PASS gate failed: receipts diverged during benchmark")
        if reference is None:
            reference = sample["baseline"]
        elif sample["baseline"] != reference:
            raise SystemExit("PASS gate failed: receipts drifted across rounds")

    base_med = statistics.median(base_times)
    prod_med = statistics.median(prod_times)
    ratio = base_med / prod_med if prod_med else float("inf")
    result = {
        "schema_version": 1,
        "package": "research/ck-dyadic-replay-production",
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "workload": "four complete integer-dyadic scalar streams (baseline/candidate × forward/backward)",
        "rounds": args.rounds,
        "baseline_seconds": base_times,
        "production_seconds": prod_times,
        "median_baseline_seconds": base_med,
        "median_production_seconds": prod_med,
        "median_speedup": ratio,
        "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
        "production_sha256": hashlib.sha256(PRODUCTION.read_bytes()).hexdigest(),
        "stream_receipt_sha256": reference,
        "total_primitives_per_run": sum(map(len, programs.values())),
        "python": sys.version,
        "platform": os.uname().sysname + " " + os.uname().release,
        "note": "Host-descriptive; not a correctness gate. Receipts identical each round.",
    }
    print(
        json.dumps(
            {
                "median_baseline_seconds": base_med,
                "median_production_seconds": prod_med,
                "median_speedup": ratio,
            },
            indent=2,
        ),
        flush=True,
    )
    print(
        "PASS_IDENTICAL_CK_DYADIC_REPLAY_PRODUCTION_RECEIPTS "
        f"streams=4 primitives={result['total_primitives_per_run']} "
        f"median_speedup={ratio:.3f}x",
        flush=True,
    )
    if args.write_result:
        out = PACKAGE / "RESULT.json"
        if out.exists():
            raise SystemExit(f"refusing to overwrite existing {out}")
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
