#!/usr/bin/env python3
"""Independent recomputation of PR2298 §3 gap-g opcount bounds. Wentao Li + AI, Apache-2.0."""

from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"


def need(ok, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def load_json_reject_duplicates(path: Path):
    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r}")
            out[key] = value
        return out

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_hook)


def pair_cost(wi: int, wj: int) -> tuple[int, int]:
    """Return (interchanges, bit_moves) for one exchange of widths wi,wj (any gap)."""
    g = abs(wi - wj)
    return 1, g


def reversal_counts(widths: tuple[int, ...]) -> tuple[int, int, int]:
    d = len(widths)
    exchanges = d // 2
    inter = bit = 0
    for k in range(exchanges):
        a, b = pair_cost(widths[k], widths[d - 1 - k])
        inter += a
        bit += b
    return exchanges, inter, bit


def tensor_counts(widths: tuple[int, ...]) -> tuple[int, int, int]:
    d = len(widths)
    exchanges = 2 * max(d - 1, 0)
    inter = bit = 0
    live = list(widths)
    for i in range(d - 1):
        for _ in range(2):
            a, b = pair_cost(live[i], live[d - 1])
            inter += a
            bit += b
            live[i], live[d - 1] = live[d - 1], live[i]
    need(tuple(live) == widths, "independent tensor restore")
    return exchanges, inter, bit


def main():
    cert = load_json_reject_duplicates(CERT_PATH)
    short, long = cert["short_width"], cert["long_width"]
    max_d = cert["max_d"]
    gap = cert["gap"]
    need(gap == long - short and gap >= 2, "certificate gap")
    digests = {tuple(r["widths"]): r for r in cert["row_digests"]}
    count = 0
    for d in range(1, max_d + 1):
        for widths in product((short, long), repeat=d):
            count += 1
            row = digests[widths]
            re, ri, rb = reversal_counts(widths)
            te, ti, tb = tensor_counts(widths)
            need(row["rev"] == [re, ri, rb], f"reversal digest {widths}")
            need(row["ten"] == [te, ti, tb], f"tensor digest {widths}")
            need(re == d // 2, "rev bound")
            need(te == 2 * max(d - 1, 0), "tensor bound")
    need(count == cert["pattern_count"], "pattern count")
    # Closed form on unit pairs.
    for case in cert["unit_gap_pairs"]:
        wi, wj = case["widths"]
        inter, bits = pair_cost(wi, wj)
        need(case["interchanges"] == inter and case["bit_moves"] == bits, "unit")
    print(
        "PASS_INDEPENDENT_PR2298_SECTION3_GAP2_OPCOUNTS "
        f"patterns={count} max_d={max_d} gap={gap} "
        f"rev_bound=floor(d/2) tensor_bound=2(d-1) pair_invoice=1+g "
        "no_new_kappa"
    )


if __name__ == "__main__":
    main()
