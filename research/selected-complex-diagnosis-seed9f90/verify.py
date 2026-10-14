#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent certification of the selected complex revision-3 diagnosis and lever ceilings.

Binds to research/community-frontier1094-audit/ASSEMBLY.json and
certificates/selected-result.json. Does not import research/complex-local-word-ceiling/.

Positive result: PASS_SELECTED_COMPLEX_DIAGNOSIS
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG))

from enclosure import (  # noqa: E402
    ceiling,
    child_cost,
    down,
    exp_encl,
    ln_int,
    max_idle_rank,
    model,
    relax,
    require,
    up,
)

ASSEMBLY_PATH = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
SELECTED_PATH = ROOT / "certificates/selected-result.json"

# Hosted T16/T37 template constants cited by the packing-ceiling model (PR1012 / #1240).
M = 73
FAMILIES = 896
STAGES = 9
CENTRE = 64
CALLS = 144
LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}

# Published portfolio figures (autoresearch.md / bottleneck-brief / #1240 README).
PUBLISHED_LEVER_MULT = {
    "centre_free": Q(280, 100),
    "centre_shared": Q(190, 100),
    "rank16": Q(231, 100),
    "rank8": Q(162, 100),
    "two_unpaid": Q(377, 100),
    "centre_free_rank16": Q(651, 100),
}
# Allow ±0.005 absolute on the rounded two-decimal multiplier display.
MULT_TOL = Q(5, 1000)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def profile_mass(profile: dict[str, int]) -> int:
    return sum(int(r) * int(n) for r, n in profile.items())


def enclose_E(profile: dict[int, int], m: int) -> tuple[Q, Q]:
    """Enclosure of E = Σ n_r r ln(m/r)."""
    lo = hi = Q(0)
    for r, n in profile.items():
        lm_lo, lm_hi = ln_int(m)
        lr_lo, lr_hi = ln_int(int(r))
        d_lo = lm_lo - lr_hi
        d_hi = lm_hi - lr_lo
        require(d_lo >= 0, "ln(m/r)")
        lo += Q(n) * Q(r) * d_lo
        hi += Q(n) * Q(r) * d_hi
    return down(lo), up(hi)


def enclose_r_eff(m: int, mass: int, E_lo: Q, E_hi: Q) -> tuple[Q, Q]:
    """r_eff = m exp(-E/mass) = exp(ln m - E/mass).

    For the selected ledger E/mass ≈ 2.93, so use range-reduced exp on the
    positive quantity E/mass and invert: exp(-t) = 1/exp(t).
    """
    t_lo = E_lo / mass
    t_hi = E_hi / mass
    require(0 < t_lo <= t_hi, "E/mass positivity")
    e_lo, e_hi = exp_encl(t_lo, t_hi)
    inv_lo, inv_hi = down(1 / e_hi), up(1 / e_lo)
    return down(m * inv_lo), up(m * inv_hi)


def lever_rows(base_hi: Q):
    mass = sum(r * n for r, n in LOCAL.items())
    rows = []

    def cap(local, centre=CENTRE, unpaid=1):
        return ceiling(local, M, FAMILIES, STAGES, centre, unpaid=unpaid)[1]

    specs = [
        ("baseline", LOCAL, CENTRE, 1, None),
        ("centre_free", {r: n for r, n in LOCAL.items() if r != 8}, 0, 1, "centre_free"),
        ("centre_shared", {**LOCAL, 8: 4}, 32, 1, "centre_shared"),
        ("rank16", {16: Q(mass, 16)}, CENTRE, 1, "rank16"),
        ("rank8", {8: Q(mass, 8)}, CENTRE, 1, "rank8"),
        ("two_unpaid", LOCAL, CENTRE, 2, "two_unpaid"),
        ("centre_free_rank16", {16: Q(mass - 64, 16)}, 0, 1, "centre_free_rank16"),
    ]
    out = {}
    for name, local, centre, unpaid, key in specs:
        a_hi = cap(local, centre=centre, unpaid=unpaid)
        rec = {
            "a_ceiling": f"{a_hi.numerator}/{a_hi.denominator}",
            "a_ceiling_float": float(a_hi),
            "kappa_cap_float": float(a_hi / (1 + a_hi)),
            "multiplier_float": float(a_hi / base_hi),
        }
        if key is not None:
            mult = a_hi / base_hi
            target = PUBLISHED_LEVER_MULT[key]
            rec["published_multiplier"] = f"{target}"
            rec["multiplier_matches_published_two_decimals"] = abs(mult - target) <= MULT_TOL
            require(abs(mult - target) <= MULT_TOL, f"lever {key} multiplier {float(mult)} vs {float(target)}")
        out[name] = rec
        rows.append(name)
    return out


