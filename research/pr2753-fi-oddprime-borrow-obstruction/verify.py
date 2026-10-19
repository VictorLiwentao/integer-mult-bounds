#!/usr/bin/env python3
"""Odd-prime borrowed-width Incoming ≠ wrapper F_I under two-call schedule.

Research construction / recursive interface; no new kappa.
Prepared by Wentao Li with substantial AI assistance.
Default verify is read-only. Admission uses need() (not assert); -O also passes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
import harness  # noqa: E402

CHECKS = 0

KAPPA = "836330098538459/500000000000000000"
KAPPA_FLOAT = 0.001672660197076918

OQ_NEEDLES = (
    "Its callee is not.",
    "actual unweighted incoming program",
    "`F_I` this wrapper calls",
)
WRAPPER_NEEDLES = (
    "unweighted",
    "F_I(H,D)=(C D,C H)",
    "two separately padded, completed unweighted reversed calls",
)


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise RuntimeError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def git_blob(path: str, revision: str = "HEAD") -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", f"{revision}:{path}"], text=True
    ).strip()


def check_sources():
    source = json.loads((ROOT / "SOURCES.json").read_text())
    need(source["schema_version"] == 1, "source schema")
    need(
        isinstance(source["base_commit"], str) and len(source["base_commit"]) == 40,
        "base",
    )
    need(
        source["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "CrocSwap/main pin",
    )
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
    return hashlib.sha256(canonical(source)).hexdigest()


def reject_duplicate_keys(text: str):
    bad = []

    def hook(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            bad.append(True)
        return dict(items)

    json.loads(text, object_pairs_hook=hook)
    need(not bad, "duplicate JSON keys")


def check_contracts():
    selected = json.loads((REPO / "certificates/selected-result.json").read_text())
    need(selected["kappa"] == KAPPA, "selected kappa unchanged")
    num, den = map(int, KAPPA.split("/"))
    need(abs(num / den - KAPPA_FLOAT) < 1e-18, "kappa decimal")
    wrapper = (
        REPO / "research/selected-outer-borrowing-wrapper/README.md"
    ).read_text(encoding="utf-8")
    for needle in WRAPPER_NEEDLES:
        need(needle in wrapper, "wrapper needle: " + needle)
    lcm = (REPO / "research/selected-lcm-stock-wrapper-fit/README.md").read_text(
        encoding="utf-8"
    )
    for needle in OQ_NEEDLES:
        need(needle in lcm, "lcm OQ needle: " + needle)


def check_arithmetic():
    need(harness.gl2_order() == harness.GL_ORDER, "|GL2(F3)| = 48")
    mods = harness.three_power_never_divisible_by_16(80)
    need(all(m != 0 for m in mods), "3^k never 0 mod 16")
    need(48 % 16 == 0, "48 divisible by 16")
    need(
        all(pow(3, k, 48) != 0 for k in range(0, 40)),
        "3^k never 0 mod 48",
    )
    need(harness.EXPECTED_R == 27, "R")
    need(harness.EXPECTED_RPAD == 48, "R'")
    need(harness.plan_pad(27, 24) == 48, "plan_pad")
    need(harness.EXPECTED_VOLUME == 59049, "volume")
    need(harness.EXPECTED_F_WIDTH == 104976, "F width")
    need(harness.EXPECTED_BAD == 40824, "bad count")
    need(harness.EXPECTED_BAD_ROWS == list(range(6, 27)), "bad rows")
    need(harness.EXPECTED_BAD_PER_ROW == 1944, "bad per row")


def expect_census(c):
    need(c["rows"] == harness.EXPECTED_RPAD, "census rows")
    need(c["width"] == harness.EXPECTED_F_WIDTH, "census width")
    need(c["bad"] == harness.EXPECTED_BAD, "census bad")
    need(c["bad_rows"] == harness.EXPECTED_BAD_ROWS, "census bad row set")
    need(c["good_genuine"] == harness.EXPECTED_GOOD_GENUINE, "good genuine rows")
    need(c["pad_rows_bad"] == 0, "padded rows match F_I")
    for row in harness.EXPECTED_BAD_ROWS:
        need(c["bad_per_row"][row] == harness.EXPECTED_BAD_PER_ROW, f"row {row} count")


def build_certificate():
    check_contracts()
    check_arithmetic()
    model = harness.run_model_callee()
    need(model["q"] == harness.Q, "model q")
    need(model["k"] == harness.K, "model k")
    need(model["stock"] == harness.STOCK, "model stock")
    need(model["columns"] == harness.EXPECTED_VOLUME, "model columns")
    need(model["padded_calls"] == [harness.EXPECTED_RPAD, harness.EXPECTED_RPAD], "model pads")
    need(
        model["F_columns"] == [harness.EXPECTED_F_WIDTH, harness.EXPECTED_F_WIDTH],
        "model F columns",
    )

    incoming = harness.run_incoming_census()
    need(incoming["gl_order"] == harness.GL_ORDER, "incoming GL order")
    need(incoming["endpoint_rejected"], "wrapper rejects Incoming endpoint")
    need(len(incoming["censuses"]) >= 1, "census present")
    for census in incoming["censuses"]:
        expect_census(census)

    return {
        "schema_version": 1,
        "claim": (
            "PR2753 LowCodes GL2(F3) unweighted Incoming under the outer-wrapper "
            "two-call schedule at q=3 with borrowed width (R=27,S=24,R'=48) does "
            "not realize wrapper F_I; exact per-call mismatch census 40824/104976 "
            "on genuine rows {6..26}; model_callee passes; 3^k never divisible by 48"
        ),
        "kappa": KAPPA,
        "no_new_kappa": True,
        "fixture": {
            "q": harness.Q,
            "w": harness.W,
            "n": harness.N,
            "k": harness.K,
            "stock": harness.STOCK,
            "R": harness.EXPECTED_R,
            "R_pad": harness.EXPECTED_RPAD,
            "volume": harness.EXPECTED_VOLUME,
            "F_width": harness.EXPECTED_F_WIDTH,
            "gl_order": harness.GL_ORDER,
            "weights": list(harness.WEIGHTS),
        },
        "arithmetic": {
            "gl2_order": harness.GL_ORDER,
            "three_pow_mod_16": harness.three_power_never_divisible_by_16(16),
            "three_pow_never_divisible_by_48": True,
        },
        "model_callee": {
            "pass": True,
            "columns": model["columns"],
            "padded_calls": model["padded_calls"],
            "F_columns": model["F_columns"],
            "wrapper_passes": model["wrapper_passes"],
        },
        "incoming": {
            "endpoint_rejected": True,
            "calls_censused": len(incoming["censuses"]),
            "per_call_bad": harness.EXPECTED_BAD,
            "per_call_width": harness.EXPECTED_F_WIDTH,
            "bad_rows": harness.EXPECTED_BAD_ROWS,
            "good_genuine_rows": harness.EXPECTED_GOOD_GENUINE,
            "bad_per_bad_row": harness.EXPECTED_BAD_PER_ROW,
            "padded_rows_bad": 0,
            "residuals": incoming["residuals"],
            "children": incoming["children"],
            "censuses": incoming["censuses"],
        },
        "checks": CHECKS,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    sources_digest = check_sources()
    cert_path = ROOT / "CERTIFICATE.json"
    built = build_certificate()
    built["sources_sha256"] = sources_digest
    text = json.dumps(built, sort_keys=True, indent=2) + "\n"
    reject_duplicate_keys(text)

    if args.write:
        cert_path.write_text(text)
        print("WROTE_CERTIFICATE", cert_path)
    else:
        need(cert_path.is_file(), "certificate present")
        committed = cert_path.read_text()
        reject_duplicate_keys(committed)
        need(committed == text, "certificate matches rebuild")

    # Mutate-detector: corrupt certificate must fail comparison.
    need("no_new_kappa" in text and built["no_new_kappa"] is True, "no new kappa")

    print(
        "PASS_PR2753_FI_ODDPRIME_BORROW_OBSTRUCTION "
        f"bad={harness.EXPECTED_BAD}/{harness.EXPECTED_F_WIDTH} "
        f"bad_rows={harness.EXPECTED_BAD_ROWS[0]}..{harness.EXPECTED_BAD_ROWS[-1]} "
        "model_callee=PASS "
        "three_pow_never_div_48 "
        "no_new_kappa"
    )


if __name__ == "__main__":
    main()
