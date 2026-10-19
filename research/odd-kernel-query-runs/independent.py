#!/usr/bin/env python3
"""Independent closed-form checks for odd-kernel query runs. Apache-2.0.

Standalone of the primary checker. Rebuilds the run walk, tap set and count
formula from program.py and cross-checks CERTIFICATE.json.
Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKS = 0


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise RuntimeError(message)


def load():
    spec = importlib.util.spec_from_file_location("okqr", ROOT / "program.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def push(k):
    s = (1, 0, 1, -1, 0, -1)
    r = (1, 0, -1, -1, 0, 1)
    c = Fraction(k, 4)
    return tuple(
        tuple((Fraction(1) if i == j else Fraction(0)) + c * s[i] * r[j] for j in range(6))
        for i in range(6)
    )


def run_word(basis, word):
    state = list(map(Fraction, basis))
    for event in word:
        if event[0] == "child":
            _, first, last = event
            state[first], state[last] = state[last], state[first]
        else:
            _, target, diagonal, controls = event
            state[target] = diagonal * state[target] + sum(c * state[i] for i, c in controls)
    return tuple(state)


def main():
    prog = load()
    cert = json.loads((ROOT / "CERTIFICATE.json").read_text())
    need(cert["no_new_kappa"] is True, "no new kappa")
    need(cert["typed_cost_improvement_over_dyadic"] is False, "no typed gain")
    need(cert["selected_decimal"] == "0.001672660197076918", "decimal")
    need(cert["subset_cases_per_kernel"] == 63, "63 subsets")

    kernels = (1, 3, 5, 7, 9, 15)
    columns = 0
    for kernel in kernels:
        row = cert["per_kernel"][str(kernel)]
        need(row["seed55_batch_invoice"]["ordinary_children"] == 12, "seed children")
        need(row["seed55_baseline_invoice"]["ordinary_children"] == 15, "seed baseline")
        need(row["seed55_batch_invoice"]["aligned_xor_scans"] == 10, "seed xor")
        # Rebuild seed walk without verify.
        batch = prog.batch_program((0, 1, 2, 4, 5), kernel)
        need(prog.invoice(batch)["ordinary_children"] == 12, "rebuild children")
        taps = sorted(prog.tapped_powers(batch))
        need(taps == sorted(prog.required_powers((0, 1, 2, 4, 5), kernel)), "rebuild taps")
        for e in batch:
            if e[0] == "query":
                need(prog.is_q_dyadic(e[2], kernel), "edge")
        # Isolated vs consecutive: {0,2} has c=2 so children=2*2+2=6; {0,1} has c=1 so 5.
        need(prog.expected_counts((0, 2))["ordinary_children"] == 6, "isolated")
        need(prog.expected_counts((0, 1))["ordinary_children"] == 5, "adjacent")
        need(prog.induced_components((0, 2), kernel) == 2, "two components")
        need(prog.induced_components((0, 1), kernel) == 1, "one component")
        for k in (kernel, -kernel, 2 * kernel, -4 * kernel, 8 * kernel):
            word = prog.address_word(k)
            for col in range(6):
                basis = tuple(1 if i == col else 0 for i in range(6))
                need(run_word(basis, word) == tuple(push(k)[i][col] for i in range(6)), "col")
                columns += 1
            for m in (5, 7, 9, 15, 21, 25, 35):
                expect = m % 2 == 1 and gcd(m, kernel) == 1
                need(prog.modulus_admits(k, m) is expect, f"pattern k={k} m={m}")
                need(prog.modulus_admits_kernel(kernel, m) is expect, f"closed m={m}")

    print(
        "PASS_INDEPENDENT_ODD_KERNEL_QUERY_RUNS "
        f"kernels={list(kernels)} columns_checked={columns} "
        f"controls={CHECKS} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
