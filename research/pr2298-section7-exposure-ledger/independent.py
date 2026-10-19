#!/usr/bin/env python3
"""Independent recomputation of the §7 exposure ledger closed forms."""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"

TAU = Fraction(99830289, 10**8)
EPSILON = Fraction(1, 40)
PUBLISHED = Fraction(6618729, 4 * 10**9)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=_hook)


def m(d: int) -> int:
    return 2 * (d // 2) + 2 * max(d - 1, 0)


def main() -> int:
    # Closed forms without importing ledger.py.
    for d in range(1, 9):
        need(m(d) <= 3 * d - 2, f"majorant d={d}")
    need(m(8) == 22 and (3 * 8 - 2) == 22, "d=8 sharpness")
    need(m(1) == 0, "d=1 empty")
    saving = (1 - TAU) * (1 - EPSILON)
    exponent = TAU + EPSILON * (1 - TAU)
    need(saving == PUBLISHED, "saving identity")
    need(saving == 1 - exponent, "saving vs exponent")
    cert = load_json_reject_duplicates(CERT_PATH)
    need(cert["model"]["section7_saving"] == str(saving), "cert saving")
    need(cert["model"]["section7_exponent"] == str(exponent), "cert exponent")
    need(cert["multipliers"]["8"]["M"] == 22, "cert M8")
    need(cert["pattern_count"] == 510, "cert patterns")
    need(cert["saving_matches_published"] is True, "cert flag")
    # Re-hash row digest contract: independent engine only checks presence.
    need(len(cert["row_digest_sha256"]) == 64, "digest hex")
    print(
        "PASS_INDEPENDENT_PR2298_SECTION7_EXPOSURE_LEDGER",
        "M8=22",
        f"saving={saving}",
        f"exponent={exponent}",
        "patterns=510",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
