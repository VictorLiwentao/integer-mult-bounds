#!/usr/bin/env python3
"""Behavioural tests: corruption rejection and read-only replay.

Each case copies the package and its pinned inputs into a temporary tree,
mutates one thing and runs the scanners there under python -O. Every scanner
that reads the mutated file must reject it; the clean tree must pass and stay
byte-identical.
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
    "research/p104-joint-unit-flags/CERTIFICATE.json",
]
BOTH = ("verify.py", "independent.py")


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


def cert(fn):
    def mutate(base):
        path = base / PKG / "CERTIFICATE.json"
        data = json.loads(path.read_text())
        fn(data)
        path.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    return mutate


def dup_key(base):
    p = base / PKG / "CERTIFICATE.json"
    text = p.read_text()
    need('"basis_head": 232,' in text, "duplicate-key anchor")
    p.write_text(text.replace('"basis_head": 232,', '"basis_head": 232,\n "basis_head": 232,', 1))


def flip(rel, anchor):
    def mutate(base):
        p = base / rel
        raw = bytearray(p.read_bytes())
        raw[raw.index(anchor)] ^= 1
        p.write_bytes(bytes(raw))
    return mutate


def harness_edit(base):
    p = base / PKG / "headstep.py"
    p.write_text(p.read_text().replace("return bad + [", "return bad[:0] + [", 1))


def core_row(c, p):
    return c["late_core"]["single_event_pin"][str(p)]


def open_late(c):
    c["late_window"]["pinned_with_head"].update(obstructed=0, obstruction_sets=[])
    c["scans"]["pinned_with_head"]["obstructed_slots"] = 868


CASES = {
    "relaxed_count": (cert(lambda c: c["scans"]["relaxed_with_head"].__setitem__("obstructed_slots", 867)), BOTH),
    "pinned_late_open": (cert(open_late), BOTH),
    "late_blocker_renamed": (cert(lambda c: c["late_window"]["pinned_with_head"].__setitem__("obstruction_sets", [[["final", "Y103"]]])), ("verify.py",)),
    "head_free_start": (cert(lambda c: c["scans"]["pinned_head_free"]["runs"][-1].__setitem__("after_published_first", 3366)), ("verify.py",)),
    "head_free_count": (cert(lambda c: c["scans"]["pinned_head_free"].__setitem__("obstructed_slots", 247)), BOTH),
    "annihilator": (cert(lambda c: c.__setitem__("target_final_annihilator", 60)), BOTH),
    "core_pin_weak": (cert(lambda c: core_row(c, 2511)["late_window"].__setitem__("obstructed", 246)), BOTH),
    "released_core_blocks": (cert(lambda c: c["late_core"]["pin_all_but_core"].__setitem__("obstructed", 1)), BOTH),
    "core_swapped": (cert(lambda c: c["late_core"].__setitem__("events", [2480, 2482, 2504, 2512])), BOTH),
    "chain_link": (cert(lambda c: core_row(c, 2482)["propagation_chain_to_partner"][1].__setitem__(0, 2833)), BOTH),
    "chain_truncated": (cert(lambda c: core_row(c, 2480)["propagation_chain_to_partner"].pop(2)), BOTH),
    "partner_frame": (cert(lambda c: c["pinned_partner_least_frame"]["3366"].__setitem__("outside_target_final", [32, 6])), ("verify.py",)),
    "private_events": (cert(lambda c: c["private_add_copy_events"].pop()), BOTH),
    "kappa": (cert(lambda c: c.__setitem__("selected_kappa", "0.0016726601970769181")), BOTH),
    "duplicate_key": (dup_key, BOTH),
    "witness_byte": (flip(f"{NATIVE}/inputs/LOWRANK-WITNESS.json", b"486"), BOTH),
    "flags_byte": (flip("research/p104-joint-unit-flags/CERTIFICATE.json", b"232"), BOTH),
    "harness_edit": (harness_edit, ("verify.py",)),
}


def case(name):
    mutate, scanners = CASES[name]
    with tempfile.TemporaryDirectory(prefix="flag1-late-") as d:
        base = tree(Path(d))
        mutate(base)
        for scanner in scanners:
            code, out = run(base, scanner)
            need(code != 0, f"{name}: {scanner} accepted a mutation")
            need("PASS_" not in out, f"{name}: {scanner} printed a pass marker")
    return name


def clean():
    with tempfile.TemporaryDirectory(prefix="flag1-late-") as d:
        base = tree(Path(d))
        before = digest(base)
        for scanner in BOTH:
            code, out = run(base, scanner)
            need(code == 0 and "PASS_P104_FLAG1_PINNED_LATE_RELOCATION" in out, f"clean {scanner}: {out[-400:]}")
        need(digest(base) == before, "scanners modified the tree")


def main():
    clean()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        done = list(pool.map(case, sorted(CASES)))
    need(len(done) == len(CASES), "all cases ran")
    print(f"PASS_P104_FLAG1_PINNED_LATE_RELOCATION_TESTS cases={len(CASES)} clean_read_only=1 scanners=2")


if __name__ == "__main__":
    main()
