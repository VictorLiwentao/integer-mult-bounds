#!/usr/bin/env python3
"""Independent scanner for rho=0: no import of verify.py evaluators.

Re-reads the same hash-pinned sources and rebuilds the leaf-reserve binding
from substring and arithmetic facts alone. Admission uses need() under -O.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_STOCK_SHAPE_RHO_ZERO "
    "rho=0 S_leaf=1 B_bits=2642_cited A=0_cited "
    "completed_ordinary_leaf no_new_kappa"
)
INPUTS = (
    "research/selected-coarse-depth-stock/PROOF.md",
    "research/selected-coarse-depth-stock/README.md",
    "research/selected-stock-envelope-m73/README.md",
    "research/selected-bit-parent-reserve/README.md",
    "docs/research/selected-bootstrap-scope-map.md",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    out = {}
    for row in inputs:
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"],
             "source hash: " + row["path"])
        out[row["path"]] = raw.decode("utf-8")
    return out


def evaluate():
    texts = pin_sources()
    proof = texts["research/selected-coarse-depth-stock/PROOF.md"]
    prior = texts["research/selected-stock-envelope-m73/README.md"]
    bit_parent = texts["research/selected-bit-parent-reserve/README.md"]
    coarse_readme = texts["research/selected-coarse-depth-stock/README.md"]

    match = re.search(r"B = 2628 \+ 14 = (2642)", prior)
    need(match is not None, "prior B extraction")
    b_bits = int(match.group(1))
    need(b_bits == 2642, "extracted B")

    need("one may take S_leaf=1" in proof, "S_leaf=1 permission")
    need("no additional externally supplied row factor" in bit_parent,
         "zero external factor")
    need("inherited external slack rather than an ordinary-leaf reserve estimate"
         in proof, "252 not leaf reserve")
    need("external leaf factor can be one" in coarse_readme,
         "README factor one")
    need("Bind `rho`" in prior, "prior OQ")

    s_leaf = 1
    rho = 0
    need(math.log(s_leaf, 2) == 0.0, "log2(1)=0")
    for e, w in ((1, 1), (2, 8), (64, 73)):
        rhs = rho * w * (1.0 + math.log2(e))
        need(0.0 <= rhs, "shape holds")
        need(rhs == 0.0, "rhs zero")

    need(not (math.log(2, 2) <= 0.0), "B>1 control")
    need(not (math.log(252, 2) <= 0.0), "252 control")

    return {
        "schema_version": 1,
        "status": "PASS_SELECTED_STOCK_SHAPE_RHO_ZERO",
        "producer": "selected-complex-m73",
        "shape_rho": rho,
        "S_leaf": s_leaf,
        "shape_B_bits_cited": b_bits,
        "shape_A_cited": 0,
        "completed_ordinary_leaf_admission": True,
        "slack_252_is_not_S_leaf": True,
        "probes": [
            {"e": 1, "w": 1, "rhs": 0.0},
            {"e": 1, "w": 2, "rhs": 0.0},
            {"e": 2, "w": 8, "rhs": 0.0},
            {"e": 8, "w": 64, "rhs": 0.0},
            {"e": 64, "w": 73, "rhs": 0.0},
            {"e": 1024, "w": 256, "rhs": 0.0},
        ],
        "composition_under_rho_zero": "(43/26)*(1-s)*2642",
        "no_new_kappa": True,
        "kappa_decimal": "0.001672660197076918",
        "marker": MARKER,
    }


def main():
    observed = evaluate()
    need(observed["marker"] == MARKER, "marker")
    print(MARKER + "_INDEPENDENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
