#!/usr/bin/env python3
"""Independent closed-form checks: F_I algebra + plan_rows multiplicity metadata.

Does not execute the PR2753 Node. Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
import harness  # noqa: E402

CHECKS = 0


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise RuntimeError(message)


def main():
    # Local F_I formula equals runtime destination at identity weights on one body.
    with harness.install_predecessor():
        from check_runtime import destination as rt_destination

        for address in range(harness.BODY):
            need(
                harness.fi_destination(address)
                == rt_destination(address, 2, 3, harness.IDENTITY),
                "F_I closed form",
            )
            # Involutive: F_I^2 = id on the atom block with gap=suffix=1.
            mid = harness.fi_destination(address)
            need(harness.fi_destination(mid) == address, "F_I involution")

        # Weighted destination differs from F_I on a positive body set.
        body_diffs = sum(
            1
            for a in range(harness.BODY)
            if rt_destination(a, 2, 3, harness.WEIGHTED)
            != rt_destination(a, 2, 3, harness.IDENTITY)
        )
        need(body_diffs == 72, "weighted body differs from F_I")

    oracle = harness.weighted_oracle_fi_mismatches(harness.GENUINE_ROWS)
    need(oracle == 3528, "49*72 weighted F_I mismatches")

    census, peak = harness.plan_rows_census(stock=4, t_max=16)
    need(peak == 2, "Counter peak")
    need(all(row["added"] == 0 and row["padded"] == row["rows"] for row in census), "multiples")
    # Non-multiple control: rows = t*stock + r adds stock-r.
    with harness.install_predecessor():
        import padding
        from cardinal_counts import Count

        padded, added = padding.plan_rows(Count.literal(10), Count.literal(4))
        need(harness.decode_count(padded) == 12 and harness.decode_count(added) == 2, "partial group")
        padded.close()
        added.close()

    # Certificate agrees on the independent quantities.
    cert = json.loads((ROOT / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(cert["fi_mismatches_weighted_oracle"] == 3528, "cert oracle")
    need(cert["plan_rows_counter_peak"] == 2, "cert peak")
    need(cert["no_new_kappa"] is True, "no kappa claim")

    print(
        "PASS_INDEPENDENT_PR2753_FI_CALLEE_IDENTITY_PAD "
        f"body_diffs=72 oracle=3528 counter_peak={peak} no_new_kappa"
    )


if __name__ == "__main__":
    main()
