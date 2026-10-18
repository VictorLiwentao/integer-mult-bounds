"""Verify the selected m=73 complex peeled residual through the completed ordinary engine.

Default: read-only.  Re-hash every pinned input (including every imported
engine file) before importing the engine, check source citations, replay the
exact residual plan for every n < 73*21, execute the physical residual cases,
reject four mutation controls, and compare the complete typed summary with
CERTIFICATE.json.  --suite fitted replays the slower fitted-branch section.
--write regenerates the selected certificate section.
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
import residual  # noqa: E402  (no engine import at module load)
from residual import need  # noqa: E402

PLAN_LIMIT = residual.M_COMPLEX * 21
PHYSICAL_CASES = (
    # q, delta, atom width, parent reserve extent, collapsed middle extent (0: n < 73 leaf)
    (2, 1, 1, 1, 2), (2, 1, 1, 3, 2),
    (2, 2, 1, 1, 2), (2, 2, 1, 3, 2),
    (3, 2, 1, 1, 2), (3, 2, 1, 3, 2),
    (5, 1, 2, 1, 2), (5, 1, 2, 3, 2),
    (2, 3, 1, 1, 0), (2, 3, 1, 3, 0),
    (3, 3, 1, 1, 0), (3, 3, 1, 3, 0),
)
CITATIONS = {
    "notes/stopped-product-interface.tex": (
        "pair the first $\\delta$ head atoms with the last $\\delta$ tail atoms in reverse order. "
        "Each pair uses the retained ordinary width-$w$ interchange.",
        "The remaining two contiguous $m_bf$-atom intervals receive the finite construction.",
        "When $n<m_b$, at most $m_b$ such ordinary calls complete $F_n$.",
    ),
    "research/selected-coarse-depth-stock/PROOF.md": (
        "A coarse node is internal exactly when `n >= m = 73`.",
        "Ordinary peeled atoms, routing, adapters and high-part exchanges are separate completed calls.",
        "S_parent(e,w) = C(w)^D(n) * S_leaf(e,w)",
        "If the full completed ordinary-leaf contract is available without an external reserve, "
        "one may take S_leaf=1.",
        "Actual A, B and rho are **not established here**.",
    ),
    "notes/three-stage-cover-rows.tex": (
        "Every completed call restores its row coordinate, so successive residuals and the outer "
        "wrapper reuse one reserve",
    ),
    "research/physical-ordinary-interchange/PROOF.md": (
        "where C_n reverses the n atom positions.",
        "I require no external fresh-row factor.",
        "old_count=P, depth=0, old_directory=empty,",
        "The complex supplier, selected bootstrap-stage adoption and analytic transfer remain separate.",
    ),
    "research/community-round8-audit/pr185-proof-reviewed.md": (
        "Peeled atoms and bounded stopped leaves: a fixed number of ordinary width-`w` calls",
        "restores preceding row coordinates",
    ),
    "research/selected-stock-envelope-m73/README.md": (
        "2. **Bind `rho`.** Find the complex analogue of the ordinary leaf reserve statement.",
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
    need(manifest.get("base_commit") == "6f100d4bb5083f8c35d96fd95a539811c62f245c", "pinned base")
    count = 0
    for entry in manifest["files"]:
        data = (ROOT / entry["path"]).read_bytes()
        need(sha256(data).hexdigest() == entry["sha256"], "pinned sha256: " + entry["path"])
        need(git_blob(data) == entry["git_blob"], "pinned git blob: " + entry["path"])
        count += 1
    engine_files = {entry["path"] for entry in manifest["files"]
                    if entry["usage"] == "input" and entry.get("role") == "engine"}
    imported = {"research/physical-ordinary-interchange/" + path.name
                for path in residual.ENGINE.glob("*.py")}
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
    return total


def plan_summary(m=residual.M_COMPLEX, pairs_fn=residual.peel_pairs, limit=PLAN_LIMIT):
    internal_deltas, max_calls, total_calls, reserve_active = set(), 0, 0, 0
    leaf_nodes = internal_nodes = 0
    for n in range(limit):
        record = residual.plan_identities(n, m, pairs_fn)
        if n >= residual.M_COMPLEX:
            internal_nodes += 1
            internal_deltas.add(record["delta"])
        else:
            leaf_nodes += 1
        max_calls = max(max_calls, record["calls"])
        total_calls += record["calls"]
        reserve_active += record["reserve_active_calls"]
    return dict(m=m, nodes=limit, leaf_nodes=leaf_nodes, internal_nodes=internal_nodes,
                internal_deltas_covered=len(internal_deltas), max_calls=max_calls,
                total_calls=total_calls, reserve_active_calls=reserve_active)


def physical_summary():
    cases, by_shape = [], {}
    for q, delta, width, reserve, middle in PHYSICAL_CASES:
        out = residual.run_residual(q, delta, width, reserve, middle)
        expected = residual.expected_residual_endpoint(out["fields"], delta)
        need(out["composed"] == expected, "composed residual equals H_i <-> D_{n-1-i} endpoint")
        final = bytearray(out["volume"])
        for source, target in enumerate(expected):
            final[target] = out["original"][source]
        need(bytes(final) == out["final"], "physical residual payload endpoint")
        if middle == 0:
            n = delta
            extents = [extent for _label, extent in out["fields"]]
            names = [label for label, _extent in out["fields"]]
            # Field "Dr%d" % i holds D_{n-1-i}.  F_n(H, D) = (rev D, rev H).
            for source in range(out["volume"]):
                values = dict(zip(names, residual.digits(source, extents)))
                head = [values["H%d" % i] for i in range(n)]
                tail = [values["Dr%d" % (n - 1 - j)] for j in range(n)]
                new_head, new_tail = tail[::-1], head[::-1]
                for i in range(n):
                    values["H%d" % i] = new_head[i]
                for j in range(n):
                    values["Dr%d" % (n - 1 - j)] = new_tail[j]
                need(residual.address_of([values[name] for name in names], extents) == expected[source],
                     "n<73 leaf: residual is the complete F_n")
        record = dict(q=q, delta=delta, width=width, reserve=reserve, middle=middle,
                      volume=out["volume"], calls=len(out["signatures"]),
                      signatures=[list(s) for s in out["signatures"]],
                      peaks=[list(p) for p in out["peaks"]],
                      final_sha256=sha256(out["final"]).hexdigest())
        cases.append(record)
        by_shape.setdefault((q, delta, width, middle), {})[reserve] = record
    for shape, pair in by_shape.items():
        need(sorted(pair) == [1, 3], "reserve extents 1 and 3 for every shape")
        one, three = pair[1], pair[3]
        need(one["peaks"] == three["peaks"], "internal peaks independent of parent reserve")
        need([[s[0] * 3, s[1], s[2]] for s in one["signatures"]] == three["signatures"],
             "reserve enters only the call prefix multiplicity")
    return cases


def controls():
    rejected = []

    def forward(n, m):
        delta, _pairs, middle = residual.peel_pairs(n, m)
        return delta, tuple((i, n - delta + i) for i in range(delta)), middle
    try:
        residual.plan_identities(75, pairs_fn=forward)
    except ValueError as error:
        need("F_n" in str(error), "forward-pairing control rejected for the right reason")
        rejected.append("forward_pairing")

    alt = plan_summary(m=64, limit=residual.M_COMPLEX * 3)
    ref = plan_summary(limit=residual.M_COMPLEX * 3)
    need(alt != ref, "m=64 residual histogram differs from the selected m=73 plan")
    rejected.append("ordinary_m64_histogram")

    native, engine = residual.elementary_binary(2)
    fields = residual.layout(1, 1, 2, 2)
    extents = [extent for _label, extent in fields]
    volume = 1
    for extent in extents:
        volume *= extent
    reserve_index = residual.field_index(fields, "Reserve")
    head = residual.field_index(fields, "H0")
    reserve_digit = [residual.digits(a, extents)[reserve_index] for a in range(volume)]
    try:
        residual.one_call(engine, native, residual.initial_payload(volume, 0x53), 1,
                          residual.call_counts(fields, reserve_index, head),
                          residual.swap_permutation(fields, reserve_index, head), reserve_digit)
    except ValueError as error:
        need("reserve coordinate" in str(error), "reserve-consuming control rejected for the right reason")
        rejected.append("reserve_consuming_call")

    out = residual.run_residual(2, 2, 1, 3, 2, calls_fn=lambda f, d: residual.residual_calls(f, d)[:-1])
    if out["composed"] != residual.expected_residual_endpoint(out["fields"], 2):
        rejected.append("omitted_residual_call")

    need(rejected == ["forward_pairing", "ordinary_m64_histogram", "reserve_consuming_call",
                      "omitted_residual_call"], "all four controls rejected")
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
        print("PASS_SELECTED_COMPLEX_PEELED_LEAF_FITTED cases=%d padded_ratio=%s own_rows=%d "
              "reserve_extents=1,2 parent_reserve_restored_through_C0" %
              (len(cases), cases[0]["padded_ratio"], cases[0]["own_rows"]))
        return
    plan = result["plan"]
    print("PASS_SELECTED_COMPLEX_PEELED_LEAF m=73 nodes=%d deltas=%d/73 max_calls=%d "
          "reserve_active_calls=%d physical_cases=%d controls=%d S_leaf=1_realized_on_peeled_residual "
          "no_new_kappa" % (plan["nodes"], plan["internal_deltas_covered"], plan["max_calls"],
                            plan["reserve_active_calls"], len(result["physical"]),
                            len(result["controls"])))


if __name__ == "__main__":
    main()
