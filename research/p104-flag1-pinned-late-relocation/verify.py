#!/usr/bin/env python3
"""Read-only replay: the C-pinned least-frame sweep on flag 1's relocation window.

Loads the package's headstep.py (byte-identical to the deferred flag-9
package's harness, SHA-256 pinned here) and runs its exact least-frame model
for zero added non-private rank mass on flag 1's delivering ADD (event 2797,
Y7 += D17/4), with the private register C relaxed and pinned. It then locates
the private events that carry the late-window obstruction, and checks that
keeping any one of them blocks all 247 late slots while releasing exactly
those opens them. No repaired word is built. Admission uses need() and stays
active under python -O. Nothing is written.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HEADSTEP_SHA256 = "baad56ee042484681ad4c809bf9fc770a5a0f053ed72e1e2270f7e36898b22d8"


def _load_headstep():
    raw = (HERE / "headstep.py").read_bytes()
    if hashlib.sha256(raw).hexdigest() != HEADSTEP_SHA256:
        raise ValueError("headstep.py differs from the pinned flag-9 harness")
    spec = importlib.util.spec_from_file_location("flag1_late_headstep", HERE / "headstep.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


H = _load_headstep()
need = H.need

FLAG_INDEX = 1
DELIVERY = 2797
LATE_FIRST, LATE_LAST = 3366, 3612
CORE = [2480, 2482, 2504, 2511]
CHECKPOINTS = [2797, 3183, 3184, 3366, 3612]
SELECTED_KAPPA = "0.001672660197076918"
PINNED_MAIN = "6f100d4bb5083f8c35d96fd95a539811c62f245c"
MARKER = (
    "PASS_P104_FLAG1_PINNED_LATE_RELOCATION flag=1 head=232 delivering_update=2797 partner=D17 "
    "window=2497..3613 relaxed_obstructed=868/1115 late_open_in_3532=247 "
    "pinned_obstructed=1115/1115 late_pinned_obstructed=247/247 late_blocker=final(Y7) "
    "head_free_pinned_obstructed_after_3183=429/429 target_final=ker(61) "
    "core=2480,2482,2504,2511 single_core_pin_blocks_late=4/4 release_core_only_opens_late=247/247 "
    "rank_mass_floor=2_over_window_for_C_keeping_relocations no_new_kappa"
)


class PinnedSubset(H.Least):
    """C-pinned model that enforces only the private events named in keep (by event index)."""

    def __init__(self, witness, program, keep):
        super().__init__(witness, True)
        self.keep = {tuple(program[i][1:3]) for i in keep}

    def step(self, L, bad, i, e, head=None):
        if e[0] in ("add", "copy") and H.PRIVATE in e[1:3] and tuple(e[1:3]) not in self.keep:
            return
        super().step(L, bad, i, e, head)


def late(scan):
    """Per-slot obstruction count and obstruction sets over the late window."""
    blocked, total, sets = 0, 0, []
    for r in scan["runs"]:
        lo, hi = max(r["after_published_first"], LATE_FIRST), min(r["after_published_last"], LATE_LAST)
        if lo <= hi:
            total += hi - lo + 1
            if r["obstructions"]:
                blocked += hi - lo + 1
                if r["obstructions"] not in sets:
                    sets.append(r["obstructions"])
    return {"slots": total, "obstructed": blocked, "obstruction_sets": sets}


def annihilator(frame):
    ws = [w for w in range(1, 512) if all((w & x).bit_count() % 2 == 0 for x in frame)]
    need(len(ws) == 1, "target final frame is a hyperplane")
    return ws[0]


def chain(model, program, partner, final, until):
    """Backtrack the first event at which each register's least frame leaves final(target)."""
    L, bad = model.start()
    first = {}
    for i, e in enumerate(program[:until + 1]):
        if i == DELIVERY:
            continue
        model.step(L, bad, i, e)
        if e[0] in ("add", "copy"):
            for r, other in ((e[1], e[2]), (e[2], e[1])):
                if r != H.PRIVATE and r not in first and not H.within(L[r], final):
                    first[r] = (i, other)
    need(bad == [], "chain prefix feasible")
    out, r = [], partner
    while r in first:
        i, other = first[r]
        out.append([i] + program[i][:3])
        if other == H.PRIVATE:
            break
        r = other
    return out[::-1]


