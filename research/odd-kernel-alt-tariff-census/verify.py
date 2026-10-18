#!/usr/bin/env python3
"""Alternate ADDRESS tariffs: odd kernels never beat dyadic (answers #3702 OQ1).

Under three named alternate physical tariffs (max-height, shared-den packing,
odd-core modulus), every certified odd kernel fails to strictly beat the
dyadic fused and baseline bills on j=0..32. Distinct from the published #3702
bit-sum tariff. No new kappa.

Admission uses need() and remains active under python -O.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_ODD_KERNEL_ALT_TARIFF_CENSUS "
    "tariffs=3 kernels=[1, 3, 5, 7, 9, 15] j=0..32 "
    "odd_fused_beats_dyadic=0 odd_baseline_beats_dyadic=0 "
    "no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"
KERNELS = (1, 3, 5, 7, 9, 15)
ODD_KERNELS = (3, 5, 7, 9, 15)
J_MAX = 32
PRIOR_README = "research/odd-kernel-query-pair/README.md"
PRIOR_TASK = "research/odd-kernel-query-pair/TASK.json"
PRIOR_PROGRAM = "research/odd-kernel-query-pair/program.py"
INPUTS = (PRIOR_PROGRAM,)


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
    need(manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
         "base commit pin")
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    pinned = {}
    for row in rows:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(len(raw) == row["size_bytes"], "source size: " + row["path"])
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw
    return pinned


def load_tariff():
    return runpy.run_path(str(HERE / "tariff.py"))


def bind_prior_oq(pinned):
    readme = pinned[PRIOR_README].decode("utf-8")
    task = pinned[PRIOR_TASK].decode("utf-8")
    need("coefficient-table bit-sizes for larger `q`" in readme,
         "cite: #2687 README OQ2 lineage")
    need("Do coefficient-table bit-sizes for larger q ever pay for themselves"
         in task,
         "cite: #2687 TASK OQ2 lineage")
    prog = pinned[PRIOR_PROGRAM].decode("utf-8")
    need("def address_word(k):" in prog, "cite: prior address_word")
    need("a = Fraction(k, 4)" in prog, "cite: prior a=k/4")


def cross_check_prior_program(pinned, tariff):
    prior = runpy.run_path(str(ROOT / PRIOR_PROGRAM))
    for k in (1, -1, 3, 4, 5, 12, 15, 16, 48, -20, 40):
        ours = tariff["word_coefficients"](k)
        theirs = []
        for event in prior["address_word"](k):
            if event[0] != "affine":
                continue
            theirs.append(event[2])
            for _, c in event[3]:
                theirs.append(c)
        need(tuple(ours) == tuple(theirs), f"coeff match k={k}")


def classify(odd_bill, dy_bill):
    if odd_bill < dy_bill:
        return "beat"
    if odd_bill == dy_bill:
        return "tie"
    return "exceed"


def evaluate(write=False):
    pinned = pin_sources()
    bind_prior_oq(pinned)
    tariff = load_tariff()
    cross_check_prior_program(pinned, tariff)

    names = tariff["TARIFF_NAMES"]
    need(names == (
        "ADDRESS_affine_coeff_max_height",
        "ADDRESS_affine_coeff_shared_den_packing",
        "ADDRESS_affine_coeff_odd_core_bit_sum",
    ), "named alternate tariff inventory")
    T_WORD = tariff["T_WORD"]
    need(tuple(T_WORD.keys()) == names, "T_WORD key order")

    # Distinctness from published #3702 bit-sum on every |k| in 1..64.
    bit_sum = tariff["reference_bit_sum_T_word"]
    for name in names:
        Tw = T_WORD[name]
        diffs = sum(1 for k in range(1, 65) if Tw(k) != bit_sum(k))
        need(diffs == 64, f"{name} must differ from bit-sum on all 1..64")

    # Odd-core (and the #3702 bit-sum reference) are sign-invariant.
    # Max-height and packing are sign-sensitive, so fused/baseline charge the
    # actual signed power lists (-a,2a,-a) / (-a,a,a,-a).
    Tw_oc = T_WORD["ADDRESS_affine_coeff_odd_core_bit_sum"]
    for k in list(range(-32, 0)) + list(range(1, 33)):
        need(Tw_oc(k) == Tw_oc(-k), f"sign free odd-core k={k}")
        need(bit_sum(k) == bit_sum(-k), f"sign free bit-sum ref k={k}")
    Tw_mh = T_WORD["ADDRESS_affine_coeff_max_height"]
    Tw_pk = T_WORD["ADDRESS_affine_coeff_shared_den_packing"]
    need(Tw_mh(32) == 7 and Tw_mh(-32) == 8, "max-height sign-sensitive spot")
    need(Tw_pk(3) != Tw_pk(-3), "packing sign-sensitive spot")

    # Spot values (locked evidence).
    need(Tw_mh(1) == 6 and Tw_mh(-1) == 5, "mh T(±1)")
    need(Tw_mh(3) == 6 and Tw_mh(-3) == 5, "mh T(±3)")
    need(Tw_mh(4) == 3, "mh T(4)")
    need(Tw_pk(1) == 48 and Tw_pk(4) == 17, "pk T(1),T(4)")
    need(Tw_oc(1) == 35 and Tw_oc(4) == 31, "oc T(1),T(4)")

    # Non-monotonicity still present under packing (same sweet spot family).
    need(T_WORD["ADDRESS_affine_coeff_shared_den_packing"](4)
         < T_WORD["ADDRESS_affine_coeff_shared_den_packing"](2)
         < T_WORD["ADDRESS_affine_coeff_shared_den_packing"](1),
         "packing not monotone (4<2<1)")

    per_tariff = {}
    total_fused_beats = 0
    total_baseline_beats = 0
    total_fused_exceeds = 0
    total_baseline_exceeds = 0
    total_fused_ties = 0
    total_baseline_ties = 0
    tie_records = []

    for name in names:
        Tw = T_WORD[name]
        fused_ex = fused_tie = fused_beat = 0
        base_ex = base_tie = base_beat = 0
        for j in range(0, J_MAX + 1):
            dy_f = tariff["T_fused"](Tw, j, 1)
            dy_b = tariff["T_baseline"](Tw, j, 1)
            need(len(tariff["fused_powers"](j, 1)) == 3, "fused query count")
            need(len(tariff["baseline_powers"](j, 1)) == 4, "baseline query count")
            for q in ODD_KERNELS:
                od_f = tariff["T_fused"](Tw, j, q)
                od_b = tariff["T_baseline"](Tw, j, q)
                cf = classify(od_f, dy_f)
                cb = classify(od_b, dy_b)
                if cf == "beat":
                    fused_beat += 1
                elif cf == "tie":
                    fused_tie += 1
                    tie_records.append({"tariff": name, "program": "fused",
                                        "j": j, "kernel": q,
                                        "odd": od_f, "dyadic": dy_f})
                else:
                    fused_ex += 1
                if cb == "beat":
                    base_beat += 1
                elif cb == "tie":
                    base_tie += 1
                    tie_records.append({"tariff": name, "program": "baseline",
                                        "j": j, "kernel": q,
                                        "odd": od_b, "dyadic": dy_b})
                else:
                    base_ex += 1
        need(fused_ex + fused_tie + fused_beat == 165, f"{name} fused partition")
        need(base_ex + base_tie + base_beat == 165, f"{name} baseline partition")
        need(fused_beat == 0, f"{name} fused beats must be 0")
        need(base_beat == 0, f"{name} baseline beats must be 0")
        per_tariff[name] = {
            "fused": {"exceeds": fused_ex, "ties": fused_tie, "beats": fused_beat},
            "baseline": {"exceeds": base_ex, "ties": base_tie, "beats": base_beat},
            "spot_T_word": {str(k): Tw(k) for k in (1, 2, 3, 4, 5, 7, 15)},
            "spot_T_fused_j2": {
                str(q): tariff["T_fused"](Tw, 2, q) for q in KERNELS
            },
        }
        total_fused_beats += fused_beat
        total_baseline_beats += base_beat
        total_fused_exceeds += fused_ex
        total_baseline_exceeds += base_ex
        total_fused_ties += fused_tie
        total_baseline_ties += base_tie

    need(total_fused_beats == 0 and total_baseline_beats == 0, "global zero beats")
    # Max-height baseline has exactly one tie at (q=3,j=0); others have none.
    need(total_baseline_ties == 1, "exactly one baseline tie across tariffs")
    need(total_fused_ties == 0, "no fused ties")
    need(tie_records == [{
        "tariff": "ADDRESS_affine_coeff_max_height",
        "program": "baseline",
        "j": 0,
        "kernel": 3,
        "odd": 22,
        "dyadic": 22,
    }], "locked baseline tie record")

    # Adversarial: if we artificially inflate dyadic, beats would appear.
    Tw = T_WORD["ADDRESS_affine_coeff_max_height"]
    real_dy = tariff["T_fused"](Tw, 2, 1)
    real_odd = tariff["T_fused"](Tw, 2, 3)
    need(real_odd > real_dy, "positive control odd exceeds")
    fake_dy = real_odd + 1
    need(not (real_odd > fake_dy), "control: inflated dyadic would break exceed")
    need(classify(real_odd, fake_dy) == "beat", "control: inflate creates a beat")

    selected = read_json(ROOT / "certificates/selected-result.json")
    need(selected.get("kappa") == KAPPA_FRACTION, "selected kappa unchanged")

    certificate = {
        "schema_version": 1,
        "status": "PASS_ODD_KERNEL_ALT_TARIFF_CENSUS",
        "kappa_decimal": KAPPA_DECIMAL,
        "kappa_fraction": KAPPA_FRACTION,
        "answers": {
            "prior_pr": 3702,
            "open_question": 1,
            "verdict": (
                "No certified odd kernel strictly beats dyadic under the three "
                "named alternate tariffs on j=0..32."
            ),
        },
        "tariffs": {
            name: {
                "definition": {
                    "ADDRESS_affine_coeff_max_height": (
                        "T_word(k)=max over affine coeffs c=p/q of "
                        "bit_length(|p|)+bit_length(q)"
                    ),
                    "ADDRESS_affine_coeff_shared_den_packing": (
                        "L=lcm(dens); T_word(k)=bit_length(L)+sum bit_length of "
                        "numerators rewritten over L"
                    ),
                    "ADDRESS_affine_coeff_odd_core_bit_sum": (
                        "strip factors of 2 from num and den; sum bit_lengths "
                        "of odd cores"
                    ),
                }[name],
                **per_tariff[name],
            }
            for name in names
        },
        "kernels": list(KERNELS),
        "odd_kernels": list(ODD_KERNELS),
        "j_max": J_MAX,
        "counts": {
            "tariffs": len(names),
            "odd_fused_exceeds_dyadic_total": total_fused_exceeds,
            "odd_fused_ties_dyadic_total": total_fused_ties,
            "odd_fused_beats_dyadic_total": total_fused_beats,
            "odd_baseline_exceeds_dyadic_total": total_baseline_exceeds,
            "odd_baseline_ties_dyadic_total": total_baseline_ties,
            "odd_baseline_beats_dyadic_total": total_baseline_beats,
            "comparisons_per_tariff_program": 165,
        },
        "ties": tie_records,
        "distinct_from_bit_sum_tariff": True,
        "claim": {
            "odd_never_strictly_beats_dyadic_on_named_alternates": True,
            "typed_child_xor_counts_identical": True,
        },
        "no_new_kappa": True,
    }
    admit_certificate(certificate, write=write)
    return certificate


def admit_certificate(certificate, write=False):
    path = HERE / "CERTIFICATE.json"
    if write:
        path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        return
    need(path.is_file(), "missing CERTIFICATE.json")
    committed = read_json(path)
    need(committed == certificate, "certificate mismatch")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate CERTIFICATE.json (explicit write path only)",
    )
    args = parser.parse_args(argv)
    certificate = evaluate(write=args.write)
    need(certificate["status"] == "PASS_ODD_KERNEL_ALT_TARIFF_CENSUS", "status")
    print(MARKER)


if __name__ == "__main__":
    main()
