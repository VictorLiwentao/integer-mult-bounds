#!/usr/bin/env python3
"""Independent equality-class scan of the flag-0 vector-equal host splice.

Does not import verify.py. Rebuilds the same five-event splice, tracks a
copy-created equality relation on register names, and rechecks: vector equality
of D0 with X0 at the ADD, outside-window dirt save/restore, unchanged window
length, zero in-window dirty touches, and zero endpoint repayment. Admission
uses need(); active under -O.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_FLAG0_TAIL_VECTOR_EQUAL_HOST_INDEPENDENT flag=0 host=D0 "
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
FULL = (1, 2, 4, 8, 16, 32, 64, 128, 256)
RANK8 = (499, 23, 232, 32, 112, 15, 7, 2)
SOURCE_INIT = (232,)
TARGET_INIT = ()
PUB_PROMOTE = 5758
PUB_ADD = 5759
PUB_RESTORE = 5807
CHANNEL_LEN = 4058
PREFIX = 3
SUFFIX = 2
ADDED = 5
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


def as_tuple(frame):
    need(type(frame) is list, "frame type")
    return tuple(frame)


def dirty_name(item):
    if type(item) is not str:
        return False
    if item == "C":
        return True
    if len(item) < 2 or item[0] not in "DGQ":
        return False
    return item[1:].isdigit()


def authenticate():
    sources = read_json(HERE / "SOURCES.json")
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    need(set(pinned) == set(INPUTS), "input inventory changed")
    for path, row in pinned.items():
        need(sha256(ROOT / path) == row["sha256"], "source hash " + path)


def splice(program):
    prefix = [
        ["zero", "C", list(FULL)],
        ["copy", "C", "D0", list(FULL)],
        ["copy", "D0", "X0", list(FULL)],
    ]
    suffix = [
        ["copy", "D0", "C", list(FULL)],
        ["erase", "C", list(FULL)],
    ]
    head = program[:CHANNEL_LEN]
    mid = program[CHANNEL_LEN : PUB_RESTORE + 1]
    tail = program[PUB_RESTORE + 1 :]
    out = head + prefix + mid + suffix + tail
    promote = PUB_PROMOTE + PREFIX
    add = PUB_ADD + PREFIX
    restore = PUB_RESTORE + PREFIX
    return out, promote, add, restore, prefix, suffix


class Equality:
    """Value-id equality: copy shares an id; overwrite allocates a fresh id.

    Saving D0 into C then overwriting D0 from X0 leaves C on the pre-overwrite
    id, so dirt restore via D0 <- C correctly breaks D0/X0 equality.
    """

    def __init__(self):
        self.value = {}
        self.next_id = 1

    def ensure(self, name):
        if name not in self.value:
            self.value[name] = self.next_id
            self.next_id += 1

    def fresh(self, name):
        self.value[name] = self.next_id
        self.next_id += 1

    def copy_eq(self, dest, src):
        self.ensure(src)
        self.value[dest] = self.value[src]

    def same(self, a, b):
        self.ensure(a)
        self.ensure(b)
        return self.value[a] == self.value[b]


def frame_walk(program, initial, names, cut):
    """Walk only the named registers. Full-witness Q/G charts are not a closed
    transport chain under copy annotations; this package only needs X0/Y34/D0/C.
    """
    frames = {}
    for name in names:
        if name == "C":
            frames[name] = None
        else:
            frames[name] = as_tuple(initial[name])
    for index, event in enumerate(program[:cut]):
        op = event[0]
        if op == "transport" and event[1] in frames:
            need(as_tuple(event[2]) == frames[event[1]], "transport at " + str(index))
            frames[event[1]] = as_tuple(event[3])
        elif op == "zero" and event[1] in frames:
            frames[event[1]] = as_tuple(event[2])
        elif op == "copy" and event[1] in frames:
            frames[event[1]] = as_tuple(event[3])
        elif op == "erase" and event[1] in frames:
            need(as_tuple(event[2]) == frames[event[1]], "erase at " + str(index))
            frames[event[1]] = None
    return frames


def evaluate():
    authenticate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    channel = read_json(ROOT / INPUTS[0])
    tail = read_json_gz(ROOT / INPUTS[1])
    rows = read_json(ROOT / INPUTS[2])
    owner_receipt = read_json(ROOT / INPUTS[3])
    touch = read_json(ROOT / INPUTS[4])

    need(tail["program"][:CHANNEL_LEN] == channel["program"], "prefix drift")
    need(as_tuple(channel["final_frames"]["D0"]) == FULL, "D0 final")
    need(touch["frame_restored_sources"] == 0, "touch sources")
    need(owner_receipt["owner_assigned"] is False, "owner gap")

    program = tail["program"]
    spliced, promote, add, restore, prefix, suffix = splice(program)
    need(ADDED == PREFIX + SUFFIX == 5, "cost")
    need(restore - promote + 1 == 50, "window length")
    need(spliced[CHANNEL_LEN: CHANNEL_LEN + PREFIX] == prefix, "prefix")
    need(spliced[restore + 1: restore + 1 + SUFFIX] == suffix, "suffix")
    need(spliced[add] == ["add", "Y34", "X0", "-1/2", list(FULL)], "add")

    # Value-id walk through the ADD.
    eq = Equality()
    for event in spliced[: add + 1]:
        op = event[0]
        if op == "copy":
            eq.copy_eq(event[1], event[2])
        elif op in ("transport", "add", "zero", "erase") and len(event) > 1:
            eq.fresh(event[1])
        # Source reads do not change value ids.
    need(eq.same("D0", "X0"), "equality class at add")
    # C holds the pre-overwrite D0 id, so it is not equal to X0 at the ADD.
    need(not eq.same("C", "X0"), "scratch collapsed into X0")
    # After the dirt-restore suffix copy D0 <- C, D0 leaves X0's class.
    eq_after = Equality()
    for event in spliced[: restore + 1 + SUFFIX]:
        op = event[0]
        if op == "copy":
            eq_after.copy_eq(event[1], event[2])
        elif op in ("transport", "add", "zero", "erase") and len(event) > 1:
            eq_after.fresh(event[1])
    need(not eq_after.same("D0", "X0"), "D0 still equal X0 after dirt restore")
    need(suffix[0] == ["copy", "D0", "C", list(FULL)], "restore event")

    tracked = ("X0", "Y34", "D0", "C")
    frames = frame_walk(spliced, tail["initial_frames"], tracked, add + 1)
    need(frames["X0"] == frames["D0"] == frames["Y34"] == FULL, "charts at add")
    frames_rest = frame_walk(spliced, tail["initial_frames"], tracked, restore + 1)
    need(frames_rest["X0"] == FULL and frames_rest["Y34"] == RANK8, "after restore")
    need(frames_rest["X0"] != SOURCE_INIT and frames_rest["Y34"] != TARGET_INIT, "repay")

    dirty = 0
    adds = 0
    for event in spliced[promote : restore + 1]:
        for item in event:
            if dirty_name(item):
                dirty += 1
        if event[0] == "add" and event[1] == "Y34":
            adds += 1
    need(dirty == 0, "window dirty")
    need(adds == 48, "adds")

    # Splice dirty names only D0 and C.
    foreign = 0
    for index in list(range(CHANNEL_LEN, CHANNEL_LEN + PREFIX)) + list(
        range(restore + 1, restore + 1 + SUFFIX)
    ):
        for item in spliced[index]:
            if dirty_name(item) and item not in ("D0", "C"):
                foreign += 1
    need(foreign == 0, "foreign dirty")

    hits = [e for e in rows["rows"][34]["nonzero"] if e["source"] == 0]
    need(len(hits) == 1 and hits[0]["coefficient"] == "-1/2", "coefficient")

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
        "window_length_events": 50,
        "window_length_unchanged": True,
        "dirty_helper_touches_in_window": 0,
        "vector_equal_at_add": True,
        "x0_frozen_through_add": True,
        "d0_frozen_from_copy_through_add": True,
        "d0_dirt_saved_before_overwrite": True,
        "d0_dirt_restored_after_window": True,
        "other_dirty_helpers_untouched_by_splice": True,
        "endpoint_repay_x0_to_initial": False,
        "endpoint_repay_y34_to_initial": False,
        "host_chart": list(FULL),
        "coefficient": "-1/2",
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }
    need(certificate == expected, "certificate mismatch")
    return True


def main():
    evaluate()
    print(MARKER)


if __name__ == "__main__":
    main()
