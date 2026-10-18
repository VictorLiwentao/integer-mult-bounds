#!/usr/bin/env python3
"""Second scanner. Imports neither verify.py, headstep.py nor the native checker.

Reads the hash-pinned witness and flag matching itself, finds flag 1's
delivering update with its own rational replay, and replays the zero-mass
least-frame model slot by slot with lowest-bit-pivot echelon frames (the other
scanner uses highest-bit pivots). It checks the four relocation scans, the
late-window verdicts, the hyperplane form of final(Y7), the four single-event
pins, the released-core control and every committed propagation chain, then
compares with CERTIFICATE.json. Read-only; checks survive python -O.
"""

import gzip
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WITNESS = ("research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
           "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e")
FLAGS = ("research/p104-joint-unit-flags/CERTIFICATE.json",
         "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128")
LATE = range(3366, 3613)
KAPPA = "0.001672660197076918"
MARKER = ("PASS_P104_FLAG1_PINNED_LATE_RELOCATION_INDEPENDENT flag=1 head=232 delivering_update=2797 "
          "relaxed_obstructed=868/1115 pinned_obstructed=1115/1115 late_pinned_obstructed=247/247 "
          "late_blocker=final(Y7) head_free_pinned_obstructed=458/1115 target_final=ker(61) "
          "single_core_pin_blocks_late=4/4 release_core_only_opens_late=247/247 chains=4 no_new_kappa")


def check(ok, what):
    if not ok:
        raise ValueError("independent: " + what)


def strict(pairs):
    seen = {}
    for k, v in pairs:
        check(k not in seen, "duplicate JSON key: " + k)
        seen[k] = v
    return seen


def read(root, rel, sha):
    raw = (root / rel).read_bytes()
    check(hashlib.sha256(raw).hexdigest() == sha, "pinned input changed: " + rel)
    return json.loads(gzip.decompress(raw) if rel.endswith(".gz") else raw, object_pairs_hook=strict)


def ech(vectors, into=()):
    """Echelon basis keyed by lowest set bit, fully reduced."""
    rows = dict(into)
    for x in vectors:
        for p, v in rows.items():
            if x >> p & 1:
                x ^= v
        if x:
            p = (x & -x).bit_length() - 1
            for q in list(rows):
                if rows[q] >> p & 1:
                    rows[q] ^= x
            rows[p] = x
    return rows


def frame(vectors):
    return tuple(sorted(ech(vectors).items()))


def meet_free(a, b):
    """Span of a and b."""
    if a == b:
        return a
    return tuple(sorted(ech([v for _, v in b], a).items()))


def inside(a, b):
    rows = dict(b)
    for _, x in a:
        for p, v in rows.items():
            if x >> p & 1:
                x ^= v
        if x:
            return False
    return True


def replay_least(witness, events, keep, forced, skip=-1):
    """Least frames for the event list; forced is the position of the moved ADD (or None) and the head."""
    L = {r: frame(f) for r, f in witness["initial_frames"].items()}
    fin = {r: frame(f) for r, f in witness["final_frames"].items()}
    bad = set()
    for pos, e in enumerate(events):
        if e[0] not in ("add", "copy") or pos == skip:
            continue
        a, b = e[1], e[2]
        if "C" in (a, b):
            if keep is None or (a, b) not in keep:
                continue
            r = a if b == "C" else b
            chart = frame(e[-1])
            if not inside(L[r], chart):
                bad.add("chart:" + r)
            L[r] = meet_free(L[r], chart)
            continue
        j = meet_free(L[a], L[b])
        if forced is not None and pos == forced[0] and forced[1] is not None:
            j = meet_free(j, frame([forced[1]]))
        L[a] = L[b] = j
    return L, sorted(r for r in fin if not inside(L[r], fin[r])) + sorted(bad)


def scan(witness, program, d, head, keep, slots):
    """Verdict for each requested slot label (published index the ADD follows), replayed from scratch."""
    e = program[d]
    rest = program[:d] + program[d + 1:]
    out = {}
    for after in slots:
        k = after + 1 if after < d else after
        word = rest[:k] + [e] + rest[k:]
        _, bad = replay_least(witness, word, keep, (k, head))
        out[after] = bad
    return out


def deliveries(witness, program, target, source):
    rows = {r: {r: Fraction(1)} for r in witness["initial_frames"]}
    found = []
    for i, e in enumerate(program):
        if e[0] == "zero":
            rows[e[1]] = {}
        elif e[0] == "erase":
            del rows[e[1]]
        elif e[0] == "copy":
            rows[e[1]] = dict(rows[e[2]])
        elif e[0] == "add":
            a = Fraction(e[3])
            if e[1] == target and rows[e[2]].get(source):
                found.append(i)
            for n, v in rows[e[2]].items():
                rows[e[1]][n] = rows[e[1]].get(n, Fraction(0)) + a * v
    return found


