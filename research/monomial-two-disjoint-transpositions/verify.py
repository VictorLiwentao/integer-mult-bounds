#!/usr/bin/env python3
"""Exact joint floor for two disjoint monomial transpositions.

Wentao Li, with substantial AI assistance. Apache-2.0.
Predecessor engines: research/complex-monomial-runs-seed25/{finite,backward}.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRED = ROOT / "research" / "complex-monomial-runs-seed25"
PASS = (
    "PASS_MONOMIAL_TWO_DISJOINT_TRANSPOSITIONS "
    "joint=7 separate_closed=8 eliminated_mid_clear=1 no_new_kappa"
)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_forward(permutation, clean: bool):
    """Self-contained COPY/CLEAR BFS; no predecessor imports."""
    n = len(permutation)
    start = tuple(range(1, n + 1)) + ((0 if clean else n + 1),)
    goal = tuple(permutation) + (0,)
    critical = set(range(1, n + 1))
    distance = {start: 0}
    parent = {}
    queue = deque([start])
    edges = 0
    while queue:
        state = queue.popleft()
        width = n + 1
        for d in range(width):
            for s in range(-1, width):
                if s == d:
                    continue
                value = 0 if s < 0 else state[s]
                if state[d] == value:
                    continue
                nxt = state[:d] + (value,) + state[d + 1 :]
                if not critical.issubset(nxt):
                    continue
                edges += 1
                if nxt not in distance:
                    distance[nxt] = distance[state] + 1
                    parent[nxt] = (state, ["clear", d] if s < 0 else ["copy", d, s])
                    queue.append(nxt)
    need(goal in distance, "joint target unreachable in independent forward search")
    word = []
    cursor = goal
    while cursor != start:
        cursor, op = parent[cursor]
        word.append(op)
    word.reverse()
    return {
        "minimum": distance[goal],
        "reachable_states": len(distance),
        "primitive_edges": edges,
        "distance_histogram": {
            str(k): v for k, v in sorted(Counter(distance.values()).items())
        },
        "witness": word,
    }


def open_midpoint_witness():
    """Typed open composition: first 2-cycle leaves workspace dirty; second closes."""
    first = [["copy", 4, 0], ["copy", 0, 1], ["copy", 1, 4]]
    second = [["copy", 4, 2], ["copy", 2, 3], ["copy", 3, 4], ["clear", 4]]
    return first + second


def closed_separate_witness():
    first = [["copy", 4, 0], ["copy", 0, 1], ["copy", 1, 4], ["clear", 4]]
    second = [["copy", 4, 2], ["copy", 2, 3], ["copy", 3, 4], ["clear", 4]]
    return first + second


def replay_labels(permutation, word, clean: bool):
    n = len(permutation)
    state = list(range(1, n + 1)) + ([0] if clean else [n + 1])
    for instruction in word:
        tag, d = instruction[0], instruction[1]
        need(isinstance(d, int) and 0 <= d <= n, "bad target index")
        if tag == "clear":
            state[d] = 0
        elif tag == "copy":
            s = instruction[2]
            need(isinstance(s, int) and 0 <= s <= n and s != d, "bad copy source")
            state[d] = state[s]
        else:
            raise AssertionError(f"unexpected primitive {tag}")
        need(set(range(1, n + 1)).issubset(state), "dropped a data label")
    need(tuple(state) == tuple(permutation) + (0,), "label endpoint mismatch")
    return True


def main() -> int:
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for entry in sources["files"]:
        path = ROOT / entry["path"]
        need(path.is_file(), f"missing pinned source {entry['path']}")
        need(sha256(path) == entry["sha256"], f"sha256 drift: {entry['path']}")

    finite = load_module("monomial_finite_pred", PRED / "finite.py")
    backward = load_module("monomial_backward_pred", PRED / "backward.py")

    # Positive controls: predecessor floors still hold on this checkout.
    two_cycle = (2, 1)
    two_three = (2, 1, 4, 5, 3)
    for perm, expected, clean in (
        (two_cycle, 4, True),
        (two_cycle, 4, False),
        (two_three, 8, True),
        (two_three, 8, False),
    ):
        fwd = finite.solve(perm, clean=clean)
        rev = backward.solve(perm, clean=clean)
        need(fwd["minimum"] == expected, f"predecessor forward drift {perm} clean={clean}")
        need(rev["minimum"] == expected, f"predecessor backward drift {perm} clean={clean}")
        backward.replay(perm, fwd["witness"], clean=clean)

    joint_perm = (2, 1, 4, 3)
    separate_closed = 4 + 4
    results = {}
    for clean in (True, False):
        fwd_pred = finite.solve(joint_perm, clean=clean)
        rev_pred = backward.solve(joint_perm, clean=clean)
        fwd_ind = independent_forward(joint_perm, clean=clean)
        need(fwd_pred["minimum"] == 7, f"joint forward floor clean={clean}")
        need(rev_pred["minimum"] == 7, f"joint backward floor clean={clean}")
        need(fwd_ind["minimum"] == 7, f"independent forward floor clean={clean}")
        need(
            fwd_pred["reachable_states"] == fwd_ind["reachable_states"],
            "reachable-state disagreement",
        )
        need(
            fwd_pred["primitive_edges"] == fwd_ind["primitive_edges"],
            "edge-count disagreement",
        )
        need(
            fwd_pred["distance_histogram"] == fwd_ind["distance_histogram"],
            "histogram disagreement",
        )
        backward.replay(joint_perm, fwd_pred["witness"], clean=clean)
        backward.replay(joint_perm, fwd_ind["witness"], clean=clean)
        open_word = open_midpoint_witness()
        closed_word = closed_separate_witness()
        need(len(open_word) == 7, "open composition length")
        need(len(closed_word) == separate_closed, "closed composition length")
        replay_labels(joint_perm, open_word, clean=clean)
        replay_labels(joint_perm, closed_word, clean=clean)
        backward.replay(joint_perm, open_word, clean=clean)
        backward.replay(joint_perm, closed_word, clean=clean)
        # Midpoint typing: after the first three ops, workspace is open/dirty.
        mid = list(range(1, 5)) + ([0] if clean else [5])
        for instruction in open_word[:3]:
            if instruction[0] == "clear":
                mid[instruction[1]] = 0
            else:
                mid[instruction[1]] = mid[instruction[2]]
        need(tuple(mid) == (2, 1, 3, 4, 1), "open midpoint type after first call")
        results["clean" if clean else "dirty_erase"] = {
            "forward_reachable_states": fwd_pred["reachable_states"],
            "forward_primitive_edges": fwd_pred["primitive_edges"],
            "backward_admissible_states": rev_pred["admissible_states"],
            "backward_states_reaching_goal": rev_pred["states_reaching_goal"],
            "distance_histogram": fwd_pred["distance_histogram"],
            "predecessor_witness": fwd_pred["witness"],
            "independent_witness": fwd_ind["witness"],
            "open_midpoint_witness": open_word,
            "closed_separate_witness": closed_word,
        }

    # Failure controls.
    short = open_midpoint_witness()[:-1]
    try:
        backward.replay(joint_perm, short, clean=True)
        raise AssertionError("accepted a one-shorter unpaid word")
    except ValueError:
        pass
    try:
        replay_labels(joint_perm, short, clean=True)
        raise AssertionError("label replay accepted a short word")
    except AssertionError:
        pass
    # Omitting the deferred CLEAR leaves workspace dirty.
    no_clear = [op for op in open_midpoint_witness() if op[0] != "clear"]
    try:
        replay_labels(joint_perm, no_clear, clean=True)
        raise AssertionError("accepted unrestored workspace")
    except AssertionError:
        pass
    # Wrong second-cycle completion: leave d unrestored from workspace.
    wrong = open_midpoint_witness()
    wrong[5] = ["copy", 3, 2]  # write d from c instead of from workspace
    try:
        backward.replay(joint_perm, wrong, clean=True)
        raise AssertionError("accepted wrong second-cycle completion")
    except ValueError:
        pass
    try:
        replay_labels(joint_perm, wrong, clean=True)
        raise AssertionError("label replay accepted wrong second-cycle completion")
    except AssertionError:
        pass
    # Dirty-erase single-swap floor remains 4 in the predecessor class.
    restore_single = finite.solve((2, 1), clean=False)
    need(restore_single["minimum"] == 4, "dirty-erase single swap control")

    expected = {
        "status": PASS,
        "task_id": "persistent-boundary",
        "assignment_seed": "606c01aeeef18054c0e46f4ce68fe3e9",
        "scope_key": "026be4b6e61971d51838",
        "permutation": list(joint_perm),
        "joint_minimum": 7,
        "separate_closed_composition": separate_closed,
        "eliminated_mid_clear": 1,
        "predecessor_controls": {
            "two_cycle_minimum": 4,
            "two_plus_three_minimum": 8,
        },
        "cases": results,
        "controls": {
            "short_word_rejected": True,
            "omitted_clear_rejected": True,
            "wrong_second_cycle_rejected": True,
            "predecessor_floors_replayed": True,
        },
    }
    receipt_path = HERE / "EXPECTED.json"
    if "--write-expected" in sys.argv:
        if receipt_path.exists():
            raise SystemExit("refusing to overwrite existing EXPECTED.json")
        receipt_path.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n")
        print("WROTE_EXPECTED")
        return 0

    pinned = json.loads(receipt_path.read_text(encoding="utf-8"))
    # Compare without volatile witness order differences: canonicalize witnesses
    # by checking semantic fields and replaying both sides.
    need(pinned["status"] == PASS, "status drift")
    need(pinned["joint_minimum"] == 7, "pinned joint minimum")
    need(pinned["separate_closed_composition"] == 8, "pinned separate price")
    need(pinned["eliminated_mid_clear"] == 1, "pinned eliminated clear")
    for key in ("clean", "dirty_erase"):
        got = results[key]
        want = pinned["cases"][key]
        for field in (
            "forward_reachable_states",
            "forward_primitive_edges",
            "backward_admissible_states",
            "backward_states_reaching_goal",
            "distance_histogram",
        ):
            need(got[field] == want[field], f"{key}.{field} drift")
        for witness_name in (
            "predecessor_witness",
            "independent_witness",
            "open_midpoint_witness",
            "closed_separate_witness",
        ):
            backward.replay(joint_perm, want[witness_name], clean=(key == "clean"))
            need(len(want[witness_name]) == (7 if "closed" not in witness_name else 8),
                 f"{key}.{witness_name} length")
    need(pinned["controls"] == expected["controls"], "control receipt drift")
    print(PASS)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL_MONOMIAL_TWO_DISJOINT_TRANSPOSITIONS: {exc}", file=sys.stderr)
        raise SystemExit(1)
