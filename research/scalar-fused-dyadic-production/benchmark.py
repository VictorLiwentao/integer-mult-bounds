#!/usr/bin/env python3
"""Paired wall-time samples for production fused dyadic audit_local.

Descriptive only: timing is not a correctness gate.
"""
from __future__ import annotations

import argparse
import contextlib
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import statistics
import sys
import tarfile
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/gauge44-frames-x/independent/audit_local.py"
BASELINE = PACKAGE / "baseline.py"
ARCHIVE = ROOT / "research/community-frontier799-audit/integrated799-replay.tar.gz"
WORD_MEMBER = "native/jx/FULL-WORD.json.gz"
WORD_SHA256 = "0841ef246eea89d612342d80ae503eda573626d99b92ce0c3f94225b6e00d3d9"
BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"


def load_module(name: str, path: Path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), module.__dict__)
    return module


def stable(report: dict) -> dict:
    report = dict(report)
    report.pop("elapsed_seconds", None)
    return report


def run_once(module, word: Path, out: Path) -> tuple[float, dict]:
    printed = io.StringIO()
    start = time.perf_counter()
    with contextlib.redirect_stdout(printed):
        module.run(word, out, ROOT)
    elapsed = time.perf_counter() - start
    return elapsed, stable(json.loads(out.read_text()))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args(argv)

    with tarfile.open(ARCHIVE) as archive:
        raw = archive.extractfile(WORD_MEMBER).read()
    if hashlib.sha256(raw).hexdigest() != WORD_SHA256:
        raise SystemExit("benchmark word digest drift")

    base_times = []
    prod_times = []
    with tempfile.TemporaryDirectory(prefix="scalar-fused-bench-") as tmp:
        tmp_path = Path(tmp)
        word = tmp_path / "FULL-WORD.json.gz"
        word.write_bytes(raw)
        for i in range(args.rounds):
            order = ("baseline", "production") if i % 2 == 0 else ("production", "baseline")
            receipts = {}
            for engine in order:
                path = BASELINE if engine == "baseline" else PRODUCTION
                module = load_module(f"{engine}_{i}", path)
                out = tmp_path / f"r{i}-{engine}.json"
                dt, receipt = run_once(module, word, out)
                receipts[engine] = receipt
                if engine == "baseline":
                    base_times.append(dt)
                else:
                    prod_times.append(dt)
            if receipts["baseline"] != receipts["production"]:
                raise SystemExit("PASS gate failed: receipts diverged during benchmark")

    base_med = statistics.median(base_times)
    prod_med = statistics.median(prod_times)
    ratio = base_med / prod_med if prod_med else float("inf")
    result = {
        "schema_version": 1,
        "package": "research/scalar-fused-dyadic-production",
        "base_commit": BASE_COMMIT,
        "workload": "PR799 jx FULL-WORD independent audit with parent centre/port check",
        "rounds": args.rounds,
        "baseline_seconds": base_times,
        "production_seconds": prod_times,
        "median_baseline_seconds": base_med,
        "median_production_seconds": prod_med,
        "median_speedup": ratio,
        "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
        "production_sha256": hashlib.sha256(PRODUCTION.read_bytes()).hexdigest(),
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
        f"PASS_IDENTICAL_SCALAR_FUSED_DYADIC_PRODUCTION_RECEIPTS "
        f"median {base_med:.3f}->{prod_med:.3f}s ({ratio:.3f}x)",
        flush=True,
    )
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
