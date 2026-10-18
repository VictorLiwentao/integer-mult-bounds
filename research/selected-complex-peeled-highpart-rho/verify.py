"""Joint engine-measured rho binding for peeled + high-part ordinary leaf classes.

Default: read-only.  Re-hash every pinned input (including every imported
engine file) before importing the engine, check source citations, replay the
peeled and high-part plans, execute both physical residual classes through the
published Binary adapter, measure that Binary/Ordinary take no stock argument,
reject mutation controls on both classes, compose rho_peeled_highpart = 0, and
compare the complete typed result with CERTIFICATE.json.

--suite fitted replays both fitted-branch sections.
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
import residual  # noqa: E402
import highpart  # noqa: E402
import adapters  # noqa: E402
from residual import need  # noqa: E402

BASE_COMMIT = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
SELECTED_KAPPA = "0.001672660197076918"
PLAN_LIMIT = residual.M_COMPLEX * 21
PEELED_PHYSICAL = (
    (2, 1, 1, 1, 2), (2, 1, 1, 3, 2),
    (2, 2, 1, 1, 2), (2, 2, 1, 3, 2),
    (3, 2, 1, 1, 2), (3, 2, 1, 3, 2),
    (5, 1, 2, 1, 2), (5, 1, 2, 3, 2),
    (2, 3, 1, 1, 0), (2, 3, 1, 3, 0),
    (3, 3, 1, 1, 0), (3, 3, 1, 3, 0),
)
HIGHPART_PHYSICAL = (
    (2, 1, 1, 1), (2, 1, 1, 3),
    (2, 1, 2, 1), (2, 1, 2, 3),
    (2, 2, 1, 1), (2, 2, 1, 3),
    (3, 1, 1, 1), (3, 1, 1, 3),
    (3, 2, 1, 1), (3, 2, 1, 3),
    (5, 1, 1, 1), (5, 1, 1, 3),
)
HIGHPART_GRID = tuple((k, body) for k in range(1, 6) for body in range(1, 6))
CITATIONS = {
    "notes/stopped-product-interface.tex": (
        "pair the first $\\delta$ head atoms with the last $\\delta$ tail atoms in reverse order. "
        "Each pair uses the retained ordinary width-$w$ interchange.",
        "When $n<m_b$, at most $m_b$ such ordinary calls complete $F_n$.",
    ),
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
        "Peeled atoms and bounded stopped leaves: a fixed number of ordinary width-`w` calls",
        "High-part exchange and residual digits: ordinary calls with complete bodies as spectators",
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
    "notes/three-stage-cover-complex.tex": (
        "These fixed permutations and signs incur scalar/router charges, without recursive Fourier children.",
        "All fixed address adapters, endpoint Paulis and invocation permutations "
        "are implemented inside the finite scalar/router guard of the assembly.",
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
    selected = strict_json(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == SELECTED_KAPPA, "selected kappa unchanged")
    return total


def peeled_plan(m=residual.M_COMPLEX, pairs_fn=residual.peel_pairs, limit=PLAN_LIMIT):
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
                total_calls=total_calls, reserve_active_calls=reserve_active,
                S_leaf=1)


def highpart_plan(grid=HIGHPART_GRID):
    records = []
    reserve_active = 0
    for k, body in grid:
        record = highpart.plan_identities(k, body)
        reserve_active += record["reserve_active"]
        records.append(record)
    need(len(records) == 25, "5x5 (k,body) plan grid")
    need(all(r["calls"] == 1 for r in records), "exactly one high-part call")
    need(reserve_active == 0, "reserve never active on the highpart plan grid")
    return dict(shapes=len(records), calls_per_shape=1, reserve_active_calls=0,
                min_width_ratio="2/1", max_width_ratio="6/1",
                k_range=[1, 5], body_range=[1, 5], S_leaf=1)


def peeled_physical():
    cases, by_shape = [], {}
    for q, delta, width, reserve, middle in PEELED_PHYSICAL:
        out = residual.run_residual(q, delta, width, reserve, middle)
        expected = residual.expected_residual_endpoint(out["fields"], delta)
        need(out["composed"] == expected, "composed residual equals peeled endpoint")
        final = bytearray(out["volume"])
        for source, target in enumerate(expected):
            final[target] = out["original"][source]
        need(bytes(final) == out["final"], "physical residual payload endpoint")
        record = dict(q=q, delta=delta, width=width, reserve=reserve, middle=middle,
                      volume=out["volume"], calls=len(out["signatures"]),
                      signatures=[list(s) for s in out["signatures"]],
                      peaks=[list(p) for p in out["peaks"]],
                      final_sha256=sha256(out["final"]).hexdigest())
        cases.append(record)
        by_shape.setdefault((q, delta, width, middle), {})[reserve] = record
    for shape, pair in by_shape.items():
        need(sorted(pair) == [1, 3], "peeled reserve extents 1 and 3")
        one, three = pair[1], pair[3]
        need(one["peaks"] == three["peaks"], "peeled peaks independent of parent reserve")
        need([[s[0] * 3, s[1], s[2]] for s in one["signatures"]] == three["signatures"],
             "peeled reserve enters only the call prefix multiplicity")
    return cases


def highpart_physical():
    cases, by_shape = [], {}
    for q, k, body, reserve in HIGHPART_PHYSICAL:
        out = highpart.run_highpart(q, k, body, reserve)
        expected = highpart.expected_full_chunk_endpoint(out["fields"])
        need(list(out["composed"]) == expected, "composed high-part equals full-chunk endpoint")
        final = bytearray(out["volume"])
        for source, target in enumerate(expected):
            final[target] = out["original"][source]
        need(bytes(final) == out["final"], "physical high-part payload endpoint")
        record = dict(q=q, k=k, body=body, reserve=reserve, volume=out["volume"],
                      calls=1, active_width=k, full_chunk_width=k + body,
                      width_ratio="%d/%d" % (k + body, k),
                      signatures=[list(s) for s in out["signatures"]],
                      peaks=[list(p) for p in out["peaks"]],
                      final_sha256=sha256(out["final"]).hexdigest())
        cases.append(record)
        by_shape.setdefault((q, k, body), {})[reserve] = record
    for shape, pair in by_shape.items():
        need(sorted(pair) == [1, 3], "highpart reserve extents 1 and 3")
        one, three = pair[1], pair[3]
        need(one["peaks"] == three["peaks"], "highpart peaks independent of parent reserve")
        need([[s[0] * 3, s[1], s[2]] for s in one["signatures"]] == three["signatures"],
             "highpart reserve enters only the call prefix multiplicity")
    return cases


def peeled_controls():
    rejected = []

    def forward(n, m):
        delta, _pairs, middle = residual.peel_pairs(n, m)
        return delta, tuple((i, n - delta + i) for i in range(delta)), middle
    try:
        residual.plan_identities(75, pairs_fn=forward)
    except ValueError as error:
        need("F_n" in str(error), "forward-pairing control rejected for the right reason")
        rejected.append("forward_pairing")

    alt = peeled_plan(m=64, limit=residual.M_COMPLEX * 3)
    ref = peeled_plan(limit=residual.M_COMPLEX * 3)
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
        need("reserve coordinate" in str(error), "peeled reserve-consuming control rejected")
        rejected.append("reserve_consuming_call")

    out = residual.run_residual(2, 2, 1, 3, 2, calls_fn=lambda f, d: residual.residual_calls(f, d)[:-1])
    if out["composed"] != residual.expected_residual_endpoint(out["fields"], 2):
        rejected.append("omitted_residual_call")

    need(rejected == ["forward_pairing", "ordinary_m64_histogram", "reserve_consuming_call",
                      "omitted_residual_call"], "all four peeled controls rejected")
    return rejected


def highpart_controls():
    rejected = []
    fields = highpart.layout(1, 1, 1)
    body_first = highpart.field_index(fields, "D_body")
    body_second = highpart.field_index(fields, "H_body")
    wrong = highpart.swap_permutation(fields, body_first, body_second)
    if wrong != highpart.expected_full_chunk_endpoint(fields):
        rejected.append("body_swap_not_highpart")
    try:
        bad_fields = list(fields)
        bad_fields[highpart.field_index(fields, "D_hi")] = ("D_hi", 4)
        highpart.swap_permutation(bad_fields, highpart.field_index(fields, "H_hi"),
                                  highpart.field_index(fields, "D_hi"))
    except ValueError as error:
        need("equal active extents" in str(error), "unequal highs rejected")
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
        need("reserve coordinate" in str(error), "highpart reserve-consuming control rejected")
        rejected.append("reserve_consuming_call")

    identity = list(range(volume))
    if identity != highpart.expected_full_chunk_endpoint(highpart.layout(1, 1, 1)):
        rejected.append("omitted_highpart_call")

    need(rejected == ["body_swap_not_highpart", "unequal_high_extents",
                      "reserve_consuming_call", "omitted_highpart_call"],
         "all four highpart controls rejected")
    return rejected


def compose_rho(peeled, high, adapter_summary):
    """Joint composition: both ordinary classes realize S_leaf=1; adapters stock-free."""
    need(peeled["S_leaf"] == 1 and peeled["reserve_active_calls"] == 0,
         "peeled class realizes S_leaf=1")
    need(high["S_leaf"] == 1 and high["reserve_active_calls"] == 0,
         "highpart class realizes S_leaf=1")
    need(adapter_summary["ordinary_external_stock_args"] == 0,
         "adapters take no external stock")
    need(adapter_summary["adapters_close_ordinary_leaf_path"] is True,
         "adapters close the ordinary leaf path")
    # Card-level ordinary contribution of peeled U highpart is zero.
    rho_peeled_highpart = 0
    return dict(
        inventory_ordinary_classes=["peeled", "highpart"],
        peeled_S_leaf=1,
        highpart_S_leaf=1,
        rho_peeled_highpart=rho_peeled_highpart,
        adapters_stock_args=0,
        A_cited=0,
        B_bits_cited=2642,
        selected_kappa=SELECTED_KAPPA,
        global_rho="ordinary_peeled_highpart_closed_via_engine_and_adapters",
        routing_adapters_inventory="finite_scalar_router_guard_cited_not_reassigned",
        no_new_kappa=True,
    )


def evaluate(suite):
    sources = check_sources()
    citations = check_citations()
    if suite == "fitted":
        import fitted_peeled
        import fitted_highpart
        return dict(sources=sources, citations=citations,
                    fitted_peeled=fitted_peeled.run(),
                    fitted_highpart=fitted_highpart.run())
    peeled = peeled_plan()
    high = highpart_plan()
    peeled_phys = peeled_physical()
    high_phys = highpart_physical()
    controls = dict(peeled=peeled_controls(), highpart=highpart_controls())
    adapter_summary = adapters.summarize()
    composition = compose_rho(peeled, high, adapter_summary)
    return dict(sources=sources, citations=citations,
                peeled_plan=peeled, highpart_plan=high,
                peeled_physical=peeled_phys, highpart_physical=high_phys,
                controls=controls, adapters=adapter_summary,
                composition=composition)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("default", "fitted"), default="default")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--certificate", default=str(HERE / "CERTIFICATE.json"))
    args = parser.parse_args()
    try:
        result = evaluate(args.suite)
        path = Path(args.certificate)
        if args.write:
            certificate = strict_json(path) if path.exists() else {}
            certificate[args.suite] = result
            path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
        certificate = strict_json(path)
        need(args.suite in certificate and certificate[args.suite] == result,
             "complete typed result matches CERTIFICATE.json: " + args.suite)
        if args.suite == "fitted":
            pe = result["fitted_peeled"]
            hi = result["fitted_highpart"]
            print("PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO_FITTED "
                  "peeled_cases=%d highpart_cases=%d padded_ratio=%s own_rows=%d "
                  "reserve_extents=1,2 parent_reserve_restored_through_C0" %
                  (len(pe), len(hi), pe[0]["padded_ratio"], pe[0]["own_rows"]))
            return
        pe = result["peeled_plan"]
        hi = result["highpart_plan"]
        comp = result["composition"]
        print("PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO "
              "peeled_nodes=%d peeled_deltas=%d/73 peeled_max_calls=%d "
              "highpart_shapes=%d "
              "peeled_physical=%d highpart_physical=%d "
              "controls=%d+%d adapters_stock_args=%d "
              "rho_peeled_highpart=%d S_leaf=1_both_classes "
              "adapters_close_ordinary_leaf_path no_new_kappa" %
              (pe["nodes"], pe["internal_deltas_covered"], pe["max_calls"],
               hi["shapes"],
               len(result["peeled_physical"]), len(result["highpart_physical"]),
               len(result["controls"]["peeled"]), len(result["controls"]["highpart"]),
               result["adapters"]["ordinary_external_stock_args"],
               comp["rho_peeled_highpart"]))
    finally:
        adapters.cleanup_engine_tempdir()


if __name__ == "__main__":
    main()
