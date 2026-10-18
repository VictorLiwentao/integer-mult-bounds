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


def r0_splice(start):
    def get(c):
        return [r for r in c["repairs"]["R0"]["splices"] if r["published_range"][0] == start][0]
    return get


def without_drop(c):
    r0_splice(3369)(c)["events"] = r0_splice(3369)(c)["events"][:1]


def target_only(c):
    without_drop(c)
    c["repairs"]["R0"]["splices"] = [r for r in c["repairs"]["R0"]["splices"] if r["published_range"][0] != 3367]


def undercharge(c):
    r0_splice(3367)(c)["events"][0][4] = 1


def r1_after_restore(c):
    rows = c["repairs"]["R1"]["splices"]
    last = [r for r in rows if r["published_range"][0] == 3624][0]
    lift, add, drop = last["events"][1:]
    pub3624 = last["events"][0]
    pub3625 = ["add", "D23", "Q6", -1, FULL]
    last["published_range"] = [3624, 3626]
    last["published"] = [pub3624, pub3625]
    last["events"] = [pub3624, pub3625, lift, add, drop]


def cert_field(fn):
    return lambda base: edit_json(base / PKG / "CERTIFICATE.json", fn)


def dup_key(base):
    p = base / PKG / "CERTIFICATE.json"
    text = p.read_text()
    need('"basis_head": 232,' in text, "duplicate-key anchor")
    p.write_text(text.replace('"basis_head": 232,', '"basis_head": 232,\n  "basis_head": 232,', 1))


def flip_witness(base):
    p = base / f"{NATIVE}/inputs/LOWRANK-WITNESS.json"
    raw = bytearray(p.read_bytes())
    k = raw.index(b"502")
    raw[k] ^= 1
    p.write_bytes(bytes(raw))


def bad_phase(base):
    p = base / PKG / "REPAIR-RECIPES.json"
    data = json.loads(p.read_text())
    left = data["recipes"][0]["recipe"]["left"]
    left["phase"] = (left["phase"] + 1) % 4
    p.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")


def scan(c):
    return c["forced_hosting"]["least_frame_relocation_scan"]


CASES = {
    "bill_rank_mass": (cert_field(lambda c: c["bill"]["R0"].__setitem__("rank_mass", 2368)), None),
    "bill_profile_delta": (cert_field(lambda c: c["bill"]["R1"]["profile_delta"].__setitem__("5", 0)), None),
    "register_mass": (cert_field(lambda c: c["bill"]["R0"].__setitem__("register_mass_delta", {"D23": 1, "Y34": 1})), None),
    "cohosted_updates": (cert_field(lambda c: c["head_cohosting"]["R0"].__setitem__("cohosted_target_updates", [])), None),
    "delivery": (cert_field(lambda c: c["head_cohosting"]["R1"]["source_delivery_into_target"][-1].__setitem__(2, "-1/2")), None),
    "closure_3369": (cert_field(lambda c: [r.__setitem__("obstructions", 0) for r in c["forced_hosting"]["head_closure_table"] if r["event"] == 3369]), None),
    "sweep_3369_feasible": (cert_field(lambda c: c["forced_hosting"]["least_frame_order_preserving_infeasible"].__setitem__("3369", [])), None),
    "scan_window_moved": (cert_field(lambda c: scan(c)["runs"][-1].__setitem__("after_published_first", 3366)), None),
    "scan_count": (cert_field(lambda c: scan(c).__setitem__("obstructed_slots", 1113)), None),
    "kappa": (cert_field(lambda c: c.__setitem__("selected_kappa", "0.0016726601970769181")), None),
    "duplicate_key": (dup_key, "duplicate JSON key"),
    "witness_byte": (flip_witness, None),
    "recipe_phase": (bad_phase, None),
    # without_drop leaves D23 on the head chart into later published transports, so
    # verify fails at the native before-frame invariant; independent fails at continuity.
    "control_without_drop": (cert_field(without_drop), None),
    "control_target_only": (cert_field(target_only), "common"),
    "control_undercharge": (cert_field(undercharge), None),
    "control_r1_after_restore": (cert_field(r1_after_restore), None),
}


def case(name):
    mutate, expect = CASES[name]
    with tempfile.TemporaryDirectory(prefix="flag0-schedule-") as d:
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
    with tempfile.TemporaryDirectory(prefix="flag0-schedule-") as d:
        base = tree(Path(d))
        before = digest(base)
        for scanner in SCANNERS:
            code, out = run(base, scanner)
            need(code == 0 and "PASS_P104_FLAG0_HEAD_SPAN_SCHEDULE" in out, f"clean {scanner}: {out[-400:]}")
        need(digest(base) == before, "scanners modified the tree")


def main():
    clean()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        done = list(pool.map(case, sorted(CASES)))
    need(len(done) == len(CASES), "all cases ran")
    print(f"PASS_P104_FLAG0_HEAD_SPAN_SCHEDULE_TESTS cases={len(CASES)} clean_read_only=1 scanners=2")


if __name__ == "__main__":
    main()
