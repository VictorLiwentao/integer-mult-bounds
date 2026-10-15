#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for production cyclic zero-skip.

Timing is host-descriptive and is not a correctness gate.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASELINE = PACKAGE / "baseline.py"
PRODUCTION = ROOT / "research/prime-power-cyclic-inverse/verify.py"
RECEIPT_SHA256 = "2c4ab855129670053f4f39ee14269cc9b5bda015eab71d5a226dd0d395740ebd"


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise SystemExit(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def clean_env():
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_once(engine: str) -> dict:
    source = BASELINE if engine == "baseline" else PRODUCTION
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(source)],
        cwd=ROOT,
        env=clean_env(),
        capture_output=True,
    )
    elapsed = time.perf_counter() - start
    if proc.returncode != 0:
        raise SystemExit(f"{engine} failed\n{proc.stderr.decode()}\n{proc.stdout.decode()}")
    digest = sha256(proc.stdout).hexdigest()
    if digest != RECEIPT_SHA256:
        raise SystemExit(f"{engine} receipt digest {digest} != {RECEIPT_SHA256}")
    json.loads(proc.stdout.decode(), object_pairs_hook=unique_object)
    return {"engine": engine, "seconds": elapsed, "receipt_sha256": digest}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument(
        "--write-result",
        action="store_true",
        help="write RESULT.json (default prints only; use explicitly to refresh the artifact)",
    )
    parser.add_argument("--output", type=Path, default=PACKAGE / "RESULT.json")
    args = parser.parse_args(argv)
    if args.rounds < 1:
        raise SystemExit("--rounds must be >= 1")

    samples = []
    baseline_times = []
    production_times = []
    for round_index in range(args.rounds):
        order = ("baseline", "production") if round_index % 2 == 0 else ("production", "baseline")
        pair = []
        for engine in order:
            row = run_once(engine)
            pair.append(row)
            if engine == "baseline":
                baseline_times.append(row["seconds"])
            else:
                production_times.append(row["seconds"])
            print(
                f"round={round_index} engine={engine} seconds={row['seconds']:.6f} "
                f"receipt={row['receipt_sha256'][:16]}…",
                flush=True,
            )
        samples.append(pair)

    base_med = statistics.median(baseline_times)
    prod_med = statistics.median(production_times)
    result = {
        "status": "PASS_IDENTICAL_CYCLIC_ZERO_PRODUCTION_RECEIPTS",
        "ai_assistance": (
            "Substantial AI assistance for orientation, overlap search, profiling, "
            "production wiring, packaging, benchmarking and writing. Not independent "
            "human peer review."
        ),
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "predecessor": "research/cyclic-zero-elimination/",
        "python": sys.version,
        "platform": platform.platform(),
        "rounds": args.rounds,
        "receipt_sha256": RECEIPT_SHA256,
        "baseline_median_seconds": base_med,
        "production_median_seconds": prod_med,
        "median_ratio": base_med / prod_med if prod_med else None,
        "samples": samples,
        "implementation_sha256": {
            "baseline.py": sha256(BASELINE.read_bytes()).hexdigest(),
            "production": sha256(PRODUCTION.read_bytes()).hexdigest(),
            "benchmark.py": sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "no_new_kappa": True,
    }
    print(result["status"])
    print(
        f"median {base_med:.6f} -> {prod_med:.6f} "
        f"({result['median_ratio']:.3f}x)"
    )
    if args.write_result:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
