"""Flag-agnostic head-step repair harness for the published P104 native channel.

Imported by verify.py and build.py; independent.py does not import it. A later
present-head flag package can load this module by path and supply only its
own flag constants and splices. Every function is read-only. Frames are
canonical reduced GF(2) bases (tuples), so equal spans compare equal.

The splice/assemble/validate harness, the head-closure rule and the bill
format follow #3508 and #3532; the private-pinned least-frame model is new.
"""

import copy
import gzip
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction

NATIVE = "research/p104-native-channel"
FLAGS = "research/p104-joint-unit-flags/CERTIFICATE.json"
PINS = {
    f"{NATIVE}/inputs/LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    f"{NATIVE}/inputs/P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    f"{NATIVE}/NATIVE-RECIPES.json.gz": "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    f"{NATIVE}/check_native.py": "e67b874a061a4a28007b9a0fabaf30c8db4a587b1e1c7dd9396c77ff1e3a9fe6",
    f"{NATIVE}/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    FLAGS: "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
}
PRIVATE = "C"
FULL = (1, 2, 4, 8, 16, 32, 64, 128, 256)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def _unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key: " + str(key))
        out[key] = value
    return out


def loads(raw):
    return json.loads(raw, object_pairs_hook=_unique)


def pinned_bytes(root, rel):
    raw = (root / rel).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[rel], "pinned input changed: " + rel)
    return raw