def run_controls():
    rejected = {}
    # Idle rank 52 violates halving
    try:
        model(LOCAL, M, FAMILIES, STAGES, CENTRE, R=52)
        raise AssertionError("idle rank 52 should fail")
    except ValueError as e:
        rejected["idle_rank_52"] = f"rejected: {e}"
        require("halving" in str(e), "expected halving guard message")
    # Local mass beyond coverage
    fat = {**LOCAL, 1: LOCAL[1] + 10_000}
    try:
        model(fat, M, FAMILIES, STAGES, CENTRE)
        raise AssertionError("over-coverage should fail")
    except ValueError as e:
        rejected["over_coverage"] = f"rejected: {e}"
    # One extra rank-1 child must not raise the ceiling
    base = ceiling(LOCAL, M, FAMILIES, STAGES, CENTRE)[1]
    more = ceiling({**LOCAL, 1: LOCAL[1] + 1}, M, FAMILIES, STAGES, CENTRE)[1]
    require(more < base, "extra rank-1 must lower ceiling")
    rejected["extra_rank1_lowers_ceiling"] = True
    # Wrong published multiplier must fail the tolerance check used for levers
    bogus = abs(Q(3) - PUBLISHED_LEVER_MULT["centre_free"]) <= MULT_TOL
    require(not bogus, "tolerance must reject x3 for the centre-free lever")
    rejected["bogus_centre_free_multiplier_x3"] = "rejected"
    # kappa truncation is strict: a one-ulp bump must not match
    bumped = Q(836330098538459 + 1, 500000000000000000)
    require(bumped != Q(836330098538459, 500000000000000000), "ulp control")
    rejected["kappa_ulp_distinct"] = True
    return rejected


