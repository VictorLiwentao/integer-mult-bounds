#!/usr/bin/env python3
"""Gate-operand guards after #3696: simple-support vs destination-absent.

Answers PR #3696 open question 1 under priority revision 6: does a
simple-support (or other) guard reject all dest-in-sources divergent cases
without rejecting agreeing dest-free lists?

Admission uses need() and remains active under python -O.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_GATE_OPERAND_DEST_ABSENT_GUARD "
    "dest_absent_rejects_divergent=3492 "
    "dest_absent_rejects_dest_free_agree=0 "
    "simple_rejects_divergent=3492 "
    "simple_rejects_dest_free_agree=3450 "
    "no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
PREDECESSOR_TIP = "0581402f978addb2eda5306fd124001486c76b08"
PREDECESSOR_PACKAGE = "research/gate-operand-export-parity"
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
INPUTS = (WORD, CHECKER, EXPORTER)
N = 6
MAX_LEN = 4
DEST_FREE_AGREE = 4686
DEST_IN_DISAGREE = 3492
DEST_IN_AGREE = 1152
SIMPLE_ACCEPT = 1236
SIMPLE_REJECT_DEST_FREE_AGREE = 3450


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


def sym_coeffs(d, srcs, n):
    basis = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    acc = [0] * n
    for s in srcs:
        acc = [a ^ b for a, b in zip(acc, basis[s])]
    return tuple(a ^ b for a, b in zip(basis[d], acc))


def exp_coeffs(d, srcs, n):
    cur = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for s in srcs:
        cur[d] = [a ^ b for a, b in zip(cur[d], cur[s])]
    return tuple(cur[d])


def simple_support(d, srcs):
    """Every listed register distinct: d and all source occurrences."""
    regs = [d] + list(srcs)
    return len(set(regs)) == len(regs)


def dest_absent(d, srcs):
    """Destination does not appear among sources."""
    return d not in srcs


def guard_census(n=N, max_len=MAX_LEN):
    dest_free_agree = 0
    dest_in_disagree = 0
    dest_in_agree = 0
    simple_accept = 0
    simple_accept_disagree = 0
    simple_reject_dest_free_agree = 0
    dest_absent_accept = 0
    dest_absent_accept_disagree = 0
    dest_absent_reject_dest_free_agree = 0
    simple_reject_dest_in_disagree = 0
    dest_absent_reject_dest_in_disagree = 0
    simple_reject_witness = None
    for length in range(0, max_len + 1):
        for srcs in itertools.product(range(n), repeat=length):
            for d in range(n):
                agree = sym_coeffs(d, srcs, n) == exp_coeffs(d, srcs, n)
                free = d not in srcs
                if free and agree:
                    dest_free_agree += 1
                if (not free) and (not agree):
                    dest_in_disagree += 1
                if (not free) and agree:
                    dest_in_agree += 1
                s_ok = simple_support(d, srcs)
                a_ok = dest_absent(d, srcs)
                if s_ok:
                    simple_accept += 1
                    if not agree:
                        simple_accept_disagree += 1
                if a_ok:
                    dest_absent_accept += 1
                    if not agree:
                        dest_absent_accept_disagree += 1
                if free and agree and not s_ok:
                    simple_reject_dest_free_agree += 1
                    if simple_reject_witness is None:
                        simple_reject_witness = [d, list(srcs)]
                if free and agree and not a_ok:
                    dest_absent_reject_dest_free_agree += 1
                if (not free) and (not agree) and not s_ok:
                    simple_reject_dest_in_disagree += 1
                if (not free) and (not agree) and not a_ok:
                    dest_absent_reject_dest_in_disagree += 1
    return {
        "dest_free_agree": dest_free_agree,
        "dest_in_disagree": dest_in_disagree,
        "dest_in_agree": dest_in_agree,
        "simple_accept": simple_accept,
        "simple_accept_disagree": simple_accept_disagree,
        "simple_reject_dest_free_agree": simple_reject_dest_free_agree,
        "dest_absent_accept": dest_absent_accept,
        "dest_absent_accept_disagree": dest_absent_accept_disagree,
        "dest_absent_reject_dest_free_agree": dest_absent_reject_dest_free_agree,
        "simple_reject_dest_in_disagree": simple_reject_dest_in_disagree,
        "dest_absent_reject_dest_in_disagree": dest_absent_reject_dest_in_disagree,
        "simple_reject_witness": simple_reject_witness,
    }


def named_controls():
    """Named patterns relative to #3696 witnesses and the new simple-reject witness."""
    cases = {
        "self_even": (0, [0, 0]),
        "dest_with_src": (0, [1, 0]),
        "dup_src": (0, [1, 1]),
        "self_once": (0, [0]),
        "dest_free_ok": (0, [1, 2]),
        "simple_rejects_agreeing_dest_free": (1, [0, 0]),
    }
    out = {}
    for name, (d, srcs) in cases.items():
        agree = sym_coeffs(d, srcs, 3) == exp_coeffs(d, srcs, 3)
        out[name] = {
            "d": d,
            "srcs": srcs,
            "agree": agree,
            "simple_accept": simple_support(d, srcs),
            "dest_absent_accept": dest_absent(d, srcs),
        }
    need(out["self_even"]["agree"] is False, "self_even diverges")
    need(out["dest_with_src"]["agree"] is False, "dest_with_src diverges")
    need(out["dup_src"]["agree"] is True, "dup_src agrees")
    need(out["dup_src"]["dest_absent_accept"] is True, "dup_src dest-absent")
    need(out["dup_src"]["simple_accept"] is False, "dup_src fails simple")
    need(out["self_once"]["agree"] is True, "self_once agrees")
    need(out["self_once"]["dest_absent_accept"] is False, "self_once dest-in")
    need(out["dest_free_ok"]["simple_accept"] is True, "ok simple")
    need(out["dest_free_ok"]["dest_absent_accept"] is True, "ok dest-absent")
    need(out["simple_rejects_agreeing_dest_free"]["agree"] is True, "witness agrees")
    need(out["simple_rejects_agreeing_dest_free"]["simple_accept"] is False,
         "witness fails simple")
    need(out["simple_rejects_agreeing_dest_free"]["dest_absent_accept"] is True,
         "witness dest-absent")
    # Both guards reject the two #3696 divergent witnesses.
    for name in ("self_even", "dest_with_src"):
        need(out[name]["simple_accept"] is False, name + " simple")
        need(out[name]["dest_absent_accept"] is False, name + " dest-absent")
    return out


