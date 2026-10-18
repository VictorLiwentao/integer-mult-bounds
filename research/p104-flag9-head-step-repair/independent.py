#!/usr/bin/env python3
"""Second, separately written scanner for the flag-9 head-step repair bill.

Does not import verify.py, headstep.py, check_native.py or the compiler.
Frames are sorted reduced GF(2) bases; the repaired words are replayed with
exact rational rows and compared register by register with the published
word's final rows and frames. Both least-frame models (private register
relaxed, and private register pinned to its published charts) are replayed
from the window start for each relocation slot and from scratch for each
order-preserving update. New native recipes are checked directly with the
vendored independent interpreter. Admission uses need() and stays active
under python -O.
"""

import gzip
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = "research/p104-native-channel"
PINS = {
    f"{NATIVE}/inputs/LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    f"{NATIVE}/NATIVE-RECIPES.json.gz": "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    f"{NATIVE}/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "research/p104-joint-unit-flags/CERTIFICATE.json": "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
}
SRC, TGT, PARTNER, HEAD, DELIVERY = "X4", "Y23", "D28", 196, 3124
MARKER = (
    "PASS_P104_FLAG9_HEAD_STEP_REPAIR_INDEPENDENT flag=9 head=196 delivering_update=3124 "
    "R0 added_events=1 added_transports=1 added_rank_mass=2 R1 added_events=0 added_transports=0 "
    "added_rank_mass=2 rows_equal=280/280 zero_mass_order_preserving=0/9 "
    "zero_mass_relocation_obstructed_relaxed=941/1114 zero_mass_relocation_obstructed_pinned=1114/1114 "
    "no_new_kappa"
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def strict(pairs):
    seen = {}
    for k, v in pairs:
        need(k not in seen, "duplicate JSON key: " + str(k))
        seen[k] = v
    return seen


def read(root, rel, gz=False):
    raw = (root / rel).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[rel], "source hash: " + rel)
    return json.loads(gzip.decompress(raw) if gz else raw, object_pairs_hook=strict)


def basis(vectors):
    rows = []
    for v in vectors:
        for r in rows:
            if v ^ r < v:
                v ^= r
        if v:
            rows = [r ^ v if r ^ v < r else r for r in rows]
            rows.append(v)
            rows.sort(reverse=True)
    return tuple(rows)


def inside(a, b):
    return basis(b + a) == b


def splice(program, rows):
    out = list(program)
    prev = len(program)
    for a, b, r in sorted(((r["published_range"][0], r["published_range"][1], r) for r in rows), reverse=True):
        need(a < b <= prev, "disjoint splices")
        need(program[a:b] == r["published"], "splice binding at %d" % a)
        out[a:b] = [list(e) for e in r["events"]]
        prev = a
    return out


def replay(witness, program):
    rows = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
    frames = {n: basis(f) for n, f in witness["initial_frames"].items()}
    profile, mass, adds = {}, {}, 0
    for i, e in enumerate(program):
        op = e[0]
        if op == "transport":
            _, r, old, new, k = e
            a, b = basis(old), basis(new)
            need(frames[r] == a, "transport before-frame continuity at %d" % i)
            need(inside(a, b) or inside(b, a), "nested transport at %d" % i)
            need(k == abs(len(b) - len(a)) and k > 0, "paid rank equals frame gap at %d" % i)
            need(len(new) == len(b) and len(old) == len(a), "independent frame lists at %d" % i)
            frames[r] = b
            profile[k] = profile.get(k, 0) + 1
            mass[r] = mass.get(r, 0) + k
        elif op == "zero":
            need(e[1] not in frames, "fresh private")
            rows[e[1]] = {}
            frames[e[1]] = basis(e[2])
        elif op == "erase":
            need(frames[e[1]] == basis(e[2]), "erase chart")
            rows.pop(e[1])
            frames.pop(e[1])
        elif op == "copy":
            need(not rows[e[1]] and frames[e[1]] == frames[e[2]] == basis(e[3]), "copy chart")
            rows[e[1]] = dict(rows[e[2]])
        else:
            need(op == "add", "opcode")
            _, d, s, c, f = e
            need(d != s and frames[d] == frames[s] == basis(f), "common chart at %d" % i)
            adds += 1
            for n, v in rows[s].items():
                z = rows[d].get(n, Fraction(0)) + Fraction(c) * v
                if z:
                    rows[d][n] = z
                else:
                    rows[d].pop(n, None)
    for n, f in witness["final_frames"].items():
        need(frames[n] == basis(f), "final frame " + n)
    return rows, profile, mass, adds