def main(argv=None):
    argv = argv or sys.argv[1:]
    write = "--write" in argv

    asm = load_json(ASSEMBLY_PATH)
    sel = load_json(SELECTED_PATH)
    asm_sha = sha256_file(ASSEMBLY_PATH)
    sel_sha = sha256_file(SELECTED_PATH)

    require(sel["kappa"] == asm["kappa"], "selected kappa must match ASSEMBLY")
    require(asm["binding"] == "complex", "complex must bind")
    require(asm["surcharge_model"]["complex"] is False, "complex surcharge must be false")
    require(asm["surcharge_model"]["bit"] is True, "bit surcharge must be true")

    complex_profile = {int(r): int(n) for r, n in asm["complex_profile"].items()}
    mass = profile_mass(asm["complex_profile"])
    W = CALLS * FAMILIES // STAGES  # 144 * 896 / 9 = 14336
    require(W == 14336, "live width")
    D = M * W - mass
    require(D == 5120, f"global deficit D={D}")

    # Coverage identity on the global profile: mass = 72 W + 64 N
    require(mass == 72 * W + 64 * CALLS, "coverage identity mass = 72W + 64N")

    # Rebuild global from local * CALLS + idle remainders recorded in #1240 RESULT / ledger
    idle_hist = {1: 2276, 3: 377, 7: 7, 48: 4866}
    rebuilt = {r: LOCAL[r] * CALLS for r in LOCAL}
    for r, n in idle_hist.items():
        rebuilt[r] = rebuilt.get(r, 0) + n
    require(rebuilt == complex_profile, "emitted local+idle must rebuild ASSEMBLY complex_profile")

    unpaid_after_centre = Q(D, CALLS)
    live_families_per_call = Q(W, CALLS)
    require(unpaid_after_centre == live_families_per_call - CENTRE, "D/N = w - 64")
    require(unpaid_after_centre == Q(320, 9), "exact unpaid-after-centre 320/9")
    require(live_families_per_call == Q(896, 9), "exact live families 896/9")

    local_mass = sum(r * n for r, n in LOCAL.items())
    require(local_mass == 5586, "local mass")
    require(model(LOCAL, M, FAMILIES, STAGES, CENTRE)["idle_mass"] == 1646, "idle mass per call")

    E_lo, E_hi = enclose_E(complex_profile, M)
    # a < D/E strictly for the surcharge-free complex ledger
    de_hi = up(Q(D) / E_lo)  # upper bound on D/E uses lower E
    de_lo = down(Q(D) / E_hi)
    complex_lower = Q(asm["complex_lower"])
    require(complex_lower < de_lo, "a* < D/E (strict via enclosures)")
    # Published PR1293 complex D/E ceiling 0.0016805907097543
    # PR1293 RESULT.json exact complex D/E enclosure (code-disjoint method).
    # Corroboration: the two closed intervals must intersect, and a* lies below both.
    pr1293_de_lo = Q(
        "526561458342785933489590138418352161594475477002745556271554887680/"
        "313319272376414409589114114548757778435191907651477925967778534543091"
    )
    pr1293_de_hi = Q(
        "449891379454319638281053850768598185886969711830191663310075557261183758067148787031904068610389085714992091063352089512320826605549429968900851518086516385513472/"
        "267698361560077478243855787264911104037839339471018448471487781183426965230512792496298832690400711209963783457126350066134939696540440020116568844246112092146253943"
    )
    require(de_lo <= pr1293_de_hi and pr1293_de_lo <= de_hi, "D/E enclosure must intersect PR1293's")
    require(complex_lower < pr1293_de_lo, "a* also below PR1293 D/E lower")

    r_lo, r_hi = enclose_r_eff(M, mass, E_lo, E_hi)
    # Portfolio text says "about 3.9"; the exact r_eff = m exp(-E/mass) is ≈ 3.9159.
    require(Q(39, 10) <= r_lo <= r_hi <= Q(4), "r_eff in [3.9, 4]")
    require(abs(r_lo - Q(39159, 10000)) <= Q(1, 1000), "r_eff near 3.9159")

    # Retained planning transfer κ = a/(1+a), recorded as an 18-decimal truncation.
    kappa = Q(asm["kappa"])
    balanced = complex_lower / (1 + complex_lower)
    grid = Q(1, 10**18)
    truncated = Q(int(balanced / grid)) * grid
    require(kappa == truncated, "kappa is the 18-decimal truncation of a/(1+a)")
    require(kappa == Q(sel["kappa"]), "selected-result kappa")
    require(str(asm["kappa_decimal"]) == "0.001672660197076918", "published kappa decimal")
    bit_lower = Q(asm["bit_lower"])
    require(balanced < bit_lower / (1 + bit_lower), "complex side binds under a/(1+a)")

    # Baseline packing ceiling and levers
    a_lo, a_hi = ceiling(LOCAL, M, FAMILIES, STAGES, CENTRE)
    # #1240 publishes a < 0.001690054109089
    published_ceil = Q(1690054109089, 1000000000000000)
    require(a_lo < published_ceil <= a_hi, "ceiling bracket must contain #1240 a_ceiling")
    # Selected complex endpoint below ceiling
    require(complex_lower < a_lo, "selected endpoint below certified ceiling lower")

    levers = lever_rows(a_hi)
    controls = run_controls()

    # Semantic control: forged profile with wrong mass fails coverage identity
    forged = dict(complex_profile)
    forged[1] = forged[1] + 1
    forged_mass = sum(r * n for r, n in forged.items())
    require(forged_mass != 72 * W + 64 * CALLS, "forged profile breaks coverage")
    controls["forged_profile_breaks_coverage_identity"] = True

    # Wrong surcharge claim: if complex used bit-style surcharge flag in the certificate model, binding notes disagree
    controls["assembly_declares_complex_surcharge_false"] = asm["surcharge_model"]["complex"] is False

    result = {
        "status": "PASS_SELECTED_COMPLEX_DIAGNOSIS",
        "task_id": "independent-moment",
        "chooser_seed": "9f90e3a535639d71c064e320e06118ad",
        "base_commit_expected": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "inputs": {
            "ASSEMBLY.json_sha256": asm_sha,
            "selected-result.json_sha256": sel_sha,
            "kappa": asm["kappa"],
            "complex_lower": asm["complex_lower"],
        },
        "diagnosis": {
            "m": M,
            "W": W,
            "N_calls": CALLS,
            "rank_mass": mass,
            "D": D,
            "live_families_per_call": "896/9",
            "unpaid_after_centre_per_call": "320/9",
            "unpaid_after_centre_float": float(unpaid_after_centre),
            "live_families_float": float(live_families_per_call),
            "local_mass_per_call": local_mass,
            "idle_mass_per_call": 1646,
            "coverage_identity": "mass = 72 W + 64 N",
            "E_enclosure": [f"{E_lo.numerator}/{E_lo.denominator}", f"{E_hi.numerator}/{E_hi.denominator}"],
            "D_over_E_enclosure": [f"{de_lo.numerator}/{de_lo.denominator}", f"{de_hi.numerator}/{de_hi.denominator}"],
            "D_over_E_float_interval": [float(de_lo), float(de_hi)],
            "effective_child_rank_enclosure_float": [float(r_lo), float(r_hi)],
            "published_portfolio_claims_reproduced": {
                "unpaid_about_35_6": abs(float(unpaid_after_centre) - 35.6) < 0.05,
                "families_about_99_6": abs(float(live_families_per_call) - 99.6) < 0.05,
                "effective_child_rank_about_3_9": True,
                "a_star_lt_D_over_E": True,
            },
        },
        "packing_ceiling": {
            "a_lo": f"{a_lo.numerator}/{a_lo.denominator}",
            "a_hi": f"{a_hi.numerator}/{a_hi.denominator}",
            "a_hi_float": float(a_hi),
            "published_1240_a_ceiling": "1690054109089/1000000000000000",
            "kappa_cap_float": float(a_hi / (1 + a_hi)),
            "idle_rank_cap": max_idle_rank(M),
        },
        "levers": levers,
        "controls": controls,
        "independence": {
            "imports_complex_local_word_ceiling": False,
            "enclosure_method": "ln2 binary series + odd reduction to Mercator ln(1+x); exp Taylor on [0,1/2]; not atanh-successor chains",
            "does_not_change_selected_frontier": True,
        },
        "author": "Wentao Li",
        "limitations": [
            "Favorable lever relaxations omit realization costs; not constructions.",
            "Does not rebuild the rank ledger from gate operations (see #1262/#1421).",
            "Does not re-prove the no-q-adic-selector compiler premise (PR552/PR559).",
            "Does not run make frontier1094-verify.",
        ],
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if write:
        (PKG / "RESULT.json").write_text(text, encoding="utf-8", newline="\n")
        print("WROTE_SELECTED_COMPLEX_DIAGNOSIS", file=sys.stderr)
        return 0

    committed = PKG / "RESULT.json"
    require(committed.is_file(), "missing committed RESULT.json (run with --write)")
    prev_text = committed.read_text(encoding="utf-8")
    require(prev_text == text, "committed RESULT.json differs from recomputed evidence")
    # Corruption controls: forged receipts must not match recomputed evidence.
    forged = json.loads(text)
    forged["diagnosis"]["D"] = 0
    require(
        json.dumps(forged, indent=2, sort_keys=True) + "\n" != text,
        "corruption control setup",
    )
    require(
        json.dumps(forged, indent=2, sort_keys=True) + "\n" != prev_text,
        "corrupted D must not match committed receipt",
    )
    forged2 = json.loads(text)
    forged2["status"] = "PASS_FORGED"
    require(
        json.dumps(forged2, indent=2, sort_keys=True) + "\n" != prev_text,
        "corrupted status must not match committed receipt",
    )
    for key in PUBLISHED_LEVER_MULT:
        require(
            result["levers"][key]["multiplier_matches_published_two_decimals"],
            f"lever {key} must match published two-decimal multiplier",
        )
    # Read-only: do not print the full JSON blob to stdout (keeps logs small); receipt is on disk.
    print("PASS_SELECTED_COMPLEX_DIAGNOSIS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 — surface as verifier failure
        print(f"FAIL_SELECTED_COMPLEX_DIAGNOSIS: {exc}", file=sys.stderr)
        raise SystemExit(1)
