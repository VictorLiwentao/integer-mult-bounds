# Notice

This package reads the published P104 native-channel witness and the #2981 flag
matching, both hash-pinned. It does not modify frozen upstream sources, and it
builds no repaired word.

`headstep.py` is a byte-identical copy of
`research/p104-flag9-head-step-repair/headstep.py`, which is git blob
`d70e0dba6201b4c313d0cb07cf3b9577838f9b4c` at fork commit
`a919d13033a6215c06aa7780ebbf5db5ec8b67f6` (VictorLiwentao/integer-mult-bounds,
branch `cursor/p104-flag9-head-step-repair-9fb3`). That package is deferred and
not on the pinned base, so the copy is carried here. `verify.py` refuses to load
it unless its SHA-256 is
`baad56ee042484681ad4c809bf9fc770a5a0f053ed72e1e2270f7e36898b22d8`. Its
splice, assemble and validate functions are not called here.

The flag-1 facts this package builds on are from open #3532: the delivering
update, the window, the relaxed sweep, R0/R1 and the +2 parity floor. The
head-step method is #3508's.

Prepared by Wentao Li <wentaol4@illinois.edu> with substantial AI assistance.
Apache-2.0; predecessor notices and exact source pins are retained in
`SOURCES.json`.
