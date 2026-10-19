#!/usr/bin/env python3
"""Independent priced park/restore invoice on the interrupt path.

Answers open #4018 OQ2 / #3999 OQ3: machine-step charge for park/restore when
Callback stack faces are included. Uses pinned ``records.Tape`` meters and the
published PR2769 parking-table tariff. Does not import verify.py.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_BIT_PRICED_PARK_INVOICE "
    "callback_abort_tape_formula "
    "park_restore_table "
    "interrupt_no_output_disposal "
    "three_mutants "
    "no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
INPUTS = (
    "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/controller.py",
    "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/records.py",
    "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/words.py",
    "research/selected-bit-physical-caller/inputs/pr2769/vendor/parking_machine.py",
    "research/selected-bit-physical-caller/inputs/pr2769/PROOF.md",
    "research/selected-bit-physical-caller/numerical_frame.py",
    "docs/research/selected-bit-physical-contract-map.md",
)

sys.path.insert(0, str(HERE))
import invoice  # noqa: E402


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
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    need(
        manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "base pin",
    )
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    texts = {}
    for row in inputs:
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
        need(
            hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            == row["git_blob"],
            "git blob: " + row["path"],
        )
        texts[row["path"]] = raw.decode("utf-8")
    selected = read_json(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == KAPPA_DECIMAL, "selected decimal")
    return texts


def load_vendor():
    vendor = ROOT / (
        "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor"
    )
    parking = ROOT / "research/selected-bit-physical-caller/inputs/pr2769/vendor"
    # Prefer parking_machine then records/words from their vendor dirs.
    sys.path.insert(0, str(parking))
    sys.path.insert(0, str(vendor))
    import parking_machine  # noqa: WPS433
    import records  # noqa: WPS433
    import words  # noqa: WPS433

    return words, records, parking_machine


def body_len(tape):
    """Symbols between LEFT and the blank under the head after appends."""
    need(tape.head >= 1, "tape head")
    return tape.head - 1


def snap_meter(tape):
    return {
        "reads": tape.meter.reads,
        "writes": tape.meter.writes,
        "moves": tape.meter.moves,
    }


def delta_meter(tape, before):
    now = snap_meter(tape)
    return {key: now[key] - before[key] for key in before}


def formula_grid_matches_live_tape(words, records):
    """Exhaustive small-L check: rewind/clear formulas match ``records.Tape``."""
    Tape = records.Tape
    ZERO = words.ZERO
    for length in range(0, 13):
        tape = Tape()
        for _ in range(length):
            tape.append(ZERO)
        before = snap_meter(tape)
        tape.rewind()
        need(delta_meter(tape, before) == invoice.rewind_charge(length), "rewind L=" + str(length))
        tape2 = Tape()
        for _ in range(length):
            tape2.append(ZERO)
        before = snap_meter(tape2)
        tape2.clear()
        need(delta_meter(tape2, before) == invoice.clear_charge(length), "clear L=" + str(length))
    return True


def metered_callback_abort_invoice(words, records):
    """Build dirty Callback stacks and meter abort's four clears + two rewinds."""
    Arena = words.Arena
    Tape = records.Tape
    Stack = records.Stack
    VALUE = records.VALUE
    PAIR = records.PAIR
    CONSTANT = records.CONSTANT

    residue = Arena(bits=4, capacity=16)
    index = Arena(bits=4, capacity=16)
    program, fields = Tape(), Tape()
    program.append(words.ONE)
    fields.append(words.ZERO)
    fields.append(words.ONE)

    pending = Stack(index, residue)
    values = Stack(index, residue)
    pending.push(VALUE, residue.literal(1), residue.literal(1))
    values.push(PAIR, residue.literal(1))
    values.reverse.append(CONSTANT)

    face_lengths = (
        body_len(pending.tape),
        body_len(pending.reverse),
        body_len(values.tape),
        body_len(values.reverse),
    )
    program_len = body_len(program)
    fields_len = body_len(fields)
    expected = invoice.callback_abort_tape_charge(face_lengths, program_len, fields_len)

    faces = (pending.tape, pending.reverse, values.tape, values.reverse)
    befores = [snap_meter(tape) for tape in faces] + [snap_meter(program), snap_meter(fields)]
    for stack in (pending, values):
        stack.tape.clear()
        stack.reverse.clear()
    program.rewind()
    fields.rewind()
    observed = {"reads": 0, "writes": 0, "moves": 0}
    for tape, before in zip(faces + (program, fields), befores):
        part = delta_meter(tape, before)
        for key in observed:
            observed[key] += part[key]

    need(observed == expected, "abort tape meter matches closed form")
    need(pending.empty() and values.empty(), "stacks empty after abort clears")
    return {
        "face_lengths": list(face_lengths),
        "program_len": program_len,
        "fields_len": fields_len,
        "abort_tape": expected,
        "observed_abort_tape": observed,
    }


