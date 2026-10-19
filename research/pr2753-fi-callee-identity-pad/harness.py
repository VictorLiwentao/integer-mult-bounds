"""Shared GL2(F3) Node+padding harness for the F_I identity-weight claim.

Reuses the authenticated PR2753 predecessor archive and padding.complete from
selected-compatible-row-padding. Does not claim selected GL64 admission.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PADDING_PKG = REPO / "research" / "selected-compatible-row-padding"

BODY = 81
STOCK = 48
GENUINE_ROWS = 49
T2_ROWS = 96  # exact multiplicity t=2 with stock 48
IDENTITY = (1, 1)
WEIGHTED = (2, 1)


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def decode_count(count):
    return sum(bit << i for i, bit in enumerate(count.tape.cells[1:]) if bit in (0, 1))


def fi_destination(address, n=2, modulus=3, gap=1, suffix=1):
    """Unweighted F_I: head'_i = tail_(n-1-i), tail'_(n-1-i) = head_i."""
    address, s = divmod(address, suffix)
    address, tail = divmod(address, modulus**n)
    address, g = divmod(address, gap)
    outer, head = divmod(address, modulus**n)
    h, d = [0] * n, [0] * n
    for i in range(n - 1, -1, -1):
        head, h[i] = divmod(head, modulus)
        tail, d[i] = divmod(tail, modulus)
    new_h = [d[n - 1 - i] % modulus for i in range(n)]
    new_d = [0] * n
    for i in range(n):
        new_d[n - 1 - i] = h[i] % modulus
    head = tail = 0
    for a, b in zip(new_h, new_d):
        head = modulus * head + a
        tail = modulus * tail + b
    return ((((outer * modulus**n + head) * gap + g) * modulus**n + tail) * suffix + s)


def install_predecessor():
    """Authenticate and install the pinned padding predecessor."""
    # Drop cached package-local padding so it rebinds to this install's Count.
    for name in list(sys.modules):
        if name == "padding" or name.startswith("padding."):
            del sys.modules[name]
    if str(PADDING_PKG) not in sys.path:
        sys.path.insert(0, str(PADDING_PKG))
    import source as padding_source

    return padding_source.installed()


def run_padded_node(weights, rows, stock=STOCK):
    """Return (fi_mismatches, weight_mismatches, plan_padded, plan_added, children)."""
    with install_predecessor():
        import model
        import padding  # freshly rebound Count/Counter from this install
        from cardinal_counts import Count
        from check_nested_model import Topology
        from check_runtime import Tracker, destination as rt_destination
        from check_support import no_decode
        from directory import Context
        from low_codes import LowCodes
        from node import Node
        from records import Tape
        from words import Arena, Ring

        need(
            all(
                fi_destination(a) == rt_destination(a, 2, 3, IDENTITY)
                for a in range(BODY)
            ),
            "local F_I formula matches runtime destination at identity weights",
        )

        catalogue = model.Catalogue()
        catalogue.requests = (
            model.Request("MOVE", 0, 0),
            model.Request("MOVE", 1, 0),
        )
        catalogue.codes = LowCodes(3, 2, 2)
        topology = Topology(catalogue)
        arena, indices = Arena(3), Arena(8)
        modulus = arena.input(3)
        ring = Ring(modulus)
        context = Context(ring, catalogue.codes)
        size, depth = indices.input(2), indices.input(0)
        program = object()
        incoming = model.Incoming(context, indices, weights)
        consumer = model.Consumer(
            context, indices, program, size, depth, catalogue, incoming
        )
        node = Node(
            context, indices, program, size, depth, topology, consumer, incoming
        )
        tracker = Tracker()
        source_tape = tracker.source(rows * BODY)
        saved = bytes(source_tape.cells)
        old = Tape()
        old_count, before, gap, suffix = (Count.literal(1) for _ in range(4))
        prefixes, rows_c, stock_c, body_c = (
            Count.literal(v) for v in (1, rows, stock, BODY)
        )
        original_tape, original_scan = padding.Tape, padding.scan_rows
        padding.Tape = tracker.payload

        def annotated_scan(src, output, count, width, mode):
            if mode == "zero":
                tracker.last = 0
            return original_scan(src, output, count, width, mode)

        padding.scan_rows = annotated_scan

        def callee(padded, row_count):
            return node.run(padded, old, old_count, row_count, before, gap, suffix)

        try:
            with tracker.install(), no_decode():
                result = padding.complete(
                    source_tape, prefixes, rows_c, stock_c, body_c, callee
                )
            fi_bad = 0
            wt_bad = 0
            for address in range(rows * BODY):
                fi_tgt = rt_destination(address, 2, 3, IDENTITY)
                wt_tgt = rt_destination(address, 2, 3, weights)
                origin = result.origins.get(fi_tgt + 1)
                cell = result.cells[fi_tgt + 1]
                if origin != (1 << address) or cell != saved[address + 1]:
                    fi_bad += 1
                origin_w = result.origins.get(wt_tgt + 1)
                cell_w = result.cells[wt_tgt + 1]
                if origin_w != (1 << address) or cell_w != saved[address + 1]:
                    wt_bad += 1
            plan_p, plan_a = padding.plan_rows(Count.literal(rows), Count.literal(stock))
            padded_v, added_v = decode_count(plan_p), decode_count(plan_a)
            plan_p.close()
            plan_a.close()
            children = dict(sorted(consumer.children.items()))
            result.clear()
            return fi_bad, wt_bad, padded_v, added_v, children
        finally:
            padding.Tape, padding.scan_rows = original_tape, original_scan
            source_tape.clear()
            old.clear()
            for count in (
                old_count,
                before,
                gap,
                suffix,
                prefixes,
                rows_c,
                stock_c,
                body_c,
            ):
                count.close()
            incoming.close()


def plan_rows_census(stock=4, t_max=16):
    """Exact plan_rows on fitted multiples rows=t*stock for t=1..t_max."""
    with install_predecessor():
        import padding
        from cardinal_counts import Count

        rows_out = []
        # Instrument padding.Counter (already bound at import) for live peak.
        live = {"n": 0, "peak": 0}
        OriginalCounter = padding.Counter

        class PeakCounter(OriginalCounter):
            def __init__(self, *args, **kwargs):
                live["n"] += 1
                live["peak"] = max(live["peak"], live["n"])
                super().__init__(*args, **kwargs)

            def close(self):
                super().close()
                live["n"] -= 1

        padding.Counter = PeakCounter
        try:
            for t in range(1, t_max + 1):
                live["n"] = 0
                live["peak"] = 0
                rows = t * stock
                padded, added = padding.plan_rows(
                    Count.literal(rows), Count.literal(stock)
                )
                pv, av = decode_count(padded), decode_count(added)
                need(pv == rows and av == 0, f"exact multiple t={t}")
                rows_out.append(
                    {
                        "t": t,
                        "rows": rows,
                        "padded": pv,
                        "added": av,
                        "counter_peak": live["peak"],
                    }
                )
                padded.close()
                added.close()
            peaks = {row["counter_peak"] for row in rows_out}
            need(len(peaks) == 1, "counter live peak independent of multiplicity t")
            peak_live = next(iter(peaks))
            need(peak_live == 2, "plan_rows holds at most two live Counters")
        finally:
            padding.Counter = OriginalCounter
        return rows_out, peak_live


def weighted_oracle_fi_mismatches(rows=GENUINE_ROWS):
    """How many genuine columns the published (2,1) destination disagrees with F_I."""
    with install_predecessor():
        from check_runtime import destination as rt_destination

        bad = 0
        for address in range(rows * BODY):
            if rt_destination(address, 2, 3, WEIGHTED) != rt_destination(
                address, 2, 3, IDENTITY
            ):
                bad += 1
        return bad
