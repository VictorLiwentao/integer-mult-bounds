#!/usr/bin/env python3
"""Vector-equal dirty-helper host for flag-0 tail under an outside-window dirt splice.

Construct word W' from the published #2089 tail by splicing five events around
the promote/add/restore window: save D0's restored dirt into scratch C, copy
X0 onto D0 (vector equality), run the unchanged window, then restore D0 from C
and erase C. Schedule S_D0 assigns owner=D0 on host chart FULL at the ADD.
Window length stays 50; dirty-helper touches inside the window stay 0; X0/Y34
endpoint repayment toward initials stays false. Answers the strong form of
#3683 OQ1 (vector-equal dirty-helper copy, not interpretive co-chart) and the
dirt-restore half of #3683 OQ2 (displaced D0 dirt restored outside the window).

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
    "PASS_P104_FLAG0_TAIL_VECTOR_EQUAL_HOST flag=0 host=D0 "
    "added_events=5 window_len=50 dirty_helper_touches=0 "
    "vector_equal=1 dirt_restored=1 endpoint_repay=0 no_new_kappa"
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
PUB_PROMOTE = 5758
PUB_ADD = 5759
PUB_RESTORE = 5807
CHANNEL_LEN = 4058
PREFIX = 3
SUFFIX = 2
ADDED = PREFIX + SUFFIX
SELECTED_KAPPA = "0.001672660197076918"


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
    if name == "C":
        return True
    if len(name) < 2 or name[0] not in "DGQ":
        return False
    return name[1:].isdigit() and int(name[1:]) <= 103


def prefix_splice():
    return [
        ["zero", "C", list(FULL)],
        ["copy", "C", "D0", list(FULL)],
        ["copy", "D0", "X0", list(FULL)],
    ]


def suffix_splice():
    return [
        ["copy", "D0", "C", list(FULL)],
        ["erase", "C", list(FULL)],
    ]


def build_spliced(program):
    need(len(program) > PUB_RESTORE, "published program too short")
    head = program[:CHANNEL_LEN]
    mid = program[CHANNEL_LEN : PUB_RESTORE + 1]
    tail = program[PUB_RESTORE + 1 :]
    spliced = head + prefix_splice() + mid + suffix_splice() + tail
    promote = PUB_PROMOTE + PREFIX
    add = PUB_ADD + PREFIX
    restore = PUB_RESTORE + PREFIX
    need(spliced[promote] == program[PUB_PROMOTE], "promote drift under splice")
    need(spliced[add] == program[PUB_ADD], "add drift under splice")
    need(spliced[restore] == program[PUB_RESTORE], "restore drift under splice")
    need(len(mid) == PUB_RESTORE - CHANNEL_LEN + 1, "mid span")
    need(restore - promote == PUB_RESTORE - PUB_PROMOTE, "window length drift")
    return spliced, promote, add, restore


def destinations_through(program, names, cut_inclusive):
    dest = {name: [] for name in names}
    for index, event in enumerate(program[: cut_inclusive + 1]):
        need(type(event) is list and event, "event shape")
        op = event[0]
        if op in ("transport", "add", "copy", "zero", "erase") and len(event) > 1:
            reg = event[1]
            if reg in dest:
                dest[reg].append(index)
    return dest


def frames_at(program, initial, names, cut_inclusive):
    frames = {name: list(initial[name]) for name in names if name in initial}
    # Scratch C starts absent; treat as uninitialized until zero/copy.
    if "C" in names and "C" not in frames:
        frames["C"] = None
    for index, event in enumerate(program[: cut_inclusive + 1]):
        op = event[0]
        if op == "transport" and event[1] in frames:
            need(frames[event[1]] == event[2], "transport left live frame at " + str(index))
            frames[event[1]] = list(event[3])
        elif op == "zero" and event[1] in frames:
            frames[event[1]] = list(event[2])
        elif op == "copy" and event[1] in frames:
            frames[event[1]] = list(event[3])
        elif op == "erase" and event[1] in frames:
            need(frames[event[1]] == event[2], "erase left live frame at " + str(index))
            frames[event[1]] = None
    return frames


def dirty_touches(program, start, end):
    count = 0
    for event in program[start : end + 1]:
        for item in event:
            if is_dirty_helper(item):
                count += 1
    return count


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
    need(channel["final_frames"]["D0"] == FULL, "channel D0 final")
    need(channel["initial_frames"]["D0"] == [], "channel D0 initial")
    need(touch["flag0"]["source_frame_restored"] is False, "touch flag0 source")
    need(owner_receipt["owner_assigned"] is False, "owner already assigned")
    need(owner_receipt["event"] == PUB_ADD, "owner receipt event")

    published = tail["program"]
    need(published[PUB_PROMOTE] == ["transport", "Y34", RANK8, FULL, 1], "promote event")
    need(published[PUB_ADD] == ["add", "Y34", "X0", "-1/2", FULL], "add event")
    need(published[PUB_RESTORE] == ["transport", "Y34", FULL, RANK8, 1], "restore event")
    need(dirty_touches(published, PUB_PROMOTE, PUB_RESTORE) == 0, "published window already dirty")

    # Published word has no post-channel dirty mentions and no X0 copy targets.
    for index, event in enumerate(published[CHANNEL_LEN:], CHANNEL_LEN):
        for item in event:
            need(not is_dirty_helper(item), "published post-channel dirty at " + str(index))
        need(not (event[0] == "copy" and len(event) > 2 and event[2] == "X0"),
             "published already copies X0")

    spliced, promote, add, restore = build_spliced(published)
    need(promote == PUB_PROMOTE + PREFIX, "promote index")
    need(add == PUB_ADD + PREFIX, "add index")
    need(restore == PUB_RESTORE + PREFIX, "restore index")
    need(restore - promote == PUB_RESTORE - PUB_PROMOTE, "window length")
    need(restore - promote + 1 == 50, "window event count")

    # Prefix splice shape and placement.
    need(spliced[CHANNEL_LEN: CHANNEL_LEN + PREFIX] == prefix_splice(), "prefix splice")
    need(spliced[restore + 1: restore + 1 + SUFFIX] == suffix_splice(), "suffix splice")
    need(ADDED == 5, "added cost constant")

    # Frames at ADD on the spliced word.
    tracked = ("X0", "Y34", "D0", "C")
    initial = dict(tail["initial_frames"])
    frames = frames_at(spliced, initial, tracked, add)
    need(frames["X0"] == FULL, "X0 chart at add")
    need(frames["Y34"] == FULL, "Y34 chart at add")
    need(frames["D0"] == FULL, "D0 chart at add")
    need(frames["C"] == FULL, "C chart at add")
    need(spliced[add][4] == frames["X0"] == frames["D0"] == frames["Y34"], "common chart")

    # Vector equality via destination freeze: after the X0->D0 copy, neither
    # X0 nor D0 is a destination again before/at the ADD, so the copy's equality
    # is preserved at the read.
    dest = destinations_through(spliced, ("X0", "D0", "C", "Y34"), restore + SUFFIX)
    copy_eq = CHANNEL_LEN + 2  # third prefix event: copy D0 <- X0
    need(spliced[copy_eq] == ["copy", "D0", "X0", list(FULL)], "equality copy")
    x0_after_copy = [i for i in dest["X0"] if i > copy_eq]
    d0_between = [i for i in dest["D0"] if copy_eq < i <= add]
    need(x0_after_copy == [] or min(x0_after_copy) > add, "X0 rewritten before add")
    # X0's last destination remains the channel write.
    need(max(i for i in dest["X0"] if i <= add) == 1486, "X0 last dest before add")
    need(d0_between == [], "D0 rewritten between equality copy and add")
    vector_equal = True

    # Window dirt and length.
    window_dirt = dirty_touches(spliced, promote, restore)
    need(window_dirt == 0, "dirty helper touched in window")
    adds = sum(
        1
        for event in spliced[promote : restore + 1]
        if event[0] == "add" and event[1] == "Y34"
    )
    need(adds == 48, "window add count")

    # Endpoint non-repayment after restore (before suffix, same as published).
    frames_after = frames_at(spliced, initial, tracked, restore)
    need(frames_after["X0"] == FULL, "X0 after restore")
    need(frames_after["Y34"] == RANK8, "Y34 after restore")
    need(frames_after["X0"] != SOURCE_INIT, "X0 repaid")
    need(frames_after["Y34"] != TARGET_INIT, "Y34 repaid")

    # Dirt restore of D0 after the window: suffix copy D0 <- C, then erase C.
    need(spliced[restore + 1] == ["copy", "D0", "C", list(FULL)], "dirt restore copy")
    need(spliced[restore + 2] == ["erase", "C", list(FULL)], "scratch erase")
    # Between save-copy (C <- D0) and dirt-restore, C is not rewritten.
    save_copy = CHANNEL_LEN + 1
    need(spliced[save_copy] == ["copy", "C", "D0", list(FULL)], "dirt save copy")
    c_between = [i for i in dest["C"] if save_copy < i < restore + 1]
    need(c_between == [], "scratch C rewritten before dirt restore")
    dirt_restored = True

    # Other dirty helpers (besides D0 and scratch C) never appear in the splice.
    splice_events = (
        list(range(CHANNEL_LEN, CHANNEL_LEN + PREFIX))
        + list(range(restore + 1, restore + 1 + SUFFIX))
    )
    other_dirty = 0
    for index in splice_events:
        for item in spliced[index]:
            if is_dirty_helper(item) and item not in ("D0", "C"):
                other_dirty += 1
    need(other_dirty == 0, "splice touched foreign dirty helper")

    # Coefficient unchanged.
    row = rows["rows"][34]
    hits = [entry for entry in row["nonzero"] if entry["source"] == 0]
    need(len(hits) == 1 and hits[0]["coefficient"] == "-1/2", "correction coefficient")

    expected = {
        "schema_version": 1,
        "claim_id": "p104-flag0-tail-vector-equal-host",
        "pinned_main": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "answers": "CrocSwap#3683 OQ1-strong / OQ2",
        "flag_index": 0,
        "source": 0,
        "target": 34,
        "source_register": "X0",
        "target_register": "Y34",
        "host_register": "D0",
        "scratch_register": "C",
        "schedule_id": "S_D0",
        "owner": "D0",
        "owner_kind": "dirty_helper_vector_equal_copy",
        "published_promote_add_restore": [PUB_PROMOTE, PUB_ADD, PUB_RESTORE],
        "spliced_promote_add_restore": [promote, add, restore],
        "prefix_splice_events": PREFIX,
        "suffix_splice_events": SUFFIX,
        "added_event_cost": ADDED,
        "window_length_events": restore - promote + 1,
        "window_length_unchanged": True,
        "dirty_helper_touches_in_window": 0,
        "vector_equal_at_add": vector_equal,
        "x0_frozen_through_add": True,
        "d0_frozen_from_copy_through_add": True,
        "d0_dirt_saved_before_overwrite": True,
        "d0_dirt_restored_after_window": dirt_restored,
        "other_dirty_helpers_untouched_by_splice": True,
        "endpoint_repay_x0_to_initial": False,
        "endpoint_repay_y34_to_initial": False,
        "host_chart": FULL,
        "coefficient": "-1/2",
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }
    need(certificate == expected, "certificate mismatch")
    need(certificate["selected_kappa"] == SELECTED_KAPPA, "kappa drift")
    return {
        "host": "D0",
        "added_events": ADDED,
        "window_len": restore - promote + 1,
        "dirty_helper_touches": window_dirt,
        "vector_equal": 1,
        "dirt_restored": 1,
        "endpoint_repay": 0,
    }


def main():
    result = evaluate()
    need(result["host"] == "D0", "host")
    need(result["vector_equal"] == 1, "vector equal")
    print(MARKER)


if __name__ == "__main__":
    main()
