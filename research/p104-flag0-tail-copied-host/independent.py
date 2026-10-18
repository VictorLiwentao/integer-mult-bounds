#!/usr/bin/env python3
"""Independent index-list scan of non-self co-chart hosts on the flag-0 tail cut.

Rebuilds each tracked register's frame from its transport subsequence alone,
then checks the same co-chart census as verify.py. Imports neither verify.py
nor the native checker.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_FLAG0_TAIL_COPIED_HOST_INDEPENDENT flag=0 nonself_cochart=47 "
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


def transport_index(program, name):
    rows = []
    for index, event in enumerate(program):
        if event[0] == "transport" and event[1] == name:
            rows.append((index, event[2], event[3], event[4]))
    return rows


def frame_at(initial, transports, cutoff):
    frame = list(initial)
    last_dest = None
    for index, old, new, rank in transports:
        if index > cutoff:
            break
        need(old == frame, "transport left live frame")
        need(type(rank) is int and rank >= 0, "rank")
        frame = list(new)
        last_dest = index
    return frame, last_dest


def destination_events(program, name, cutoff):
    events = []
    for index, event in enumerate(program):
        if index > cutoff:
            break
        if event[0] == "transport" and event[1] == name:
            events.append(index)
        elif event[0] in ("add", "copy") and event[1] == name:
            events.append(index)
    return events


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
    owner_receipt = read_json(ROOT / INPUTS[3])
    touch = read_json(ROOT / INPUTS[4])

    need(tail["program"][:CHANNEL_LEN] == channel["program"], "tail prefix")
    need(touch["flag0"]["source_frame_restored"] is False, "touch source")
    need(touch["flag0"]["target_frame_restored"] is False, "touch target")
    need(owner_receipt["owner_assigned"] is False, "owner assigned")

    program = tail["program"]
    need(program[PROMOTE][0] == "transport" and program[PROMOTE][1] == "Y34", "promote")
    need(program[ADD] == ["add", "Y34", "X0", "-1/2", FULL], "add")
    need(program[RESTORE][0] == "transport" and program[RESTORE][1] == "Y34", "restore")

    window = program[PROMOTE : RESTORE + 1]
    dirty_touches = sum(
        1 for event in window for item in event if is_dirty_helper(item)
    )
    need(dirty_touches == 0, "dirty touches")

    sources_first_seen = []
    seen = set()
    add_count = 0
    transport_count = 0
    for event in window:
        if event[0] == "transport":
            transport_count += 1
        elif event[0] == "add":
            add_count += 1
            source = event[2]
            if source not in seen:
                seen.add(source)
                sources_first_seen.append(source)
    need(add_count == 48 and transport_count == 2, "window ops")
    need(sources_first_seen == WINDOW_ADD_SOURCES, "source order")

    x0_transports = transport_index(program, "X0")
    y34_transports = transport_index(program, "Y34")
    x0_at_add, _ = frame_at(tail["initial_frames"]["X0"], x0_transports, ADD)
    y34_at_add, _ = frame_at(tail["initial_frames"]["Y34"], y34_transports, ADD)
    x0_after, x0_last = frame_at(tail["initial_frames"]["X0"], x0_transports, RESTORE)
    y34_after, _ = frame_at(tail["initial_frames"]["Y34"], y34_transports, RESTORE)
    need(x0_at_add == FULL and y34_at_add == FULL, "charts at add")
    need(x0_after == FULL and y34_after == RANK8, "frames after restore")
    need(x0_after != SOURCE_INIT and y34_after != TARGET_INIT, "endpoint repay")
    need(x0_last is not None and x0_last < CHANNEL_LEN, "X0 last dest")

    for name in NONSELF:
        transports = transport_index(program, name)
        at_add, _ = frame_at(tail["initial_frames"][name], transports, ADD)
        after, last = frame_at(tail["initial_frames"][name], transports, RESTORE)
        need(at_add == FULL and after == FULL, name + " cochart")
        dests = destination_events(program, name, RESTORE)
        need(all(i < CHANNEL_LEN for i in dests), name + " post-channel write")
        need(last is not None and last < CHANNEL_LEN, name + " last transport")
        need(after != tail["initial_frames"][name], name + " repaid")

    all_x_nonself = 0
    for index in range(104):
        name = "X" + str(index)
        if name == "X0":
            continue
        transports = transport_index(program, name)
        at_add, _ = frame_at(tail["initial_frames"][name], transports, ADD)
        after, last = frame_at(tail["initial_frames"][name], transports, RESTORE)
        need(at_add == FULL and after == FULL, name + " all-X cochart")
        dests = destination_events(program, name, RESTORE)
        need(all(i < CHANNEL_LEN for i in dests), name + " all-X write")
        need(after != tail["initial_frames"][name], name + " all-X repay")
        all_x_nonself += 1
    need(all_x_nonself == 103, "all-X count")

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
    return {
        "nonself_cochart": 47,
        "all_x_cochart_nonself": all_x_nonself,
        "dirty_helper_touches": dirty_touches,
        "endpoint_repay": 0,
    }


def main():
    result = evaluate()
    need(result["nonself_cochart"] == 47, "nonself")
    print(MARKER)


if __name__ == "__main__":
    main()