def bind_predecessor_and_boundary(pinned):
    """Cite #3696 tip + checker/exporter lines without reprinting its census claim."""
    need(PREDECESSOR_TIP == "0581402f978addb2eda5306fd124001486c76b08",
         "predecessor tip pin")
    pred = ROOT / PREDECESSOR_PACKAGE / "CERTIFICATE.json"
    need(pred.is_file(), "predecessor certificate present on branch")
    prior = read_json(pred)
    need(prior["status"] == "PASS_GATE_OPERAND_EXPORT_PARITY", "predecessor status")
    need(prior["claim"]["dest_free_always_agree"] is True, "predecessor dest-free lemma")
    need(prior["claim"]["dest_in_can_disagree"] is True, "predecessor dest-in lemma")
    # Soft-overlap hygiene: this package must not treat predecessor census as its claim.
    need(prior["claim"]["small_domain"]["dest_free_agree"] == DEST_FREE_AGREE,
         "domain pin matches predecessor")
    checker = pinned[CHECKER].decode("utf-8")
    exporter = pinned[EXPORTER].decode("utf-8")
    need("len(set(regs)) == len(regs)" in checker, "cite: checker distinct operands")
    need("bad operands" in checker, "cite: checker bad-operands message")
    compact = exporter.replace(" ", "")
    need("forsinsrcs:rec.append((1,d,s,1,f,ph))" in compact,
         "cite: exporter one ADD per source occurrence")


def selected_word_positive_control(pinned):
    """Selected gates already satisfy both guards; not a new selected-word defect."""
    import gzip

    word = json.loads(gzip.decompress(pinned[WORD]), object_pairs_hook=pairs_unique)
    total = 0
    both = 0
    for name in ("D", "A", "B", "C"):
        for _f, d, srcs in word[name]:
            total += 1
            if simple_support(d, srcs) and dest_absent(d, srcs):
                both += 1
    need(total == both, "selected gates already pass both guards")
    need(total == 5472, "selected gate count pin")
    return {"gates": total, "both_guards_accept": both}