def park_restore_tariff_matches(parking_machine):
    """PR2769 table invoice equals begin + r·push(s) + r·pop(s) + end."""
    total_bits, records, frames = 12, 3, 1
    bit_width = total_bits // records
    need(bit_width * records == total_bits, "uniform record width")
    table = invoice.park_restore_table_charge(total_bits, records, frames)
    ops = [parking_machine.tariff("begin")]
    ops.extend(parking_machine.tariff("push", bit_width) for _ in range(records))
    ops.extend(parking_machine.tariff("pop", bit_width) for _ in range(records))
    ops.append(parking_machine.tariff("end"))
    summed = {"steps": 0, "reads": 0, "writes": 0, "moves": 0}
    for part in ops:
        for key in summed:
            summed[key] += part[key]
    need(summed == table, "tariff sum equals published table")
    return {
        "S": total_bits,
        "r": records,
        "d": frames,
        "park_restore": table,
    }


def success_path_output_disposal_control(abort_tape, park_restore):
    """Success path may charge returned-output disposal; interrupt does not."""
    disposal = {"reads": 5, "writes": 5, "moves": 5, "steps": 0}
    interrupt = invoice.interrupt_park_invoice(abort_tape, park_restore)
    success = invoice.interrupt_park_invoice(abort_tape, park_restore, disposal)
    need(interrupt["returned_output_disposal"]["reads"] == 0, "interrupt disposal zero")
    need(success["returned_output_disposal"]["reads"] == 5, "success disposal control")
    need(interrupt["interrupt_pays_output_disposal"] is False, "flag")
    return interrupt, success


def mutant_omit_stack_clear_undercounts(words, records):
    """Omitting face clears leaves dirt and undercounts the abort Tape invoice."""
    Tape = records.Tape
    Stack = records.Stack
    VALUE = records.VALUE
    residue = words.Arena(bits=4, capacity=8)
    index = words.Arena(bits=4, capacity=8)
    pending = Stack(index, residue)
    pending.push(VALUE, residue.literal(1), residue.literal(1))
    length = body_len(pending.tape)
    expected_face = invoice.clear_charge(length)
    before = snap_meter(pending.tape)
    # Mutant: rewind program/fields only; omit stack clears.
    program = Tape()
    program.append(words.ONE)
    program.rewind()
    observed_face = delta_meter(pending.tape, before)
    need(observed_face == {"reads": 0, "writes": 0, "moves": 0}, "mutant charged nothing on face")
    need(not pending.empty(), "mutant left pending dirt")
    need(expected_face["writes"] > 0, "honest clear would write")
    return True


def mutant_omit_park_restore_steps():
    """Charging only abort Tape without park+restore undercounts interrupt steps."""
    abort_tape = {"reads": 10, "writes": 2, "moves": 12}
    park_restore = invoice.park_restore_table_charge(12, 3, 1)
    full = invoice.interrupt_park_invoice(abort_tape, park_restore)
    bare = invoice.interrupt_park_invoice(abort_tape, {"steps": 0, "reads": 0, "writes": 0, "moves": 0})
    need(full["park_restore_steps"] == 84, "full park steps")
    need(bare["park_restore_steps"] == 0, "mutant omitted park steps")
    need(full["park_restore_steps"] > bare["park_restore_steps"], "undercount")
    return True


