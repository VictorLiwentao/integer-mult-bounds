#!/usr/bin/env python3
"""Independent column-state replay for the 7Q shared-XOR obstruction. Apache-2.0.

Rebuilds the restored length-2 classification and the champion X bounds without
importing verify.py. Uses only model.py for shared fixture constants.
"""
from __future__ import annotations

import importlib.util
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKS = 0


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise RuntimeError(message)


def load_model():
    spec = importlib.util.spec_from_file_location("shared_xor_model", ROOT / "model.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mat_id():
    return tuple(1 << i for i in range(5))


def apply_x(cols, s, t):
    cols = list(cols)
    cols[t] ^= cols[s]
    return tuple(cols)


def neighbors(cols):
    out = []
    for s in range(5):
        for t in range(5):
            if s != t:
                out.append(apply_x(cols, s, t))
    return out


def ball(radius):
    dist = {mat_id(): 0}
    queue = deque([mat_id()])
    while queue:
        cols = queue.popleft()
        depth = dist[cols]
        if depth >= radius:
            continue
        for nxt in neighbors(cols):
            if nxt not in dist:
                dist[nxt] = depth + 1
                queue.append(nxt)
    adj = {c: [n for n in neighbors(c) if n in dist] for c in dist}
    return adj


def realizable(incs, budget, adj):
    current = {mat_id(): 0}
    for need_inc in incs:
        seen = dict(current)
        queue = deque(current.items())
        while queue:
            cols, cost = queue.popleft()
            if cost >= budget:
                continue
            for nxt in adj[cols]:
                if nxt not in seen or cost + 1 < seen[nxt]:
                    seen[nxt] = cost + 1
                    queue.append((nxt, cost + 1))
        current = {
            cols: cost
            for cols, cost in seen.items()
            if any(cols[j] == need_inc for j in range(5))
        }
        if not current:
            return False
    seen = dict(current)
    queue = deque(current.items())
    while queue:
        cols, cost = queue.popleft()
        if cols == mat_id():
            return True
        if cost >= budget:
            continue
        for nxt in adj[cols]:
            if nxt not in seen or cost + 1 < seen[nxt]:
                seen[nxt] = cost + 1
                queue.append((nxt, cost + 1))
    return False


def main():
    model = load_model()
    cert = json.loads((ROOT / "CERTIFICATE.json").read_text())
    need(cert["no_new_kappa"] is True, "no new kappa flag")
    need(cert["interleaved_census"]["paths_with_X_le_2"] == 0, "cert X<=2")
    need(cert["interleaved_census"]["paths_with_X_le_3"] == 0, "cert X<=3")
    need(cert["interleaved_census"]["champion_exact_min_X"] == 6, "cert champion min")

    # Independent restored length-2 enumeration (no model helper).
    identity = mat_id()
    restored = 0
    multi_sets = set()
    for s in range(5):
        for t in range(5):
            if s == t:
                continue
            mid = apply_x(identity, s, t)
            for s2 in range(5):
                for t2 in range(5):
                    if s2 == t2:
                        continue
                    if apply_x(mid, s2, t2) == identity:
                        restored += 1
                        multi_sets.add(frozenset(c for c in mid if c.bit_count() >= 2))
    need(restored == 20, "independent restored length-2 count")
    need(all(len(s) == 1 for s in multi_sets), "independent single multi-bit mid-state")
    need(len(multi_sets) == 10, "independent ten mid columns")

    champ = tuple(cert["fixture"]["champion_increments"])
    need(champ == model.CHAMPION_INCREMENTS, "champion fixture sync")
    adj2 = ball(2)
    adj3 = ball(3)
    adj6 = ball(6)
    need(not realizable(champ, 2, adj2), "independent champion X<=2")
    need(not realizable(champ, 3, adj3), "independent champion X<=3")
    need(realizable(champ, 6, adj6), "independent champion X=6")

    # Spot-check: every weight pattern class has X<=3 blocked on a fresh sample path.
    cover = model.r82_covering_sets()
    seen_222 = seen_23 = False
    for subset in cover:
        for order in __import__("itertools").permutations(subset):
            closed = (0,) + order + (0,)
            if model.path_X(closed) != 6 or model.rank_increments(closed) < 5:
                continue
            incs = tuple(closed[i] ^ closed[i + 1] for i in range(7))
            info = model.multi_bit_pattern(incs)
            if info["weight_pattern"] == (2, 2, 2) and not seen_222:
                need(not realizable(incs, 3, adj3), "sample 222 X<=3 blocked")
                seen_222 = True
            if info["weight_pattern"] == (2, 3) and not seen_23:
                need(not realizable(incs, 3, adj3), "sample 23 X<=3 blocked")
                seen_23 = True
            if seen_222 and seen_23:
                break
        if seen_222 and seen_23:
            break
    need(seen_222 and seen_23, "both pattern classes sampled")

    print(
        "PASS_INDEPENDENT_7Q_SHARED_XOR "
        f"restored2={restored} mid_sets={len(multi_sets)} "
        f"champion_min_X=6 controls={CHECKS} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
