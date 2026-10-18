#!/usr/bin/env python3
"""Producer for CERTIFICATE.json and REPAIR-RECIPES.json (not part of replay).

Defines the two changed schedules as splices of the published witness,
lowers each transport edge absent from the published recipe set with the
pinned native compiler, and writes the receipt computed by verify.py.
Refuses to overwrite existing outputs unless --force is given.
"""

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402

COMPILER_SHA256 = "9d2fc2d81962ddb0b4dd7d6482d9918a87a6b05759690317dea79939ca5656a3"
CLIFFORD_SHA256 = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"

A2 = [95, 486]
A3 = A2 + [232]
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]


def splices(program, final):
    def one(i, event):
        return {"published_range": [i, i + 1], "published": [program[i]], "events": [event]}
    r0 = [
        one(2795, ["transport", "D17", [486], A3, 2]),
        one(2796, ["transport", "Y7", [95], A3, 2]),
        {"published_range": [2797, 2798], "published": [program[2797]],
         "events": [["add", "Y7", "D17", "1/4", A3], ["transport", "D17", A3, A2, 1]]},
        one(3473, ["transport", "Y7", A3, final["Y7"], 5]),
    ]
    r1 = [
        {"published_range": [2796, 2798], "published": program[2796:2798], "events": []},
        {"published_range": [3473, 3474], "published": [program[3473]], "events": []},
        {"published_range": [3612, 3613], "published": [program[3612]],
         "events": [program[3612],
                    ["transport", "Y7", [95], FULL, 8],
                    ["add", "Y7", "D17", "1/4", FULL],
                    ["transport", "Y7", FULL, final["Y7"], 1]]},
    ]
    return {
        "R0": {
            "class": "order-preserving: every published event kept in published order with the same ADD registers and coefficients; one downward D17 transport inserted after the delivering ADD",
            "rule": "D17 and Y7 enter the published 2797 chart plus the head (rank 3) at their last transports before 2797; D17 drops back to the published chart immediately after; Y7's terminal transport starts from the rank-3 chart",
            "splices": r0,
        },
        "R1": {
            "class": "relocation: the delivering ADD (with Y7's 2796 and 3473 transports) moves into D17's full-chart window between its lift at 3612 and its restoration at 3613; no event added or removed",
            "rule": "Y7 lifts from [95] to the full chart, takes Y7 += D17/4 there, then drops to its final frame",
            "splices": r1,
        },
    }


def load(name, path, digest):
    raw = path.read_bytes()
    V.need(hashlib.sha256(raw).hexdigest() == digest, "pinned compiler module: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    for name in ("CERTIFICATE.json", "REPAIR-RECIPES.json"):
        V.need(args.force or not (HERE / name).exists(), name + " exists")
    root = V.ROOT
    load("flag1_clifford_pin", root / V.NATIVE / "vendor/clifford_exact.py", CLIFFORD_SHA256)
    co = load("flag1_native_compile", root / V.NATIVE / "compile.py", COMPILER_SHA256)
    witness, _fixture, recipes, _flags = V.load_inputs(root)
    cert = {"repairs": splices(witness["program"], witness["final_frames"])}
    physical = V.physical_map(recipes)
    pub = {(tuple(r["old"]), tuple(r["new"])) for r in recipes["transports"]}
    new = {}
    for name in ("R0", "R1"):
        prog = V.apply_splices(witness["program"], cert["repairs"][name]["splices"])
        for e in prog:
            if e[0] != "transport":
                continue
            key = (physical(e[2]), physical(e[3]))
            if key in pub or key in new:
                continue
            actual = co.CE.canonical_frame(9, key[0]).adjoint().then(co.CE.canonical_frame(9, key[1]))
            record, _ = co.CE.lower_child(actual)
            V.need(record["rank"] == e[4], "native rank equals frame gap")
            new[key] = {"old": list(key[0]), "new": list(key[1]), "rank": e[4], "recipe": record}
    recs = [new[k] for k in sorted(new)]
    payload = {
        "schema_version": 1,
        "scope": "Native recipes for the transport edges used by repairs R0 and R1 that are absent from the published p104-native-channel recipe set. Lowered with the pinned compile.py / vendor/clifford_exact.py; checked by the published check_native.validate() during replay.",
        "compiler_sha256": COMPILER_SHA256,
        "clifford_exact_sha256": CLIFFORD_SHA256,
        "recipes": recs,
    }
    got = V.receipt(root, cert, recs)
    (HERE / "REPAIR-RECIPES.json").write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    (HERE / "CERTIFICATE.json").write_text(json.dumps(got, indent=2, sort_keys=True) + "\n")
    print("WROTE", len(recs), "new recipes")


if __name__ == "__main__":
    main()
