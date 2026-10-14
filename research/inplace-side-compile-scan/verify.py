#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for faster inplace-side compile_side.

Read-only by default. Regenerates no certificate unless --write-certificate is
passed. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
from prepare_layers import serializable  # noqa: E402
from audit_inplace_side import certificate as production_certificate  # noqa: E402
from experiments import inplace_side as production  # noqa: E402


BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "4f5e7b3f61697ac2095e18d5cd00e3cacd875d99"
ORIGINAL_SHA256 = "4397b84f3ac52554bf14303171410a2799af0bf8dae11ec64594bb5c011e93a2"
BASE_CERTIFICATE_SHA256 = "0a312ea4a442361cb7d23626daaaa8a638f4847d0b7fae166b11c2a696fba2a1"
IDENTITY_H = (6, 10, 14, 18, 22, 26, 30)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_base_certificate_bytes() -> bytes:
    return subprocess.check_output(["git", "show", f"{BASE_COMMIT}:certificates/inplace-side.json"], cwd=ROOT)


def check_baseline_bytes() -> None:
    baseline = PACKAGE / "baseline.py"
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:scripts/experiments/inplace_side.py"], cwd=ROOT
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base inplace_side.py sha256 drift")
    require(
        subprocess.check_output(["git", "rev-parse", f"{BASE_COMMIT}:scripts/experiments/inplace_side.py"], cwd=ROOT)
        .decode()
        .strip()
        == ORIGINAL_BLOB,
        "base inplace_side.py blob drift",
    )
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")


def check_compile_identity(baseline, optimized) -> list[dict]:
    rows = []
    for h in IDENTITY_H:
        old = baseline.compile_side(h)
        new = optimized.compile_side(h)
        require(old == new, f"compile_side({h}) gate/pivot/receipt drift")
        rows.append(
            dict(
                h=h,
                roles=new["roles"],
                gates=len(new["gates"]),
                pivots=len(new["pivots"]),
            )
        )
    return rows


def check_singular_rejection(baseline, optimized) -> None:
    for eng, name in ((baseline, "baseline"), (optimized, "optimized")):
        try:
            eng.compile_side(8)
            raise AssertionError(f"{name} accepted singular h=8")
        except ValueError as exc:
            require("singular" in str(exc).lower(), f"{name} wrong rejection: {exc}")


def greatest_unused_mutant_compile_side(h):
    """Deliberate mutant: picks the greatest unused row instead of the least."""
    from experiments.inplace_side import triple_side

    triples, points, rows = triple_side(h)
    n = len(rows)
    work = list(rows)
    unused = [True] * n
    ops = []
    require(h % 4 == 2, "The n-role side matrix is singular for h divisible by four")
    pivots = []
    for col in range(n):
        mask = 1 << col
        p = None
        for i in range(n - 1, -1, -1):  # MUTATION: greatest instead of least
            if unused[i] and work[i] & mask:
                p = i
                break
        require(p is not None, "missing pivot")
        unused[p] = False
        pivots.append(p)
        row = work[p]
        for i in range(n):
            if i != p and work[i] & mask:
                work[i] ^= row
                ops.append((i, p))
    require(set(work) == {1 << i for i in range(n)}, "Incomplete elimination")
    initial = [row.bit_length() - 1 for row in work]
    values = [1 << j for j in initial]
    gates = list(reversed(ops))
    for t, s in gates:
        values[t] ^= values[s]
    require(values == rows, "Input matching and in-place mixer do not give the side map")
    return dict(
        h=h,
        triples=triples,
        points=points,
        rows=rows,
        pivots=pivots,
        initial=initial,
        gates=gates,
        roles=n,
    )


def check_mutant_rejected(baseline) -> None:
    # On every identity size the least/greatest unused rows differ for some column,
    # so the mutant gate list must differ from the lexicographic compile.
    raised = 0
    for h in IDENTITY_H:
        mutant = greatest_unused_mutant_compile_side(h)
        truth = baseline.compile_side(h)
        require(mutant != truth, f"mutant matched lexicographic compile_side at h={h}")
        require(mutant["pivots"] != truth["pivots"], f"mutant pivots matched at h={h}")
        raised += 1
    require(raised == len(IDENTITY_H), "mutant control incomplete")


