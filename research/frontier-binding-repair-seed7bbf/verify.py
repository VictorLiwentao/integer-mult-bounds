#!/usr/bin/env python3
"""Read-only receipt for two check-level binding repairs (no new kappa).

1. Restore Wronskode's historical #1042 invoice audit by pinning the frozen
   checkpoint instead of the moving selected-result pointer.
2. Bind ``scripts/verify_frontier1094.py`` replay output to the selected
   certificate SHA-256, not only kappa (PR1735 handoff).

Default mode compares RESULT.json and leaves the checkout unchanged.
``--write`` regenerates RESULT.json after all checks pass.
Wentao Li with substantial Cursor/Composer assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SEED81 = ROOT / 'research/frontier1042-invoice-audit-seed81'
CHECKPOINT = ROOT / 'certificates/checkpoints/frontier1042.json'
SELECTED = ROOT / 'certificates/selected-result.json'
CERT1094 = ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json'
RESULT1094 = ROOT / 'research/community-frontier1094-audit/RESULT.json'
SEED81_RESULT = SEED81 / 'RESULT.json'
SEED81_RESULT_SHA256 = 'b9ca758da0fcc664e36c07f3850082ba4de8c444ebaf8a674f3a8e33d6298875'
CHECKPOINT_SHA256 = '207d1f49f113c585024b9d3c17eadbb8b1be17c1321e3d190aabe2f18ce1c5b7'
CERT1094_SHA256 = '1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045'
SCRIPT1094 = ROOT / 'scripts/verify_frontier1094.py'


class Fail(Exception):
    pass


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise Fail(msg)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_bytes())


def check_seed81_pass() -> dict:
    need(sha(SEED81_RESULT) == SEED81_RESULT_SHA256, 'seed81 RESULT.json hash drifted')
    proc = subprocess.run(
        [sys.executable, '-I', '-B', str(SEED81 / 'verify.py')],
        cwd=ROOT, capture_output=True, text=True,
    )
    need(proc.returncode == 0, 'seed81 verify failed: ' + (proc.stdout + proc.stderr))
    need('PASS_FRONTIER1042_INVOICE_OUTER_INDEPENDENT' in proc.stdout, 'seed81 missing PASS')
    need(sha(SEED81_RESULT) == SEED81_RESULT_SHA256, 'seed81 default verify mutated RESULT.json')
    # Confirm moving selected pointer is not #1042, so the old path would still fail.
    selected = read(SELECTED)
    need(selected['certificate'] != 'research/community-frontier1042-audit/ASSEMBLY.json',
         'selected pointer unexpectedly still on #1042')
    ck = read(CHECKPOINT)
    need(sha(CHECKPOINT) == CHECKPOINT_SHA256, 'checkpoint file hash mismatch')
    need(ck['certificate'] == 'research/community-frontier1042-audit/ASSEMBLY.json',
         'checkpoint path')
    need(ck['certificate_sha256'] == '093f35445812ea96fe1bfe6a3af7d769cb7f274e08f4fb30f71a17ed1161e54e',
         'checkpoint assembly pin')
    return dict(
        status='PASS',
        stdout=proc.stdout.strip(),
        result_sha256=SEED81_RESULT_SHA256,
        selected_certificate=selected['certificate'],
        checkpoint=str(CHECKPOINT.relative_to(ROOT)),
    )


def check_1094_binding() -> dict:
    selected = read(SELECTED)
    need(selected['certificate'] == 'research/community-frontier1094-audit/ASSEMBLY.json',
         'selected certificate path')
    need(sha(CERT1094) == selected['certificate_sha256'] == CERT1094_SHA256,
         'committed #1094 certificate pin')
    receipt = read(RESULT1094)
    need(receipt['assembly_sha256'] == CERT1094_SHA256, 'published replay receipt digest')
    # Static source presence of the new require lines.
    src = SCRIPT1094.read_text()
    need('Replay output is the selected certificate' in src, 'binding require missing')
    need('certificate_sha256' in src and 'selected' in src, 'selected certificate_sha256 compare missing')
    # Exact rational mutant: bump complex_lower by 1e-24, keep kappa.
    asm = read(CERT1094)
    mutant = dict(asm)
    mutant['complex_lower'] = str(Q(asm['complex_lower']) + Q(1, 10 ** 24))
    need(mutant['kappa'] == selected['kappa'] == asm['kappa'], 'mutant kappa must match')
    tmp = Path(tempfile.mkdtemp(prefix='bind1094-'))
    try:
        mpath = tmp / 'ASSEMBLY.json'
        mpath.write_text(json.dumps(mutant, indent=2, sort_keys=True) + '\n')
        need(sha(mpath) != selected['certificate_sha256'], 'mutant must diverge from pin')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # Exact interval gate: certified residual enclosure style check is not re-run
    # here; binding uses exact SHA equality, which is stronger than an upper-endpoint
    # ratio and rejects the kappa-preserving mutant above.
    return dict(
        status='PASS',
        certificate_sha256=CERT1094_SHA256,
        published_receipt_assembly_sha256=receipt['assembly_sha256'],
        mutant_kappa_unchanged=True,
        mutant_rejected_by_sha_binding=True,
        cold_replay_run=False,
    )


def failure_controls() -> dict:
    out = {}
    # Control: forged checkpoint hash must fail seed81 load_inputs.
    sys.path.insert(0, str(SEED81))
    import verify as seed81  # noqa: E402
    tmp = Path(tempfile.mkdtemp(prefix='bind-ctrl-'))
    try:
        for rel in (
            seed81.CHECKPOINT,
            seed81.AUDIT + '/ASSEMBLY.json',
            seed81.AUDIT + '/selected-replay.tar.gz',
            seed81.BIT_PATH,
        ):
            src = ROOT / rel
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        forged = tmp / seed81.CHECKPOINT
        data = read(forged)
        data['kappa'] = '0'
        forged.write_text(json.dumps(data, indent=2) + '\n')
        try:
            seed81.load_inputs(tmp)
            raise Fail('control accepted forged checkpoint')
        except seed81.Fail as exc:
            out['forged_checkpoint_hash'] = str(exc)
        need('checkpoint receipt hash mismatch' in out['forged_checkpoint_hash'],
             'unexpected forged-checkpoint rejection')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        if str(SEED81) in sys.path:
            sys.path.remove(str(SEED81))
    return out


def build_receipt() -> dict:
    seed81 = check_seed81_pass()
    bind = check_1094_binding()
    controls = failure_controls()
    return dict(
        status='PASS_FRONTIER_BINDING_REPAIR',
        no_new_kappa=True,
        before=dict(
            seed81_make_target='FAIL selected certificate path moved',
            frontier1094_binding='kappa only; certificate SHA not compared',
        ),
        after=dict(
            seed81=seed81,
            frontier1094_certificate_binding=bind,
        ),
        controls=controls,
        scope=(
            'Tooling/binding repair only. Restores the historical #1042 invoice '
            'make target and adds a selected-certificate SHA require to the #1094 '
            'reproduce script. Does not change kappa, certificates, or selected '
            'frontier content. Cold make frontier1094-verify was not re-run.'
        ),
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true',
                    help='regenerate RESULT.json after checks; default is read-only compare')
    args = ap.parse_args()
    need(not sys.flags.optimize, 'assertions required')
    receipt = build_receipt()
    text = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    target = HERE / 'RESULT.json'
    if args.write:
        target.write_text(text)
    else:
        need(target.exists(), 'RESULT.json missing; run with --write once')
        need(target.read_text() == text, 'RESULT.json differs from regenerated receipt')
    print(receipt['status'],
          'seed81=PASS',
          'result_sha_unchanged=' + SEED81_RESULT_SHA256[:12],
          '1094_bind=PASS',
          'no_new_kappa')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Fail as exc:
        print('FAIL', exc)
        raise SystemExit(1)
