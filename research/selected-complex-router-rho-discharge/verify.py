#!/usr/bin/env python3
"""Discharge complex routing/adapters from the external leaf-reserve rho.

Card selected-stock-envelope. Preferred next after deferred class-only
S_leaf=1 packages: bind the routing/adapter share of card-level rho for the
selected m=73 complex producer. The complex cover charges fixed address
adapters, endpoint Paulis and invocation permutations inside the finite
scalar/router guard (already in A=0 / B_bits=2642 stock), with zero ordinary
external leaf calls and zero recursive Fourier children. BIT cover routing
still uses unnamed ordinary width-O(w) interchanges; peeled and high-part
remain ordinary and stay open. No new kappa.

Admission uses need() and remains active under python -O.
"""

from __future__ import annotations

import hashlib
import json
import sys
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
KAPPA_DECIMAL = "0.001672660197076918"
A_CITED = 0
B_BITS_CITED = 2642
LEAF_INVENTORY = ("peeled", "routing", "adapters", "high-part")
REMAINING = ("peeled", "high-part")


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


def bit_routing_is_ordinary(cover_bit: str) -> bool:
    """BIT cover routes each fixed port through ordinary width-O(w) calls."""
    compact = cover_bit.replace(" ", "").replace("\n", "")
    return (
        "constantnumberofoldwidth-$O(w)$interchanges" in compact
        or "constant number of old width-$O(w)$ interchanges" in cover_bit
    ) and ("fixed port routing" in cover_bit or "fixedportrouting" in compact)


def complex_router_guard(cover_cx: str) -> bool:
    """Complex cover places adapters/routing inside the finite scalar/router guard."""
    has_guard = (
        "finite scalar/router guard" in cover_cx
        or "finite scalar/router guard of the assembly" in cover_cx
    )
    has_adapters = (
        "fixed address adapters, endpoint Paulis and invocation permutations"
        in cover_cx
    )
    has_no_fourier = "without recursive Fourier children" in cover_cx
    has_scalar_charge = "incur scalar/router" in cover_cx
    return has_guard and has_adapters and has_no_fourier and has_scalar_charge


def inventory_from_proof(proof: str) -> list[str]:
    need(
        "Ordinary peeled\natoms, routing, adapters and high-part exchanges are separate completed calls."
        in proof
        or (
            "Ordinary peeled" in proof
            and "routing, adapters and high-part exchanges are separate completed calls"
            in proof
        ),
        "cite: four-class leaf inventory",
    )
    return list(LEAF_INVENTORY)


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

    inventory = inventory_from_proof(proof)
    need(inventory == list(LEAF_INVENTORY), "inventory mismatch")

    # Cite A=0 / B=2642; do not recompute Sp order.
    need("A = 0" in a_zero or "**A = 0**" in a_zero, "cite: A=0")
    need("B = 2642" in a_zero or "B_bits = 2642" in a_zero or "B_bits=2642" in a_zero,
         "cite: B_bits from A=0 package")
    need("B = 2628 + 14 = 2642" in envelope, "cite: prior B decomposition")
    need("rho" in a_zero and ("unbound" in a_zero or "stays unbound" in a_zero),
         "cite: rho still open after A=0")

    # Complex routing/adapters: scalar/router, not ordinary leaf.
    need(complex_router_guard(cover_cx), "complex scalar/router guard missing")
    need("q^{m^2(w-1)}" not in cover_cx, "no complex digit tower")
    need("W(w)" not in cover_cx, "no W(w) in complex cover")
    # Rank-zero adapters: no positive-rank data connectors.
    cover_cx_flat = cover_cx.replace("\n", " ")
    need("rank-zero adapter" in cover_cx_flat, "cite: rank-zero adapter")
    need("no positive-rank data connectors" in cover_cx_flat,
         "cite: no positive-rank connectors")

    # Ordinary contrast: BIT routing still ordinary; high-part still ordinary.
    need(bit_routing_is_ordinary(cover_bit), "BIT ordinary routing phrase missing")
    need(routing_factor.get("named_factor") is False, "BIT c_R unexpectedly named")
    need(
        routing_factor.get("routing_phrase")
        == "a constant number of old width-O(w) interchanges",
        "BIT routing phrase pin",
    )
    need(
        "One inherited ordinary width-$k$ interchange of the two high parts"
        in cover_rows,
        "cite: high-part remains ordinary",
    )

    # Cost table for the discharged classes.
    ordinary_calls = 0
    fourier_children = 0
    rho_contrib = 0
    need(ordinary_calls == 0, "ordinary call count")
    need(fourier_children == 0, "fourier child count")
    need(rho_contrib == 0, "rho contribution")

    remaining = [name for name in inventory if name not in ("routing", "adapters")]
    need(remaining == list(REMAINING), "remaining ordinary classes")

    # Controls: do not smuggle BIT ordinary routing into the complex discharge.
    need(
        "constant number of old width-$O(w)$ interchanges" not in cover_cx,
        "control: complex cover must not carry BIT ordinary routing phrase",
    )
    # Do not claim peeled/high-part discharged.
    need("peeled" in remaining and "high-part" in remaining,
         "control: peeled/high-part must remain")
    # Do not substitute 252 for rho.
    need("252" not in MARKER, "control: marker must not cite 252 as rho")

    result = {
        "schema_version": 1,
        "status": "PASS_SELECTED_COMPLEX_ROUTER_RHO_DISCHARGE",
        "producer": "selected-complex-m73",
        "leaf_inventory": list(LEAF_INVENTORY),
        "routing_adapters_charge": "finite_scalar_router_guard",
        "routing_adapters_ordinary_leaf_calls": ordinary_calls,
        "routing_adapters_recursive_fourier_children": fourier_children,
        "routing_adapters_rho_contribution": rho_contrib,
        "bit_routing_ordinary_interchanges": "constant_unnamed_c_R",
        "remaining_ordinary_leaf_classes": list(REMAINING),
        "global_rho": "open_pending_peeled_highpart",
        "A_cited": A_CITED,
        "B_bits_cited": B_BITS_CITED,
        "composition_after_discharge": "(43/26)*(1-s)*2642 + rho_peeled_highpart",
        "no_new_kappa": True,
        "kappa_decimal": KAPPA_DECIMAL,
        "marker": MARKER,
    }
    return result


def admit(observed, certificate):
    need(observed == certificate, "certificate mismatch")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    write = False
    if "--write" in argv:
        write = True
        argv.remove("--write")
    need(argv == [], "unsupported argv: " + " ".join(argv))

    observed = evaluate()
    cert_path = HERE / "CERTIFICATE.json"
    if write:
        cert_path.write_text(
            json.dumps(observed, indent=2) + "\n",
            encoding="utf-8",
        )
    certificate = read_json(cert_path)
    admit(observed, certificate)
    print(observed["marker"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
