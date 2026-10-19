# Priced park invoice on the interrupt path (Callback stack faces)

**No new kappa.** Selected κ stays `0.001672660197076918`.

## Setup

Pin Jose Manuel / jmbarrancoml’s PR2809 physical caller sources at base
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Open
[#4018](https://github.com/CrocSwap/integer-mult-bounds/pull/4018) binds
`Callback.abort` qualitatively to the NumericLease parked-child interrupt
invoice and leaves machine-step pricing as OQ2. Open
[#3999](https://github.com/CrocSwap/integer-mult-bounds/pull/3999) asks the
same pricing question as OQ3, separating returned-output disposal from failed
construction cleanup.

## Tape-meter lemmas

Let `L` be the number of body symbols on a `records.Tape` whose head sits on
the blank immediately after those symbols (the retained append invariant).

**Lemma (rewind).** `Tape.rewind` costs exactly

```text
reads = L + 1,   writes = 0,   moves = L + 2.
```

**Lemma (clear).** `Tape.clear` is rewind, then blank the `L` body cells with
unit steps, then rewind again, costing exactly

```text
reads = 3L + 3,   writes = L,   moves = 3L + 4.
```

Both identities are checked on the live pinned `records.Tape` for every
`L ∈ {0,…,12}`.

## Callback.abort Tape invoice

At the pinned `controller.Callback.abort`, the continuation work is:

1. four Stack-face clears: `pending.tape`, `pending.reverse`, `values.tape`,
   `values.reverse`;
2. `program.tape.rewind()` and `fields.tape.rewind()`;
3. residue/index rollback to the Callback entry protected sets (bank API,
   outside the Tape meter).

**Theorem (abort Tape charge).** If the four faces have body lengths
`(L0,L1,L2,L3)` and the program/fields tapes have lengths `(Lp,Lf)` at abort
time, then the Tape-meter charge is

```text
Σ_{i=0..3} clear(Li)  +  rewind(Lp)  +  rewind(Lf).
```

A concrete dirty fixture (VALUE + PAIR continuations, one reverse-face tag,
program length 1, fields length 2) meters exactly to the closed form.

## Park+restore table invoice

PR2769/PR2635 publish the parking-table invoice for one complete park+restore
of `S` parked word bits, `r` records, and `d` frames:

```text
steps  = 5S + 7r + 3d
reads  = 10S + 14r + 6d
writes = 4S + 4r + 2d
moves  = 8S + 8r + 2d
```

For uniform width `s = S/r`, this equals
`tariff(begin) + r·tariff(push,s) + r·tariff(pop,s) + tariff(end)` from the
pinned `parking_machine.tariff`. Checked at `(S,r,d)=(12,3,1)` (steps `84`).

## Composed interrupt invoice

On the interrupt path the parent has already paid park; abort then pays the
Callback Tape invoice above; `NumericLease.close(strict=False)` pays restore
after clearing child grants. Returned-output disposal is **not** charged on
interrupt (failed construction cleanup only). A success-path control may attach
a positive disposal term; the interrupt flag stays false.

## Mutants

1. Omitting Stack-face clears charges `0` on those faces and leaves continuation
   dirt.
2. Omitting the park+restore table undercounts interrupt steps (`0` vs `84` on
   the `(12,3,1)` fixture).
3. An adversarial `2L+2` clear formula disagrees with the live Tape on `L=3`.

## Scope

This is a priced invoice for the named interrupt schedule. It does not claim
enclosing ownership with ScratchPool lease-end, a joint RoleParking+Callback
meter, selected GL64 execution, H2 improvement, or a new kappa.