def receipt(root):
    witness, _fixture, _recipes, flags = H.load_inputs(root)
    helper = flags["helpers"][FLAG_INDEX]
    head = helper["basis"][0]
    source, target = "X%d" % helper["source"], "Y%d" % helper["target"]
    need((source, target, head) == ("X0", "Y7", 232), "flag 1 identity")
    program = witness["program"]
    partner = program[DELIVERY][2]
    final = H.canon(witness["final_frames"][target])
    floor = H.at_rank_floor(witness, program)
    need(len(floor) == len(witness["initial_frames"]) == 280, "every non-private register at its rank floor")
    private = [i for i, e in enumerate(program) if e[0] in ("add", "copy") and H.PRIVATE in e[1:3]]
    need(max(private) < DELIVERY, "every private ADD or copy precedes the delivering update")

    relaxed, pinned = H.Least(witness, False), H.Least(witness, True)
    scans = {
        "relaxed_with_head": H.relocation_scan(relaxed, program, DELIVERY, head),
        "pinned_with_head": H.relocation_scan(pinned, program, DELIVERY, head),
        "relaxed_head_free": H.relocation_scan(relaxed, program, DELIVERY, None),
        "pinned_head_free": H.relocation_scan(pinned, program, DELIVERY, None),
    }
    core = {}
    for p in CORE:
        model = PinnedSubset(witness, program, [p])
        core[str(p)] = {
            "event": program[p],
            "chart_parity_against_target_annihilator": [(annihilator(final) & x).bit_count() % 2 for x in program[p][-1]],
            "late_window": late(H.relocation_scan(model, program, DELIVERY, head)),
            "propagation_chain_to_partner": chain(model, program, partner, final, LATE_FIRST),
        }
    released = PinnedSubset(witness, program, [i for i in private if i not in CORE])
    return {
        "schema_version": 1,
        "claim_id": "p104-flag1-pinned-late-relocation",
        "pinned_main": PINNED_MAIN,
        "headstep_sha256": HEADSTEP_SHA256,
        "flag_index": FLAG_INDEX,
        "source_register": source,
        "target_register": target,
        "basis_head": head,
        "delivering_update": DELIVERY,
        "delivering_event": program[DELIVERY],
        "source_delivery_into_target": H.deliveries(witness, program, target, source),
        "partner_row_writes": H.writes(program, partner),
        "target_read_events": H.reads(program, target),
        "non_private_registers_at_rank_floor": len(floor),
        "private_add_copy_events": private,
        "target_final_frame": list(final),
        "target_final_annihilator": annihilator(final),
        "scans": scans,
        "late_window": {
            "after_published": [LATE_FIRST, LATE_LAST],
            **{name: late(scan) for name, scan in scans.items()},
        },
        "pinned_partner_least_frame": {
            str(t): {
                "frame": list(f),
                "outside_target_final": [v for v in f if not H.hosts(final, v)],
            }
            for t in CHECKPOINTS
            for f in [H.partner_frame_after(pinned, program, DELIVERY, t)]
        },
        "relaxed_partner_least_frame_after_3366": list(H.partner_frame_after(relaxed, program, DELIVERY, LATE_FIRST)),
        "late_core": {
            "events": CORE,
            "single_event_pin": core,
            "pin_all_but_core": late(H.relocation_scan(released, program, DELIVERY, head)),
        },
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }


def headline(cert):
    """Cheap checks of the committed claim, run before the replay."""
    need(cert["headstep_sha256"] == HEADSTEP_SHA256, "headstep pin")
    need((cert["flag_index"], cert["source_register"], cert["target_register"], cert["basis_head"])
         == (1, "X0", "Y7", 232), "flag 1 identity")
    need(cert["delivering_update"] == 2797 and cert["delivering_event"] == ["add", "Y7", "D17", "1/4", [95, 486]],
         "delivering update")
    need(cert["source_delivery_into_target"] == [[2797, "D17", "-1/2", "-1/2"]], "2797 delivers X0")
    need(cert["partner_row_writes"] == [2497, 3613] and cert["target_read_events"] == [], "commutation window")
    need(cert["non_private_registers_at_rank_floor"] == 280, "rank floor")
    s = cert["scans"]
    counts = {k: (v["slots"], v["obstructed_slots"]) for k, v in s.items()}
    need(counts == {"relaxed_with_head": (1115, 868), "pinned_with_head": (1115, 1115),
                    "relaxed_head_free": (1115, 0), "pinned_head_free": (1115, 458)}, "scan counts")
    need(s["relaxed_with_head"]["runs"][-1]["after_published_first"] == LATE_FIRST
         and s["relaxed_with_head"]["runs"][-1]["obstructions"] == [], "#3532's open window starts after 3366")
    lw = cert["late_window"]
    need(lw["relaxed_with_head"] == {"slots": 247, "obstructed": 0, "obstruction_sets": []}, "late window open when C relaxed")
    need(lw["pinned_with_head"] == {"slots": 247, "obstructed": 247, "obstruction_sets": [[["final", "Y7"]]]},
         "late window closed when C pinned, by final(Y7) alone")
    need(lw["pinned_head_free"]["obstructed"] == 247, "late window closed head-free")
    tail = s["pinned_head_free"]["runs"][-1]
    need((tail["after_published_first"], tail["after_published_last"], tail["slots"], tail["obstructions"])
         == (3184, 3612, 429, [["final", "Y7"]]), "head-free pinned obstruction from 3184")
    need(cert["target_final_annihilator"] == 61, "final(Y7) = ker(61)")
    pf = cert["pinned_partner_least_frame"]
    need(pf["3183"]["outside_target_final"] == [] and pf["3184"]["outside_target_final"] != []
         and pf["3366"]["outside_target_final"] == [32, 18, 6], "D17 leaves final(Y7) at the 3184 read")
    need(cert["relaxed_partner_least_frame_after_3366"] == [], "relaxed D17 frame empty late")
    core = cert["late_core"]
    need(core["events"] == CORE and sorted(core["single_event_pin"]) == [str(p) for p in CORE], "core events")
    for p, row in core["single_event_pin"].items():
        need(row["late_window"] == {"slots": 247, "obstructed": 247, "obstruction_sets": [[["final", "Y7"]]]},
             "pinning only %s blocks the late window" % p)
        need(row["chart_parity_against_target_annihilator"] == [1], "core chart %s is odd" % p)
        ch = row["propagation_chain_to_partner"]
        need(ch and ch[0][0] == int(p) and ch[0][3] == H.PRIVATE and ch[-1][3] == "D17", "chain %s reaches D17" % p)
    need(core["pin_all_but_core"] == {"slots": 247, "obstructed": 0, "obstruction_sets": []}, "releasing the core opens the window")
    need(cert["selected_kappa"] == SELECTED_KAPPA and cert["no_new_kappa"] is True, "kappa unchanged")


def admit(root, cert):
    headline(cert)
    got = json.loads(json.dumps(receipt(root)))
    need(got == cert, "receipt differs from committed certificate")
    return got


def main(root=ROOT):
    admit(root, H.loads((HERE / "CERTIFICATE.json").read_bytes()))
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
