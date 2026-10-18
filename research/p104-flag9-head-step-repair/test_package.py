#!/usr/bin/env python3
"""Behavioural tests: corruption, negative controls and read-only replay.

Each case copies the package and its pinned inputs into a temporary tree,
mutates one thing and runs both scanners there under python -O. The scanners
must reject every mutation; the clean tree must pass and stay byte-identical.
"""

import concurrent.futures
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PKG = HERE.relative_to(ROOT).as_posix()
NATIVE = "research/p104-native-channel"
COPY = [
    f"{NATIVE}/inputs/LOWRANK-WITNESS.json",
    f"{NATIVE}/inputs/P104-FIXTURE.json",
    f"{NATIVE}/NATIVE-RECIPES.json.gz",
    f"{NATIVE}/check_native.py",
    f"{NATIVE}/vendor/native_verify.py",
    "research/p104-joint-unit-flags/CERTIFICATE.json",
]
SCANNERS = ("verify.py", "independent.py")
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def tree(base):
    for rel in COPY:
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, base / rel)
    shutil.copytree(HERE, base / PKG, ignore=shutil.ignore_patterns("__pycache__"))
    return base


def run(base, scanner):
    p = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(base / PKG / scanner), str(base)],
                       capture_output=True, text=True, timeout=600)
    return p.returncode, p.stdout + p.stderr


def digest(base):
    return {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(base.rglob("*")) if p.is_file()}