def check_temp_corruption_rejected() -> None:
    """On-disk corruption of a temp production copy must change compile receipts."""
    src = SCRIPTS / "experiments/inplace_side.py"
    with tempfile.TemporaryDirectory(prefix="inplace-compile-scan-") as tmp:
        dest = Path(tmp) / "inplace_side.py"
        shutil.copy2(src, dest)
        text = dest.read_text(encoding="utf-8")
        # Flip least-unused scan direction in the temp copy only.
        corrupted = text.replace(
            "p=next(i for i in range(n) if unused[i] and work[i]&mask)",
            "p=next(i for i in range(n-1,-1,-1) if unused[i] and work[i]&mask)",
            1,
        )
        require(corrupted != text, "corruption edit did not apply")
        dest.write_text(corrupted, encoding="utf-8")
        mutant = load_module(dest, "inplace_side_corrupted_temp")
        truth = production.compile_side(10)
        bad = mutant.compile_side(10)
        require(bad != truth, "temp corruption still matched production compile_side(10)")


def check_duplicate_json_keys(path: Path) -> None:
    """Reject duplicate object keys in package JSON (object_pairs_hook)."""

    def hook(pairs):
        seen = {}
        for key, value in pairs:
            require(key not in seen, f"duplicate JSON key {key!r} in {path}")
            seen[key] = value
        return seen

    json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)


def check_certificate(write: bool) -> dict:
    result = production_certificate()
    path = ROOT / "certificates/inplace-side.json"
    text = json.dumps(serializable(result), indent=2, sort_keys=True) + "\n"
    if write:
        path.write_text(text, encoding="utf-8")
    committed = path.read_text(encoding="utf-8")
    require(committed == text, "working certificates/inplace-side.json does not match regenerated certificate()")
    check_duplicate_json_keys(path)
    base = load_base_certificate_bytes()
    require(sha256(base).hexdigest() == BASE_CERTIFICATE_SHA256, "base certificate sha256 drift")
    old = json.loads(base.decode("utf-8"))
    new = json.loads(committed)
    old_pin = old["source_sha256"].pop("scripts/experiments/inplace_side.py")
    new_pin = new["source_sha256"].pop("scripts/experiments/inplace_side.py")
    require(old_pin == ORIGINAL_SHA256, "unexpected base pin")
    require(new_pin == digest_file(SCRIPTS / "experiments/inplace_side.py"), "certificate pin != working source")
    require(old == new, "certificate changed outside the single inplace_side.py source pin")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="regenerate certificates/inplace-side.json (default: read-only compare)",
    )
    args = parser.parse_args(argv)

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "inplace_side_compile_baseline")
    optimized = production
    require(
        digest_file(SCRIPTS / "experiments/inplace_side.py") != ORIGINAL_SHA256,
        "production source still equals the unoptimized base pin",
    )
    require(
        digest_file(PACKAGE / "baseline.py") == ORIGINAL_SHA256,
        "baseline.py must equal the original source sha256",
    )

    rows = check_compile_identity(baseline, optimized)
    check_singular_rejection(baseline, optimized)
    check_mutant_rejected(baseline)
    check_temp_corruption_rejected()
    for name in ("TASK.json", "SOURCES.json", "VERIFY.json", "RESULT.json"):
        path = PACKAGE / name
        if path.exists():
            check_duplicate_json_keys(path)
    cert = check_certificate(write=args.write_certificate)

    print(
        "PASS_INPLACE_SIDE_COMPILE_SCAN "
        f"identity_h={[r['h'] for r in rows]} "
        f"gates={[r['gates'] for r in rows]} "
        f"optimize={sys.flags.optimize} "
        f"certificate_source_pin={cert['source_sha256']['scripts/experiments/inplace_side.py'][:12]} "
        "no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
