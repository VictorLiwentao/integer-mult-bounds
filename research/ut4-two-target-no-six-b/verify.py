#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier: no legal two-target UT4 word has n_b=6.

Exhausts GL2-minimal zero-sum six-call middle sequences with rank(X),rank(Y)>=2
and every side-zero a/c profile (unbounded outer length) on two active roles.
Reports zero abc=cba=I key pairs. Prepared by Wentao Li with substantial AI
assistance. Apache-2.0.
"""
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def repo_root():
    cur = HERE
    for _ in range(8):
        if (cur / "certificates" / "selected-result.json").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return HERE.parents[1]


ROOT = repo_root()

from core import (  # noqa: E402
    count_key_pairs,
    cross_coeffs,
    diag,
    key,
    key_cross,
    middle_sequences,
    need,
    ranks_XY,
    side_coeffs,
    side_tables,
    side_zero_keys,
)
BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
PASS = "PASS_UT4_TWO_TARGET_NO_NB6"
CERT_KEYS = (
    "schema_version",
    "status",
    "active_roles",
    "targets",
    "n_b",
    "canonical_zero_sum_middles",
    "rank_XY_at_least_2",
    "low_rank_excluded",
    "side_zero_key_joins",
    "keys_sum",
    "max_keys_per_middle",
    "key_pairs_abc_cba_I",
)


def read_json(path):
    def pairs(items):
        obj = {}
        for k, v in items:
            need(k not in obj, "duplicate JSON key: " + k)
            obj[k] = v
        return obj

    def bad(value):
        raise ValueError("noninteger/nonfinite JSON number: " + value)

    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_float=bad, parse_constant=bad)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_sources():
    pins = read_json(HERE / "SOURCES.json")
    need(pins["base_commit"] == BASE, "base pin")
    need(pins["schema_version"] == 1, "SOURCES schema")
    need(len(pins["files"]) >= 2, "source inventory")
    for row in pins["files"]:
        need(row["usage"] in ("input", "provenance"), "source role: " + row["path"])
        need(isinstance(row.get("git_blob"), str) and len(row["git_blob"]) >= 40, "git blob")
        need(isinstance(row.get("sha256"), str) and len(row["sha256"]) == 64, "sha256")
        # Optional live check when the checkout is present (skipped under isolated copies).
        if row["usage"] == "input" and (ROOT / row["path"]).is_file():
            data = (ROOT / row["path"]).read_bytes()
            need(sha256(data).hexdigest() == row["sha256"], "live input SHA256: " + row["path"])
            need(
                sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == row["git_blob"],
                "live input Git blob: " + row["path"],
            )


def worker(bt):
    keys, joins = side_zero_keys(bt)
    return joins, len(keys), count_key_pairs(keys)


def run_census():
    all_m = list(middle_sequences(6, True))
    good = [bt for bt in all_m if ranks_XY(bt)[0] >= 2 and ranks_XY(bt)[1] >= 2]
    need(len(all_m) == 5582, "canonical middle count")
    need(len(good) == 5400, "rank-filtered middle count")
    tot_join = tot_keys = tot_kp = 0
    max_keys = 0
    with ProcessPoolExecutor(max_workers=4) as pool:
        for joins, nk, kp in pool.map(worker, good, chunksize=20):
            tot_join += joins
            tot_keys += nk
            tot_kp += kp
            if nk > max_keys:
                max_keys = nk
    need(tot_kp == 0, "unexpected abc=cba=I key pair for n_b=6")
    return {
        "schema_version": 1,
        "status": "no_nb6_two_target_quotient",
        "active_roles": 2,
        "targets": 2,
        "n_b": 6,
        "canonical_zero_sum_middles": len(all_m),
        "rank_XY_at_least_2": len(good),
        "low_rank_excluded": len(all_m) - len(good),
        "side_zero_key_joins": tot_join,
        "keys_sum": tot_keys,
        "max_keys_per_middle": max_keys,
        "key_pairs_abc_cba_I": tot_kp,
    }


def check_certificate(cert, expected=None):
    expected = expected if expected is not None else read_json(HERE / "CERTIFICATE.json")
    for key_name in CERT_KEYS:
        need(key_name in expected and key_name in cert, "certificate field: " + key_name)
        need(cert[key_name] == expected[key_name], "certificate mismatch: " + key_name)


def check_controls():
    need(diag(2, 2) == 9, "I_2 pack")
    # Low-rank middle admits abc=cba=I keys; the rank filter excludes it.
    low = (1, 1, 1, 1, 1, 1)
    need(ranks_XY(low) == (1, 1), "low-rank diagnostic")
    keys_low, _ = side_zero_keys(low)
    need(count_key_pairs(keys_low) > 0, "search must find pairs on low-rank control")
    # Rank-adequate sample has no I-pairs; side/key formulas agree with directs.
    sample = None
    for bt in middle_sequences(6, True):
        if ranks_XY(bt) == (2, 2):
            sample = bt
            break
    need(sample is not None, "rank-2 middle exists")
    keys, _ = side_zero_keys(sample)
    need(count_key_pairs(keys) == 0, "sample rank-2 middle has no I-pairs")
    tab = side_tables(sample)
    probes = 0
    for p0 in range(16):
        for p1 in range(16):
            P = (p0, p1, 0, 0, 0, 0)
            v = tab[0][p0] ^ tab[1][p1] ^ tab[2][0] ^ tab[3][0] ^ tab[4][0] ^ tab[5][0]
            direct = side_coeffs(sample, P)
            packed = direct[0] | direct[1] << 4 | direct[2] << 8 | direct[3] << 12
            need(v == packed, "side_tables vs side_coeffs")
            probes += 1
    need(probes == 256, "side formula probes ran")
    P = (9, 0, 9, 0, 9, 0)
    Q = (0, 9, 0, 9, 0, 9)
    need(cross_coeffs(sample, P, Q) == key_cross(key(sample, P), key(sample, Q)),
         "cross vs key_cross")


def reject_corrupted_temporary_certificate():
    with tempfile.TemporaryDirectory(prefix="nb6-cert-") as directory:
        path = Path(directory) / "CERTIFICATE.json"
        path.write_text('{"status":"first","status":"second"}\n')
        try:
            read_json(path)
            raised = False
        except ValueError as exc:
            raised = True
            need("duplicate JSON key" in str(exc), "duplicate key message")
        need(raised, "duplicate JSON key must reject")
        # Plant a temporary certificate that claims a positive key-pair count.
        # Use a synthetic honest payload so this control still works when the
        # on-disk CERTIFICATE.json has itself been corrupted by fault tests.
        live = read_json(HERE / "CERTIFICATE.json")
        honest = {k: live[k] for k in CERT_KEYS}
        honest["key_pairs_abc_cba_I"] = 0
        fake = dict(honest)
        fake["key_pairs_abc_cba_I"] = 1
        path.write_text(json.dumps(fake, sort_keys=True) + "\n")
        corrupted = read_json(path)
        try:
            check_certificate(honest, expected=corrupted)
            raised = False
        except ValueError as exc:
            raised = True
            need("certificate mismatch" in str(exc), "corrupted certificate message")
        need(raised, "corrupted temporary certificate must reject")


def package_files():
    return {
        p.name: sha256(p.read_bytes()).hexdigest()
        for p in HERE.iterdir()
        if p.is_file() and p.suffix in {".py", ".json", ".md"}
    }


def main():
    need((HERE / "CERTIFICATE.json").is_file(), "certificate present")
    before = package_files()
    check_sources()
    reject_corrupted_temporary_certificate()
    check_controls()
    cert = run_census()
    check_certificate(cert)
    after = package_files()
    need(before == after, "verify must not mutate package files")
    print(PASS, "key_pairs=0", "middles=" + str(cert["rank_XY_at_least_2"]))
    print(canonical({k: cert[k] for k in CERT_KEYS}))


if __name__ == "__main__":
    main()
