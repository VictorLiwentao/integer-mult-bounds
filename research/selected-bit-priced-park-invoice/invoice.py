#!/usr/bin/env python3
"""Closed-form Tape-meter invoice for Callback.abort stack faces + rewinds.

Formulas are derived from the pinned PR2753 ``records.Tape.clear`` /
``Tape.rewind`` scans and checked against live meters. Parking-table
park+restore uses the published PR2769/PR2635 tariff
``steps = 5S + 7r + 3d`` (and matching reads/writes/moves).
"""

from __future__ import annotations


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rewind_charge(body_len):
    """Unit-meter charge of ``Tape.rewind`` from the blank after ``body_len`` symbols."""
    need(type(body_len) is int and body_len >= 0, "nonnegative body length")
    return {
        "reads": body_len + 1,
        "writes": 0,
        "moves": body_len + 2,
    }


def clear_charge(body_len):
    """Unit-meter charge of ``Tape.clear`` for a body of ``body_len`` symbols."""
    need(type(body_len) is int and body_len >= 0, "nonnegative body length")
    return {
        "reads": 3 * body_len + 3,
        "writes": body_len,
        "moves": 3 * body_len + 4,
    }


def add_charges(*parts):
    total = {"reads": 0, "writes": 0, "moves": 0}
    for part in parts:
        for key in total:
            total[key] += part[key]
    return total


def callback_abort_tape_charge(face_lengths, program_len, fields_len):
    """Tape-meter invoice of Callback.abort.

    ``face_lengths`` is the 4-tuple
    ``(pending.tape, pending.reverse, values.tape, values.reverse)`` body
    lengths at abort time. Program/fields contribute one ``rewind`` each.
    Arena rollback is outside the Tape meter (separate bank API).
    """
    need(len(face_lengths) == 4, "four Stack faces")
    parts = [clear_charge(length) for length in face_lengths]
    parts.append(rewind_charge(program_len))
    parts.append(rewind_charge(fields_len))
    return add_charges(*parts)


def park_restore_table_charge(total_bits, records, frames=1):
    """Published PR2769/PR2635 parking-table invoice for park+restore.

    ``S`` = total parked word bits, ``r`` = record count, ``d`` = frames.
    """
    need(total_bits >= 0 and records >= 0 and frames >= 0, "nonnegative parking sizes")
    s, r, d = total_bits, records, frames
    return {
        "steps": 5 * s + 7 * r + 3 * d,
        "reads": 10 * s + 14 * r + 6 * d,
        "writes": 4 * s + 4 * r + 2 * d,
        "moves": 8 * s + 8 * r + 2 * d,
    }


def interrupt_park_invoice(abort_tape, park_restore, returned_output_disposal=None):
    """Compose Callback.abort Tape charge with park+restore table charge.

    Interrupt pays no returned-output disposal (failed construction cleanup
    only). Pass ``returned_output_disposal`` only as a success-path control.
    """
    if returned_output_disposal is None:
        returned_output_disposal = {"reads": 0, "writes": 0, "moves": 0, "steps": 0}
    return {
        "abort_tape": dict(abort_tape),
        "park_restore": dict(park_restore),
        "returned_output_disposal": dict(returned_output_disposal),
        "interrupt_pays_output_disposal": False,
        "abort_tape_total": abort_tape["reads"] + abort_tape["writes"] + abort_tape["moves"],
        "park_restore_steps": park_restore["steps"],
    }
