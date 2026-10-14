#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for compile_side.

Timing is descriptive evidence for RESULT.json. Equivalence is enforced by
verify.py; this script fails only on unequal compile receipts or subprocess errors.
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

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent

# Meaningful sizes where sorted(unused) and column shifts are measurable.
# Certificate controls only use h=6,10; identity is checked through h=30 in verify.py.
BENCH_H = (22, 26, 30)

WORKER = r"""
import json, sys, time
from pathlib import Path
root = Path(sys.argv[1])
engine = sys.argv[2]
hs = [int(x) for x in sys.argv[3].split(",")]
sys.path.insert(0, str(root / "scripts"))
if engine == "baseline":
    import importlib.util
    path = root / "research/inplace-side-compile-scan/baseline.py"
    spec = importlib.util.spec_from_file_location("inplace_side_compile_baseline", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
else:
    from experiments import inplace_side as mod
t0 = time.perf_counter()
receipts = [mod.compile_side(h) for h in hs]
elapsed = time.perf_counter() - t0
# Drop huge row/point payloads from the compared receipt; keep proof-relevant fields.
slim = []
for r in receipts:
    slim.append({
        "h": r["h"],
        "roles": r["roles"],
        "pivots": r["pivots"],
        "initial": r["initial"],
        "gates": r["gates"],
    })
print(json.dumps({"elapsed": elapsed, "receipts": slim}))
"""


def run_engine(engine: str, hs: list[int]) -> dict:
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-B", "-c", WORKER, str(ROOT), engine, ",".join(str(h) for h in hs)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"engine={engine} failed\n{proc.stderr}\n{proc.stdout}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--output", type=Path, default=PACKAGE / "RESULT.json")
    args = parser.parse_args(argv)
    if args.rounds < 1:
        raise SystemExit("--rounds must be >= 1")

    baseline_samples = []
    optimized_samples = []
    reference = None
    for round_index in range(args.rounds):
        order = ("baseline", "optimized") if round_index % 2 == 0 else ("optimized", "baseline")
        pair = {}
        for engine in order:
            payload = run_engine(engine, list(BENCH_H))
            if reference is None:
                reference = payload["receipts"]
            elif payload["receipts"] != reference:
                raise SystemExit(f"receipt mismatch on round {round_index} engine={engine}")
            pair[engine] = payload["elapsed"]
        baseline_samples.append(pair["baseline"])
        optimized_samples.append(pair["optimized"])
        print(
            f"round={round_index} order={order[0]}->{order[1]} "
            f"baseline={pair['baseline']:.6f}s optimized={pair['optimized']:.6f}s",
            flush=True,
        )

    base_med = statistics.median(baseline_samples)
    opt_med = statistics.median(optimized_samples)
    result = {
        "status": "PASS_IDENTICAL_INPLACE_COMPILE_RECEIPTS",
        "ai_assistance": (
            "Substantial AI assistance for profiling, implementation, packaging, "
            "benchmarking and writing. Not independent human peer review."
        ),
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "fixture": f"compile_side h={list(BENCH_H)}",
        "engines": {
            "baseline": "research/inplace-side-compile-scan/baseline.py",
            "optimized": "scripts/experiments/inplace_side.py",
        },
        "source_sha256": {
            "baseline.py": sha256((PACKAGE / "baseline.py").read_bytes()).hexdigest(),
            "scripts/experiments/inplace_side.py": sha256(
                (ROOT / "scripts/experiments/inplace_side.py").read_bytes()
            ).hexdigest(),
        },
        "environment": {
            "python": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "implementation": platform.python_implementation(),
            "os_caches_flushed": False,
            "isolated_host": False,
        },
        "rounds": args.rounds,
        "baseline_seconds": baseline_samples,
        "optimized_seconds": optimized_samples,
        "medians": {
            "baseline": base_med,
            "optimized": opt_med,
            "speedup": (base_med / opt_med) if opt_med else None,
        },
        "receipt_fields_compared": sorted(reference[0].keys()) if reference else [],
        "compile_h": [r["h"] for r in reference] if reference else [],
        "gate_counts": [len(r["gates"]) for r in reference] if reference else [],
        "scope": (
            "Historical inplace-side compile_side on h in {22,26,30}. "
            "Not a selected-supplier cold replay or multiplication runtime."
        ),
        "no_new_kappa": True,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"PASS_IDENTICAL_INPLACE_COMPILE_RECEIPTS "
        f"median_baseline={base_med:.6f}s median_optimized={opt_med:.6f}s "
        f"speedup={base_med / opt_med:.3f}x output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
