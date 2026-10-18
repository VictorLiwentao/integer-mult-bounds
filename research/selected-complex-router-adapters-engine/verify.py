#!/usr/bin/env python3
"""Engine-measure complex routing∪adapters external leaf-reserve rho share.

Card selected-stock-envelope. Preferred next after deferred citation-only
router-rho discharge: measure ordinary external leaf calls / rho contribution
of routing∪adapters from an executable scalar/router residual engine, not
from tex phrase-matching. Cite A=0 / B_bits=2642; do not recompute. Peeled and
high-part remain open. No new kappa.

Admission uses need() and remains active under python -O.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import router  # noqa: E402

MARKER = (
    "PASS_SELECTED_COMPLEX_ROUTER_ADAPTERS_ENGINE "
    "inventory=4 routing_adapters_ordinary_calls=0 rho_contrib=0 "
    "fourier_children=0 positive_rank=0 exhaust=64 reserve_indep=1 "
    "remaining=peeled+highpart A=0_cited B=2642_cited engine_measured "
    "no_new_kappa"
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
ENGINE_FILES = (
    "research/selected-complex-router-adapters-engine/router.py",
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
    need(tuple(row["path"] for row in inputs) == INPUTS + ENGINE_FILES,
         "input inventory")
    pinned = {}
    for row in inputs:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(len(raw) <= 4_000_000, "source size")
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source hash: " + row["path"])
        if row["path"].endswith(".py"):
            pinned[row["path"]] = raw
        else:
            pinned[row["path"]] = raw.decode("utf-8")
    return pinned


def inventory_from_proof(proof: str) -> list[str]:
    need(
        "Ordinary peeled" in proof
        and "routing, adapters and high-part exchanges are separate completed calls"
        in proof,
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
    need(
        "B = 2642" in a_zero or "B_bits = 2642" in a_zero or "B_bits=2642" in a_zero,
        "cite: B_bits from A=0 package",
    )
    need("B = 2628 + 14 = 2642" in envelope, "cite: prior B decomposition")
    need("rho" in a_zero and ("unbound" in a_zero or "stays unbound" in a_zero),
         "cite: rho still open after A=0")

    # Complex cover operation class (cited; engine measures costs).
    need("rank-zero adapter" in cover_cx.replace("\n", " "),
         "cite: rank-zero adapter")
    need("no positive-rank data connectors" in cover_cx.replace("\n", " "),
         "cite: no positive-rank connectors")
    need("finite scalar/router guard" in cover_cx, "cite: scalar/router guard")
    need("without recursive Fourier children" in cover_cx,
         "cite: no recursive Fourier children")
    need(
        "fixed address adapters, endpoint Paulis and invocation permutations"
        in cover_cx,
        "cite: adapter inventory",
    )

    # BIT contrast: ordinary width-O(w) routing remains ordinary (not this class).
    compact_bit = cover_bit.replace(" ", "").replace("\n", "")
    need(
        "constantnumberofoldwidth-$O(w)$interchanges" in compact_bit
        or "constant number of old width-$O(w)$ interchanges" in cover_bit,
        "cite: BIT ordinary routing",
    )
    need(routing_factor.get("named_factor") is False, "BIT c_R unexpectedly named")
    need(
        "One inherited ordinary width-$k$ interchange of the two high parts"
        in cover_rows,
        "cite: high-part remains ordinary",
    )

    # --- Engine measurement (not phrase-assigned zeros) ---
    cases = router.exhaust_small(m=3, parent_reserve_extent=1)
    need(cases == 64, "exhaustive domain size")
    indep = router.reserve_independence(m=4)
    need(indep["extent_1"]["rho_contrib"] == 0, "engine rho_contrib")
    need(indep["extent_1"]["ordinary_leaf_calls"] == 0, "engine ordinary calls")
    need(indep["extent_1"]["recursive_fourier_children"] == 0, "engine fourier")
    need(indep["extent_1"]["positive_rank_connectors"] == 0, "engine positive-rank")
    need(indep["extent_1"]["parent_reserve_active_reads"] == 0, "engine reserve")
    need(indep["extent_1"]["rank_zero_adapters"] == 2, "two rank-zero adapters")
    need(indep["extent_1"]["scalar_shears"] == 3, "three scalar shears")

    # Mutant controls: each injected ordinary/Fourier/positive-rank/reserve path
    # is measured as nonzero and rejected as outside the discharged class.
    base = router.run_router_adapters([1, 0, 1, 0], [0, 1, 0, 1])
    need(base["rho_contrib"] == 0, "clean residual")

    ordinary = router.run_router_adapters(
        [1, 0, 1, 0], [0, 1, 0, 1], mutate="ordinary"
    )
    need(ordinary["ordinary_leaf_calls"] == 1, "ordinary mutant measured")
    need(ordinary["rho_contrib"] == 1, "ordinary mutant charges rho")

    fourier = router.run_router_adapters(
        [1, 0, 1, 0], [0, 1, 0, 1], mutate="fourier"
    )
    need(fourier["recursive_fourier_children"] == 1, "fourier mutant measured")
    need(fourier["rho_contrib"] == 1, "fourier mutant charges rho")

    pos = router.run_router_adapters(
        [1, 0, 1, 0], [0, 1, 0, 1], mutate="positive_rank"
    )
    need(pos["positive_rank_connectors"] == 1, "positive-rank mutant measured")

    touch = router.run_router_adapters(
        [1, 0, 1, 0], [0, 1, 0, 1], mutate="touch_reserve"
    )
    need(touch["parent_reserve_active_reads"] == 1, "reserve mutant measured")
    need(touch["rho_contrib"] == 1, "reserve mutant charges rho")

    # Control: complex cover must not carry BIT ordinary routing phrase.
    need(
        "constant number of old width-$O(w)$ interchanges" not in cover_cx,
        "control: complex cover must not carry BIT ordinary routing phrase",
    )

    remaining = [name for name in inventory if name not in ("routing", "adapters")]
    need(remaining == list(REMAINING), "remaining ordinary classes")

    result = {
        "schema_version": 1,
        "status": "PASS_SELECTED_COMPLEX_ROUTER_ADAPTERS_ENGINE",
        "producer": "selected-complex-m73",
        "leaf_inventory": list(LEAF_INVENTORY),
        "routing_adapters_charge": "finite_scalar_router_engine",
        "measurement": "executable_scalar_router_residual",
        "routing_adapters_ordinary_leaf_calls": 0,
        "routing_adapters_recursive_fourier_children": 0,
        "routing_adapters_positive_rank_connectors": 0,
        "routing_adapters_rho_contribution": 0,
        "exhaustive_cases_m3": cases,
        "reserve_independence": True,
        "rank_zero_adapters_per_call": 2,
        "scalar_shears_per_call": 3,
        "bit_routing_ordinary_interchanges": "constant_unnamed_c_R",
        "remaining_ordinary_leaf_classes": list(REMAINING),
        "global_rho": "open_pending_peeled_highpart",
        "A_cited": A_CITED,
        "B_bits_cited": B_BITS_CITED,
        "composition_after_discharge": "(43/26)*(1-s)*2642 + rho_peeled_highpart",
        "controls_rejected": [
            "ordinary_leaf_injection",
            "recursive_fourier_injection",
            "positive_rank_connector",
            "parent_reserve_active_read",
        ],
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