def mutant_wrong_clear_formula_rejected():
    """Adversarial 2L+2 clear formula disagrees with live Tape on L=3."""
    fake = {"reads": 2 * 3 + 2, "writes": 3, "moves": 2 * 3 + 2}
    honest = invoice.clear_charge(3)
    need(fake != honest, "adversarial formula differs")
    return True


def authenticate_sources(texts):
    controller = texts[INPUTS[0]]
    records_src = texts[INPUTS[1]]
    parking_proof = texts[INPUTS[4]]
    frame = texts[INPUTS[5]]
    contract = texts[INPUTS[6]]
    need("def abort(self):" in controller, "cite: Callback.abort")
    need("stack.tape.clear()" in controller and "stack.reverse.clear()" in controller,
         "cite: four stack-face clears")
    need("self.program.tape.rewind()" in controller, "cite: program rewind")
    need("self.fields.tape.rewind()" in controller, "cite: fields rewind")
    need("def clear(self):" in records_src and "def rewind(self):" in records_src,
         "cite: Tape.clear/rewind")
    need("steps  =  5S +  7r + 3d" in parking_proof, "cite: PR2769 steps formula")
    need("self.session.codec.restore()" in frame, "cite: lease restore")
    need('elif self.phase == "child":' in frame and "self.close(strict=False)" in frame,
         "cite: child nonstrict close")
    need("not interrupted-macro recovery" in contract, "cite: interrupt gap")
    return {
        "callback_abort_present": True,
        "four_stack_face_clear": True,
        "tape_clear_rewind_present": True,
        "park_restore_formula_present": True,
        "lease_restore_present": True,
        "contract_names_interrupt_gap": True,
    }


def evaluate():
    texts = pin_sources()
    source_report = authenticate_sources(texts)
    words, records, parking_machine = load_vendor()
    need(formula_grid_matches_live_tape(words, records), "formula grid")
    abort_report = metered_callback_abort_invoice(words, records)
    park_report = park_restore_tariff_matches(parking_machine)
    composed = invoice.interrupt_park_invoice(
        abort_report["abort_tape"], park_report["park_restore"]
    )
    interrupt_ctrl, success_ctrl = success_path_output_disposal_control(
        abort_report["abort_tape"], park_report["park_restore"]
    )
    need(interrupt_ctrl["park_restore_steps"] == composed["park_restore_steps"], "compose steps")
    need(mutant_omit_stack_clear_undercounts(words, records), "mutant stack")
    need(mutant_omit_park_restore_steps(), "mutant park")
    need(mutant_wrong_clear_formula_rejected(), "mutant formula")

    report = {
        "schema_version": 1,
        "status": "PASS_SELECTED_BIT_PRICED_PARK_INVOICE",
        "marker": MARKER,
        "kappa_decimal": KAPPA_DECIMAL,
        "no_new_kappa": True,
        "callback_abort_tape_formula": True,
        "park_restore_table": True,
        "interrupt_no_output_disposal": True,
        "face_lengths": abort_report["face_lengths"],
        "program_len": abort_report["program_len"],
        "fields_len": abort_report["fields_len"],
        "abort_tape": abort_report["abort_tape"],
        "park_restore": park_report["park_restore"],
        "park_restore_params": {
            "S": park_report["S"],
            "r": park_report["r"],
            "d": park_report["d"],
        },
        "composed": composed,
        "success_path_disposal_control_reads": success_ctrl["returned_output_disposal"]["reads"],
        "mutants": {
            "omit_stack_clear_undercounts_and_leaves_dirt": True,
            "omit_park_restore_undercounts_steps": True,
            "wrong_clear_formula_rejected": True,
        },
        "source_correspondence": source_report,
        "scope": (
            "Priced park/restore invoice on the PR2809 interrupt path including "
            "Callback.abort four Stack-face Tape.clear charges and program/fields "
            "rewinds, composed with the published PR2769/PR2635 park+restore table "
            "invoice; interrupt pays no returned-output disposal; three mutants; "
            "not ScratchPool lease-end, enclosing ownership, GL64, H2, or stock-envelope"
        ),
    }
    return report


def main():
    report = evaluate()
    print(report["marker"])


if __name__ == "__main__":
    main()
