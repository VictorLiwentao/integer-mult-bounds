#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production fused dyadic audit.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import random
import subprocess
import sys
import tarfile
import tempfile
import types
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/gauge44-frames-x/independent/audit_local.py"
BASELINE = PACKAGE / "baseline.py"
OPT_IN_KERNEL = ROOT / "research/scalar-fused-dyadic/kernel.py"
ARCHIVE = ROOT / "research/community-frontier799-audit/integrated799-replay.tar.gz"
WORD_MEMBER = "native/jx/FULL-WORD.json.gz"
PARENT = ROOT / (
    "research/community-k492-audit/pr622/replay/baseline558/complex-global/base/"
    "split-centres/CANONICAL-WORD.json.gz"
)
REFERENCE_RECEIPT = ROOT / "research/community-frontier799-audit/INDEPENDENT-LOCAL.json"

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "4744d8783c25bf7bf5076886169077ca3808309a"
ORIGINAL_SHA256 = "03afcfc9da428b3f6edac81c1fee7f277ab81b64998efae78380b63498dec6cd"
OPTIMIZED_SHA256 = "b3695bf9c9988a8929702a1645c36b00791b9a8d5ab4dfd84568edeb26ecb7e9"
WORD_SHA256 = "0841ef246eea89d612342d80ae503eda573626d99b92ce0c3f94225b6e00d3d9"
PARENT_SHA256 = "66d3c3c70983224650643a0a05a21ac6c6959f84d0f4528650601016f5a76844"
SECTIONS = ("A", "B", "cut", "precondition", "cleanup")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_module(name: str, path: Path):
    """Load a checker with assertions kept even when this wrapper runs under -O."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), module.__dict__)
    return module


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/gauge44-frames-x/independent/audit_local.py"],
        cwd=ROOT,
    )
    require(hashlib.sha256(original).hexdigest() == ORIGINAL_SHA256, "base audit sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/gauge44-frames-x/independent/audit_local.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base audit blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit audit")
    require(digest_file(PRODUCTION) == OPTIMIZED_SHA256, "production audit digest drift")
    require(PRODUCTION.read_bytes() != original, "production must differ from pairwise baseline")
    require(digest_file(PARENT) == PARENT_SHA256, "parent word digest drift")
    require(OPT_IN_KERNEL.exists(), "opt-in fused kernel missing")
    prod_text = PRODUCTION.read_text(encoding="utf-8")
    base_text = BASELINE.read_text(encoding="utf-8")
    require("def fused(" in prod_text, "production must define fused")
    require("def apply(" in prod_text, "production must define apply")
    require("def fused(" not in base_text, "baseline must stay pairwise")
    require("dst.get(k,F(0))+q*x" in base_text.replace(" ", ""),
            "baseline must keep the pairwise multiply-add")


def stable(report: dict) -> dict:
    report = dict(report)
    elapsed = report.pop("elapsed_seconds", None)
    require(elapsed is None or (type(elapsed) in (int, float) and elapsed >= 0), "invalid timing")
    return report


def word_bytes() -> bytes:
    with tarfile.open(ARCHIVE) as archive:
        members = [m for m in archive.getmembers() if m.name == WORD_MEMBER]
        require(len(members) == 1 and members[0].isfile(), "ambiguous benchmark member")
        raw = archive.extractfile(members[0]).read()
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA256, "immutable word bytes")
    return raw


def outcome(module, word: Path, out: Path, main: Path | None):
    printed = io.StringIO()
    try:
        with redirect_stdout(printed):
            module.run(word, out, main)
    except Exception as exc:  # noqa: BLE001 - compare exact failure class/message
        return ("raise", type(exc).__name__, str(exc))
    report = json.loads(out.read_text(), object_pairs_hook=unique_object)
    return ("pass", stable(report))


def check_identical_receipts() -> dict:
    ref = load_module("fused_baseline", BASELINE)
    prod = load_module("fused_production", PRODUCTION)
    raw = word_bytes()
    expected = stable(json.loads(REFERENCE_RECEIPT.read_text(), object_pairs_hook=unique_object))
    with tempfile.TemporaryDirectory(prefix="scalar-fused-prod-") as tmp:
        tmp_path = Path(tmp)
        word = tmp_path / "FULL-WORD.json.gz"
        word.write_bytes(raw)
        left = outcome(ref, word, tmp_path / "ref.json", ROOT)
        right = outcome(prod, word, tmp_path / "prod.json", ROOT)
        require(left == right, "honest mismatch on PR799 jx word")
        require(left[0] == "pass", "honest word must pass")
        require(left[1] == expected, "honest receipt must match maintainer INDEPENDENT-LOCAL.json")
        # Seeded fuzz mutations must agree on accept/reject and receipts.
        word_obj = json.loads(gzip.decompress(raw))
        rng = random.Random(93)
        fuzz_ok = 0
        for i in range(40):
            mutant = mutate(word_obj, rng)
            path = tmp_path / f"fuzz-{i}.json.gz"
            path.write_bytes(gzip.compress(json.dumps(mutant).encode(), mtime=0))
            left = outcome(ref, path, tmp_path / f"fuzz-{i}-ref.json", ROOT)
            right = outcome(prod, path, tmp_path / f"fuzz-{i}-prod.json", ROOT)
            require(left == right, f"fuzz mismatch #{i}")
            fuzz_ok += 1
    return {"honest": 1, "fuzz": fuzz_ok}


def mutate(word, rng):
    w = copy.deepcopy(word)
    n = 2 * w["report"]["v"] + w["report"]["R"]
    sec = rng.choice([s for s in SECTIONS if w[s]])
    i = rng.randrange(len(w[sec]))
    g = list(w[sec][i])
    kind = rng.choice(["coef", "coef", "coef", "drop", "swap", "dup", "reg", "self", "zero_scale"])
    if kind == "coef" and g[0] == "add":
        g[3] = g[3] + rng.choice([-2, -1, 1, 2, 3])
    elif kind == "drop":
        del w[sec][i]
        return w
    elif kind == "swap" and len(w[sec]) > 1:
        j = i + 1 if i + 1 < len(w[sec]) else i - 1
        w[sec][i], w[sec][j] = w[sec][j], w[sec][i]
        return w
    elif kind == "dup":
        w[sec].insert(i, copy.deepcopy(g))
        return w
    elif kind == "reg":
        g[1 + (rng.randrange(2) if g[0] == "add" else 0)] = rng.randrange(n)
    elif kind == "self" and g[0] == "add":
        g[2] = g[1]
    elif kind == "zero_scale" and g[0] == "scale":
        g[2] = 0
    w[sec][i] = g
    return w


def check_temp_corruption_rejection() -> dict:
    """On-disk foil that drops the destination term must diverge or fail closed."""
    ref = load_module("fused_baseline_corrupt", BASELINE)
    raw = word_bytes()
    with tempfile.TemporaryDirectory(prefix="scalar-fused-prod-honest-") as tmp:
        tmp_path = Path(tmp)
        word = tmp_path / "honest.json.gz"
        word.write_bytes(raw)
        honest = outcome(load_module("fused_production_honest", PRODUCTION), word, tmp_path / "honest.json", ROOT)

    text = PRODUCTION.read_text(encoding="utf-8")
    needle = "a=fused(q,x,dst.get(k))"
    require(needle in text, "fused apply site missing for corruption control")
    foil_text = text.replace(needle, "a=fused(q,x,None)", 1)
    require(foil_text != text, "mutant must differ on disk")
    with tempfile.TemporaryDirectory(prefix="scalar-fused-prod-foil-") as tmp:
        mutant_path = Path(tmp) / "audit_local.py"
        mutant_path.write_text(foil_text, encoding="utf-8")
        work = Path(tmp) / "work"
        work.mkdir()
        word = work / "word.json.gz"
        word.write_bytes(raw)
        try:
            bad = outcome(load_module("fused_foil", mutant_path), word, work / "out.json", ROOT)
        except Exception as exc:  # noqa: BLE001
            return {"rejected": True, "mode": "import_or_runtime_failure", "detail": str(exc)[:240]}
        require(bad != honest, "destination-drop foil must change the audit outcome")
        return {"rejected": True, "mode": "receipt_divergence"}


def check_o_admission() -> None:
    """require()/RuntimeError admission stays enforced under -O loaders."""
    prod = load_module("fused_production_assert_gate", PRODUCTION)
    rows = [{0: __import__("fractions").Fraction(1)}, {1: __import__("fractions").Fraction(1)}]
    fired = False
    try:
        prod.apply(["scale", 0, 0, 1], rows)
    except RuntimeError as exc:
        require("zero scale" in str(exc), f"unexpected scale error: {exc}")
        fired = True
    except Exception as exc:  # noqa: BLE001
        require(False, f"zero-scale admission must raise RuntimeError, got {type(exc).__name__}: {exc}")
    require(fired, "NO_ASSERT_FIRED: zero-scale admission stripped under -O loader")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    check_baseline_bytes()
    check_o_admission()
    receipts = check_identical_receipts()
    corruption = check_temp_corruption_rejection()
    require(corruption["rejected"], "corruption control must reject")
    print(
        "PASS_SCALAR_FUSED_DYADIC_PRODUCTION "
        f"honest={receipts['honest']} "
        f"fuzz={receipts['fuzz']} "
        f"corruption={corruption['mode']} "
        "certs=0 no_new_kappa",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