def frame_when(witness, program, reg, t):
    cur = basis(witness["initial_frames"][reg])
    for e in program[:t]:
        if e[0] == "transport" and e[1] == reg:
            cur = basis(e[3])
    return cur


def carried_into_target(program, witness):
    rows = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
    carried = []
    for i, e in enumerate(program):
        if e[0] == "zero":
            rows[e[1]] = {}
        elif e[0] == "erase":
            rows.pop(e[1])
        elif e[0] == "copy":
            rows[e[1]] = dict(rows[e[2]])
        elif e[0] == "add":
            if e[1] == TGT and rows[e[2]].get(SRC):
                carried.append([i, e[2], str(Fraction(e[3]) * rows[e[2]][SRC])])
            for n, v in rows[e[2]].items():
                z = rows[e[1]].get(n, Fraction(0)) + Fraction(e[3]) * v
                if z:
                    rows[e[1]][n] = z
                else:
                    rows[e[1]].pop(n, None)
    return carried


class Lower:
    """Least monotone frames; pinned=True also binds partners to the private charts."""

    def __init__(self, witness, pinned):
        self.pinned = pinned
        self.lo0 = {n: basis(f) for n, f in witness["initial_frames"].items()}
        self.fin = {n: basis(f) for n, f in witness["final_frames"].items()}

    def feed(self, lo, bad, e, extra):
        if e[0] == "add" and "C" not in (e[1], e[2]):
            j = basis(lo[e[1]] + lo[e[2]] + extra)
            lo[e[1]] = lo[e[2]] = j
        elif self.pinned and e[0] in ("add", "copy"):
            r = e[2] if e[1] == "C" else e[1]
            chart = basis(e[-1])
            if not inside(lo[r], chart):
                bad.append(["private chart", r])
            lo[r] = basis(lo[r] + chart)

    def verdict(self, lo, bad):
        return bad + [["final", n] for n in sorted(self.fin) if not inside(lo[n], self.fin[n])]

    def whole(self, program, forced):
        lo, bad = dict(self.lo0), []
        for i, e in enumerate(program):
            self.feed(lo, bad, e, (HEAD,) if i == forced else ())
        return self.verdict(lo, bad)


