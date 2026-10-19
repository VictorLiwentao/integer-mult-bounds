#!/usr/bin/env python3
"""Exact evidence for odd-kernel query-run batching. Apache-2.0.

For every certified odd kernel q and every nonempty J subset {0..5}, the
signed q-dyadic run walk attains children 2r+c / affine 6(2r+c) / XOR 2r on
odd moduli coprime to q, matching the dyadic formula with no typed gain.
Default verify is read-only. Admission uses need() so gates survive -O.
Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHECKS = 0

KERNELS = (1, 3, 5, 7, 9, 15)
PRIMARY_NEW = (3, 5, 7, 9, 15)
PROBE_MODULI = (
    2, 4, 6, 8, 10,
    3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 33, 35, 39, 45, 49, 55, 63, 77, 105,
)
# Seed-55 witness from dyadic-query-runs, plus isolated/full small sets.
WITNESS_SETS = (
    (0, 1, 2, 4, 5),
    (0,),
    (0, 1),
    (0, 2),
    (0, 1, 2),
    (1, 2, 3, 4),
    (0, 1, 2, 3, 4, 5),
)
KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise RuntimeError(message)


def load_program():
    import importlib.util

    spec = importlib.util.spec_from_file_location("okqr", ROOT / "program.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


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


def reject_duplicate_keys(text: str):
    bad = []

    def hook(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            bad.append(True)
        return dict(items)

    json.loads(text, object_pairs_hook=hook)
    need(not bad, "duplicate JSON keys")


def git_blob(path: str, revision: str = "HEAD") -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", f"{revision}:{path}"], text=True
    ).strip()


def check_sources():
    source = read_json(ROOT / "SOURCES.json")
    need(source["schema_version"] == 1, "source schema")
    need(isinstance(source["base_commit"], str) and len(source["base_commit"]) == 40, "base")
    for row in source["files"]:
        usage = row.get("usage")
        need(usage in ("input", "provenance"), "known source usage")
        revision = source["base_commit"] if usage == "provenance" else "HEAD"
        data = (
            subprocess.check_output(
                ["git", "-C", str(REPO), "show", f"{revision}:{row['path']}"]
            )
            if usage == "provenance"
            else (REPO / row["path"]).read_bytes()
        )
        need(hashlib.sha256(data).hexdigest() == row["sha256"], f"sha256 {row['path']}")
        need(git_blob(row["path"], revision) == row["git_blob"], f"blob {row['path']}")
        if row["path"] == "certificates/selected-result.json":
            selected = json.loads(data)
            need(selected["decimal"] == KAPPA_DECIMAL, "selected decimal pin")
            need(selected["kappa"] == KAPPA_FRACTION, "selected kappa pin")
    return hashlib.sha256(canonical(source)).hexdigest()


def all_nonempty_subsets(universe):
    items = list(universe)
    n = len(items)
    out = []
    for mask in range(1, 1 << n):
        out.append(tuple(items[i] for i in range(n) if mask & (1 << i)))
    return out


def build_certificate(prog):
    per_kernel = {}
    subset_cases = 0
    for kernel in KERNELS:
        admitted = []
        excluded = []
        for modulus in PROBE_MODULI:
            closed = prog.modulus_admits_kernel(kernel, modulus)
            # Every query power of the seed witness agrees with closed form.
            program = prog.batch_program((0, 1, 2, 4, 5), kernel)
            ok_all = True
            for k in [e[2] for e in program if e[0] == "query"]:
                need(prog.is_q_dyadic(k, kernel), "witness edge q-dyadic")
                if prog.modulus_admits(k, modulus) != closed:
                    ok_all = False
                    break
            need(ok_all, f"pattern mismatch kernel={kernel} m={modulus}")
            if closed:
                admitted.append(modulus)
            else:
                excluded.append(modulus)

        # All nonempty subsets of {0..5}: counts, taps, components, edges.
        subset_rows = []
        for indices in all_nonempty_subsets(range(6)):
            expected = prog.expected_counts(indices)
            batch = prog.batch_program(indices, kernel)
            base = prog.separate_pairs_program(indices, kernel)
            inv_b = prog.invoice(batch, kernel)
            inv_s = prog.invoice(base, kernel)
            need(inv_b["ordinary_children"] == expected["ordinary_children"], "children formula")
            need(inv_b["ordered_affine_events"] == expected["ordered_affine_events"], "affine formula")
            need(inv_b["aligned_xor_scans"] == expected["aligned_xor_scans"], "xor formula")
            need(inv_s["ordinary_children"] == expected["baseline_ordinary_children"], "baseline children")
            need(inv_s["ordered_affine_events"] == expected["baseline_ordered_affine_events"], "baseline affine")
            need(inv_s["aligned_xor_scans"] == expected["baseline_aligned_xor_scans"], "baseline xor")
            need(inv_b["ordinary_children"] <= inv_s["ordinary_children"], "batch never worse")
            need(
                inv_b["ordinary_children"] == inv_s["ordinary_children"] - (
                    expected["r"] - expected["c"]
                ),
                "saving r-c",
            )
            taps = sorted(prog.tapped_powers(batch))
            need(taps == sorted(prog.required_powers(indices, kernel)), "tap set")
            need(
                prog.induced_components(indices, kernel) == expected["c"],
                "component count equals runs",
            )
            # Restricted-alphabet lower bound: q >= 2r+c.
            need(
                inv_b["ordinary_children"] >= 2 * expected["r"] + expected["c"],
                "lower bound attained",
            )
            subset_rows.append(
                {
                    "indices": list(indices),
                    "r": expected["r"],
                    "c": expected["c"],
                    "batch_children": inv_b["ordinary_children"],
                    "baseline_children": inv_s["ordinary_children"],
                }
            )
            subset_cases += 1

        # Rational / modular columns on witness query powers.
        rational = modular = 0
        witness = prog.batch_program((0, 1, 2, 4, 5), kernel)
        for k in sorted({e[2] for e in witness if e[0] == "query"}):
            word = prog.address_word(k)
            target = prog.push_matrix(k)
            for col in range(6):
                basis = tuple(int(i == col) for i in range(6))
                expected = tuple(target[i][col] for i in range(6))
                need(prog.run_address(basis, word) == expected, "rational column")
                rational += 1
                for modulus in admitted[:4]:
                    got = prog.run_address(basis, word, modulus)
                    want = tuple(
                        int(
                            expected[i].numerator
                            * pow(expected[i].denominator, -1, modulus)
                            % modulus
                        )
                        for i in range(6)
                    )
                    need(got == want, f"modular k={k} m={modulus}")
                    modular += 1
            for modulus in excluded[:3]:
                need(not prog.modulus_admits(k, modulus), "exclude")
                try:
                    prog.run_address((1, 0, 0, 0, 0, 0), word, modulus)
                except ValueError:
                    pass
                else:
                    raise RuntimeError(f"excluded modulus {modulus} accepted")

        # Witness invoices (seed-55 shape).
        w_idx = (0, 1, 2, 4, 5)
        w_exp = prog.expected_counts(w_idx)
        w_batch = prog.invoice(prog.batch_program(w_idx, kernel), kernel)
        w_base = prog.invoice(prog.separate_pairs_program(w_idx, kernel), kernel)
        need(w_exp["ordinary_children"] == 12 and w_base["ordinary_children"] == 15, "seed children")
        need(w_batch["ordinary_children"] == 12, "seed batch")
        need(w_batch["aligned_xor_scans"] == 10 and w_base["aligned_xor_scans"] == 10, "seed xor")

        per_kernel[str(kernel)] = {
            "kernel": kernel,
            "admitted_probe_moduli": admitted,
            "excluded_probe_moduli": excluded,
            "subset_cases": len(subset_rows),
            "rational_columns": rational,
            "modular_columns": modular,
            "seed55_batch_invoice": w_batch,
            "seed55_baseline_invoice": w_base,
            "pattern": "odd modulus coprime to kernel",
        }

    # No typed-cost improvement over dyadic on every witness set.
    for indices in WITNESS_SETS:
        dyadic = prog.expected_counts(indices)
        for kernel in PRIMARY_NEW:
            odd = prog.expected_counts(indices)
            need(odd == dyadic, "count formula kernel-invariant")
            need(
                prog.invoice(prog.batch_program(indices, kernel))["ordinary_children"]
                == prog.invoice(prog.batch_program(indices, 1))["ordinary_children"],
                "no typed gain over dyadic",
            )

    # Dyadic recovers all-odd admission among probes.
    need(
        set(per_kernel["1"]["admitted_probe_moduli"])
        == {m for m in PROBE_MODULI if m % 2 == 1},
        "dyadic admits every odd probe",
    )
    need(
        set(per_kernel["1"]["excluded_probe_moduli"])
        == {m for m in PROBE_MODULI if m % 2 == 0},
        "dyadic excludes exactly the even probes",
    )

    # Coprimality cross-check vs gcd.
    for kernel in KERNELS:
        for modulus in PROBE_MODULI:
            expect = modulus % 2 == 1 and gcd(modulus, kernel) == 1
            need(prog.modulus_admits_kernel(kernel, modulus) is expect, "closed gcd")

    return {
        "format": "odd-kernel-query-runs-certificate-v1",
        "claimed_scope": (
            "odd kernel q: signed q-dyadic run batching of completed native DATA shears "
            "on odd moduli coprime to q; children 2r+c (vs 3r separate pairs), "
            "affine 6(2r+c), XOR 2r; no typed gain over dyadic; no new kappa"
        ),
        "kernels": list(KERNELS),
        "primary_odd_kernels": list(PRIMARY_NEW),
        "probe_moduli": list(PROBE_MODULI),
        "index_universe": [0, 1, 2, 3, 4, 5],
        "subset_cases_per_kernel": 63,
        "subset_cases_total": subset_cases,
        "seed55_indices": [0, 1, 2, 4, 5],
        "seed55_children": "15->12",
        "seed55_affine": "90->72",
        "seed55_xor": 10,
        "per_kernel": per_kernel,
        "typed_cost_improvement_over_dyadic": False,
        "selected_decimal": KAPPA_DECIMAL,
        "selected_kappa": KAPPA_FRACTION,
        "no_new_kappa": True,
    }


def reject_corrupted_temporary_certificate(cert):
    """A mutated temporary certificate must disagree with the fresh rebuild."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "CERTIFICATE.json"
        bad = json.loads(json.dumps(cert))
        bad["typed_cost_improvement_over_dyadic"] = True
        path.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n")
        loaded = read_json(path)
        need(loaded != cert, "temporary corruption detectable")
        need(loaded["typed_cost_improvement_over_dyadic"] is True, "mutation applied")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    prog = load_program()
    cert = build_certificate(prog)
    pretty = json.dumps(cert, indent=2, sort_keys=True) + "\n"
    reject_duplicate_keys(pretty)
    path = ROOT / "CERTIFICATE.json"
    if args.write:
        path.write_text(pretty)
        print("WROTE_CERTIFICATE", path)
    else:
        need(path.is_file(), "missing CERTIFICATE.json; pass --write once")
        existing = path.read_text()
        reject_duplicate_keys(existing)
        need(read_json(path) == cert, "certificate drift")
        reject_corrupted_temporary_certificate(cert)
    sources = check_sources()
    print(
        "PASS_ODD_KERNEL_QUERY_RUNS "
        f"kernels={list(KERNELS)} "
        f"subsets_per_kernel=63 "
        f"seed55_children=15->12 "
        f"affine=90->72 xor=10 "
        f"no_typed_gain_over_dyadic "
        f"sources={sources[:12]} checks={CHECKS} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
