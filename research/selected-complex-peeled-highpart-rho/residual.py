"""Selected m=73 complex peeled residual: exact plan and physical execution.

The plan is the source rule of notes/stopped-product-interface.tex at the
selected complex coarse size m=73: for n = 73 f + delta, the first delta head
atoms pair with the last delta tail atoms in reverse order, one completed
ordinary width-w interchange per pair; for n < 73 the same pairing covers all
n atoms.  Physical execution passes every call to the unchanged completed
ordinary binary interface of research/physical-ordinary-interchange.
"""
from pathlib import Path
import sys

M_COMPLEX = 73
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = ROOT / "research" / "physical-ordinary-interchange"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def peel_pairs(n, m=M_COMPLEX):
    """Return (delta, pairs, middle) for one node of n atoms per chunk."""
    need(type(n) is int and n >= 0 and type(m) is int and m >= 2, "admissible node")
    delta = n % m if n >= m else n
    pairs = tuple((i, n - 1 - i) for i in range(delta))
    middle = n - delta
    return delta, pairs, middle


def reversal_target(n, side, index):
    """F_n(H,D) = (C_n D, C_n H) with C_n the atom-order reversal."""
    return ("D" if side == "H" else "H"), n - 1 - index


def plan_identities(n, m=M_COMPLEX, pairs_fn=peel_pairs):
    """Exact atom-level checks for one node; returns a compact record."""
    delta, pairs, middle = pairs_fn(n, m)
    need(n < m or middle % m == 0 and middle >= m, "middle intervals are whole coarse blocks")
    need(len(pairs) == delta and delta <= m - 1, "at most m-1 ordinary residual calls")
    touched = set()
    for i, j in pairs:
        need(("H", i) not in touched and ("D", j) not in touched, "disjoint residual pairs")
        touched.update({("H", i), ("D", j)})
    head_middle = {("H", k) for k in range(delta, n)}
    tail_middle = {("D", k) for k in range(0, n - delta)}
    need(not (touched & (head_middle | tail_middle)), "residual avoids the coarse intervals")
    position = {(side, k): (side, k) for side in "HD" for k in range(n)}
    for i, j in pairs:
        position[("H", i)], position[("D", j)] = ("D", j), ("H", i)
    for k in range(middle):
        position[("H", delta + k)] = ("D", middle - 1 - k)
        position[("D", middle - 1 - k)] = ("H", delta + k)
    for key, value in position.items():
        need(value == reversal_target(n, *key), "peeled pairs plus coarse middle give F_n")
    # Stream positions: 0 Pre, 1 reserve, 2..n+1 H, n+2 Z, n+3..2n+2 D, 2n+3 Post.
    reserve_position, shapes, reserve_active, reserve_in_prefix = 1, [], 0, 0
    for i, j in pairs:
        first, second = 2 + i, n + 3 + j
        need(first < n + 2 < second <= 2 * n + 2, "active fields are one head and one tail atom")
        reserve_active += reserve_position in (first, second)
        reserve_in_prefix += reserve_position < first
        prefix_atoms, gap_atoms, suffix_atoms = first - 2, second - first - 2, 2 * n + 2 - second
        need(prefix_atoms + gap_atoms + suffix_atoms + 2 == 2 * n, "call covers the node stream")
        need(prefix_atoms == suffix_atoms, "reverse pairing is symmetric")
        shapes.append((prefix_atoms, gap_atoms, suffix_atoms))
    need(reserve_in_prefix + reserve_active == len(pairs), "reserve placement accounted for every call")
    return dict(n=n, delta=delta, middle=middle, calls=len(pairs),
                reserve_active_calls=reserve_active, shapes=shapes)


def layout(delta, width, reserve, middle_extent, spectators=(2, 2, 2)):
    """Materialized node stream with collapsed coarse intervals.

    Fields, most significant first:
    [Pre][Reserve][H_0..H_{d-1}][MH][Z][MD][D_{n-d}..D_{n-1}][Post].
    MH and MD stand for the two whole 73f-atom intervals; they are complete
    spectators of every residual call.  middle_extent=0 omits them (n < 73).
    """
    pre, z, post = spectators
    atom = 2 ** width
    fields = [("Pre", pre), ("Reserve", reserve)]
    fields += [("H%d" % i, atom) for i in range(delta)]
    if middle_extent:
        fields.append(("MH", middle_extent))
    fields.append(("Z", z))
    if middle_extent:
        fields.append(("MD", middle_extent))
    fields += [("Dr%d" % (delta - 1 - k), atom) for k in range(delta)]
    fields.append(("Post", post))
    return fields


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
    """target[source] for the exchange of two equal-extent fields."""
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


def residual_calls(fields, delta):
    """Ordered (first, second) field indices: H_i with D_{n-1-i}."""
    return [(field_index(fields, "H%d" % i), field_index(fields, "Dr%d" % i)) for i in range(delta)]


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
    """Run one residual call on a fresh borrowed payload; check every column.

    reserve_digit[address] is the parent-reserve coordinate of that address.
    """
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
             "every column follows the one ordinary pair exchange")
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


def run_residual(q, delta, width, reserve, middle_extent, seed=0x53, calls_fn=None):
    """Execute the whole peeled residual of one node, one call per pair."""
    native, engine = elementary_binary(q)
    fields = layout(delta, width, reserve, middle_extent)
    extents = [extent for _label, extent in fields]
    volume = 1
    for extent in extents:
        volume *= extent
    reserve_index = field_index(fields, "Reserve")
    reserve_digit = [digits(address, extents)[reserve_index] for address in range(volume)]
    data = initial_payload(volume, seed)
    original = data
    composed = list(range(volume))
    calls = (calls_fn or residual_calls)(fields, delta)
    peaks = set()
    signatures = []
    for first, second in calls:
        counts = call_counts(fields, first, second)
        need(first > reserve_index and second > reserve_index, "reserve is never an active field")
        need(counts[0] % reserve == 0, "reserve multiplicity lies in the call prefix")
        target = swap_permutation(fields, first, second)
        data, peak = one_call(engine, native, data, width, counts, target, reserve_digit)
        peaks.add(peak)
        signatures.append(counts)
        composed = [target[place] for place in composed]
    return dict(fields=fields, volume=volume, original=original, final=data, composed=composed,
                peaks=sorted(peaks), signatures=signatures)


def expected_residual_endpoint(fields, delta):
    """Independent endpoint: H_i <-> D_{n-1-i} for every peeled i, all else fixed."""
    extents = [extent for _label, extent in fields]
    names = [label for label, _extent in fields]
    volume = 1
    for extent in extents:
        volume *= extent
    target = [0] * volume
    for source in range(volume):
        values = dict(zip(names, digits(source, extents)))
        for i in range(delta):
            values["H%d" % i], values["Dr%d" % i] = values["Dr%d" % i], values["H%d" % i]
        target[source] = address_of([values[name] for name in names], extents)
    return target