def main(root=ROOT):
    cert = json.loads((HERE / "CERTIFICATE.json").read_bytes(), object_pairs_hook=strict)
    recipes_new = json.loads((HERE / "REPAIR-RECIPES.json").read_bytes(), object_pairs_hook=strict)["recipes"]
    witness = read(root, f"{NATIVE}/inputs/LOWRANK-WITNESS.json")
    published_recipes = read(root, f"{NATIVE}/NATIVE-RECIPES.json.gz", gz=True)
    flags = read(root, "research/p104-joint-unit-flags/CERTIFICATE.json")
    raw = (root / NATIVE / "vendor/native_verify.py").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[f"{NATIVE}/vendor/native_verify.py"], "native interpreter pin")
    spec = importlib.util.spec_from_file_location("flag9_independent_native", root / NATIVE / "vendor/native_verify.py")
    N = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(N)

    h = flags["helpers"][9]
    need((h["basis"][0], "X%d" % h["source"], "Y%d" % h["target"]) == (HEAD, SRC, TGT), "flag 9")
    need((cert["basis_head"], cert["source_register"], cert["target_register"]) == (HEAD, SRC, TGT), "certificate flag")
    P = witness["program"]
    base_rows, base_profile, base_mass, base_adds = replay(witness, P)
    bill = cert["bill"]
    need(sum(base_profile.values()) == bill["published"]["transport_occurrences"] == 1410, "published transports")
    need(sum(k * v for k, v in base_profile.items()) == bill["published"]["rank_mass"] == 2368, "published rank mass")
    need(base_adds == bill["published"]["scalar_adds"] == 2624, "published adds")
    for n in witness["initial_frames"]:
        floor = len(basis(witness["final_frames"][n])) - len(basis(witness["initial_frames"][n]))
        need(base_mass.get(n, 0) == floor, "rank floor " + n)
    need(cert["forced_hosting"]["non_private_registers_at_rank_floor"] == 280, "floor count")

    iso = published_recipes["label_isometry"]
    dual, orth = iso["compressed_dual_gram"], iso["orthonormal_basis_compressed"]

    def to_phys(x):
        bx = sum(((((row & x).bit_count()) & 1) << i) for i, row in enumerate(dual))
        return sum((((v & bx).bit_count()) & 1) << j for j, v in enumerate(orth))

    pub_edges = {(basis(r["old"]), basis(r["new"])) for r in published_recipes["transports"]}
    new_edges = {}
    for rec in recipes_new:
        key = (basis(rec["old"]), basis(rec["new"]))
        need(key not in pub_edges and key not in new_edges, "new edge is new and unique")
        need(rec["rank"] == rec["recipe"]["rank"] == abs(len(key[1]) - len(key[0])), "new recipe rank")
        N.equal(N.recipe(rec["recipe"]), N.adjoint(N.frame(tuple(rec["old"]), 9)) + N.frame(tuple(rec["new"]), 9),
                "new native edge")
        new_edges[key] = rec

    used, progs = set(), {}
    for name in ("R0", "R1"):
        prog = splice(P, cert["repairs"][name]["splices"])
        rows, profile, mass, adds = replay(witness, prog)
        need(sum(1 for n in base_rows if rows[n] == base_rows[n]) == len(base_rows) == 280,
             "every final row equals the published row")
        for e in prog:
            if e[0] == "transport":
                key = (basis([to_phys(x) for x in e[2]]), basis([to_phys(x) for x in e[3]]))
                if key not in pub_edges:
                    need(key in new_edges, "repaired edge has a committed recipe")
                    used.add(key)
        b = bill[name]
        need(b["events"] == len(prog) and b["scalar_adds"] == adds, name + " counts")
        need(b["transport_occurrences"] == sum(profile.values()), name + " transports")
        need(b["rank_mass"] == sum(k * v for k, v in profile.items()), name + " rank mass")
        need(b["paid_profile"] == {str(k): v for k, v in sorted(profile.items())}, name + " profile")
        delta = {str(k): profile.get(k, 0) - base_profile.get(k, 0)
                 for k in sorted(set(profile) | set(base_profile)) if profile.get(k, 0) != base_profile.get(k, 0)}
        need(b["profile_delta"] == delta, name + " delta")
        md = {r: mass.get(r, 0) - base_mass.get(r, 0)
              for r in sorted(set(mass) | set(base_mass)) if mass.get(r, 0) != base_mass.get(r, 0)}
        need(b["register_mass_delta"] == md, name + " register mass delta")
        need([e for e in prog if "C" in e[1:3]] == [e for e in P if "C" in e[1:3]], name + " private register untouched")
        progs[name] = prog
    need(used == set(new_edges), "every committed recipe used")
    need((bill["R0"]["added_events"], bill["R0"]["added_transport_occurrences"], bill["R0"]["added_rank_mass"]) == (1, 1, 2), "R0 bill")
    need(bill["R0"]["profile_delta"] == {"1": -1, "2": 2, "4": 1, "5": -1} and bill["R0"]["register_mass_delta"] == {PARTNER: 2}, "R0 delta")
    need((bill["R1"]["added_events"], bill["R1"]["added_transport_occurrences"], bill["R1"]["added_rank_mass"]) == (0, 0, 2), "R1 bill")
    need(bill["R1"]["profile_delta"] == {"5": -1, "7": 1} and bill["R1"]["register_mass_delta"] == {TGT: 2}, "R1 delta")

    hc = cert["head_cohosting"]
    upd = [i for i, e in enumerate(P) if e[0] == "add" and e[1] == TGT]
    need(upd == hc["published_target_updates"] and len(upd) == 9, "published Y23 updates")
    need([i for i in upd if inside((HEAD,), frame_when(witness, P, TGT, i))] == [] == hc["published_head_hosting_target_updates"],
         "published head-free updates")
    need([i for i in upd if inside((HEAD,), frame_when(witness, P, SRC, i))] == upd
         == hc["published_source_spans_head_at_target_updates"], "X4 spans the head at every Y23 update")
    need(carried_into_target(P, witness) == [[DELIVERY, PARTNER, "-1/2"]], "published delivery")
    need(hc["published_source_delivery_into_target"] == [[DELIVERY, PARTNER, "-1/2", "-1/2"]], "published delivery record")
    need([i for i, e in enumerate(P) if e[0] in ("add", "copy") and e[2] == TGT] == [], "Y23 never read")
    need([i for i, e in enumerate(P) if e[0] in ("add", "copy", "zero", "erase") and e[1] == PARTNER] == [2520, 3635], "D28 row window")
    for name in ("R0", "R1"):
        prog = progs[name]
        carried = carried_into_target(prog, witness)
        need(len(carried) == 1 and carried[0][1:] == [PARTNER, "-1/2"], name + " single delivery of X4 via D28")
        u = carried[0][0]
        need(hc[name]["delivering_update"] == u and hc[name]["delivering_update_event"] == prog[u], name + " delivering event")
        need(hc[name]["source_delivery_into_target"] == [[u, PARTNER, "-1/2", "-1/2"]], name + " delivery record")
        tf, sf = frame_when(witness, prog, TGT, u), frame_when(witness, prog, SRC, u)
        need(inside((HEAD,), tf) and inside((HEAD,), sf) and len(sf) == 9, name + " co-hosting at the delivering update")
        co = [i for i, e in enumerate(prog) if e[0] == "add" and e[1] == TGT
              and inside((HEAD,), frame_when(witness, prog, TGT, i)) and inside((HEAD,), frame_when(witness, prog, SRC, i))]
        need(co == [u] == hc[name]["cohosted_target_updates"], name + " only the delivering update is co-hosted")
        later = [i for i, e in enumerate(prog) if i > u and SRC in e[1:3]]
        need(later == hc[name]["source_events_after_update"] and len(later) == 5, name + " source live")
        need(all(prog[i][0] == "add" and prog[i][2] == SRC for i in later), name + " later source events are reads")
    need(len(basis(progs["R0"][DELIVERY][4])) == 4 and len(basis(progs["R1"][hc["R1"]["delivering_update"]][4])) == 9,
         "update chart ranks")

    fh = cert["forced_hosting"]
    finals = {n: basis(f) for n, f in witness["final_frames"].items()}
    frames_before, cur = {}, {n: basis(f) for n, f in witness["initial_frames"].items()}
    for i, e in enumerate(P):
        for r in {e[1], e[2]} if e[0] in ("add", "copy") else ():
            frames_before[(r, i)] = cur[r]
        if e[0] == "transport":
            cur[e[1]] = basis(e[3])
        elif e[0] == "zero":
            cur[e[1]] = basis(e[2])
    table = []
    for t0 in upd:
        hosting = {}
        for j in range(t0, len(P)):
            e = P[j]
            if e[0] in ("add", "copy") and (j == t0 or e[1] in hosting or e[2] in hosting):
                for r in (e[1], e[2]):
                    hosting.setdefault(r, j)
        change = sorted(((r, t) for r, t in hosting.items() if not inside((HEAD,), frames_before[(r, t)])),
                        key=lambda x: (x[1], x[0]))
        hard = [[r, t, "final frame excludes head"] for r, t in change if r != "C" and not inside((HEAD,), finals[r])]
        table.append({"event": t0, "first_obstruction": hard[0] if hard else None, "must_change": len(change),
                      "obstructions": len(hard), "partner": P[t0][2],
                      "private_registers_forced": [[r, t] for r, t in change if r == "C"]})
    need(table == fh["head_closure_table"] and all(row["obstructions"] for row in table), "head-closure table")

    add = P[DELIVERY]
    rest = P[:DELIVERY] + P[DELIVERY + 1:]
    expected = {"least_frame_relaxed": (941, 173), "least_frame_pinned": (1114, 0)}
    for key, pinned in (("least_frame_relaxed", False), ("least_frame_pinned", True)):
        model = Lower(witness, pinned)
        need(model.whole(P, -1) == [], key + " published least frames feasible")
        sweep = {}
        for i in upd:
            got = model.whole(P, i)
            sweep[str(i)] = got
        need(len(sweep) == 9 and all(sweep.values()), key + " order-preserving zero-mass obstruction")
        need({k: [[x[0], x[-1]] for x in v] for k, v in sweep.items()}
             == {k: [[x[0], x[-1]] for x in v] for k, v in fh[key]["order_preserving"].items()}, key + " sweep lists")
        base, pre_bad = dict(model.lo0), []
        for e in rest[:2521]:
            model.feed(base, pre_bad, e, ())
        need(pre_bad == [], key + " window prefix")
        runs = []
        for k in range(2521, 3635):
            lo, bad = dict(base), []
            for f in rest[2521:k]:
                model.feed(lo, bad, f, ())
            model.feed(lo, bad, add, (HEAD,))
            for f in rest[k:]:
                model.feed(lo, bad, f, ())
            bad = model.verdict(lo, bad)
            after = k - 1 if k <= DELIVERY else k
            if runs and runs[-1][3] == bad:
                runs[-1][1] = after
                runs[-1][2] += 1
            else:
                runs.append([after, after, 1, bad])
        scan = fh[key]["relocation_scan"]
        need([[r["after_published_first"], r["after_published_last"], r["slots"], r["obstructions"]] for r in scan["runs"]]
             == runs, key + " relocation runs")
        blocked = sum(r[2] for r in runs if r[3])
        need((sum(r[2] for r in runs), blocked, sum(r[2] for r in runs) - blocked) == (1114,) + expected[key]
             == (scan["slots"], scan["obstructed_slots"], scan["feasible_slots"]), key + " relocation counts")
        need(runs[-1][:3] == [3462, 3634, 173], key + " late window boundary")
        lo, bad = dict(model.lo0), []
        for e in rest[:3462]:
            model.feed(lo, bad, e, ())
        lw = fh["late_window_partner_frame"]
        need(list(lo[PARTNER]) == lw["pinned_partner_least_frame" if pinned else "relaxed_partner_least_frame"],
             key + " late partner frame")
        if pinned:
            need(runs[-1][3] == [["final", TGT]], "pinned late window blocked by Y23's final frame")
            outside = [v for v in lo[PARTNER] if not inside((v,), finals[TGT])]
            need(outside == lw["pinned_basis_vectors_outside_target_final"] and outside, "late partner frame leaves final(Y23)")
        else:
            need(runs[-1][3] == [], "relaxed late window feasible")
    need(cert["selected_kappa"] == "0.001672660197076918" and cert["no_new_kappa"] is True, "kappa")
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
