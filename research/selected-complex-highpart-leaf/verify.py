"""Verify the selected complex high-part exchange through the completed ordinary engine.

Default: read-only.  Re-hash every pinned input (including every imported
engine file) before importing the engine, check source citations, replay the
exact high-part plan for a grid of (k, body) widths, execute the physical
high-part cases, reject four mutation controls, and compare the complete typed
summary with CERTIFICATE.json.  --suite fitted replays the slower fitted-branch
section.  --write regenerates the selected certificate section.
"""
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import highpart  # noqa: E402  (no engine import at module load)
from highpart import need  # noqa: E402

BASE_COMMIT = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
SELECTED_KAPPA = "0.001672660197076918"

# (q, k, body, reserve) — reserve extents 1 and 3 for each shape
PHYSICAL_CASES = (
    (2, 1, 1, 1), (2, 1, 1, 3),
    (2, 1, 2, 1), (2, 1, 2, 3),
    (2, 2, 1, 1), (2, 2, 1, 3),
    (3, 1, 1, 1), (3, 1, 1, 3),
    (3, 2, 1, 1), (3, 2, 1, 3),
    (5, 1, 1, 1), (5, 1, 1, 3),
)
PLAN_GRID = tuple((k, body) for k in range(1, 6) for body in range(1, 6))
CITATIONS = {
    "notes/three-stage-cover-rows.tex": (
        "One inherited ordinary width-$k$ interchange of the two high parts",
        "with the bodies and $Z$ as spectators, gives",
        "Every completed call restores its row coordinate, so successive residuals and the outer "
        "wrapper reuse one reserve",
    ),
    "research/selected-coarse-depth-stock/PROOF.md": (
        "Ordinary peeled atoms, routing, adapters and high-part exchanges are separate completed calls.",
        "S_parent(e,w) = C(w)^D(n) * S_leaf(e,w)",
        "If the full completed ordinary-leaf contract is available without an external reserve, "
        "one may take S_leaf=1.",
        "Actual A, B and rho are **not established here**.",
    ),
    "research/community-round8-audit/pr185-proof-reviewed.md": (
        "High-part exchange and residual digits: ordinary calls with complete bodies as spectators",
        "Fixed cover routing: a fixed number of ordinary width-`O(w)` calls",
        "restores preceding row coordinates",
    ),
    "research/physical-ordinary-interchange/PROOF.md": (
        "I require no external fresh-row factor.",
        "old_count=P, depth=0, old_directory=empty,",
        "The complex supplier, selected bootstrap-stage adoption and analytic transfer remain separate.",
    ),
    "research/selected-stock-envelope-m73/README.md": (
        "2. **Bind `rho`.** Find the complex analogue of the ordinary leaf reserve statement.",
    ),
    "research/selected-stock-shape-a-zero/PROOF.md": (
        "holds for every atom width w >= 1 with **A = 0** and **B = 2642**.",
        "This is not a closed envelope: rho is still unbound, and adopting the finite",
    ),
}


def strict_json(path):
    def pairs(items):
        keys = [key for key, _value in items]
        need(len(keys) == len(set(keys)), "duplicate JSON key in " + str(path))
        return dict(items)
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs)


def git_blob(data):
    return sha1(b"blob %d\0" % len(data) + data).hexdigest()


def check_sources(manifest=None):
    manifest = manifest or strict_json(HERE / "SOURCES.json")
    need(manifest.get("base_commit") == BASE_COMMIT, "pinned base")
    count = 0
    for entry in manifest["files"]:
        data = (ROOT / entry["path"]).read_bytes()
        need(sha256(data).hexdigest() == entry["sha256"], "pinned sha256: " + entry["path"])
        need(git_blob(data) == entry["git_blob"], "pinned git blob: " + entry["path"])
        count += 1
    engine_files = {entry["path"] for entry in manifest["files"]
                    if entry["usage"] == "input" and entry.get("role") == "engine"}
    imported = {"research/physical-ordinary-interchange/" + path.name
                for path in highpart.ENGINE.glob("*.py")}
    need(imported <= engine_files, "every importable engine module is pinned")
    need({"research/physical-ordinary-interchange/inputs/pr2808.tar",
          "research/physical-ordinary-interchange/inputs/pr2809.tar"} <= engine_files,
         "engine source archives are pinned")
    return count


def check_citations():
    total = 0
    for path, phrases in CITATIONS.items():
        text = re.sub(r"\s+", " ", (ROOT / path).read_text(encoding="utf-8"))
        for phrase in phrases:
            need(phrase in text, "source citation: " + path + ": " + phrase[:50])
            total += 1
    selected = strict_json(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == SELECTED_KAPPA, "selected kappa unchanged")
    return total


def plan_summary(grid=PLAN_GRID):
    records = []
    reserve_active = 0
    for k, body in grid:
        record = highpart.plan_identities(k, body)
        reserve_active += record["reserve_active"]
        records.append(record)
    need(len(records) == len(grid) == 25, "5x5 (k,body) plan grid")
    need(all(r["calls"] == 1 for r in records), "exactly one high-part call")
    need(all(r["active_width"] == r["k"] for r in records), "active width is k")
    need(all(r["full_chunk_width"] == r["k"] + r["body"] for r in records),
         "full chunk width is k+body")
    need(reserve_active == 0, "reserve never active on the plan grid")
    return dict(shapes=len(records), calls_per_shape=1, reserve_active_calls=0,
                min_width_ratio=["%d/%d" % (r["width_ratio_num"], r["width_ratio_den"])
                                for r in records if r["k"] == 1 and r["body"] == 1][0],
                max_width_ratio=["%d/%d" % (r["width_ratio_num"], r["width_ratio_den"])
                                for r in records if r["k"] == 1 and r["body"] == 5][0],
                k_range=[1, 5], body_range=[1, 5])