def edit_json(path, fn):
    data = json.loads(path.read_text())
    fn(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def splice_at(c, name, start):
    return [r for r in c["repairs"][name]["splices"] if r["published_range"][0] == start][0]


def without_drop(c):
    row = splice_at(c, "R0", 3124)
    row["events"] = row["events"][:1]


def target_only(c):
    without_drop(c)
    c["repairs"]["R0"]["splices"] = [r for r in c["repairs"]["R0"]["splices"] if r["published_range"][0] != 3122]


def undercharge(c):
    splice_at(c, "R0", 3122)["events"][0][4] = 1


def r1_after_restore(c):
    last = splice_at(c, "R1", 3634)
    lift, add, drop = last["events"][1:]
    pub3634 = last["events"][0]
    pub3635 = ["add", "D28", "Q7", -1, FULL]
    last["published_range"] = [3634, 3636]
    last["published"] = [pub3634, pub3635]
    last["events"] = [pub3634, pub3635, lift, add, drop]


def r1_before_partner_lift(c):
    last = splice_at(c, "R1", 3634)
    pub3634, lift, add, drop = last["events"]
    last["events"] = [lift, add, drop, pub3634]


def cert_field(fn):
    return lambda base: edit_json(base / PKG / "CERTIFICATE.json", fn)


def dup_key(base):
    p = base / PKG / "CERTIFICATE.json"
    text = p.read_text()
    need('"basis_head": 196,' in text, "duplicate-key anchor")
    p.write_text(text.replace('"basis_head": 196,', '"basis_head": 196,\n  "basis_head": 196,', 1))


def flip_witness(base):
    p = base / f"{NATIVE}/inputs/LOWRANK-WITNESS.json"
    raw = bytearray(p.read_bytes())
    raw[raw.index(b"447")] ^= 1
    p.write_bytes(bytes(raw))


def bad_phase(base):
    p = base / PKG / "REPAIR-RECIPES.json"
    data = json.loads(p.read_text())
    left = data["recipes"][0]["recipe"]["left"]
    left["phase"] = (left["phase"] + 1) % 4
    p.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")


def relaxed(c):
    return c["forced_hosting"]["least_frame_relaxed"]


def pinned(c):
    return c["forced_hosting"]["least_frame_pinned"]


def pinned_late_open(c):
    s = pinned(c)["relocation_scan"]
    s["runs"][-1]["obstructions"] = []
    s["runs"][-1]["obstruction_count"] = 0
    s["obstructed_slots"] = 941
    s["feasible_slots"] = 173


CASES = {
    "bill_rank_mass": (cert_field(lambda c: c["bill"]["R0"].__setitem__("rank_mass", 2368)), None),
    "bill_profile_delta": (cert_field(lambda c: c["bill"]["R1"]["profile_delta"].__setitem__("7", 0)), None),
    "register_mass": (cert_field(lambda c: c["bill"]["R0"].__setitem__("register_mass_delta", {"D28": 1, "Y23": 1})), None),
    "cohosted_updates": (cert_field(lambda c: c["head_cohosting"]["R0"].__setitem__("cohosted_target_updates", [])), None),
    "delivery": (cert_field(lambda c: c["head_cohosting"]["R1"]["source_delivery_into_target"][0].__setitem__(2, "1/2")), None),
    "source_live": (cert_field(lambda c: c["head_cohosting"]["R0"]["source_events_after_update"].pop()), None),
    "closure_3124": (cert_field(lambda c: [r.__setitem__("obstructions", 0) for r in c["forced_hosting"]["head_closure_table"] if r["event"] == 3124]), None),
    "relaxed_sweep_3124_feasible": (cert_field(lambda c: relaxed(c)["order_preserving"].__setitem__("3124", [])), None),
    "pinned_sweep_3124_feasible": (cert_field(lambda c: pinned(c)["order_preserving"].__setitem__("3124", [])), None),
    "relaxed_scan_window_moved": (cert_field(lambda c: relaxed(c)["relocation_scan"]["runs"][-1].__setitem__("after_published_first", 3387)), None),
    "relaxed_scan_count": (cert_field(lambda c: relaxed(c)["relocation_scan"].__setitem__("obstructed_slots", 1114)), None),
    "pinned_late_window_open": (cert_field(pinned_late_open), None),
    "late_partner_frame": (cert_field(lambda c: c["forced_hosting"]["late_window_partner_frame"].__setitem__("pinned_basis_vectors_outside_target_final", [])), None),
    "kappa": (cert_field(lambda c: c.__setitem__("selected_kappa", "0.0016726601970769181")), None),
    "duplicate_key": (dup_key, "duplicate JSON key"),
    "witness_byte": (flip_witness, None),
    "recipe_phase": (bad_phase, None),
    "control_without_drop": (cert_field(without_drop), "common"),
    "control_target_only": (cert_field(target_only), "common"),
    "control_undercharge": (cert_field(undercharge), None),
    "control_r1_after_restore": (cert_field(r1_after_restore), None),
    "control_r1_before_partner_lift": (cert_field(r1_before_partner_lift), "common"),
}


def case(name):
    mutate, expect = CASES[name]
    with tempfile.TemporaryDirectory(prefix="flag9-repair-") as d:
        base = tree(Path(d))
        mutate(base)
        for scanner in SCANNERS:
            code, out = run(base, scanner)
            need(code != 0, f"{name}: {scanner} accepted a mutation")
            need("PASS_" not in out, f"{name}: {scanner} printed a pass marker")
            if expect:
                need(expect in out, f"{name}: {scanner} rejected for the wrong reason: {out[-300:]}")
    return name


def clean():
    with tempfile.TemporaryDirectory(prefix="flag9-repair-") as d:
        base = tree(Path(d))
        before = digest(base)
        for scanner in SCANNERS:
            code, out = run(base, scanner)
            need(code == 0 and "PASS_P104_FLAG9_HEAD_STEP_REPAIR" in out, f"clean {scanner}: {out[-400:]}")
        need(digest(base) == before, "scanners modified the tree")


def main():
    clean()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        done = list(pool.map(case, sorted(CASES)))
    need(len(done) == len(CASES), "all cases ran")
    print(f"PASS_P104_FLAG9_HEAD_STEP_REPAIR_TESTS cases={len(CASES)} clean_read_only=1 scanners=2")


if __name__ == "__main__":
    main()
