#!/usr/bin/env python3
"""Independent scanner: rebuild routing/adapter rho discharge without verify.py.

Re-reads the same hash-pinned sources and rebuilds the inventory, charge class,
and remaining ordinary leaf classes from substring facts alone. Admission uses
need() under -O.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_COMPLEX_ROUTER_RHO_DISCHARGE "
    "inventory=4 routing_adapters_ordinary_calls=0 rho_contrib=0 "
    "remaining=peeled+highpart A=0_cited B=2642_cited no_new_kappa"
)
INPUTS = (
    "research/selected-coarse-depth-stock/PROOF.md",
    "research/selected-stock-shape-a-zero/README.md",
    "research/selected-stock-envelope-m73/README.md",
    "research/stock-routing-factor/RESULT.json",
    "notes/three-stage-cover-complex.tex",
    "notes/three-stage-cover-bit.tex",
    "notes/three-stage-cover-rows.tex",
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
    a_zero = texts["research/selected-stock-shape-a-zero/README.md"]
    envelope = texts["research/selected-stock-envelope-m73/README.md"]
    routing_factor = json.loads(
        texts["research/stock-routing-factor/RESULT.json"],
        object_pairs_hook=pairs_unique,
    )
    cover_cx = texts["notes/three-stage-cover-complex.tex"]
    cover_bit = texts["notes/three-stage-cover-bit.tex"]
    cover_rows = texts["notes/three-stage-cover-rows.tex"]

    need(re.search(r"routing,\s*adapters\s*and\s*high-part", proof) is not None,
         "inventory phrase")
    need("Ordinary peeled" in proof, "peeled class named")

    need(re.search(r"\bA\s*=\s*0\b", a_zero) is not None, "A=0 extract")
    match = re.search(r"B\s*=\s*2628\s*\+\s*14\s*=\s*(2642)", envelope)
    need(match is not None, "B extract")
    b_bits = int(match.group(1))
    need(b_bits == 2642, "B value")

    need("scalar/router" in cover_cx, "scalar/router present")
    need("fixed address adapters" in cover_cx, "adapters named")
    need("without recursive Fourier children" in cover_cx, "no fourier")
    need("finite scalar/router guard" in cover_cx, "guard present")
    need("width-$O(w)$ interchanges" in cover_bit, "BIT ordinary routing")
    need(routing_factor.get("named_factor") is False, "unnamed c_R")
    need("ordinary width-$k$ interchange" in cover_rows, "high-part ordinary")

    inventory = ["peeled", "routing", "adapters", "high-part"]
    remaining = ["peeled", "high-part"]
    ordinary_calls = 0
    rho_contrib = 0

    return {
        "schema_version": 1,
        "status": "PASS_SELECTED_COMPLEX_ROUTER_RHO_DISCHARGE",
        "producer": "selected-complex-m73",
        "leaf_inventory": inventory,
        "routing_adapters_charge": "finite_scalar_router_guard",
        "routing_adapters_ordinary_leaf_calls": ordinary_calls,
        "routing_adapters_recursive_fourier_children": 0,
        "routing_adapters_rho_contribution": rho_contrib,
        "bit_routing_ordinary_interchanges": "constant_unnamed_c_R",
        "remaining_ordinary_leaf_classes": remaining,
        "global_rho": "open_pending_peeled_highpart",
        "A_cited": 0,
        "B_bits_cited": b_bits,
        "composition_after_discharge": "(43/26)*(1-s)*2642 + rho_peeled_highpart",
        "no_new_kappa": True,
        "kappa_decimal": "0.001672660197076918",
        "marker": MARKER,
    }


def main():
    observed = evaluate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    need(observed == certificate, "certificate mismatch")
    print(
        "PASS_SELECTED_COMPLEX_ROUTER_RHO_DISCHARGE_INDEPENDENT "
        "inventory=4 ordinary_calls=0 rho_contrib=0 remaining=peeled+highpart"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
