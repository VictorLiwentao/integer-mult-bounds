#!/usr/bin/env python3
"""Bind shape constant rho=0 for the selected m=73 complex leaf reserve.

Card selected-stock-envelope. Predecessor #3113 bound B_bits=2642 and left
A,B,rho unbound. In-flight selected-stock-shape-a-zero answers A=0; this
package does not reprint A or B. It proves that under the completed
ordinary-leaf interface already named for the complex parent formula,
S_leaf=1, so log_q S_leaf=0 and rho=0 satisfies the shape inequality.
No new kappa.

Admission uses need() and remains active under python -O.
"""

from __future__ import annotations

import hashlib
import json
import math
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
B_BITS_CITED = 2642
SHAPE_RHO = 0
S_LEAF = 1
KAPPA_DECIMAL = "0.001672660197076918"


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


def log_q_of_one(q: int) -> float:
    """Exact log_q(1) = 0 for every q > 1."""
    need(q > 1, "base q>1")
    return math.log(1, q)


def shape_rhs(rho: int, w: int, e: int) -> float:
    need(w >= 1 and e >= 1, "positive widths")
    return rho * w * (1.0 + math.log2(e))


def evaluate():
    texts = pin_sources()
    proof = texts["research/selected-coarse-depth-stock/PROOF.md"]
    coarse_readme = texts["research/selected-coarse-depth-stock/README.md"]
    prior = texts["research/selected-stock-envelope-m73/README.md"]
    bit_parent = texts["research/selected-bit-parent-reserve/README.md"]
    scope = texts["docs/research/selected-bootstrap-scope-map.md"]

    # Predecessor left rho unbound; cite, do not re-derive B or A.
    need("B = 2628 + 14 = 2642" in prior, "cite: prior B decomposition")
    need("missing_lemma=A_B_rho_unbound" in prior or "A, B and rho" in prior,
         "cite: prior left rho unbound")
    need("Bind `rho`" in prior, "cite: prior OQ bind rho")
    need("Actual A, B and rho are **not established here**" in proof,
         "cite: coarse left rho unbound")
    need("sigma <= (43/26)*(1-s)*(A+B) + rho" in proof, "cite: composition")

    # Complex parent formula names S_leaf and the S_leaf=1 permission.
    need("S_parent(e,w) = C(w)^D(n) * S_leaf(e,w)" in proof,
         "cite: parent = C^D * S_leaf")
    need(
        "If the full completed ordinary-leaf contract is available without an external"
        in proof,
        "cite: completed-leaf permission",
    )
    need("one may take S_leaf=1" in proof, "cite: S_leaf=1 permission")
    need(
        "log_qS_leaf(e,w)<=rho*w*(1+log2e)" in proof.replace(" ", ""),
        "cite: rho shape premise",
    )

    # Complex coarse leaves are ordinary completed calls.
    need("Ordinary peeled" in proof, "cite: ordinary peeled")
    need(
        "atoms, routing, adapters and high-part exchanges are separate completed calls."
        in proof,
        "cite: ordinary completed calls",
    )
    need(
        "Completed inner ordinary calls borrow" in proof,
        "cite: inner ordinary borrowing",
    )
    need(
        "Their internal stock remains in their completed contract" in proof,
        "cite: internal stock stays in leaf contract",
    )
    need(
        "Under a fully completed\nordinary-leaf contract the external leaf factor can be one"
        in coarse_readme
        or "external leaf factor can be one" in coarse_readme,
        "cite: README external factor one",
    )

    # Ordinary completed-leaf interface (hypothesis 4) that complex leaves invoke.
    need("Completed leaves." in bit_parent or "**Completed leaves.**" in bit_parent
         or "4. **Completed leaves.**" in bit_parent,
         "cite: BIT hypothesis 4")
    need("no additional externally supplied row factor" in bit_parent,
         "cite: zero external row factor")
    need(
        "At a leaf there is no external factor" in bit_parent,
        "cite: leaf has no external factor",
    )
    need(
        "If a leaf instead needs external factor `B>1`, the base case becomes `S_leaf=B`"
        in bit_parent,
        "cite: B>1 failure mode",
    )

    # 252 is ledger slack, not S_leaf / rho.
    need(
        "252 as\ninherited external slack rather than an ordinary-leaf reserve estimate"
        in proof
        or "inherited external slack rather than an ordinary-leaf reserve estimate"
        in proof,
        "cite: 252 is not leaf reserve",
    )
    need(
        "Neither historical m=120's\n57,604 nor external 252 slack is substituted"
        in proof
        or "external 252 slack is substituted" in proof,
        "cite: 252 not substituted for coefficients",
    )
    need(
        "historical 57,604 and 252 numbers do not" in coarse_readme,
        "cite: README rejects 252 as coefficient",
    )

    # Selected m=73 producer identification.
    need("The selected complex supplier has `m=73`" in scope,
         "cite: m=73 binding")
    need(
        "must not be identified with\nthat m=64 producer" in proof
        or "must not be identified with that m=64 producer" in proof.replace("\n", " "),
        "cite: complex/BIT distinction",
    )

    # Arithmetic: S_leaf=1 => log_q = 0 => rho=0 works.
    need(S_LEAF == 1, "S_leaf is one")
    need(SHAPE_RHO == 0, "rho is zero")
    need(B_BITS_CITED == 2642, "cited B_bits")
    for q in (2, 3, 5, 17, 521):
        need(log_q_of_one(q) == 0.0, "log_q(1)=0")
    probes = ((1, 1), (1, 2), (2, 8), (8, 64), (64, 73), (1024, 256))
    for e, w in probes:
        lhs = log_q_of_one(2)
        rhs = shape_rhs(SHAPE_RHO, w, e)
        need(lhs <= rhs, "shape inequality at e=%s w=%s" % (e, w))
        need(rhs == 0.0, "rhs zero at e=%s w=%s" % (e, w))

    # Composition consequence under cited A=0, B=2642, proved rho=0.
    collapsed = "(43/26)*(1-s)*2642"
    need(SHAPE_RHO == 0, "rho term vanishes")

    # Kappa unchanged.
    selected = read_json(ROOT / "certificates/selected-result.json")
    decimal = selected.get("decimal")
    need(decimal == KAPPA_DECIMAL or str(decimal) == KAPPA_DECIMAL,
         "kappa decimal pin")

    # Mutation / failure controls.
    need(log_q_of_one(2) == 0.0, "control: log(1) still zero")
    # External B>1 forces positive left-hand side; rho=0 fails.
    fake_leaf = 2
    need(math.log(fake_leaf, 2) > 0, "control: B>1 has positive log")
    need(
        not (math.log(fake_leaf, 2) <= shape_rhs(0, 1, 2)),
        "control: rho=0 rejected when S_leaf=B>1",
    )
    # Treating 252 as S_leaf would also reject rho=0.
    need(
        not (math.log(252, 2) <= shape_rhs(0, 1, 2)),
        "control: 252-as-S_leaf rejected under rho=0",
    )
    need(SHAPE_RHO + 1 != 0, "control: rho=1 not the claim")
    need(S_LEAF != 252, "control: S_leaf is not 252")

    return {
        "schema_version": 1,
        "status": "PASS_SELECTED_STOCK_SHAPE_RHO_ZERO",
        "producer": "selected-complex-m73",
        "shape_rho": SHAPE_RHO,
        "S_leaf": S_LEAF,
        "shape_B_bits_cited": B_BITS_CITED,
        "shape_A_cited": 0,
        "completed_ordinary_leaf_admission": True,
        "slack_252_is_not_S_leaf": True,
        "probes": [{"e": e, "w": w, "rhs": shape_rhs(SHAPE_RHO, w, e)}
                   for e, w in probes],
        "composition_under_rho_zero": collapsed,
        "no_new_kappa": True,
        "kappa_decimal": KAPPA_DECIMAL,
        "marker": MARKER,
    }


def admit(observed, certificate):
    need(observed["status"] == certificate["status"], "certificate mismatch")
    need(observed["shape_rho"] == certificate["shape_rho"],
         "certificate mismatch")
    need(observed["S_leaf"] == certificate["S_leaf"], "certificate mismatch")
    need(observed["marker"] == certificate["marker"], "certificate mismatch")
    need(observed["no_new_kappa"] is True, "certificate mismatch")
    need(observed["completed_ordinary_leaf_admission"] is True,
         "certificate mismatch")
    need(observed["slack_252_is_not_S_leaf"] is True, "certificate mismatch")


def main():
    observed = evaluate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    admit(observed, certificate)
    print(MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