def main(root=ROOT):
    cert = json.loads((HERE / "CERTIFICATE.json").read_bytes(), object_pairs_hook=strict)
    witness = read(root, *WITNESS)
    flags = read(root, *FLAGS)
    h = flags["helpers"][1]
    head, source, target = h["basis"][0], "X%d" % h["source"], "Y%d" % h["target"]
    check((source, target, head) == ("X0", "Y7", 232), "flag 1 identity")
    program = witness["program"]
    found = deliveries(witness, program, target, source)
    check(found == [2797] and found == [cert["delivering_update"]], "single delivering update")
    d = found[0]
    partner = program[d][2]
    writes = [i for i, e in enumerate(program) if e[0] in ("add", "copy", "zero", "erase") and e[1] == partner]
    lo, hi = max(i for i in writes if i < d), min(i for i in writes if i > d)
    check([lo, hi] == [2497, 3613] and not [e for e in program if e[0] in ("add", "copy") and e[2] == target],
          "commutation window")
    labels = [k - 1 if k <= d else k for k in range(lo + 1, hi)]
    check(len(labels) == 1115, "slot count")
    private = [i for i, e in enumerate(program) if e[0] in ("add", "copy") and "C" in e[1:3]]
    check(private == cert["private_add_copy_events"] and max(private) < d, "private events")
    everything = {tuple(program[i][1:3]) for i in private}

    _, published = replay_least(witness, program, everything, None)
    check(published == [], "published word feasible with C pinned")

    rel = scan(witness, program, d, head, None, labels)
    pin = scan(witness, program, d, head, everything, labels)
    pin_free = scan(witness, program, d, None, everything, labels)
    rel_free = scan(witness, program, d, None, None, labels)
    late = list(LATE)
    check(sum(1 for v in rel.values() if v) == 868 and [s for s, v in rel.items() if not v] == late,
          "relaxed: exactly the 247 slots after 3366 are open")
    check(all(pin.values()) and all(pin[s] == [target] for s in late), "pinned: every slot closed, late by Y7 alone")
    check(sum(1 for v in pin_free.values() if v) == 458 and all(pin_free[s] == [target] for s in range(3184, 3613)),
          "pinned head-free: closed from 3184 by Y7")
    check(not any(rel_free.values()), "relaxed head-free window free")

    fin = frame(witness["final_frames"][target])
    ann = [w for w in range(1, 512) if all((w & v).bit_count() % 2 == 0 for _, v in fin)]
    check(len(fin) == 8 and ann == [61] == [cert["target_final_annihilator"]], "final(Y7) = ker(61)")

    core = cert["late_core"]["events"]
    check(core == [2480, 2482, 2504, 2511], "core list")
    for p in core:
        keep = {tuple(program[p][1:3])}
        v = scan(witness, program, d, head, keep, late)
        check(all(v[s] == [target] for s in late), "single pin %d blocks every late slot" % p)
        check(all((61 & x).bit_count() % 2 for x in program[p][-1]), "core chart %d odd" % p)
        ch = cert["late_core"]["single_event_pin"][str(p)]["propagation_chain_to_partner"]
        check(ch[0][0] == p and ch[-1][3] == partner and ch[-1][0] <= 3366, "chain %d endpoints" % p)
        for prev, nxt in zip(ch, ch[1:]):
            check(prev[0] < nxt[0] and set(prev[2:]) & set(nxt[2:]) - {"C"}, "chain %d links" % p)
        for step in ch:
            check(program[step[0]][:3] == step[1:], "chain %d event %d" % (p, step[0]))
            L, _ = replay_least(witness, program[:step[0] + 1], keep, None, d)
            moved = [r for r in step[2:] if r != "C"]
            check(all(not inside(L[r], fin) for r in moved), "chain %d leaves final(Y7) at %d" % (p, step[0]))
            before, _ = replay_least(witness, program[:step[0]], keep, None, d)
            check(any(inside(before[r], fin) for r in moved), "chain %d step %d is a first exit" % (p, step[0]))
    others = {tuple(program[i][1:3]) for i in private if i not in core}
    v = scan(witness, program, d, head, others, late)
    check(not any(v.values()), "pinning everything but the core leaves every late slot open")

    s = cert["scans"]
    check([(s[k]["slots"], s[k]["obstructed_slots"]) for k in
           ("relaxed_with_head", "pinned_with_head", "relaxed_head_free", "pinned_head_free")]
          == [(1115, 868), (1115, 1115), (1115, 0), (1115, 458)], "certificate scan counts")
    lw = cert["late_window"]
    check(lw["pinned_with_head"]["obstructed"] == lw["pinned_head_free"]["obstructed"] == 247
          and lw["relaxed_with_head"]["obstructed"] == 0, "certificate late window")
    check(all(cert["late_core"]["single_event_pin"][str(p)]["late_window"]["obstructed"] == 247 for p in core)
          and cert["late_core"]["pin_all_but_core"]["obstructed"] == 0, "certificate core verdicts")
    check(cert["selected_kappa"] == KAPPA and cert["no_new_kappa"] is True, "kappa unchanged")
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
