#!/usr/bin/env python3
"""Read-only replay of the flag-0 head-span schedule bill and its zero-mass obstruction.

Applies two changed schedules to the published 4,058-event P104 witness in
memory, assembles their native recipe sets from the published recipes plus
the committed new-edge recipes, and runs the published native checker's
complete validate() on each: every native edge, every endpoint adapter, all
280 framed rows and the 72 dirty-helper restorations. It then recomputes the
bill, the head co-hosting facts, the forced-hosting closure of every Y34
update, the exact least-frame sweep for zero added non-private rank mass
(order-preserving, and for every relocation slot of the delivering ADD), and
compares the receipt with CERTIFICATE.json. Admission uses need() and stays
active under python -O. Nothing is written.
"""

import bisect
import copy
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
    f"{NATIVE}/inputs/P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    f"{NATIVE}/NATIVE-RECIPES.json.gz": "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    f"{NATIVE}/check_native.py": "e67b874a061a4a28007b9a0fabaf30c8db4a587b1e1c7dd9396c77ff1e3a9fe6",
    f"{NATIVE}/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "research/p104-joint-unit-flags/CERTIFICATE.json": "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
}
FLAG_INDEX = 0
SELECTED_KAPPA = "0.001672660197076918"
PRIVATE = "C"
DELIVERY = 3369
MARKER = (
    "PASS_P104_FLAG0_HEAD_SPAN_SCHEDULE flag=0 head=232 delivering_update=3369 "
    "R0=order_preserving added_events=1 added_adds=0 added_transports=1 added_rank_mass=2 "
    "profile_delta=-H1+3H2-H3 R1=relocated added_events=0 added_transports=0 added_rank_mass=2 "
    "profile_delta=-H3+H5 native_validate=PASS zero_mass_order_preserving=0/15 "
    "zero_mass_relocation_obstructed=926/1113 no_new_kappa"
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key: " + str(key))
        out[key] = value
    return out


def loads(raw):
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pinned_bytes(root, rel):
    raw = (root / rel).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[rel], "pinned input changed: " + rel)
    return raw