def load_checker(root, name):
    pinned_bytes(root, f"{NATIVE}/check_native.py")
    pinned_bytes(root, f"{NATIVE}/vendor/native_verify.py")
    spec = importlib.util.spec_from_file_location(name, root / NATIVE / "check_native.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_inputs(root):
    witness = loads(pinned_bytes(root, f"{NATIVE}/inputs/LOWRANK-WITNESS.json"))
    fixture = loads(pinned_bytes(root, f"{NATIVE}/inputs/P104-FIXTURE.json"))["section4_explicit_P104"]
    recipes = loads(gzip.decompress(pinned_bytes(root, f"{NATIVE}/NATIVE-RECIPES.json.gz")))
    flags = loads(pinned_bytes(root, FLAGS))
    return witness, fixture, recipes, flags


# --- GF(2) frames ------------------------------------------------------------

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


def join(*frames):
    return canon([x for f in frames for x in f])


def within(a, b):
    return join(a, b) == b


def hosts(frame, v):
    return join(frame, (v,)) == frame


def rank(values):
    return len(canon(values))


def physical_map(recipes):
    iso = recipes["label_isometry"]
    dual = iso["compressed_dual_gram"]
    orth = iso["orthonormal_basis_compressed"]

    def mv(rows, x):
        return sum((((row & x).bit_count()) & 1) << i for i, row in enumerate(rows))

    def convert(x):
        bx = mv(dual, x)
        return sum((((v & bx).bit_count()) & 1) << j for j, v in enumerate(orth))

    return lambda frame: canon(convert(x) for x in frame)


# --- schedules and bill ------------------------------------------------------

def apply_splices(program, splices):
    out = list(program)
    last = len(program) + 1
    for row in sorted(splices, key=lambda r: -r["published_range"][0]):
        start, stop = row["published_range"]
        need(0 <= start < stop <= len(program) and stop <= last, "ordered disjoint splices")
        need(len(row["published"]) == stop - start, "splice covers its range")
        for k, old in enumerate(row["published"]):
            need(program[start + k] == old, "splice binds published event %d" % (start + k))
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
    used_new, out, profile = set(), [], {}
    for key in sorted(edges):
        if key in pub:
            rec = dict(pub[key])
        else:
            need(key in extra, "missing native recipe for new edge")
            rec = dict(extra[key])
            used_new.add(key)
        rec["events"] = edges[key]
        out.append(rec)
        profile[rec["rank"]] = profile.get(rec["rank"], 0) + len(edges[key])
    assembled = dict(recipes)
    assembled["transports"] = out
    assembled["paid_profile"] = {str(k): v for k, v in sorted(profile.items())}
    return assembled, used_new, len(set(pub) - set(edges))


def bill(result, program):
    profile = {str(k): v for k, v in sorted(result["paid_profile"].items())}
    return {
        "events": len(program),
        "scalar_adds": result["scalar_events"]["add"],
        "private_events": {k: result["scalar_events"][k] for k in ("zero", "copy", "erase")},
        "transport_occurrences": sum(profile.values()),
        "rank_mass": result["rank_mass"],
        "paid_profile": profile,
        "distinct_native_edges": result["transports"],
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


def mass_delta(a, b):
    ma, mb = register_mass(a), register_mass(b)
    return {r: mb.get(r, 0) - ma.get(r, 0) for r in sorted(set(ma) | set(mb)) if ma.get(r, 0) != mb.get(r, 0)}


def private_events(program):
    return [e for e in program if PRIVATE in e[1:3]]


def validate_repairs(root, checker_name, repairs, new_recipes):
    """Run the published check_native.validate() on the published word and every repair."""
    ck = load_checker(root, checker_name)
    witness, fixture, recipes, _flags = load_inputs(root)
    physical = physical_map(recipes)
    program = witness["program"]
    published = ck.validate(recipes, witness, fixture, False)
    need(published["transports"] == len(recipes["transports"]) == 740, "published native edges")
    bills = {"published": bill(published, program)}
    words, used = {}, set()
    for name in sorted(repairs):
        prog = apply_splices(program, repairs[name]["splices"])
        w2 = dict(witness)
        w2["program"] = prog
        assembled, used_new, dropped = assemble(recipes, prog, new_recipes, physical)
        used |= used_new
        result = ck.validate(assembled, w2, fixture, False)
        b = bill(result, prog)
        b["new_native_edges"] = len(used_new)
        b["dropped_native_edges"] = dropped
        b["profile_delta"] = profile_delta(bills["published"], b)
        for key in ("events", "scalar_adds", "transport_occurrences", "rank_mass"):
            b["added_" + key] = b[key] - bills["published"][key]
        b["register_mass_delta"] = mass_delta(program, prog)
        b["private_events_unchanged"] = private_events(prog) == private_events(program)
        bills[name] = b
        words[name] = prog
    need(len(used) == len(new_recipes), "every committed recipe is used")
    return witness, bills, words


# --- chronology --------------------------------------------------------------

def frame_at(witness, program, reg, t):
    cur = canon(witness["initial_frames"].get(reg, ()))
    for e in program[:t]:
        if e[1] == reg and e[0] == "transport":
            cur = canon(e[3])
        elif e[1] == reg and e[0] == "zero":
            cur = canon(e[2])
    return cur


def deliveries(witness, program, target, source):
    """Every ADD into target whose read row carries a nonzero source entry."""
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
            _, dst, src, a, _frame = e
            if dst == target:
                carried = Fraction(a) * state[src].get(source, Fraction(0))
                if carried:
                    seen.append([i, src, str(carried), str(state[dst].get(source, Fraction(0)) + carried)])
            for name, v in list(state[src].items()):
                z = state[dst].get(name, Fraction(0)) + Fraction(a) * v
                if z:
                    state[dst][name] = z
                else:
                    state[dst].pop(name, None)
    return seen


def writes(program, reg):
    return [i for i, e in enumerate(program) if e[0] in ("add", "copy", "zero", "erase") and e[1] == reg]


def reads(program, reg):
    return [i for i, e in enumerate(program) if e[0] in ("add", "copy") and e[2] == reg]


def at_rank_floor(witness, program):
    gain = register_mass(program)
    return [r for r in witness["initial_frames"]
            if gain.get(r, 0) == rank(witness["final_frames"][r]) - rank(witness["initial_frames"][r])]


# --- head closure (#3508 rule) -----------------------------------------------

def closure_table(witness, program, target, head):
    finals = {n: canon(f) for n, f in witness["final_frames"].items()}
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
            for j in touch.get(r, []):
                if j < host[r]:
                    continue
                other = program[j][2] if program[j][1] == r else program[j][1]
                if other not in host or host[other] > j:
                    host[other] = j
                    work.append(other)
        change = {r: t for r, t in host.items() if not hosts(frame_at(witness, program, r, t), head)}
        order = sorted(change.items(), key=lambda x: (x[1], x[0]))
        hard = [[r, t, "final frame excludes head"] for r, t in order
                if r != PRIVATE and not hosts(finals[r], head)]
        rows.append({
            "event": i,
            "partner": e[2],
            "must_change": len(change),
            "obstructions": len(hard),
            "first_obstruction": hard[0] if hard else None,
            "private_registers_forced": [[r, t] for r, t in order if r == PRIVATE],
        })
    return rows


# --- exact least-frame model (zero added non-private rank mass) --------------

class Least:
    """Least monotone frames forced by the common-chart rule.

    relaxed: the private register is free, so its ADDs and copies impose
    nothing. pinned: the private register keeps its published events, so a
    partner must equal the private chart at each private ADD or copy.
    """

    def __init__(self, witness, pinned):
        self.pinned = pinned
        self.init = {n: canon(f) for n, f in witness["initial_frames"].items()}
        self.finals = {n: canon(f) for n, f in witness["final_frames"].items()}

    def start(self):
        return dict(self.init), []

    def step(self, L, bad, i, e, head=None):
        if e[0] not in ("add", "copy"):
            return
        a, b = e[1], e[2]
        if PRIVATE not in (a, b):
            L[a] = L[b] = join(L[a], L[b], (head,) if head is not None else ())
            return
        if not self.pinned:
            return
        r = b if a == PRIVATE else a
        chart = canon(e[-1])
        if not within(L[r], chart):
            bad.append(["private chart", i, r])
        L[r] = join(L[r], chart)

    def finish(self, L, bad):
        return bad + [["final", r] for r in sorted(self.finals) if not within(L[r], self.finals[r])]

    def run(self, program, forced=-1, head=None):
        L, bad = self.start()
        for i, e in enumerate(program):
            self.step(L, bad, i, e, head if i == forced else None)
        return self.finish(L, bad)


def partner_frame_after(model, program, delivery, slot):
    """Least frame of the delivering partner once the published word (less the delivering ADD) reaches slot."""
    L, bad = model.start()
    for i, e in enumerate(program[:slot + 1]):
        if i != delivery:
            model.step(L, bad, i, e)
    need(bad == [], "prefix feasible")
    return L[program[delivery][2]]


def order_preserving_sweep(model, program, target, head):
    need(model.run(program) == [], "published word feasible in the least-frame model")
    return {str(i): model.run(program, i, head)
            for i, e in enumerate(program) if e[0] == "add" and e[1] == target}


def relocation_scan(model, program, delivery, head):
    """Move the delivering ADD to every slot of its row-commutation window."""
    e = program[delivery]
    target, partner = e[1], e[2]
    need(reads(program, target) == [], "target never read")
    w = writes(program, partner)
    lo = max(i for i in w if i < delivery)
    hi = min(i for i in w if i > delivery)
    rest = program[:delivery] + program[delivery + 1:]
    L, bad = model.start()
    for i, f in enumerate(rest[:lo + 1]):
        model.step(L, bad, i, f)
    need(bad == [], "prefix feasible")
    runs = []
    for k in range(lo + 1, hi):
        after = k - 1 if k <= delivery else k
        M, b = dict(L), []
        model.step(M, b, k, e, head)
        for j, f in enumerate(rest[k:]):
            model.step(M, b, k + 1 + j, f)
        b = [[x[0], x[-1]] for x in model.finish(M, b)]
        if runs and runs[-1]["obstructions"] == b:
            runs[-1]["after_published_last"] = after
            runs[-1]["slots"] += 1
        else:
            runs.append({"after_published_first": after, "after_published_last": after,
                         "slots": 1, "obstructions": b})
        model.step(L, [], k, rest[k])
    slots = sum(r["slots"] for r in runs)
    blocked = sum(r["slots"] for r in runs if r["obstructions"])
    return {
        "partner_row_writes_bounding_window": [lo, hi],
        "slots": slots,
        "obstructed_slots": blocked,
        "feasible_slots": slots - blocked,
        "runs": [dict(r, obstruction_count=len(r["obstructions"])) for r in runs],
    }
