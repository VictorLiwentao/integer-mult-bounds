"""Offline controls for the selected #1094 replay-to-certificate binding.

No cold replay. Uses the committed certificate and selected-record pins.
Wentao Li with substantial Cursor/Composer assistance. Apache-2.0.
"""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json'
SELECTED = ROOT / 'certificates/selected-result.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind_ok(assembly_path: Path, selected: dict) -> None:
    """The predicate added to scripts/verify_frontier1094.py."""
    assert selected['certificate'] == 'research/community-frontier1094-audit/ASSEMBLY.json'
    assert sha(assembly_path) == selected['certificate_sha256']


class Frontier1094CertificateBind(unittest.TestCase):
    def test_published_certificate_matches_selected_pin(self):
        selected = json.loads(SELECTED.read_text())
        self.assertEqual(sha(CERT), selected['certificate_sha256'])
        self.assertEqual(
            selected['certificate_sha256'],
            '1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045',
        )
        bind_ok(CERT, selected)

    def test_published_replay_receipt_records_same_digest(self):
        receipt = json.loads((ROOT / 'research/community-frontier1094-audit/RESULT.json').read_text())
        self.assertEqual(receipt['assembly_sha256'], sha(CERT))

    def test_mutant_same_kappa_rejected_by_binding(self):
        selected = json.loads(SELECTED.read_text())
        asm = json.loads(CERT.read_text())
        # Next-grid complex endpoint; kappa left unchanged (PR1735 mutant class).
        from fractions import Fraction as Q
        asm['complex_lower'] = str(Q(asm['complex_lower']) + Q(1, 10 ** 24))
        self.assertEqual(asm['kappa'], selected['kappa'])
        tmp = Path(tempfile.mkdtemp(prefix='f1094-bind-'))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        mutant = tmp / 'ASSEMBLY.json'
        mutant.write_text(json.dumps(asm, indent=2, sort_keys=True) + '\n')
        self.assertNotEqual(sha(mutant), selected['certificate_sha256'])
        with self.assertRaises(AssertionError):
            bind_ok(mutant, selected)


if __name__ == '__main__':
    unittest.main()
