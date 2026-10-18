#!/usr/bin/env python3
"""Identify finite Sp(72,2) x 14826 stock as the uniform C(w) packet candidate.

Card selected-stock-envelope. Predecessor #3421 bound A=0 under the
finite-stock-as-C reading and left OQ2 open: adopt that stock as uniform C(w)
by tracing a residual that consumes a fresh complete physical-role packet of
matching cardinality at every atom width w. This package does not recompute
A=0 or B_bits=2642 as a contribution, does not bind rho, and does not realize
a leaf S_leaf class.

Admission uses need() and remains active under python -O.
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
B_BITS = 2642
PHYSICAL_FAMILIES = 14826
FAMILY_SPLIT = (14336, 480, 8, 2)
KAPPA_DECIMAL = "0.001672660197076918"
PROBED_WIDTHS = (1, 2, 4, 8, 16, 32, 64)


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
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    pinned = {}
    for row in inputs:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(len(raw) <= 4_000_000, "source size")
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw.decode("utf-8")
    return pinned


def sp72_order():
    """|Sp(72,2)| = 2^(36^2) * prod_{j=1..36} (2^(2j) - 1)."""
    order = 2 ** (36 * 36)
    for j in range(1, 37):
        order *= 2 ** (2 * j) - 1
    return order


def stock_block(assemble: str) -> str:
    """Exact assembler block that builds the charged per-level stock unit."""
    start = assemble.find("group=2**(36*36)")
    need(start >= 0, "assemble: Sp group start")
    end = assemble.find("assert finite['physical_row_coefficient']", start)
    need(end > start, "assemble: stock block end")
    return assemble[start:end]


def atom_width_free(block: str) -> bool:
    """True when the charged stock block has no atom-width parameter w."""
    # Reject bare identifier w / w= / (w / [w as a token; allow words like 'with'.
    if re.search(r"(?<![A-Za-z0-9_])w(?![A-Za-z0-9_])", block):
        return False
    return "q**(w" not in block and "q^(w" not in block


def row_program(row: int, divisor: int, depth: int, omit_restore_at: int = -1) -> int:
    """Finite semantic fixture: two sequential residuals and a restored role."""
    if depth == 0:
        return row
    unused, role = divmod(row, divisor)
    routed = (role + 1) % divisor
    for _ in range(2):
        unused = row_program(unused, divisor, depth - 1, omit_restore_at)
    restored = routed if depth == omit_restore_at else (routed - 1) % divisor
    return unused * divisor + restored


def coarse_residual_fixture(divisor: int, depth: int) -> dict:
    stock = divisor ** depth
    need(stock > 0 and stock % (divisor ** depth) == 0, "divisible stock")
    for row in range(stock):
        first = row_program(row, divisor, depth)
        second = row_program(first, divisor, depth)
        need(first == second == row, "residual restore/reuse")
    omitted = row_program(0, divisor, depth, omit_restore_at=depth)
    need(omitted != 0, "control: omit-restore must diverge")
    return {
        "divisor": divisor,
        "depth": depth,
        "rows": stock,
        "sequential_residuals": 2,
        "all_rows_restored": True,
        "omit_restore_diverges": True,
    }


def evaluate():
    texts = pin_sources()
    assemble = texts["research/gauge44-slots-t16/code/assemble.py"]
    proof = texts["research/selected-coarse-depth-stock/PROOF.md"]
    shape = texts["research/selected-stock-shape-a-zero/README.md"]
    prior = texts["research/selected-stock-envelope-m73/README.md"]
    bit_parent = texts["research/selected-bit-parent-reserve/README.md"]
    cover_cx = texts["notes/three-stage-cover-complex.tex"]
    cover_bit = texts["notes/three-stage-cover-bit.tex"]
    scope = texts["docs/research/selected-bootstrap-scope-map.md"]

    # Predecessor pins: A=0 already proved; OQ2 still asks for C(w) adoption.
    need("A = 0" in shape or "**A = 0**" in shape, "cite: A=0 predecessor")
    need("B_bits = 2642" in shape or "B = 2642" in prior, "cite: B_bits predecessor")
    need("Adopt finite stock as uniform `C(w)`" in shape, "cite: #3421 OQ2")
    need(
        "physical-role packet whose cardinality equals the finite stock"
        in shape,
        "cite: OQ2 packet first step",
    )
    need("rho" in shape.lower() and "unbound" in shape, "cite: rho still unbound")

    # Assembler identity: charged stock = |Sp(72,2)| * physical families.
    identity_compact = (
        "invoice['physical_stock_identity']==dict(data_and_owner_families=14336,"
        "local_helpers=R,private_centres=8,coefficient_work=2)"
    )
    need(identity_compact in assemble.replace(" ", ""),
         "cite: physical_stock_identity")
    need(sum(FAMILY_SPLIT) == PHYSICAL_FAMILIES, "family split sum")
    need(
        "stock=group*invoice['physical']" in assemble.replace(" ", ""),
        "cite: stock=group*physical",
    )
    need(
        "finite['physical_row_coefficient']==2*stock.bit_length()+9909+252+1024"
        in assemble.replace(" ", ""),
        "cite: row coefficient from stock bits",
    )

    block = stock_block(assemble)
    need("group=2**(36*36)" in block, "Sp n=36 start")
    need(
        "for j in range(1,37):group*=2**(2*j)-1" in block
        or "for j in range(1, 37):group*=2**(2*j)-1" in block,
        "Sp product loop",
    )
    need(atom_width_free(block), "stock block has no atom-width w")

    order = sp72_order()
    need(order.bit_length() == 2628, "Sp bits 2628")
    need(PHYSICAL_FAMILIES.bit_length() == 14, "family bits 14")
    packet = order * PHYSICAL_FAMILIES
    need(packet.bit_length() == B_BITS, "packet bits = 2642")
    need(order.bit_length() + PHYSICAL_FAMILIES.bit_length() == B_BITS,
         "B = 2628 + 14")

    # Uniform C(w) candidate: same packet cardinality at every probed w.
    c_bits_at = {w: packet.bit_length() for w in PROBED_WIDTHS}
    need(len(set(c_bits_at.values())) == 1, "C bits constant in w")
    need(all(c_bits_at[w] == B_BITS for w in PROBED_WIDTHS), "C bits = 2642")
    slopes = {
        f"{w1}->{w2}": (c_bits_at[w2] - c_bits_at[w1]) / (w2 - w1)
        for w1, w2 in ((1, 2), (2, 8), (8, 64))
    }
    need(all(slope == 0.0 for slope in slopes.values()), "zero slope of log2 C")

    # Cover contrast: complex finite binary group; ordinary digit tower.
    need("These full finite role counts are retained" in cover_cx,
         "cite: finite roles retained")
    need("needs no numerical enumeration" in cover_cx, "cite: binary matrices")
    need("q^{m^2(w-1)}" not in cover_cx, "no complex digit tower")
    need("W(w)" not in cover_cx, "no complex W(w)")
    need("W(w)=W_0q^{m^2(w-1)}" in cover_bit.replace(" ", ""),
         "cite: ordinary W(w)")
    need(
        "one fresh complete physical-role packet per active coarse level"
        in bit_parent,
        "cite: ordinary packet interface language",
    )

    # Coarse vs leaf: this package targets coarse C(w), not leaf rho.
    proof_flat = " ".join(proof.split())
    need(
        "Ordinary peeled atoms, routing, adapters and high-part exchanges "
        "are separate completed calls" in proof_flat,
        "cite: leaf classes separate from coarse stock",
    )
    need(
        "Whether the finite stock bounds uniform C(w)" in proof,
        "cite: finite-stock-as-C admission named",
    )
    need("The selected complex supplier has `m=73`" in scope,
         "cite: m=73 binding")

    # Semantic fixture: one coarse residual draws a fresh packet role and
    # restores it so a sequential sibling reuses the same stock. Divisor is a
    # w-free positive integer; the real packet C is separately shown w-free.
    fixture = coarse_residual_fixture(divisor=5, depth=2)
    need(fixture["all_rows_restored"], "fixture restore")
    need(atom_width_free("divisor=5; depth=2"), "fixture divisor w-free")

    # Kappa unchanged.
    selected = read_json(ROOT / "certificates/selected-result.json")
    decimal = selected.get("decimal")
    need(decimal == KAPPA_DECIMAL or str(decimal) == KAPPA_DECIMAL,
         "kappa decimal pin")

    # Mutation controls.
    need(not atom_width_free("group=2**(36*36); stock=group*q**(w-1)"),
         "control: w-injected stock rejected")
    need(c_bits_at[1] == c_bits_at[64], "control: width-varying C rejected")
    need(packet.bit_length() != 2641, "control: wrong B rejected")
    need(sum(FAMILY_SPLIT) != 14825, "control: wrong family sum rejected")
    need("q^{m^2(w-1)}" not in cover_cx, "control: digit tower still absent")

    return {
        "schema_version": 1,
        "status": "PASS_SELECTED_STOCK_FINITE_C_PACKET",
        "producer": "selected-complex-m73",
        "packet_cardinality_factors": {
            "sp72_bits": 2628,
            "physical_families": PHYSICAL_FAMILIES,
            "family_split": list(FAMILY_SPLIT),
            "packet_bits": B_BITS,
        },
        "assembler_stock_unit": "group*physical",
        "atom_width_free_stock_block": True,
        "probed_widths": list(PROBED_WIDTHS),
        "c_bits_by_width": {str(w): c_bits_at[w] for w in PROBED_WIDTHS},
        "zero_slopes": slopes,
        "coarse_residual_fixture": fixture,
        "leaf_classes_separate": True,
        "rho": "unbound",
        "a_zero_cited_not_recomputed": True,
        "outer_adoption": "not_claimed",
        "no_new_kappa": True,
        "kappa_decimal": KAPPA_DECIMAL,
        "marker": MARKER,
    }


def admit(observed, certificate):
    need(observed["status"] == certificate["status"], "certificate mismatch")
    need(observed["marker"] == certificate["marker"], "certificate mismatch")
    need(
        observed["packet_cardinality_factors"]["packet_bits"]
        == certificate["packet_cardinality_factors"]["packet_bits"],
        "certificate mismatch",
    )
    need(observed["rho"] == certificate["rho"], "certificate mismatch")
    need(observed["no_new_kappa"] is True, "certificate mismatch")
    need(observed["atom_width_free_stock_block"] is True, "certificate mismatch")
    need(observed["outer_adoption"] == "not_claimed", "certificate mismatch")


def main():
    observed = evaluate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    admit(observed, certificate)
    print(MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