def physical_summary():
    cases, by_shape = [], {}
    for q, k, body, reserve in PHYSICAL_CASES:
        out = highpart.run_highpart(q, k, body, reserve)
        expected = highpart.expected_full_chunk_endpoint(out["fields"])
        need(list(out["composed"]) == expected, "composed high-part equals full-chunk endpoint")
        final = bytearray(out["volume"])
        for source, target in enumerate(expected):
            final[target] = out["original"][source]
        need(bytes(final) == out["final"], "physical high-part payload endpoint")
        plan = highpart.plan_identities(k, body, reserve)
        need(out["signatures"][0] == tuple(plan["signature"]), "physical signature matches plan")
        record = dict(q=q, k=k, body=body, reserve=reserve, volume=out["volume"],
                      calls=1, active_width=k, full_chunk_width=k + body,
                      width_ratio="%d/%d" % (k + body, k),
                      signatures=[list(s) for s in out["signatures"]],
                      peaks=[list(p) for p in out["peaks"]],
                      final_sha256=sha256(out["final"]).hexdigest())
        cases.append(record)
        by_shape.setdefault((q, k, body), {})[reserve] = record
    for shape, pair in by_shape.items():
        need(sorted(pair) == [1, 3], "reserve extents 1 and 3 for every shape")
        one, three = pair[1], pair[3]
        need(one["peaks"] == three["peaks"], "internal peaks independent of parent reserve")
        need([[s[0] * 3, s[1], s[2]] for s in one["signatures"]] == three["signatures"],
             "reserve enters only the call prefix multiplicity")
        need(one["active_width"] == three["active_width"] == shape[1],
             "exact after-cost width is k")
        need(one["full_chunk_width"] == three["full_chunk_width"] == shape[1] + shape[2],
             "exact before-cost full-chunk width is k+body")
    return cases


def controls():
    rejected = []

    # Body-swap instead of high-part swap fails the full-chunk endpoint identity.
    fields = highpart.layout(1, 1, 1)
    body_first = highpart.field_index(fields, "D_body")
    body_second = highpart.field_index(fields, "H_body")
    wrong = highpart.swap_permutation(fields, body_first, body_second)
    if wrong != highpart.expected_full_chunk_endpoint(fields):
        rejected.append("body_swap_not_highpart")

    # Unequal high extents rejected at the engine admission boundary.
    try:
        bad_fields = list(fields)
        bad_fields[highpart.field_index(fields, "D_hi")] = ("D_hi", 4)
        highpart.swap_permutation(bad_fields, highpart.field_index(fields, "H_hi"),
                                  highpart.field_index(fields, "D_hi"))
    except ValueError as error:
        need("equal active extents" in str(error), "unequal highs rejected for the right reason")
        rejected.append("unequal_high_extents")

    native, engine = highpart.elementary_binary(2)
    fields = highpart.layout(1, 1, 2)
    extents = [extent for _label, extent in fields]
    volume = 1
    for extent in extents:
        volume *= extent
    reserve_index = highpart.field_index(fields, "Reserve")
    head = highpart.field_index(fields, "H_hi")
    reserve_digit = [highpart.digits(a, extents)[reserve_index] for a in range(volume)]
    try:
        highpart.one_call(engine, native, highpart.initial_payload(volume, 0x53), 1,
                          highpart.call_counts(fields, reserve_index, head),
                          highpart.swap_permutation(fields, reserve_index, head), reserve_digit)
    except ValueError as error:
        need("reserve coordinate" in str(error), "reserve-consuming control rejected for the right reason")
        rejected.append("reserve_consuming_call")

    # Omitting the high-part call leaves the identity permutation.
    identity = list(range(volume))
    if identity != highpart.expected_full_chunk_endpoint(highpart.layout(1, 1, 1)):
        rejected.append("omitted_highpart_call")

    need(rejected == ["body_swap_not_highpart", "unequal_high_extents",
                      "reserve_consuming_call", "omitted_highpart_call"],
         "all four controls rejected")
    return rejected


def evaluate(suite):
    sources = check_sources()
    citations = check_citations()
    if suite == "fitted":
        import fitted
        return dict(sources=sources, citations=citations, fitted=fitted.run())
    return dict(sources=sources, citations=citations, plan=plan_summary(),
                physical=physical_summary(), controls=controls())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("default", "fitted"), default="default")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--certificate", default=str(HERE / "CERTIFICATE.json"))
    args = parser.parse_args()
    result = evaluate(args.suite)
    path = Path(args.certificate)
    if args.write:
        certificate = strict_json(path) if path.exists() else {}
        certificate[args.suite] = result
        path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    certificate = strict_json(path)
    need(args.suite in certificate and certificate[args.suite] == result,
         "complete typed result matches CERTIFICATE.json: " + args.suite)
    if args.suite == "fitted":
        cases = result["fitted"]
        print("PASS_SELECTED_COMPLEX_HIGHPART_LEAF_FITTED cases=%d padded_ratio=%s own_rows=%d "
              "reserve_extents=1,2 parent_reserve_restored_through_C0" %
              (len(cases), cases[0]["padded_ratio"], cases[0]["own_rows"]))
        return
    plan = result["plan"]
    print("PASS_SELECTED_COMPLEX_HIGHPART_LEAF shapes=%d calls=1 active_width=k "
          "full_chunk_width=k+body width_ratios=%s..%s physical_cases=%d controls=%d "
          "S_leaf=1_realized_on_highpart_exchange no_new_kappa" %
          (plan["shapes"], plan["min_width_ratio"], plan["max_width_ratio"],
           len(result["physical"]), len(result["controls"])))


if __name__ == "__main__":
    main()
