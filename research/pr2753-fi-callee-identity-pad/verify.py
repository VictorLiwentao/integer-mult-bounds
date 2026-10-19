#!/usr/bin/env python3
"""Bind identity-weight PR2753 Node+padding to wrapper F_I; fitted t>1 metadata.

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

F_I_NEEDLES_PLAIN = (
    "unweighted",
    "F_I(H,D)=(C D,C H)",
    "weighted reversed call is not a substitute",
    "R'=ceil(R/S)*S",
)
LCM_OQ_NEEDLES = (
    "Its callee is not.",
    "actual unweighted incoming program",
    "`F_I` this wrapper calls",
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
    wrapper = (
        REPO / "research/selected-outer-borrowing-wrapper/README.md"
    ).read_text(encoding="utf-8")
    for needle in F_I_NEEDLES_PLAIN:
        need(needle in wrapper, "wrapper F_I contract: " + needle)
    lcm = (REPO / "research/selected-lcm-stock-wrapper-fit/README.md").read_text(
        encoding="utf-8"
    )
    for needle in LCM_OQ_NEEDLES:
        need(needle in lcm, "lcm OQ callee: " + needle)
    integration = (
        REPO / "research/selected-compatible-row-padding/integration_check.py"
    ).read_text(encoding="utf-8")
    need(
        "Incoming(context, indices, (2, 1))" in integration,
        "published integration uses weighted (2,1)",
    )
    need("2 * t1" in integration, "published destination is weighted")


def build_receipt():
    check_contracts()
    # Algebraic oracle: published weighted destination is not F_I.
    weighted_fi_bad = harness.weighted_oracle_fi_mismatches(harness.GENUINE_ROWS)
    need(weighted_fi_bad == 3528, "weighted oracle F_I mismatches")

    # Identity-weight Node under padding equals F_I.
    fi_bad, wt_bad, padded, added, children = harness.run_padded_node(
        harness.IDENTITY, harness.GENUINE_ROWS, harness.STOCK
    )
    need(fi_bad == 0, "identity Node matches F_I")
    need(wt_bad == 0, "identity Node matches its own weight destination")
    need(padded == 96 and added == 47, "published 49→96 padding plan")
    need(
        children.get("enter") == children.get("return") == 816,
        "completed child returns",
    )

    # Fitted multiplicity t=2: R=t·S exact, still F_I, added=0.
    fi2, wt2, padded2, added2, children2 = harness.run_padded_node(
        harness.IDENTITY, harness.T2_ROWS, harness.STOCK
    )
    need(fi2 == 0, "t=2 identity Node matches F_I")
    need(padded2 == harness.T2_ROWS and added2 == 0, "t=2 exact stock multiple")
    need(
        children2.get("enter") == children2.get("return") == 816,
        "t=2 completed child returns",
    )

    census, peak = harness.plan_rows_census(stock=4, t_max=16)
    need(peak == 2, "plan_rows Counter peak")
    need(all(row["added"] == 0 for row in census), "exact multiples add nothing")
    need(all(row["counter_peak"] == 2 for row in census), "peak independent of t")

    return {
        "claim": "identity-weight PR2753 Node+padding equals wrapper F_I; fitted t>1 metadata peak independent of t",
        "fixture": "one-family GL2(F3) two-MOVE model, not selected GL64",
        "identity_weights": list(harness.IDENTITY),
        "weighted_control": list(harness.WEIGHTED),
        "genuine_rows": harness.GENUINE_ROWS,
        "stock": harness.STOCK,
        "body": harness.BODY,
        "compatible_rows_t1": 96,
        "added_t1": 47,
        "fi_mismatches_identity_t1": fi_bad,
        "fi_mismatches_weighted_oracle": weighted_fi_bad,
        "multiplicity_t2_rows": harness.T2_ROWS,
        "added_t2": added2,
        "fi_mismatches_identity_t2": fi2,
        "children_enter_return": 816,
        "plan_rows_t_max": 16,
        "plan_rows_counter_peak": peak,
        "plan_rows_peak_independent_of_t": True,
        "no_new_kappa": True,
        "kappa_unchanged": "0.001672660197076918",
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate CERTIFICATE.json (explicit write only)",
    )
    args = parser.parse_args(argv)

    sources_digest = check_sources()
    receipt = build_receipt()
    receipt["sources_sha256"] = sources_digest
    receipt["checks"] = CHECKS
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    reject_duplicate_keys(text)
    path = ROOT / "CERTIFICATE.json"
    if args.write:
        path.write_text(text, encoding="utf-8")
    else:
        need(path.is_file(), "committed certificate present")
        committed = path.read_text(encoding="utf-8")
        reject_duplicate_keys(committed)
        need(committed == text, "certificate drift")
        # On-disk corruption rejection via temp compare already covered by equality.

    print(
        "PASS_PR2753_FI_CALLEE_IDENTITY_PAD "
        f"identity=F_I fi_bad=0 weighted_oracle_fi_bad={receipt['fi_mismatches_weighted_oracle']} "
        f"t2_added=0 counter_peak={receipt['plan_rows_counter_peak']} "
        "no_new_kappa"
    )


if __name__ == "__main__":
    main()
