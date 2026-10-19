#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact non-fibre key/Counter invoice for PR2753 routes.route_cube.

Meters decoration append_word, stripping read_word, high_key call count,
partition copy_key cells, and partition-local Counter lifetimes. Does not
meter fibre copy_bits and does not reprint the #3944 fibre formula.

Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDOR = ROOT / "research/selected-bit-recursive-caller/predecessor/vendor"

EXPECTED = {
    "append_word_calls": "H*d*d",
    "append_word_cells": "H*d*d*(L+1)",
    "read_word_calls": "H*d*d",
    "high_key_calls": "H",
    "partition_count_cap_gt_1": "d*d*L",
    "partition_count_cap_eq_1": 0,
    "copy_key_calls": "2*H*P",
    "copy_key_cells": "2*H*P*d*d*(L+1)",
    "counter_ctors": "3*P",
    "counter_decrements": "2*H*P",
    "counter_closes": "3*P",
    "L_identity": "arena.bits",
    "H_identity": "cap**(d*d)",
    "word_width_lemma": (
        "Every Arena key digit Word has exactly L payload cells before RIGHT; "
        "append_word therefore writes L bits plus one WORD_END per digit."
    ),
    "selected_decimal": "0.001672660197076918",
    "source_pr": 2753,
    "source_head": "7dba5452a4071a856a0b11cebdcd2d3b6bcd7659",
    "routes_sha256": "ed7dc3679451696ab1dd841146b215c9515a3eec5e4ff3763f33c315f1696ada",
    "fibre_pr": 3944,
    "not_fibre_formula": True,
    "not_high_key_numerical": True,
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_vendor():
    need(VENDOR.is_dir(), "missing PR2753 vendor tree")
    path = str(VENDOR)
    if path not in sys.path:
        sys.path.insert(0, path)
    import bitstream  # noqa: F401
    import records
    import routes
    import stream
    from counts import Count
    from directory import Context
    from records import Tape
    from words import Arena, Ring, ZERO, ONE

    return {
        "bitstream": bitstream,
        "records": records,
        "routes": routes,
        "stream": stream,
        "Count": Count,
        "Context": Context,
        "Tape": Tape,
        "Arena": Arena,
        "Ring": Ring,
        "ZERO": ZERO,
        "ONE": ONE,
    }


class Vocab:
    def __init__(self, q, dimension):
        self.q = q
        self.dimension = dimension
        self.bits = 2
        self.limit = 4

    def rank(self, _low):
        return None


def identity_low(dimension):
    return tuple(
        tuple(1 if i == j else 0 for j in range(dimension))
        for i in range(dimension)
    )


def identity_chart(dimension):
    return tuple(
        tuple(Fraction(1 if i == j else 0) for j in range(dimension))
        for i in range(dimension)
    )


def scale_chart(dimension, scale):
    return tuple(
        tuple(Fraction(scale if i == j else 0) for j in range(dimension))
        for i in range(dimension)
    )


def predicted(q, w, dimension, fibre_bits, arena_bits=None):
    need(q >= 3 and q % 2 == 1, "odd prime label q>=3")
    need(w >= 1 and dimension >= 1 and fibre_bits >= 1, "positive extents")
    modulus = q**w
    bits = arena_bits if arena_bits is not None else modulus.bit_length() + 1
    need(bits >= modulus.bit_length() + 1, "arena bits cover modulus margin")
    cap = modulus // q
    highs = cap ** (dimension * dimension)
    coords = dimension * dimension
    partitions = coords * bits if cap > 1 else 0
    word_cells = bits + 1  # L payload bits + WORD_END
    append_calls = highs * coords
    append_cells = append_calls * word_cells
    read_calls = highs * coords
    high_key_calls = highs
    copy_key_calls = 2 * highs * partitions
    copy_key_cells = copy_key_calls * coords * word_cells
    counter_ctors = 3 * partitions
    counter_decs = 2 * highs * partitions
    return {
        "q": q,
        "w": w,
        "dimension": dimension,
        "fibre_bits": fibre_bits,
        "modulus": modulus,
        "arena_bits": bits,
        "cap": cap,
        "highs": highs,
        "coords": coords,
        "partition_count": partitions,
        "append_word_calls": append_calls,
        "append_word_cells": append_cells,
        "read_word_calls": read_calls,
        "high_key_calls": high_key_calls,
        "copy_key_calls": copy_key_calls,
        "copy_key_cells": copy_key_cells,
        "counter_ctors": counter_ctors,
        "counter_decrements": counter_decs,
        "counter_closes": counter_ctors,
    }


def measure_route_cube(q, w, dimension, fibre_bits, chart=None, low=None):
    """Run pinned route_cube; meter non-fibre key/Counter sites only."""
    mods = load_vendor()
    routes = mods["routes"]
    records = mods["records"]
    stream = mods["stream"]
    Count = mods["Count"]
    Context = mods["Context"]
    Tape = mods["Tape"]
    Arena = mods["Arena"]
    Ring = mods["Ring"]
    ZERO = mods["ZERO"]
    ONE = mods["ONE"]

    pred = predicted(q, w, dimension, fibre_bits)
    arena = Arena(bits=pred["arena_bits"], capacity=1 << 20)
    modulus_word = arena.input(pred["modulus"])
    ring = Ring(modulus_word)
    vocab = Vocab(q, dimension)
    context = Context(ring, vocab)
    if low is None:
        low = identity_low(dimension)
    if chart is None:
        chart = identity_chart(dimension)
    route = routes.compile_route(low, chart, vocab)

    fibre = Count.literal(fibre_bits)
    source = Tape()
    for index in range(pred["highs"] * fibre_bits):
        source.append(ONE if index % 2 else ZERO)
    source.rewind()

    aw = {"calls": 0, "cells": 0}
    real_aw = records.append_word

    def metered_aw(tape, word):
        aw["calls"] += 1
        before = len(tape.cells)
        real_aw(tape, word)
        aw["cells"] += len(tape.cells) - before

    records.append_word = metered_aw
    routes.append_word = metered_aw

    rw = {"calls": 0}
    real_rw = records.read_word

    def metered_rw(tape, arena_arg):
        rw["calls"] += 1
        return real_rw(tape, arena_arg)

    records.read_word = metered_rw
    routes.read_word = metered_rw

    ck = {"calls": 0, "cells": 0}
    real_ck = routes.copy_key

    def metered_ck(source_tape, output, context_arg, selected=None, cursor=None):
        ck["calls"] += 1
        before = len(output.cells)
        bit = real_ck(source_tape, output, context_arg, selected, cursor)
        ck["cells"] += len(output.cells) - before
        return bit

    routes.copy_key = metered_ck

    hk = {"calls": 0}
    real_hk = routes.high_key

    def metered_hk(*args, **kwargs):
        hk["calls"] += 1
        return real_hk(*args, **kwargs)

    routes.high_key = metered_hk

    # Partition-local Counters only (routes.Counter). bitstream.Counter stays unpatched.
    RealCounter = stream.Counter
    ctr = {"ctors": 0, "decs": 0, "closes": 0}

    class MeteredCounter:
        def __init__(self, word):
            self._inner = RealCounter(word)
            ctr["ctors"] += 1

        @property
        def finished(self):
            return self._inner.finished

        def decrement(self):
            ctr["decs"] += 1
            return self._inner.decrement()

        def close(self):
            ctr["closes"] += 1
            return self._inner.close()

        def __getattr__(self, name):
            return getattr(self._inner, name)

    routes.Counter = MeteredCounter

    try:
        output = routes.route_cube(source, route, context, fibre)
        need(aw["calls"] == pred["append_word_calls"], "append_word calls")
        need(aw["cells"] == pred["append_word_cells"], "append_word cells")
        need(rw["calls"] == pred["read_word_calls"], "read_word calls")
        need(hk["calls"] == pred["high_key_calls"], "high_key calls")
        need(ck["calls"] == pred["copy_key_calls"], "copy_key calls")
        need(ck["cells"] == pred["copy_key_cells"], "copy_key cells")
        need(ctr["ctors"] == pred["counter_ctors"], "counter ctors")
        need(ctr["decs"] == pred["counter_decrements"], "counter decrements")
        need(ctr["closes"] == pred["counter_closes"], "counter closes")
        result = {
            **pred,
            "measured_append_word_calls": aw["calls"],
            "measured_append_word_cells": aw["cells"],
            "measured_read_word_calls": rw["calls"],
            "measured_high_key_calls": hk["calls"],
            "measured_copy_key_calls": ck["calls"],
            "measured_copy_key_cells": ck["cells"],
            "measured_counter_ctors": ctr["ctors"],
            "measured_counter_decrements": ctr["decs"],
            "measured_counter_closes": ctr["closes"],
            "chart_kind": (
                "identity" if chart == identity_chart(dimension) else "scaled"
            ),
        }
        output.clear()
        return result
    finally:
        records.append_word = real_aw
        routes.append_word = real_aw
        records.read_word = real_rw
        routes.read_word = real_rw
        routes.copy_key = real_ck
        routes.high_key = real_hk
        routes.Counter = RealCounter
        source.clear()
        fibre.close()
        context.close()
        ring.close()
        arena.free(modulus_word)


def word_width_check(arena_bits):
    """Arena Words expose exactly arena_bits payload cells before RIGHT."""
    mods = load_vendor()
    Arena = mods["Arena"]
    RIGHT = __import__("words", fromlist=["RIGHT"]).RIGHT
    arena = Arena(bits=arena_bits, capacity=64)
    samples = [arena.zero(), arena.literal(0), arena.literal(1), arena.literal((1 << (arena_bits - 1)) - 1)]
    try:
        for word in samples:
            word.rewind()
            width = 0
            while word.read() != RIGHT:
                width += 1
                word.step(1)
            word.rewind()
            need(width == arena_bits, "word payload width equals arena.bits")
        return arena_bits
    finally:
        for word in samples:
            arena.free(word)


FIXTURES = (
    {"q": 3, "w": 1, "dimension": 1, "fibre_bits": 5},
    {"q": 3, "w": 2, "dimension": 1, "fibre_bits": 4},
    {"q": 3, "w": 2, "dimension": 1, "fibre_bits": 3, "scale": 2},
    {"q": 3, "w": 3, "dimension": 1, "fibre_bits": 2},
    {"q": 3, "w": 2, "dimension": 2, "fibre_bits": 1},
    {"q": 5, "w": 2, "dimension": 1, "fibre_bits": 2},
)


def run_suite():
    rows = []
    for fixture in FIXTURES:
        scale = fixture.get("scale")
        chart = None
        if scale is not None:
            chart = scale_chart(fixture["dimension"], scale)
        row = measure_route_cube(
            fixture["q"],
            fixture["w"],
            fixture["dimension"],
            fixture["fibre_bits"],
            chart=chart,
        )
        rows.append(row)
    widths = {bits: word_width_check(bits) for bits in (3, 5, 6, 8)}
    return rows, widths
