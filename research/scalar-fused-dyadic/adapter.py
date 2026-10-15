"""Opt-in fused arithmetic in the pinned complete PR799 independent audit.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
Original checker by icekylinx, retained by Jeremy Kothe; source bytes unchanged.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# Production frames-x now ships fused apply; the pairwise reference is vendored.
BASELINE = HERE / "baseline.py"
PRODUCTION = "research/gauge44-frames-x/independent/audit_local.py"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_pins(root=ROOT):
    pins = json.loads((HERE / "SOURCES.json").read_bytes())
    for entry in pins["files"]:
        usage = entry.get("usage", "input")
        if usage == "provenance":
            continue
        data = (root / entry["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry["sha256"],
                "source pin mismatch: " + entry["path"])
    # Pairwise baseline bytes must stay exact.
    require(hashlib.sha256(BASELINE.read_bytes()).hexdigest() ==
            "03afcfc9da428b3f6edac81c1fee7f277ab81b64998efae78380b63498dec6cd",
            "vendored baseline drift")
    return pins


def auditor(root=ROOT, engine="fused"):
    source_pins(root)
    if engine == "reference":
        return load(BASELINE, "pinned_independent_auditor_baseline")
    require(engine == "fused", "unknown engine")
    # Prefer the production fused auditor when present; otherwise monkey-patch.
    production = root / PRODUCTION
    module = load(production, "pinned_independent_auditor")
    if "def fused(" not in production.read_text(encoding="utf-8"):
        module.apply = load(HERE / "kernel.py", "fused_scalar_kernel").apply
    return module


def run(word, output, root=ROOT, engine="fused", parent=True):
    require(not output.exists(), "output already exists")
    # Word admission is deliberately the original auditor's responsibility,
    # permitting the differential suite to exercise genuinely changed inputs.
    # The benchmark separately binds its exact word before and after each run.
    module = auditor(root, engine)
    module.run(word, output, root if parent else None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("reference", "fused"), default="fused")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.word, args.output, args.root.resolve(), args.engine)


if __name__ == "__main__":
    main()
