#!/usr/bin/env python3
"""Non-self co-chart host alternatives on the flag-0 tail cut (answers #3683 OQ1).

On the published promote/add/restore at 5758/5759/5807, every ADD-source
register named in the window other than X0 holds the same host chart FULL at
the ADD, remains FULL after restore, has no destination after the channel
prefix, and shares the window's zero dirty-helper touches and zero endpoint
repayment. Those 47 registers are non-self co-chart host alternatives to S0
on the published word. Uniqueness among registers named by ADD 5759 alone is
preserved (only X0). Broader census: all 103 non-X0 X-registers are co-chart.

Read-only. Admission uses need(); checks stay active under -O.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_FLAG0_TAIL_COPIED_HOST flag=0 nonself_cochart=47 "
    "all_x_cochart_nonself=103 dirty_helper_touches=0 endpoint_repay=0 "
    "exemplar=X5 unique_add5759_owner=1 no_new_kappa"
)
INPUTS = (
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz",
    "research/p104-tail-side-correction-seed749717/CORRECTION-ROWS.json",
    "research/p104-tail-flag0-owner/RESULT.json",
    "research/p104-channel-touch-restoration-audit/CERTIFICATE.json",
)
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]
RANK8 = [499, 23, 232, 32, 112, 15, 7, 2]
SOURCE_INIT = [232]
TARGET_INIT: list[int] = []
PROMOTE = 5758
ADD = 5759
RESTORE = 5807
CHANNEL_LEN = 4058
SELECTED_KAPPA = "0.001672660197076918"

WINDOW_ADD_SOURCES = [
    "X0", "X5", "X6", "X7", "X10", "X11", "X13", "X15", "X18", "X19",
    "X21", "X24", "X27", "X28", "X30", "X31", "X32", "X33", "X35", "X36",
    "X38", "X39", "X40", "X42", "X43", "X46", "X47", "X49", "X50", "X53",
    "X57", "X60", "X63", "X65", "X66", "X69", "X73", "X76", "X81", "X83",
    "X87", "X90", "X92", "X93", "X94", "X95", "X97", "X100",
]
NONSELF = [name for name in WINDOW_ADD_SOURCES if name != "X0"]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 8_000_000, "input exceeds 8 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def read_json_gz(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 8_000_000, "gzip input exceeds 8 MB")
    return json.loads(gzip.decompress(raw), object_pairs_hook=pairs_unique)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def is_dirty_helper(name):
    if type(name) is not str or len(name) < 1:
        return False
    head, tail = name[0], name[1:]
    if head == "C" and tail == "":
        return True
    if head not in "DGQ":
        return False
    return tail.isdigit() and int(tail) <= 103


def walk_frames(program, initial, names):
    frames = {name: list(initial[name]) for name in names}
    destinations = {name: [] for name in names}
    for index, event in enumerate(program):
        need(type(event) is list and event, "event shape")
        op = event[0]
        if op == "transport":
            need(len(event) == 5, "transport arity")
            _op, reg, old, new, rank = event
            if reg in frames:
                need(old == frames[reg], "transport left its live frame at " + str(index))
                need(type(rank) is int and rank >= 0, "transport rank")
                frames[reg] = list(new)
                destinations[reg].append(index)
        elif op == "add":
            need(len(event) == 5, "add arity")
            _op, dest, _src, _coef, _chart = event
            if dest in frames:
                destinations[dest].append(index)
        elif op == "copy":
            need(len(event) >= 3, "copy arity")
            dest = event[1]
            if dest in frames:
                destinations[dest].append(index)
    return frames, destinations


def authenticate():
    sources = read_json(HERE / "SOURCES.json")
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    need(set(pinned) == set(INPUTS), "input inventory changed")
    for path, row in pinned.items():
        need(sha256(ROOT / path) == row["sha256"], "source hash " + path)


def evaluate():
    authenticate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    channel = read_json(ROOT / INPUTS[0])
    tail = read_json_gz(ROOT / INPUTS[1])
    rows = read_json(ROOT / INPUTS[2])
    owner_receipt = read_json(ROOT / INPUTS[3])
    touch = read_json(ROOT / INPUTS[4])

    need(tail["program"][:CHANNEL_LEN] == channel["program"], "tail prefix left the channel")
    need(channel["final_frames"]["X0"] == FULL, "channel X0 final")
    need(channel["final_frames"]["Y34"] == RANK8, "channel Y34 final")
    need(channel["initial_frames"]["X0"] == SOURCE_INIT, "channel X0 initial")
    need(channel["initial_frames"]["Y34"] == TARGET_INIT, "channel Y34 initial")
    need(tail["final_frames"]["X0"] == FULL, "tail X0 final")
    need(tail["final_frames"]["Y34"] == RANK8, "tail Y34 final")

    need(touch["claim_id"] == "p104-channel-touch-restoration-audit", "touch claim id")
    need(touch["flag0"]["source_frame_restored"] is False, "touch flag0 source")
    need(touch["flag0"]["target_frame_restored"] is False, "touch flag0 target")
    need(owner_receipt["event"] == ADD, "owner receipt event")
    need(owner_receipt["owner_assigned"] is False, "owner already assigned")
    need(owner_receipt["add"] == ["Y34", "X0", "-1/2"], "owner receipt add")

    program = tail["program"]
    need(len(program) > RESTORE, "program too short")
    need(program[PROMOTE] == ["transport", "Y34", RANK8, FULL, 1], "promote event")
    need(program[ADD] == ["add", "Y34", "X0", "-1/2", FULL], "add event")
    need(program[RESTORE] == ["transport", "Y34", FULL, RANK8, 1], "restore event")

    # Uniqueness among registers named by ADD 5759 alone (S0 fact retained).
    need({program[ADD][1], program[ADD][2]} == {"Y34", "X0"}, "add 5759 named set")
    need(program[ADD][2] == "X0", "self source on published ADD")

    track = [f"X{i}" for i in range(104)] + ["Y34"]
    frames_at_add, _ = walk_frames(program[: ADD + 1], tail["initial_frames"], track)
    frames_after, destinations = walk_frames(
        program[: RESTORE + 1], tail["initial_frames"], track
    )
    need(frames_at_add["X0"] == FULL, "X0 not FULL at add")
    need(frames_at_add["Y34"] == FULL, "Y34 not FULL at add")
    need(frames_after["X0"] == FULL, "X0 after restore")
    need(frames_after["Y34"] == RANK8, "Y34 after restore")
    need(frames_after["X0"] != SOURCE_INIT, "X0 repaid")
    need(frames_after["Y34"] != TARGET_INIT, "Y34 repaid")

    window = program[PROMOTE : RESTORE + 1]
    need(len(window) == 50, "window length")
    dirty_touches = 0
    add_count = 0
    transport_count = 0
    sources_first_seen = []
    seen = set()
    for event in window:
        for item in event:
            if is_dirty_helper(item):
                dirty_touches += 1
        if event[0] == "transport":
            transport_count += 1
        elif event[0] == "add":
            need(event[1] == "Y34", "window add destination")
            add_count += 1
            source = event[2]
            if source not in seen:
                seen.add(source)
                sources_first_seen.append(source)
    need(dirty_touches == 0, "dirty helper touched in window")
    need(add_count == 48, "window add count")
    need(transport_count == 2, "window transport count")
    need(sources_first_seen == WINDOW_ADD_SOURCES, "window ADD source order")
    need(len(NONSELF) == 47, "nonself count")

    # Non-self co-chart hosts among window-named ADD sources.
    for name in NONSELF:
        need(frames_at_add[name] == FULL, name + " not FULL at add")
        need(frames_after[name] == FULL, name + " not FULL after restore")
        after_channel = [i for i in destinations[name] if i >= CHANNEL_LEN]
        need(after_channel == [], name + " written after channel")
        need(destinations[name], name + " never written")
        need(destinations[name][-1] < CHANNEL_LEN, name + " last dest after channel")
        initial = tail["initial_frames"][name]
        need(frames_after[name] != initial, name + " repaid to initial")
        need(initial != FULL, name + " initial unexpectedly FULL")

    # Broader: every non-X0 X register is co-chart with the same zero-repay profile.
    all_x_nonself = 0
    for index in range(104):
        name = "X" + str(index)
        if name == "X0":
            continue
        need(frames_at_add[name] == FULL, name + " missing FULL at add")
        need(frames_after[name] == FULL, name + " missing FULL after restore")
        after_channel = [i for i in destinations[name] if i >= CHANNEL_LEN]
        need(after_channel == [], name + " X written after channel")
        need(frames_after[name] != tail["initial_frames"][name], name + " X repaid")
        all_x_nonself += 1
    need(all_x_nonself == 103, "all-X nonself count")

    row = rows["rows"][34]
    need(row["target"] == 34, "correction target")
    hits = [entry for entry in row["nonzero"] if entry["source"] == 0]
    need(len(hits) == 1 and hits[0]["coefficient"] == "-1/2", "correction coefficient")

    expected = {
        "schema_version": 1,
        "claim_id": "p104-flag0-tail-copied-host",
        "pinned_main": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "answers": "CrocSwap#3683 OQ1",
        "flag_index": 0,
        "source": 0,
        "target": 34,
        "source_register": "X0",
        "target_register": "Y34",
        "promote_event": PROMOTE,
        "add_event": ADD,
        "restore_event": RESTORE,
        "host_chart": FULL,
        "channel_final_x0": FULL,
        "channel_final_y34": RANK8,
        "schedule_family": "S_cochart",
        "self_owner_s0": "X0",
        "unique_owner_among_add_5759_named_registers": True,
        "window_add_source_count": 48,
        "window_add_sources_first_seen": WINDOW_ADD_SOURCES,
        "nonself_cochart_host_count": 47,
        "nonself_cochart_hosts": NONSELF,
        "all_x_cochart_nonself_count": 103,
        "dirty_helper_touches_in_window": 0,
        "endpoint_repay_x0_to_initial": False,
        "endpoint_repay_y34_to_initial": False,
        "endpoint_repay_any_nonself_cochart_host_to_initial": False,
        "nonself_hosts_full_at_add": True,
        "nonself_hosts_full_after_restore": True,
        "nonself_hosts_destination_events_after_channel": 0,
        "window_event_count": 50,
        "window_transport_count": 2,
        "window_add_count": 48,
        "exemplar_nonself_owner": "X5",
        "exemplar_schedule_id": "S_cochart_X5",
        "owner_kind": "nonself_cochart",
        "semantic_scope": "interpretive_cochart_host_on_published_word",
        "does_not_claim_vector_equality_with_x0": True,
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }
    need(certificate == expected, "certificate mismatch")
    need(certificate["selected_kappa"] == SELECTED_KAPPA, "kappa drift")
    return {
        "nonself_cochart": len(NONSELF),
        "all_x_cochart_nonself": all_x_nonself,
        "dirty_helper_touches": dirty_touches,
        "endpoint_repay": 0,
        "exemplar": "X5",
    }


def main():
    result = evaluate()
    need(result["nonself_cochart"] == 47, "nonself")
    print(MARKER)


if __name__ == "__main__":
    main()