def load_checker(root):
    pinned_bytes(root, f"{NATIVE}/check_native.py")
    pinned_bytes(root, f"{NATIVE}/vendor/native_verify.py")
    name = "flag0_schedule_check_native"
    spec = importlib.util.spec_from_file_location(name, root / NATIVE / "check_native.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_inputs(root):
    witness = loads(pinned_bytes(root, f"{NATIVE}/inputs/LOWRANK-WITNESS.json"))
    fixture = loads(pinned_bytes(root, f"{NATIVE}/inputs/P104-FIXTURE.json"))["section4_explicit_P104"]
    recipes = loads(gzip.decompress(pinned_bytes(root, f"{NATIVE}/NATIVE-RECIPES.json.gz")))
    flags = loads(pinned_bytes(root, "research/p104-joint-unit-flags/CERTIFICATE.json"))
    return witness, fixture, recipes, flags


# --- GF(2) frames -----------------------------------------------------------

def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def rank(vectors):
    piv = {}
    for x in vectors:
        while x:
            j = x.bit_length() - 1
            if j in piv:
                x ^= piv[j]
            else:
                piv[j] = x
                break
    return len(piv)


def canon(values):
    piv = {}
    for x in values:
        while x:
            j = x.bit_length() - 1
            if j in piv:
                x ^= piv[j]
            else:
                piv[j] = x
                break
    for j in sorted(piv):
        for k in piv:
            if k > j and piv[k] >> j & 1:
                piv[k] ^= piv[j]
    return tuple(piv[j] for j in sorted(piv, reverse=True))


def physical_map(recipes):
    iso = recipes["label_isometry"]
    dual = iso["compressed_dual_gram"]
    orth = iso["orthonormal_basis_compressed"]
    mv = lambda rows, x: sum((((row & x).bit_count()) & 1) << i for i, row in enumerate(rows))
    dot = lambda a, b: (a & mv(dual, b)).bit_count() & 1
    convert = lambda x: sum(dot(x, v) << j for j, v in enumerate(orth))
    return lambda frame: canon(convert(x) for x in frame)


# --- schedules ---------------------------------------------------------------

def apply_splices(program, splices):
    out = list(program)
    last = len(program) + 1
    for row in sorted(splices, key=lambda r: -r["published_range"][0]):
        start, stop = row["published_range"]
        need(0 <= start < stop <= len(program) and stop <= last, "ordered disjoint splices")
        for k, old in enumerate(row["published"]):
            need(program[start + k] == old, "splice binds published event %d" % (start + k))
        need(len(row["published"]) == stop - start, "splice covers its range")
        out[start:stop] = copy.deepcopy(row["events"])
        last = start
    return out


def assemble(recipes, program, new_recipes, physical):
    pub = {(tuple(r["old"]), tuple(r["new"])): r for r in recipes["transports"]}
    extra = {(tuple(r["old"]), tuple(r["new"])): r for r in new_recipes}
    need(len(extra) == len(new_recipes), "unique new-edge recipes")
    need(not (set(pub) & set(extra)), "new recipes are new edges")
    edges = {}
    for i, e in enumerate(program):
        if e[0] == "transport":
            edges.setdefault((physical(e[2]), physical(e[3])), []).append(i)
    used_new = set()
    out = []
    for key in sorted(edges):
        if key in pub:
            rec = dict(pub[key])
        else:
            need(key in extra, "missing native recipe for new edge")
            rec = dict(extra[key])
            used_new.add(key)
        rec["events"] = edges[key]
        out.append(rec)
    profile = {}
    for rec in out:
        profile[rec["rank"]] = profile.get(rec["rank"], 0) + len(rec["events"])
    c = dict(recipes)
    c["transports"] = out
    c["paid_profile"] = {str(k): v for k, v in sorted(profile.items())}
    return c, used_new, len(set(pub) - set(edges))


def bill(result, program, n_edges):
    profile = {str(k): v for k, v in sorted(result["paid_profile"].items())}
    return {
        "events": len(program),
        "scalar_adds": result["scalar_events"]["add"],
        "private_events": {k: result["scalar_events"][k] for k in ("zero", "copy", "erase")},
        "transport_occurrences": sum(profile.values()),
        "rank_mass": result["rank_mass"],
        "paid_profile": profile,
        "distinct_native_edges": n_edges,
        "endpoint_adapters": result["intrinsic_endpoint_adapters"],
        "formal_boundary_columns": result["formal_boundary_columns"],
    }


def profile_delta(a, b):
    keys = sorted({int(k) for k in a["paid_profile"]} | {int(k) for k in b["paid_profile"]})
    out = {}
    for k in keys:
        d = b["paid_profile"].get(str(k), 0) - a["paid_profile"].get(str(k), 0)
        if d:
            out[str(k)] = d
    return out


def register_mass(program):
    out = {}
    for e in program:
        if e[0] == "transport":
            out[e[1]] = out.get(e[1], 0) + e[4]
    return out


# --- frame chronology --------------------------------------------------------

def frame_history(witness, program):
    hist = {n: [(-1, span(f))] for n, f in witness["initial_frames"].items()}
    for i, e in enumerate(program):
        if e[0] == "transport":
            hist[e[1]].append((i, span(e[3])))
        elif e[0] == "zero":
            hist.setdefault(e[1], []).append((i, span(e[2])))
    return hist


def frame_at(hist, reg, t):
    h = hist[reg]
    k = bisect.bisect_left([x[0] for x in h], t) - 1
    return h[k][1]


def row_replay(witness, program, watch):
    state = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
    seen = []
    for i, e in enumerate(program):
        op = e[0]
        if op == "zero":
            state[e[1]] = {}
        elif op == "erase":
            state.pop(e[1])
        elif op == "copy":
            state[e[1]] = dict(state[e[2]])
        elif op == "add":
            _, dst, src, a, _f = e
            if dst == watch[0]:
                carried = Fraction(a) * state[src].get(watch[1], Fraction(0))
                before = state[dst].get(watch[1], Fraction(0))
                seen.append((i, src, carried, before + carried))
            for name, v in list(state[src].items()):
                z = state[dst].get(name, Fraction(0)) + Fraction(a) * v
                if z:
                    state[dst][name] = z
                else:
                    state[dst].pop(name, None)
    return state, seen


def writes(program, reg):
    return [i for i, e in enumerate(program) if e[0] in ("add", "copy", "zero", "erase") and e[1] == reg]


# --- forced closure (head propagation, as in the flag-43 package) ------------

def closure_table(witness, program, target, head):
    hist = frame_history(witness, program)
    finals = {n: span(f) for n, f in witness["final_frames"].items()}
    monotone = {r: r != PRIVATE and all(a[1] <= b[1] for a, b in zip(h, h[1:])) for r, h in hist.items()}
    touch = {}
    for i, e in enumerate(program):
        if e[0] in ("add", "copy"):
            for r in (e[1], e[2]):
                touch.setdefault(r, []).append(i)
    rows = []
    for i, e in enumerate(program):
        if e[0] != "add" or e[1] != target:
            continue
        host = {target: i}
        work = [target]
        while work:
            r = work.pop()
            t = host[r]
            for j in touch.get(r, []):
                if j < t:
                    continue
                other = program[j][2] if program[j][1] == r else program[j][1]
                if other not in host or host[other] > j:
                    host[other] = j
                    work.append(other)
        change = {r: t for r, t in host.items() if head not in frame_at(hist, r, t)}
        hard, private = [], []
        for r, t in sorted(change.items(), key=lambda x: (x[1], x[0])):
            if not monotone.get(r, False):
                private.append([r, t])
            elif r in finals and head not in finals[r]:
                hard.append([r, t, "final frame excludes head"])
        rows.append({
            "event": i,
            "partner": e[2],
            "must_change": len(change),
            "obstructions": len(hard),
            "first_obstruction": hard[0] if hard else None,
            "private_registers_forced": private,
        })
    return rows


# --- exact least-frame sweep (zero added non-private rank mass) ---------------

def least_step(L, e):
    if e[0] != "add" or PRIVATE in (e[1], e[2]):
        return
    a, b = e[1], e[2]
    x, y = L[a], L[b]
    j = y if x <= y else x if y <= x else span(list(x) + list(y))
    L[a] = L[b] = j


def least_forced(L, a, b, head):
    j = span(list(L[a]) + list(L[b]) + [head])
    L[a] = L[b] = j


def infeasible(L, finals):
    return sorted(r for r in finals if not L[r] <= finals[r])


def least_sweep_order_preserving(witness, program, target, head):
    finals = {n: span(f) for n, f in witness["final_frames"].items()}
    init = {n: span(f) for n, f in witness["initial_frames"].items()}
    L = dict(init)
    for e in program:
        least_step(L, e)
    need(infeasible(L, finals) == [], "published word feasible in the least-frame model")
    out = {}
    for i, e in enumerate(program):
        if e[0] != "add" or e[1] != target:
            continue
        L = dict(init)
        for j, f in enumerate(program):
            if j == i:
                least_forced(L, f[1], f[2], head)
            else:
                least_step(L, f)
        out[str(i)] = infeasible(L, finals)
    return out


def relocation_scan(witness, program, delivery, head):
    """Move the delivering ADD to every slot inside its row-commutation window."""
    e = program[delivery]
    target, partner = e[1], e[2]
    w = writes(program, partner)
    lo = max(i for i in w if i < delivery)
    hi = min(i for i in w if i > delivery)
    need(not [i for i, f in enumerate(program) if f[0] in ("add", "copy") and f[2] == target], "target never read")
    finals = {n: span(f) for n, f in witness["final_frames"].items()}
    init = {n: span(f) for n, f in witness["initial_frames"].items()}
    rest = program[:delivery] + program[delivery + 1:]
    L = dict(init)
    for f in rest[:lo + 1]:
        least_step(L, f)
    runs = []
    slots = 0
    for k in range(lo + 1, hi):
        after = k - 1 if k <= delivery else k
        M = dict(L)
        least_forced(M, target, partner, head)
        for f in rest[k:]:
            least_step(M, f)
        bad = infeasible(M, finals)
        slots += 1
        if runs and runs[-1]["infeasible"] == bad:
            runs[-1]["after_published_last"] = after
            runs[-1]["slots"] += 1
        else:
            runs.append({"after_published_first": after, "after_published_last": after,
                         "slots": 1, "infeasible": bad})
        least_step(L, rest[k])
    obstructed = sum(r["slots"] for r in runs if r["infeasible"])
    return {
        "partner_row_writes_bounding_window": [lo, hi],
        "slots": slots,
        "obstructed_slots": obstructed,
        "relaxed_feasible_slots": slots - obstructed,
        "runs": [dict(r, infeasible_count=len(r["infeasible"])) for r in runs],
    }


# --- receipt -----------------------------------------------------------------

def receipt(root, cert, new_recipes):
    ck = load_checker(root)
    witness, fixture, recipes, flags = load_inputs(root)
    helper = flags["helpers"][FLAG_INDEX]
    head = helper["basis"][0]
    source, target = "X%d" % helper["source"], "Y%d" % helper["target"]
    need((source, target, head) == ("X0", "Y34", 232), "flag 0 identity")
    physical = physical_map(recipes)
    program = witness["program"]
    published = ck.validate(recipes, witness, fixture, False)
    need(published["transports"] == len(recipes["transports"]) == 740, "published native edges")
    out = {"published": bill(published, program, published["transports"])}
    repaired = {}
    used = set()
    for name in ("R0", "R1"):
        prog = apply_splices(program, cert["repairs"][name]["splices"])
        w2 = dict(witness)
        w2["program"] = prog
        c2, used_new, dropped = assemble(recipes, prog, new_recipes, physical)
        used |= used_new
        result = ck.validate(c2, w2, fixture, False)
        out[name] = bill(result, prog, result["transports"])
        out[name]["new_native_edges"] = len(used_new)
        out[name]["dropped_native_edges"] = dropped
        repaired[name] = prog
    need(len(used) == len(new_recipes), "every committed recipe is used")
    pub_mass = register_mass(program)
    for name in ("R0", "R1"):
        out[name]["profile_delta"] = profile_delta(out["published"], out[name])
        for key in ("events", "scalar_adds", "transport_occurrences", "rank_mass"):
            out[name]["added_" + key] = out[name][key] - out["published"][key]
        mass = register_mass(repaired[name])
        excess = {r: mass.get(r, 0) - pub_mass.get(r, 0) for r in sorted(set(mass) | set(pub_mass))
                  if mass.get(r, 0) != pub_mass.get(r, 0)}
        out[name]["register_mass_delta"] = excess
        out[name]["private_events_unchanged"] = [e for e in repaired[name] if PRIVATE in e[1:3]] == [e for e in program if PRIVATE in e[1:3]]

    gain = register_mass(program)
    floor = [r for r in witness["initial_frames"]
             if gain.get(r, 0) == rank(witness["final_frames"][r]) - rank(witness["initial_frames"][r])]
    need(len(floor) == len(witness["initial_frames"]) == 280, "every non-private register at its rank floor")

    pub_hist = frame_history(witness, program)
    pub_adds = [i for i, e in enumerate(program) if e[0] == "add" and e[1] == target]
    _, pub_seen = row_replay(witness, program, (target, source))
    pub_delivery = [[i, s, str(c), str(a)] for i, s, c, a in pub_seen if c]
    cohost = {
        "published_target_updates": pub_adds,
        "published_head_hosting_target_updates": [i for i in pub_adds if head in frame_at(pub_hist, target, i)],
        "published_source_delivery_into_target": pub_delivery,
        "published_settling_delivery": pub_delivery[-1],
        "partner_row_writes": writes(program, program[DELIVERY][2]),
        "target_read_events": [i for i, e in enumerate(program) if e[0] in ("add", "copy") and e[2] == target],
    }
    for name in ("R0", "R1"):
        prog = repaired[name]
        hist = frame_history(witness, prog)
        adds = [i for i, e in enumerate(prog) if e[0] == "add" and e[1] == target]
        co = [i for i in adds if head in frame_at(hist, target, i) and head in frame_at(hist, source, i)]
        _, seen = row_replay(witness, prog, (target, source))
        delivery = [[i, s, str(c), str(a)] for i, s, c, a in seen if c]
        need(delivery and delivery[-1][3] == "1/2", name + " settles the source coefficient")
        u = delivery[-1][0]
        cohost[name] = {
            "target_updates": adds,
            "cohosted_target_updates": co,
            "settling_update": u,
            "settling_update_event": prog[u],
            "update_chart_rank": rank(prog[u][4]),
            "source_frame_rank_at_update": rank(sorted(frame_at(hist, source, u) - {0})),
            "source_spans_head_at_update": head in frame_at(hist, source, u),
            "source_events_after_update": [i for i, e in enumerate(prog) if i > u and source in e[1:3]],
            "source_delivery_into_target": delivery,
        }

    table = closure_table(witness, program, target, head)
    sweep_op = least_sweep_order_preserving(witness, program, target, head)
    scan = relocation_scan(witness, program, DELIVERY, head)
    return {
        "schema_version": 1,
        "claim_id": "p104-flag0-head-span-schedule",
        "pinned_main": "6f100d4bb5083f8c35d96fd95a539811c62f245c",
        "flag_index": FLAG_INDEX,
        "source_register": source,
        "target_register": target,
        "basis_head": head,
        "repairs": cert["repairs"],
        "bill": {k: out[k] for k in ("published", "R0", "R1")},
        "head_cohosting": cohost,
        "forced_hosting": {
            "non_private_registers_at_rank_floor": len(floor),
            "head_closure_table": table,
            "least_frame_order_preserving_infeasible": sweep_op,
            "least_frame_relocation_scan": scan,
        },
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }


def admit(root, cert, new_recipes):
    got = json.loads(json.dumps(receipt(root, cert, new_recipes)))
    need(got == cert, "receipt differs from committed certificate")
    b = cert["bill"]
    r0, r1, hc, fh = b["R0"], b["R1"], cert["head_cohosting"], cert["forced_hosting"]
    need([r0["added_" + k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")] == [1, 0, 1, 2], "R0 bill")
    need(r0["profile_delta"] == {"1": -1, "2": 3, "3": -1}, "R0 profile delta")
    need(r0["register_mass_delta"] == {"D23": 2} and r0["private_events_unchanged"], "R0 surcharge sits on D23")
    need([r1["added_" + k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")] == [0, 0, 0, 2], "R1 bill")
    need(r1["profile_delta"] == {"3": -1, "5": 1}, "R1 profile delta")
    need(r1["register_mass_delta"] == {"Y34": 2} and r1["private_events_unchanged"], "R1 surcharge sits on Y34")
    need(hc["published_head_hosting_target_updates"] == [], "published word has no head-hosting update")
    need(hc["published_settling_delivery"] == [DELIVERY, "D23", "1/2", "1/2"], "3369 settles the source")
    need(hc["published_source_delivery_into_target"] == [
        [2815, "D17", "1/2", "1/2"],
        [2998, "D13", "-1/2", "0"],
        [DELIVERY, "D23", "1/2", "1/2"],
    ], "published X0 delivery path into Y34")
    need(hc["partner_row_writes"] == [2511, 3625] and hc["target_read_events"] == [], "commutation window")
    need(hc["R0"]["cohosted_target_updates"] == [DELIVERY] == [hc["R0"]["settling_update"]], "R0 co-hosts at 3369")
    need(hc["R0"]["update_chart_rank"] == 6, "R0 chart is the published chart plus the head")
    u1 = hc["R1"]["settling_update"]
    need(hc["R1"]["cohosted_target_updates"] == [u1] and hc["R1"]["update_chart_rank"] == 9, "R1 co-hosts in D23's full chart")
    for name in ("R0", "R1"):
        need(hc[name]["source_spans_head_at_update"] and hc[name]["source_frame_rank_at_update"] == 9, name + " source hosts")
        need(len(hc[name]["source_events_after_update"]) == 4, name + " source still live")
        need(hc[name]["source_delivery_into_target"][-1] == [hc[name]["settling_update"], "D23", "1/2", "1/2"], name + " settling delivery")
    need(all(row["obstructions"] > 0 for row in fh["head_closure_table"]) and len(fh["head_closure_table"]) == 15, "head closure blocks all fifteen updates")
    need(all(v for v in fh["least_frame_order_preserving_infeasible"].values()) and len(fh["least_frame_order_preserving_infeasible"]) == 15, "zero mass infeasible for all fifteen order-preserving updates")
    scan = fh["least_frame_relocation_scan"]
    need((scan["slots"], scan["obstructed_slots"], scan["relaxed_feasible_slots"]) == (1113, 926, 187), "relocation scan counts")
    need(scan["runs"][-1]["after_published_first"] == 3438 and scan["runs"][-1]["infeasible"] == [], "relaxed-feasible window starts after 3438")
    need(cert["selected_kappa"] == SELECTED_KAPPA and cert["no_new_kappa"] is True, "kappa unchanged")
    return got


def main(root=ROOT):
    cert = loads((HERE / "CERTIFICATE.json").read_bytes())
    new_recipes = loads((HERE / "REPAIR-RECIPES.json").read_bytes())["recipes"]
    admit(root, cert, new_recipes)
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
