# Research: priced park invoice on interrupt path with Callback stack faces (no new kappa)

Independent audit answering open
[#4018](https://github.com/CrocSwap/integer-mult-bounds/pull/4018) OQ2 and
[#3999](https://github.com/CrocSwap/integer-mult-bounds/pull/3999) OQ3: the
complete machine-step charge for park/restore on the PR2809 interrupt path
when Callback stack faces are included.

At the pinned bytes, `records.Tape.clear` / `Tape.rewind` have closed forms
`clear(L)=(3L+3,L,3L+4)` and `rewind(L)=(L+1,0,L+2)` in `(reads,writes,moves)`.
`Callback.abort` therefore costs exactly four face clears plus program/fields
rewinds. Composing that Tape invoice with the published PR2769/PR2635
park+restore table (`steps=5S+7r+3d`) yields the priced park invoice.
Interrupt pays no returned-output disposal. Three mutants show omitted face
clears, omitted park+restore steps, and a wrong clear formula are load-bearing.

Complements open [#4018](https://github.com/CrocSwap/integer-mult-bounds/pull/4018)
(qualitative Callback.abort + parked child) and
[#3999](https://github.com/CrocSwap/integer-mult-bounds/pull/3999)
(NumericLease/SharedFrame interrupt). Primary new obligation is the Tape-meter
and parking-table charge, not another MiniArena qualitative rollback. Does not
close enclosing ownership with ScratchPool lease-end.

**No new kappa.** Selected κ stays `0.001672660197076918`.

## Reproduce

```sh
python3.12 -I -B research/selected-bit-priced-park-invoice/verify.py
python3.12 -I -O -Werror -B research/selected-bit-priced-park-invoice/verify.py
python3.12 -I -B research/selected-bit-priced-park-invoice/independent.py
python3.12 -I -B research/selected-bit-priced-park-invoice/test_package.py
python3.12 -B scripts/research_package.py --package research/selected-bit-priced-park-invoice
```

Expected:

```text
PASS_SELECTED_BIT_PRICED_PARK_INVOICE callback_abort_tape_formula park_restore_table interrupt_no_output_disposal three_mutants no_new_kappa
PASS_SELECTED_BIT_PRICED_PARK_INVOICE_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-bit-priced-park-invoice outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`.
Corrupted temporary certificates and duplicate JSON keys are rejected.

## Open next questions

1. Does the composed invoice stay exact when RoleParking stream roles share the
   same parking tape as the numerical codec during Callback.abort?
2. Can Callback.abort compose with ScratchPool lease-end/CALL-empty into one
   enclosing ownership argument that carries this priced invoice?

## Credit

Credit Jose Manuel / jmbarrancoml / PR2809 for NumericLease child-phase
nonstrict close and the physical Callback lowering of David Arias’s PR2753
caller; PR2769 / PR2635 for the parking-table tariff; PR2899 / the
physical-contract map for naming the interrupted-macro gap; open
[#4018](https://github.com/CrocSwap/integer-mult-bounds/pull/4018) for the
Callback.abort binding and OQ2 answered here;
[#3999](https://github.com/CrocSwap/integer-mult-bounds/pull/3999) for the
NumericLease interrupt invoice and OQ3 answered here. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
