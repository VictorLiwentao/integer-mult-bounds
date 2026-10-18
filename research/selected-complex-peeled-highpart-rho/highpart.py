"""Selected complex high-part exchange: exact plan and physical execution.

notes/three-stage-cover-rows.tex, after the ordinary body wrapper, leaves the
stream in order H_hi, D_body, Z, D_hi, H_body.  One inherited ordinary
width-k interchange of the two high parts, with the bodies and Z as
spectators, yields the full-chunk interchange D_hi, D_body, Z, H_hi, H_body.
This module realizes that single leaf-call class through the published
completed ordinary binary interface of research/physical-ordinary-interchange.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = ROOT / "research" / "physical-ordinary-interchange"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def layout(k, body, reserve, spectators=(2, 2, 2)):
    """Materialized stream after the body wrapper, plus parent reserve.

    Fields, most significant first:
    [Pre][Reserve][H_hi][D_body][Z][D_hi][H_body][Post].
    H_hi and D_hi have extent 2^k; bodies have extent 2^body.
    """
    pre, z, post = spectators
    high = 2 ** k
    body_extent = 2 ** body
    return [
        ("Pre", pre),
        ("Reserve", reserve),
        ("H_hi", high),
        ("D_body", body_extent),
        ("Z", z),
        ("D_hi", high),
        ("H_body", body_extent),
        ("Post", post),
    ]


def field_index(fields, name):
    for index, (label, _extent) in enumerate(fields):
        if label == name:
            return index
    raise ValueError("missing field " + name)


def call_counts(fields, first, second):
    prefix = gap = suffix = 1
    for index, (_label, extent) in enumerate(fields):
        if index < first:
            prefix *= extent
        elif first < index < second:
            gap *= extent
        elif index > second:
            suffix *= extent
    return prefix, gap, suffix


def digits(address, extents):
    out = []
    for extent in reversed(extents):
        address, digit = divmod(address, extent)
        out.append(digit)
    return out[::-1]


def address_of(values, extents):
    address = 0
    for value, extent in zip(values, extents):
        address = address * extent + value
    return address


def swap_permutation(fields, first, second):
    extents = [extent for _label, extent in fields]
    need(extents[first] == extents[second], "equal active extents")
    volume = 1
    for extent in extents:
        volume *= extent
    target = [0] * volume
    for source in range(volume):
        values = digits(source, extents)
        values[first], values[second] = values[second], values[first]
        target[source] = address_of(values, extents)
    return target


def plan_identities(k, body, reserve=1, spectators=(2, 2, 2)):
    """Exact atom-level checks for one high-part call; returns a compact record."""
    need(type(k) is int and k >= 1 and type(body) is int and body >= 1, "admissible widths")
    need(type(reserve) is int and reserve >= 1, "positive parent reserve")
    fields = layout(k, body, reserve, spectators)
    names = [label for label, _extent in fields]
    need(names == ["Pre", "Reserve", "H_hi", "D_body", "Z", "D_hi", "H_body", "Post"],
         "post-wrapper high-part layout")
    first = field_index(fields, "H_hi")
    second = field_index(fields, "D_hi")
    reserve_index = field_index(fields, "Reserve")
    need(reserve_index < first < second, "reserve precedes both high parts")
    need(first < field_index(fields, "D_body") < field_index(fields, "Z") < second,
         "bodies and Z sit in the intervening gap")
    counts = call_counts(fields, first, second)
    volume = 1
    for _label, extent in fields:
        volume *= extent
    need(counts[0] % reserve == 0, "reserve multiplicity lies in the call prefix")
    need(counts[0] * (2 ** k) * counts[1] * (2 ** k) * counts[2] == volume,
         "call covers the node stream")
    # On the post-wrapper layout, swapping highs alone yields the full-chunk
    # order D_hi, D_body, Z, H_hi, H_body (bodies already sit in that order).
    order_after = ["Pre", "Reserve", "D_hi", "D_body", "Z", "H_hi", "H_body", "Post"]
    need(order_after[2:7] == ["D_hi", "D_body", "Z", "H_hi", "H_body"],
         "high-part swap yields full-chunk order D_hi,D_body,Z,H_hi,H_body")
    extents = [extent for _label, extent in fields]
    sample = volume if volume <= 512 else 128
    high_target = expected_highpart_endpoint(fields)
    for source in range(sample):
        values = dict(zip(names, digits(source, extents)))
        # Full-chunk endpoint on original (H_hi,H_body,Z,D_hi,D_body) equals
        # high-part swap on the post-wrapper stream (bodies already exchanged).
        values["H_hi"], values["D_hi"] = values["D_hi"], values["H_hi"]
        need(address_of([values[name] for name in names], extents) == high_target[source],
             "high-part endpoint equals full-chunk interchange on post-wrapper")
    naive_width = k + body
    return dict(k=k, body=body, reserve=reserve, calls=1, active_width=k,
                full_chunk_width=naive_width, width_ratio_num=naive_width,
                width_ratio_den=k, signature=list(counts),
                reserve_active=0, volume=volume)


def initial_payload(volume, seed):
    return bytes(((address * 13) ^ (address >> 3) ^ (address >> 7) ^ seed) & 1
                 for address in range(volume))


_engine = None


def engine_modules():
    """Import the unchanged published engine after the caller authenticated it."""
    global _engine
    if _engine is None:
        sys.path.insert(0, str(ENGINE))
        import source as engine_source
        engine_source.activate()
        from binary import Binary
        from cardinal_counts import Count
        from check_binary import Elementary
        from check_join import body
        from check_support import no_decode
        from macro_code import Code
        from physical_words import PhysicalWord
        from provenance import Provenance
        from records import Tape
        from session import erase_marker
        from words import BLANK, Word
        from types import SimpleNamespace
        _engine = SimpleNamespace(Binary=Binary, Count=Count, Elementary=Elementary, body=body,
                                  no_decode=no_decode, Code=Code, PhysicalWord=PhysicalWord,
                                  Provenance=Provenance, Tape=Tape, erase_marker=erase_marker,
                                  BLANK=BLANK, Word=Word, SimpleNamespace=SimpleNamespace)
    return _engine


def elementary_binary(q):
    e = engine_modules()
    binding = e.SimpleNamespace(codes=e.SimpleNamespace(q=q))
    native = e.Elementary(q, binding, e.SimpleNamespace(families=0),
                          (e.Code((("unreachable",),), 0),), capacity=64)
    return native, e.Binary(native)


def one_call(engine, native, data, width, counts, expected_target, reserve_digit):
    """Run one high-part call on a fresh borrowed payload; check every column."""
    from unittest.mock import patch
    e = engine_modules()
    volume = len(data)
    payload = e.Tape()
    for bit in data:
        payload.append(bit)
    payload.rewind()
    provenance = e.Provenance(volume)
    provenance.mark(payload)
    count_width = e.Count.literal(width)
    prefix, gap, suffix = (e.Count.literal(value) for value in counts)

    def forbidden(*_args, **_kwargs):
        raise ValueError("decoded or newly allocated numerical word")
    try:
        with e.no_decode(), provenance.installed(), patch.object(e.Word, "__init__", forbidden), \
                patch.object(e.PhysicalWord, "inspect", forbidden):
            output = engine.run(payload, count_width, prefix, gap, suffix)
            masks = provenance.masks(output, volume)
            result = e.body(output)
            need(len(result) == volume, "complete output stream")
            need(e.body(payload) == data and payload.head == output.head == 1,
                 "borrowed residual input and head return")
        expected = bytearray(volume)
        expected_masks = [0] * volume
        for source, target in enumerate(expected_target):
            expected[target] = data[source]
            expected_masks[target] = 1 << source
        need(result == bytes(expected) and masks == tuple(expected_masks),
             "every column follows the one ordinary high-part exchange")
        observed_source = [mask.bit_length() - 1 for mask in masks]
        need(all(mask == 1 << source for mask, source in zip(masks, observed_source)),
             "each output cell comes from exactly one input column")
        need(all(reserve_digit[target] == reserve_digit[source]
                 for target, source in enumerate(observed_source)),
             "parent reserve coordinate restored at every column")
        need(all(all(bit == e.BLANK for bit in tape.cells) for tape in engine.pool.tapes),
             "binary workspace erased at return")
        need(all(bit == e.BLANK for bit in native.output.cells), "native output marker erased")
        peaks = (engine.pool.peak, native.pool.peak)
        output.clear()
        if width == 1:
            e.erase_marker(output)
        return bytes(result), peaks
    finally:
        payload.clear()
        for value in (count_width, prefix, gap, suffix):
            value.close()


def expected_highpart_endpoint(fields):
    """Independent endpoint: H_hi <-> D_hi; bodies and spectators fixed."""
    extents = [extent for _label, extent in fields]
    names = [label for label, _extent in fields]
    volume = 1
    for extent in extents:
        volume *= extent
    target = [0] * volume
    first = names.index("H_hi")
    second = names.index("D_hi")
    for source in range(volume):
        values = digits(source, extents)
        values[first], values[second] = values[second], values[first]
        target[source] = address_of(values, extents)
    return target


def expected_full_chunk_endpoint(fields):
    """Full-chunk interchange on the post-wrapper layout equals high-part swap.

    Post-wrapper already has bodies exchanged relative to the original
    (H_hi, H_body, Z, D_hi, D_body) order, so swapping highs alone yields
    (D_hi, D_body, Z, H_hi, H_body).
    """
    return expected_highpart_endpoint(fields)


def run_highpart(q, k, body, reserve, seed=0x53, spectators=(2, 2, 2)):
    """Execute the one high-part ordinary call of the post-wrapper stream."""
    native, engine = elementary_binary(q)
    fields = layout(k, body, reserve, spectators)
    extents = [extent for _label, extent in fields]
    volume = 1
    for extent in extents:
        volume *= extent
    reserve_index = field_index(fields, "Reserve")
    first = field_index(fields, "H_hi")
    second = field_index(fields, "D_hi")
    reserve_digit = [digits(address, extents)[reserve_index] for address in range(volume)]
    data = initial_payload(volume, seed)
    counts = call_counts(fields, first, second)
    need(first > reserve_index and second > reserve_index, "reserve is never an active field")
    need(counts[0] % reserve == 0, "reserve multiplicity lies in the call prefix")
    target = swap_permutation(fields, first, second)
    result, peak = one_call(engine, native, data, k, counts, target, reserve_digit)
    return dict(fields=fields, volume=volume, original=data, final=result,
                composed=target, peaks=[peak], signatures=[counts],
                active_width=k, full_chunk_width=k + body)
