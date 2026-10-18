# Notice

This package applies two explicit schedule changes to the published P104
native-channel witness in memory and checks them with the published native
checker and a second scanner. It does not modify frozen upstream sources. The
six recipes in `REPAIR-RECIPES.json` were lowered with the pinned
`research/p104-native-channel/compile.py` and `vendor/clifford_exact.py`
(PR1991 lineage, Chafik Boukhalfa), whose notices are retained in that package.
The repair method, head-closure rule and bill format follow #3508 (flag 43)
and open #3532 (flag 1); `headstep.py` re-implements that harness in a
flag-agnostic form. The flag-9 published chronology is #3443.

Prepared by Wentao Li <wentaol4@illinois.edu> with substantial AI assistance.
Apache-2.0; predecessor notices and exact source pins are retained in
`SOURCES.json`.
