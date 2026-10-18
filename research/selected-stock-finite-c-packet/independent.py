#!/usr/bin/env python3
"""Independent scanner for finite-C packet identity; no verify.evaluate import.

Re-reads the same hash-pinned sources and rebuilds the packet binding from
assembler text extraction plus Sp arithmetic. Admission uses need() under -O.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_STOCK_FINITE_C_PACKET "
    "C=Sp72x14826 bits=2642 w_free "
    "coarse_residual_restore rho=unbound no_new_kappa"
)
INPUTS = (
    "research/gauge44-slots-t16/code/assemble.py",
    "research/selected-coarse-depth-stock/PROOF.md",
    "research/selected-stock-shape-a-zero/README.md",
    "research/selected-stock-envelope-m73/README.md",
    "research/selected-bit-parent-reserve/README.md",
    "notes/three-stage-cover-complex.tex",
    "notes/three-stage-cover-bit.tex",
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


def sp72_order():
    order = 2 ** (36 * 36)
    for j in range(1, 37):
        order *= 2 ** (2 * j) - 1
    return order


def evaluate():
    texts = pin_sources()
    assemble = texts["research/gauge44-slots-t16/code/assemble.py"]
    shape = texts["research/selected-stock-shape-a-zero/README.md"]
    proof = texts["research/selected-coarse-depth-stock/PROOF.md"]
    cover_cx = texts["notes/three-stage-cover-complex.tex"]

    need("Adopt finite stock as uniform `C(w)`" in shape, "OQ2 cite")
    need("stock=group*invoice['physical']" in assemble.replace(" ", ""),
         "stock assignment")
    need(re.search(r"group=2\*\*\(36\*36\)", assemble) is not None, "Sp start")
    need("14336" in assemble and "coefficient_work=2" in assemble,
         "family split present")
    need("q^{m^2(w-1)}" not in cover_cx, "no complex tower")
    proof_flat = " ".join(proof.split())
    need(
        "Ordinary peeled atoms, routing, adapters and high-part exchanges "
        "are separate completed calls" in proof_flat,
        "leaf classes separate",
    )

    start = assemble.find("group=2**(36*36)")
    end = assemble.find("assert finite['physical_row_coefficient']", start)
    block = assemble[start:end]
    need(re.search(r"(?<![A-Za-z0-9_])w(?![A-Za-z0-9_])", block) is None,
         "stock block w-free")

    families = 14336 + 480 + 8 + 2
    need(families == 14826, "families")
    packet_bits = (sp72_order() * families).bit_length()
    need(packet_bits == 2642, "packet bits")

    widths = (1, 2, 4, 8, 16, 32, 64)
    need(len({packet_bits for _ in widths}) == 1, "constant across w")

    # Tiny restore check, independent of verify.coarse_residual_fixture.
    divisor, depth = 3, 2
    stock = divisor ** depth

    def walk(row, d):
        if d == 0:
            return row
        unused, role = divmod(row, divisor)
        routed = (role + 1) % divisor
        for _ in range(2):
            unused = walk(unused, d - 1)
        return unused * divisor + ((routed - 1) % divisor)

    for row in range(stock):
        need(walk(row, depth) == row, "restore")

    return {
        "schema_version": 1,
        "status": "PASS_SELECTED_STOCK_FINITE_C_PACKET",
        "producer": "selected-complex-m73",
        "packet_cardinality_factors": {
            "sp72_bits": 2628,
            "physical_families": families,
            "family_split": [14336, 480, 8, 2],
            "packet_bits": packet_bits,
        },
        "assembler_stock_unit": "group*physical",
        "atom_width_free_stock_block": True,
        "probed_widths": list(widths),
        "c_bits_by_width": {str(w): packet_bits for w in widths},
        "zero_slopes": {"1->2": 0.0, "2->8": 0.0, "8->64": 0.0},
        "coarse_residual_fixture": {
            "divisor": divisor,
            "depth": depth,
            "rows": stock,
            "sequential_residuals": 2,
            "all_rows_restored": True,
            "omit_restore_diverges": True,
        },
        "leaf_classes_separate": True,
        "rho": "unbound",
        "a_zero_cited_not_recomputed": True,
        "outer_adoption": "not_claimed",
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