def admit_certificate(certificate, write=False):
    path = HERE / "CERTIFICATE.json"
    if write:
        path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        return
    need(path.is_file(), "missing CERTIFICATE.json")
    committed = read_json(path)
    need(committed == certificate, "certificate mismatch")


def evaluate(write=False):
    pinned = pin_sources()
    bind_predecessor_and_boundary(pinned)
    census = guard_census()
    need(census["dest_free_agree"] == DEST_FREE_AGREE, "dest-free agree pin")
    need(census["dest_in_disagree"] == DEST_IN_DISAGREE, "dest-in disagree pin")
    need(census["dest_in_agree"] == DEST_IN_AGREE, "dest-in agree pin")
    need(census["simple_accept_disagree"] == 0, "simple never accepts disagree")
    need(census["dest_absent_accept_disagree"] == 0, "dest-absent never accepts disagree")
    need(census["simple_reject_dest_in_disagree"] == DEST_IN_DISAGREE,
         "simple rejects all divergent dest-in")
    need(census["dest_absent_reject_dest_in_disagree"] == DEST_IN_DISAGREE,
         "dest-absent rejects all divergent dest-in")
    need(census["dest_absent_reject_dest_free_agree"] == 0,
         "dest-absent preserves dest-free agree")
    need(census["simple_reject_dest_free_agree"] == SIMPLE_REJECT_DEST_FREE_AGREE,
         "simple rejects agreeing dest-free")
    need(census["simple_accept"] == SIMPLE_ACCEPT, "simple accept count")
    need(census["dest_absent_accept"] == DEST_FREE_AGREE, "dest-absent accept count")
    need(census["simple_reject_witness"] == [1, [0, 0]], "simple-reject witness")

    controls = named_controls()
    selected = selected_word_positive_control(pinned)

    selected_result = read_json(ROOT / "certificates/selected-result.json")
    need(selected_result.get("kappa") == "836330098538459/500000000000000000",
         "selected kappa fraction unchanged")

    certificate = {
        "schema_version": 1,
        "status": "PASS_GATE_OPERAND_DEST_ABSENT_GUARD",
        "kappa_decimal": KAPPA_DECIMAL,
        "predecessor": {
            "pr": 3696,
            "tip": PREDECESSOR_TIP,
            "package": PREDECESSOR_PACKAGE,
            "answers_oq": 1,
        },
        "claim": {
            "oq1_simple_support_preserves_dest_free_agree": False,
            "oq1_dest_absent_preserves_dest_free_agree": True,
            "both_reject_all_dest_in_divergent": True,
            "census": {
                "n": N,
                "max_len": MAX_LEN,
                "dest_free_agree": census["dest_free_agree"],
                "dest_in_disagree": census["dest_in_disagree"],
                "dest_in_agree": census["dest_in_agree"],
                "simple_accept": census["simple_accept"],
                "simple_reject_dest_free_agree": census["simple_reject_dest_free_agree"],
                "simple_reject_dest_in_disagree": census["simple_reject_dest_in_disagree"],
                "dest_absent_accept": census["dest_absent_accept"],
                "dest_absent_reject_dest_free_agree":
                    census["dest_absent_reject_dest_free_agree"],
                "dest_absent_reject_dest_in_disagree":
                    census["dest_absent_reject_dest_in_disagree"],
                "simple_reject_witness": census["simple_reject_witness"],
            },
            "named_controls": controls,
        },
        "selected_word_positive_control": selected,
        "no_new_kappa": True,
    }
    admit_certificate(certificate, write=write)
    return certificate


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate CERTIFICATE.json (explicit write path only)",
    )
    args = parser.parse_args(argv)
    certificate = evaluate(write=args.write)
    need(certificate["status"] == "PASS_GATE_OPERAND_DEST_ABSENT_GUARD", "status")
    print(MARKER)


if __name__ == "__main__":
    main()
