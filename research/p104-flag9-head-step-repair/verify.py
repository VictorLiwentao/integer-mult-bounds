#!/usr/bin/env python3
"""Read-only replay of the flag-9 head-step repair bill and its zero-mass floor.

Applies two changed schedules to the published 4,058-event P104 witness in
memory, runs the published native checker's complete validate() on each
(every native edge, every endpoint adapter, all 280 framed rows and the 72
dirty-helper restorations), recomputes the bill and the head co-hosting
facts, the head closure of every Y23 update, and the exact least-frame sweep
for zero added non-private rank mass in two models (private register relaxed,
and private register pinned to its published events), both order-preserving
and for every relocation slot of the delivering ADD. Admission uses need()
and stays active under python -O. Nothing is written.
"""

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("flag9_headstep", HERE / "headstep.py")
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)
need = H.need

FLAG_INDEX = 9
DELIVERY = 3124
LATE_SLOT = 3462
SELECTED_KAPPA = "0.001672660197076918"
PINNED_MAIN = "6f100d4bb5083f8c35d96fd95a539811c62f245c"
MARKER = (
    "PASS_P104_FLAG9_HEAD_STEP_REPAIR flag=9 head=196 delivering_update=3124 "
    "R0=order_preserving added_events=1 added_adds=0 added_transports=1 added_rank_mass=2 "
    "profile_delta=-H1+2H2+H4-H5 R1=relocated added_events=0 added_transports=0 added_rank_mass=2 "
    "profile_delta=-H5+H7 native_validate=PASS zero_mass_order_preserving=0/9 "
    "zero_mass_relocation_obstructed_relaxed=941/1114 zero_mass_relocation_obstructed_pinned=1114/1114 "
    "rank_mass_floor=2 no_new_kappa"
)


def receipt(root, cert, new_recipes):
    witness, bills, words = H.validate_repairs(root, "flag9_repair_check_native", cert["repairs"], new_recipes)
    flags = H.load_inputs(root)[3]
    helper = flags["helpers"][FLAG_INDEX]
    head = helper["basis"][0]
    source, target = "X%d" % helper["source"], "Y%d" % helper["target"]
    need((source, target, head) == ("X4", "Y23", 196), "flag 9 identity")
    program = witness["program"]
    floor = H.at_rank_floor(witness, program)
    need(len(floor) == len(witness["initial_frames"]) == 280, "every non-private register at its rank floor")

    updates = [i for i, e in enumerate(program) if e[0] == "add" and e[1] == target]
    cohost = {
        "published_target_updates": updates,
        "published_head_hosting_target_updates": [
            i for i in updates if H.hosts(H.frame_at(witness, program, target, i), head)],
        "published_source_spans_head_at_target_updates": [
            i for i in updates if H.hosts(H.frame_at(witness, program, source, i), head)],
        "published_source_delivery_into_target": H.deliveries(witness, program, target, source),
        "partner_row_writes": H.writes(program, program[DELIVERY][2]),
        "target_read_events": H.reads(program, target),
    }
    for name in ("R0", "R1"):
        prog = words[name]
        adds = [i for i, e in enumerate(prog) if e[0] == "add" and e[1] == target]
        delivery = H.deliveries(witness, prog, target, source)
        need(len(delivery) == 1, name + " single delivering update")
        u = delivery[0][0]
        src_frame = H.frame_at(witness, prog, source, u)
        cohost[name] = {
            "target_updates": adds,
            "cohosted_target_updates": [
                i for i in adds if H.hosts(H.frame_at(witness, prog, target, i), head)
                and H.hosts(H.frame_at(witness, prog, source, i), head)],
            "delivering_update": u,
            "delivering_update_event": prog[u],
            "update_chart_rank": H.rank(prog[u][4]),
            "source_frame_rank_at_update": len(src_frame),
            "source_spans_head_at_update": H.hosts(src_frame, head),
            "source_events_after_update": [i for i, e in enumerate(prog) if i > u and source in e[1:3]],
            "source_later_events_are_reads": all(
                e[0] == "add" and e[2] == source for i, e in enumerate(prog) if i > u and source in e[1:3]),
            "source_delivery_into_target": delivery,
        }

    relaxed, pinned = H.Least(witness, False), H.Least(witness, True)
    late = H.partner_frame_after(pinned, program, DELIVERY, LATE_SLOT)
    final = H.canon(witness["final_frames"][target])
    late_witness = {
        "slot_after_published": LATE_SLOT,
        "relaxed_partner_least_frame": list(H.partner_frame_after(relaxed, program, DELIVERY, LATE_SLOT)),
        "pinned_partner_least_frame": list(late),
        "pinned_basis_vectors_outside_target_final": [v for v in late if not H.hosts(final, v)],
    }
    return {
        "schema_version": 1,
        "claim_id": "p104-flag9-head-step-repair",
        "pinned_main": PINNED_MAIN,
        "flag_index": FLAG_INDEX,
        "source_register": source,
        "target_register": target,
        "basis_head": head,
        "repairs": cert["repairs"],
        "bill": bills,
        "head_cohosting": cohost,
        "forced_hosting": {
            "non_private_registers_at_rank_floor": len(floor),
            "head_closure_table": H.closure_table(witness, program, target, head),
            "least_frame_relaxed": {
                "order_preserving": H.order_preserving_sweep(relaxed, program, target, head),
                "relocation_scan": H.relocation_scan(relaxed, program, DELIVERY, head),
            },
            "least_frame_pinned": {
                "order_preserving": H.order_preserving_sweep(pinned, program, target, head),
                "relocation_scan": H.relocation_scan(pinned, program, DELIVERY, head),
            },
            "late_window_partner_frame": late_witness,
        },
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }


def admit(root, cert, new_recipes):
    got = json.loads(json.dumps(receipt(root, cert, new_recipes)))
    need(got == cert, "receipt differs from committed certificate")
    b, hc, fh = cert["bill"], cert["head_cohosting"], cert["forced_hosting"]
    r0, r1 = b["R0"], b["R1"]
    added = ("events", "scalar_adds", "transport_occurrences", "rank_mass")
    need([r0["added_" + k] for k in added] == [1, 0, 1, 2], "R0 bill")
    need(r0["profile_delta"] == {"1": -1, "2": 2, "4": 1, "5": -1}, "R0 profile delta")
    need(r0["register_mass_delta"] == {"D28": 2} and r0["private_events_unchanged"], "R0 surcharge sits on D28")
    need([r1["added_" + k] for k in added] == [0, 0, 0, 2], "R1 bill")
    need(r1["profile_delta"] == {"5": -1, "7": 1}, "R1 profile delta")
    need(r1["register_mass_delta"] == {"Y23": 2} and r1["private_events_unchanged"], "R1 surcharge sits on Y23")
    need(hc["published_target_updates"] == [74, 75, 76, 2070, 2160, 2296, 2640, 2826, 3124], "Y23 updates")
    need(hc["published_head_hosting_target_updates"] == [], "published word has no head-hosting update")
    need(hc["published_source_spans_head_at_target_updates"] == hc["published_target_updates"],
         "X4 spans the head at every Y23 update (generator-only drop)")
    need(hc["published_source_delivery_into_target"] == [[DELIVERY, "D28", "-1/2", "-1/2"]], "3124 delivers X4")
    need(hc["partner_row_writes"] == [2520, 3635] and hc["target_read_events"] == [], "commutation window")
    need(hc["R0"]["cohosted_target_updates"] == [DELIVERY] == [hc["R0"]["delivering_update"]], "R0 co-hosts at 3124")
    need(hc["R0"]["update_chart_rank"] == 4, "R0 chart is the published chart plus the head")
    u1 = hc["R1"]["delivering_update"]
    need(hc["R1"]["cohosted_target_updates"] == [u1] and hc["R1"]["update_chart_rank"] == 9, "R1 co-hosts in D28's full chart")
    for name in ("R0", "R1"):
        need(hc[name]["source_spans_head_at_update"] and hc[name]["source_frame_rank_at_update"] == 9, name + " source hosts")
        need(len(hc[name]["source_events_after_update"]) == 5 and hc[name]["source_later_events_are_reads"],
             name + " source still live")
        need(hc[name]["source_delivery_into_target"] == [[hc[name]["delivering_update"], "D28", "-1/2", "-1/2"]],
             name + " delivery")
    table = fh["head_closure_table"]
    need(len(table) == 9 and all(row["obstructions"] > 0 for row in table), "head closure blocks all nine updates")
    for model in ("least_frame_relaxed", "least_frame_pinned"):
        sweep = fh[model]["order_preserving"]
        need(len(sweep) == 9 and all(sweep.values()), model + " order-preserving zero mass blocked")
    relaxed = fh["least_frame_relaxed"]["relocation_scan"]
    need((relaxed["slots"], relaxed["obstructed_slots"], relaxed["feasible_slots"]) == (1114, 941, 173), "relaxed scan counts")
    need(relaxed["runs"][-1]["after_published_first"] == 3462 and relaxed["runs"][-1]["obstructions"] == [],
         "relaxed-feasible window starts after Y103's read at 3462")
    pinned = fh["least_frame_pinned"]["relocation_scan"]
    need((pinned["slots"], pinned["obstructed_slots"], pinned["feasible_slots"]) == (1114, 1114, 0), "pinned scan counts")
    need(pinned["runs"][-1]["after_published_first"] == 3462 and pinned["runs"][-1]["obstructions"] == [["final", "Y23"]],
         "pinned late window blocked by Y23's own final frame")
    lw = fh["late_window_partner_frame"]
    need(lw["relaxed_partner_least_frame"] == [] and len(lw["pinned_partner_least_frame"]) == 6
         and lw["pinned_basis_vectors_outside_target_final"], "late-window partner frame witness")
    need(cert["selected_kappa"] == SELECTED_KAPPA and cert["no_new_kappa"] is True, "kappa unchanged")
    return got


def main(root=ROOT):
    cert = H.loads((HERE / "CERTIFICATE.json").read_bytes())
    new_recipes = H.loads((HERE / "REPAIR-RECIPES.json").read_bytes())["recipes"]
    admit(root, cert, new_recipes)
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
