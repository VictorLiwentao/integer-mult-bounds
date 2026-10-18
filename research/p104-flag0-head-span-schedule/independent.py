#!/usr/bin/env python3
"""Second, separately written scanner for the flag-0 head-span schedule bill.

Does not import verify.py, check_native.py or the compiler. Frames are kept as
reduced GF(2) bases; the repaired words are replayed with exact rational rows
and compared register by register with the published word's final rows and
frames. The zero-mass obstruction is recomputed by a fresh least-frame replay
for each order-preserving target update and for each relocation slot of the
delivering ADD. The new native recipes are checked directly with the vendored
independent interpreter. Admission uses need() and stays active under python -O.
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
MARKER = (
    "PASS_P104_FLAG0_HEAD_SPAN_SCHEDULE_INDEPENDENT flag=0 head=232 delivering_update=3369 "
    "R0 added_events=1 added_transports=1 added_rank_mass=2 R1 added_events=0 added_transports=0 "
    "added_rank_mass=2 rows_equal=280/280 zero_mass_order_preserving=0/15 "
    "zero_mass_relocation_obstructed=926/1113 no_new_kappa"
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
    """Reduced row-echelon basis as a sorted tuple; equal subspaces give equal tuples."""
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


def dim(b):
    return len(b)


def splice(program, rows):
    out = list(program)
    edits = sorted(((r["published_range"][0], r["published_range"][1], r) for r in rows), reverse=True)
    prev = len(program)
    for a, b, r in edits:
        need(b <= prev and a < b, "disjoint splices")
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
            need(k == abs(dim(b) - dim(a)) and k > 0, "paid rank equals frame gap at %d" % i)
            need(len(new) == dim(b) and len(old) == dim(a), "independent frame lists at %d" % i)
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
    for i, e in enumerate(program[:t]):
        if e[0] == "transport" and e[1] == reg:
            cur = basis(e[3])
    return cur


def least(witness, program, forced_index, head):
    """Least monotone frames when the C-free ADD system is forced to host the head at one ADD."""
    lo = {n: basis(f) for n, f in witness["initial_frames"].items()}
    for i, e in enumerate(program):
        if e[0] != "add" or "C" in (e[1], e[2]):
            continue
        j = basis(lo[e[1]] + lo[e[2]] + ((head,) if i == forced_index else ()))
        lo[e[1]] = lo[e[2]] = j
    finals = {n: basis(f) for n, f in witness["final_frames"].items()}
    return sorted(n for n in finals if not inside(lo[n], finals[n]))


def main(root=ROOT):
    cert = json.loads((HERE / "CERTIFICATE.json").read_bytes(), object_pairs_hook=strict)
    recipes_new = json.loads((HERE / "REPAIR-RECIPES.json").read_bytes(), object_pairs_hook=strict)["recipes"]
    witness = read(root, f"{NATIVE}/inputs/LOWRANK-WITNESS.json")
    published_recipes = read(root, f"{NATIVE}/NATIVE-RECIPES.json.gz", gz=True)
    flags = read(root, "research/p104-joint-unit-flags/CERTIFICATE.json")
    raw = (root / NATIVE / "vendor/native_verify.py").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[f"{NATIVE}/vendor/native_verify.py"], "native interpreter pin")
    spec = importlib.util.spec_from_file_location("flag0_independent_native", root / NATIVE / "vendor/native_verify.py")
    N = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(N)

    h = flags["helpers"][0]
    head, src, tgt = h["basis"][0], "X%d" % h["source"], "Y%d" % h["target"]
    need((head, src, tgt) == (232, "X0", "Y34"), "flag 0")
    need(cert["basis_head"] == head and cert["source_register"] == src and cert["target_register"] == tgt, "certificate flag")
    P = witness["program"]
    base_rows, base_profile, base_mass, base_adds = replay(witness, P)
    bill = cert["bill"]
    need(sum(base_profile.values()) == bill["published"]["transport_occurrences"] == 1410, "published transports")
    need(sum(k * v for k, v in base_profile.items()) == bill["published"]["rank_mass"] == 2368, "published rank mass")
    need(base_adds == bill["published"]["scalar_adds"] == 2624, "published adds")
    for n in witness["initial_frames"]:
        need(base_mass.get(n, 0) == dim(basis(witness["final_frames"][n])) - dim(basis(witness["initial_frames"][n])), "rank floor " + n)

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
        need(rec["rank"] == rec["recipe"]["rank"] == abs(dim(key[1]) - dim(key[0])), "new recipe rank")
        N.equal(N.recipe(rec["recipe"]), N.adjoint(N.frame(tuple(rec["old"]), 9)) + N.frame(tuple(rec["new"]), 9), "new native edge")
        new_edges[key] = rec

    used = set()
    progs = {}
    for name in ("R0", "R1"):
        prog = splice(P, cert["repairs"][name]["splices"])
        rows, profile, mass, adds = replay(witness, prog)
        same = sum(1 for n in base_rows if rows[n] == base_rows[n])
        need(same == len(base_rows) == 280, "every final row equals the published row")
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
        delta = {str(k): profile.get(k, 0) - base_profile.get(k, 0) for k in sorted(set(profile) | set(base_profile)) if profile.get(k, 0) != base_profile.get(k, 0)}
        need(b["profile_delta"] == delta, name + " delta")
        md = {r: mass.get(r, 0) - base_mass.get(r, 0) for r in sorted(set(mass) | set(base_mass)) if mass.get(r, 0) != base_mass.get(r, 0)}
        need(b["register_mass_delta"] == md, name + " register mass delta")
        need([e for e in prog if "C" in e[1:3]] == [e for e in P if "C" in e[1:3]], name + " private register untouched")
        progs[name] = prog
    need(used == set(new_edges), "every committed recipe used")
    need((bill["R0"]["added_events"], bill["R0"]["added_transport_occurrences"], bill["R0"]["added_rank_mass"]) == (1, 1, 2), "R0 bill")
    need(bill["R0"]["profile_delta"] == {"1": -1, "2": 3, "3": -1} and bill["R0"]["register_mass_delta"] == {"D23": 2}, "R0 delta")
    need((bill["R1"]["added_events"], bill["R1"]["added_transport_occurrences"], bill["R1"]["added_rank_mass"]) == (0, 0, 2), "R1 bill")
    need(bill["R1"]["profile_delta"] == {"3": -1, "5": 1} and bill["R1"]["register_mass_delta"] == {"Y34": 2}, "R1 delta")

    hc = cert["head_cohosting"]
    upd = [i for i, e in enumerate(P) if e[0] == "add" and e[1] == tgt]
    need(upd == hc["published_target_updates"], "published Y34 updates")
    need(len(upd) == 15, "fifteen Y34 updates")
    need([i for i in upd if inside((head,), frame_when(witness, P, tgt, i))] == [] == hc["published_head_hosting_target_updates"], "published head-free updates")
    need(hc["published_settling_delivery"] == [3369, "D23", "1/2", "1/2"], "published settling delivery")
    need(hc["published_source_delivery_into_target"] == [
        [2815, "D17", "1/2", "1/2"],
        [2998, "D13", "-1/2", "0"],
        [3369, "D23", "1/2", "1/2"],
    ], "published delivery record")
    need([i for i, e in enumerate(P) if e[0] in ("add", "copy") and e[2] == tgt] == [], "Y34 never read")
    need([i for i, e in enumerate(P) if e[0] in ("add", "copy", "zero", "erase") and e[1] == "D23"] == [2511, 3625], "D23 row window")
    for name in ("R0", "R1"):
        prog = progs[name]
        rows = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
        carried = []
        for i, e in enumerate(prog):
            if e[0] == "zero":
                rows[e[1]] = {}
            elif e[0] == "erase":
                rows.pop(e[1])
            elif e[0] == "copy":
                rows[e[1]] = dict(rows[e[2]])
            elif e[0] == "add":
                if e[1] == tgt and rows[e[2]].get(src):
                    before = rows[e[1]].get(src, Fraction(0))
                    c = Fraction(e[3]) * rows[e[2]][src]
                    carried.append([i, e[2], str(c), str(before + c)])
                for n, v in rows[e[2]].items():
                    z = rows[e[1]].get(n, Fraction(0)) + Fraction(e[3]) * v
                    if z:
                        rows[e[1]][n] = z
                    else:
                        rows[e[1]].pop(n, None)
        need(carried and carried[-1][1:] == ["D23", "1/2", "1/2"], name + " settles X0 via D23")
        u = carried[-1][0]
        need(hc[name]["settling_update"] == u, name + " settling index")
        need(hc[name]["source_delivery_into_target"][-1] == [u, "D23", "1/2", "1/2"], name + " delivery record")
        need(hc[name]["settling_update_event"] == prog[u], name + " settling event record")
        tf, sf = frame_when(witness, prog, tgt, u), frame_when(witness, prog, src, u)
        need(inside((head,), tf) and inside((head,), sf) and dim(sf) == 9, name + " co-hosting at the settling update")
        co = [i for i, e in enumerate(prog) if e[0] == "add" and e[1] == tgt
              and inside((head,), frame_when(witness, prog, tgt, i)) and inside((head,), frame_when(witness, prog, src, i))]
        need(co == [u] == hc[name]["cohosted_target_updates"], name + " only the settling update is co-hosted")
        later = [i for i, e in enumerate(prog) if i > u and src in e[1:3]]
        need(later == hc[name]["source_events_after_update"] and len(later) == 4, name + " source live")
    need(dim(basis(progs["R0"][3369][4])) == 6 and dim(basis(progs["R1"][hc["R1"]["settling_update"]][4])) == 9, "update chart ranks")

    fh = cert["forced_hosting"]
    finals = {n: basis(f) for n, f in witness["final_frames"].items()}
    frames_before = {}
    cur = {n: basis(f) for n, f in witness["initial_frames"].items()}
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
            if e[0] not in ("add", "copy"):
                continue
            if j == t0 or e[1] in hosting or e[2] in hosting:
                for r in (e[1], e[2]):
                    hosting.setdefault(r, j)
        change = {r: t for r, t in hosting.items() if not inside((head,), frames_before[(r, t)])}
        order = sorted(change.items(), key=lambda x: (x[1], x[0]))
        hard = [[r, t, "final frame excludes head"] for r, t in order if r != "C" and not inside((head,), finals[r])]
        table.append({"event": t0, "partner": P[t0][2], "must_change": len(change), "obstructions": len(hard),
                      "first_obstruction": hard[0] if hard else None,
                      "private_registers_forced": [[r, t] for r, t in order if r == "C"]})
    need(table == fh["head_closure_table"] and all(row["obstructions"] for row in table), "head-closure table")
    sweep = {}
    for i in upd:
        sweep[str(i)] = least(witness, P, i, head)
    need(least(witness, P, -1, head) == [], "published least frames feasible")
    need(sweep == fh["least_frame_order_preserving_infeasible"] and all(sweep.values()), "order-preserving zero-mass obstruction")

    add = P[3369]
    rest = P[:3369] + P[3370:]
    runs = []
    for k in range(2512, 3625):
        after = k - 1 if k <= 3369 else k
        bad = least(witness, rest[:k] + [add] + rest[k:], k, head)
        if runs and runs[-1][3] == bad:
            runs[-1][1] = after
            runs[-1][2] += 1
        else:
            runs.append([after, after, 1, bad])
    scan = fh["least_frame_relocation_scan"]
    need([[r["after_published_first"], r["after_published_last"], r["slots"], r["infeasible"]] for r in scan["runs"]] == runs, "relocation runs")
    total = sum(r[2] for r in runs)
    blocked = sum(r[2] for r in runs if r[3])
    need((total, blocked) == (scan["slots"], scan["obstructed_slots"]) == (1113, 926), "relocation counts")
    need(runs[-1][:3] == [3438, 3624, 187] and runs[-1][3] == [], "relaxed-feasible window")
    need(cert["selected_kappa"] == "0.001672660197076918" and cert["no_new_kappa"] is True, "kappa")
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
