#!/usr/bin/env python3
"""Independent scanner: rebuild meters without importing verify.evaluate."""

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
    "PASS_SELECTED_COMPLEX_ROUTER_ADAPTERS_ENGINE_INDEPENDENT "
    "ordinary_calls=0 rho_contrib=0 fourier_children=0 "
    "exhaust=64 reserve_indep=1 remaining=peeled+highpart"
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
    return json.loads(raw, object_pairs_hook=pairs_unique)


def main():
    manifest = read_json(HERE / "SOURCES.json")
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"],
             "independent pin: " + row["path"])

    # Rebuild exhaustive + independence without calling verify.evaluate.
    cases = router.exhaust_small(m=3, parent_reserve_extent=1)
    need(cases == 64, "exhaustive")
    indep = router.reserve_independence(m=4)
    need(indep["extent_1"]["ordinary_leaf_calls"] == 0, "ordinary")
    need(indep["extent_1"]["recursive_fourier_children"] == 0, "fourier")
    need(indep["extent_1"]["rho_contrib"] == 0, "rho")
    need(indep["extent_1"]["parent_reserve_active_reads"] == 0, "reserve")

    # Closed-form check on a mixed Pauli/permutation case.
    F = router.permutation_matrix([2, 0, 3, 1])
    s = [1, 0, 1, 0]
    x = [1, 1, 0, 0]
    y = [0, 1, 1, 0]
    out = router.run_router_adapters(x, y, F=F, pauli_support=s)
    exp_x, exp_y = router.expected_endpoint(x, y, F, s)
    need(out["x"] == exp_x and out["y"] == exp_y, "closed form")

    # Mutants measured nonzero.
    need(router.run_router_adapters(x, y, mutate="ordinary")["ordinary_leaf_calls"] == 1,
         "ordinary mutant")
    need(router.run_router_adapters(x, y, mutate="fourier")["recursive_fourier_children"] == 1,
         "fourier mutant")

    cert = read_json(HERE / "CERTIFICATE.json")
    need(cert["routing_adapters_ordinary_leaf_calls"] == 0, "cert ordinary")
    need(cert["routing_adapters_rho_contribution"] == 0, "cert rho")
    need(cert["remaining_ordinary_leaf_classes"] == ["peeled", "high-part"],
         "cert remaining")
    need(cert["measurement"] == "executable_scalar_router_residual",
         "cert measurement")

    print(MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
