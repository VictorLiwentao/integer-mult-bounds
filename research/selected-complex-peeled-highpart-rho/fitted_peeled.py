"""One peeled pair through the fitted, internally borrowing ordinary branch.

The fitted fixture of research/physical-ordinary-interchange borrows k=3 high
digits of its own width-5 field (R = 8 rows >= stock 6, padded to R' = 12) and
passes the caller prefix to C0 only as old_count.  Here the caller prefix is
the parent reserve of the complex node.  The observer checks that C0 returns
every column with its parent-reserve coordinate unchanged and that the padded
fresh-row ratio R'/R does not depend on the parent reserve extent.
"""
from fractions import Fraction
from unittest.mock import patch

import residual

FIXTURE = dict(width=1, depth=1, stock=6, rows=8, borrowed=3, body=2, remainder=0)
ATOM_WIDTH = 5


def run_case(reserve, gap):
    e = residual.engine_modules()
    import check_engine
    import scheduler
    engine = check_engine.fixture_engine()
    fields = [("Reserve", reserve), ("H0", 2 ** ATOM_WIDTH), ("Z", gap),
              ("Dr0", 2 ** ATOM_WIDTH), ("Post", 1)]
    extents = [extent for _label, extent in fields]
    volume = 1
    for extent in extents:
        volume *= extent
    data = residual.initial_payload(volume, 0x53)
    payload = e.Tape()
    for bit in data:
        payload.append(bit)
    payload.rewind()
    provenance = e.Provenance(volume)
    provenance.mark(payload)
    roots = []

    def observe(stage, padded, returned):
        if stage == "before":
            roots.append(dict(padded=e.body(padded), masks=provenance.masks(padded, len(e.body(padded)))))
            return
        record = roots[-1]
        length = len(record["padded"])
        residual.need(length % reserve == 0, "parent reserve is the leading C0 prefix factor")
        block = length // reserve
        position = {mask: place for place, mask in enumerate(record["masks"])
                    if mask and mask & (mask - 1) == 0 and mask < (1 << volume)}
        returned_masks = provenance.masks(returned, length)
        checked = 0
        for place, mask in enumerate(returned_masks):
            if mask in position:
                residual.need(place // block == position[mask] // block,
                              "C0 restores the parent-reserve coordinate")
                checked += 1
        residual.need(checked == volume, "every genuine column observed through C0")
        record.update(length=length, checked=checked)
        del record["padded"], record["masks"]

    engine.observe = observe

    def plan():
        return dict(fits=True, **{name: e.Count.literal(value) for name, value in FIXTURE.items()})

    def forbidden(*_args, **_kwargs):
        raise ValueError("fixture-only construction or decoding during execution")
    counts = residual.call_counts(fields, 1, 3)
    original, prefix, middle, tail = (e.Count.literal(value) for value in (ATOM_WIDTH, *counts))
    try:
        with e.no_decode(), provenance.installed(), patch.object(e.Word, "__init__", forbidden), \
                patch.object(e.PhysicalWord, "inspect", forbidden), \
                patch.object(scheduler.Invocation, "__init__", forbidden):
            output = engine.execute_plan(payload, original, prefix, middle, tail, plan)
            masks = provenance.masks(output, volume)
            result = e.body(output)
        target = residual.swap_permutation(fields, 1, 3)
        expected, expected_masks = bytearray(volume), [0] * volume
        for source, place in enumerate(target):
            expected[place], expected_masks[place] = data[source], 1 << source
        residual.need(result == bytes(expected) and masks == tuple(expected_masks),
                      "fitted residual call: complete independent-column endpoint")
        residual.need(engine.closed and engine.runtime.closed and engine.last_fitted is True,
                      "fitted branch closed")
        work = [*engine.pool.tapes, *engine.runtime.pool.tapes, *engine.runtime.roles.values(),
                *engine.runtime.handoff.values(), engine.runtime.output]
        for bank in (*engine.banks, engine.runtime.arena, engine.runtime.indices):
            residual.need(not bank.live and not bank.initialized, "closed encoded word banks")
            work.extend(word.tape for word in (*bank.words, bank.template))
        residual.need(all(all(bit == e.BLANK for bit in tape.cells) for tape in work),
                      "owned fitted work erased at return")
        residual.need(len(roots) == 2, "two padded C0 roots")
        ratios = [Fraction(root["length"], volume) for root in roots]
        own_rows = 2 ** FIXTURE["borrowed"]
        padded_rows = -(-own_rows // FIXTURE["stock"]) * FIXTURE["stock"]
        residual.need(FIXTURE["width"] * FIXTURE["body"] + FIXTURE["borrowed"] + FIXTURE["remainder"]
                      == ATOM_WIDTH, "borrowed rows are digits of the call's own field")
        residual.need(FIXTURE["stock"] <= own_rows <= padded_rows < 2 * own_rows,
                      "internal stock fits the call's own high field")
        residual.need(all(ratio == Fraction(padded_rows, own_rows) for ratio in ratios),
                      "padded fresh rows come only from the call's own high field")
        output.clear()
        return dict(reserve=reserve, gap=gap, columns=volume, signature=list(counts),
                    roots=len(roots), padded_ratio=str(ratios[0]), own_rows=own_rows,
                    padded_rows=padded_rows, outer_peak=engine.pool.peak,
                    inner_peak=engine.runtime.pool.peak)
    finally:
        payload.clear()
        for value in (original, prefix, middle, tail):
            value.close()


def run():
    cases = [run_case(1, 1), run_case(2, 1)]
    residual.need(cases[0]["padded_ratio"] == cases[1]["padded_ratio"] and
                  cases[0]["outer_peak"] == cases[1]["outer_peak"] and
                  cases[0]["inner_peak"] == cases[1]["inner_peak"],
                  "fitted internal resources independent of parent reserve extent")
    return cases
