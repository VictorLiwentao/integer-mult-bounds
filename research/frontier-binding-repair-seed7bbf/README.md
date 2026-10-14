# Frontier binding repair: #1042 invoice checkpoint pin and #1094 certificate SHA

**Tooling / adversarial-audit repair; no new κ; selected frontier content unchanged.**

After #1094 became selected, two check-level gaps remained:

1. Wronskode's historical `#1042` invoice/outer audit
   (`research/frontier1042-invoice-audit-seed81/`) still required the *moving*
   `certificates/selected-result.json` pointer to name the #1042 certificate, so
   `make frontier1042-invoice-audit-verify` failed with
   `FAIL selected certificate path moved` even though the arithmetic was intact.
2. `scripts/verify_frontier1094.py` bound the cold replay to the selected record
   **only through κ**. A well-formed mutant with unchanged κ is accepted once the
   selected hash pin is rewritten (demonstrated in open #1735).

This package applies both handoffs from #1735 and records exact before/after
evidence. It does not change any certificate bytes, κ, or packing claim.

## Exact before / after

| Check | Before (main `0b1cccf8`) | After |
|---|---|---|
| `python3 -I -B research/frontier1042-invoice-audit-seed81/verify.py` | `FAIL selected certificate path moved` | `PASS_FRONTIER1042_INVOICE_OUTER_INDEPENDENT \| guards 9 \| slacks 94 \| bootstrap 14 \| controls 15` |
| seed81 `RESULT.json` SHA-256 | `b9ca758d…8875` (committed) | **identical** `b9ca758d…8875` (arithmetic unchanged) |
| #1094 replay ↔ certificate | κ compared; certificate SHA not compared | `require(sha(ASSEMBLY) == selected['certificate_sha256'])` |
| κ-preserving endpoint mutant | accepted by selected-record pin once rehashed | rejected by the new SHA binding |

The seed81 loader now pins `certificates/checkpoints/frontier1042.json` by file
SHA-256, certificate path, `certificate_sha256`, and κ. Default verify remains
read-only and compares the regenerated receipt to the committed `RESULT.json`;
`--write` is required to rewrite it. Checkpoint hash / SHA-field / assembly-byte
corruption controls reject forged receipts.

## Reproduce

```sh
python3 -I -B research/frontier-binding-repair-seed7bbf/verify.py
```

Expected:

```text
PASS_FRONTIER_BINDING_REPAIR seed81=PASS result_sha_unchanged=b9ca758da0fc 1094_bind=PASS no_new_kappa
```

Supporting commands:

```sh
make frontier1042-invoice-audit-verify
python3 -B -m unittest tests.test_frontier1094_certificate_bind -v
python3 scripts/research_package.py --package research/frontier-binding-repair-seed7bbf --check-only
```

`--write` regenerates only this package's `RESULT.json`. The seed81 and selected
artifacts are not rewritten by the default path.

## Scope and limits

- **No new κ.** Selected certificate, packing ceiling, and supplier moments are
  untouched.
- **Cold replay not re-run.** The #1094 SHA binding is proved offline against the
  committed certificate and published `assembly_sha256`, with a κ-preserving
  mutant control. A full `make frontier1094-verify` after the script edit remains
  an open maintainer check.
- **Historical audits for #942/#890/#799** still lack certificate-SHA comparison
  statically (#1735); not repaired here.
- Exact rational reasoning: the mutant uses an exact `Fraction` endpoint bump;
  pass/fail is SHA equality / exact pin match, not an upper-endpoint ratio.

## Open next questions

1. **Run one cold `make frontier1094-verify` with the new SHA require.** Why it
   matters: end-to-end confirmation that the live replay output still equals the
   committed certificate under the stronger gate. First step: reuse a published
   `#1042` baseline with `--baseline1042` if available. Blocked by: long baseline
   wall time on this session budget.
2. **Whether checkpoint-bound historical audits should be a shared helper.** Why
   it matters: other frozen invoice/capsule audits may still read the moving
   selected pointer. First step: grep loaders for `selected-result.json` paired
   with a historical `ASSEMBLY_SHA256`. Blocked by: need a maintainer convention
   for when a package is historical vs current.

## Credit

- **Wronskode (@Wronskode):** original seed81 invoice/outer independent audit.
- **#1735 / discussion #1730 (rtyu193-rgb):** identified both gaps and proposed
  the checkpoint pin and SHA binding; this package applies those handoffs.
- **#474 (artuskg):** earlier gen4 certificate-to-replay binding pattern.
- **Douglas Colkitt / Rohan Arun / Jeremy Kothe** and the retained #1042/#1094
  supplier lineage as credited in those packages.

Prepared by **Wentao Li** ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial **Cursor/Composer**
assistance. Apache-2.0. Not a formal proof of the multiplication theorem.
